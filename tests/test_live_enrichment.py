"""Opt-in small API probes, including real GeoServer ECQL and GDAL WFS pagination."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from skill_examples import read_example, run_example
from test_enrichment import EXPORT, FEED
from test_workflows import GDALCase

LIVE = os.environ.get("GEOSKILLS_LIVE") == "1"
HOST = "https://data.geopf.fr"
WFS = HOST + "/wfs/ows"
LAYER = "ADMINEXPRESS-COG.LATEST:commune"
FILTER = "code_insee IN ('94067','94080','94033')"


def request(path, **params):
    url = HOST + path + ("?" + urlencode(params) if params else "")
    with urlopen(url, timeout=60) as response:
        return response.read()


def discover_communes():
    capabilities = ET.fromstring(request("/wfs/ows", service="WFS", version="2.0.0", request="GetCapabilities"))
    names = {node.text for node in capabilities.findall(".//{http://www.opengis.net/wfs/2.0}FeatureType/{http://www.opengis.net/wfs/2.0}Name")}
    if LAYER not in names:
        raise AssertionError("Fixture layer no longer advertised; review the live fixture")
    schema = ET.fromstring(request("/wfs/ows", service="WFS", version="2.0.0",
                                  request="DescribeFeatureType", typeNames=LAYER))
    fields = {e.get("name"): e.get("type") for e in schema.findall(".//{http://www.w3.org/2001/XMLSchema}element")}
    if not {"code_insee", "cleabs", "nom_officiel"}.issubset(fields):
        raise AssertionError("Fixture schema changed")
    geometries = [name for name, kind in fields.items() if kind and kind.startswith("gml:")]
    if len(geometries) != 1:
        raise AssertionError("Expected one discoverable geometry field")
    return geometries[0]


@unittest.skipUnless(LIVE, "Set GEOSKILLS_LIVE=1 for public IGN API probes")
class LiveNewSkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="geoskills-live-new-")
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)

    def recipe(self, reference, heading, filename, *, example=0, resource=""):
        code = read_example(reference, heading, language="bash", example=example)
        result = subprocess.run(["bash", "-eu", "-c", code], cwd=self.output,
                                env=dict(os.environ, RESOURCE=resource), capture_output=True,
                                text=True, timeout=70)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.output / filename

    def test_catalogue_script_on_advertised_page(self):
        # Run curl separately: the entry block also invokes the skill-relative helper.
        code = read_example("geopf-download-files/SKILL.md", "## Discover before downloading",
                            language="bash").split("python3 scripts/", 1)[0]
        result = subprocess.run(["bash", "-eu", "-c", code], cwd=self.output,
                                capture_output=True, text=True, timeout=70)
        self.assertEqual(result.returncode, 0, result.stderr)
        page = FEED.inspect_feed(self.output / "capabilities.xml")
        self.assertTrue(page["entries"])
        self.assertEqual(page["page"], 1)
        self.assertEqual(page["page_size"], 10)
        self.assertTrue(all(e["links"] for e in page["entries"]))

    def test_elevation_points_and_twenty_sample_profile(self):
        path = self.recipe("geopf-altimetry/SKILL.md", "## Discover and query points", "resources.json")
        resources = json.loads(path.read_text())["resources"]
        wanted = "ign_rge_alti_wld"  # Fixture product, required to be present before use.
        self.assertIn(wanted, {r["_id"] for r in resources})
        detail = json.loads(request("/altimetrie/resources/" + wanted))
        self.assertTrue(detail)
        path = self.recipe("geopf-altimetry/SKILL.md", "## Discover and query points", "elevations.json",
                           example=1, resource=wanted)
        response = json.loads(path.read_text())
        rows = [dict(id="01", longitude="2.337306", latitude="48.849319"),
                dict(id="02", longitude="2.367776", latitude="48.852891")]
        result = run_example("geopf-altimetry/references/points-and-profiles.md", "## Attach point elevations",
                             dict(rows=rows, response=response, resource=wanted, vertical_reference="unknown"))["result"]
        self.assertTrue(all(r["elevation_status"] == "ok" and 10 < r["elevation_m"] < 200 for r in result))
        path = self.recipe("geopf-altimetry/references/points-and-profiles.md", "## Sample a profile",
                           "profile.json", resource=wanted)
        points = json.loads(path.read_text())["elevations"]
        self.assertEqual(len(points), 20)
        self.assertAlmostEqual(points[0]["lon"], 2.337306, places=6)
        self.assertAlmostEqual(points[-1]["lat"], 48.852891, places=6)
        self.assertTrue(all(10 < float(p["z"]) < 200 for p in points))

    def test_route_and_isochrone_use_discovered_resources(self):
        import geopandas as gpd
        from shapely.geometry import Point
        path = self.recipe("geopf-routing/SKILL.md", "## Discover and calculate a route", "capabilities.json")
        resources = json.loads(path.read_text())["resources"]
        for operation in ("route", "isochrone"):
            candidates = []
            for resource in resources:
                for available in resource["availableOperations"]:
                    if available["id"] != operation:
                        continue
                    params = {p["id"]: p.get("values", []) for p in available["availableParameters"]}
                    required = dict(profile="pedestrian", timeUnit="second", distanceUnit="meter", geometryFormat="geojson")
                    required.update(dict(optimization="fastest") if operation == "route" else
                                    dict(direction="departure", costType="time"))
                    if all(value in params.get(key, []) for key, value in required.items()):
                        candidates.append(resource["id"])
            self.assertTrue(candidates)
            resource = "bdtopo-valhalla" if "bdtopo-valhalla" in candidates else candidates[0]
            if operation == "route":
                path = self.recipe("geopf-routing/SKILL.md", "## Discover and calculate a route",
                                   "route.json", example=1, resource=resource)
            else:
                path = self.recipe("geopf-routing/references/reachable-areas.md", "## Five-minute walking area",
                                   "isochrone.json", resource=resource)
            response = json.loads(path.read_text())
            self.assertEqual(response["resource"], resource)
            self.assertEqual(response["profile"], "pedestrian")
            self.assertEqual(response["timeUnit"], "second")
            collection = run_example("geopf-routing/references/reachable-areas.md", "## Export the response geometry",
                                     dict(response=response, operation=operation))["collection"]
            frame = gpd.GeoDataFrame.from_features(collection["features"], crs="EPSG:4326").to_crs(2154)
            self.assertTrue(frame.geometry.is_valid.all())
            self.assertFalse(frame.geometry.is_empty.any())
            if operation == "route":
                self.assertTrue(1000 < response["distance"] < 10000)
                self.assertEqual(response["distanceUnit"], "meter")
                endpoints = gpd.GeoSeries([Point(2.337306,48.849319), Point(2.367776,48.852891)], crs=4326).to_crs(2154)
                line = frame.geometry.iloc[0]
                self.assertLess(Point(line.coords[0]).distance(endpoints.iloc[0]), 100)
                self.assertLess(Point(line.coords[-1]).distance(endpoints.iloc[1]), 100)
            else:
                self.assertEqual(response["costValue"], 300)
                self.assertEqual(response["direction"], "departure")
                self.assertTrue(10000 < frame.area.iloc[0] < 10000000)


@unittest.skipUnless(LIVE, "Set GEOSKILLS_LIVE=1 for real GeoServer/GDAL paging")
class LiveWFSSemanticsTests(GDALCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.geometry_field = discover_communes()

    def hits(self, cql, filename):
        code = read_example("geoserver-cql-filter/references/requests.md", "## WFS count-only probe", language="bash")
        code = code.replace("--output hits.xml", "--output " + filename)
        result = subprocess.run(["bash", "-eu", "-c", code], cwd=self.output,
                                env=dict(self.env, WFS_URL=WFS, TYPE_NAME=LAYER, CQL=cql),
                                capture_output=True, text=True, timeout=70)
        self.assertEqual(result.returncode, 0, result.stderr)
        return EXPORT.matched(self.output / filename)

    def test_real_ecql_attribute_and_spatial_semantics(self):
        self.assertEqual(self.hits(FILTER, "three.xml"), 3)
        self.assertEqual(self.hits(FILTER + " AND code_insee = '94067'", "one.xml"), 1)
        self.assertEqual(self.hits(FILTER + " AND code_insee = '00000'", "zero.xml"), 0)
        # BBOX CRS support does not establish EWKT compatibility on this deployment.
        spatial = f"code_insee = '94067' AND BBOX({self.geometry_field},2.41,48.83,2.43,48.85,'CRS:84')"
        self.assertEqual(self.hits(spatial, "spatial.xml"), 1)
        outside = f"code_insee = '94067' AND BBOX({self.geometry_field},0,0,0.01,0.01,'CRS:84')"
        self.assertEqual(self.hits(outside, "outside.xml"), 0)
        # A schema-valid field with malformed syntax must fail, not broaden to INCLUDE.
        try:
            body = request("/wfs/ows", service="WFS", version="2.0.0", request="GetFeature",
                           typeNames=LAYER, resultType="hits", cql_filter="code_insee = '")
        except HTTPError as exc:
            self.assertTrue(400 <= exc.code < 500)
        else:
            self.assertIn("Exception", ET.fromstring(body).tag)

    def test_gdal_export_with_one_feature_per_page_is_complete(self):
        self.assertEqual(self.hits(FILTER, "before.xml"), 3)
        path = self.output / "communes.gpkg"
        # GDAL converts this same predicate to WFS Filter Encoding; no client-side limit.
        self.run_tool("ogr2ogr", "--config", "OGR_WFS_PAGING_ALLOWED", "ON", "--config",
                      "OGR_WFS_PAGE_SIZE", "1", "--config", "GDAL_HTTP_TIMEOUT", "45",
                      "-f", "GPKG", "-progress", "-nln", "communes", "-where", FILTER,
                      path, "WFS:" + WFS, LAYER, timeout=180)
        self.assertEqual(self.hits(FILTER, "after.xml"), 3)
        result = EXPORT.check_export(path, "communes", "cleabs", self.output / "before.xml", self.output / "after.xml")
        self.assertEqual(result["status"], "consistent", result)
        self.assertEqual(result["distinct_ids"], 3)
        import geopandas as gpd
        frame = gpd.read_file(path, layer="communes")
        self.assertEqual(set(frame.code_insee), {"94067", "94080", "94033"})
        self.assertIsNotNone(frame.crs)
        self.assertTrue(frame.geometry.is_valid.all())
