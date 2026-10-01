"""Regression tests for the vector-data-quality audit and repair workflow."""
import importlib.util
import unittest

from test_workflows import GDALCase


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


if __name__ == "__main__":
    unittest.main()
