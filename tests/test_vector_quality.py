"""Regression tests for the vector-data-quality audit and repair workflow."""
import importlib.util
import unittest

from test_workflows import GDALCase
from skill_examples import run_example


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

    def test_audit_distinguishes_geometry_issue_classes(self):
        gdf = self.sample()
        comparable = ~gdf.geometry.isna() & ~gdf.geometry.is_empty
        duplicate_geometry = (
            comparable & gdf.geometry.normalize().duplicated(keep=False)
        )
        invalid = ~gdf.geometry.isna() & ~gdf.geometry.is_valid

        self.assertEqual(gdf.geometry.isna().tolist(), [False, False, False, True, False])
        self.assertEqual(gdf.geometry.is_empty.tolist(), [False, False, False, False, True])
        self.assertEqual(invalid.tolist(), [True, False, False, False, False])
        self.assertEqual(duplicate_geometry.tolist(), [False, True, True, False, False])
        self.assertEqual(gdf["id"].duplicated(keep=False).tolist(),
                         [False, True, True, False, False])
        self.assertIn("Self-intersection", gdf.geometry[invalid].is_valid_reason().iloc[0])

    def test_make_valid_and_roundtrip(self):
        import geopandas as gpd

        source = self.sample()
        quarantine_mask = source.geometry.isna() | source.geometry.is_empty
        quarantine = source.loc[quarantine_mask].copy()
        clean = source.loc[~quarantine_mask].copy()
        bad = ~clean.geometry.is_valid
        clean.loc[bad, "geometry"] = clean.geometry[bad].make_valid()

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


if __name__ == "__main__":
    unittest.main()
