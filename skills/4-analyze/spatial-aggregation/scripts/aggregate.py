"""Auditable vector object-to-zone aggregation using GeoPandas joins."""
import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


def aggregate(objects, zones, zone_id, *, field=None, object_id=None,
              predicate='within', policy='error', denominator=None, numerator='count'):
    if predicate not in ('within', 'intersects') or policy not in ('error', 'all', 'lowest-id'):
        raise ValueError('Choose within/intersects and error/all/lowest-id explicitly')
    if zone_id not in zones or zones[zone_id].isna().any() or not zones[zone_id].is_unique:
        raise ValueError('Zone IDs must exist, be unique and non-null')
    if not zones[zone_id].map(lambda v: isinstance(v, str)).all():
        raise ValueError('Load zone IDs as strings to preserve identifiers')
    for name, frame in [('objects', objects), ('zones', zones)]:
        if frame.crs is None:
            raise ValueError(f'{name}: missing CRS; do not infer it')
        if frame.geometry.isna().any() or frame.geometry.is_empty.any() or not frame.geometry.is_valid.all():
            raise ValueError(f'{name}: null, empty or invalid geometry requires an explicit quality decision')
    if not zones.geom_type.isin(['Polygon', 'MultiPolygon']).all() or zones.empty:
        raise ValueError('Nonempty polygon zones are required')
    if not objects.geom_type.isin(['Point', 'MultiPoint', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']).all():
        raise ValueError('Unsupported object geometry')
    ids = list(range(len(objects)))
    if object_id:
        if object_id not in objects or objects[object_id].isna().any() or not objects[object_id].is_unique:
            raise ValueError('Object IDs must exist, be unique and non-null')
        ids = objects[object_id].astype(str).tolist()
        if len(set(ids)) != len(ids):
            raise ValueError('Object IDs collide when serialized as strings')
    reserved = {'count', 'valid', 'missing', 'sum', 'mean', 'ratio'}
    if zone_id in reserved:
        raise ValueError('Zone ID name conflicts with an output statistic')
    # Reset positional indices and isolate internal names from user column collisions.
    left = gpd.GeoDataFrame({'_row': range(len(objects))}, geometry=list(objects.geometry), crs=objects.crs)
    right = gpd.GeoDataFrame({'_zone': zones[zone_id].tolist()}, geometry=list(zones.geometry), crs=zones.crs)
    if left.crs != right.crs:
        left = left.to_crs(right.crs)
    if field:
        if field not in objects or not pd.api.types.is_numeric_dtype(objects[field]) or pd.api.types.is_bool_dtype(objects[field]):
            raise ValueError('Measure field must have a numeric dtype; inspect/convert separately')
        values = objects[field].astype(float)
        if values.isin([float('inf'), -float('inf')]).any():
            raise ValueError('Infinite measures are not accepted')
        left['_value'] = values.to_numpy()
    matched = gpd.sjoin(left, right, how='inner', predicate=predicate).sort_values(['_row', '_zone'])
    multiplicity = matched.groupby('_row').size()
    unmatched = [i for i in range(len(objects)) if i not in multiplicity.index]
    multiple = multiplicity[multiplicity > 1].index.tolist()
    if multiple and policy == 'error':
        raise ValueError(f'{len(multiple)} objects match multiple zones; choose an explicit assignment policy')
    if policy == 'lowest-id':
        matched = matched.drop_duplicates('_row', keep='first')
    # Output intentionally contains IDs, zone geometry and derived fields only.
    result = zones[[zone_id, zones.geometry.name]].copy().reset_index(drop=True)
    counts = matched.groupby('_zone').size()
    result['count'] = result[zone_id].map(counts).fillna(0).astype('int64')
    if field:
        groups = matched.groupby('_zone')['_value']
        result['valid'] = result[zone_id].map(groups.count()).fillna(0).astype('int64')
        result['missing'] = result['count'] - result['valid']
        result['sum'] = result[zone_id].map(groups.sum(min_count=1))
        result.loc[result['count'] == 0, 'sum'] = 0.0
        result['mean'] = result[zone_id].map(groups.mean())
    if denominator:
        if denominator not in zones or numerator not in ('count', 'sum') or numerator not in result:
            raise ValueError('Supply a zone denominator and a valid count/sum numerator')
        denom = zones[denominator].reset_index(drop=True)
        if not pd.api.types.is_numeric_dtype(denom) or (denom.dropna() < 0).any() or denom.isin([float('inf'), -float('inf')]).any():
            raise ValueError('Denominator must be numeric, finite and nonnegative, or null')
        result['ratio'] = result[numerator] / denom.where(denom > 0)
    for col in ['sum', 'mean', 'ratio']:
        if col in result and result[col].isin([float('inf'), -float('inf')]).any():
            raise ValueError(f'{col}: numeric overflow; no result exported')
    report = {'objects': len(objects), 'zones': len(zones), 'matched_objects': len(multiplicity),
              'assignments': len(matched), 'unmatched_ids': [ids[i] for i in unmatched],
              'multiple_match_ids': [ids[i] for i in multiple], 'id_basis': object_id or 'zero-based source row',
              'predicate': predicate, 'policy': policy, 'field': field,
              'object_crs': str(objects.crs), 'output_crs': str(zones.crs),
              'denominator': denominator, 'numerator': numerator if denominator else None,
              'undefined_ratios': int(result['ratio'].isna().sum()) if denominator else None,
              'geopandas': gpd.__version__, 'pandas': pd.__version__}
    assert report['matched_objects'] + len(unmatched) == len(objects)
    assert int(result['count'].sum()) == report['assignments']
    if policy != 'all':
        assert report['assignments'] == report['matched_objects']
    return result, report


def export(result, report, directory, zone_id):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    result.to_file(directory/'indicators.gpkg', layer='indicators', driver='GPKG', index=False)
    result.drop(columns=result.geometry.name).to_csv(directory/'indicators.csv', index=False, na_rep='')
    (directory/'audit.json').write_text(json.dumps(report, allow_nan=False, indent=2)+'\n')
    reopened = gpd.read_file(directory/'indicators.gpkg', layer='indicators')
    csv = pd.read_csv(directory/'indicators.csv', dtype={zone_id: 'string'}, keep_default_na=False)
    if len(reopened) != len(result) or reopened.crs != result.crs or reopened[zone_id].tolist() != result[zone_id].tolist():
        raise ValueError('GeoPackage round-trip failed')
    if csv[zone_id].tolist() != result[zone_id].tolist() or int(csv['count'].sum()) != report['assignments']:
        raise ValueError('CSV reconciliation failed')
    if not reopened.geometry.geom_equals(result.geometry).all():
        raise ValueError('Zone geometry changed on export')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('objects', 'zones', 'output'):
        parser.add_argument(name)
    for name in ('objects-layer', 'zones-layer', 'zone-id'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--field')
    parser.add_argument('--object-id')
    parser.add_argument('--predicate', choices=['within', 'intersects'], default='within')
    parser.add_argument('--policy', choices=['error', 'all', 'lowest-id'], default='error')
    parser.add_argument('--denominator')
    parser.add_argument('--numerator', choices=['count', 'sum'], default='count')
    args = parser.parse_args()
    objects = gpd.read_file(args.objects, layer=args.objects_layer)
    zones = gpd.read_file(args.zones, layer=args.zones_layer)
    result, report = aggregate(objects, zones, args.zone_id, field=args.field, object_id=args.object_id,
                               predicate=args.predicate, policy=args.policy,
                               denominator=args.denominator, numerator=args.numerator)
    report['sources'] = {'objects': args.objects, 'objects_layer': args.objects_layer,
                         'zones': args.zones, 'zones_layer': args.zones_layer}
    export(result, report, args.output, args.zone_id)
    print(json.dumps(report, allow_nan=False, indent=2))


if __name__ == '__main__':
    main()
