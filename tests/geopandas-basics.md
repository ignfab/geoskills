# geopandas-basics

## GPD-01 — Spatial join

> Avec Python, trouve lesquels des points de data/points.csv sont dans la commune de
> Saint-Mandé (data/saint_mande.geojson).

**Expected skill:** `geopandas-basics`

**Expected result:** only point `id=1` (lon 2.4245, lat 48.8451) is in Saint-Mandé
(code INSEE 94067). Points 2 (Toulouse) and 3 (La Réunion) are not.

- [ ] builds a GeoDataFrame from the CSV with `gpd.points_from_xy` and `crs=4326`
- [ ] uses `gpd.sjoin` with `predicate="within"` (or `intersects`)
- [ ] aligns the CRS of the two layers before the join

## GPD-02 — Assign versus reproject

> Avec Python, lis data/monuments_sans_prj/monuments.shp et donne les coordonnées GPS
> (lon/lat) des monuments.

**Expected skill:** `geopandas-basics` (CRS reasoning may also load `crs-reprojection-france`)

**Expected result:** the shapefile has **no CRS** (`gdf.crs is None`); the coordinates are
Lambert-93. Notre-Dame de Paris ≈ (2.3499, 48.8530).

- [ ] detects that `gdf.crs` is `None`
- [ ] confirms the source CRS with `data/README.md` or a known landmark, then **assigns**
  with `set_crs(2154)` (does not reproject the raw coordinates)
- [ ] then reprojects with `to_crs(4326)`

## GPD-03 — Zonal statistics with rasterstats

> Avec Python, calcule l'altitude moyenne de la commune de Saint-Mandé
> (data/saint_mande.geojson) à partir des dalles MNT de data/mnt_dalles/.

**Expected skill:** `geopandas-basics` (loads `gdal-raster-basics` for the VRT at most)

**Expected result:** mean ≈ 50.15 m (min ≈ 39.30, max ≈ 54.08, count 9046).

- [ ] reprojects the commune to EPSG:2154 (the raster CRS) before `zonal_stats`
- [ ] handles the missing `.prj` of the raster tiles using the fixture metadata and a VRT
  with `-a_srs EPSG:2154`; GeoPandas `set_crs` applies to vectors, not raster files
- [ ] uses `rasterstats.zonal_stats` (or hands over to the CLI `gdal raster zonal-stats`)

## GPD-04 — Preserve row alignment after filtering

> Calcule les statistiques du MNT pour une sélection de polygones conservant leurs index
> d’origine (par exemple 42), puis rattache les résultats aux bons polygones.

- [ ] constructs the statistics DataFrame with the same index as the input GeoDataFrame
- [ ] checks that the join preserves IDs and does not silently introduce missing statistics

The automated test uses the Saint-Mandé fixture at index 42 and verifies its known statistics.

## GPD-N1 — Negative: one-shot download

> Télécharge les bâtiments de Saint-Mandé depuis le WFS de la Géoplateforme en GeoPackage.

**Expected skill:** `geopf-wfs-download` (a one-shot download does not need Python).
`geopandas-basics` may appear only if the user then asks to process the result.
