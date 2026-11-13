# gdal-raster-processing

**Family:** [3. Prepare and check](../README.md).

Inspect, clip, reproject, resample, mosaic and convert rasters (DEMs, orthophotos, satellite
images) with the GDAL command-line tools `gdalinfo`, `gdalwarp`, `gdal_translate` and
`gdalbuildvrt`, produce Cloud Optimized GeoTIFFs and compute zonal statistics. This skill
processes rasters you already have, such as RGE ALTI or BD ORTHO tiles, and checks the
coverage, grid and COG structure of its outputs.

## When to use it

- Read the size, resolution, CRS, nodata value and value range of a GeoTIFF or a DEM tile.
- Mosaic DEM tiles into a VRT, clip the mosaic to a municipality and write a COG.
- Aggregate a DEM to a coarser grid aligned on multiples of the pixel size, by averaging.
- Produce a hillshade or another DEM derivative with `gdaldem`.
- Compute zonal statistics per polygon, for example the mean elevation per municipality.
- Resample a categorical raster to a COG without interpolating class codes, keeping a valid
  class 0 apart from nodata.

## When to use another skill

- The elevation of one or a few points: call the Elevation API with
  [`geopf-altimetry`](../../4-analyze/geopf-altimetry/README.md) instead of downloading and
  sampling a DEM.
- Downloading rasters from the Géoplateforme:
  [`geopf-raster-download`](../../2-access/geopf-raster-download/README.md) for map-service extracts, or
  [`geopf-file-download`](../../2-access/geopf-file-download/README.md) for ready-made files.
- Choosing a CRS (Lambert-93, CC zones, overseas territories):
  [`crs-reprojection-france`](../crs-reprojection-france/README.md).
- Zonal statistics in Python with `rasterstats`:
  [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md).
- Counting or summing vector objects per zone, which is not a raster operation:
  [`spatial-aggregation`](../../4-analyze/spatial-aggregation/README.md).
- Selecting candidate areas by altitude, with optional slope and area criteria, from DEM
  to polygons: [`terrain-elevation-screening`](../../6-workflows/terrain-elevation-screening/README.md).

## What you get

- Rasters (GeoTIFF, COG, VRT mosaics) with an explicit compression, or a CSV or GeoPackage
  of statistics per polygon.
- Before reporting, the agent runs `gdalinfo -stats` on the output and checks:
  - the requested CRS, pixel size and extent (after a clip, close to the polygon extent);
  - the nodata value or mask, valid-data coverage and a plausible min/max for the source and
    area; zero can be a valid value, and an all-nodata output fails;
  - `LAYOUT=COG` as a quick check when a COG was requested, then the structural validator
    `gdal driver cog validate` when available. Otherwise structural validation is reported
    as not performed: the metadata marker is not proof of conformance;
  - for class rasters, that output values are a subset of the source classes.
- Zonal statistics require zones in the raster CRS: they are not reprojected, and a
  mismatch silently yields empty statistics.
- A report with source, output, CRS and units, extent, raster dimensions, processing
  choices and checks, separating failed checks, warnings and checks not performed.

## Requirements

GDAL 3.1 or later for the basic recipes (`sudo apt install gdal-bin`, or
`conda install -c conda-forge libgdal-core` for native CLI tools). Python utilities or
bindings additionally need matching `python3-gdal` (system) or `gdal` (Conda), with NumPy
for array calculations. Reuse existing tools and add only the selected recipe's missing
packages. The optional `gdal raster zonal-stats` command
requires GDAL ≥ 3.12; some options require 3.13 as noted in its reference.
Full structural COG validation requires GDAL ≥ 3.13 with matching Python bindings;
see [quality checks](references/quality-checks.md#structural-cog-validation).
The user installs missing software; the agent does not.

The recipes work on local files. Remote rasters can be read over HTTP with `/vsicurl/`.

## Installation

```bash
npx skills add ignfab/geoskills --skill gdal-raster-processing
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/3-prepare`.

## Example

> Assemble the tiles in `data/mnt_dalles/`, clip the DEM to the municipality of Saint-Mandé
> (`data/saint_mande.geojson`) and produce a COG in `output/mnt_saint_mande.tif`. The tile
> metadata is in `data/README.md`.

```bash
gdalbuildvrt mnt.vrt dalles/*.asc
gdalwarp -cutline commune.gpkg -crop_to_cutline -dstnodata -9999 \
  -of COG -co COMPRESS=DEFLATE mnt.vrt mnt_commune.tif
```

ASCII tiles without a `.prj` have no CRS. Once it is confirmed from the producer metadata,
assign it when building the VRT (`gdalbuildvrt -a_srs EPSG:2154`), as shown in
[references/cog-and-vrt.md](references/cog-and-vrt.md).

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | The core tools and the commands covering most needs. |
| [references/gdalwarp-options.md](references/gdalwarp-options.md) | Reprojection, clipping, resolution, resampling, nodata, performance, troubleshooting. |
| [references/cog-and-vrt.md](references/cog-and-vrt.md) | COG, overviews, VRT mosaics, remote reads, `gdal_translate` recipes. |
| [references/zonal-stats.md](references/zonal-stats.md) | Statistics per polygon with `gdal raster zonal-stats` (GDAL ≥ 3.12) and its pitfalls. |
| [references/quality-checks.md](references/quality-checks.md) | Valid-data coverage, grid alignment, categorical resampling and structural COG validation. |

## Tests

- Agent scenarios: [tests/gdal-raster-processing.md](../../../tests/gdal-raster-processing.md), in
  French (6 positive, 1 negative).
- Offline: [test_workflows.py](../../../tests/test_workflows.py) (mosaic, clip and COG,
  weighted averaging, hillshade, zonal statistics, nodata conversion) and
  [test_raster_quality.py](../../../tests/test_raster_quality.py) (categorical resampling,
  full COG validation on GDAL ≥ 3.13). No live test.

## Related skills

- [`geopf-file-download`](../../2-access/geopf-file-download/README.md) and
  [`geopf-raster-download`](../../2-access/geopf-raster-download/README.md) supply the rasters that this
  skill processes.
- [`crs-reprojection-france`](../crs-reprojection-france/README.md) confirms a missing tile
  CRS before it is assigned, and chooses the target CRS.
- [`geodata-intake`](../geodata-intake/README.md) inventories a raster delivery before any
  processing.
