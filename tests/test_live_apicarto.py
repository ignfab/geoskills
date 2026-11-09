"""Opt-in bounded API Carto probes: discovery, paging, protected areas and urban planning."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from test_apicarto import FETCH

LIVE = os.environ.get("GEOSKILLS_LIVE") == "1"
API = "https://apicarto.ign.fr/api"
SAINT_MANDE = {"type": "Point", "coordinates": [2.419441, 48.841526]}
FONTAINEBLEAU = {"type": "Point", "coordinates": [2.6458, 48.4038]}


def get(path, **params):
    with urlopen(f"{API}/{path}?{urlencode(params)}", timeout=120) as response:
        return response.read()


@unittest.skipUnless(LIVE, "Set GEOSKILLS_LIVE=1 for public API Carto probes")
class LiveAPICartoTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="geoskills-live-apicarto-")
        self.addCleanup(temporary.cleanup)
        self.output = Path(temporary.name)

    def geometry(self, geometry):
        path = self.output / "geometry.geojson"
        path.write_text(json.dumps(geometry), encoding="utf-8")
        return path

    def test_openapi_documents_the_padded_parcel_parameters(self):
        spec = get("doc/cadastre.yml").decode("utf-8")
        self.assertIn("/api/cadastre/parcelle:", spec)
        self.assertIn("pattern: '\\d{4}'", spec)
        with self.assertRaises(HTTPError) as error:
            get("cadastre/parcelle", code_insee="94067", section="J", numero="182")
        self.assertEqual(error.exception.code, 400)
        self.assertIn("section", json.loads(error.exception.read())["message"])

    def test_every_parcel_of_saint_mande_across_pages(self):
        result = FETCH.fetch_all("cadastre/parcelle", self.output / "parcels.geojson",
                                 ["code_insee=94067"], page_size=500)
        self.assertEqual(result["status"], "complete")
        self.assertGreater(result["number_matched"], 1000)
        self.assertGreaterEqual(result["pages"], 3)
        features = json.loads((self.output / "parcels.geojson").read_text(encoding="utf-8"))["features"]
        self.assertEqual(len({f["properties"]["idu"] for f in features}), result["features"])
        self.assertTrue(all(f["properties"]["code_insee"] == "94067" for f in features))

    def test_both_natura_2000_networks_at_a_point(self):
        codes = {}
        for endpoint in ("nature/natura-habitat", "nature/natura-oiseaux"):
            name = endpoint.split("/")[1] + ".geojson"
            FETCH.fetch_all(endpoint, self.output / name, geometry_path=self.geometry(FONTAINEBLEAU))
            features = json.loads((self.output / name).read_text(encoding="utf-8"))["features"]
            codes[endpoint] = {f["properties"]["sitecode"] for f in features}
        self.assertIn("FR1100795", codes["nature/natura-habitat"])
        self.assertIn("FR1110795", codes["nature/natura-oiseaux"])

    def test_urban_planning_zone_and_document(self):
        geometry = self.geometry(SAINT_MANDE)
        municipality = json.loads(get("gpu/municipality", insee="94067"))["features"][0]["properties"]
        self.assertFalse(municipality["is_rnu"])
        FETCH.fetch_all("gpu/zone-urba", self.output / "zones.geojson", geometry_path=geometry)
        zones = json.loads((self.output / "zones.geojson").read_text(encoding="utf-8"))["features"]
        self.assertGreaterEqual(len(zones), 1)
        for zone in zones:
            self.assertIn(zone["properties"]["typezone"], {"U", "AUc", "AUs", "A", "N"})
            self.assertTrue(zone["properties"]["partition"].startswith("DU_"))


if __name__ == "__main__":
    unittest.main()
