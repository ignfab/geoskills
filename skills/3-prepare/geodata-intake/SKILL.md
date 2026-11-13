---
name: geodata-intake
description: Inspects unfamiliar local geospatial files or a mixed delivery to inventory formats, layers, CRSs, fields, extents and missing metadata before choosing a workflow. Use when the user asks what received GIS files contain or whether they are ready to use. For an already specified conversion, reprojection or geometry repair, use gdal-vector-processing, gdal-raster-processing, crs-reprojection-france or vector-data-quality directly.
---

# Inspect a geospatial delivery

Produce an inventory and a justified next step without changing the source. Start with
the files the user supplied; do not recursively scan unrelated directories. Group
Shapefile sidecars as one dataset. List archive members before extracting selected data
into a separate directory; reject absolute paths and `..` traversal.

## MCP servers

Optional. When the delivery is a PostGIS database, or the user asks what a database
contains, and a PostGIS MCP server is connected (a server giving SQL access to that
database; its name or tools mention `postgis`, `postgres` or `sql`, and tool names differ
between servers, so read the tool list), inventory it through that server first: list the
schemas and tables, then read `geometry_columns` for geometry types and SRIDs, the column
types, and the row counts where an exact count is cheap; otherwise give the estimate of
`pg_class.reltuples` and label it as an estimate (`-1` or `0` there, as for a view or a
table never analyzed, means unknown, not empty). Run read-only queries: `SELECT` without
`INTO`, and no function that changes data, schema or SRID. Aggregate in the database and
bound exploratory queries with `LIMIT`. In `geometry_columns`, SRID 0 or type `GEOMETRY`
only means that the column declares none, as in a view: read `ST_SRID` and `GeometryType`
from the rows. An SRID of 0 on the rows is an unknown CRS: report it, never set one. For
files, use the commands below. Without such a server, or when a query fails, ask the user
for an export and inventory it with the commands below; never ask for database
credentials, and never take them from a configuration file or the environment to connect
another way. Never install, configure or start an MCP server yourself.

## Prerequisites

Check `ogrinfo --version` for vectors, `gdalinfo --version` for rasters, and Python 3 for
the CSV/JSON recipes. A CSV-only inventory uses Python's standard library without GDAL.
If unavailable, give the user `sudo apt install gdal-bin` or `sudo apt install python3`
(Debian/Ubuntu); Conda equivalents are `libgdal-core` and `python`, only as needed in
the chosen environment. No GeoPandas, QGIS or GDAL Python bindings are required.
**Never install software yourself.**
Do not launch interactive setup or login commands.

## Inspect metadata first

List vector layers, schemas and declared CRSs without fetching all features:

```bash
ogrinfo -ro -so -al -nocount -noextent input.gpkg
```

Read raster metadata without generating statistics sidecars:

```bash
gdalinfo --config GDAL_PAM_ENABLED NO -json input.tif > raster-info.json
```

For a small selected vector layer, obtain counts and extent with
`ogrinfo -ro -so input.gpkg layer_name`, replacing the layer name from discovery.
Some formats must scan the data for these values; report unknown values when a full scan
is disproportionate. Do not fetch remote VRT sources or database connections merely to
inventory local files without checking their location and the requested scope.

## Decide the next operation

- Missing or uncertain CRS: keep it unknown; investigate producer metadata before assigning
  one. Coordinate ranges alone do not establish an EPSG code.
- Vector repair/coverage audit: use `vector-data-quality` if available.
- Confirmed reprojection: use `crs-reprojection-france` for French CRSs if available.
- Raster processing: use `gdal-raster-processing`; vector conversion, encoding or clipping on
  the command line: `gdal-vector-processing`; vector joins/overlay: `geopandas-vector-analysis`.
- Known online service task: use its specialized skill directly. Do not install skills.

Read [inspection details](references/inspection.md) for CSVs, sidecars and large inputs.

## Validate the output

Reconcile the inventory with supplied files, including unreadable/empty datasets. Record
layer names, schema, CRS or unknown, extent, count/dimensions and file size where obtained.
Flag implausible coordinate magnitudes or empty layers without guessing a repair. Confirm
source files and sidecars are unchanged. A metadata inventory is not a geometry audit.

## Report the result

Return a table of datasets, evidence and missing metadata, followed by the next operation.
State which checks ran and which require further inspection; do not invent source dates.

## References

- [Inspection details](references/inspection.md) — CSVs, archives, sidecars and cost.
