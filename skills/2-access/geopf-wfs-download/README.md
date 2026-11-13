# geopf-wfs-download

**Family:** [2. Access and extract](../README.md).

Download WFS layers from the French
[Géoplateforme](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/)
(`data.geopf.fr`) and convert them to GeoPackage, GeoJSON, GeoParquet, Shapefile or GML
using `ogr2ogr`.

## Requirements

Working GDAL CLI tools with WFS read support **and a driver that can create the requested
output format**. Check `ogr2ogr --version`, `ogrinfo --format WFS` and
`ogrinfo --format <output-driver>` before downloading.

The user can install distribution GDAL with `sudo apt install gdal-bin`, or Conda GDAL
with `conda install -c conda-forge libgdal-core` for native CLI tools. Only a requested
GeoParquet export may need the additional plugin:
`conda install -c conda-forge libgdal-arrow-parquet`. Distribution builds do not
necessarily include it. Reuse an existing capable environment first. An official GDAL
`ubuntu-full` container is a larger fallback, not a default dependency; see
[missing-driver options](references/formats.md#missing-gdal-or-parquet-support).

The agent uses `ogr2ogr`, never installs software itself and asks for an environment
choice when a capability is missing. It does not silently switch to Python or another
format. GeoParquet exports use one file per layer.

The discovery/count requests use `curl`. The optional GeoPackage completeness helper
uses Python 3 and its standard library: user-run commands are `sudo apt install curl`
and `sudo apt install python3`, only if the selected route needs them.
This helper audits an export; downloads and conversions
still use `ogr2ogr`.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-wfs-download
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Tool/driver checks, tooling rule, endpoint, download recipes and validation. |
| [references/formats.md](references/formats.md) | Output formats, missing-driver options and GeoParquet layer limits. |
| [references/ogr2ogr-options.md](references/ogr2ogr-options.md) | Filtering, reprojection, performance, troubleshooting. |
| [references/completeness.md](references/completeness.md) | Compare WFS counts before/after export, check source IDs and handle interrupted jobs. |
| [scripts/check_export.py](scripts/check_export.py) | Audit GeoPackage counts and source IDs against saved WFS hits responses. |

## Example

```bash
ogr2ogr -f GPKG -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  batiments_toulouse.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```
