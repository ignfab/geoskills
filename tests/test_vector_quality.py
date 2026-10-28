"""Regression tests for the vector-data-quality audit and repair workflow."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import re
import shutil
import unittest
import warnings

from test_workflows import GDALCase
from skill_examples import read_example, run_example

FIXTURE = Path(__file__).resolve().parent / "data" / "coverage_synthetic.geojson"
VALIDITY = "vector-data-quality/references/geometry-validity.md"
COVERAGE = "vector-data-quality/references/coverage-topology.md"


def run_quietly(reference, heading, namespace, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as output:
        run_example(reference, heading, namespace, **kwargs)
    return namespace, output.getvalue()


class VectorQualityTests(GDALCase):
    @classmethod
    def setUpClass(cls):
        for module in ("geopandas", "shapely"):
            if importlib.util.find_spec(module) is None:
                raise unittest.SkipTest(
                    "Install tests/requirements-geospatial.txt for vector quality tests"
                )
        super().setUpClass()

    @staticmethod
    def sample():
        import geopandas as gpd
        from shapely.geometry import Polygon

        bowtie = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
        square = Polygon([(10, 10), (12, 10), (12, 12), (10, 12), (10, 10)])
        reversed_square = Polygon([(12, 12), (12, 10), (10, 10), (10, 12), (12, 12)])
        return gpd.GeoDataFrame(
            {
                "id": ["bad", "duplicate", "duplicate", None, "empty"],
                "status": ["active", "active", "active", "active", "unknown"],
            },
            geometry=[bowtie, square, reversed_square, None, Polygon()],
            crs=2154,
        )

    @staticmethod
    def parcels():
        import geopandas as gpd

        return gpd.read_file(FIXTURE).rename(columns={"parcel_id": "id"})

    def in_output_dir(self):
        previous = os.getcwd()
        os.chdir(self.output)
        self.addCleanup(os.chdir, previous)

    def require_coverage_api(self):
        import geopandas as gpd
        import shapely

        if not (hasattr(gpd.GeoSeries, "is_valid_coverage")
                and hasattr(shapely, "coverage_is_valid")):
            self.skipTest("Needs GeoPandas >= 1.1 with Shapely >= 2.1")

    def require_gdal_vector_cli(self):
        version = re.search(r"GDAL (\d+)\.(\d+)", self.run_tool("gdalinfo", "--version"))
        if not shutil.which("gdal") or tuple(map(int, version.groups())) < (3, 12):
            self.skipTest("The gdal vector validity commands need GDAL >= 3.12")

    def test_audit_distinguishes_geometry_issue_classes(self):
        gdf = self.sample()
        comparable = ~gdf.geometry.isna() & ~gdf.geometry.is_empty
        duplicate_geometry = (
            comparable & gdf.geometry.normalize().duplicated(keep=False)
        )
        audit = run_example("vector-data-quality/references/geometry-validity.md",
                            "## Classify geometry problems", {"gdf": gdf})
        invalid = audit["invalid"]

        self.assertEqual(audit["null"].tolist(), [False, False, False, True, False])
        self.assertEqual(audit["empty"].tolist(), [False, False, False, False, True])
        self.assertEqual(invalid.tolist(), [True, False, False, False, False])
        self.assertEqual(duplicate_geometry.tolist(), [False, True, True, False, False])
        self.assertEqual(gdf["id"].duplicated(keep=False).tolist(),
                         [False, True, True, False, False])
        self.assertIn("Self-intersection", audit["reasons"].iloc[0])
        self.assertEqual(audit["reason_type"].tolist(), ["Self-intersection"])

    def test_make_valid_and_roundtrip(self):
        import geopandas as gpd

        source = self.sample()
        quarantine_mask = source.geometry.isna() | source.geometry.is_empty
        quarantine = source.loc[quarantine_mask].copy()
        clean = source.loc[~quarantine_mask].copy()
        clean = run_example("vector-data-quality/references/geometry-validity.md",
                            "## Repair with `make_valid`", {"gdf": clean})["fixed"]

        self.assertTrue(quarantine["id"].isna().iloc[0])
        self.assertEqual(quarantine["id"].iloc[1], "empty")
        self.assertTrue(clean.geometry.is_valid.all())
        self.assertEqual(clean.loc[clean["id"] == "bad", "geometry"].iloc[0].geom_type,
                         "MultiPolygon")

        output = self.output / "repaired.gpkg"
        clean.to_file(output, layer="features")
        check = gpd.read_file(output, layer="features")
        self.assertEqual(len(check), 3)
        self.assertEqual(check.crs, clean.crs)
        self.assertTrue(check.geometry.is_valid.all())
        self.assertFalse(check.geometry.isna().any())
        self.assertFalse(check.geometry.is_empty.any())
        self.assertEqual(check["id"].tolist(), ["bad", "duplicate", "duplicate"])
        self.assertAlmostEqual(check.geometry.iloc[0].area, 2)
        self.assertFalse(source.geometry.iloc[0].is_valid)

    def test_documented_polygon_quarantine_keeps_collapsed_parts_auditable(self):
        import geopandas as gpd
        from shapely.geometry import Polygon

        source = self.sample()
        # A wholly collapsed polygon becomes a line, not a usable polygon.
        source.loc[0, "geometry"] = Polygon([(0, 0), (1, 1), (2, 2), (0, 0)])
        before = source.copy(deep=True)
        result = run_example("vector-data-quality/references/geometry-validity.md",
                             "## Repair with `make_valid`", {"gdf": source})
        result = run_example("vector-data-quality/references/geometry-validity.md",
                             "## Repair with `make_valid`", result, example=2)
        self.assertEqual(result["fixed"].index.tolist(), [1, 2])
        self.assertEqual(result["quarantine"].index.tolist(), [0, 3, 4])
        self.assertIn(result["quarantine"].geometry.iloc[0].geom_type,
                      ("LineString", "MultiLineString"))
        self.assertEqual(len(result["fixed"]) + len(result["quarantine"]), len(source))
        from geopandas.testing import assert_geodataframe_equal
        assert_geodataframe_equal(source, before)

    def test_duplicate_features_require_the_same_pair(self):
        import geopandas as gpd
        from shapely.geometry import Point

        source = gpd.GeoDataFrame(
            {"source": ["a", "a", "b", "b"], "source_id": ["1", "1", "2", "2"],
             "status": ["active"] * 4},
            geometry=[Point(0, 0), Point(1, 1), Point(0, 0), Point(1, 1)], crs=2154,
        )
        result = run_example("vector-data-quality/references/attributes-and-duplicates.md",
                             "### Duplicate features", {"gdf": source})
        self.assertEqual(result["duplicate_feature"].tolist(), [False] * 4)

    def test_duplicate_feature_keys_preserve_nulls_and_separators(self):
        import geopandas as gpd
        from shapely.geometry import Polygon

        square = Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)])
        source = gpd.GeoDataFrame(
            {"source": [None, "<NULL>", "a\x1fb", "a", "same", "same", "x", "x", "y", "y"],
             "source_id": ["1", "1", "c", "b\x1fc", "2", "2", "3", "3", "4", "4"],
             "status": ["active"] * 10},
            geometry=[square] * 5 + [square.reverse(), None, None, Polygon(), Polygon()],
            crs=2154,
        )
        result = run_example("vector-data-quality/references/attributes-and-duplicates.md",
                             "### Duplicate features", {"gdf": source})
        self.assertEqual(result["duplicate_feature"].tolist(),
                         [False, False, False, False, True, True, False, False, False, False])

    def test_cli_repair_discards_collapsed_collection_parts(self):
        import geopandas as gpd
        from shapely.geometry import Polygon

        spike = Polygon([(0, 0), (2, 0), (2, 2), (1, 2), (1, 3),
                         (1, 2), (0, 2), (0, 0)])
        source = gpd.GeoDataFrame({"id": ["spike"]}, geometry=[spike], crs=2154)
        python_result = source.geometry.make_valid().iloc[0]
        self.assertEqual({part.geom_type for part in python_result.geoms},
                         {"Polygon", "LineString"})
        path = self.output / "source.gpkg"
        source.to_file(path, layer="features")
        target = self.output / "repaired.gpkg"
        self.run_tool("ogr2ogr", "-f", "GPKG", target, path, "-makevalid")
        restored = gpd.read_file(target)
        self.assertEqual(len(restored), 1)
        self.assertEqual(restored.geometry.iloc[0].geom_type, "Polygon")
        self.assertAlmostEqual(restored.geometry.iloc[0].area, 4)


    def test_skill_workflow_audits_repairs_and_accounts_for_every_feature(self):
        self.in_output_dir()
        sample = self.sample()
        sample["geometry"] = sample.geometry.translate(653000, 6859000)
        sample.to_file("input.gpkg", layer="features")
        skill = "vector-data-quality/SKILL.md"
        namespace, _ = run_quietly(skill, "## Audit first", {})
        report = namespace["report"]
        self.assertEqual(report["features"], 5)
        self.assertEqual(report["null_geometry"] + report["empty_geometry"], 2)
        self.assertEqual(report["invalid_geometry"], 1)
        self.assertEqual(report["duplicate_geometry"], 2)
        self.assertFalse(report["has_z"])
        run_quietly(skill, "## Audit first", namespace, example=1)
        self.assertFalse(namespace["outside_crs_area"])
        _, output = run_quietly(skill, "## Audit first", namespace, example=2)
        self.assertRegex(output, r"(?m)^Self-intersection\s+1$")

        run_example(skill, "## Repair deliberately", namespace)
        _, output = run_quietly(skill, "## Validate the output", namespace)
        self.assertEqual(len(namespace["check"]), 3)
        self.assertEqual(len(namespace["quarantine"]), 2)
        self.assertIn("Area before/after:", output)

    def test_crs_area_check_flags_projected_coordinates_labelled_wgs84(self):
        self.in_output_dir()
        parcels = self.parcels()
        parcels.set_crs(4326, allow_override=True).to_file("input.gpkg", layer="features")
        skill = "vector-data-quality/SKILL.md"
        namespace, _ = run_quietly(skill, "## Audit first", {})
        run_quietly(skill, "## Audit first", namespace, example=1)
        self.assertTrue(namespace["outside_crs_area"])

    def test_documented_reasons_match_geos(self):
        import geopandas as gpd
        from shapely import from_wkt

        cases = {
            "Self-intersection": "POLYGON((0 0,2 2,0 2,2 0,0 0))",
            "Ring Self-intersection": "POLYGON((0 0,4 0,4 4,2 0,0 4,0 0))",
            "Hole lies outside shell": "POLYGON((0 0,4 0,4 4,0 4,0 0),(5 5,6 5,6 6,5 6,5 5))",
            "Holes are nested": "POLYGON((0 0,10 0,10 10,0 10,0 0),"
                                "(1 1,9 1,9 9,1 9,1 1),(2 2,8 2,8 8,2 8,2 2))",
            "Interior is disconnected": "POLYGON((0 0,10 0,10 10,0 10,0 0),"
                                        "(0 5,5 0,10 5,5 10,0 5))",
            "Nested shells": "MULTIPOLYGON(((0 0,10 0,10 10,0 10,0 0)),((2 2,8 2,8 8,2 8,2 2)))",
            "Too few points in geometry component": "POLYGON((0 0,1 1,0 0,0 0))",
            "Invalid Coordinate": "POLYGON((0 0,1 0,NaN 1,0 0))",
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # the NaN coordinate
            geometries = [from_wkt(wkt) for wkt in cases.values()]
        gdf = gpd.GeoDataFrame({"id": list(cases)}, geometry=geometries)
        audit, _ = run_quietly(VALIDITY, "## Classify geometry problems", {"gdf": gdf})
        self.assertEqual(audit["reason_type"].tolist(), list(cases))
        text = (Path(__file__).resolve().parents[1] / "skills" / VALIDITY).read_text(
            encoding="utf-8")
        for reason in cases:
            self.assertIn(f"| `{reason}` |", text)

    def test_repair_methods_differ_and_structure_keeps_polygons_only(self):
        import geopandas as gpd
        from shapely.geometry import MultiPolygon, Polygon, box

        self.require_coverage_api()
        spike = Polygon([(0, 0), (2, 0), (2, 2), (1, 2), (1, 3), (1, 2), (0, 2), (0, 0)])
        collapsed = Polygon([(0, 0), (1, 1), (2, 2), (0, 0)])
        nested = MultiPolygon([box(0, 0, 10, 10), box(2, 2, 8, 8)])
        source = gpd.GeoDataFrame({"id": ["spike", "collapsed", "nested"]},
                                  geometry=[spike, collapsed, nested], crs=2154)
        linework = run_example(VALIDITY, "## Repair with `make_valid`",
                               {"gdf": source})["fixed"]
        result = run_example(VALIDITY, "### Choose the repair method", {"gdf": source})
        structure = result["fixed"]
        self.assertEqual(linework.geometry.iloc[0].geom_type, "GeometryCollection")
        self.assertEqual(structure.geometry.iloc[0].geom_type, "Polygon")
        self.assertAlmostEqual(structure.geometry.iloc[0].area, 4)
        self.assertTrue(structure.geometry.iloc[1].is_empty)
        self.assertAlmostEqual(linework.geometry.iloc[2].area, 64)
        self.assertAlmostEqual(structure.geometry.iloc[2].area, 100)
        result = run_example(VALIDITY, "## Repair with `make_valid`", result, example=2)
        self.assertEqual(result["fixed"]["id"].tolist(), ["spike", "nested"])
        self.assertEqual(result["quarantine"]["id"].tolist(), ["collapsed"])

    def test_suspicious_valid_geometries_are_flagged_not_removed(self):
        import geopandas as gpd

        parcels = self.parcels()
        result, _ = run_quietly(VALIDITY, "## Valid but suspicious",
                                {"gdf": parcels, "gpd": gpd})
        flags = result["flags"].set_index("id")
        self.assertTrue(parcels.geometry.is_valid.all())
        self.assertEqual(flags.index[flags["thin"]].tolist(), ["P09"])
        self.assertFalse(flags["tiny"].any())
        self.assertEqual(flags.loc["P01", "repeated_points"], 1)
        self.assertEqual(int(flags["repeated_points"].sum()), 1)
        self.assertFalse(flags["has_z"].any())
        self.assertEqual(len(flags), len(parcels))

    def test_severity_report_ranks_issues(self):
        self.in_output_dir()
        gdf = self.sample()
        reference = "vector-data-quality/references/attributes-and-duplicates.md"
        namespace = run_example(reference, "## Produce an audit report", {"gdf": gdf})
        namespace, _ = run_quietly(reference, "### Severity levels", namespace)
        counts = namespace["issues"]["severity"].value_counts().to_dict()
        self.assertEqual(counts, {"blocker": 3, "major": 2, "minor": 2})
        self.assertTrue((self.output / "quality_issues.csv").is_file())

    def test_overlap_pairs_and_enclosed_gaps_on_fixture(self):
        import geopandas as gpd

        parcels = self.parcels()
        result, _ = run_quietly(COVERAGE, "## Find overlapping pairs", {"gdf": parcels})
        overlaps = result["overlaps"]
        self.assertEqual(overlaps[["left_id", "right_id"]].values.tolist(), [["P02", "P03"]])
        self.assertAlmostEqual(overlaps["overlap_area"].iloc[0], 1.0)
        self.assertGreater(len(result["pairs"]), len(overlaps))
        result, _ = run_quietly(COVERAGE, "## Find gaps", {"gdf": parcels, "gpd": gpd})
        self.assertEqual(len(result["holes"]), 1)
        self.assertAlmostEqual(result["holes"].area.iloc[0], 16.0)

    def test_coverage_checks_on_fixture(self):
        self.require_coverage_api()
        parcels = self.parcels()
        result, output = run_quietly(COVERAGE, "## Check the coverage", {"gdf": parcels})
        self.assertEqual(result["flagged"]["id"].tolist(), ["P02", "P03"])
        self.assertTrue(output.startswith("False"))
        result, _ = run_quietly(COVERAGE, "## Find gaps", result, example=1)
        narrow = result["narrow"]
        self.assertEqual(parcels.loc[~narrow.is_empty, "id"].tolist(),
                         ["P02", "P03", "P04", "P09"])
        _, output = run_quietly("vector-data-quality/SKILL.md",
                                "## Check topology between features", {"src": parcels})
        self.assertEqual(output.strip(), "False")

    def test_gdal_check_geometry_and_review_repair(self):
        import geopandas as gpd
        from shapely.geometry import Polygon

        self.require_gdal_vector_cli()
        spike = Polygon([(0, 0), (2, 0), (2, 2), (1, 2), (1, 3), (1, 2), (0, 2), (0, 0)])
        bowtie = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
        source = gpd.GeoDataFrame({"id": ["spike", "bowtie"]}, geometry=[spike, bowtie],
                                  crs=2154)
        source.to_file(self.output / "input.gpkg", layer="features")
        check = read_example(VALIDITY, "## GDAL command line", language="bash", example=1)
        self.run_tool("bash", "-eu", "-c", check)
        errors = gpd.read_file(self.output / "validity_errors.gpkg")
        self.assertEqual(sorted(errors["id"]), ["bowtie", "spike"])
        self.assertEqual(set(errors["error"]), {"Self-intersection"})

        review = read_example(VALIDITY, "## GDAL command line", language="bash", example=3)
        self.run_tool("bash", "-eu", "-c", review)
        repaired = gpd.read_file(self.output / "repaired_review.gpkg")
        self.assertEqual(repaired.set_index("id").geom_type.to_dict(),
                         {"spike": "GeometryCollection", "bowtie": "MultiPolygon"})
        self.assertTrue(repaired.geometry.is_valid.all())

    def test_gdal_check_coverage_matches_python_edges(self):
        import geopandas as gpd

        self.require_gdal_vector_cli()
        self.parcels().to_file(self.output / "input.gpkg", layer="features")
        recipe = read_example(COVERAGE, "## GDAL command line", language="bash")
        self.run_tool("bash", "-eu", "-c", recipe)
        edges = gpd.read_file(self.output / "coverage_errors.gpkg")
        self.assertEqual(len(edges), 4)
        self.assertTrue(edges.geom_type.isin(["LineString", "MultiLineString"]).all())
        self.assertGreater(edges.length.sum(), 0)


if __name__ == "__main__":
    unittest.main()
