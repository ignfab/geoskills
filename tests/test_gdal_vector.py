"""Run the documented ogr2ogr and gdal vector recipes on local fixtures."""
import csv
import io
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import unittest

from skill_examples import read_example
from test_workflows import DATA, GDALCase

SKILL = "gdal-vector-processing/SKILL.md"
FORMATS = "gdal-vector-processing/references/formats-and-encodings.md"
FILTERS = "gdal-vector-processing/references/filters-sql-and-merge.md"
CLI = "gdal-vector-processing/references/gdal-vector-cli.md"
NAMES = {"94067": "Saint-Mandé", "94038": "L'Haÿ-les-Roses", "02201": "Cœuvres-et-Valsery"}
ZONE = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"name": "zone"},
        "geometry": {"type": "Polygon", "coordinates": [[[2.35975, 48.82932], [2.35998, 48.82932],
                     [2.35998, 48.82962], [2.35975, 48.82962], [2.35975, 48.82932]]]}}]}


class VectorCase(GDALCase):
    def recipe(self, reference, heading, example=0, *, check=True, cwd=None):
        code = read_example(reference, heading, language="bash", example=example)
        result = subprocess.run(["bash", "-eu", "-c", code], cwd=cwd or self.output, env=self.env,
                                capture_output=True, text=True, timeout=120)
        if check:
            self.assertEqual(result.returncode, 0, f"{heading} #{example}\n{result.stdout}\n{result.stderr}")
        return result

    def stage(self, directory=None):
        directory = directory or self.output
        for source in (DATA / "communes_sans_cpg").iterdir():
            shutil.copy(source, directory / source.name)
        shutil.copy(DATA / "coverage_synthetic.geojson", directory / "parcels.geojson")
        shutil.copy(DATA / "points.csv", directory / "points.csv")
        shutil.copy(DATA / "communes_points.geojson", directory / "communes_points.geojson")
        (directory / "zone.geojson").write_text(json.dumps(ZONE), encoding="utf-8")

    def project(self):
        """Build projet.gpkg with the first two documented commands."""
        self.stage()
        self.recipe(SKILL, "## Most common commands", 0)
        self.recipe(SKILL, "## Most common commands", 1)
        return self.output / "projet.gpkg"

    def rows(self, path, sql, *, dialect="SQLite"):
        output = self.run_tool("ogr2ogr", "-f", "CSV", "/vsistdout/", "-dialect", dialect, "-sql", sql, path)
        return list(csv.DictReader(io.StringIO(output)))

    def layers(self, path):
        with sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True) as db:
            return {name: (kind, srs) for name, kind, srs in db.execute(
                "SELECT c.table_name, g.geometry_type_name, g.srs_id FROM gpkg_contents c "
                "LEFT JOIN gpkg_geometry_columns g USING (table_name)")}

    def count(self, source, where, *options):
        output = self.run_tool("ogrinfo", "-q", *options, source, "communes", "-where", where, "-geom=NO")
        return output.count("code_insee (String)")

    def sheets(self):
        sheets = self.output / "sheets"
        sheets.mkdir()
        for name, where in (("sheet_1", "parcel_id <= 'P04'"), ("sheet_2", "parcel_id > 'P04'")):
            self.run_tool("ogr2ogr", "-nln", "parcels", "-where", where, sheets / f"{name}.gpkg", "parcels.geojson")
        return sheets

    def gdal_version(self):
        return tuple(map(int, re.search(r"GDAL (\d+)\.(\d+)", self.run_tool("gdalinfo", "--version")).groups()))


class SkillRecipeTests(VectorCase):
    def test_inspection_reports_the_missing_encoding(self):
        self.stage()
        output = self.recipe(SKILL, "## Inspect first").stdout
        self.assertIn("Feature Count: 3", output)
        self.assertRegex(output, r"(?m)SOURCE_ENCODING=\s*$")

    def test_common_commands_and_validation(self):
        project = self.project()
        for example in range(2, 6):
            self.recipe(SKILL, "## Most common commands", example)
        self.assertEqual(self.layers(project), {"communes": ("POINT", 2154), "parcels": ("MULTIPOLYGON", 2154)})
        communes = self.rows(project, "SELECT code_insee, nom FROM communes")
        self.assertEqual({row["code_insee"]: row["nom"] for row in communes}, NAMES)
        self.assertEqual(len(self.rows(project, "SELECT * FROM parcels")), 9)

        subset = self.rows(self.output / "communes_94.gpkg", "SELECT * FROM communes")
        self.assertEqual(sorted(row["code_insee"] for row in subset), ["94038", "94067"])
        self.assertEqual(list(subset[0]), ["code_insee", "nom"])
        self.assertEqual(self.layers(self.output / "communes_94.gpkg"), {"communes": ("POINT", 2154)})

        clip = self.rows(self.output / "parcels_clip.gpkg",
                         "SELECT parcel_id, ST_Area(geom) AS area FROM parcels ORDER BY parcel_id")
        self.assertEqual([row["parcel_id"] for row in clip], ["P01", "P05"])
        self.assertAlmostEqual(sum(float(row["area"]) for row in clip), 319.2, delta=0.1)

        points = self.rows(self.output / "points.gpkg", "SELECT id, ST_X(geom) AS x, ST_Y(geom) AS y FROM points")
        self.assertEqual([row["id"] for row in points], ["1", "2", "3"])
        self.assertAlmostEqual(float(points[0]["x"]), 2.4245)
        self.assertEqual(self.layers(self.output / "points.gpkg")["points"][1], 4326)

        web = json.loads((self.output / "parcels_web.geojson").read_text(encoding="utf-8"))
        self.assertNotIn("crs", web)
        first = web["features"][0]["geometry"]["coordinates"]
        while isinstance(first[0], list):
            first = first[0]
        self.assertAlmostEqual(first[0], 2.3597718, places=6)
        self.assertLessEqual(len(str(first[0]).split(".")[1]), 7)

        report = self.recipe(SKILL, "## Validate the output", 0).stdout
        self.assertIn("Layer name: communes", report)
        self.assertIn("Layer name: parcels", report)
        self.assertIn("suspicious characters: 0", self.recipe(SKILL, "## Validate the output", 1).stdout)

    def test_character_check_rejects_raw_and_latin1_readings(self):
        self.stage()
        for option in ([], ["-oo", "ENCODING=ISO-8859-1"]):
            with self.subTest(option=option):
                (self.output / "projet.gpkg").unlink(missing_ok=True)
                self.run_tool("ogr2ogr", *option, "-nln", "communes", "projet.gpkg", "communes.shp")
                result = self.recipe(SKILL, "## Validate the output", 1, check=False)
                self.assertEqual(result.returncode, 1)
                self.assertRegex(result.stdout, r"suspicious characters: [1-9]")

    def test_rewriting_without_update_replaces_the_geopackage(self):
        project = self.project()
        self.run_tool("ogr2ogr", "-nln", "other", project, "points.csv")
        self.assertEqual(self.layers(project), {"other": (None, None)})

    def test_numeric_clip_box_is_read_in_the_source_crs(self):
        project = self.project()
        self.run_tool("ogr2ogr", "-clipsrc", "2.35975", "48.82932", "2.35998", "48.82962",
                      "wrong.gpkg", project, "parcels")
        self.assertEqual(self.rows(self.output / "wrong.gpkg", "SELECT * FROM parcels"), [])


class ReferenceRecipeTests(VectorCase):
    def test_shapefile_export_keeps_short_names_and_text(self):
        self.stage()
        self.recipe(FORMATS, "## Shapefile limits")
        export = self.output / "export"
        self.assertEqual((export / "communes.cpg").read_text().strip(), "UTF-8")
        rows = self.rows(export / "communes.shp", "SELECT * FROM communes", dialect="OGRSQL")
        self.assertEqual(list(rows[0]), ["code_insee", "nom", "nom_maj", "remarque"])
        self.assertEqual({row["code_insee"]: row["nom"] for row in rows}, NAMES)
        self.assertTrue(all("–" in row["remarque"] for row in rows))
        self.assertIn("« œ »", rows[2]["remarque"])

    def test_default_shapefile_export_loses_characters(self):
        self.stage()
        self.run_tool("ogr2ogr", "default.shp", "communes_points.geojson")
        self.assertFalse((self.output / "default.cpg").exists())
        rows = self.rows(self.output / "default.shp", "SELECT * FROM \"default\"", dialect="OGRSQL")
        self.assertIn("nom_offi_1", rows[0])
        self.assertIn("C?uvres-et-Valsery", {row["nom_offici"] for row in rows})

    def test_encoding_recipe(self):
        self.stage()
        self.recipe(FORMATS, "## Fix the text encoding on read")
        rows = self.rows(self.output / "communes.gpkg", "SELECT code_insee, nom, remarque FROM communes")
        self.assertEqual({row["code_insee"]: row["nom"] for row in rows}, NAMES)
        self.assertIn("« œ »", rows[2]["remarque"])

    def test_filters_clip_selection_dissolve_and_like(self):
        project = self.project()
        self.recipe(FILTERS, "## Spatial filters and clipping", 0)
        clip = self.rows(self.output / "parcels_zone_clip.gpkg",
                         "SELECT parcel_id, ST_Area(geom) AS area FROM parcels")
        self.assertEqual(sorted(row["parcel_id"] for row in clip), ["P01", "P05"])
        self.assertAlmostEqual(sum(float(row["area"]) for row in clip), 319.2, delta=0.1)

        self.recipe(FILTERS, "## Spatial filters and clipping", 1)
        whole = self.rows(self.output / "parcels_zone.gpkg",
                          "SELECT parcel_id, ST_Area(geom) AS area FROM parcels_zone")
        self.assertEqual(sorted(row["parcel_id"] for row in whole), ["P01", "P05"])
        self.assertGreater(sum(float(row["area"]) for row in whole), 319.2)

        self.recipe(FILTERS, "## SQL dialects")
        dissolved = self.rows(self.output / "dissolved.gpkg", "SELECT n, ST_Area(geom) AS area FROM dissolved")
        self.assertEqual(dissolved[0]["n"], "9")
        self.assertAlmostEqual(float(dissolved[0]["area"]), 3191, delta=0.01)

        self.assertEqual(self.count(project, "nom LIKE 'saint%'", "-ro"), 1)
        shapefile, encoding = self.output / "communes.shp", ("-oo", "ENCODING=CP1252")
        self.assertEqual(self.count(shapefile, "nom LIKE 'saint%'", *encoding), 0)
        self.assertEqual(self.count(shapefile, "nom ILIKE 'saint%'", *encoding), 1)
        self.assertEqual(self.count(shapefile, "nom = 'L''Haÿ-les-Roses'", *encoding), 1)

    def test_merge_and_split(self):
        self.project()
        self.sheets()
        self.recipe(FILTERS, "## Merge files", 0)
        self.assertEqual(len(self.rows(self.output / "merged.gpkg", "SELECT * FROM parcels")), 9)
        self.recipe(FILTERS, "## Merge files", 1)
        traced = self.rows(self.output / "merged_traced.gpkg", "SELECT source FROM parcels_traced")
        self.assertEqual({row["source"] for row in traced}, {"sheet_1"})
        self.assertEqual(len(traced), 4)
        values = self.recipe(FILTERS, "## Split a layer").stdout
        self.assertEqual(sorted(row["code_insee"] for row in csv.DictReader(io.StringIO(values))),
                         sorted(NAMES))


class GDALVectorCLITests(VectorCase):
    def setUp(self):
        super().setUp()
        if not shutil.which("gdal") or self.gdal_version() < (3, 12):
            self.skipTest("The gdal vector examples need GDAL >= 3.12")
        self.stage()

    def test_info_and_convert_refuses_an_existing_output(self):
        output = self.recipe(CLI, "## Inspect and convert").stdout
        self.assertIn("Feature Count: 3", output)
        rows = self.rows(self.output / "communes_cli.gpkg", "SELECT code_insee, nom FROM communes")
        self.assertEqual({row["code_insee"]: row["nom"] for row in rows}, NAMES)
        again = subprocess.run(["gdal", "vector", "convert", "parcels.geojson", "communes_cli.gpkg"],
                               cwd=self.output, env=self.env, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("already exists", again.stderr)

    def test_pipeline_and_select_geometry(self):
        self.recipe(CLI, "## Pipelines")
        target = self.output / "communes_94_wgs84.gpkg"
        self.assertEqual(self.layers(target), {"communes": ("POINT", 4326)})
        rows = self.rows(target, "SELECT code_insee, nom, ST_X(geom) AS x FROM communes ORDER BY code_insee")
        self.assertEqual([row["nom"] for row in rows], ["L'Haÿ-les-Roses", "Saint-Mandé"])
        self.assertAlmostEqual(float(rows[1]["x"]), 2.419441, places=5)
        for fields, geometry in (("code_insee,nom", False), ("code_insee,nom,_ogr_geometry_", True)):
            with self.subTest(fields=fields):
                target = self.output / f"select_{geometry}.gpkg"
                self.run_tool("gdal", "vector", "pipeline", "read", "--oo", "ENCODING=CP1252", "communes.shp",
                              "!", "select", "--fields", fields, "!", "write", target)
                info = self.run_tool("ogrinfo", "-so", "-al", target)
                self.assertEqual("Geometry: None" in info, not geometry)
        self.run_tool("gdal", "vector", "pipeline", "read", "--oo", "ENCODING=CP1252", "communes.shp",
                      "!", "select", "--exclude", "--fields", "remarque", "!", "write", "excluded.gpkg")
        self.assertNotIn("remarque", self.run_tool("ogrinfo", "-so", "-al", "excluded.gpkg"))

    def test_clip_concat_and_partition(self):
        self.recipe(CLI, "## Clip, merge and split", 0)
        for name in ("parcels_clip_cli.gpkg", "parcels_bbox_cli.gpkg"):
            with self.subTest(output=name):
                clip = self.rows(self.output / name, "SELECT parcel_id, ST_Area(geom) AS area FROM parcels")
                self.assertEqual(sorted(row["parcel_id"] for row in clip), ["P01", "P05"])
                self.assertAlmostEqual(sum(float(row["area"]) for row in clip), 319.2, delta=0.5)
        self.sheets()
        self.recipe(CLI, "## Clip, merge and split", 1)
        merged = self.rows(self.output / "parcels_merged.gpkg", "SELECT source, count(*) AS n FROM parcels GROUP BY source")
        self.assertEqual({row["source"]: row["n"] for row in merged}, {"sheet_1": "4", "sheet_2": "5"})
        self.recipe(CLI, "## Clip, merge and split", 2)
        self.assertEqual(len(list((self.output / "parts").glob("*.gpkg"))), 3)


if __name__ == "__main__":
    unittest.main()
