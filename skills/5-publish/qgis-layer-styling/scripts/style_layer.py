"""Create and independently reload local vector QML with QGIS 3.34–3.x."""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile


def style_layer(source, output, spec):
    from qgis.core import (Qgis, QgsVectorLayer, QgsSymbol, QgsSingleSymbolRenderer,
                           QgsCategorizedSymbolRenderer, QgsRendererCategory,
                           QgsGraduatedSymbolRenderer, QgsRendererRange, QgsVariantUtils)
    from qgis.PyQt.QtGui import QColor
    if not 33400 <= Qgis.QGIS_VERSION_INT < 40000:
        raise ValueError('This helper supports QGIS 3.34–3.x; verify APIs before using QGIS 4')
    path = Path(source.split('|')[0])
    if not path.is_file():
        raise ValueError('An existing local vector source is required')
    output = Path(output)
    if output.suffix.lower() != '.qml' or output.exists():
        raise ValueError('Choose an unused .qml output path')
    layer = QgsVectorLayer(source, 'source', 'ogr')
    if not layer.isValid() or layer.featureCount() <= 0 or layer.geometryType() not in (0, 1, 2):
        raise ValueError('Expected a valid, nonempty point, line or polygon layer')
    mode = spec.get('mode', 'single')
    field = spec.get('field')
    values = []
    if mode != 'single':
        idx = layer.fields().indexFromName(field or '')
        if idx < 0:
            raise ValueError('Renderer field is absent; inspect layer fields')
        values = [f[idx] for f in layer.getFeatures()]
    missing = sum(QgsVariantUtils.isNull(v) for v in values)
    unit_name = spec.get('units', 'mm')
    if unit_name not in ('mm', 'map'):
        raise ValueError('units must be mm or map (layer/project CRS units, not assumed metres)')
    unit = Qgis.RenderUnit.Millimeters if unit_name == 'mm' else Qgis.RenderUnit.MapUnits
    opacity = float(spec.get('opacity', 1))
    size = float(spec.get('size', 2 if layer.geometryType() == 0 else .3))
    if not 0 <= opacity <= 1 or not math.isfinite(size) or size <= 0:
        raise ValueError('Invalid opacity or size')

    def symbol(color):
        col = QColor(color)
        if not col.isValid():
            raise ValueError('Invalid symbol color')
        sym = QgsSymbol.defaultSymbol(layer.geometryType())
        sym.setColor(col)
        sym.setOpacity(opacity)
        sym.setOutputUnit(unit)
        if layer.geometryType() == 0:
            sym.setSize(size)
        elif layer.geometryType() == 1:
            sym.setWidth(size)
        else:
            outline = QColor(spec.get('outline', color))
            if not outline.isValid():
                raise ValueError('Invalid outline color')
            sl = sym.symbolLayer(0)
            sl.setStrokeColor(outline)
            sl.setStrokeWidth(size)
            if spec.get('no_fill', False):
                from qgis.PyQt.QtCore import Qt
                sl.setBrushStyle(Qt.NoBrush)
        return sym

    if mode == 'single':
        renderer = QgsSingleSymbolRenderer(symbol(spec.get('color', '#d73027')))
    elif mode == 'categorized':
        distinct = sorted({v for v in values if not QgsVariantUtils.isNull(v)}, key=lambda v: (type(v).__name__, str(v)))
        colors = spec.get('colors', ['#4575b4', '#d73027', '#66bd63', '#fdae61'])
        if not colors or len(distinct) > 100:
            raise ValueError('Provide colors and at most 100 categories; group explicitly otherwise')
        categories = [QgsRendererCategory(v, symbol(colors[i % len(colors)]), str(v)) for i, v in enumerate(distinct)]
        categories.append(QgsRendererCategory(None, symbol(spec.get('fallback', '#999999')), 'Missing / other'))
        renderer = QgsCategorizedSymbolRenderer(field, categories)
    elif mode == 'graduated':
        if not layer.fields().at(idx).isNumeric():
            raise ValueError('Graduated rendering requires a numeric field')
        finite = [float(v) for v in values if not QgsVariantUtils.isNull(v)]
        if not finite or not all(math.isfinite(v) for v in finite):
            raise ValueError('Graduated values must include finite numbers and no infinity')
        breaks = [float(v) for v in spec.get('breaks', [])]
        if len(breaks) < 2 or not all(math.isfinite(v) for v in breaks) or any(a >= b for a, b in zip(breaks, breaks[1:])):
            raise ValueError('Supply strictly increasing finite breaks including both endpoints')
        if min(finite) < breaks[0] or max(finite) > breaks[-1]:
            raise ValueError('Breaks do not cover all observed values')
        colors = spec.get('colors', [])
        if len(colors) != len(breaks)-1:
            raise ValueError('Provide exactly one color per interval')
        ranges = [QgsRendererRange(a, b, symbol(c), f'{a:g} – {b:g}')
                  for a, b, c in zip(breaks, breaks[1:], colors)]
        renderer = QgsGraduatedSymbolRenderer(field, ranges)
    else:
        raise ValueError('mode must be single, categorized or graduated')
    layer.setRenderer(renderer)

    def fingerprint(obj):
        ren = obj.renderer()
        from qgis.core import QgsReadWriteContext
        from qgis.PyQt.QtXml import QDomDocument
        doc = QDomDocument('renderer')
        doc.appendChild(ren.save(doc, QgsReadWriteContext()))
        return doc.toString()

    expected = fingerprint(layer)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        qml = str(Path(temporary)/'style.qml')
        message, ok = layer.saveNamedStyle(qml)
        if not ok:
            raise ValueError(f'QML save failed: {message}')
        fresh = QgsVectorLayer(source, 'verification', 'ogr')
        message, ok = fresh.loadNamedStyle(qml)
        if not ok or not fresh.isValid() or fingerprint(fresh) != expected:
            raise ValueError(f'Renderer round-trip failed: {message}')
        with output.open('xb') as stream:
            stream.write(Path(qml).read_bytes())
    return {'source': source, 'output': str(output), 'qgis': Qgis.QGIS_VERSION,
            'features': layer.featureCount(), 'crs': layer.crs().authid(),
            'renderer': renderer.type(), 'field': field, 'specification': spec,
            'units': unit_name, 'null_values': missing,
            'null_policy': 'not rendered' if mode == 'graduated' else 'missing / other category' if mode == 'categorized' else 'same symbol',
            'validation': 'fresh layer renderer XML matches before and after QML reload'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='local OGR URI, with discovered layername for GeoPackage')
    parser.add_argument('output')
    parser.add_argument('--spec', required=True, help='JSON rendering specification file')
    args = parser.parse_args()
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    try:
        from qgis.core import QgsApplication
    except ImportError:
        parser.exit(2, 'PyQGIS is missing: use the Python shipped with an existing QGIS installation.\n')
    app = QgsApplication([], False)
    app.initQgis()
    try:
        print(json.dumps(style_layer(args.source, args.output, json.loads(Path(args.spec).read_text())), allow_nan=False, indent=2))
    finally:
        app.exitQgis()


if __name__ == '__main__':
    main()
