"""Actual lightweight map files, bounded raster reads and explicit HTML dependencies."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from skill_examples import skill_dir, run_example

ROOT = Path(__file__).resolve().parents[1]
SKILL = skill_dir('map-illustration')


class IllustrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for name in ['geopandas', 'matplotlib', 'folium', 'PIL']:
            if importlib.util.find_spec(name) is None:
                raise unittest.SkipTest('Map illustration tests need geopandas, matplotlib, folium and Pillow')
        import geopandas as gpd
        cls.gpd = gpd
        spec = importlib.util.spec_from_file_location('render_vector', SKILL/'scripts/render_vector.py')
        cls.helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.helper)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.frame = self.gpd.read_file(ROOT/'tests/data/admin_units_synthetic.geojson')
        self.frame['indicator'] = [0, 10, None]
        self.frame['secret'] = 'DO_NOT_EXPORT_THIS'
        self.kwargs = dict(crs=2154, title='Synthetic study areas', source_note='Source: synthetic fixture; not real data')

    def test_static_png_svg_pdf_keep_values_geometry_and_dimensions(self):
        from PIL import Image
        import numpy as np
        from geopandas.testing import assert_geodataframe_equal
        original = self.frame.copy(deep=True)
        report = self.helper.illustrate(self.frame, self.root/'static', column='indicator', units='units',
                                       formats=('png', 'svg', 'pdf'), **self.kwargs)
        image = Image.open(self.root/'static/map.png').convert('RGB')
        self.assertEqual(image.size, (1400, 1000))
        self.assertGreater(np.count_nonzero(np.any(np.asarray(image) < 220, axis=2)), 10000)
        self.assertIn('<svg', (self.root/'static/map.svg').read_text())
        self.assertTrue((self.root/'static/map.pdf').read_bytes().startswith(b'%PDF'))
        self.assertEqual(report['range'], [0, 10])
        self.assertEqual(report['null_values'], 1)
        self.assertEqual(report['features'], 3)
        self.assertEqual(report['display_crs'], 'EPSG:2154')
        self.assertEqual(report['visual_check'], 'not performed by helper')
        self.assertEqual(json.loads((self.root/'static/report.json').read_text()), report)
        assert_geodataframe_equal(self.frame, original)

    def test_html_selects_properties_escapes_text_and_declares_assets(self):
        self.frame.loc[0, 'label'] = '<script>alert(1)</script>'
        report = self.helper.illustrate(self.frame, self.root/'web', formats=('html',),
                                       tooltip=('unit_id', 'label'), **self.kwargs)
        markup = (self.root/'web/map.html').read_text()
        self.assertNotIn('DO_NOT_EXPORT_THIS', markup)
        self.assertNotIn('<script>alert(1)</script>', markup)
        self.assertIn('001', markup)
        assets = re.findall(r'(?:src|href)="(https://[^\"]+)"', markup)
        self.assertEqual(set(assets), set(report['html']['external_assets']))
        self.assertEqual(len(assets), 2)
        self.assertFalse(report['html']['offline'])
        self.assertEqual(report['html']['tooltip_fields'], ['unit_id', 'label'])
        self.assertNotIn('tileLayer(', markup)
        self.assertEqual(report['html']['data_crs'], 'EPSG:4326')

    def test_uniform_html_does_not_require_matplotlib(self):
        with patch.dict(sys.modules, {'matplotlib': None}):
            report = self.helper.illustrate(self.frame, self.root/'web', formats=('html',), **self.kwargs)
        self.assertNotIn('matplotlib', report['versions'])

    def test_small_island_is_not_hidden_by_the_scale_bar(self):
        from PIL import Image
        import numpy as np
        frame = self.gpd.read_file(ROOT/'tests/data/admin_units_synthetic.geojson')
        self.helper.illustrate(frame, self.root/'island', column='population', units='synthetic people', **self.kwargs)
        # Only the tiny third polygon has the maximum-value yellow, apart from the colourbar.
        pixels = np.asarray(Image.open(self.root/'island/map.png').convert('RGB'))[:900, :1100]
        yellow = (pixels[:,:,0] > 220) & (pixels[:,:,1] > 200) & (pixels[:,:,2] < 80)
        self.assertGreaterEqual(int(yellow.sum()), 10)

    def test_invalid_inputs_and_existing_outputs_fail(self):
        for change in ({'column': 'absent', 'units': 'm'}, {'column': 'label', 'units': 'm'},
                       {'column': 'indicator'}, {'tooltip': ('secret_missing',)},
                       {'crs': 4326}, {'formats': ('jpeg',)}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.helper.illustrate(self.frame, self.root/'bad', **(self.kwargs | change))
            self.assertFalse((self.root/'bad').exists())
        for frame in (self.frame.iloc[:0], self.frame.set_crs(None, allow_override=True),
                      self.frame.assign(indicator=float('inf')), self.frame.assign(indicator=float('nan'))):
            with self.assertRaises(ValueError):
                self.helper.illustrate(frame, self.root/'bad', column='indicator', units='m', **self.kwargs)
        target = self.root/'existing'
        target.mkdir()
        sentinel = target/'keep.txt'
        sentinel.write_text('keep')
        with self.assertRaises(ValueError):
            self.helper.illustrate(self.frame, target, **self.kwargs)
        self.assertEqual(sentinel.read_text(), 'keep')

    def test_cli_preserves_input_bytes_and_emits_only_requested_format(self):
        source = ROOT/'tests/data/admin_units_synthetic.geojson'
        before = source.read_bytes()
        result = subprocess.run([sys.executable, str(SKILL/'scripts/render_vector.py'), str(source),
                                 str(self.root/'cli'), '--crs', 'EPSG:2154', '--title', 'Test map',
                                 '--source-note', 'Source: synthetic fixture'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(p.name for p in (self.root/'cli').iterdir()), {'map.png', 'report.json'})
        self.assertEqual(source.read_bytes(), before)

    def test_raster_recipe_bounds_resolution_and_preserves_nodata(self):
        if importlib.util.find_spec('rasterio') is None:
            self.skipTest('Raster preview needs rasterio')
        import rasterio
        from rasterio.transform import from_origin
        import numpy as np
        source = self.root/'terrain.tif'
        data = np.full((20, 2800), 100, dtype='float32')
        data[:, :20] = -9999
        with rasterio.open(source, 'w', driver='GTiff', width=2800, height=20, count=1,
                           dtype='float32', crs='EPSG:2154', nodata=-9999,
                           transform=from_origin(650000, 6860020, 1, 1)) as dst:
            dst.write(data, 1)
        before = source.read_bytes()
        result = run_example('map-illustration/references/python-rendering.md', '## Bounded raster preview',
                             {'raster_path': source, 'output_png': self.root/'raster.png',
                              'title': 'Synthetic terrain', 'unit_label': 'Elevation (m)'})
        self.assertEqual(result['values'].shape, (10, 1400))
        self.assertTrue(result['values'].mask[:, :10].all())
        self.assertEqual(set(result['values'].compressed()), {100})
        self.assertEqual(source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
