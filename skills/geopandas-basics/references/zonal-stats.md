# Zonal statistics (rasterstats)

Compute raster statistics (elevation, temperature, …) per polygon from Python, with
**rasterstats**. For the CLI equivalent, see the `gdal-raster-basics` skill
(`gdal raster zonal-stats`, GDAL ≥ 3.12).

## Basic usage

```python
import geopandas as gpd
from rasterstats import zonal_stats

communes = gpd.read_file("communes.geojson").to_crs(2154)   # match the raster CRS
stats = zonal_stats(communes, "mnt_l93.tif",
                    stats=["mean", "min", "max", "count"])
# [{'mean': 50.15, 'min': 39.3, 'max': 54.08, 'count': 9046}, ...]
```

`zonal_stats` returns one dict per polygon, in order — attach them as columns:

```python
import pandas as pd
communes = communes.join(pd.DataFrame(stats, index=communes.index))
```

Use the same index when attaching results: a filtered GeoDataFrame may have a non-default
index, while a new DataFrame otherwise starts at 0 and silently joins the wrong rows.

Available statistics: `count`, `min`, `max`, `mean`, `median`, `sum`, `std`, `majority`,
`minority`, `unique`, `range`, `nodata`, `percentile_<q>` (e.g. `percentile_90`).

## Options

```python
stats = zonal_stats(
    communes, "mnt_l93.tif",
    stats=["mean"],
    all_touched=True,        # include every touched pixel, not only centre-inside
    nodata=-9999,            # override when the raster does not declare its nodata
    band=1,
)
```

## Pitfalls

The same two as the CLI:

- **CRS mismatch** — rasterstats does not reproject the polygons. `to_crs` them to the
  raster CRS first, otherwise the statistics are empty or wrong.
- **Undeclared nodata** — sentinel values (e.g. `-9999`) poison `mean` and `min` unless the
  raster declares them or you pass `nodata=`.

## Categorical rasters

Count pixels per class (land cover, classifications):

```python
stats = zonal_stats(zones, "occupation_sol.tif", categorical=True)
# [{1: 3200, 2: 5100, 3: 746}, ...]   # class -> pixel count
```

## Point queries

Sample a raster at point locations:

```python
from rasterstats import point_query
altitudes = point_query(points_l93, "mnt_l93.tif")
```
