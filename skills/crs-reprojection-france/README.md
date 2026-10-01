# crs-reprojection-france

Choose the right coordinate reference system for French data (Lambert-93, CC zones, NTF,
the overseas UTM systems) and reproject vectors, rasters and points with GDAL, PROJ and
pyproj, without the usual pitfalls.

## Requirements

GDAL and PROJ (`sudo apt install gdal-bin proj-bin`, or `conda install -c conda-forge gdal`).
Accurate NTF and altitude transformations also need the IGN grids (`projsync --source-id fr_ign`
or `PROJ_NETWORK=ON`).

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
