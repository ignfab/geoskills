# gdal-raster-basics

Inspect, clip, reproject, resample, mosaic and convert rasters (DEMs, orthophotos, satellite
images) with the GDAL command-line tools, produce Cloud Optimized GeoTIFFs and compute
zonal statistics. This skill
processes rasters you already have.

## Requirements

GDAL 3.1 or later for the basic recipes (`sudo apt install gdal-bin`, or
`conda install -c conda-forge gdal`). The optional `gdal raster zonal-stats` command
requires GDAL ≥ 3.12; some options require 3.13 as noted in its reference.

## Installation

```bash
npx skills add ignfab/geoskills --skill gdal-raster-basics
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | The core tools and the commands covering most needs. |
| [references/gdalwarp-options.md](references/gdalwarp-options.md) | Reprojection, clipping, resolution, resampling, nodata, performance, troubleshooting. |
| [references/cog-and-vrt.md](references/cog-and-vrt.md) | COG, overviews, VRT mosaics, remote reads, `gdal_translate` recipes. |
| [references/zonal-stats.md](references/zonal-stats.md) | Statistics per polygon with `gdal raster zonal-stats` (GDAL ≥ 3.12) and its pitfalls. |

## Example

```bash
gdalbuildvrt mnt.vrt dalles/*.asc
gdalwarp -cutline commune.gpkg -crop_to_cutline -dstnodata -9999 \
  -of COG -co COMPRESS=DEFLATE mnt.vrt mnt_commune.tif
```
