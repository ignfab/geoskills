# geopandas-vector-analysis

**Family:** [4. Analyze and derive](../README.md).

Process vector data in Python with [GeoPandas](https://geopandas.org/): read and write
GeoPackage, GeoParquet and Shapefile, reproject, spatial joins, overlay, clip, buffer,
dissolve, and zonal statistics with rasterstats.

The CLI counterparts: [geopf-wfs-download](../../2-access/geopf-wfs-download/README.md) (WFS download),
[gdal-raster-processing](../../3-prepare/gdal-raster-processing/README.md) (rasters, including CLI zonal
statistics) and [crs-reprojection-france](../../3-prepare/crs-reprojection-france/README.md) (choosing
a CRS).

## Requirements

Reuse an existing Python environment with GeoPandas ≥ 1.0, Pyogrio and pyproj for vector
I/O, reprojection, joins, overlay and buffers. If absent, the user can run
`python3 -m pip install 'geopandas>=1.0,<2'`.

Add `pyarrow` only for GeoParquet (`python3 -m pip install pyarrow`), or `rasterstats`
only for raster zonal statistics (`python3 -m pip install rasterstats`). Neither is a
prerequisite for ordinary vector processing; plotting libraries are also optional.

For Conda users, `conda install -c conda-forge 'geopandas-base>=1.0,<2' pyogrio pyproj`
provides the vector route without the plotting extras of the Conda `geopandas` package.
Choose the command matching the existing environment; do not run both Pip and Conda
recipes. The agent never installs software itself. See the
[dependency guide](../../../docs/dependencies.md) for shared environments and package sources.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopandas-vector-analysis
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
