# geopf-raster-download

**Family:** [2. Access and extract](../README.md).

Download raster layers — orthophotos, Plan IGN, elevation — from the French
[Géoplateforme](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/)
(`data.geopf.fr`) WMTS and WMS-R services and convert them to GeoTIFF or another raster
format using `gdalwarp` / `gdal_translate`. Extracts are always bounded to the requested
area, and layer identifiers come from the service capabilities.

## When to use it

- Extract an orthophoto around a site to a compressed Lambert-93 GeoTIFF at a chosen
  resolution (for example 50 cm).
- Download high-resolution elevation values (RGE ALTI) over the extent of a local file as
  a Float32 GeoTIFF, not a colored rendering.
- Make a Plan IGN image of a bounding box in Web Mercator (EPSG:3857).
- List the orthophoto layers currently advertised by the WMTS.
- Check whether a named product (for example SCAN 25) is actually served before
  downloading it.

WMTS (pre-rendered, cached tiles) is preferred for pyramided layers in Web Mercator. WMS-R
is used for a specific source CRS such as Lambert-93, an exact pixel size, a server-side
GeoTIFF, or elevation values.

## When to use another skill

- Vector layers (BD TOPO, ADMIN EXPRESS, cadastre), rather than a rendered image of them:
  [`geopf-wfs-download`](../geopf-wfs-download/README.md).

## What you get

- A raster file, usually GeoTIFF, restricted to the requested extent (a full-resolution
  nationwide raster would be terabytes). An orthophoto has 3 bands from WMS-R or 4 bands
  (RGB + alpha) from WMTS; elevation is Float32 with `-99999` as nodata.
- Before reporting, the agent treats a non-zero exit code as a failed download and runs
  `gdalinfo -stats` on the output: CRS, pixel size and size must match the request, and
  statistics must not be all 0 or nodata. For elevation, values must be plausible (about
  −10 to 4,810 m in mainland France).
- GDAL can leave a partial file after an HTTP error, so non-empty statistics alone do not
  prove that every tile was fetched. Transient 429/502/503/504 errors are retried at most
  twice, respecting `Retry-After`; a repeated HTTP 400 is investigated as a request error.
  These codes are never added to `<ZeroBlockHttpCodes>`, which would hide failures, and an
  incomplete download is reported as such.
- The agent never invents a layer identifier: it checks that a layer is listed in the
  capabilities and, when a requested product is not advertised, reports the limitation
  instead of writing an empty or unrelated image.

## Requirements

- GDAL with the WMTS and WMS drivers (`gdalinfo`, `gdal_translate`, `gdalwarp`). Check
  driver support with `gdalinfo --formats | grep -iE "WMTS|WMS"`.
- The user can install GDAL with `sudo apt install gdal-bin` (Debian/Ubuntu), or
  `conda install -c conda-forge libgdal-core`. The agent never installs software itself.
- Network: the public Géoplateforme WMTS (`https://data.geopf.fr/wmts`) and WMS-R
  (`https://data.geopf.fr/wms-r/wms`) services; the documented requests carry no API key. GDAL needs the full
  WMTS GetCapabilities URL: `WMTS:https://data.geopf.fr/wmts` alone fails with HTTP 400.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-raster-download
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`.

## Example

> Download the orthophoto over 500 m × 500 m around the Capitole in Toulouse, at 50 cm, as
> a Lambert-93 GeoTIFF, to output/ortho_capitole.tif.

The same command shape on a wider box in central Toulouse:

```bash
gdalwarp -te 1.43 43.59 1.45 43.61 -te_srs EPSG:4326 \
  -t_srs EPSG:2154 -tr 0.5 0.5 -of GTiff -co COMPRESS=DEFLATE \
  "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS" \
  ortho_toulouse.tif
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Endpoints, WMTS/WMS choice and the main extraction commands. |
| [references/wmts.md](references/wmts.md) | GDAL WMTS driver: connection string, zoom/resolution, tile matrix sets. |
| [references/wms.md](references/wms.md) | GDAL WMS driver: subdatasets, `GDAL_WMS` XML, CRS/format, elevation. |

## Tests

- Agent scenarios: [tests/geopf-raster-download.md](../../../tests/geopf-raster-download.md) (French
  prompts, 5 positive + 1 negative).
- No offline test: the skill's value is advice and remote requests. Live (opt-in):
  [test_live.py](../../../tests/test_live.py) (WMTS, WMS-R).

## Related skills

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) chooses the access route
  and covers the display services (WMS, WMTS, vector tiles) that show data without
  downloading it.
- [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md) processes the
  downloaded raster (clip, mosaic, resample, COG).
- [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md) helps
  choose the coordinate system (Lambert-93, CC zones, overseas territories).
- [`qgis-project-builder`](../../5-publish/qgis-project-builder/README.md) can add a
  Géoplateforme basemap to a QGIS project; this skill helps discover the advertised layer.
- [`terrain-elevation-screening`](../../6-workflows/terrain-elevation-screening/README.md)
  can use a verified numeric elevation extract from this skill as its DEM.
