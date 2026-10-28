"""Regression cases for complete exports, review policies and new skill recipes."""
import csv
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from skill_examples import run_example

ROOT = Path(__file__).resolve().parents[1]


def helper(skill, filename):
    path = ROOT / "skills" / skill / "scripts" / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EXPORT = helper("geopf-wfs-download", "check_export.py")
CLASSIFY = helper("geopf-geocoding", "classify_results.py")
FEED = helper("geopf-download-files", "inspect_feed.py")


class ExportCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.path = self.directory / "export.gpkg"
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE gpkg_contents(table_name TEXT, data_type TEXT)")
            db.execute("INSERT INTO gpkg_contents VALUES('features','features')")
            db.execute("CREATE TABLE features(fid INTEGER PRIMARY KEY, source_id TEXT)")
        self.before, self.after = self.directory / "before.xml", self.directory / "after.xml"
        self.hits("5")

    def hits(self, count, after=None):
        for path, value in ((self.before, count), (self.after, count if after is None else after)):
            path.write_text(f'<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" numberMatched="{value}"/>')

    def pages(self, pages):
        with sqlite3.connect(self.path) as db:
            for page in pages:
                db.executemany("INSERT INTO features(source_id) VALUES(?)", [(x,) for x in page])

    def result(self):
        return EXPORT.check_export(self.path, "features", "source_id", self.before, self.after)

    def test_complete_page_set_preserves_source_ids(self):
        self.pages([["01", "02"], ["03", "04"], ["05"]])
        result = self.result()
        self.assertEqual(result["status"], "consistent")
        self.assertEqual((result["count"], result["distinct_ids"]), (5, 5))

    def test_missing_last_page_and_repeated_page_are_detected(self):
        self.pages([["01", "02"], ["03", "04"]])
        self.assertIn("count_mismatch", self.result()["issues"])
        self.pages([["04"]])  # Right count, wrong contents.
        self.assertIn("duplicate_source_ids", self.result()["issues"])
        self.assertEqual(self.result()["status"], "unverified")

    def test_null_blank_ids_and_unknown_or_changing_count(self):
        self.pages([["01", None, "", "  ", "05"]])
        self.assertEqual(self.result()["missing_ids"], 3)
        self.hits("unknown")
        self.assertIn("unknown_expected_count", self.result()["issues"])
        self.hits("5", "6")
        self.assertIn("source_count_changed", self.result()["issues"])

    def test_exception_missing_source_field_and_read_only_typo(self):
        self.before.write_text('<ExceptionReport/>')
        with self.assertRaises(ValueError):
            self.result()
        self.hits("0")
        with self.assertRaises(ValueError):
            EXPORT.check_export(self.path, "features", "unknown", self.before, self.after)
        missing = self.directory / "typo.gpkg"
        with self.assertRaises(sqlite3.OperationalError):
            EXPORT.check_export(missing, "features", "source_id", self.before, self.after)
        self.assertFalse(missing.exists())

    def test_cli_fails_an_incomplete_export(self):
        self.pages([["01"]])
        script = ROOT / "skills/geopf-wfs-download/scripts/check_export.py"
        result = subprocess.run([sys.executable, str(script), str(self.path), "--layer", "features",
                                 "--id-field", "source_id", "--hits-before", str(self.before),
                                 "--hits-after", str(self.after)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("count_mismatch", json.loads(result.stdout)["issues"])


class GeocodingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(id="001", expected_citycode="01001", result_citycode="01001",
                        result_status="ok", result_score="0.95", result_score_next="0.4",
                        result_type="housenumber", longitude="2.35", latitude="48.85")
        self.policy = dict(min_score=0.7, min_margin=0.1, city_column="expected_citycode",
                           accepted_types=["housenumber"])

    def test_statuses_and_independent_quality_failures(self):
        cases = [({}, "accepted", "policy_pass"),
                 ({"result_status": "not-found"}, "unmatched", "not_found"),
                 ({"result_score_next": "0.94"}, "review", "ambiguous_candidates"),
                 ({"result_citycode": "10001"}, "review", "city_mismatch"),
                 ({"result_type": "street"}, "review", "unexpected_match_type"),
                 ({"result_status": "error"}, "review", "service_error"),
                 ({"result_score": "nan"}, "review", "invalid_score"),
                 ({"result_score_next": "infinity"}, "review", "invalid_second_score"),
                 ({"longitude": "181"}, "review", "invalid_longitude"),
                 ({"latitude": "nan"}, "review", "invalid_latitude"),
                 ({"result_score_next": ""}, "accepted", "policy_pass"),
                 ({"result_score": "0.9", "result_score_next": "0.8"}, "accepted", "policy_pass")]
        for changes, status, reason in cases:
            with self.subTest(changes=changes):
                actual = CLASSIFY.classify(dict(self.row, **changes), **self.policy)
                self.assertEqual(actual[0], status)
                self.assertIn(reason, actual[1])

    def test_csv_conserves_rows_ids_and_all_input_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / "input.csv", Path(directory) / "output.csv"
            rows = [self.row, dict(self.row, id="002", result_score_next="0.94"),
                    dict(self.row, id="003", result_status="not-found")]
            with source.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(self.row))
                writer.writeheader(); writer.writerows(rows)
            original = source.read_bytes()
            report = CLASSIFY.classify_file(source, target, **self.policy)
            with target.open(newline="", encoding="utf-8") as handle:
                actual = list(csv.DictReader(handle))
            self.assertEqual([{k: row[k] for k in self.row} for row in actual], rows)
            self.assertEqual(report["counts"], dict(accepted=1, review=1, unmatched=1))
            self.assertEqual(source.read_bytes(), original)
            with self.assertRaises(FileExistsError):
                CLASSIFY.classify_file(source, target, **self.policy)
            with self.assertRaises(FileExistsError):
                CLASSIFY.classify_file(source, source, **self.policy)

    def test_malformed_csv_and_output_columns_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            source, target = Path(directory) / "input.csv", Path(directory) / "output.csv"
            for content in ("a,a\n1,2\n", ",".join(self.row) + "\nmissing,fields\n",
                            ",".join([*self.row, "review_status"]) + "\n"):
                source.write_text(content)
                with self.assertRaises(ValueError):
                    CLASSIFY.classify_file(source, target, **self.policy)
                self.assertFalse(target.exists())


class CatalogueTests(unittest.TestCase):
    def inspect(self, *, total=3, page=1, ids=("a", "b"), size=2):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "feed.xml"
            path.write_text(f'<feed xmlns="http://www.w3.org/2005/Atom" '
                            f'xmlns:g="{FEED.GPF[1:-1]}" g:page="{page}" '
                            f'g:pagesize="{size}" g:totalentries="{total}">' +
                            ''.join(f'<entry><id>{i}</id><title>{i}</title>'
                                    f'<link rel="alternate" href="https://example.org/{i}"/></entry>'
                                    for i in ids) + '</feed>')
            return FEED.inspect_feed(path)

    def test_first_last_and_empty_pages(self):
        self.assertEqual(self.inspect()["next_page"], 2)
        self.assertIsNone(self.inspect(page=2, ids=("c",))["next_page"])
        self.assertEqual(self.inspect(total=0, ids=())["entries"], [])

    def test_truncated_duplicate_and_invalid_pages(self):
        for kwargs in ({"ids": ("a",)}, {"ids": ("a", "a")}, {"page": 0}, {"size": 51}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.inspect(**kwargs)


class GeographicAPIRecipeTests(unittest.TestCase):
    def attach(self, elevations):
        return run_example("geopf-altimetry/references/points-and-profiles.md", "## Attach point elevations",
                           dict(rows=[dict(id="001", latitude="48.85", longitude="2.35"),
                                      dict(id="002", latitude="0", longitude="0")],
                                response={"elevations": elevations}, resource="test-terrain",
                                vertical_reference="unknown"))["result"]

    def test_elevations_preserve_ids_and_nodata_without_false_vertical_crs(self):
        result = self.attach([dict(lon=2.35, lat=48.85, z=42), dict(lon=0, lat=0, z=-99999)])
        self.assertEqual([r["id"] for r in result], ["001", "002"])
        self.assertEqual(result[0]["elevation_m"], 42)
        self.assertEqual(result[1]["elevation_m"], "")
        self.assertEqual(result[1]["elevation_status"], "nodata")
        self.assertTrue(all(r["vertical_reference"] == "unknown" for r in result))

    def test_missing_reordered_and_nonfinite_elevations_are_rejected(self):
        for points in ([], [dict(lon=0, lat=0, z=0), dict(lon=2.35, lat=48.85, z=42)],
                       [dict(lon=2.35, lat=48.85, z=float('nan')), dict(lon=0, lat=0, z=0)]):
            with self.subTest(points=points), self.assertRaises(ValueError):
                self.attach(points)

    def export(self, response, operation="route"):
        return run_example("geopf-routing/references/reachable-areas.md", "## Export the response geometry",
                           dict(response=response, operation=operation))["collection"]

    def test_navigation_export_preserves_units_version_and_direction(self):
        route = dict(crs="EPSG:4326", geometry=dict(type="LineString", coordinates=[[2,48],[2.01,48]]),
                     resourceVersion="fixture-edition", distance=750, duration=600,
                     distanceUnit="meter", timeUnit="second")
        feature = self.export(route)["features"][0]
        self.assertEqual(feature["properties"]["timeUnit"], "second")
        self.assertEqual(feature["properties"]["resourceVersion"], "fixture-edition")
        area = dict(crs="EPSG:4326", geometry=dict(type="Polygon", coordinates=[[[2,48],[2.01,48],[2,48.01],[2,48]]]),
                    direction="arrival", costValue=300, timeUnit="second")
        self.assertEqual(self.export(area, "isochrone")["features"][0]["properties"]["direction"], "arrival")
        for invalid in (dict(route, crs="EPSG:2154"), dict(route, duration=-1),
                        dict(route, geometry={}), dict(route, distance=float('inf'))):
            with self.assertRaises(ValueError):
                self.export(invalid)


if __name__ == "__main__":
    unittest.main()
