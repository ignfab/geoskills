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
        joined = run_example("geopandas-basics/references/spatial-operations.md",
            "## Spatial join", {"gpd": gpd, "points": points, "communes": commune})["joined"]
        self.assertEqual(len(joined), 3)
        self.assertEqual(joined.loc[joined.index_right.notna(), "id"].tolist(), [1])
        matched = joined.loc[joined.index_right.notna()]
        self.assertEqual(matched["code_insee"].tolist(), ["94067"])
        self.assertEqual(matched["nom_officiel"].tolist(), ["Saint-Mandé"])

    def test_documented_join_keeps_unmatched_and_multiple_matches(self):
        import geopandas as gpd
        from shapely.geometry import Point, box

        points = gpd.GeoDataFrame({"id": ["inside", "edge", "overlap", "outside"]},
            geometry=[Point(1, 1), Point(0, 1), Point(3, 1), Point(9, 9)], crs=2154)
        communes = gpd.GeoDataFrame({"code_insee": ["001", "002"], "nom_officiel": ["A", "B"]},
            geometry=[box(0, 0, 4, 4), box(2, 0, 6, 4)], crs=2154)
        communes.index.name = "municipality_row"
        joined = run_example("geopandas-basics/references/spatial-operations.md",
            "## Spatial join", {"gpd": gpd, "points": points, "communes": communes})["joined"]
        self.assertEqual(len(joined), 5)
        self.assertEqual(joined.groupby("id").size().to_dict(),
                         {"inside": 1, "edge": 1, "overlap": 2, "outside": 1})
        self.assertEqual(joined.loc[joined.code_insee.isna(), "id"].tolist(), ["edge", "outside"])
        self.assertEqual(set(joined.loc[joined.id == "overlap", "code_insee"]), {"001", "002"})
        self.assertIn("municipality_row", joined)
        self.assertEqual(joined.crs, points.crs)
        for row in joined.itertuples():
            self.assertTrue(row.geometry.equals(points.loc[points.id == row.id].geometry.iloc[0]))

    def test_documented_nearest_join_reports_metres(self):
        import geopandas as gpd
        from shapely.geometry import Point

        points = gpd.GeoDataFrame({"id": ["a", "b"]},
            geometry=[Point(650000, 6860000), Point(650300, 6860400)], crs=2154)
        stations = gpd.GeoDataFrame({"station": ["near", "far"]},
            geometry=[Point(650000, 6860000), Point(660000, 6860000)], crs=2154)
        result = run_example("geopandas-basics/references/spatial-operations.md",
            "## Spatial join", {"gpd": gpd, "points": points, "gares": stations}, example=1)["nearest"]
        self.assertEqual(result["id"].tolist(), ["a", "b"])
        self.assertEqual(result["station"].tolist(), ["near", "near"])
        self.assertEqual(result["dist_m"].tolist(), [0, 500])

    def test_documented_overlay_cuts_geometry_and_preserves_attributes(self):
        import geopandas as gpd
        from shapely.geometry import box

        zones = gpd.GeoDataFrame({"zone_id": ["001"]}, geometry=[box(0, 0, 4, 4)], crs=2154)
        communes = gpd.GeoDataFrame({"code_insee": ["002"]}, geometry=[box(2, 0, 6, 4)], crs=2154)
        result = run_example("geopandas-basics/references/spatial-operations.md",
            "## Overlay", {"gpd": gpd, "zones": zones, "communes": communes})
        for key, area in (("inter", 8), ("diff", 8), ("union", 24)):
            with self.subTest(operation=key):
                self.assertEqual(result[key].crs.to_epsg(), 2154)
                self.assertTrue(result[key].geometry.is_valid.all())
                self.assertAlmostEqual(result[key].area.sum(), area)
        self.assertTrue(result["inter"].geometry.iloc[0].equals(box(2, 0, 4, 4)))
        self.assertEqual(result["inter"][["zone_id", "code_insee"]].values.tolist(), [["001", "002"]])
        self.assertEqual(zones.area.tolist(), [16])  # Inputs remain intact.

    def test_documented_buffer_reprojects_and_keeps_attributes(self):
        import geopandas as gpd
        from shapely.geometry import Point

        source = gpd.GeoDataFrame({"id": ["001"], "note": [None]},
                                  geometry=[Point(2.35, 48.85)], crs=4326)
        result = run_example("geopandas-basics/references/spatial-operations.md",
                             "## Buffer", {"gdf": source})
        result = run_example("geopandas-basics/references/spatial-operations.md",
                             "## Buffer", result, example=1)["tampon"]
        self.assertEqual(result.crs.to_epsg(), 2154)
        self.assertEqual(result["id"].tolist(), ["001"])
        self.assertTrue(result["note"].isna().all())
        self.assertAlmostEqual(result.area.iloc[0], 31415.93, delta=60)
        center = source.to_crs(2154).geometry.iloc[0]
        self.assertLess(result.geometry.iloc[0].centroid.distance(center), 0.001)
        self.assertEqual(source.crs.to_epsg(), 4326)
        self.assertEqual(source.geom_type.tolist(), ["Point"])

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
        from geopandas.testing import assert_geodataframe_equal
        assert_geodataframe_equal(restored, points)
        gpkg = self.output / "points.gpkg"
        points.to_file(gpkg, layer="original")
        points.to_file(gpkg, layer="copy")
        self.assertEqual(set(gpd.list_layers(gpkg)["name"]), {"original", "copy"})
        for layer in ("original", "copy"):
            assert_geodataframe_equal(gpd.read_file(gpkg, layer=layer), points)

    def test_geoparquet_preserves_string_ids_nulls_and_repeated_index(self):
        import geopandas as gpd
        import pandas as pd
        from geopandas.testing import assert_geodataframe_equal
        from shapely.geometry import Point

        source = gpd.GeoDataFrame({"id": ["001", "010", "100"],
            "population": pd.array([1, None, 0], dtype="Int64"), "label": ["École", None, ""]},
            geometry=[Point(2.35, 48.85), None, Point(2.4, 48.9)], crs=4326,
            index=pd.Index([42, 42, 7], name="source_row"))
        path = self.output / "nullable.parquet"
        source.to_parquet(path)
        assert_geodataframe_equal(gpd.read_parquet(path), source)

    def test_zonal_stats_distinguishes_zero_nodata_and_outside(self):
        import geopandas as gpd
        import numpy as np
        import pandas as pd
        from affine import Affine
        from rasterstats import zonal_stats
        from shapely.geometry import box

        raster = np.array([[0, -9999], [10, 20]], dtype="float32")
        zones = gpd.GeoDataFrame({"id": ["zero", "nodata", "outside", "all"]},
            geometry=[box(0, 1, 1, 2), box(1, 1, 2, 2), box(3, 0, 4, 1), box(0, 0, 2, 2)],
            crs=2154, index=[7, 7, 42, 0])
        stats = zonal_stats(zones, raster, affine=Affine(1, 0, 0, 0, -1, 2), nodata=-9999,
                            stats=["mean", "min", "max", "count"])
        result = run_example("geopandas-basics/references/zonal-stats.md", "## Basic usage",
                             {"communes": zones, "stats": stats}, example=1)["communes"]
        self.assertEqual(result["id"].tolist(), ["zero", "nodata", "outside", "all"])
        self.assertEqual(result.index.tolist(), [7, 7, 42, 0])
        self.assertEqual(result["count"].tolist(), [1, 0, 0, 3])
        self.assertEqual(result["mean"].iloc[0], 0)
        self.assertEqual(result["mean"].iloc[3], 10)
        for column in ("mean", "min", "max"):
            self.assertTrue(pd.isna(result[column].iloc[1:3]).all())
        self.assertEqual(result["min"].iloc[3], 0)
        self.assertEqual(result["max"].iloc[3], 20)

    def test_zonal_stats_rejects_missing_or_extra_results(self):
        import geopandas as gpd
        from geopandas.testing import assert_geodataframe_equal

        zones = gpd.read_file(DATA / "saint_mande.geojson")
        original = zones.copy(deep=True)
        for stats in ([], [{"mean": 1}, {"mean": 2}]):
            with self.subTest(stats=stats), self.assertRaises(AssertionError):
                run_example("geopandas-basics/references/zonal-stats.md", "## Basic usage",
                            {"communes": zones, "stats": stats}, example=1)
            assert_geodataframe_equal(zones, original)

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
