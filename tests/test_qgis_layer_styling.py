"""Real QML artifacts checked through independent PyQGIS layer instances."""
from pathlib import Path
import tempfile
import unittest
from qgis_test_support import qgis_app, load_helper, vector_fixture, ROOT


class QMLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qgis_app()
        cls.helper = load_helper('qgis-layer-styling', '5-publish', 'style_layer.py')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)

    def fresh(self, source, output):
        from qgis.core import QgsVectorLayer
        layer = QgsVectorLayer(source, 'reopened', 'ogr')
        message, ok = layer.loadNamedStyle(str(output))
        self.assertTrue(ok, message)
        return layer

    def test_transparent_polygon_red_outline_and_source_unchanged(self):
        from qgis.PyQt.QtCore import Qt
        source = ROOT/'tests/data/saint_mande.geojson'
        before = source.read_bytes()
        output = self.dir/'polygon.qml'
        report = self.helper.style_layer(str(source), output,
                 {'mode': 'single', 'color': '#ff0000', 'no_fill': True, 'size': .4})
        layer = self.fresh(str(source), output)
        symbol = layer.renderer().symbol().symbolLayer(0)
        self.assertEqual(symbol.brushStyle(), Qt.NoBrush)
        self.assertEqual(symbol.strokeColor().name(), '#ff0000')
        self.assertAlmostEqual(symbol.strokeWidth(), .4)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(report['renderer'], 'singleSymbol')

    def test_point_and_line_units(self):
        from qgis.core import Qgis
        for kind in ['Point', 'LineString']:
            source = vector_fixture(self.dir/(kind+'.geojson'), kind)
            output = self.dir/(kind+'.qml')
            self.helper.style_layer(source, output, {'size': 3, 'units': 'map', 'opacity': .6})
            symbol = self.fresh(source, output).renderer().symbol().clone()
            self.assertEqual(symbol.outputUnit(), Qgis.RenderUnit.MapUnits)
            self.assertAlmostEqual(symbol.opacity(), .6)
            self.assertEqual(symbol.size() if kind == 'Point' else symbol.width(), 3)

    def test_categories_and_fallback(self):
        source = vector_fixture(self.dir/'categories.geojson')
        output = self.dir/'categories.qml'
        report = self.helper.style_layer(source, output, {'mode': 'categorized', 'field': 'category'})
        layer = self.fresh(source, output)
        renderer = layer.renderer()
        self.assertEqual(renderer.classAttribute(), 'category')
        self.assertEqual(len(renderer.categories()), 4)
        self.assertEqual([c.value() for c in renderer.categories()[:3]], ['0', '10', '20'])
        self.assertEqual(renderer.categories()[-1].label(), 'Missing / other')
        self.assertEqual(report['null_values'], 1)

    def test_graduated_ranges_and_boundaries(self):
        source = vector_fixture(self.dir/'numeric.geojson')
        output = self.dir/'numeric.qml'
        report = self.helper.style_layer(source, output, {'mode': 'graduated', 'field': 'value',
                               'breaks': [0, 10, 20], 'colors': ['#ffffff', '#000000']})
        layer = self.fresh(source, output)
        renderer = layer.renderer()
        self.assertEqual(renderer.classAttribute(), 'value')
        self.assertEqual([(r.lowerValue(), r.upperValue()) for r in renderer.ranges()], [(0, 10), (10, 20)])
        self.assertEqual(renderer.symbolForValue(10).color().name(), '#ffffff')
        self.assertEqual(renderer.symbolForValue(20).color().name(), '#000000')
        self.assertEqual(report['null_policy'], 'not rendered')

    def test_reject_unknown_fields_types_breaks_and_existing_output(self):
        source = vector_fixture(self.dir/'numeric.geojson')
        for spec in [{'mode': 'categorized', 'field': 'absent'},
                     {'mode': 'graduated', 'field': 'category', 'breaks': [0, 20], 'colors': ['red']},
                     {'mode': 'graduated', 'field': 'value', 'breaks': [0, 10, 10, 20]},
                     {'mode': 'graduated', 'field': 'value', 'breaks': [0, 10], 'colors': ['red']}]:
            output = self.dir/'invalid.qml'
            with self.assertRaises(ValueError):
                self.helper.style_layer(source, output, spec)
            self.assertFalse(output.exists())
        empty = vector_fixture(self.dir/'empty.geojson', values=())
        with self.assertRaises(ValueError):
            self.helper.style_layer(empty, self.dir/'empty.qml', {})
        output = self.dir/'existing.qml'
        output.write_text('keep')
        with self.assertRaises(ValueError):
            self.helper.style_layer(source, output, {})
        self.assertEqual(output.read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
