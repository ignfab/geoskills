---
name: geopandas-basics
description: "Processes vector data in Python with GeoPandas: read and write GeoPackage, GeoParquet and Shapefile, reproject with to_crs, spatial joins (sjoin), overlay, clip, buffer, dissolve, and zonal statistics with rasterstats. Use when the user wants to join or intersect layers spatially, build buffers, dissolve or clip features, compute zonal statistics in Python, work with a GeoDataFrame, convert vector formats in a script, or read Géoplateforme WFS data directly into Python."
---

# GeoPandas basics

Process vector data in Python with **GeoPandas**: read and write the common formats,
reproject, join and overlay layers, and compute zonal statistics with **rasterstats**.

For one-shot conversions and downloads, the CLI is often enough: see `geopf-wfs-download`
(WFS download), `gdal-raster-basics` (rasters) and `crs-reprojection-france` (choosing a
CRS). For invalid geometries, duplicates and schema audits, use `vector-data-quality`.
Use GeoPandas when the workflow is scripted, iterative or mixes analysis steps.

## Prerequisites

- **geopandas** ≥ 1.0 (`pyogrio` I/O engine included). For GeoParquet: **pyarrow**.
  For zonal statistics: **rasterstats**.

Install: `pip install geopandas pyarrow rasterstats` or
`conda install -c conda-forge geopandas pyarrow rasterstats`.
If a package is missing, give the user the install command and let them run it; do not
install software or run interactive setup yourself.

## Inspect first

List layers with `gpd.list_layers(path)`, then read the intended layer explicitly. Inspect
`gdf.columns`, `gdf.crs`, `gdf.geom_type` and `gdf.total_bounds` before choosing fields or a
target CRS. Confirm a missing CRS from source metadata before using `set_crs`.
Discover WFS layer names, fields and CRSs from GetCapabilities and DescribeFeatureType
before adapting the service example below.

## Minimal syntax

```python
import geopandas as gpd

gdf = gpd.read_file("communes.gpkg")          # GPKG, Shapefile, GeoJSON, ...
gdf = gdf.to_crs(2154)                        # reproject to Lambert-93
gdf.to_file("communes_l93.gpkg")              # write GPKG
gdf.to_parquet("communes_l93.parquet")        # write GeoParquet
```

Read a Géoplateforme WFS layer directly (always bound the request with `COUNT` or a
`BBOX` — a nationwide layer is gigabytes). `COUNT` returns a limited sample; a single
GetFeature response must not be presented as a complete large extraction:

```python
url = ("https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature"
       "&TYPENAMES=ADMINEXPRESS-COG.LATEST:region&OUTPUTFORMAT=application/json&COUNT=50")
regions = gpd.read_file(url)                  # GeoDataFrame in EPSG:4326
```

Spatial join — which commune contains each point:

```python
communes = gpd.read_file("communes.gpkg")
pts = gpd.read_file("points.gpkg").to_crs(communes.crs)
joined = gpd.sjoin(pts, communes[["code_insee", "geometry"]],
                   predicate="within", how="left")
```

**Always work in a single CRS**, and use a **projected** CRS (EPSG:2154 in mainland
France) for buffers, areas and distances — in EPSG:4326 they come out in degrees and
GeoPandas emits a `Geometry is in a geographic CRS` warning.

## Validate the output

- Write to a new file, reopen it and check the expected non-zero count, CRS, bounds,
  geometry types and required fields. Investigate an empty result rather than treating a
  successful write as a successful analysis.
- For spatial joins, report unmatched features and multiple matches per source feature;
  a left join can increase the row count. Preserve a source identifier before joining.
- Check areas and distances in a projected CRS suitable for the study area and compare
  their magnitude with the source. Use the local projection for overseas territories.
- For zonal statistics, check valid pixel counts and plausible values, and attach results
  by position as shown in the reference so repeated indices cannot multiply rows.

## References

- [references/io-and-crs.md](references/io-and-crs.md) — formats (GPKG, GeoParquet,
  Shapefile), reading WFS and remote files, `set_crs` versus `to_crs`.
- [references/spatial-operations.md](references/spatial-operations.md) — sjoin,
  sjoin_nearest, overlay, clip, buffer, dissolve, explode.
- [references/zonal-stats.md](references/zonal-stats.md) — raster statistics per polygon
  with rasterstats.

## Additional resources

- GeoPandas documentation: <https://geopandas.org/en/stable/docs.html>
- rasterstats: <https://pythonhosted.org/rasterstats/>
- GeoParquet: <https://geoparquet.org/>
