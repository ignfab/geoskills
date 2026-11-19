"""Run real CLIs in fresh interpreters with unrelated packages made unavailable.

This checks import isolation, not package-manager resolution or download sizes. The
guard is installed before any third-party import, so earlier tests cannot warm the
module cache and conceal a required dependency. No environments are installed.
"""
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

from python_test_support import requires_packages
from skill_examples import skill_dir

ROOT = Path(__file__).resolve().parents[1]
MAP = skill_dir('map-illustration') / 'scripts/render_vector.py'
SUMMARY = skill_dir('geospatial-descriptive-statistics') / 'scripts/summarize.py'
GIS_PACKAGES = ('geopandas', 'shapely', 'pyproj', 'pyogrio', 'fiona', 'osgeo',
                'rasterio', 'rasterstats', 'pyarrow', 'qgis')

GUARDED_RUNNER = textwrap.dedent('''\
    import importlib.abc
    import json
    import runpy
    import sys

    blocked = set(json.loads(sys.argv[1]))
    assert not any(name.split('.')[0] in blocked for name in sys.modules), 'Guard installed too late'

    class MissingPackages(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname.split('.')[0] in blocked:
                raise ModuleNotFoundError('Blocked test dependency: ' + fullname, name=fullname)

    sys.meta_path.insert(0, MissingPackages())
    sys.argv = sys.argv[2:]
    runpy.run_path(sys.argv[0], run_name='__main__')
''')


class MinimalDependencyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='geoskills-dependencies-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / 'out'
        self.source = self.root / 'areas.geojson'
        # Standard-library fixture creation must not import the packages being tested.
        self.source.write_text(json.dumps({'type': 'FeatureCollection', 'features': [
            {'type': 'Feature', 'properties': {'id': '001', 'value': 0},
             'geometry': {'type': 'Polygon', 'coordinates': [
                 [[2.34, 48.85], [2.35, 48.85], [2.35, 48.86], [2.34, 48.86], [2.34, 48.85]]]}},
        ]}), encoding='utf-8')

    def run_guarded(self, script, args, blocked):
        return subprocess.run(
            [sys.executable, '-I', '-c', GUARDED_RUNNER, json.dumps(blocked), str(script), *map(str, args)],
            cwd=self.root, capture_output=True, text=True, timeout=60,
            env=dict(os.environ, PROJ_NETWORK='OFF', GDAL_PAM_ENABLED='NO',
                     MPLCONFIGDIR=str(self.root / 'matplotlib-cache')))

    def render(self, formats, blocked, *extra):
        before = self.source.read_bytes()
        result = self.run_guarded(MAP, [self.source, self.output, '--title', 'Synthetic area',
            '--source-note', 'Source: synthetic fixture', '--formats', *formats, *extra], blocked)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((self.output / 'report.json').read_text())
        self.assertEqual(json.loads(result.stdout), report)
        self.assertEqual(report['features'], 1)
        self.assertEqual(set(p.name for p in self.output.iterdir()),
                         {'report.json'} | {f'map.{extension}' for extension in formats})
        for name, size in report['files'].items():
            self.assertEqual((self.output / name).stat().st_size, size)
            self.assertGreater(size, 100)
        self.assertEqual(self.source.read_bytes(), before)
        return report

    @requires_packages('pandas')
    def test_csv_summary_without_gis_rendering_or_arrow(self):
        source = self.root / 'values.csv'
        source.write_text('height,code\n0,001\n10,001\n20,NA\n,\n', encoding='utf-8')
        before = source.read_bytes()
        result = self.run_guarded(SUMMARY, [source, self.output, '--numeric', 'height',
            '--categorical', 'code'], GIS_PACKAGES + ('matplotlib', 'folium'))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((self.output / 'summary.json').read_text())
        self.assertEqual(report['rows'], 4)
        self.assertEqual(report['fields']['height']['mean'], 10)
        self.assertEqual(report['fields']['height']['missing'], 1)
        self.assertEqual(report['fields']['code']['categories'], [
            {'value': '001', 'count': 2, 'frequency': .5},
            {'value': 'NA', 'count': 1, 'frequency': .25},
            {'value': None, 'count': 1, 'frequency': .25}])
        with (self.output / 'summary.csv').open(newline='') as stream:
            rows = list(csv.DictReader(stream))
        mean = next(row for row in rows if row['field'] == 'height' and row['metric'] == 'mean')
        self.assertEqual(json.loads(mean['value_json']), 10)
        self.assertTrue((self.output / 'summary.md').is_file())
        self.assertEqual(source.read_bytes(), before)

    @requires_packages('geopandas', 'matplotlib', 'PIL')
    def test_static_map_without_html_raster_arrow_or_qgis(self):
        from PIL import Image
        report = self.render(['png', 'svg'], ('folium', 'branca', 'rasterio', 'rasterstats',
                                            'pyarrow', 'qgis', 'osgeo'))
        with Image.open(self.output / 'map.png') as image:
            image.load()
            self.assertEqual(image.size, (1400, 1000))
        self.assertIn('<svg', (self.output / 'map.svg').read_text())
        self.assertNotIn('folium', report['versions'])
        self.assertEqual(report['display_crs'], 'EPSG:4326')
        self.assertIsNone(report['scale_bar'])

    @requires_packages('geopandas', 'folium')
    def test_uniform_html_without_matplotlib_raster_arrow_or_qgis(self):
        report = self.render(['html'], ('matplotlib', 'rasterio', 'rasterstats', 'pyarrow', 'qgis', 'osgeo'),
                             '--tooltip', 'id')
        self.assertNotIn('matplotlib', report['versions'])
        self.assertEqual(report['display_crs'], 'EPSG:3857')
        self.assertEqual(report['html']['data_crs'], 'EPSG:4326')
        markup = (self.output / 'map.html').read_text()
        self.assertIn('001', markup)
        self.assertIn('2.34', markup)
        self.assertNotIn('tileLayer(', markup)
        self.assertEqual(len(report['html']['external_assets']), 2)

    @requires_packages('geopandas')
    def test_selected_renderer_is_required_before_output_is_created(self):
        # Negative controls also prove the import guard really blocks an installed module.
        for formats, extra, package in [
                (['png'], [], 'matplotlib'),
                (['html'], [], 'folium'),
                (['html'], ['--column', 'value', '--units', 'synthetic units'], 'matplotlib')]:
            with self.subTest(formats=formats, package=package):
                result = self.run_guarded(MAP, [self.source, self.output, '--title', 'Test',
                    '--source-note', 'Synthetic fixture', '--formats', *formats, *extra], [package])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Blocked test dependency: ' + package, result.stderr)
                self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
