"""Exercise local skill recipes with GDAL CLI; all outputs stay in temporary directories."""
import csv
import json
import os
from pathlib import Path
import shutil
import re
import subprocess
import tempfile
import unittest

DATA = Path(__file__).resolve().parent / "data"


class GDALCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        required = ("gdalinfo", "gdal_translate", "gdalwarp", "gdalbuildvrt", "gdaltransform",
                    "gdaldem", "ogr2ogr", "gdalsrsinfo", "projinfo")
        missing = [name for name in required if not shutil.which(name)]
        if missing:
            message = "Missing GDAL/PROJ tools: " + ", ".join(missing)
            if os.environ.get("GEOSKILLS_REQUIRE_GDAL") == "1":
                raise RuntimeError(message)
            raise unittest.SkipTest(message)
        probe = subprocess.run(["gdalinfo", "--version"], text=True, capture_output=True)
        if probe.returncode:
            raise RuntimeError("GDAL is installed but cannot start: " + probe.stderr)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="geoskills-test-")
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        self.env = dict(os.environ, GDAL_PAM_ENABLED="NO", PROJ_NETWORK="OFF")

    def run_tool(self, *args, input=None, timeout=60):
        result = subprocess.run([str(arg) for arg in args], input=input, capture_output=True,
                                text=True, env=self.env, cwd=self.output, timeout=timeout)
        self.assertEqual(result.returncode, 0, f"{args}\n{result.stdout}\n{result.stderr}")
        return result.stdout

    def info(self, path):
        return json.loads(self.run_tool("gdalinfo", "-json", "-stats", path))

    def assert_crs(self, path, epsg):
        self.assertIn(f"EPSG:{epsg}", self.run_tool("gdalsrsinfo", "-o", "epsg", path))

    def mosaic(self):
        target = self.output / "mosaic.vrt"
        self.run_tool("gdalbuildvrt", "-a_srs", "EPSG:2154", target,
                      *sorted((DATA / "mnt_dalles").glob("*.asc")))
        return target


class LocalWorkflowTests(GDALCase):
    def test_gps_axis_order_and_overseas(self):
        with (DATA / "points_gps.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        expected = [(2154, 652296.97, 6861636.36), (2154, 574357.38, 6279620.75),
                    (2975, 338568.32, 7690475.44)]
        for row, (epsg, x, y) in zip(rows, expected):
            with self.subTest(point=row["nom"]):
                result = self.run_tool("gdaltransform", "-s_srs", "EPSG:4326", "-t_srs", f"EPSG:{epsg}",
                                       input=f'{row["longitude"]} {row["latitude"]}\n')
                actual = list(map(float, result.split()))
                self.assertAlmostEqual(actual[0], x, delta=0.1)
                self.assertAlmostEqual(actual[1], y, delta=0.1)

    def test_missing_prj_using_confirmed_fixture_crs(self):
        source = DATA / "monuments_sans_prj/monuments.shp"
        self.assertFalse(source.with_suffix(".prj").exists())
        target = self.output / "monuments.geojson"
        self.run_tool("ogr2ogr", "-s_srs", "EPSG:2154", "-t_srs", "EPSG:4326",
                      "-lco", "RFC7946=YES", target, source)
        features = json.loads(target.read_text())["features"]
        self.assertEqual(len(features), 3)
        expected = [(2.3499, 48.8530), (2.2945, 48.8584), (2.3431, 48.8867)]
        for feature, pair in zip(features, expected):
            self.assertEqual(feature["geometry"]["type"], "Point")
            for actual, wanted in zip(feature["geometry"]["coordinates"], pair):
                self.assertAlmostEqual(actual, wanted, delta=0.00001)

    def test_commune_area(self):
        target = self.output / "commune_l93.geojson"
        self.run_tool("ogr2ogr", "-t_srs", "EPSG:2154", target, DATA / "saint_mande.geojson")
        def ring_area(ring):
            # Shift the origin to avoid loss of precision for large projected values.
            x0, y0 = ring[0][:2]
            points = [(p[0] - x0, p[1] - y0) for p in ring]
            return abs(sum(x1*y2 - x2*y1 for (x1,y1),(x2,y2) in zip(points,points[1:]))) / 2
        area = 0
        for feature in json.loads(target.read_text())["features"]:
            geom = feature["geometry"]
            polygons = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
            for polygon in polygons:
                area += ring_area(polygon[0]) - sum(ring_area(ring) for ring in polygon[1:])
        self.assertAlmostEqual(area / 10000, 90.6, delta=0.1)

    def test_raster_metadata(self):
        info = self.info(DATA / "mnt_dalles/dalle_ouest.asc")
        self.assertEqual(info["size"], [72, 195])
        self.assertEqual(info["geoTransform"], [656700, 10, 0, 6861300, 0, -10])
        self.assertFalse(info.get("coordinateSystem", {}).get("wkt"))
        band = info["bands"][0]
        self.assertEqual(band["noDataValue"], -99999)
        self.assertAlmostEqual(band["minimum"], 40.40, delta=0.02)
        self.assertAlmostEqual(band["maximum"], 59.97, delta=0.02)

    def test_mosaic_clip_cog(self):
        target = self.output / "clipped.tif"
        self.run_tool("gdalwarp", "-cutline", DATA / "saint_mande.geojson", "-crop_to_cutline",
                      "-tr", "10", "10", "-tap", "-dstnodata", "-9999", "-of", "COG", "-co", "COMPRESS=DEFLATE",
                      "-co", "RESAMPLING=AVERAGE", self.mosaic(), target)
        info = self.info(target)
        self.assert_crs(target, 2154)
        self.assertEqual(info["size"], [126, 175])
        self.assertEqual(info["geoTransform"], [656790, 10, 0, 6861200, 0, -10])
        self.assertEqual(info["metadata"]["IMAGE_STRUCTURE"]["LAYOUT"], "COG")
        self.assertEqual(info["metadata"]["IMAGE_STRUCTURE"]["COMPRESSION"], "DEFLATE")
        band = info["bands"][0]
        self.assertEqual(band["noDataValue"], -9999)
        self.assertAlmostEqual(band["minimum"], 39.30, delta=0.05)
        self.assertAlmostEqual(band["maximum"], 54.08, delta=0.05)
        self.assertAlmostEqual(band["mean"], 50.15, delta=0.05)
        xyz = self.run_tool("gdal_translate", "-q", "-of", "XYZ", target, "/vsistdout/")
        values = [float(line.split()[-1]) for line in xyz.splitlines()]
        valid = [value for value in values if value != -9999]
        self.assertEqual(len(valid), 9046)
        self.assertAlmostEqual(sum(valid) / len(valid), 50.15, delta=0.05)

    def test_average_downsample_alignment(self):
        target = self.output / "average.tif"
        self.run_tool("gdalwarp", "-tr", "25", "25", "-tap", "-r", "average", self.mosaic(), target)
        info = self.info(target)
        self.assertEqual(info["size"], [58, 78])
        self.assertEqual(info["geoTransform"], [656700, 25, 0, 6861300, 0, -25])
        # Check the first pixel against the weighted mean of its 2.5 x 2.5 source pixels.
        source = DATA / "mnt_dalles/dalle_ouest.asc"
        values = [list(map(float,line.split()))[:3] for line in source.read_text().splitlines()[6:9]]
        weights = [1, 1, 0.5]
        mean = sum(values[y][x]*weights[y]*weights[x] for y in range(3) for x in range(3)) / 6.25
        xyz = self.run_tool("gdal_translate", "-q", "-srcwin", "0", "0", "1", "1",
                            "-of", "XYZ", target, "/vsistdout/")
        self.assertAlmostEqual(float(xyz.split()[-1]), mean, delta=0.001)

    def test_hillshade(self):
        target = self.output / "hillshade.tif"
        self.run_tool("gdaldem", "hillshade", self.mosaic(), target)
        info = self.info(target)
        self.assertEqual(info["size"], [145, 195])
        self.assertEqual(len(info["bands"]), 1)
        self.assertEqual(info["bands"][0]["type"], "Byte")
        self.assertGreater(info["bands"][0]["maximum"], info["bands"][0]["minimum"])
        self.assert_crs(target, 2154)

    def test_gdal_zonal_stats(self):
        version = re.search(r"GDAL (\d+)\.(\d+)", self.run_tool("gdalinfo", "--version"))
        if not shutil.which("gdal") or tuple(map(int, version.groups())) < (3, 12):
            self.skipTest("The zonal-stats CLI needs GDAL >= 3.12")
        zones = self.output / "zones.gpkg"
        self.run_tool("ogr2ogr", "-t_srs", "EPSG:2154", zones, DATA / "saint_mande.geojson")
        target = self.output / "stats.csv"
        self.run_tool("gdal", "raster", "zonal-stats", "--stat", "mean", "--stat", "min",
                      "--stat", "max", "--stat", "count", "--zones", zones,
                      "--include-field", "code_insee", "-f", "CSV", self.mosaic(), target)
        with target.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["code_insee"], "94067")
        self.assertEqual(float(rows[0]["count"]), 9046)
        self.assertAlmostEqual(float(rows[0]["mean"]), 50.15, delta=0.05)
        self.assertAlmostEqual(float(rows[0]["min"]), 39.30, delta=0.05)
        self.assertAlmostEqual(float(rows[0]["max"]), 54.08, delta=0.05)

    def test_ntf_with_local_grid(self):
        operations = self.run_tool("projinfo", "-s", "EPSG:27572", "-t", "EPSG:2154",
                                   "--grid-check", "discard_missing", "--hide-ballpark", "-o", "PROJ")
        if not any(grid in operations for grid in ("fr_ign_gr3df97a.tif", "fr_ign_ntf_r93.tif", "ntf_r93.gsb")):
            self.skipTest("Accurate NTF transformation needs an installed IGN grid")
        result = self.run_tool("gdaltransform", "-s_srs", "EPSG:27572", "-t_srs", "EPSG:2154",
                               input="600000 2428000\n536000 1841000\n")
        for line, expected in zip(result.splitlines(), [(651313.03,6861349.81),(582461.10,6275414.00)]):
            for actual, wanted in zip(map(float,line.split()),expected):
                self.assertAlmostEqual(actual, wanted, delta=0.1)

    def test_vertical_with_local_grid(self):
        operations = self.run_tool("projinfo", "-s", "EPSG:4965", "-t", "EPSG:5698",
                                   "--grid-check", "discard_missing", "--hide-ballpark", "-o", "PROJ")
        if "fr_ign_RAF18.tif" not in operations:
            self.skipTest("Vertical check needs the installed RAF18 grid")
        result = self.run_tool("gdaltransform", "-s_srs", "EPSG:4965", "-t_srs", "EPSG:5698",
                               input="2.3499 48.8530 100\n")
        self.assertAlmostEqual(float(result.split()[2]), 56.20, delta=0.1)


if __name__ == "__main__":
    unittest.main()
