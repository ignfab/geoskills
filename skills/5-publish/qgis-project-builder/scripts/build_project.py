"""Build a new local QGIS project, with optional public, discovered WMTS basemaps."""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen
import xml.etree.ElementTree as ET


def wmts_layer(item):
    """Bounded capabilities discovery; credentials/custom URL queries are unsupported."""
    from qgis.core import QgsRasterLayer, QgsCoordinateReferenceSystem, QgsDataSourceUri
    url = item['url']
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Only public HTTPS service endpoints without credentials/query/fragment are accepted')
    request = url + '?' + urlencode({'SERVICE': 'WMTS', 'REQUEST': 'GetCapabilities', 'VERSION': '1.0.0'})
    with urlopen(request, timeout=15) as response:
        raw = response.read(8 * 1024 * 1024 + 1)
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError('Capabilities exceed the bounded metadata limit')
    root = ET.fromstring(raw)
    ns = {'w': 'http://www.opengis.net/wmts/1.0', 'o': 'http://www.opengis.net/ows/1.1'}
    if root.tag != '{'+ns['w']+'}Capabilities':
        raise ValueError('Expected WMTS capabilities, not an exception or HTML response')
    layer = next((node for node in root.findall('w:Contents/w:Layer', ns)
                  if node.findtext('o:Identifier', namespaces=ns) == item['layer']), None)
    if layer is None:
        raise ValueError('Requested WMTS layer is not advertised')
    styles = [n.findtext('o:Identifier', namespaces=ns) for n in layer.findall('w:Style', ns)]
    matrices = [n.text for n in layer.findall('w:TileMatrixSetLink/w:TileMatrixSet', ns)]
    formats = [n.text for n in layer.findall('w:Format', ns)]
    if item['style'] not in styles or item['format'] not in formats or item['tile_matrix_set'] not in matrices:
        raise ValueError('Requested style, format or matrix set is not advertised')
    matrix = next((node for node in root.findall('w:Contents/w:TileMatrixSet', ns)
                   if node.findtext('o:Identifier', namespaces=ns) == item['tile_matrix_set']), None)
    if matrix is None or not matrix.findall('w:TileMatrix', ns):
        raise ValueError('Missing matrix-set definition')
    actual_crs = QgsCoordinateReferenceSystem(matrix.findtext('o:SupportedCRS', namespaces=ns))
    wanted = QgsCoordinateReferenceSystem(item['crs'])
    if not actual_crs.isValid() or actual_crs != wanted:
        raise ValueError('Matrix-set CRS differs from requested CRS')
    # QGIS distinguishes WMTS via the full capabilities URL in the provider URI.
    uri = QgsDataSourceUri()
    for key, value in {'url': request, 'layers': item['layer'], 'styles': item['style'],
                       'format': item['format'], 'crs': item['crs'], 'tileMatrixSet': item['tile_matrix_set']}.items():
        uri.setParam(key, value)
    result = QgsRasterLayer(bytes(uri.encodedUri()).decode(), item['name'], 'wms')
    if not result.isValid() or result.crs() != wanted:
        raise ValueError('WMTS provider is unavailable')
    return result


def build_project(config, output):
    # QGIS may compute raster statistics while opening a layer. Keep them in memory.
    from osgeo import gdal
    previous = gdal.GetConfigOption('GDAL_PAM_ENABLED')
    gdal.SetConfigOption('GDAL_PAM_ENABLED', 'NO')
    try:
        return _build_project(config, output)
    finally:
        gdal.SetConfigOption('GDAL_PAM_ENABLED', previous)


def _build_project(config, output):
    from qgis.core import (Qgis, QgsProject, QgsVectorLayer, QgsRasterLayer,
                           QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsRectangle,
                           QgsReferencedRectangle, QgsRenderContext, QgsReadWriteContext, QgsPointXY)
    from qgis.PyQt.QtXml import QDomDocument
    if not 33400 <= Qgis.QGIS_VERSION_INT < 40000:
        raise ValueError('This helper supports QGIS 3.34–3.x')
    output = Path(output).resolve()
    if output.exists() or output.suffix.lower() not in ('.qgz', '.qgs'):
        raise ValueError('Choose an unused .qgz or .qgs path')
    crs = QgsCoordinateReferenceSystem(config['crs'])
    if not crs.isValid():
        raise ValueError('Invalid project CRS')
    project = QgsProject()
    project.setCrs(crs)
    project.setFilePathStorage(Qgis.FilePathType.Relative)
    local = config.get('layers', [])
    if not local:
        raise ValueError('At least one existing local vector/raster layer is required')
    extent = None
    groups = {}
    previous_group = None
    local_paths = []
    warnings = []
    names = set()
    for item in local:
        path = Path(item['source']).resolve()
        if not path.is_file():
            raise ValueError('Missing local data source')
        if item['name'] in names:
            raise ValueError('Layer names must be distinct')
        names.add(item['name'])
        local_paths.append(path)
        kind = item.get('kind', 'vector')
        if kind == 'vector':
            uri = str(path)
            if path.suffix.lower() == '.gpkg' and not item.get('layer'):
                raise ValueError('GeoPackage layer name must be discovered and supplied')
            if item.get('layer'):
                uri += '|layername='+item['layer']
            layer = QgsVectorLayer(uri, item['name'], 'ogr')
        elif kind == 'raster':
            layer = QgsRasterLayer(str(path), item['name'], 'gdal')
        else:
            raise ValueError('Local kind must be vector or raster')
        if not layer.isValid() or not layer.crs().isValid():
            raise ValueError('Invalid source/layer or undeclared source CRS')
        if item.get('qml'):
            if kind != 'vector' or not Path(item['qml']).is_file():
                raise ValueError('An existing vector QML is required')
            message, ok = layer.loadNamedStyle(str(item['qml']))
            renderer = layer.renderer()
            if not ok or renderer is None:
                raise ValueError('QML could not be loaded')
            if not renderer.usedAttributes(QgsRenderContext()).issubset(set(layer.fields().names())):
                raise ValueError('QML references fields missing from the layer')
            if any(int(s.type()) != int(layer.geometryType()) for s in renderer.symbols(QgsRenderContext())):
                raise ValueError('QML symbol geometry is incompatible')
        group = item.get('group')
        if group and group in groups and previous_group != group:
            raise ValueError('Group members must be consecutive in top-to-bottom layer order')
        parent = project.layerTreeRoot()
        if group:
            if group not in groups:
                groups[group] = parent.addGroup(group)
            parent = groups[group]
        project.addMapLayer(layer, False)
        node = parent.addLayer(layer)
        node.setItemVisibilityChecked(item.get('visible', True))
        previous_group = group
        if kind == 'raster' or layer.featureCount() > 0:
            bounds = layer.extent()
            transform = QgsCoordinateTransform(layer.crs(), crs, project)
            if bounds.isEmpty():
                # A point or aligned points have zero width/height but still affect the union.
                a = transform.transform(QgsPointXY(bounds.xMinimum(), bounds.yMinimum()))
                b = transform.transform(QgsPointXY(bounds.xMaximum(), bounds.yMaximum()))
                transformed = QgsRectangle(a, b)
            else:
                transformed = transform.transformBoundingBox(bounds)
            if extent is None:
                extent = QgsRectangle(transformed)
            else:
                extent = QgsRectangle(min(extent.xMinimum(), transformed.xMinimum()),
                                      min(extent.yMinimum(), transformed.yMinimum()),
                                      max(extent.xMaximum(), transformed.xMaximum()),
                                      max(extent.yMaximum(), transformed.yMaximum()))
    portable = all(p.is_relative_to(output.parent) for p in local_paths)
    if config.get('require_portable', False) and not portable:
        raise ValueError('Portable bundle requires every local source under the project directory')
    if not portable:
        warnings.append('Move the enclosing data/project directory together; the project directory alone is not portable')
    remote_names = []
    for item in config.get('wmts', []):
        if item['name'] in names:
            raise ValueError('Layer names must be distinct')
        names.add(item['name'])
        try:
            layer = wmts_layer(item)
        except Exception:
            # URLs/errors may carry sensitive data; never echo provider or network errors.
            warnings.append('Optional WMTS omitted: metadata/provider verification failed')
            continue
        project.addMapLayer(layer, False)
        project.layerTreeRoot().addLayer(layer).setItemVisibilityChecked(item.get('visible', True))
        remote_names.append(item['name'])
    if 'extent' in config:
        box = config['extent']
        if len(box) != 4 or not all(math.isfinite(v) for v in box) or box[0] >= box[2] or box[1] >= box[3]:
            raise ValueError('Extent must be xmin,ymin,xmax,ymax in project CRS with positive width/height')
        extent = QgsRectangle(*box)
    elif extent is None or extent.isEmpty():
        raise ValueError('Supply a nonempty initial extent in the project CRS')
    else:
        extent.scale(1.05)
    project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent, crs))

    def snapshot(proj):
        items = []
        for node in proj.layerTreeRoot().findLayers():
            layer = node.layer()
            record = {'name': layer.name(), 'visible': node.itemVisibilityChecked(),
                      'group': node.parent().name(), 'valid': layer.isValid(), 'source': layer.source(),
                      'crs': layer.crs().authid()}
            if isinstance(layer, QgsVectorLayer):
                record['feature_count'] = layer.featureCount()
                doc = QDomDocument()
                doc.appendChild(layer.renderer().save(doc, QgsReadWriteContext()))
                record['renderer'] = ET.canonicalize(doc.toString())
            else:
                record['raster_size'] = [layer.width(), layer.height(), layer.bandCount()]
            items.append(record)
        box = proj.viewSettings().defaultViewExtent()
        return {'layers': items, 'crs': proj.crs().authid(), 'relative': proj.filePathStorage() == Qgis.FilePathType.Relative,
                'extent': [box.xMinimum(), box.yMinimum(), box.xMaximum(), box.yMaximum()]}

    expected = snapshot(project)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Stage in the same directory so relative paths remain unchanged on publication.
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        staged = output.parent/(Path(temporary).name+output.suffix)
        try:
            if not project.write(str(staged)):
                raise ValueError('Project write failed')
            fresh = QgsProject()
            if not fresh.read(str(staged)) or snapshot(fresh) != expected:
                raise ValueError('Fresh project round-trip failed')
            with output.open('xb') as stream:
                stream.write(staged.read_bytes())
        finally:
            staged.unlink(missing_ok=True)
    return {'output': str(output), 'qgis': Qgis.QGIS_VERSION, 'local_layers': len(local),
            'remote_layers': remote_names, 'remote_status': 'metadata/provider checked; tile rendering not verified',
            'portable_bundle': portable, 'warnings': warnings, 'validated': expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('output')
    args = parser.parse_args()
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    try:
        from qgis.core import QgsApplication
    except ImportError:
        parser.exit(2, 'PyQGIS missing: use Python from an existing QGIS installation.\n')
    config_path = Path(args.manifest).resolve()
    config = json.loads(config_path.read_text())
    for item in config.get('layers', []):
        for key in ['source', 'qml']:
            if key in item:
                item[key] = str((config_path.parent/item[key]).resolve())
    app = QgsApplication([], False)
    app.initQgis()
    try:
        print(json.dumps(build_project(config, args.output), allow_nan=False, indent=2))
    finally:
        app.exitQgis()


if __name__ == '__main__':
    main()
