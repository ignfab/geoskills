---
name: wfs-geopf-download
description: Downloads WFS data from the French Géoplateforme (data.geopf.fr) to various formats using ogr2ogr. Use when the user wants to export or télécharger GPF/IGN WFS layers (couches) to GeoJSON, GeoPackage, Shapefile, GeoParquet, GML or another vector format from https://data.geopf.fr/wfs.
---

# WFS Géoplateforme download (ogr2ogr)

Download WFS layers from the French Géoplateforme (data.geopf.fr) and convert them to
vector formats using **ogr2ogr**.

## Prerequisites

- **GDAL** with WFS support (`ogr2ogr` available).
- Check WFS support: `ogr2ogr --formats | grep -i WFS`.

Install: `sudo apt install gdal-bin` (Ubuntu/Debian) or `conda install -c conda-forge gdal`.

## WFS endpoint

- **Géoplateforme WFS**: `https://data.geopf.fr/wfs/ows` (WFS 2.0).
- GetCapabilities: `https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities`
- Layer names include a namespace prefix, e.g. `BDTOPO_V3:batiment`, `ADMINEXPRESS-COG.2020:region`.
- Discover layers with the MCP tool `gpf_wfs_search_types` from
  [@ignfab/geocontext](https://github.com/ignfab/demo-geocontext), or by opening
  GetCapabilities in a browser.

## Basic syntax

```bash
ogr2ogr -f <FORMAT> <output_file> "WFS:https://data.geopf.fr/wfs/ows" <typename>
```

Download a layer to GeoPackage, the recommended default format:

```bash
ogr2ogr -f GPKG batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

**Always restrict the extent or the number of features** on a nationwide layer such as
`BDTOPO_V3:batiment` — a full download is several gigabytes:

```bash
ogr2ogr -f GeoJSON -limit 5000 \
  -spat 1.4 43.5 1.6 43.7 \
  batiments_extract.geojson \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## References

- [references/formats.md](references/formats.md) — output formats, `-f` driver names and
  one example per format (GeoJSON, GPKG, Shapefile, GeoParquet, GML).
- [references/ogr2ogr-options.md](references/ogr2ogr-options.md) — filtering, reprojection,
  field selection, performance and troubleshooting.

## Additional resources

- GDAL WFS driver: <https://gdal.org/drivers/vector/wfs.html>
- ogr2ogr: <https://gdal.org/programs/ogr2ogr.html>
- Géoplateforme diffusion: <https://geoservices.ign.fr/services-geoplateforme-diffusion>
