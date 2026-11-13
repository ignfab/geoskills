# Source selection

## Inspect local inputs first

Use supplied data when it fits the request. Read layers/fields/CRSs from `ogrinfo -so -al`
and raster bands, units, scale, offset, nodata/masks and geotransform from `gdalinfo -json`.
Set `GDAL_PAM_ENABLED=NO` for read-only inspection to avoid source sidecars. An absent CRS
requires evidence before assignment. A known horizontal CRS does not identify a vertical
datum. Record an unknown datum explicitly and resolve it before applying a datum-specific
threshold. Terrain altitude, ellipsoidal GNSS height and height above ground differ.

For terrain filtering choose a digital terrain model (DTM), not a surface model (DSM).
The IGN [RGE ALTI specification](https://data.geopf.fr/annexes/ressources/documentation/DC_RGEALTI_2-0.pdf)
describes ground elevations in metres. Check the actual delivery's datum and accuracy;
do not infer them from that product name alone, particularly outside mainland France.
A DSM includes surface objects and does not substitute for bare ground. Subtracting DSM
and DTM needs compatible dates, grids and references and is a separate obstacle analysis.

## Acquire an area, not millions of points

Discover current metadata rather than guessing resource names, coverage or file URLs:

```bash
curl --fail --show-error --location --max-time 60 \
  'https://data.geopf.fr/telechargement/capabilities?page=1&limit=10' \
  --output download-capabilities.xml
```

Follow advertised resource/folder/file links and pagination with `geopf-download-files`
when available. Select intersecting tiles, recording product, edition, acquisition date
if known, resolution, horizontal/vertical references, accuracy and licence. A catalogue
bounding box is not evidence of complete valid coverage. Run downloads in the foreground
with visible progress, bounded retries and transfer checks; do not truncate their output.

For a small AOI, `geopf-wms-wmts` can obtain a numeric elevation extract if the service
advertises it. Inspect GetCapabilities for the layer, format, CRS and request limits;
verify the resulting band actually contains elevations. Colour relief, hillshade and
ordinary image tiles are not numeric terrain models. Split oversized requests on one
aligned grid. If only a few coordinates or a path are needed, use `geopf-altimetry`.

## Prepare a common metric grid

Choose a projected metre CRS appropriate to the territory; EPSG:2154 is an option for
metropolitan France, not a worldwide default. Verify metre elevation values too. Apply
documented scale/offset with `gdal_translate -unscale` to a new file where necessary.
Convert units or vertical references explicitly, with available validated transformations;
do not merely relabel the band or CRS. Normalize mask-only or documented missing values
to an explicit nodata sentinel outside the valid range. Investigate non-finite values.

Prepare `dem_metric.tif`: one north-up elevation band, square cells, projected metre
coordinates, metre elevations, explicit nodata, and enough coverage for the AOI. Use
`gdalbuildvrt` for compatible tiles and `gdalwarp` if reprojection is required. Keep the
source resolution unless a change is justified; use a documented continuous resampler
such as bilinear for reprojection. Interpolation or coarsening can alter threshold results
and suppress local relief; report that. Finer pixels do not create new source detail.

For slope, retain at least one valid-cell halo around the AOI on the final grid and mosaic
before deriving it to avoid artificial tile seams. Extra source coverage may be required
by the reprojection kernel. If coverage is missing, retain unknown edge cells rather than
interpolating them into candidates. Never fill nodata merely to obtain a complete screen.

Prepare `aoi_metric.gpkg`, layer `aoi`, with a valid polygon/multipolygon in that same CRS
and no unintended extra AOI features. Resolve overlapping AOIs as one footprint. Set grid
bounds and resolution explicitly when preparing the DEM; the local recipe uses a grid
aligned to multiples of its cell size. Keep provenance and intermediate processing in a
manifest/report; all scratch files belong in a new working/output directory.
