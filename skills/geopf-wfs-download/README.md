# geopf-wfs-download

Download WFS layers from the French
[Géoplateforme](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/)
(`data.geopf.fr`) and convert them to GeoPackage, GeoJSON, GeoParquet, Shapefile or GML
using `ogr2ogr`.

## Requirements

GDAL with WFS support (`sudo apt install gdal-bin`, or `conda install -c conda-forge gdal`).

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-wfs-download
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Endpoint, basic syntax and the two commands covering most needs. |
| [references/formats.md](references/formats.md) | Output formats and one example per format. |
| [references/ogr2ogr-options.md](references/ogr2ogr-options.md) | Filtering, reprojection, performance, troubleshooting. |

## Example

```bash
ogr2ogr -f GPKG -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  batiments_toulouse.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```
