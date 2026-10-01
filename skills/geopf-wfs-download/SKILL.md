---
name: geopf-wfs-download
description: Downloads WFS data from the French Géoplateforme (data.geopf.fr) to various formats using ogr2ogr. Use when the user wants to download or export GPF/IGN WFS layers (BD TOPO, ADMIN EXPRESS, cadastre) to GeoJSON, GeoPackage, Shapefile, GeoParquet, GML or another vector format from https://data.geopf.fr/wfs/ows.
---

# Géoplateforme WFS download (ogr2ogr)

Download WFS layers from the French Géoplateforme (data.geopf.fr) and convert them to
vector formats using **ogr2ogr**.

To process the downloaded layers in Python (joins, buffers, overlays), see the
`geopandas-basics` skill.

## Prerequisites

- **GDAL** with WFS support (`ogr2ogr` available).
- Check WFS support: `ogr2ogr --formats | grep -i WFS`.

Install: `sudo apt install gdal-bin` (Ubuntu/Debian) or `conda install -c conda-forge gdal`.
If a tool is missing, give the user the install command and let them run it; do not
install software yourself.

## WFS endpoint

- **Géoplateforme WFS**: `https://data.geopf.fr/wfs/ows` (WFS 2.0).
- GetCapabilities: `https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities`
- Layer names include a namespace prefix, e.g. `BDTOPO_V3:batiment`, `ADMINEXPRESS-COG.LATEST:region`.
- Discover layers with the MCP tool `gpf_wfs_search_types` from
  [@ignfab/geocontext](https://github.com/ignfab/demo-geocontext), or by opening
  GetCapabilities in a browser.

## Discover before querying

Do not guess layer or field names: they change between editions (`ADMINEXPRESS-COG.2025`
became `ADMINEXPRESS-COG.LATEST`), and a wrong field name in `-where` fails or returns
nothing. Read them from the service first:

```bash
# Layer names matching a theme (a few seconds; listing every layer with ogrinfo takes minutes)
curl -fsS "https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities" \
  | grep -o "<Name>[^<]*ADMINEXPRESS-COG.LATEST[^<]*</Name>"
# Fields, geometry type and CRS of one layer
ogrinfo -so -nocount -noextent "WFS:https://data.geopf.fr/wfs/ows" "ADMINEXPRESS-COG.LATEST:commune"
```

For a named area (commune, department), take its boundary from ADMIN EXPRESS instead of
typing a bounding box from memory: see *Selecting features inside a named area* in
[references/ogr2ogr-options.md](references/ogr2ogr-options.md).

## Basic syntax

```bash
ogr2ogr -f <FORMAT> <output_file> "WFS:https://data.geopf.fr/wfs/ows" <typename>
```

Download a small Toulouse extract to GeoPackage, the recommended default format:

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GPKG batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

**Bound nationwide layers** such as `BDTOPO_V3:batiment` to the requested area. A full
download is several gigabytes. Add `-limit` only for a sample; it can truncate an extract
and must not be presented as a complete dataset:

```bash
ogr2ogr -f GeoJSON -lco RFC7946=YES -limit 5000 \
  -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  batiments_extract.geojson \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Validate the output

Before reporting a download as complete:

- Run `ogrinfo -so <output> <layer>`: the feature count must be non-zero, the CRS the one
  expected, and the extent must cover the requested area.
- Compare with an order of magnitude you know. For polygons, compute the total area in
  Lambert-93 (see *Selecting features inside a named area* in the options reference).
- Say explicitly when the result is a sample (`-limit`) or when pages failed.
- Run long downloads in the foreground, with `-progress`. Do not pipe `ogr2ogr` through
  `head` or `tail`, which hides progress and can cut the output.

## References

- [references/formats.md](references/formats.md) — output formats, `-f` driver names and
  one example per format (GeoJSON, GPKG, Shapefile, GeoParquet, GML).
- [references/ogr2ogr-options.md](references/ogr2ogr-options.md) — filtering, reprojection,
  field selection, performance and troubleshooting.

## Additional resources

- GDAL WFS driver: <https://gdal.org/drivers/vector/wfs.html>
- ogr2ogr: <https://gdal.org/programs/ogr2ogr.html>
- Géoplateforme diffusion: <https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/>
