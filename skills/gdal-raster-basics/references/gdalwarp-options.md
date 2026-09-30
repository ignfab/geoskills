# Common gdalwarp options

| Option | Description | Example |
|--------|-------------|---------|
| `-t_srs <crs>` | Target CRS | `-t_srs EPSG:2154` |
| `-s_srs <crs>` | Override the source CRS (when it is missing or wrong) | `-s_srs EPSG:2154` |
| `-te xmin ymin xmax ymax` | Output extent, in the target CRS | `-te 650000 6860000 660000 6870000` |
| `-te_srs <crs>` | CRS in which `-te` is given | `-te_srs EPSG:4326` |
| `-tr xres yres` | Output resolution, in target CRS units | `-tr 5 5` |
| `-tap` | Align the output grid on multiples of `-tr` | `-tr 5 5 -tap` |
| `-ts width height` | Output size in pixels (use this or `-tr`, not both) | `-ts 2000 0` |
| `-r <method>` | Resampling method | `-r bilinear` |
| `-cutline <file>` | Clip with a polygon layer | `-cutline zone.gpkg` |
| `-crop_to_cutline` | Shrink the extent to the polygon | |
| `-srcnodata` / `-dstnodata` | Input and output nodata values | `-dstnodata -9999` |
| `-of <driver>` | Output format (default GTiff) | `-of COG` |
| `-co KEY=VALUE` | Creation option | `-co COMPRESS=DEFLATE` |
| `-overwrite` | Replace an existing output file | |
| `-multi -wo NUM_THREADS=ALL_CPUS` | Use all CPU cores | |

## Resampling methods

| Method | Use for |
|--------|---------|
| `near` | Categorical data: land cover, classifications, masks. This is the default |
| `bilinear` | Continuous data: elevation, temperature. A good general default |
| `cubic` / `cubicspline` | Smoother continuous surfaces, imagery |
| `lanczos` | High-quality imagery upsampling (slower) |
| `average` | Downsampling continuous data |
| `mode` | Downsampling categorical data (keeps the most frequent class) |
| `min`, `max`, `med`, `q1`, `q3`, `sum` | Aggregating statistics when downsampling |

## Clipping

To a box in the target CRS:

```bash
gdalwarp -te 650000 6860000 660000 6870000 input.tif clip.tif
```

To a box in another CRS (here, degrees):

```bash
gdalwarp -t_srs EPSG:2154 -te 2.40 48.83 2.45 48.86 -te_srs EPSG:4326 input.tif clip.tif
```

`gdal_translate -projwin` is faster for a simple window without reprojection. Note that the
order is **ulx uly lrx lry** (top-left corner, then bottom-right corner):

```bash
gdal_translate -projwin 650000 6870000 660000 6860000 input.tif clip.tif
```

To a polygon, selecting one feature with a SQL filter:

```bash
gdalwarp -cutline communes.gpkg -cl communes -cwhere "code_insee = '94067'" \
  -crop_to_cutline -dstnodata -9999 \
  mnt.tif mnt_saint_mande.tif
```

The cutline can be in any CRS: GDAL reprojects it on the fly.

## Changing resolution

Aggregate a 1 m DEM to 25 m, on a grid aligned to multiples of 25 m:

```bash
gdalwarp -tr 25 25 -tap -r average mnt_1m.tif mnt_25m.tif
```

## Nodata

```bash
gdalwarp -srcnodata -99999 -dstnodata -9999 input.tif output.tif
```

Without `-dstnodata`, gdalwarp reuses the source nodata value. If the source has **no**
nodata value, the areas outside the source (after reprojection or clipping) are filled with
0, which is a valid elevation. Always check with `gdalinfo`, and set `-dstnodata` for DEMs.

Add an alpha band instead, for RGB imagery:

```bash
gdalwarp -t_srs EPSG:3857 -dstalpha ortho.tif ortho_3857.tif
```

## Performance

```bash
gdalwarp -multi -wo NUM_THREADS=ALL_CPUS -wm 2048 \
  --config GDAL_CACHEMAX 2048 \
  -co COMPRESS=DEFLATE -co TILED=YES -co BIGTIFF=IF_SAFER \
  input.vrt output.tif
```

- `-wm` sets the warp memory in MB.
- When processing many tiles, build a VRT first and run a single `gdalwarp` on it, rather
  than warping each tile and merging the results.
- `-co PREDICTOR=2` (integers) or `-co PREDICTOR=3` (floats) improves DEFLATE compression.

## Troubleshooting

- **Output is huge**: no compression was set. Add `-co COMPRESS=DEFLATE` (or `LZW`, `ZSTD`).
- **Output is empty or all nodata**: the `-te` extent is in the wrong CRS. It is expressed
  in the target CRS unless you pass `-te_srs`.
- **Black or zero border after reprojection**: set `-dstnodata`, or `-dstalpha` for imagery.
- **"Output dataset ... exists, but some command line options were provided indicating a new
  dataset should be created"**: add `-overwrite`. Without options such as `-tr` or `-te`,
  gdalwarp would instead warp *into* the existing file.
- **Blocky DEM after reprojection**: the default resampling is `near`. Use `-r bilinear`.
- **Missing or unknown CRS** (`gdalinfo` shows no coordinate system): assign one with
  `gdal_translate -a_srs EPSG:2154 in.tif out.tif`. Do not use `gdalwarp -t_srs` for this,
  because it would transform the data.
