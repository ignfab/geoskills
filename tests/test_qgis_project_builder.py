"""Real QGZ/QGS round trips, bundle relocation and controlled remote failure."""
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile
from qgis_test_support import qgis_app, load_helper, vector_fixture


class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qgis_app()
        cls.helper = load_helper('qgis-project-builder', '5-publish', 'build_project.py')

    def setUp(self):
        from osgeo import gdal, osr
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'bundle'
        (self.root/'data').mkdir(parents=True)
        self.vector = Path(vector_fixture(self.root/'data/boundary.geojson', 'Polygon'))
        self.raster = self.root/'data/elevation.tif'
        raster = gdal.GetDriverByName('GTiff').Create(str(self.raster), 2, 2, 1, gdal.GDT_Float32)
        raster.SetGeoTransform([2.4, .005, 0, 48.81, 0, -.005])
        crs = osr.SpatialReference()
        crs.ImportFromEPSG(4326)
        raster.SetProjection(crs.ExportToWkt())
        raster.GetRasterBand(1).Fill(12)
        raster = None
        self.config = {'crs': 'EPSG:2154', 'require_portable': True,
                       'layers': [
                           {'source': str(self.vector), 'name': 'Boundary', 'group': 'Study'},
                           {'source': str(self.raster), 'kind': 'raster', 'name': 'Terrain', 'group': 'Study', 'visible': False}]}

    def reopen(self, path):
        from qgis.core import QgsProject
        project = QgsProject()
        self.assertTrue(project.read(str(path)))
        self.assertTrue(all(layer.isValid() for layer in project.mapLayers().values()))
        return project

    def test_vector_raster_crs_order_visibility_extent_and_sources(self):
        before = [p.read_bytes() for p in [self.vector, self.raster]]
        files_before = set((self.root/'data').iterdir())
        self.config['extent'] = [650000, 6850000, 660000, 6870000]
        output = self.root/'map.qgz'
        report = self.helper.build_project(self.config, output)
        project = self.reopen(output)
        nodes = project.layerTreeRoot().findLayers()
        self.assertEqual([n.layer().name() for n in nodes], ['Boundary', 'Terrain'])
        self.assertEqual([n.itemVisibilityChecked() for n in nodes], [True, False])
        self.assertEqual([n.parent().name() for n in nodes], ['Study', 'Study'])
        self.assertEqual(project.crs().authid(), 'EPSG:2154')
        box = project.viewSettings().defaultViewExtent()
        self.assertEqual([box.xMinimum(), box.yMinimum(), box.xMaximum(), box.yMaximum()], self.config['extent'])
        self.assertEqual(nodes[0].layer().featureCount(), 4)
        self.assertEqual(nodes[1].layer().width(), 2)
        self.assertTrue(report['portable_bundle'])
        self.assertEqual([p.read_bytes() for p in [self.vector, self.raster]], before)
        self.assertEqual(set((self.root/'data').iterdir()), files_before)
        with zipfile.ZipFile(output) as archive:
            member = next(n for n in archive.namelist() if n.endswith('.qgs'))
            tree = ET.fromstring(archive.read(member))
        self.assertTrue(all(n.text.startswith('./data/') for n in tree.findall('.//projectlayers/maplayer/datasource')))

    def test_utm_and_custom_project_crs_survive_roundtrip(self):
        from osgeo import osr
        from qgis.core import QgsCoordinateReferenceSystem
        custom = QgsCoordinateReferenceSystem.fromProj(
            '+proj=tmerc +lat_0=48.8123 +lon_0=2.4567 +k=0.9999 +x_0=1234 +y_0=5678 +ellps=GRS80 +units=m +no_defs')
        self.assertTrue(custom.isValid())
        self.assertFalse(custom.authid())
        for name, crs in [('utm', QgsCoordinateReferenceSystem('EPSG:32631')), ('custom', custom)]:
            with self.subTest(name=name):
                self.config['crs'] = crs.toWkt()
                output = self.root/f'{name}.qgz'
                report = self.helper.build_project(self.config, output)
                project = self.reopen(output)
                expected = osr.SpatialReference(wkt=crs.toWkt())
                self.assertTrue(expected.IsSame(osr.SpatialReference(wkt=project.crs().toWkt())))
                self.assertTrue(expected.IsSame(osr.SpatialReference(wkt=report['validated']['crs_wkt'])))
                self.assertTrue(report['validated']['crs_wkt'])
                for layer in project.mapLayers().values():
                    self.assertEqual(layer.crs().authid(), 'EPSG:4326')

    def test_moving_whole_bundle_keeps_sources(self):
        output = self.root/'map.qgz'
        self.helper.build_project(self.config, output)
        moved = self.root.parent/'moved'
        shutil.move(self.root, moved)
        project = self.reopen(moved/'map.qgz')
        self.assertFalse(self.root.exists())
        for layer in project.mapLayers().values():
            self.assertTrue(Path(layer.source().split('|')[0]).is_relative_to(moved))

    def test_changed_custom_crs_is_rejected_even_without_authority_ids(self):
        from qgis.core import QgsCoordinateReferenceSystem, QgsProject
        definition = '+proj=tmerc +lat_0=48.8123 +lon_0={lon} +k=0.9999 +x_0=1234 +y_0=5678 +ellps=GRS80 +units=m +no_defs'
        intended = QgsCoordinateReferenceSystem.fromProj(definition.format(lon=2.4567))
        changed = QgsCoordinateReferenceSystem.fromProj(definition.format(lon=3.4567))
        self.assertFalse(intended.authid())
        self.assertFalse(changed.authid())
        self.config['crs'] = intended.toWkt()
        original_read = QgsProject.read

        def altered_read(project, path):
            success = original_read(project, path)
            project.setCrs(changed)
            return success

        output = self.root/'changed.qgz'
        with patch.object(QgsProject, 'read', altered_read):
            with self.assertRaisesRegex(ValueError, 'round-trip'):
                self.helper.build_project(self.config, output)
        self.assertFalse(output.exists())

    def test_existing_style_without_styling_skill(self):
        from qgis.core import QgsVectorLayer
        from qgis.PyQt.QtGui import QColor
        source = QgsVectorLayer(str(self.vector), 'styled', 'ogr')
        source.renderer().symbol().setColor(QColor('#123456'))
        qml = self.root/'existing.qml'
        self.assertTrue(source.saveNamedStyle(str(qml))[1])
        self.config['layers'][0]['qml'] = str(qml)
        output = self.root/'map.qgs'
        self.helper.build_project(self.config, output)
        project = self.reopen(output)
        layer = project.layerTreeRoot().findLayers()[0].layer()
        self.assertEqual(layer.renderer().symbol().color().name(), '#123456')

    def test_missing_source_unknown_gpkg_layer_and_existing_output(self):
        from osgeo import ogr
        output = self.root/'map.qgz'
        self.config['layers'][0]['source'] = str(self.root/'missing.geojson')
        with self.assertRaises(ValueError): self.helper.build_project(self.config, output)
        self.assertFalse(output.exists())
        gpkg = self.root/'data/points.gpkg'
        ds = ogr.GetDriverByName('GPKG').CreateDataSource(str(gpkg))
        ds.CreateLayer('known', geom_type=ogr.wkbPoint)
        ds = None
        self.config['layers'][0].update(source=str(gpkg), layer='unknown')
        with self.assertRaises(ValueError): self.helper.build_project(self.config, output)
        output.write_bytes(b'keep')
        with self.assertRaises(ValueError): self.helper.build_project(self.config, output)
        self.assertEqual(output.read_bytes(), b'keep')

    def test_offline_wmts_preserves_local_project(self):
        self.config['wmts'] = [{'name': 'Unavailable', 'url': 'https://example.invalid/wmts',
                               'layer': 'missing', 'style': 'normal', 'format': 'image/png',
                               'tile_matrix_set': 'matrix', 'crs': 'EPSG:3857'}]
        with patch.object(self.helper, 'urlopen', side_effect=OSError('offline')):
            report = self.helper.build_project(self.config, self.root/'offline.qgz')
        self.assertEqual(report['remote_layers'], [])
        self.assertTrue(report['warnings'])
        self.assertEqual(len(self.reopen(self.root/'offline.qgz').mapLayers()), 2)

    def test_credentials_and_malformed_metadata_never_embedded(self):
        for url in ['https://example.invalid/wmts?token=PRIVATE', 'https://user:PRIVATE@example.invalid/wmts']:
            self.config['wmts'] = [{'name': 'Basemap', 'url': url}]
            with patch.object(self.helper, 'urlopen', side_effect=AssertionError('must not request')):
                output = self.root/('safe'+str(len(url))+'.qgs')
                report = self.helper.build_project(self.config, output)
            self.assertNotIn('PRIVATE', output.read_text())
            self.assertNotIn('PRIVATE', json.dumps(report))
        item = {'name': 'Bad XML', 'url': 'https://example.invalid/wmts'}
        with patch.object(self.helper, 'urlopen', return_value=io.BytesIO(b'<ExceptionReport/>')):
            with self.assertRaisesRegex(ValueError, 'WMTS capabilities'):
                self.helper.wmts_layer(item)

    def test_collinear_points_expand_default_extent(self):
        path = self.root/'data/aligned.geojson'
        path.write_text(json.dumps({'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'properties': {}, 'geometry': {'type': 'Point', 'coordinates': [x, 48.8]}}
            for x in [2.4, 2.8]]}))
        self.config['layers'].insert(0, {'source': str(path), 'name': 'Aligned', 'group': 'Study'})
        self.config['crs'] = 'EPSG:4326'
        report = self.helper.build_project(self.config, self.root/'aligned.qgz')
        self.assertGreater(report['validated']['extent'][2], 2.8)

    def test_wmts_uri_retains_capabilities_request(self):
        from urllib.parse import parse_qs, urlsplit
        from qgis.core import QgsCoordinateReferenceSystem
        xml = b'''<Capabilities xmlns="http://www.opengis.net/wmts/1.0" xmlns:ows="http://www.opengis.net/ows/1.1">
          <Contents><Layer><ows:Identifier>test</ows:Identifier><Style><ows:Identifier>normal</ows:Identifier></Style>
          <Format>image/png</Format><TileMatrixSetLink><TileMatrixSet>matrix</TileMatrixSet></TileMatrixSetLink></Layer>
          <TileMatrixSet><ows:Identifier>matrix</ows:Identifier><ows:SupportedCRS>EPSG:3857</ows:SupportedCRS>
          <TileMatrix><ows:Identifier>0</ows:Identifier></TileMatrix></TileMatrixSet></Contents></Capabilities>'''
        item = {'url': 'https://example.invalid/wmts', 'name': 'Test', 'layer': 'test', 'style': 'normal',
                'format': 'image/png', 'tile_matrix_set': 'matrix', 'crs': 'EPSG:3857'}
        with patch.object(self.helper, 'urlopen', return_value=io.BytesIO(xml)), patch('qgis.core.QgsRasterLayer') as provider:
            provider.return_value.isValid.return_value = True
            provider.return_value.crs.return_value = QgsCoordinateReferenceSystem('EPSG:3857')
            self.helper.wmts_layer(item)
        provider_uri = provider.call_args.args[0]
        self.assertIn('crs=EPSG:3857', provider_uri)
        self.assertIn('format=image/png', provider_uri)
        params = parse_qs(provider_uri)
        service_request = parse_qs(urlsplit(params['url'][0]).query)
        self.assertEqual(service_request['SERVICE'], ['WMTS'])
        self.assertEqual(service_request['REQUEST'], ['GetCapabilities'])
        self.assertEqual(params['tileMatrixSet'], ['matrix'])

    def test_builder_suppresses_raster_sidecars_and_restores_gdal_setting(self):
        from osgeo import gdal
        before = set((self.root/'data').iterdir())
        previous = gdal.GetConfigOption('GDAL_PAM_ENABLED')
        gdal.SetConfigOption('GDAL_PAM_ENABLED', 'YES')
        try:
            self.helper.build_project(self.config, self.root/'pam.qgz')
            self.assertEqual(gdal.GetConfigOption('GDAL_PAM_ENABLED'), 'YES')
            self.assertEqual(set((self.root/'data').iterdir()), before)
        finally:
            gdal.SetConfigOption('GDAL_PAM_ENABLED', previous)

    def test_portability_requires_contained_sources_and_valid_extent(self):
        with self.assertRaises(ValueError):
            self.helper.build_project(self.config, self.root/'subdir/map.qgz')
        self.config['extent'] = [1, 2, 1, 2]
        with self.assertRaises(ValueError):
            self.helper.build_project(self.config, self.root/'bad.qgz')


if __name__ == '__main__':
    unittest.main()
