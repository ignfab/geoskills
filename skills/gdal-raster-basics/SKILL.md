---
name: gdal-raster-basics
description: Inspects, clips, reprojects, resamples, mosaics and converts raster data (GeoTIFF, DEM/MNT, orthophotos, satellite images) with the GDAL command-line tools gdalinfo, gdalwarp, gdal_translate and gdalbuildvrt, including Cloud Optimized GeoTIFF (COG). Use when the user wants to découper, reprojeter, rééchantillonner, mosaïquer or convertir a raster, build a COG, read a remote raster, or get information about a GeoTIFF, MNT, RGE ALTI or BD ORTHO file.
---

# GDAL raster basics

Handle raster data with the four GDAL tools that cover most needs:

| Tool | Use it to |
|------|-----------|
| `gdalinfo` | Inspect a raster: size, CRS, extent, resolution, bands, nodata, statistics |
| `gdalwarp` | Reproject, clip (to a box or a polygon), resample, merge |
| `gdal_translate` | Convert formats, extract a window or bands, rescale, set metadata |
| `gdalbuildvrt` | Build a virtual mosaic from many tiles without copying them |

## Prerequisites

- **GDAL** 3.1 or later (the COG driver was added in 3.1).
- Install: `sudo apt install gdal-bin` (Ubuntu/Debian) or `conda install -c conda-forge gdal`.

## Inspect first

Always run `gdalinfo` before processing, to learn the CRS, resolution and nodata value:

```bash
gdalinfo mnt.tif
gdalinfo -stats mnt.tif          # also compute min/max/mean/stddev
```

## Most common commands

Reproject to Lambert-93 and clip to a bounding box expressed in the **target** CRS:

```bash
gdalwarp -t_srs EPSG:2154 -te 650000 6860000 660000 6870000 \
  -r bilinear -co COMPRESS=DEFLATE \
  input.tif output_l93.tif
```

Clip to a polygon (for example a municipality boundary):

```bash
gdalwarp -cutline commune.gpkg -crop_to_cutline -dstnodata -9999 \
  mnt.tif mnt_commune.tif
```

Mosaic tiles (such as RGE ALTI or BD ORTHO tiles) into a VRT, then write a Cloud Optimized
GeoTIFF:

```bash
gdalbuildvrt mosaic.vrt tiles/*.tif
gdal_translate -of COG -co COMPRESS=DEFLATE mosaic.vrt mosaic_cog.tif
```

## Rules of thumb

- Resampling: `-r near` for categorical data (land cover, classes), `-r bilinear` or
  `-r cubic` for continuous data (elevation, temperature), `-r average` when you downsample.
- Always set a compression (`-co COMPRESS=DEFLATE`, or `-co COMPRESS=JPEG` for RGB
  orthophotos). Otherwise the output can be many times larger than the input.
- Keep nodata consistent: check it with `gdalinfo`, then use `-srcnodata` / `-dstnodata`.
- For a file larger than 4 GB, add `-co BIGTIFF=IF_SAFER`.

## References

- [references/gdalwarp-options.md](references/gdalwarp-options.md) — reprojection, clipping,
  resolution, resampling, nodata, performance and troubleshooting.
- [references/cog-and-vrt.md](references/cog-and-vrt.md) — COG creation options, overviews,
  VRT mosaics, reading remote files with `/vsicurl/`, extracting and converting with
  `gdal_translate`.

For the choice of CRS (Lambert-93, CC zones, overseas territories), see the
`crs-reprojection-france` skill.

## Additional resources

- gdalwarp: <https://gdal.org/programs/gdalwarp.html>
- gdal_translate: <https://gdal.org/programs/gdal_translate.html>
- COG driver: <https://gdal.org/drivers/raster/cog.html>
