"""Build a one-municipality building profile from discovered local polygon layers."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import geopandas as gpd
import pandas as pd
from pyproj import CRS
import shapely
from shapely.ops import unary_union


def require(condition, message):
    if not condition:
        raise ValueError(message)


def polygonal(geometry):
    if geometry.geom_type in ('Polygon', 'MultiPolygon'):
        return geometry
    return unary_union([polygonal(g) for g in getattr(geometry, 'geoms', [])
                        if g.geom_type in ('Polygon', 'MultiPolygon', 'GeometryCollection')])


def check_polygons(frame, label):
    require(frame.crs is not None, f'{label}: missing CRS; do not assign one by guesswork')
    require(frame.geom_type.isin(['Polygon', 'MultiPolygon']).all(), f'{label}: polygon geometry required')
    require(not frame.geometry.isna().any() and not frame.geometry.is_empty.any()
            and frame.geometry.is_valid.all(), f'{label}: null, empty or invalid geometry')
    if len(frame):
        require(all(math.isfinite(v) for v in frame.total_bounds), f'{label}: nonfinite coordinates')


def string_ids(frame, field, label):
    require(field in frame, f'{label}: unknown ID field {field}')
    values = frame[field]
    require(values.map(lambda v: isinstance(v, str) and bool(v.strip())).all()
            and values.is_unique, f'{label}: unique nonempty string IDs required')


def height_summary(values, spec):
    require(spec.get('unit') == 'm' and spec.get('semantics') and spec.get('source'),
            'Height requires verified metre units, semantics and source')
    sentinels = spec.get('missing_values')
    require(isinstance(sentinels, list) and all(type(v) in (int, float) and math.isfinite(v)
                                               for v in sentinels),
            'Height missing_values must be an explicit list of finite numbers (possibly empty)')
    counts = dict(valid=0, missing=0, sentinel=0, invalid=0)
    valid, cleaned = [], []
    for value in values:
        number = None
        if pd.isna(value) or (isinstance(value, str) and not value.strip()):
            counts['missing'] += 1
        else:
            try:
                parsed = float(value)
            except (ValueError, TypeError):
                parsed = float('nan')
            if isinstance(value, bool) or not math.isfinite(parsed):
                counts['invalid'] += 1
            elif parsed in sentinels:
                counts['sentinel'] += 1
            elif parsed < 0:
                counts['invalid'] += 1
            else:
                number = parsed
                valid.append(number)
                counts['valid'] += 1
        cleaned.append(number)
    series = pd.Series(valid, dtype='float64')
    summary = dict(total=len(values), **counts)
    summary.update({key: float(series.quantile(q, interpolation='linear')) if valid else None
                    for key, q in [('min_m', 0), ('q25_m', .25), ('median_m', .5),
                                   ('q75_m', .75), ('max_m', 1)]})
    summary['mean_m'] = float(series.mean()) if valid else None
    summary['unusable_pct'] = 100 * (len(values) - len(valid)) / len(values) if len(values) else None
    require(all(v is None or math.isfinite(v) for v in summary.values()), 'Height statistic overflow')
    return summary, cleaned


def profile(municipalities, buildings, manifest):
    """No file writes: preserve source frames and return three layers and an audit."""
    boundary_spec, building_spec = manifest['municipality'], manifest['buildings']
    require(building_spec.get('geometry_scope') == 'whole_objects',
            'Use whole building geometries, not pre-clipped footprints; record geometry_scope=whole_objects')
    string_ids(municipalities, boundary_spec['id_field'], 'municipalities')
    string_ids(buildings, building_spec['id_field'], 'buildings')
    require(isinstance(boundary_spec['id'], str), 'Municipality ID must be a string')
    boundary = municipalities.loc[municipalities[boundary_spec['id_field']] == boundary_spec['id']].copy()
    require(len(boundary) == 1, 'Select exactly one municipality by its discovered ID')
    check_polygons(boundary, 'municipality')
    check_polygons(buildings, 'buildings')
    crs = CRS.from_user_input(manifest['analysis_crs'])
    require(crs.is_projected and len(crs.axis_info) >= 2
            and all(axis.unit_conversion_factor == 1 for axis in crs.axis_info[:2])
            and crs.to_epsg() != 3857, 'Choose a suitable projected metre CRS, not geographic/Web Mercator')
    if crs.area_of_use:
        west, south, east, north = crs.area_of_use.bounds
        x1, y1, x2, y2 = boundary.to_crs(4326).total_bounds
        require(west <= x1 <= x2 <= east and south <= y1 <= y2 <= north,
                'Municipality falls outside the analysis CRS area of use')
    boundary = boundary.to_crs(crs).reset_index(drop=True)
    objects = buildings.to_crs(crs).reset_index(drop=True).copy()
    boundary.geometry = boundary.geometry.map(shapely.force_2d)
    objects.geometry = objects.geometry.map(shapely.force_2d)
    check_polygons(boundary, 'projected municipality')
    check_polygons(objects, 'projected buildings')
    area = float(boundary.geometry.iloc[0].area)
    require(math.isfinite(area) and area > 0, 'Municipality area must be positive and finite')
    shape = boundary.geometry.iloc[0]
    clips = objects.geometry.map(lambda g: polygonal(g.intersection(shape)))
    selected = pd.Series([g.area > 0 for g in clips], index=objects.index, dtype=bool)
    touches = objects.geometry.intersects(shape) & ~selected
    crosses = selected & pd.Series([g.difference(shape).area > max(1e-8, g.area * 1e-10)
                                    for g in objects.geometry], index=objects.index, dtype=bool)
    chosen = objects.loc[selected].copy()
    chosen_clips = list(clips.loc[selected])
    footprint = unary_union(chosen_clips)
    footprint_area = float(footprint.area)
    sum_area = float(sum(g.area for g in chosen_clips))
    require(math.isfinite(sum_area) and 0 <= footprint_area <= area + max(1e-8, area * 1e-10),
            'Footprint area cannot exceed municipality area')
    ids = objects[building_spec['id_field']]
    scope = building_spec.get('completeness', {'status': 'unknown', 'evidence': None})
    require(scope.get('status') in ('complete', 'partial', 'unknown'), 'Invalid completeness status')
    if scope['status'] == 'complete':
        require(isinstance(scope.get('evidence'), str) and bool(scope['evidence'].strip()),
                'Complete coverage requires recorded evidence')
    metrics = {'municipality_area_m2': area, 'building_count': len(chosen),
               'footprint_area_m2': footprint_area, 'observed_footprint_share_pct': 100 * footprint_area / area,
               'sum_clipped_building_area_m2': sum_area,
               'overlap_excess_m2': max(0., sum_area - footprint_area)}
    warnings = []
    if scope['status'] != 'complete':
        warnings.append('Building coverage is not established as complete: these are observed-input indicators, not a full municipal inventory.')
    if not len(chosen):
        warnings.append('No positive-area building intersection: verify coverage and location before interpreting zero.')
    if crosses.any():
        warnings.append('Cross-boundary buildings count once here; counts across municipalities are not additive.')
    duplicate_geometry = chosen.geometry.map(lambda g: shapely.normalize(g).wkb).duplicated(keep=False)
    if duplicate_geometry.any():
        warnings.append('Distinct IDs have identical geometry: counts are source-object counts; investigate before interpreting them as physical buildings.')
    output = gpd.GeoDataFrame({'building_id': pd.Series(ids.loc[selected].tolist(), dtype='str'),
                              'crosses_boundary': crosses.loc[selected].astype(int).tolist(),
                              'clipped_area_m2': [float(g.area) for g in chosen_clips]},
                             geometry=chosen_clips, crs=crs)
    heights, usage = None, None
    if manifest.get('height'):
        spec = manifest['height']
        require(spec.get('field') in chosen, 'Unknown height field')
        heights, cleaned = height_summary(chosen[spec['field']].tolist(), spec)
        output['height_m'] = pd.Series(cleaned, dtype='float64')
        if heights['invalid']:
            warnings.append('Invalid/negative/nonfinite heights were excluded and counted separately.')
    if manifest.get('usage'):
        spec = manifest['usage']
        require(spec.get('field') in chosen and spec.get('semantics') and spec.get('source'),
                'Usage requires a discovered field, semantics and source')
        values = chosen[spec['field']].map(lambda v: None if pd.isna(v) or not str(v).strip() else str(v))
        output['usage'] = pd.Series(values.tolist(), dtype='str')
        usage = [{'value': value, 'count': int(count), 'share_pct': 100 * int(count) / len(chosen)}
                 for value, count in values.value_counts(dropna=False, sort=False).items()]
        for item in usage:
            if pd.isna(item['value']):
                item['value'] = None
    municipality = gpd.GeoDataFrame({'municipality_id': [boundary_spec['id']],
                                     **{k: [v] for k, v in metrics.items()}}, geometry=[shape], crs=crs)
    union = gpd.GeoDataFrame({'area_m2': pd.Series([footprint_area] if chosen_clips else [], dtype='float64')},
                             geometry=[footprint] if chosen_clips else [], crs=crs)
    audit = {'municipality_id': boundary_spec['id'], 'analysis_crs': crs.to_string(),
             'method': 'positive-area intersection; planar 2D union; unweighted building statistics; linear quantiles',
             'completeness': scope, 'metrics': metrics, 'height': heights, 'usage': usage,
             'reconciliation': {'input_buildings': len(objects), 'selected_buildings': len(chosen),
                                'touch_only_ids': ids.loc[touches].tolist(),
                                'outside_ids': ids.loc[~selected & ~touches].tolist(),
                                'cross_boundary_ids': ids.loc[crosses].tolist(),
                                'duplicate_geometry_ids': chosen.loc[duplicate_geometry, building_spec['id_field']].tolist()},
             'inputs': manifest, 'warnings': warnings,
             'versions': {'geopandas': gpd.__version__, 'pandas': pd.__version__, 'shapely': shapely.__version__}}
    return {'municipality': municipality, 'buildings': output, 'footprint': union}, audit


def read_layer(spec, base):
    path = (base / spec['path']).resolve()
    require(path.is_file(), f'Missing local input: {path}')
    layers = gpd.list_layers(path)['name'].tolist()
    layer = spec.get('layer')
    require(layer in layers if layer else len(layers) == 1 and path.suffix.lower() != '.gpkg',
            f'Select a discovered layer from {layers}; GeoPackage requires an explicit layer')
    return gpd.read_file(path, layer=layer or layers[0]), path


def hashes(paths):
    result = {}
    for path in paths:
        files = sorted(path.parent.glob(path.stem + '.*')) if path.suffix.lower() == '.shp' else [path]
        for component in files:
            if component.is_file():
                digest = hashlib.sha256()
                with component.open('rb') as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(chunk)
                result[str(component)] = digest.hexdigest()
    return result


def export(layers, audit, directory):
    directory = Path(directory)
    # Serialize before creating anything; NaN/Infinity must never enter a report.
    json.dumps(audit, allow_nan=False)
    directory.mkdir(parents=True, exist_ok=False)
    gpkg = directory / 'profile.gpkg'
    for name, frame in layers.items():
        frame.to_file(gpkg, layer=name, driver='GPKG', index=False, engine='pyogrio')
        saved = gpd.read_file(gpkg, layer=name)
        require(saved.crs == frame.crs and len(saved) == len(frame), f'{name}: CRS/count round-trip failed')
        require(saved.geometry.geom_equals(frame.geometry).all(), f'{name}: geometry round-trip failed')
        for field in frame.columns.drop(frame.geometry.name):
            expected, actual = frame[field].reset_index(drop=True), saved[field].reset_index(drop=True)
            same = expected.eq(actual) | (expected.isna() & actual.isna())
            require(same.fillna(False).all(), f'{name}.{field}: attribute round-trip failed')
    records = [('identity', k, audit[k]) for k in ('municipality_id', 'analysis_crs')]
    records += [('metrics', k, v) for k, v in audit['metrics'].items()]
    for section in ('height', 'usage', 'completeness'):
        records.append((section, 'summary', audit[section]))
    csv_path = directory / 'indicators.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['section', 'indicator', 'value_json'])
        writer.writerows((s, k, json.dumps(v, ensure_ascii=False, allow_nan=False)) for s, k, v in records)
    with csv_path.open(encoding='utf-8', newline='') as stream:
        reopened = [(row['section'], row['indicator'], json.loads(row['value_json'])) for row in csv.DictReader(stream)]
    require(reopened == records, 'CSV round-trip failed')
    audit['validation'] = {'geopackage_layers_reopened': list(layers), 'csv_reopened': True,
                           'qgis_project': 'not_created'}
    encoded = json.dumps(audit, ensure_ascii=False, allow_nan=False, indent=2) + '\n'
    (directory / 'audit.json').write_text(encoded, encoding='utf-8')
    require(json.loads((directory / 'audit.json').read_text()) == audit, 'JSON round-trip failed')
    lines = ['# Municipality building profile', '', f"Municipality: {audit['municipality_id']}",
             f"Analysis CRS: {audit['analysis_crs']}", '', audit['method'], '',
             '## Indicators', '', '| Indicator | Value |', '| --- | --- |']
    lines += [f'| {k} | {v} |' for k, v in audit['metrics'].items()]
    for title, value in [('Height statistics', audit['height']), ('Usage distribution', audit['usage']),
                         ('Sources and field semantics', audit['inputs']), ('Coverage', audit['completeness']),
                         ('Reconciliation', audit['reconciliation']), ('Validation', audit['validation'])]:
        lines += ['', '## ' + title, '', '```json', json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2), '```']
    lines += ['', '## Limits', '', 'Counts are source building objects, not dwellings or inhabitants.',
              'Heights/usages describe whole selected objects; footprint areas are clipped to the municipality.',
              'QGIS output is optional and is not created by this helper.', '']
    lines += ['- ' + warning for warning in audit['warnings']]
    (directory / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    project = {'crs': audit['analysis_crs'], 'require_portable': True,
               'layers': [{'kind': 'vector', 'source': 'profile.gpkg', 'layer': name,
                           'name': name.capitalize(), 'visible': name != 'footprint'}
                          for name in ('buildings', 'footprint', 'municipality')]}
    (directory / 'qgis-project.json').write_text(json.dumps(project, indent=2) + '\n', encoding='utf-8')


def build(manifest_path, output):
    manifest_path, output = Path(manifest_path).resolve(), Path(output)
    if output.exists():
        raise FileExistsError(output)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    paths = [(manifest_path.parent / manifest[key]['path']).resolve() for key in ('municipality', 'buildings')]
    before = hashes(paths + [manifest_path])
    municipality, _ = read_layer(manifest['municipality'], manifest_path.parent)
    buildings, _ = read_layer(manifest['buildings'], manifest_path.parent)
    layers, audit = profile(municipality, buildings, manifest)
    require(hashes(paths + [manifest_path]) == before, 'Sources changed while reading')
    audit['source_sha256'] = before
    export(layers, audit, output)
    require(hashes(paths + [manifest_path]) == before, 'Sources changed during processing')
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', help='JSON with discovered inputs, fields, CRS and semantics')
    parser.add_argument('output', help='new output directory')
    args = parser.parse_args()
    audit = build(args.manifest, args.output)
    print(json.dumps({'output': str(args.output), 'metrics': audit['metrics'], 'warnings': audit['warnings']}, allow_nan=False))


if __name__ == '__main__':
    main()
