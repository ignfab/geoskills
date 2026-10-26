"""Run the Mapshaper skill recipes against synthetic adjacent polygons."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


FIXTURE = Path(__file__).parent / "data" / "admin_units_synthetic.geojson"


class MapshaperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        missing = [name for name in ("geopandas", "shapely")
                   if importlib.util.find_spec(name) is None]
        cls.executable = shutil.which("mapshaper")
        if cls.executable is None:
            missing.append("mapshaper")
        if missing:
            message = "Missing Mapshaper test dependencies: " + ", ".join(missing)
            if os.environ.get("GEOSKILLS_REQUIRE_MAPSHAPER") == "1":
                raise RuntimeError(message)
            raise unittest.SkipTest(message)
        # An installed but broken executable must fail, not become a skip.
        subprocess.run([cls.executable, "-version"], check=True, timeout=30,
                       capture_output=True, text=True)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="geoskills-mapshaper-")
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name)
        self.source_bytes = FIXTURE.read_bytes()
        self.source = json.loads(self.source_bytes)

    def tearDown(self):
        self.assertEqual(FIXTURE.read_bytes(), self.source_bytes)

    def run_mapshaper(self, *arguments):
        process = subprocess.run(
            [self.executable, *map(str, arguments)], cwd=self.output,
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def check_geojson(self, path, original=None):
        import geopandas as gpd
        from shapely import get_num_coordinates

        original = original if original is not None else self.source
        result = json.loads(path.read_text())
        expected_properties = {
            feature["properties"]["unit_id"]: feature["properties"]
            for feature in original["features"]
        }
        actual_properties = {
            feature["properties"]["unit_id"]: feature["properties"]
            for feature in result["features"]
        }
        self.assertEqual(len(result["features"]), len(original["features"]))
        self.assertEqual(actual_properties, expected_properties)
        source = gpd.GeoDataFrame.from_features(original, crs=4326).set_index("unit_id")
        check = gpd.read_file(path).set_index("unit_id")
        self.assertEqual(check.crs.to_epsg(), 4326)
        self.assertFalse(check.geometry.isna().any())
        self.assertFalse(check.geometry.is_empty.any())
        self.assertTrue(check.geometry.is_valid.all())
        self.assertTrue(check.geom_type.isin(["Polygon", "MultiPolygon"]).all())
        self.assertLess(get_num_coordinates(check.geometry).sum(),
                        get_num_coordinates(source.geometry).sum())
        for actual, expected in zip(check.total_bounds, source.total_bounds):
            self.assertAlmostEqual(actual, expected, delta=0.0003)
        return source, check

    def test_weighted_percentage_keeps_features_and_shared_border(self):
        result = self.output / "units-simplified.geojson"
        self.run_mapshaper(FIXTURE, "-info")
        self.run_mapshaper(FIXTURE, "-simplify", "20%", "weighted", "keep-shapes",
                           "-proj", "wgs84", "-o", "format=geojson", result)
        source, check = self.check_geojson(result)
        west, east = check.loc["001"].geometry, check.loc["002"].geometry
        self.assertGreater(west.boundary.intersection(east.boundary).length, 0.019)
        self.assertLess(west.intersection(east).area, 1e-12)
        original_coverage = source.loc["001"].geometry.union(source.loc["002"].geometry)
        self.assertLess(west.union(east).symmetric_difference(original_coverage).area, 1e-12)
        self.assertGreater(check.loc["003"].geometry.area, 0)

    def test_dp_metric_tolerance_and_crs_roundtrip(self):
        import geopandas as gpd

        projected = self.output / "units-100m.shp"
        result = self.output / "units-100m.geojson"
        self.run_mapshaper(
            FIXTURE, "-proj", "EPSG:2154", "-simplify", "dp", "interval=100",
            "keep-shapes", "-o", "format=shapefile", projected,
            "-proj", "wgs84", "-o", "format=geojson", result,
        )
        source, check = self.check_geojson(result)
        metric = gpd.read_file(projected).set_index("unit_id")
        self.assertEqual(metric.crs.to_epsg(), 2154)
        self.assertTrue(metric.geometry.is_valid.all())
        self.assertFalse(metric.geometry.is_empty.any())
        original_metric = source.to_crs(2154)
        returned_metric = check.to_crs(2154)
        for identifier in source.index:
            original = original_metric.loc[identifier].geometry
            simplified = metric.loc[identifier].geometry
            self.assertLessEqual(original.boundary.hausdorff_distance(simplified.boundary), 100.01)
            self.assertLessEqual(simplified.hausdorff_distance(
                returned_metric.loc[identifier].geometry), 0.01)

    def test_combined_layers_share_topojson_arcs(self):
        inputs = []
        for feature in self.source["features"][:2]:
            path = self.output / (feature["properties"]["label"].lower() + ".geojson")
            path.write_text(json.dumps({"type": "FeatureCollection", "features": [feature]}))
            inputs.append(path)
        result = self.output / "units-simplified.topojson"
        self.run_mapshaper(
            "-i", *inputs, "combine-files", "-simplify", "20%", "weighted", "keep-shapes",
            "-proj", "wgs84", "-o", "target=*", "format=topojson", "no-quantization", result,
        )
        topology = json.loads(result.read_text())
        self.assertEqual(topology["type"], "Topology")
        self.assertNotIn("transform", topology)  # No quantization/delta encoding.
        self.assertEqual(set(topology["objects"]), {"west", "east"})

        def arc_ids(value):
            if isinstance(value, int):
                # TopoJSON uses the bitwise complement for a reversed shared arc.
                return {value if value >= 0 else ~value}
            return set().union(*(arc_ids(item) for item in value))

        arc_sets = []
        for name in ("west", "east"):
            geometries = topology["objects"][name]["geometries"]
            self.assertEqual(len(geometries), 1)
            arc_sets.append(arc_ids(geometries[0]["arcs"]))
        self.assertTrue(arc_sets[0] & arc_sets[1], "Neighbors must reuse a common arc")

        # Reimport the delivery file to verify it still contains usable polygons.
        roundtrip = self.output / "combined.geojson"
        self.run_mapshaper(result, "-o", "target=*", "combine-layers", "format=geojson", roundtrip)
        original = {"type": "FeatureCollection", "features": self.source["features"][:2]}
        _, check = self.check_geojson(roundtrip, original=original)
        west, east = check.loc["001"].geometry, check.loc["002"].geometry
        self.assertGreater(west.boundary.intersection(east.boundary).length, 0.019)
        self.assertLess(west.intersection(east).area, 1e-12)


if __name__ == "__main__":
    unittest.main()
