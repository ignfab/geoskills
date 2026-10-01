# Zonal statistics

Compute statistics of a raster (elevation, temperature, population…) inside each polygon of
a vector layer (communes, parcels, buffers…) with `gdal raster zonal-stats`.

Requires **GDAL 3.12 or later** (the unified `gdal` CLI). Check with `gdal --version`. For a
Python alternative (`rasterstats`), see the `geopandas-basics` skill.

## Basic syntax

```bash
gdal raster zonal-stats \
  --stat mean --stat min --stat max --stat count \
  --zones communes.gpkg --include-field nom_officiel \
  -f GPKG mnt.tif stats.gpkg
```

Each output feature holds the requested fields plus one column per statistic:

```
nom_officiel (String) = Saint-Mandé
mean (Real) = 50.146
count (Real) = 9046
```

Write a CSV instead with `-f CSV stats.csv`; add the polygon geometries with
`--include-geom` (GDAL ≥ 3.13).

For a single polygon on older GDAL, `gdalwarp -cutline ... -crop_to_cutline` followed by
`gdalinfo -stats` on the masked raster is an alternative. Keep the original grid and set
nodata; resampling the DEM changes the statistics. This does not produce a per-polygon
table for multiple zones.

## Options

| Option | Description |
|--------|-------------|
| `--stat <name>` | Statistic to compute, repeatable: `count`, `min`, `max`, `mean`, `stdev`, `sum`, `mode`, `minority`, `variety`, `unique`, `frac`, `coverage`, `weighted_mean`, … |
| `--zones <file>` | Vector dataset with the zone polygons (**same CRS as the raster**, see below) |
| `--zones-layer <name>` | Layer to use when the zones file has several |
| `--include-field <name>` | Zone field copied to the output, repeatable (`ALL`, `NONE` require GDAL ≥ 3.13) |
| `--include-geom` | Copy the zone geometry to the output (GDAL ≥ 3.13) |
| `--pixels default\|fractional\|all-touched` | Which pixels count: centre inside (default), weighted by the covered fraction, or any touched pixel |
| `-b <n>` | Raster band (repeatable) |
| `--weights <raster>` | Weighting raster for the `weighted_*` statistics |

`--pixels fractional` weights border pixels by the exact fraction the polygon covers —
use it for small polygons relative to the pixel size. It requires a GDAL build with
GEOS ≥ 3.14. These options were checked against the official GDAL documentation on
2026-09-30; run `gdal raster zonal-stats --help` to check the installed build.

## Pitfall: the zones are NOT reprojected

Unlike `gdalwarp -cutline`, `zonal-stats` does **not** reproject the zones to the raster
CRS. With mismatched CRS it only emits `Warning 1: Inputs and zones do not have the same
SRS` and returns empty statistics (`count = 0`). Reproject the zones first:

```bash
ogr2ogr -t_srs EPSG:2154 communes_l93.gpkg communes_4326.geojson
gdal raster zonal-stats --stat mean \
  --zones communes_l93.gpkg -f GPKG mnt_l93.tif stats.gpkg
```

## Pitfall: undeclared nodata

Nodata pixels are excluded only if the value is **declared** in the raster. If it is not,
sentinel values poison the results (a DEM with undeclared `-9999` borders returns
`mean = -2462` instead of `50`). Check with `gdalinfo`, then declare it:

```bash
gdal_translate -a_nodata -9999 mnt.tif mnt_nodata.tif
```

## Pitfall: `--include-field` must exist

A wrong field name fails with `ERROR 1: Field <name> not found.` — list the real names
first with `ogrinfo -al -so communes.gpkg`.

## Complete example

Mean, min, max elevation per commune from ESRI ASCII DEM tiles without a `.prj`,
after confirming from their metadata that their source CRS is EPSG:2154:

```bash
gdalbuildvrt -a_srs EPSG:2154 mnt.vrt dalles/*.asc
ogr2ogr -t_srs EPSG:2154 communes_l93.gpkg communes.geojson
gdal raster zonal-stats \
  --stat mean --stat min --stat max --stat count \
  --zones communes_l93.gpkg --include-field code_insee --include-field nom_officiel \
  -f CSV mnt.vrt stats_par_commune.csv
```

## Additional resources

- [GDAL zonal-stats documentation](https://gdal.org/en/stable/programs/gdal_raster_zonal_stats.html)
