# crs-reprojection-france

**Family:** [3. Prepare and check](../README.md).

Choose the right coordinate reference system for French data (Lambert-93, CC zones, NTF,
the overseas UTM systems) and reproject vectors, rasters and points with GDAL, PROJ and
pyproj, without the usual pitfalls.

Preserve suitable requested/existing CRSs. Lambert-93 is a fallback for applicable
metropolitan-France tasks; other authority codes and custom WKT definitions remain valid.
This guide's French scope does not restrict the generic tools; see
[CRS handling](../../../docs/crs-handling.md).

## Requirements

Choose an existing route: GDAL for vector/raster files (`sudo apt install gdal-bin`),
PROJ for CLI coordinate operations (`sudo apt install proj-bin`), or pyproj for Python
points (`python3 -m pip install pyproj`). These user-run commands are alternatives by
task; metadata inspection may also use `projinfo`. The agent never installs software.

Accurate datum/altitude transformations may need grids: inspect the selected operation,
then download only its missing grid files, not the entire IGN collection or `proj-data`.
See [targeted downloads](references/pitfalls.md#3-ntf--rgf93-legacy-lambert-i-ii-iii-iv).

## Installation

```bash
npx skills add ignfab/geoskills --skill crs-reprojection-france
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | EPSG codes for France, reprojection commands, sanity checks. |
| [references/pitfalls.md](references/pitfalls.md) | Axis order, assign versus reproject, NTF grids, RGF93 v2b, altitudes, Web Mercator. |
| [references/overseas.md](references/overseas.md) | Systems for each overseas territory. |

## Example

```bash
echo "2.3522 48.8566" | gdaltransform -s_srs EPSG:4326 -t_srs EPSG:2154
# 652469.02 6862035.26
```
