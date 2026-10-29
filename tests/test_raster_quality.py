"""Execute intake and raster quality recipes against small known local datasets."""
import json
from pathlib import Path
import re
import shutil
import subprocess

from skill_examples import read_example
from test_workflows import DATA, GDALCase


class RasterQualityTests(GDALCase):
    def classes(self):
        source = self.output / "classes.asc"
        source.write_text("ncols 2\nnrows 2\nxllcorner 650000\nyllcorner 6860000\n"
                          "cellsize 10\nNODATA_value 255\n0 1\n5 255\n")
        target = self.output / "classes.tif"
        self.run_tool("gdal_translate", "-a_srs", "EPSG:2154", "-ot", "Byte", source, target)
        return target

    def test_documented_class_resampling_preserves_codes_and_valid_zero(self):
        self.classes()
        recipe = read_example("gdal-raster-basics/references/quality-checks.md",
                              "## Categorical resampling", language="bash")
        self.run_tool("bash", "-eu", "-c", recipe)
        target = self.output / "classes_cog.tif"
        info = self.info(target)
        self.assertEqual(info["size"], [4, 4])
        self.assertEqual(info["geoTransform"], [650000, 5, 0, 6860020, 0, -5])
        self.assertEqual(info["bands"][0]["noDataValue"], 255)
        xyz = self.run_tool("gdal_translate", "-q", "-of", "XYZ", target, "/vsistdout/")
        values = [float(line.split()[-1]) for line in xyz.splitlines()]
        self.assertEqual(set(values), {0, 1, 5, 255})
        self.assertEqual([values.count(x) for x in (0, 1, 5, 255)], [4, 4, 4, 4])
        valid = info["bands"][0]["metadata"][""]["STATISTICS_VALID_PERCENT"]
        self.assertEqual(float(valid), 75)

    def test_structural_cog_validation_accepts_cog_and_rejects_bad_layout(self):
        version = re.search(r"GDAL (\d+)\.(\d+)", self.run_tool("gdalinfo", "--version"))
        if not shutil.which("gdal") or tuple(map(int, version.groups())) < (3, 13):
            self.skipTest("Full COG validation requires GDAL >= 3.13 and Python bindings")
        source = self.classes()
        self.run_tool("gdal_translate", "-of", "COG", source, "output_cog.tif")
        recipe = read_example("gdal-raster-basics/references/quality-checks.md",
                              "## Structural COG validation", language="bash")
        self.run_tool("bash", "-eu", "-c", recipe)
        # Add overviews after image data to a conventional TIFF: invalid COG IFD ordering.
        self.run_tool("gdal_translate", "-of", "GTiff", "-outsize", "1024", "1024", source, "bad.tif")
        self.run_tool("gdaladdo", "bad.tif", "2", "4")
        result = subprocess.run(["gdal", "driver", "cog", "validate", "--full-check", "yes", "bad.tif"],
                                cwd=self.output, env=self.env, text=True, capture_output=True, timeout=60)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stdout + result.stderr, r"(?i)(offset|IFD|layout)")


class IntakeRecipeTests(GDALCase):
    def test_vector_inventory_keeps_a_missing_crs_unknown(self):
        folder = self.output / "delivery"
        shutil.copytree(DATA / "monuments_sans_prj", folder)
        original = {p.name: p.read_bytes() for p in folder.iterdir()}
        recipe = read_example("geodata-intake/SKILL.md", "## Inspect metadata first",
                              language="bash", example=0).replace("input.gpkg", "delivery/monuments.shp")
        result = self.run_tool("bash", "-eu", "-c", recipe)
        self.assertIn("monuments", result)
        self.assertRegex(result, r"(?i)Layer SRS WKT:\s*\(unknown\)")
        self.assertEqual({p.name: p.read_bytes() for p in folder.iterdir()}, original)

    def test_raster_inventory_creates_no_source_sidecar(self):
        # ASCII driver accepts the source by content, regardless of this temporary suffix.
        shutil.copyfile(DATA / "mnt_dalles/dalle_ouest.asc", self.output / "input.tif")
        before = (self.output / "input.tif").read_bytes()
        recipe = read_example("geodata-intake/SKILL.md", "## Inspect metadata first",
                              language="bash", example=1)
        self.run_tool("bash", "-eu", "-c", recipe)
        info = json.loads((self.output / "raster-info.json").read_text())
        self.assertEqual(info["size"], [72, 195])
        self.assertFalse(info.get("coordinateSystem"))
        self.assertEqual((self.output / "input.tif").read_bytes(), before)
        self.assertFalse((self.output / "input.tif.aux.xml").exists())
