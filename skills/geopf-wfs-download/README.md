# geopf-wfs-download

Download WFS layers from the French
[Géoplateforme](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/)
(`data.geopf.fr`) and convert them to GeoPackage, GeoJSON, GeoParquet, Shapefile or GML
using `ogr2ogr`.

## Requirements

Working GDAL CLI tools with WFS read support **and a driver that can create the requested
output format**. Check `ogr2ogr --version`, `ogrinfo --format WFS` and
`ogrinfo --format <output-driver>` before downloading.

The user can install distribution GDAL with `sudo apt install gdal-bin`, or Conda GDAL
with `conda install -c conda-forge gdal`. GeoParquet may need the additional plugin:
`conda install -c conda-forge gdal libgdal-arrow-parquet`. Distribution builds do not
necessarily include it. An official GDAL `ubuntu-full` container is another option; see
[missing-driver options](references/formats.md#missing-gdal-or-parquet-support).

The agent uses `ogr2ogr`, never installs software itself and asks for an environment
choice when a capability is missing. It does not silently switch to Python or another
format. GeoParquet exports use one file per layer.

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

## Example

```bash
ogr2ogr -f GPKG -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  batiments_toulouse.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```
