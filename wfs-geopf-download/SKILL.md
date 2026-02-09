---
name: wfs-geopf-download
description: Downloads WFS data from Géoplateforme (data.geopf.fr) to various formats using ogr2ogr. Use when the user wants to export GPF/IGN WFS layers to GeoJSON, GeoPackage, Shapefile, GeoParquet, GML, or other vector formats from http://data.geopf.fr/wfs.
---

# WFS Géoplateforme download (ogr2ogr)

Download WFS layers from the French Géoplateforme (data.geopf.fr) and convert them to multiple vector formats using **ogr2ogr**.

## Prerequisites

- **GDAL** with WFS support (`ogr2ogr` available).
- Check WFS: `ogr2ogr --formats | grep -i WFS`.
- For GeoParquet: GDAL with Parquet driver (`ogr2ogr --formats | grep -i Parquet`).

Install (examples):

- Ubuntu/Debian: `sudo apt install gdal-bin`
- Conda: `conda install -c conda-forge gdal`

## WFS endpoint

- **Géoplateforme WFS**: `https://data.geopf.fr/wfs/ows` (WFS 2.0).
- GetCapabilities: `https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities`
- Layer names must include the namespace prefix (e.g. `BDTOPO_V3:batiment`, `ADMINEXPRESS-COG.2020:region`).
- Discover layers: MCP tool `gpf_wfs_search_types` from `@ignfab/geocontext`, or open GetCapabilities in a browser.

## Basic syntax

```bash
ogr2ogr -f <FORMAT> <output_file> "WFS:<WFS_URL>" <typename>
```

- **FORMAT**: output driver name (see table below).
- **output_file**: path to the output file (extension usually matches format).
- **WFS_URL**: `https://data.geopf.fr/wfs/ows`.
- **typename**: layer name with prefix, e.g. `BDTOPO_V3:batiment`.

## Output formats

| Format       | `-f` value        | Typical extension | Notes |
|-------------|--------------------|-------------------|--------|
| GeoJSON     | `GeoJSON`          | `.geojson`        | Good for web; large datasets can be heavy. |
| GeoPackage  | `GPKG`             | `.gpkg`           | Single file, SQLite-based, widely supported. |
| Shapefile   | `ESRI Shapefile`   | (directory + .shp)| Legacy; use GPKG when possible. |
| GeoParquet  | `Parquet`          | `.parquet`        | Columnar, good for analytics; needs Parquet driver. |
| GML         | `GML`              | `.gml`            | XML; interoperable. |

## Examples by format

**GeoJSON**

```bash
ogr2ogr -f GeoJSON batiments.geojson \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

**GeoPackage (GPKG)**

```bash
ogr2ogr -f GPKG batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

**GeoParquet** (with layer options)

```bash
ogr2ogr -f Parquet \
  -lco GEOMETRY_NAME=geometry \
  -lco COMPRESSION=SNAPPY \
  batiments.parquet \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

**Shapefile**

```bash
ogr2ogr -f "ESRI Shapefile" batiments_shp \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

**GML**

```bash
ogr2ogr -f GML batiments.gml \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Common ogr2ogr options

| Option | Description | Example |
|--------|-------------|---------|
| `-limit N` | Maximum number of features | `-limit 10000` |
| `-spat xmin ymin xmax ymax` | Bounding box filter (source SRS) | `-spat 1.4 43.5 1.6 43.7` |
| `-where "expr"` | Attribute filter (SQL WHERE) | `-where "nature='Habitation'"` |
| `-select f1,f2` | Select specific fields | `-select id,nom,geometry` |
| `-t_srs EPSG:xxx` | Reproject to target SRS | `-t_srs EPSG:4326` |
| `-progress` | Show progress | `-progress` |

Example with limit and bbox (Lambert-93 approx for France):

```bash
ogr2ogr -f GeoJSON -limit 5000 \
  -spat 650000 6150000 660000 6160000 \
  batiments_extract.geojson \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Additional resources

- GDAL WFS driver: <https://gdal.org/drivers/vector/wfs.html>
- ogr2ogr: <https://gdal.org/programs/ogr2ogr.html>
- Géoplateforme diffusion: <https://geoservices.ign.fr/services-geoplateforme-diffusion>
