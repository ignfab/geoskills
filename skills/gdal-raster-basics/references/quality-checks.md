# Raster quality checks

Inspect metadata before choosing thresholds. A valid zero is not nodata; an absent nodata
tag may require producer documentation. Do not assign a sentinel that is outside the
pixel type's range. Compute statistics on a local bounded output, with PAM disabled to
avoid changing source sidecars:

```bash
gdalinfo --config GDAL_PAM_ENABLED NO -json -stats output.tif > raster-info.json
```

## Coverage and grid

Read `bands[].metadata[""].STATISTICS_VALID_PERCENT` where provided, along with min/max,
pixel size, extent and CRS. Report a missing statistic as unknown. An all-nodata output
fails; a masked polygon crop can legitimately contain nodata outside its boundary.
Compare coverage inside the requested area rather than imposing a universal percentage.

For a mosaic, require compatible CRS, pixel size, band count/type and nodata semantics.
For north-up grids, differences in the origin coordinates divided by the corresponding
pixel size must be integers within floating-point tolerance. Otherwise resample explicitly
onto a chosen grid, and report the method. `-tap` aligns to multiples of the target pixel
size, which may differ from the original grid origin.

## Categorical resampling

Use `near` when refining a class raster. When reducing resolution, choose `mode` for a
majority class or `near` for nearest-source sampling, according to the task. Neither
method guarantees retention of tiny classes. Do not interpolate class codes.

```bash
gdalwarp -tr 5 5 -r near -dstnodata 255 classes.tif classes_resampled.tif
gdal_translate -of COG -co COMPRESS=DEFLATE -co RESAMPLING=NEAREST \
  -co OVERVIEWS=IGNORE_EXISTING classes_resampled.tif classes_cog.tif
```

Here `255` must first be confirmed as an unused, representable nodata code. Inspect an
appropriate sample or histogram of the full output: valid class values must be a subset
of the source classes. Check overviews as well when publishing a categorical COG.
Record class frequencies if disappearing small classes matter for the task.

## Structural COG validation

`LAYOUT=COG` is a metadata check. With **GDAL >= 3.13 and its matching Python bindings**,
run the official validator on the local output:

```bash
gdal driver cog validate --full-check yes output_cog.tif
```

Retain warnings even when the exit code is zero. A nonzero exit is a failed validation.
If the installed GDAL lacks the command/bindings, report structural validation as not
performed; do not install or claim the metadata marker proves conformance. On large
files this reads tile data: keep it in the foreground and account for its I/O cost.

Report source/date, output path, CRS, dimensions, resolution, nodata/valid coverage,
resampling, value ranges or classes, and the checks actually run.

Official reference: [GDAL COG validator](https://gdal.org/en/stable/programs/gdal_driver_cog_validate.html).
