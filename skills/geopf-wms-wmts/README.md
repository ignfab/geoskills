# geopf-wms-wmts

Download raster layers — orthophotos, Plan IGN, elevation — from the French
[Géoplateforme](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/)
(`data.geopf.fr`) WMTS and WMS-R services and convert them to GeoTIFF or another raster
format using `gdalwarp` / `gdal_translate`.

For **vector** layers, see the sibling [`geopf-wfs-download`](../geopf-wfs-download/README.md)
skill. To process the downloaded rasters (clip, mosaic, COG), see
[`gdal-raster-basics`](../gdal-raster-basics/README.md).

## Requirements

GDAL with the WMTS and WMS drivers (`sudo apt install gdal-bin`, or
`conda install -c conda-forge gdal`).

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-wms-wmts
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Endpoints, WMTS/WMS choice and the main extraction commands. |
| [references/wmts.md](references/wmts.md) | GDAL WMTS driver: connection string, zoom/resolution, tile matrix sets. |
| [references/wms.md](references/wms.md) | GDAL WMS driver: subdatasets, `GDAL_WMS` XML, CRS/format, elevation. |

## Example

```bash
gdalwarp -te 1.43 43.59 1.45 43.61 -te_srs EPSG:4326 \
  -t_srs EPSG:2154 -tr 0.5 0.5 -of GTiff -co COMPRESS=DEFLATE \
  "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS" \
  ortho_toulouse.tif
```
