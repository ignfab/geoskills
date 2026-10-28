---
name: geodata-intake
description: Inspects unfamiliar local geospatial files or a mixed delivery to inventory formats, layers, CRSs, fields, extents and missing metadata before choosing a workflow. Use when the user asks what received GIS files contain or whether they are ready to use. For an already specified conversion, reprojection or geometry repair, use the corresponding specialized skill directly.
---

# Inspect a geospatial delivery

Produce an inventory and a justified next step without changing the source. Start with
the files the user supplied; do not recursively scan unrelated directories. Group
Shapefile sidecars as one dataset. List archive members before extracting selected data
into a separate directory; reject absolute paths and `..` traversal.

## Prerequisites

Check `ogrinfo --version`, `gdalinfo --version` and `python3 --version`. If unavailable,
give the user `sudo apt install gdal-bin python3` (Debian/Ubuntu) or
`conda install -c conda-forge gdal python` to run. **Never install software yourself.**
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
- Raster processing: use `gdal-raster-basics`; vector joins/overlay: `geopandas-basics`.
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
