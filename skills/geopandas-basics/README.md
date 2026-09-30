# geopandas-basics

Process vector data in Python with [GeoPandas](https://geopandas.org/): read and write
GeoPackage, GeoParquet and Shapefile, reproject, spatial joins, overlay, clip, buffer,
dissolve, and zonal statistics with rasterstats.

The CLI counterparts: [geopf-wfs-download](../geopf-wfs-download/README.md) (WFS download),
[gdal-raster-basics](../gdal-raster-basics/README.md) (rasters, including CLI zonal
statistics) and [crs-reprojection-france](../crs-reprojection-france/README.md) (choosing
a CRS).

## Requirements

Python with `geopandas` ≥ 1.0; `pyarrow` for GeoParquet and `rasterstats` for zonal
statistics (`pip install geopandas pyarrow rasterstats`, or
`conda install -c conda-forge geopandas pyarrow rasterstats`).

## Installation

```bash
npx skills add ignfab/geoskills --skill geopandas-basics
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Read/write, reproject, WFS reading, spatial join — the core workflow. |
| [references/io-and-crs.md](references/io-and-crs.md) | Formats, GeoParquet, WFS and remote reads, `set_crs` vs `to_crs`. |
| [references/spatial-operations.md](references/spatial-operations.md) | sjoin, sjoin_nearest, overlay, clip, buffer, dissolve, explode. |
| [references/zonal-stats.md](references/zonal-stats.md) | Raster statistics per polygon with rasterstats. |

## Example

```python
import geopandas as gpd

communes = gpd.read_file("communes.gpkg").to_crs(2154)
points = gpd.read_file("adresses.gpkg").to_crs(2154)
joined = gpd.sjoin(points, communes[["code_insee", "geometry"]], predicate="within")
joined.to_parquet("adresses_communes.parquet")
```
