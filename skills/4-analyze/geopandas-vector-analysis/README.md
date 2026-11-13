# geopandas-vector-analysis

**Family:** [4. Analyze and derive](../README.md).

Process vector data in Python with [GeoPandas](https://geopandas.org/): read and write
GeoPackage, GeoParquet and Shapefile, reproject, spatial joins, overlay, clip, buffer,
dissolve, and zonal statistics with rasterstats. It also reads bounded Géoplateforme WFS
requests directly into a GeoDataFrame. Use it when the workflow is scripted, iterative or
mixes analysis steps; for one-shot conversions and downloads the CLI is often enough.

## When to use it

- Find which points of a CSV fall inside a municipality with a spatial join (`sjoin`).
- Read a Shapefile without a CRS, assign the confirmed CRS with `set_crs`, then reproject
  with `to_crs` to get longitude/latitude.
- Compute the mean, minimum and maximum elevation of a polygon from DEM tiles with
  rasterstats, and attach the results to the right polygons even when the index is
  filtered or repeated.
- Build buffers, overlays (intersection, difference, union), clips and dissolves in a
  projected CRS.
- Convert vector formats in a script, or read a small Géoplateforme WFS extract into Python.

## When to use another skill

- One-shot download of a WFS layer to a file, without Python processing, or a repeated or
  very large extraction: [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md).
- Raster processing on the command line, including zonal statistics with
  `gdal raster zonal-stats` (GDAL ≥ 3.12): [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md).
- Choosing a French CRS: [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md).
- Invalid geometries, duplicates and schema audits: [`vector-data-quality`](../../3-prepare/vector-data-quality/README.md).

## What you get

- A new output file (GeoPackage recommended, or GeoParquet, Shapefile, RFC 7946 GeoJSON),
  reopened and checked for a non-zero count, CRS, bounds, geometry types and required
  fields. An empty result is investigated, not reported as a successful analysis.
- For spatial joins: unmatched features and multiple matches per source feature are
  reported, and a source identifier is preserved before joining (a left join can add rows).
- Areas, buffers and distances computed in a suitable projected CRS with explicit unit
  conversions, with magnitudes compared with the source. Preserve a suitable requested or
  existing CRS; EPSG:2154 is a fallback for applicable mainland-France tasks.
- For zonal statistics: valid pixel counts and plausible values checked, results attached
  by position so repeated indices cannot multiply rows.
- A report of source and edition/access date when known, output path and format, CRS and
  units, extent and counts, processing choices and checks, with failed checks, warnings
  and checks not performed kept separate.
- The skill does not present a single bounded WFS response (`COUNT`) or a `max_features`
  read as a complete dataset, and does not assign a missing CRS without confirming it from
  metadata or a known control point.

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

Network: the Géoplateforme WFS (`https://data.geopf.fr/wfs/ows`) only when reading WFS data directly. Local files need no network.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopandas-vector-analysis
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/4-analyze`.

## Example

> With Python, find which of the points in data/points.csv are in the municipality of
> Saint-Mandé (data/saint_mande.geojson).

```python
import geopandas as gpd

communes = gpd.read_file("communes.gpkg")  # inspect its declared CRS before joining
points = gpd.read_file("adresses.gpkg").to_crs(communes.crs)
joined = gpd.sjoin(points, communes[["code_insee", "geometry"]], predicate="within")
joined.to_parquet("adresses_communes.parquet")
```

The join preserves the zone CRS; it does not require Lambert-93. Measurements use a
suitable analysis CRS with explicit unit conversions. Zonal statistics align vectors to
the raster's actual CRS. See [CRS handling](../../../docs/crs-handling.md).

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Read/write, reproject, WFS reading, spatial join — the core workflow. |
| [references/io-and-crs.md](references/io-and-crs.md) | Formats, GeoParquet, WFS and remote reads, `set_crs` vs `to_crs`. |
| [references/spatial-operations.md](references/spatial-operations.md) | sjoin, sjoin_nearest, overlay, clip, buffer, dissolve, explode. |
| [references/zonal-stats.md](references/zonal-stats.md) | Raster statistics per polygon with rasterstats. |

## Tests

- [French agent scenarios](../../../tests/geopandas-vector-analysis.md): 4 positive + 1 negative.
- Offline: [test_geopandas.py](../../../tests/test_geopandas.py) (spatial joins, nearest
  joins and buffers, overlay areas, CRS and format round trips, zonal statistics with
  filtered or repeated indices). No live test.

## Related skills

- [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md) builds a VRT of DEM
  tiles with an assigned CRS before rasterstats computes zonal statistics.
- [`spatial-aggregation`](../spatial-aggregation/README.md) turns object-to-zone joins into
  audited per-zone counts, sums, means and ratios, keeping empty zones.
- [`geospatial-descriptive-statistics`](../geospatial-descriptive-statistics/README.md)
  summarizes the attributes of one layer without spatial matching.
- [`geopf-routing`](../geopf-routing/README.md) produces isochrones that GeoPandas can
  overlay with an area of interest.
