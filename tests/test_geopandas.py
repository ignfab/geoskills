"""Optional Python geospatial workflows and index-alignment regression tests."""
import importlib.util
import unittest

from test_workflows import DATA, GDALCase
from skill_examples import run_example


class GeoPandasTests(GDALCase):
    @classmethod
    def setUpClass(cls):
        for module in ("geopandas", "rasterstats", "pyarrow"):
            if importlib.util.find_spec(module) is None:
                raise unittest.SkipTest("Install tests/requirements-geospatial.txt for GeoPandas tests")
        super().setUpClass()

    def test_spatial_join(self):
        import geopandas as gpd
        import pandas as pd
        rows = pd.read_csv(DATA / "points.csv")
        points = gpd.GeoDataFrame(rows, geometry=gpd.points_from_xy(rows.lon, rows.lat), crs=4326)
        commune = gpd.read_file(DATA / "saint_mande.geojson").to_crs(points.crs)
        joined = gpd.sjoin(points, commune[["geometry"]], how="left", predicate="within")
        self.assertEqual(len(joined), 3)
        self.assertEqual(joined.loc[joined.index_right.notna(), "id"].tolist(), [1])

    def test_crs_and_format_roundtrip(self):
        import geopandas as gpd
        points = gpd.read_file(DATA / "monuments_sans_prj/monuments.shp")
        self.assertIsNone(points.crs)
        points = points.set_crs(2154).to_crs(4326)
        self.assertAlmostEqual(points.geometry.iloc[0].x, 2.3499, delta=0.00001)
        self.assertAlmostEqual(points.geometry.iloc[0].y, 48.8530, delta=0.00001)
        parquet = self.output / "points.parquet"
        points.to_parquet(parquet)
        restored = gpd.read_parquet(parquet)
        self.assertEqual(restored.crs, points.crs)
        self.assertTrue(restored.geometry.equals(points.geometry))
        gpkg = self.output / "points.gpkg"
        points.to_file(gpkg, layer="original")
        points.to_file(gpkg, layer="copy")
        self.assertEqual(set(gpd.list_layers(gpkg)["name"]), {"original", "copy"})
        self.assertEqual(len(gpd.read_file(gpkg, layer="original")), 3)

    def test_zonal_stats_with_filtered_index(self):
        import geopandas as gpd
        import pandas as pd
        from rasterstats import zonal_stats
        commune = gpd.read_file(DATA / "saint_mande.geojson").to_crs(2154)
        commune.index = pd.Index([42], name="source_row")
        stats = zonal_stats(commune, self.mosaic(), stats=["mean", "min", "max", "count"])
        result = run_example("geopandas-basics/references/zonal-stats.md", "## Basic usage",
                             {"communes": commune, "stats": stats}, example=1)["communes"]
        self.assertEqual(result.index.tolist(), [42])
        self.assertEqual(result.loc[42, "count"], 9046)
        self.assertAlmostEqual(result.loc[42, "mean"], 50.15, delta=0.05)
        self.assertAlmostEqual(result.loc[42, "min"], 39.30, delta=0.05)
        self.assertAlmostEqual(result.loc[42, "max"], 54.08, delta=0.05)

    def test_zonal_stats_with_repeated_index(self):
        import geopandas as gpd
        import pandas as pd
        from shapely.geometry import box
        from rasterstats import zonal_stats

        # Separate source cells have different values but the same dataframe index.
        zones = gpd.GeoDataFrame({"id": ["west", "east"]},
            geometry=[box(656700, 6861290, 656710, 6861300),
                      box(657000, 6861290, 657010, 6861300)],
            crs=2154, index=pd.Index([42, 42], name="source_row"))
        stats = zonal_stats(zones, self.mosaic(), stats=["mean", "count"])
        self.assertNotEqual(stats[0]["mean"], stats[1]["mean"])
        result = run_example("geopandas-basics/references/zonal-stats.md", "## Basic usage",
                             {"communes": zones, "stats": stats}, example=1)["communes"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result.index.tolist(), [42, 42])
        self.assertEqual(result["id"].tolist(), ["west", "east"])
        self.assertEqual(result["mean"].tolist(), [row["mean"] for row in stats])
        self.assertEqual(result["count"].tolist(), [1, 1])

    def test_zonal_stats_does_not_overwrite_source_attributes(self):
        import geopandas as gpd

        zones = gpd.read_file(DATA / "saint_mande.geojson")
        zones["mean"] = "source attribute"
        with self.assertRaises(AssertionError):
            run_example("geopandas-basics/references/zonal-stats.md", "## Basic usage",
                        {"communes": zones, "stats": [{"mean": 50}]}, example=1)
        self.assertEqual(zones["mean"].tolist(), ["source attribute"])


if __name__ == "__main__":
    unittest.main()
