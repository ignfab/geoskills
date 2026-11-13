#!/usr/bin/env python3
"""Small static-first vector illustration; optional HTML with explicit external assets."""
import argparse
import html
import json
from pathlib import Path
import textwrap


def illustrate(frame, output, *, crs=None, title, source_note, column=None, units=None,
               formats=('png',), tooltip=(), width=1400, height=1000, dpi=140):
    import geopandas as gpd
    import numpy as np
    import pandas as pd
    from pyproj import CRS

    output = Path(output)
    formats = tuple(formats)
    if output.exists():
        raise ValueError('Output directory must be new')
    if not formats or len(set(formats)) != len(formats) or not set(formats) <= {'png', 'svg', 'pdf', 'html'}:
        raise ValueError('Choose distinct formats from png, svg, pdf, html')
    if not title.strip() or not source_note.strip():
        raise ValueError('A title and source note are required')
    if not (400 <= width <= 4000 and 300 <= height <= 4000 and 72 <= dpi <= 600):
        raise ValueError('Use a bounded canvas: 400–4000 by 300–4000 pixels, 72–600 dpi')
    if frame.empty or frame.crs is None or frame.geometry.isna().any() or frame.geometry.is_empty.any():
        raise ValueError('Expected nonempty geometries with a known CRS')
    if not frame.geometry.is_valid.all():
        raise ValueError('Invalid geometry; diagnose before rendering')
    allowed = {'Point', 'MultiPoint', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon'}
    if not set(frame.geom_type) <= allowed or not np.isfinite(frame.total_bounds).all():
        raise ValueError('Unsupported geometry or nonfinite bounds')
    if any(field not in frame.columns or field in (frame.geometry.name, '_map_fill') for field in tooltip):
        raise ValueError('Tooltip fields must be existing attributes')
    if column is not None:
        if column not in frame or not pd.api.types.is_numeric_dtype(frame[column]) or pd.api.types.is_bool_dtype(frame[column]):
            raise ValueError('Colour column must be an existing numeric field')
        valid = frame[column].dropna().astype(float)
        if valid.empty or not np.isfinite(valid).all() or not units:
            raise ValueError('Numeric colour needs finite observations and stated units')
    else:
        valid = None
    static = bool(set(formats) - {'html'})
    display_crs = CRS.from_user_input(frame.crs if crs is None else crs)
    metres_per_unit = None
    if static:
        if not (display_crs.is_projected or display_crs.is_geographic):
            raise ValueError('Static recipe needs a projected or geographic display CRS')
        axes = display_crs.axis_info[:2]
        if len(axes) != 2 or any(not np.isfinite(a.unit_conversion_factor) or a.unit_conversion_factor <= 0 for a in axes):
            raise ValueError('Display CRS needs two axes with known positive unit conversions')
        if not np.isclose(axes[0].unit_conversion_factor, axes[1].unit_conversion_factor, rtol=1e-12, atol=0):
            raise ValueError('Display CRS horizontal axes must use compatible units')
        if display_crs.is_projected:
            metres_per_unit = axes[0].unit_conversion_factor
    plotted = frame.to_crs(display_crs) if static else None
    if static and not np.isfinite(plotted.total_bounds).all():
        raise ValueError('Reprojection produced nonfinite coordinates')
    report = {'features': len(frame), 'input_crs': str(frame.crs),
              'display_crs': display_crs.to_string() if static else 'EPSG:3857',
              'title': title, 'source_note': source_note, 'column': column, 'units': units,
              'null_values': int(frame[column].isna().sum()) if column else 0,
              'range': [float(valid.min()), float(valid.max())] if column else None,
              'simplification': 'none', 'formats': list(formats), 'files': {},
              'versions': {'geopandas': gpd.__version__}, 'visual_check': 'not performed by helper'}
    if static or column is not None:
        import matplotlib
        from matplotlib import colormaps, colors
        low, high = (float(valid.min()), float(valid.max())) if column else (0, 1)
        norm = colors.Normalize(low, high if high > low else low + 1)
        palette = colormaps['viridis']
        report['versions']['matplotlib'] = matplotlib.__version__
    if 'html' in formats:
        import folium
        report['versions']['folium'] = folium.__version__
    output.mkdir(parents=True)
    if static:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.patches import Patch
        from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
        fig = Figure(figsize=(width / dpi, height / dpi), dpi=dpi, facecolor='white')
        FigureCanvasAgg(fig)
        ax = fig.add_axes([.06, .16, .74 if column else .88, .69])
        if column:
            plotted.plot(ax=ax, column=column, cmap=palette, norm=norm, linewidth=.65, aspect=None,
                         missing_kwds={'color': '#d1d5db', 'label': 'No data'})
            from matplotlib.cm import ScalarMappable
            cax = fig.add_axes([.85, .24, .018, .47])
            bar = fig.colorbar(ScalarMappable(norm=norm, cmap=palette), cax=cax, label=f'{column} ({units})')
            if low == high:
                bar.set_ticks([low])
            if report['null_values']:
                fig.legend(handles=[Patch(facecolor='#d1d5db', label='No data')], loc='upper left',
                           bbox_to_anchor=(.82, .2), fontsize=8, frameon=False)
        else:
            plotted.plot(ax=ax, color='#237a8a', linewidth=1.1, aspect=None)
        xmin, ymin, xmax, ymax = plotted.total_bounds
        extent_span = max(xmax-xmin, ymax-ymin)
        # A one-unit minimum would add a degree-wide margin around a small geographic map.
        margin = (extent_span if extent_span > 0 else 1e-3 if display_crs.is_geographic else 1) * .06
        ax.set_xlim(xmin-margin, xmax+margin)
        ax.set_ylim(ymin-margin, ymax+margin)
        ax.set_aspect('equal')
        ax.set_axis_off()
        report['scale_bar'] = None
        if metres_per_unit is not None:
            span_m = (xmax-xmin+2*margin) / 4 * metres_per_unit
            power = 10 ** np.floor(np.log10(span_m))
            scale_m = max(value * power for value in (1, 2, 5) if value * power <= span_m)
            scale = scale_m / metres_per_unit
            ax.add_artist(AnchoredSizeBar(ax.transData, scale, f'{scale_m:g} m', 'upper left',
                                         bbox_to_anchor=(0, -.035), bbox_transform=ax.transAxes,
                                         frameon=False, borderpad=0, pad=.2, color='#263238', size_vertical=0))
            report['scale_bar'] = {'length_m': float(scale_m), 'length_crs_units': float(scale),
                                   'metres_per_unit': float(metres_per_unit), 'basis': 'projected grid distance'}
        else:
            report['scale_bar_note'] = 'Omitted for geographic coordinates; angular units are not metres.'
        fig.text(.06, .94, textwrap.fill(title, 65), fontsize=15, weight='bold', va='top')
        fig.text(.06, .07, textwrap.fill(source_note, 100), fontsize=8, color='#475569', va='top')
        for extension in formats:
            if extension != 'html':
                fig.savefig(output / f'map.{extension}', dpi=dpi, facecolor='white')
        report['pixels'] = [width, height]
        report['dpi'] = dpi
        report['bounds'] = [float(x) for x in plotted.total_bounds]
        fig.clear()
    if 'html' in formats:
        web = frame.to_crs(4326)
        bounds = web.total_bounds
        if not np.isfinite(bounds).all() or bounds[0] < -180 or bounds[2] > 180 or bounds[1] < -85 or bounds[3] > 85 or bounds[2]-bounds[0] > 180:
            raise ValueError('This Leaflet recipe needs a local extent away from poles/antimeridian')
        selected = web[list(dict.fromkeys(tooltip)) + [web.geometry.name]].copy()
        for field in tooltip:
            selected[field] = selected[field].map(lambda x: html.escape(str(x)) if pd.notna(x) else 'No data')
        data = json.loads(selected.to_json(drop_id=True, na='null'))
        for index, feature in enumerate(data['features']):
            value = frame.iloc[index][column] if column else None
            fill = ('#d1d5db' if pd.isna(value) else colors.to_hex(palette(norm(float(value))))) if column else '#237a8a'
            feature['properties']['_map_fill'] = fill
        m = folium.Map(tiles=None, prefer_canvas=True, control_scale=True)
        # This recipe uses no popups, Bootstrap, jQuery or AwesomeMarkers.
        m.default_js = [item for item in m.default_js if item[0] == 'leaflet']
        m.default_css = [item for item in m.default_css if item[0] == 'leaflet_css']
        if len(m.default_js) != 1 or len(m.default_css) != 1:
            raise RuntimeError('Inspect this Folium version before changing its asset list')
        folium.GeoJson(data, name='Features',
                       marker=folium.CircleMarker(radius=5, fill=True),
                       style_function=lambda f: {'color': f['properties']['_map_fill'] if 'LineString' in f['geometry']['type'] else '#334155', 'weight': 1, 'fillOpacity': .75,
                                                 'fillColor': f['properties']['_map_fill']},
                       tooltip=folium.GeoJsonTooltip(fields=list(tooltip), aliases=[html.escape(x) for x in tooltip]) if tooltip else None).add_to(m)
        folium.LayerControl().add_to(m)
        m.fit_bounds([[float(bounds[1]), float(bounds[0])], [float(bounds[3]), float(bounds[2])]], max_zoom=18)
        legend = ''
        if column:
            stops = ','.join(colors.to_hex(palette(x)) for x in np.linspace(0, 1, 5))
            legend = f'<div>{html.escape(column)} ({html.escape(units)})</div><div style="height:10px;background:linear-gradient(to right,{stops})"></div><div>{low:g} – {high:g}; grey: no data</div>'
        m.get_root().html.add_child(folium.Element(
            '<style>.leaflet-top{top:65px}.map-heading,.map-caption{position:fixed;z-index:999;background:white;padding:10px 14px;font:14px sans-serif;max-width:65%;box-shadow:0 1px 5px #999}'
            '.map-heading{top:8px;left:55px}.map-caption{bottom:25px;right:10px;font-size:12px}</style>'
            f'<div class="map-heading">{html.escape(title)}</div><div class="map-caption">{legend}{html.escape(source_note)}</div>'))
        m.save(str(output / 'map.html'))
        report['html'] = {'data_crs': 'EPSG:4326', 'display_crs': 'EPSG:3857',
                          'tooltip_fields': list(tooltip), 'tiles': None,
                          'external_assets': [url for _, url in m.default_js + m.default_css],
                          'offline': False, 'browser_check': 'not performed by helper'}
    for extension in formats:
        path = output / f'map.{extension}'
        report['files'][path.name] = path.stat().st_size
    (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--layer')
    parser.add_argument('--crs')
    parser.add_argument('--title', required=True)
    parser.add_argument('--source-note', required=True)
    parser.add_argument('--column')
    parser.add_argument('--units')
    parser.add_argument('--formats', nargs='+', default=['png'])
    parser.add_argument('--tooltip', nargs='*', default=[])
    args = parser.parse_args()
    import geopandas as gpd
    if not args.source.is_file():
        parser.error('Expected an existing local vector file')
    layers = gpd.list_layers(args.source)
    if args.layer is None and len(layers) != 1:
        parser.error('Select --layer from the discovered layer list')
    if args.layer is not None and args.layer not in set(layers['name']):
        parser.error('Unknown layer')
    frame = gpd.read_file(args.source, **({'layer': args.layer} if args.layer else {}))
    report = illustrate(frame, args.output, crs=args.crs, title=args.title,
                        source_note=args.source_note, column=args.column, units=args.units,
                        formats=args.formats, tooltip=args.tooltip)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
