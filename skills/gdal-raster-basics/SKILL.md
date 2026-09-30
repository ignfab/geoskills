---
name: gdal-raster-basics
description: Inspects, clips, reprojects, resamples, mosaics and converts raster data (GeoTIFF, DEM/MNT, orthophotos, satellite images) with the GDAL command-line tools gdalinfo, gdalwarp, gdal_translate and gdalbuildvrt, including Cloud Optimized GeoTIFF (COG) and zonal statistics per polygon. Use when the user wants to découper, reprojeter, rééchantillonner, mosaïquer or convertir a raster, build a COG, read a remote raster, compute statistiques zonales (mean elevation per commune, zonal statistics), or get information about a GeoTIFF, MNT, RGE ALTI or BD ORTHO file.
---

# GDAL raster basics

Handle raster data with the GDAL tools that cover most needs:

| Tool | Use it to |
|------|-----------|
| `gdalinfo` | Inspect a raster: size, CRS, extent, resolution, bands, nodata, statistics |
| `gdalwarp` | Reproject, clip (to a box or a polygon), resample, merge |
| `gdal_translate` | Convert formats, extract a window or bands, rescale, set metadata |
| `gdalbuildvrt` | Build a virtual mosaic from many tiles without copying them |
| `gdal raster zonal-stats` | Statistics per polygon, e.g. mean elevation per commune (GDAL ≥ 3.12) |

## Prerequisites

- **GDAL** 3.1 or later (the COG driver was added in 3.1).
- Install: `sudo apt install gdal-bin` (Ubuntu/Debian) or `conda install -c conda-forge gdal`.
- If GDAL is missing, give the user the install command and let them run it; do not install
  software yourself.

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
GeoTIFF (continuous data in this example):

```bash
gdalbuildvrt mosaic.vrt tiles/*.tif
gdal_translate -of COG -co COMPRESS=DEFLATE -co RESAMPLING=AVERAGE mosaic.vrt mosaic_cog.tif
```

Statistics per polygon (**the zones must be in the raster CRS**, they are not reprojected):

```bash
gdal raster zonal-stats --stat mean --stat min --stat max \
  --zones communes_l93.gpkg --include-field code_insee \
  -f CSV mnt_l93.tif stats_par_commune.csv
```

## Rules of thumb

- Resampling: `-r near` for categorical data (land cover, classes), `-r bilinear` or
  `-r cubic` for continuous data (elevation, temperature), `-r average` when downsampling
  continuous data and `-r mode` for classes. For categorical COGs, also set
  `-co RESAMPLING=NEAREST` or `MODE` for the overviews.
- Always set a compression (`-co COMPRESS=DEFLATE`, or `-co COMPRESS=JPEG` for RGB
  orthophotos). Otherwise the output can be many times larger than the input.
- Keep nodata consistent: check it with `gdalinfo`, then use `-srcnodata` / `-dstnodata`.
- If the output is expected to exceed 4 GiB, use `-co BIGTIFF=YES`; `IF_SAFER` is a
  heuristic when the final compressed size is uncertain.

## Validate the output

Before reporting a result, run `gdalinfo -stats <output>` and check:

- the CRS, pixel size and extent you asked for (after clipping, close to the extent of the
  polygon);
- a declared nodata value, and a plausible min/max: a mainland France DEM lies between about
  −10 and 4,810 m, and zeros along the edges usually mean a missing `-dstnodata`;
- `LAYOUT=COG` in the metadata when a COG was requested.

## References

- [references/gdalwarp-options.md](references/gdalwarp-options.md) — reprojection, clipping,
  resolution, resampling, nodata, performance and troubleshooting.
- [references/cog-and-vrt.md](references/cog-and-vrt.md) — COG creation options, overviews,
  VRT mosaics, reading remote files with `/vsicurl/`, extracting and converting with
  `gdal_translate`.
- [references/zonal-stats.md](references/zonal-stats.md) — statistics of a raster per
  polygon with `gdal raster zonal-stats` (GDAL ≥ 3.12), options and pitfalls.

To download rasters (orthophotos, elevation) from the Géoplateforme, see the
`geopf-wms-wmts` skill. For the choice of CRS (Lambert-93, CC zones, overseas territories),
see the `crs-reprojection-france` skill.

## Additional resources

- gdalwarp: <https://gdal.org/programs/gdalwarp.html>
- gdal_translate: <https://gdal.org/programs/gdal_translate.html>
- COG driver: <https://gdal.org/drivers/raster/cog.html>
