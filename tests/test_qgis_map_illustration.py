"""Render real QGIS styling and visible layer state without rewriting the project."""
from pathlib import Path
import tempfile
import unittest

from qgis_test_support import qgis_app, load_helper, vector_fixture


class QGISIllustrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qgis_app()
        cls.helper = load_helper('map-illustration', '5-publish', 'export_qgis.py')

    def test_png_preserves_visible_style_order_extent_and_source_bytes(self):
        from qgis.core import QgsProject, QgsVectorLayer, QgsReferencedRectangle, QgsRectangle
        from qgis.PyQt.QtGui import QColor, QImage
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = Path(vector_fixture(root/'area.geojson', 'Polygon'))
            layer = QgsVectorLayer(str(source), 'Visible area', 'ogr')
            layer.renderer().symbol().setColor(QColor('#ff0000'))
            hidden = QgsVectorLayer(str(source), 'Hidden area', 'ogr')
            hidden.renderer().symbol().setColor(QColor('#0000ff'))
            project = QgsProject()
            project.addMapLayer(layer)
            project.addMapLayer(hidden)
            project.layerTreeRoot().findLayer(hidden.id()).setItemVisibilityChecked(False)
            project.setCrs(layer.crs())
            project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(2.395,48.795,2.415,48.815), layer.crs()))
            project_path = root/'existing.qgz'
            self.assertTrue(project.write(str(project_path)))
            before = {p: p.read_bytes() for p in (source, project_path)}
            report = self.helper.export_project(project_path, root/'render', title='Test area', source_note='Source: synthetic')
            image = QImage(str(root/'render/map.png'))
            self.assertEqual((image.width(), image.height()), (1400,1000))
            colours = [image.pixelColor(x,y) for x in range(50,1350,10) for y in range(80,920,10)]
            self.assertTrue(any(c.red() > 200 and c.green() < 50 and c.blue() < 50 for c in colours))
            self.assertFalse(any(c.blue() > 200 and c.red() < 50 and c.green() < 50 for c in colours))
            self.assertEqual(report['layers_top_first'], ['Visible area'])
            self.assertEqual(report['renderer_errors'], 0)
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            with self.assertRaises(ValueError):
                self.helper.export_project(project_path, root/'render', title='Test', source_note='Source')

    def test_unusable_project_is_not_exported_as_a_blank_map(self):
        from qgis.core import QgsProject
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = QgsProject()
            source = root/'empty.qgs'
            self.assertTrue(project.write(str(source)))
            with self.assertRaises(ValueError):
                self.helper.export_project(source, root/'render', title='Test', source_note='Source')
            self.assertFalse((root/'render').exists())


if __name__ == '__main__':
    unittest.main()
