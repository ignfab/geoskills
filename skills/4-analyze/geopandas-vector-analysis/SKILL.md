---
name: geopandas-vector-analysis
description: "Processes vector data in Python with GeoPandas: read and write GeoPackage, GeoParquet and Shapefile, reproject with to_crs, spatial joins (sjoin), overlay, clip, buffer, dissolve, and zonal statistics with rasterstats. Use when the user wants to join or intersect layers spatially, build buffers, dissolve or clip features, compute zonal statistics in Python, work with a GeoDataFrame, convert vector formats in a script, or read Géoplateforme WFS data directly into Python."
---

# GeoPandas vector analysis

Process vector data in Python with **GeoPandas**: read and write the common formats,
reproject, join and overlay layers, and compute zonal statistics with **rasterstats**.

For one-shot conversions and downloads, the CLI is often enough: see `geopf-wfs-download`
(WFS download), `gdal-raster-processing` (rasters) and `crs-reprojection-france` (choosing a
CRS). For invalid geometries, duplicates and schema audits, use `vector-data-quality`.
Use GeoPandas when the workflow is scripted, iterative or mixes analysis steps.

## MCP servers

Optional. When the layers to join or overlay are tables of a PostGIS database and a
PostGIS MCP server is connected (a server giving SQL access to that database; its name or
tools mention `postgis`, `postgres` or `sql`, and tool names differ between servers, so
read the tool list), run the operation in SQL there first instead of loading the tables in
Python. Read the geometry columns and SRIDs, bring both layers to one projected CRS suited
to the territory with `ST_Transform`, state the predicate used (`ST_Within` leaves points
on a boundary unmatched), and apply the checks of *Validate the output* to the query
result: unmatched features, multiple matches, counts, and areas measured in a projected
CRS. Run read-only queries: `SELECT` without `INTO`, and no function that changes data,
schema or SRID. Aggregate in the database and bound exploratory queries with `LIMIT`.
Report counts and checks, not every joined row: when the user needs the resulting layer
itself, offer a table or ask for an export and use GeoPandas. Create a table only on
request, under a name you checked is unused; never drop, replace, alter or update an
existing table.

For files, WFS extracts and raster zonal statistics, use GeoPandas as described below.
Without such a server, or when a query fails, ask the user for an export and use GeoPandas
on it; never ask for database credentials, and never take them from a configuration file
or the environment to connect another way. Never install, configure or start an MCP server
yourself.

## Prerequisites

Check the existing Python environment and only the operation's dependencies:

| Operation | Required packages | User-run command if missing |
| --- | --- | --- |
| Vector I/O, reprojection, joins, overlay, buffers | GeoPandas ≥ 1.0, with Pyogrio and pyproj | `python3 -m pip install 'geopandas>=1.0,<2'` |
| GeoParquet I/O | Also PyArrow | `python3 -m pip install pyarrow` |
| Raster zonal statistics | Also rasterstats | `python3 -m pip install rasterstats` |

For an existing Conda environment, the vector base is
`conda install -c conda-forge 'geopandas-base>=1.0,<2' pyogrio pyproj`;
add `pyarrow` or `rasterstats` only for their operations. The Conda `geopandas` package
also brings plotting extras. Use one environment and package-manager route, not both.
Never install software or run interactive setup yourself; give the user only the missing
packages. Do not require raster or plotting libraries for vector operations.

## Inspect first

List layers with `gpd.list_layers(path)`, then read the intended layer explicitly. Inspect
`gdf.columns`, `gdf.crs`, `gdf.geom_type` and `gdf.total_bounds` before choosing fields or a
target CRS. Confirm a missing CRS from source metadata before using `set_crs`.
Preserve a suitable existing/requested CRS; EPSG:2154 is only a fallback for suitable
metropolitan-France calculations. Accept custom CRS definitions without an EPSG code.
Use a common CRS for combined layers, the raster's actual CRS for zonal statistics, and
an appropriate projected/geodesic method for measurements. Read units instead of assuming metres.
Discover WFS layer names, fields and CRSs from GetCapabilities and DescribeFeatureType
before adapting the service example below.

## Minimal syntax

```python
import geopandas as gpd

gdf = gpd.read_file("communes.gpkg")          # GPKG, Shapefile, GeoJSON, ...
gdf.to_file("communes_copy.gpkg")             # preserve the declared source CRS
# If requested: gdf = gdf.to_crs(target_crs), selected from metadata and task needs.
# Optional GeoParquet output (requires pyarrow): gdf.to_parquet("communes.parquet")
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

For planar buffers, areas and distances, use a suitable **projected** analysis CRS and
convert its linear/squared units as needed. Geographic degrees are not metric distances.
Attribute operations and local topological joins do not require a Lambert-93 conversion.

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

## Report the result

Report the source and edition/access date when known, output path and format, CRS and
units, extent and counts (or raster dimensions), processing choices and checks performed.
Separate failed checks, warnings and checks not performed; keep unknown metadata explicit.
For advice-only requests, report the recommendation and its evidence without inventing files.

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
