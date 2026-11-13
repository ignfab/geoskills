"""Known-value summaries, serialization and projected measurement checks."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/4-analyze/geospatial-descriptive-statistics'


class SummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if importlib.util.find_spec('pandas') is None:
            raise unittest.SkipTest('Pandas is not installed')
        import pandas as pd
        cls.pd = pd
        spec = importlib.util.spec_from_file_location('summarize', SKILL/'scripts/summarize.py')
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_numeric_missing_infinite_and_invalid(self):
        frame = self.pd.DataFrame({'height': [0, 10, 20, None, 'bad', float('inf'), -float('inf')]})
        original = frame.copy(deep=True)
        report = self.mod.summarize(frame, ['height'], source='synthetic', units={'height': 'm'})
        item = report['fields']['height']
        for key, value in {'valid': 3, 'missing': 1, 'invalid_text': 1, 'infinite': 2,
                           'mean': 10, 'median': 10, 'sum': 30, 'std': 10}.items():
            self.assertEqual(item[key], value)
        self.assertEqual(item['quantiles'], {'0.25': 5, '0.5': 10, '0.75': 15})
        self.assertTrue(report['warnings'])
        self.pd.testing.assert_frame_equal(frame, original)
        json.dumps(report, allow_nan=False)

    def test_empty_all_null_and_singleton(self):
        for values in ([], [None, None], [4]):
            item = self.mod.summarize(self.pd.DataFrame({'x': values}), ['x'], source='synthetic')['fields']['x']
            self.assertIsNone(item['std'])
            self.assertEqual(item['sum'], 4 if values == [4] else None)
        item = self.mod.summarize(self.pd.DataFrame({'x': [4]}), ['x'], source='synthetic', ddof=0)['fields']['x']
        self.assertEqual(item['std'], 0)

    def test_string_categories(self):
        frame = self.pd.DataFrame({'code': ['01001', '01001', '02002', None]})
        item = self.mod.summarize(frame, categorical=['code'], source='synthetic')['fields']['code']
        self.assertEqual(item['categories'], [
            {'value': '01001', 'count': 2, 'frequency': .5},
            {'value': '02002', 'count': 1, 'frequency': .25},
            {'value': None, 'count': 1, 'frequency': .25}])

    def test_bad_selection(self):
        frame = self.pd.DataFrame({'x': [True]})
        for fields in ([], ['absent'], ['x', 'x'], ['x']):
            with self.assertRaises(ValueError):
                self.mod.summarize(frame, fields, source='synthetic')

    def test_cli_roundtrip_no_overwrite_and_source_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'source.csv'
            data = 'height,code\n0,01001\n10,01001\n20,NA\n,\n'
            source.write_text(data)
            out = Path(tmp)/'report'
            command = [sys.executable, str(SKILL/'scripts/summarize.py'), str(source), str(out),
                       '--numeric', 'height', '--categorical', 'code']
            subprocess.run(command, check=True, capture_output=True)
            report = json.loads((out/'summary.json').read_text())
            self.assertEqual(report['fields']['height']['mean'], 10)
            self.assertEqual(report['fields']['code']['categories'][0]['value'], '01001')
            self.assertEqual(report['fields']['code']['categories'][1]['value'], 'NA')
            csv = self.pd.read_csv(out/'summary.csv', dtype='string', keep_default_na=False)
            row = csv[(csv.field == 'code') & (csv.metric == 'categories')].iloc[0]
            self.assertEqual(json.loads(row.value_json), report['fields']['code']['categories'])
            self.assertIn('linear', (out/'summary.md').read_text())
            before = (out/'summary.json').read_bytes()
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual((out/'summary.json').read_bytes(), before)
            self.assertEqual(source.read_text(), data)

    def test_geometry_recipe(self):
        if importlib.util.find_spec('geopandas') is None:
            self.skipTest('GeoPandas is not installed')
        import geopandas as gpd
        from shapely.geometry import box
        from skill_examples import run_example
        source = gpd.GeoDataFrame(geometry=[box(650000, 6860000, 650010, 6860010)], crs=2154)
        for frame in [source, source.to_crs(4326)]:
            result = run_example('geospatial-descriptive-statistics/references/geometry-units.md',
                                 '# Geometry measurements', {'gdf': frame, 'metric_crs': 2154})
            self.assertAlmostEqual(result['measured'].area_m2.iloc[0], 100, places=4)
        with self.assertRaises(ValueError):
            run_example('geospatial-descriptive-statistics/references/geometry-units.md',
                        '# Geometry measurements', {'gdf': source, 'metric_crs': 4326})

    def test_geometry_recipe_converts_foot_units_to_square_metres(self):
        if importlib.util.find_spec('geopandas') is None:
            self.skipTest('GeoPandas is not installed')
        import geopandas as gpd
        from shapely.geometry import box
        from skill_examples import run_example
        crs = '+proj=tmerc +lat_0=48.85 +lon_0=2.35 +k=1 +ellps=GRS80 +units=us-ft +type=crs'
        source = gpd.GeoDataFrame(geometry=[box(0, 0, 10, 10)], crs=crs)
        result = run_example('geospatial-descriptive-statistics/references/geometry-units.md',
                             '# Geometry measurements', {'gdf': source, 'metric_crs': crs})
        self.assertEqual(result['measured'].crs, source.crs)
        self.assertAlmostEqual(result['measured'].area_m2.iloc[0], 100*(1200/3937)**2)


if __name__ == '__main__':
    unittest.main()
