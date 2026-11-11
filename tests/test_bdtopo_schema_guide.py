"""Offline provenance and fail-closed version/format lookup regression tests."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/1-discover/bdtopo-schema-guide'
spec = importlib.util.spec_from_file_location('bdtopo_lookup', SKILL/'scripts/lookup.py')
lookup_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lookup_module)


class SchemaGuideTests(unittest.TestCase):
    def test_building_height_is_sourced_with_special_zero(self):
        result = lookup_module.lookup('3.5', '2026-07', 'batiment', 'hauteur')
        self.assertEqual(result['status'], 'documented')
        self.assertEqual(result['field']['unit'], 'm')
        self.assertEqual(result['field']['names']['shapefile'], 'HAUTEUR')
        self.assertEqual(result['field']['sentinels']['0'], 'unknown or not significant')
        self.assertEqual(result['field']['pages'], [76, 77])

    def test_road_field_alias_and_enum(self):
        result = lookup_module.lookup('3.5', '2026-07', 'troncon_de_route', 'NB_VOIES', 'shapefile')
        self.assertEqual(result['field']['names']['postgresql'], 'nombre_de_voies')
        result = lookup_module.lookup('3.5', '2026-07', 'troncon_de_route', 'importance')
        self.assertEqual(result['field']['enum_values'], ['1', '2', '3', '4', '5', '6'])

    def test_unknown_version_revision_field_or_format_never_inferred(self):
        for args in [('3.3', '2026-07', 'batiment', 'hauteur'),
                     ('3.5', '2025-07', 'batiment', 'hauteur'),
                     (None, None, 'batiment', 'hauteur'),
                     ('3.5', '2026-07', 'batiment', 'invented_height'),
                     ('3.5', '2026-07', 'batiment', 'HAUTEUR'),
                     ('3.5', '2026-07', 'batiment', 'hauteur', 'wfs'),
                     ('3.5', '2026-07', 'batiment', 'hauteur', 'gpkg')]:
            with self.subTest(args=args):
                self.assertEqual(lookup_module.lookup(*args)['status'], 'unverified')

    def test_offline_no_network_or_gis(self):
        with patch('socket.socket', side_effect=AssertionError('No network')):
            result = lookup_module.lookup('3.5', '2026-07', 'batiment')
        self.assertEqual(result['class']['geometry'], 'MultiPolygon Z')
        self.assertIn('subset', result['coverage'])

    def test_every_entry_resolves_to_versioned_provenance(self):
        data = json.loads((SKILL/'references/schema-3.5-2026-07.json').read_text())
        for cls in data['classes'].values():
            for item in [cls, *cls['fields'].values()]:
                source = data['sources'][item['source']]
                self.assertEqual(source['publisher'], 'IGN')
                self.assertEqual(source['model_version'], '3.5')
                self.assertEqual(source['document_revision'], '2026-07')
                self.assertTrue(source['url'].startswith('https://data.geopf.fr/'))
                self.assertRegex(source['sha256'], '^[0-9a-f]{64}$')
                self.assertTrue(source['title'] and source['checked_on'])
                self.assertTrue(all(isinstance(page, int) and page > 0 for page in item['pages']))


if __name__ == '__main__':
    unittest.main()
