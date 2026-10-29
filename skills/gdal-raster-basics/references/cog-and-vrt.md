# COG, VRT and gdal_translate

## Cloud Optimized GeoTIFF (COG)

A COG is a regular GeoTIFF with internal tiling and overviews, laid out so that clients can
read one part of it over HTTP. Use it for any raster that you publish or read remotely.

```bash
gdal_translate -of COG \
  -co COMPRESS=DEFLATE -co PREDICTOR=YES \
  -co RESAMPLING=BILINEAR -co NUM_THREADS=ALL_CPUS \
  input.tif output_cog.tif
```

The example uses bilinear resampling for continuous data. For categorical rasters, use
`-co RESAMPLING=NEAREST` or `MODE` to preserve class values in overviews. If source
overviews exist, check their resampling too; `-co OVERVIEWS=IGNORE_EXISTING` rebuilds them.

Useful COG creation options:

| Option | Values | Notes |
|--------|--------|-------|
| `COMPRESS` | `DEFLATE`, `LZW`, `ZSTD`, `JPEG`, `WEBP`, `LERC` | `JPEG` or `WEBP` for RGB imagery, `DEFLATE`, `ZSTD` or `LERC` for DEMs |
| `QUALITY` | 1–100 | For `JPEG` and `WEBP` |
| `PREDICTOR` | `YES` | Better lossless compression |
| `RESAMPLING` | `NEAREST`, `BILINEAR`, `AVERAGE`, ... | Used to build the overviews |
| `BLOCKSIZE` | 512 (default) | Tile size |
| `OVERVIEWS` | `AUTO`, `NONE`, `FORCE_USE_EXISTING` | |
| `TILING_SCHEME` | `GoogleMapsCompatible` | Aligns the file with Web Mercator tiles |
| `BIGTIFF` | `YES`, `IF_SAFER` | `YES` for expected outputs over 4 GiB; `IF_SAFER` is a heuristic |

`gdalwarp -of COG` reprojects and writes a COG in one step:

```bash
gdalwarp -t_srs EPSG:3857 -of COG -co COMPRESS=WEBP -co QUALITY=85 ortho.tif ortho_cog.tif
```

Inspect the COG layout marker (a quick check, not a full structural validation):

```bash
gdalinfo output_cog.tif | grep -i "LAYOUT=COG"
```

For structural validation with GDAL ≥ 3.13 and matching Python bindings, follow
[quality checks](quality-checks.md#structural-cog-validation); retain any warnings.

## Overviews on an existing GeoTIFF

```bash
gdaladdo -r average input.tif          # levels are chosen automatically
gdaladdo -r average input.tif 2 4 8 16 32
gdaladdo -clean input.tif              # remove the overviews
```

## VRT mosaics

A VRT is a small XML file that references source rasters. It opens as a single raster in
GDAL and QGIS, and no pixels are copied.

```bash
gdalbuildvrt mosaic.vrt tiles/*.tif
gdalbuildvrt -input_file_list files.txt mosaic.vrt     # many files
gdalbuildvrt -srcnodata -99999 -vrtnodata -9999 mosaic.vrt tiles/*.asc
gdalbuildvrt -separate stack.vrt b04.tif b03.tif b02.tif   # stack bands
```

- All sources must share the same CRS and number of bands. Reproject them first if they
  do not.
- Mosaic plus clip plus convert in one step: `gdalwarp -te ... mosaic.vrt out.tif`.
- IGN RGE ALTI and BD ALTI tiles come as ESRI ASCII Grid (`.asc`) files. A VRT reads them
  directly. If the `.prj` is missing, confirm the source CRS from the delivery metadata
  first. For tiles confirmed to be Lambert-93:
  `gdalbuildvrt -a_srs EPSG:2154 mnt.vrt dalles/*.asc`.

## Reading remote rasters

The `/vsicurl/` prefix reads a file over HTTP. With a COG, only the needed bytes are
downloaded:

```bash
gdalinfo /vsicurl/https://example.com/data/dem_cog.tif
gdal_translate -projwin 650000 6870000 660000 6860000 \
  /vsicurl/https://example.com/data/dem_cog.tif extract.tif
```

Other virtual file systems: `/vsizip/archive.zip/file.tif`, `/vsis3/bucket/key.tif`,
`/vsigs/`, `/vsiaz/`. They can be combined, for example
`/vsizip//vsicurl/https://.../tiles.zip/tile.asc`.

To speed up remote reads, avoid directory listings:

```bash
export GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR
export CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif
```

## gdal_translate recipes

| Task | Command |
|------|---------|
| Change format | `gdal_translate -of PNG in.tif out.png` |
| Keep some bands, in order | `gdal_translate -b 3 -b 2 -b 1 in.tif rgb.tif` |
| Convert to 8-bit with rescaling | `gdal_translate -ot Byte -scale in.tif out.tif` |
| Rescale a known range | `gdal_translate -ot Byte -scale 0 3000 0 255 in.tif out.tif` |
| Set nodata | `gdal_translate -a_nodata -9999 in.tif out.tif` |
| Assign a missing CRS | `gdal_translate -a_srs EPSG:2154 in.tif out.tif` |
| Pixel-window extract | `gdal_translate -srcwin 0 0 1000 1000 in.tif out.tif` |
| Downsample by a percentage | `gdal_translate -outsize 25% 25% -r average in.tif small.tif` |

## Related tools

- `gdaldem hillshade|slope|aspect mnt.tif out.tif`: DEM derivatives.
- `gdaldem color-relief mnt.tif couleurs.txt out.tif`: colour a DEM. Each line of the
  colour file is `elevation R G B`, for example `500 34 139 34`.
- `gdal_calc.py -A a.tif -B b.tif --calc="A-B" --outfile=diff.tif`: raster algebra.
- `gdal_polygonize.py classes.tif classes.gpkg`: raster to vector.
- `gdal_rasterize -a field -tr 10 10 zones.gpkg zones.tif`: vector to raster.
- `gdallocationinfo -valonly -wgs84 mnt.tif 2.42 48.84`: value at a point.
