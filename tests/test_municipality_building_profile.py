"""Independent area/count oracles and real file checks for the municipal workflow."""
import hashlib
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/data'
SCRIPT = ROOT / 'skills/6-workflows/municipality-building-profile/scripts/build_profile.py'


class BuildingProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if importlib.util.find_spec('geopandas') is None:
            raise unittest.SkipTest('GeoPandas is not installed')
        import geopandas as gpd
        cls.gpd = gpd
        spec = importlib.util.spec_from_file_location('building_profile', SCRIPT)
        cls.helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.helper)

    def setUp(self):
        self.manifest = json.loads((DATA / 'building_profile_input.json').read_text())
        self.municipalities = self.gpd.read_file(DATA / self.manifest['municipality']['path'])
        self.buildings = self.gpd.read_file(DATA / self.manifest['buildings']['path'])

    def run_profile(self):
        return self.helper.profile(self.municipalities, self.buildings, self.manifest)

    def test_independent_counts_union_area_and_shared_population(self):
        from geopandas.testing import assert_geodataframe_equal
        original = self.buildings.copy(deep=True)
        layers, audit = self.run_profile()
        self.assertEqual(audit['metrics']['building_count'], 4)
        # 400 + 400 - 100 overlap + 50 clipped crossing + 100 isolated.
        self.assertEqual(audit['metrics']['footprint_area_m2'], 850)
        self.assertEqual(audit['metrics']['municipality_area_m2'], 10000)
        self.assertEqual(audit['metrics']['observed_footprint_share_pct'], 8.5)
        self.assertEqual(audit['metrics']['overlap_excess_m2'], 100)
        self.assertEqual(layers['buildings'].building_id.tolist(), ['001', '002', '003', '004'])
        self.assertEqual(audit['reconciliation']['touch_only_ids'], ['touch'])
        self.assertEqual(audit['reconciliation']['outside_ids'], ['outside'])
        self.assertEqual(audit['reconciliation']['cross_boundary_ids'], ['003'])
        self.assertEqual(audit['height']['mean_m'], 15)
        self.assertEqual(audit['height']['q25_m'], 12.5)
        self.assertEqual(audit['height']['q75_m'], 17.5)
        self.assertEqual(audit['height']['valid'], 2)
        self.assertEqual(audit['height']['missing'], 1)
        self.assertEqual(audit['height']['sentinel'], 1)
        self.assertEqual({x['value']: x['count'] for x in audit['usage']}, {'housing': 2, 'NA': 1, None: 1})
        self.assertEqual(sum(x['count'] for x in audit['usage']), 4)
        assert_geodataframe_equal(self.buildings, original)

    def test_zero_policy_and_unusable_height_reconciliation(self):
        self.manifest['height']['missing_values'] = []
        _, audit = self.run_profile()
        self.assertEqual(audit['height']['valid'], 3)
        self.assertEqual(audit['height']['mean_m'], 10)
        self.buildings['height'] = ['bad', float('inf'), -3, 100, 100, None]
        _, audit = self.run_profile()
        self.assertEqual(audit['height']['invalid'], 3)
        self.assertEqual(audit['height']['missing'], 1)
        self.assertIsNone(audit['height']['mean_m'])
        json.dumps(audit, allow_nan=False)

    def test_empty_inventory_has_valid_empty_layers_and_null_statistics(self):
        self.buildings = self.buildings.iloc[0:0]
        layers, audit = self.run_profile()
        self.assertEqual(audit['metrics']['building_count'], 0)
        self.assertEqual(audit['metrics']['footprint_area_m2'], 0)
        self.assertIsNone(audit['height']['mean_m'])
        self.assertIsNone(audit['height']['unusable_pct'])
        self.assertEqual(audit['usage'], [])
        with tempfile.TemporaryDirectory() as tmp:
            self.helper.export(layers, audit, Path(tmp) / 'out')
            for name, expected in [('municipality', 1), ('buildings', 0), ('footprint', 0)]:
                frame = self.gpd.read_file(Path(tmp) / 'out/profile.gpkg', layer=name)
                self.assertEqual(len(frame), expected)
                self.assertEqual(frame.crs.to_epsg(), 2154)

    def test_holes_and_multipart_footprints(self):
        from shapely.geometry import Polygon, box, MultiPolygon
        shape = self.municipalities.geometry.iloc[0]
        hole = box(650012, 6860012, 650018, 6860018)
        self.municipalities.loc[0, 'geometry'] = Polygon(shape.exterior.coords, [hole.exterior.coords])
        _, audit = self.run_profile()
        self.assertEqual(audit['metrics']['municipality_area_m2'], 9964)
        self.assertEqual(audit['metrics']['footprint_area_m2'], 814)
        self.buildings.loc[5, 'geometry'] = MultiPolygon([box(650050,6860050,650055,6860055),
                                                        box(650060,6860050,650065,6860055)])
        layers, audit = self.run_profile()
        self.assertEqual(audit['metrics']['footprint_area_m2'], 764)
        self.assertEqual(layers['buildings'].geometry.iloc[-1].geom_type, 'MultiPolygon')

    def test_mixed_crs_and_z_do_not_change_height_semantics(self):
        import shapely
        # Avoid exact boundary contacts in this reprojection accuracy test.
        self.buildings = self.buildings.iloc[[0,1,2,5]].to_crs(4326)
        self.buildings.geometry = self.buildings.geometry.map(lambda g: shapely.force_3d(g, 900))
        layers, audit = self.run_profile()
        self.assertEqual(audit['metrics']['building_count'], 4)
        self.assertAlmostEqual(audit['metrics']['footprint_area_m2'], 850, places=4)
        self.assertEqual(audit['height']['mean_m'], 15)
        self.assertFalse(layers['buildings'].geometry.has_z.any())

    def test_missing_crs_invalid_geometry_and_unsuitable_projection_fail(self):
        from shapely.geometry import Polygon
        for crs in ('EPSG:4326', 'EPSG:3857', 'EPSG:2263', 'EPSG:32755'):
            self.manifest['analysis_crs'] = crs
            with self.subTest(crs=crs), self.assertRaises(ValueError):
                self.run_profile()
        self.manifest['analysis_crs'] = 'EPSG:2154'
        self.buildings.crs = None
        with self.assertRaisesRegex(ValueError, 'missing CRS'): self.run_profile()
        self.buildings = self.buildings.set_crs(2154)
        self.buildings.loc[0, 'geometry'] = Polygon([(0,0),(2,2),(0,2),(2,0),(0,0)])
        with self.assertRaisesRegex(ValueError, 'invalid geometry'): self.run_profile()

    def test_duplicate_ids_ambiguous_boundary_and_preclipped_inputs_fail(self):
        self.buildings.loc[1, 'id'] = '001'
        with self.assertRaisesRegex(ValueError, 'unique'): self.run_profile()
        self.setUp()
        self.manifest['municipality']['id'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'exactly one'): self.run_profile()
        self.setUp()
        self.manifest['municipality']['id'] = 1
        with self.assertRaisesRegex(ValueError, 'string'): self.run_profile()
        self.setUp()
        self.manifest['buildings']['geometry_scope'] = 'clipped'
        with self.assertRaisesRegex(ValueError, 'whole building'): self.run_profile()

    def test_identical_geometries_flagged_without_erasing_source_objects(self):
        self.buildings.loc[1, 'geometry'] = self.buildings.geometry.iloc[0]
        _, audit = self.run_profile()
        self.assertEqual(audit['metrics']['building_count'], 4)
        self.assertEqual(audit['metrics']['footprint_area_m2'], 550)
        self.assertEqual(audit['reconciliation']['duplicate_geometry_ids'], ['001','002'])

    def test_optional_fields_and_unverified_policies(self):
        for section in ('height', 'usage'):
            original = self.manifest[section]
            self.manifest[section] = dict(original, field='does_not_exist')
            with self.assertRaises(ValueError): self.run_profile()
            self.manifest[section] = original
        self.manifest['height']['missing_values'] = None
        with self.assertRaises(ValueError): self.run_profile()
        self.manifest.pop('height'); self.manifest.pop('usage')
        layers, audit = self.run_profile()
        self.assertIsNone(audit['height']); self.assertIsNone(audit['usage'])
        self.assertNotIn('height_m', layers['buildings'])

    def test_partial_and_unknown_inputs_never_claim_complete(self):
        for status in ('partial', 'unknown'):
            self.manifest['buildings']['completeness'] = {'status':status,'evidence':None}
            _, audit = self.run_profile()
            self.assertEqual(audit['completeness']['status'], status)
            self.assertTrue(any('not established as complete' in w for w in audit['warnings']))
        self.manifest['buildings']['completeness'] = {'status':'complete','evidence':None}
        with self.assertRaises(ValueError): self.run_profile()

    def test_real_cli_outputs_reopen_keep_ids_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'profile'
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('building_profile*')}
            result = subprocess.run([sys.executable, str(SCRIPT), str(DATA / 'building_profile_input.json'), str(target)],
                                    text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            audit = json.loads((target / 'audit.json').read_text())
            self.assertEqual(audit['metrics']['footprint_area_m2'], 850)
            self.assertEqual(self.gpd.read_file(target / 'profile.gpkg', layer='municipality').municipality_id.tolist(), ['00001'])
            self.assertEqual(audit['validation']['qgis_project'], 'not_created')
            with (target / 'indicators.csv').open(newline='') as stream:
                first = next(csv.DictReader(stream))
            self.assertEqual(first['indicator'], 'municipality_id')
            self.assertEqual(json.loads(first['value_json']), '00001')
            manifest = json.loads((target / 'qgis-project.json').read_text())
            self.assertTrue(manifest['require_portable'])
            self.assertTrue(all((target / layer['source']).is_file() for layer in manifest['layers']))
            self.assertIn('8.5', (target / 'report.md').read_text())
            snapshot = {p.name: p.read_bytes() for p in target.iterdir()}
            with self.assertRaises(FileExistsError): self.helper.build(DATA / 'building_profile_input.json', target)
            self.assertEqual(snapshot, {p.name:p.read_bytes() for p in target.iterdir()})
            self.assertEqual(before, {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('building_profile*')})

    def test_geopackage_layer_discovery_relative_paths_and_missing_layer(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.municipalities.to_file(base / 'inputs.gpkg', layer='towns', driver='GPKG')
            self.buildings.to_file(base / 'inputs.gpkg', layer='stock', driver='GPKG')
            for section, layer in [('municipality','towns'), ('buildings','stock')]:
                self.manifest[section].update(path='inputs.gpkg',layer=layer)
            path = base / 'input.json';path.write_text(json.dumps(self.manifest))
            self.helper.build(path, base / 'good')
            self.manifest['buildings']['layer'] = 'missing'
            path.write_text(json.dumps(self.manifest))
            with self.assertRaisesRegex(ValueError, 'discovered layer'):
                self.helper.build(path, base / 'bad')
            self.assertFalse((base / 'bad').exists())


if __name__ == '__main__':
    unittest.main()
