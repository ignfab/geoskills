"""Run the documented terrain workflow against independent synthetic geometry/value oracles."""
from collections import Counter
import json
import os
import shutil
import unittest

from skill_examples import read_example
from test_workflows import DATA, GDALCase

REFERENCE = "terrain-elevation-screening/references/local-processing.md"


class TerrainScreeningTests(GDALCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        missing = [name for name in ("gdal_calc.py", "gdal_polygonize.py", "ogrinfo")
                   if not shutil.which(name)]
        if missing:
            message = "Missing GDAL Python utilities: " + ", ".join(missing)
            if os.environ.get("GEOSKILLS_REQUIRE_GDAL") == "1":
                raise RuntimeError(message)
            raise unittest.SkipTest(message)

    def prepare(self, rows=None, aoi=None):
        source = DATA / "terrain_screening.asc"
        if rows is not None:
            source = self.output / "source.asc"
            header = (DATA / "terrain_screening.asc").read_text().splitlines()[:6]
            source.write_text("\n".join(header + [" ".join(map(str, row)) for row in rows]) + "\n")
        # Assignment is authorized by the fixture metadata, not guessed from its location.
        self.run_tool("gdal_translate", "-a_srs", "EPSG:2154", "-ot", "Float32",
                      source, "dem_metric.tif")
        boundary = DATA / "terrain_screening_aoi.geojson"
        if aoi is not None:
            boundary = self.output / "aoi.geojson"
            boundary.write_text(json.dumps(aoi))
        self.run_tool("ogr2ogr", "aoi_metric.gpkg", boundary, "-nln", "aoi")
        self.env.update(RES_M="10", Z_MIN_M="0", Z_MAX_M="100",
                        SLOPE_MAX_DEG="5", MIN_AREA_M2="0")

    def recipe(self, heading):
        self.run_tool("bash", "-eu", "-c", read_example(REFERENCE, heading, language="bash"))

    def screen(self, slope=False):
        self.recipe("## Clip elevations")
        self.recipe("## Optional slope mask" if slope else "## Altitude-only mask")
        self.recipe("## Candidate polygons")

    def values(self, name):
        xyz = self.run_tool("gdal_translate", "-of", "XYZ", name, "/vsistdout/")
        return [float(line.split()[-1]) for line in xyz.splitlines()]

    def candidates(self):
        # GeoJSON here retains projected coordinates; no RFC 7946 transformation requested.
        return json.loads(self.run_tool("ogr2ogr", "-f", "GeoJSON", "/vsistdout/",
                                        "candidates.gpkg"))["features"]

    def check_grids(self, epsg=2154):
        dem = json.loads(self.run_tool("gdalinfo", "-json", "elevation.tif"))
        mask = json.loads(self.run_tool("gdalinfo", "-json", "selection.tif"))
        self.assertEqual(dem["size"], mask["size"])
        self.assertEqual(dem["geoTransform"], mask["geoTransform"])
        self.assertEqual(mask["bands"][0]["noDataValue"], 255)
        for path in ("elevation.tif", "selection.tif", "candidates.gpkg"):
            self.assert_crs(path, epsg)

    def test_utm_analysis_grid_is_preserved(self):
        self.prepare()
        self.run_tool('gdalwarp', '-t_srs', 'EPSG:32631', '-tr', '10', '10', '-tap',
                      '-r', 'near', '-dstnodata', '-9999', 'dem_metric.tif', 'dem_utm.tif')
        self.run_tool('ogr2ogr', '-t_srs', 'EPSG:32631', 'aoi_utm.gpkg', 'aoi_metric.gpkg', '-nln', 'aoi')
        (self.output/'dem_utm.tif').replace(self.output/'dem_metric.tif')
        (self.output/'aoi_utm.gpkg').replace(self.output/'aoi_metric.gpkg')
        self.screen()
        self.check_grids(32631)
        selected = Counter(self.values('selection.tif'))[1]
        self.assertGreater(selected, 0)
        area = sum(feature['properties']['area_m2'] for feature in self.candidates())
        self.assertGreater(area, 0)
        self.assertLessEqual(area, selected * 100 + 1e-6)

    def test_inclusive_altitude_keeps_zero_and_preserves_missing_values_and_sources(self):
        sources = [DATA / "terrain_screening.asc", DATA / "terrain_screening_aoi.geojson"]
        before = {path: path.read_bytes() for path in sources}
        self.prepare()
        self.screen()
        self.assertEqual(Counter(self.values("selection.tif")), {1: 27, 0: 21, 255: 1})
        self.assertEqual(self.values("selection.tif")[0], 1)
        features = self.candidates()
        self.assertEqual(len(features), 1)
        self.assertAlmostEqual(features[0]["properties"]["area_m2"], 2700)
        self.check_grids()
        self.assertEqual(before, {path: path.read_bytes() for path in sources})
        self.assertFalse((DATA / "terrain_screening.asc.aux.xml").exists())

    def test_slope_excludes_steps_and_unknown_neighbourhoods(self):
        self.prepare()
        self.env["MIN_AREA_M2"] = "500"
        self.screen(slope=True)
        self.assertEqual(Counter(self.values("selection.tif")), {1: 8, 0: 16, 255: 25})
        features = self.candidates()
        self.assertEqual(len(features), 1)
        self.assertAlmostEqual(features[0]["properties"]["area_m2"], 800)
        # Horn slope on the 100 m step across 10 m cells: atan(5), in degrees.
        self.assertAlmostEqual(self.values("slope.tif")[3 * 7 + 3], 78.69007, places=4)
        self.assertEqual(self.values("slope.tif")[5 * 7 + 1], -9999)
        self.check_grids()

    def test_empty_selection_retains_output_schema_and_crs(self):
        self.prepare()
        self.env.update(Z_MIN_M="300", Z_MAX_M="400")
        self.screen()
        self.assertEqual(Counter(self.values("selection.tif")), {0: 48, 255: 1})
        self.assertEqual(self.candidates(), [])
        self.assertIn("area_m2", self.run_tool("ogrinfo", "-so", "-al", "candidates.gpkg"))
        self.check_grids()

    def test_all_nodata_is_unknown_not_rejected(self):
        self.prepare([[-9999] * 7 for _ in range(7)])
        self.screen()
        self.assertEqual(Counter(self.values("selection.tif")), {255: 49})
        self.assertEqual(self.candidates(), [])
        self.check_grids()

    def test_negative_elevations_and_hole_are_preserved(self):
        rows = [[-5] * 7 for _ in range(7)]
        rows[3][3] = -9999
        self.prepare(rows)
        self.env.update(Z_MIN_M="-5", Z_MAX_M="0")
        self.screen()
        self.assertEqual(Counter(self.values("selection.tif")), {1: 48, 255: 1})
        feature, = self.candidates()
        self.assertEqual(feature["properties"]["area_m2"], 4800)
        self.assertEqual(len(feature["geometry"]["coordinates"]), 2)  # outer ring and hole

    def test_diagonal_cells_do_not_combine_to_meet_minimum_area(self):
        rows = [[200] * 7 for _ in range(7)]
        rows[2][2] = rows[3][3] = 100
        self.prepare(rows)
        self.env["MIN_AREA_M2"] = "150"
        self.screen()
        self.assertEqual(Counter(self.values("selection.tif")), {1: 2, 0: 47})
        self.assertEqual(self.candidates(), [])  # each separate 100 m² component is too small

    def test_exact_aoi_clipping_precedes_area_filter(self):
        aoi = json.loads((DATA / "terrain_screening_aoi.geojson").read_text())
        aoi["features"][0]["geometry"]["coordinates"] = [[
            [650003, 6860003], [650037, 6860003], [650037, 6860067],
            [650003, 6860067], [650003, 6860003]]]
        self.prepare([[100] * 7 for _ in range(7)], aoi=aoi)
        self.env["MIN_AREA_M2"] = "2200"
        self.screen()
        self.assertEqual(Counter(self.values("selection.tif")), {1: 28})
        # Selected pixel footprints cover 2800 m², but the exact AOI is only 34 * 64 = 2176.
        self.assertEqual(self.candidates(), [])


if __name__ == "__main__":
    unittest.main()
