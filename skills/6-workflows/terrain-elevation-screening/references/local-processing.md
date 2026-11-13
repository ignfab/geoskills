# Local processing

Run in a new output directory with the prepared `dem_metric.tif` and `aoi_metric.gpkg`
described in [source selection](sources.md). Resolve relative input paths or use absolute
paths; do not overwrite existing results. Set `RES_M` to the verified DEM cell size and
`Z_MIN_M`, `Z_MAX_M` to the user's finite numeric bounds, with minimum ≤ maximum.
This example implements an **inclusive interval**. For an upper bound alone, remove the
lower comparison; negative terrain elevations are valid. Change `<`/`<=` only to match the
request. These variables are numbers, never arbitrary expressions copied into a command.

## Clip elevations

The prepared DEM is already on the target metric grid. The nearest-neighbour clip keeps
its values. `-9999` is an output sentinel here, not an assumed source missing-value code;
check it lies outside the source's valid range. GDAL uses the source's declared mask/nodata.

```bash
export GDAL_PAM_ENABLED=NO
gdalwarp -cutline aoi_metric.gpkg -cl aoi -crop_to_cutline \
  -tr "$RES_M" "$RES_M" -tap -r near -ot Float32 -dstnodata -9999 \
  -co COMPRESS=DEFLATE dem_metric.tif elevation.tif
```

Use pixel-centre inclusion, not `CUTLINE_ALL_TOUCHED`. Small/narrow polygons may contain
no pixel centres: report insufficient grid support, not absence of qualifying terrain.

## Altitude-only mask

```bash
gdal_calc.py -A elevation.tif \
  --calc="(A >= $Z_MIN_M) & (A <= $Z_MAX_M)" \
  --type=Byte --NoDataValue=255 --co=COMPRESS=DEFLATE --outfile=selection.tif
```

The mask is `1` selected, `0` valid but rejected, `255` unknown or outside the AOI.
Keep default nodata propagation; do not use `--hideNoData` or set nodata to zero.

## Optional slope mask

Use this **instead of** the altitude-only mask when a slope limit was supplied. Set
`SLOPE_MAX_DEG` to that limit in degrees (0–90). Derive Horn slope on the surrounding DEM
before clipping, in metre x/y/z units with scale 1. No `-compute_edges`: missing neighbours
and outer edges stay unknown. The commands follow [gdaldem](https://gdal.org/en/stable/programs/gdaldem.html).

```bash
gdaldem slope dem_metric.tif slope_full.tif -s 1 -alg Horn -co COMPRESS=DEFLATE
gdalwarp -cutline aoi_metric.gpkg -cl aoi -crop_to_cutline \
  -tr "$RES_M" "$RES_M" -tap -r near -ot Float32 -dstnodata -9999 \
  -co COMPRESS=DEFLATE slope_full.tif slope.tif
gdal_calc.py -A elevation.tif -B slope.tif \
  --projectionCheck --extent=fail \
  --calc="(A >= $Z_MIN_M) & (A <= $Z_MAX_M) & (B <= $SLOPE_MAX_DEG)" \
  --type=Byte --NoDataValue=255 --co=COMPRESS=DEFLATE --outfile=selection.tif
```

For a percent limit, use `gdaldem slope -p`, name the output/parameter accordingly and
report percent. Do not compare a percent threshold to degree values. Verify dimensions,
CRS, origin and pixel size of both clipped rasters before interpreting the mask.
The [calculator](https://gdal.org/en/stable/programs/gdal_calc.html) propagates missing
input elevations/slopes. Slope describes the local raster neighbourhood, not an aircraft
footprint or subpixel roughness.

## Candidate polygons

Set `MIN_AREA_M2` to the requested minimum, or `0` for no area filter. Polygonize using
default four-neighbour connectivity, so cells touching only at a corner do not form a
single candidate. The [polygonizer](https://gdal.org/en/stable/programs/gdal_polygonize.html)
omits nodata; explicitly retain only class 1. Clip pixel footprints to the exact AOI before
measuring/filtering area. These generated layers use the known geometry column `geom`.

```bash
gdal_polygonize.py selection.tif -f GPKG classes.gpkg classes selected
ogr2ogr -f GPKG candidates_clipped.gpkg classes.gpkg classes \
  -nln candidates -where 'selected = 1' -clipsrc aoi_metric.gpkg -clipsrclayer aoi
ogr2ogr -f GPKG candidate_parts.gpkg candidates_clipped.gpkg -nln candidates -explodecollections
ogr2ogr -f GPKG candidates.gpkg candidate_parts.gpkg -nln candidates \
  -dialect SQLite -sql "SELECT *, ST_Area(geom) AS area_m2 FROM candidates WHERE ST_Area(geom) > 0 AND ST_Area(geom) >= $MIN_AREA_M2"
```

Keep holes and narrow passages; do not smooth, bridge or dissolve disjoint patches to
meet an area requirement. Exact clipping can split one raster component, so the recipe
splits multipart features **before** the area test and calculates area per part.
A sufficient area alone does not establish sufficient width or a usable
footprint. The raster records the altitude/slope screen before the vector area filter;
report that distinction. Deliver `candidates.gpkg`, not the temporary class-0 polygons.

## Coverage and result checks

```bash
gdalinfo -json -stats elevation.tif
gdalinfo -json -stats selection.tif
ogrinfo -so -al candidates.gpkg
```

For an all-nodata raster, `gdalinfo -stats` may report no valid pixels; investigate coverage
and record insufficient data. An empty GeoPackage layer is an expected result when no
valid cells meet the criteria, not a reason to relax them.

Rasterize `aoi` with pixel-centre inclusion onto a copy of the selection grid (byte band,
initial value 0, burn 1). Count only those AOI pixels: outside cells must not inflate the
missing-data rate. Report valid elevation / AOI cells, selected/rejected/unknown mask
counts and, when relevant, valid elevation cells missing a valid slope. For larger grids,
count in blocks. Verify mask codes and finite input/output values with the declared nodata
excluded. Do not use `STATISTICS_VALID_PERCENT` of the bounding rectangle as AOI coverage.

Check candidate geometries, CRS and containment in the exact AOI; compare summed area to
selected cell count × cell area, allowing reductions for AOI clipping and minimum area.
Check representative selected and rejected cells against the original values and thresholds.
Report min/max/mean elevation over valid AOI cells and any slope range, without statistics
over nodata. Keep resolution separate from horizontal/vertical accuracy and record any
unknown metadata. Include source identifiers, dates, numeric criteria and comparison
operators, nodata policy, connectivity, coverage and the files actually reopened.
