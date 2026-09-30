---
name: geopf-wms-wmts
description: Downloads raster data (orthophotos, Plan IGN, elevation) from the French Géoplateforme (data.geopf.fr) WMTS and WMS-R services to GeoTIFF or another raster format using GDAL. Use when the user wants to download or export GPF/IGN raster layers, orthophotos, tiles, Plan IGN maps or elevation data (DEM) from https://data.geopf.fr/wmts or https://data.geopf.fr/wms-r/wms.
---

# Géoplateforme WMS / WMTS download (GDAL)

Download raster layers — orthophotos, Plan IGN, elevation — from the French Géoplateforme
(data.geopf.fr) and convert them to GeoTIFF (or another raster format) with **GDAL**.

For **vector** layers (BD TOPO, ADMIN EXPRESS, cadastre…), use the `geopf-wfs-download`
skill instead. To process a downloaded raster (clip, mosaic, resample, COG) see
`gdal-raster-basics`; for coordinate-system choices see `crs-reprojection-france`.

## Prerequisites

- **GDAL** with the WMTS and WMS drivers (`gdalinfo`, `gdal_translate`, `gdalwarp`).
- Check driver support: `gdalinfo --formats | grep -iE "WMTS|WMS"`.

Install: `sudo apt install gdal-bin` (Ubuntu/Debian) or `conda install -c conda-forge gdal`.
If a tool is missing, give the user the install command and let them run it; do not
install software yourself.

## Endpoints

- **WMTS** (pre-rendered tile pyramid, cached, fastest): `https://data.geopf.fr/wmts`.
  GDAL needs the full GetCapabilities URL: `WMTS:https://data.geopf.fr/wmts` alone fails
  with HTTP 400.
- **WMS-R** (raster WMS, arbitrary CRS / extent / size): `https://data.geopf.fr/wms-r/wms`
- Capabilities:
  - `https://data.geopf.fr/wmts?SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetCapabilities`
  - `https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities`

**WMTS or WMS?** Prefer **WMTS** for pyramided layers (ortho, Plan IGN) in Web Mercator
(EPSG:3857) — it is tiled and cached. Use **WMS-R** when you need a specific source CRS
(e.g. Lambert-93 EPSG:2154), an exact pixel size, a server-side GeoTIFF, or elevation
values (32-bit float GeoTIFF).

## Basic syntax

List the available layers (each shown as a GDAL subdataset):

```bash
gdalinfo "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities"
```

**Always restrict the extent** — a full-resolution nationwide raster is terabytes. Bounded
orthophoto extract via WMTS, reprojected to Lambert-93 (EPSG:2154) at 0.5 m, as GeoTIFF:

```bash
gdalwarp \
  -te 1.43 43.59 1.45 43.61 -te_srs EPSG:4326 \
  -t_srs EPSG:2154 -tr 0.5 0.5 \
  -of GTiff -co COMPRESS=DEFLATE \
  "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS" \
  ortho_toulouse.tif
```

For a specific source CRS, an exact size, or elevation values as a GeoTIFF, use **WMS-R**
(see [references/wms.md](references/wms.md)).

## Common layers

| Layer identifier | Content | Typical format |
|------------------|---------|----------------|
| `ORTHOIMAGERY.ORTHOPHOTOS` | Aerial orthophotos | JPEG (WMTS) / GeoTIFF (WMS) |
| `GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2` | Plan IGN (base map) | PNG |
| `ELEVATION.ELEVATIONGRIDCOVERAGE` | Elevation, national coverage | GeoTIFF Float32 (WMS-R) |
| `ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES` | Elevation, high resolution (RGE ALTI) | GeoTIFF Float32 (WMS-R) |
| `CADASTRALPARCELS.PARCELLAIRE_EXPRESS` | Cadastral parcels overlay | PNG |

Discover more layer identifiers with the `gdalinfo` listing above, or in the WMTS / WMS
capabilities (`REQUEST=GetCapabilities`). Check that a layer is listed there before using
it, and never invent an identifier: for example, no SCAN 25 layer is exposed by these
public services.

## Validate the output

- A non-zero exit code means the download failed.
- Run `gdalinfo -stats <output>`: check the CRS, pixel size and size you asked for, and
  statistics that are not all 0 or nodata. After a transient HTTP error (502, 400) from
  the tile server, GDAL can still write a file with empty blocks. Rerun the command: the
  tiles already fetched come from GDAL's local cache. Do not add those codes to
  `<ZeroBlockHttpCodes>`, which would hide the error.
- For elevation, check that the values are plausible: about −10 to 4,810 m in mainland
  France, with `-99999` as nodata.
- Do not pipe `gdalwarp` or `gdal_translate` through `head` or `tail`.

## References

- [references/wmts.md](references/wmts.md) — GDAL WMTS driver: connection string, zoom /
  resolution control, tile matrix sets, per-layer extraction.
- [references/wms.md](references/wms.md) — GDAL WMS driver: subdatasets, `<GDAL_WMS>` XML
  service description, CRS / format selection, elevation download.

## Additional resources

- GDAL WMTS driver: <https://gdal.org/drivers/raster/wmts.html>
- GDAL WMS driver: <https://gdal.org/drivers/raster/wms.html>
- Géoplateforme diffusion: <https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/>
