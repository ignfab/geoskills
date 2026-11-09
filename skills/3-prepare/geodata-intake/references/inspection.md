# Inspection details

For Shapefiles, keep `.shp`, `.shx` and `.dbf` together and inspect `.prj`/`.cpg` when
present. A missing `.prj` is missing CRS evidence, even when coordinates look projected.
Do not use `-a_srs` to make the warning disappear. Check source documentation separately.

For a CSV, inspect a small sample with Python's `csv` module, preserving strings and
leading zeros. Confirm delimiter, encoding, duplicate headers, coordinate column names
and units. Latitude/longitude column order is not guaranteed. Row width errors and a
missing coordinate pair should be reported, not silently discarded. A CSV is not spatial
until its coordinate fields and CRS have been established.

For raster files, record dimensions, band data types, geotransform, nodata and embedded
CRS. Defer `-stats` until a bounded scan is justified. A VRT may refer to missing files or
remote URLs; read its source references before opening large derived datasets.

For archives, list members and uncompressed sizes first. Select required files, preserve
sidecar groups, and check available disk space. Do not execute bundled scripts. Use an
existing archive reader; if missing, give the user its install command and stop that step.

Keep an inventory entry for every logical dataset, including errors. Use "not inspected"
for deferred scans and "unknown" for absent metadata. Recommend a targeted next operation
instead of automatically converting, repairing or publishing the entire delivery.
