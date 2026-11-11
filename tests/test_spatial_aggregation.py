"""Independent geometric assignments, reconciliation and output round trips."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AggregationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if importlib.util.find_spec('geopandas') is None:
            raise unittest.SkipTest('GeoPandas is not installed')
        import geopandas as gpd
        cls.gpd = gpd
        spec = importlib.util.spec_from_file_location('aggregate', ROOT/'skills/4-analyze/spatial-aggregation/scripts/aggregate.py')
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        from shapely.geometry import Point, box
        self.objects = self.gpd.GeoDataFrame({'id': ['a', 'b', 'c', 'edge', 'outside'],
                                              'height': [0., 10., None, 30., 100.]},
                          geometry=[Point(1, 1), Point(2, 1), Point(5, 1), Point(4, 1), Point(20, 1)], crs=2154)
        self.zones = self.gpd.GeoDataFrame({'code': ['001', '002', 'NA'], 'denom': [2., 0., None]},
                          geometry=[box(0, 0, 4, 4), box(4, 0, 8, 4), box(10, 0, 12, 4)], crs=2154)

    def run_aggregation(self, **kwargs):
        return self.mod.aggregate(self.objects, self.zones, 'code', field='height', object_id='id', **kwargs)

    def test_values_empty_zones_nulls_and_reconciliation(self):
        result, report = self.run_aggregation()
        self.assertEqual(result['count'].tolist(), [2, 1, 0])
        self.assertEqual(result['valid'].tolist(), [2, 0, 0])
        self.assertEqual(result['missing'].tolist(), [0, 1, 0])
        self.assertEqual(result['sum'].iloc[0], 10)
        self.assertEqual(result['mean'].iloc[0], 5)
        self.assertTrue(result['sum'].iloc[1:2].isna().all())
        self.assertEqual(result['sum'].iloc[2], 0)
        self.assertTrue(result['mean'].iloc[1:].isna().all())
        self.assertEqual(report['unmatched_ids'], ['edge', 'outside'])
        self.assertEqual(report['assignments'], 3)
        self.assertEqual(report['matched_objects'], 3)

    def test_boundary_policies(self):
        with self.assertRaisesRegex(ValueError, 'multiple zones'):
            self.run_aggregation(predicate='intersects')
        result, report = self.run_aggregation(predicate='intersects', policy='all')
        self.assertEqual(result['count'].tolist(), [3, 2, 0])
        self.assertEqual(report['multiple_match_ids'], ['edge'])
        self.assertEqual(report['assignments'], 5)
        result, report = self.run_aggregation(predicate='intersects', policy='lowest-id')
        self.assertEqual(result['count'].tolist(), [3, 1, 0])
        self.assertEqual(report['assignments'], 4)

    def test_overlap_and_duplicate_index_labels(self):
        from shapely.geometry import box
        self.zones.loc[1, 'geometry'] = box(1.5, 0, 8, 4)
        self.objects.index = [1, 1, 1, 2, 2]
        with self.assertRaisesRegex(ValueError, 'multiple zones'):
            self.run_aggregation()
        result, report = self.run_aggregation(policy='lowest-id')
        self.assertIn('b', report['multiple_match_ids'])
        self.assertEqual(report['assignments'], 4)
        self.assertEqual(result['count'].sum(), 4)

    def test_mixed_known_crs(self):
        # Avoid border sensitivity: exact-border fixture is tested separately.
        self.objects = self.objects.iloc[[0, 1, 2, 4]].to_crs(4326)
        result, report = self.run_aggregation()
        self.assertEqual(result['count'].tolist(), [2, 1, 0])
        self.assertEqual(result.crs, self.zones.crs)

    def test_bad_ids_missing_crs_invalid_geometry_and_infinity(self):
        from shapely.geometry import Polygon
        original = self.zones.copy()
        self.zones.loc[1, 'code'] = '001'
        with self.assertRaises(ValueError): self.run_aggregation()
        self.zones = original
        self.objects.crs = None
        with self.assertRaises(ValueError): self.run_aggregation()
        self.objects = self.objects.set_crs(2154)
        self.objects.loc[0, 'geometry'] = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
        with self.assertRaises(ValueError): self.run_aggregation()
        self.setUp()
        self.objects.loc[0, 'height'] = float('inf')
        with self.assertRaises(ValueError): self.run_aggregation()

    def test_ratio_denominators(self):
        result, report = self.run_aggregation(denominator='denom')
        self.assertEqual(result.ratio.iloc[0], 1)
        self.assertTrue(result.ratio.iloc[1:].isna().all())
        self.assertEqual(report['undefined_ratios'], 2)

    def test_no_objects(self):
        self.objects = self.objects.iloc[0:0]
        result, report = self.run_aggregation()
        self.assertEqual(result['count'].tolist(), [0, 0, 0])
        self.assertEqual(report['objects'], 0)
        self.assertTrue(result['mean'].isna().all())

    def test_roundtrip_ids_geometry_and_source_integrity(self):
        from geopandas.testing import assert_geodataframe_equal
        objects, zones = self.objects.copy(deep=True), self.zones.copy(deep=True)
        result, report = self.run_aggregation()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'out'
            self.mod.export(result, report, path, 'code')
            reopened = self.gpd.read_file(path/'indicators.gpkg')
            self.assertEqual(reopened.code.tolist(), ['001', '002', 'NA'])
            self.assertEqual(reopened['count'].tolist(), [2, 1, 0])
            self.assertTrue(reopened.geometry.geom_equals(self.zones.geometry).all())
            before = (path/'indicators.gpkg').read_bytes()
            with self.assertRaises(FileExistsError): self.mod.export(result, report, path, 'code')
            self.assertEqual((path/'indicators.gpkg').read_bytes(), before)
        assert_geodataframe_equal(self.objects, objects)
        assert_geodataframe_equal(self.zones, zones)


if __name__ == '__main__':
    unittest.main()
