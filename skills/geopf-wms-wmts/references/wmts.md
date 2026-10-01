# WMTS (GDAL WMTS driver)

The WMTS service serves **pre-rendered tile pyramids**, cached and fast. Most layers are
published in a Web Mercator (**EPSG:3857**) tile matrix set named `PM_<min>_<max>` (for
example `PM_0_19` for the orthophotos). A few layers use another set: Lambert-93
(`2154_5cm_…`, `2154_10cm_…`, for layers such as `GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2.L93`) or
WGS84 (`WGS84G_0_11` for `ELEVATION.ELEVATIONGRIDCOVERAGE`). Reproject on the fly with
`gdalwarp -t_srs` if you need another CRS.

Endpoint: `https://data.geopf.fr/wmts`. GDAL must be given the GetCapabilities URL,
`WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities`. With the bare
`WMTS:https://data.geopf.fr/wmts`, the server answers HTTP 400 and GDAL reports
`Missing Capabilities.Contents element`.

## Listing layers

```bash
gdalinfo "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities"
```

Each layer is reported as a subdataset whose name is a ready-to-use connection string, e.g.
`WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2`.
`tilematrixset` is only added when a layer offers several sets.

## Connection string

```
WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=<IDENTIFIER>[,tilematrixset=<TMS>][,style=<STYLE>][,tilematrix=<ID>][,zoom_level=<N>]
```

- `layer` — the WMTS layer identifier (e.g. `ORTHOIMAGERY.ORTHOPHOTOS`).
- `tilematrixset` — for example `PM_0_19` (EPSG:3857); optional when the layer has only
  one, which is the case for most layers.
- `style` — defaults to the layer's default (`normal` for most GPF layers).
- `tilematrix` / `zoom_level` — pin a single zoom level (see below).

Inspect a single layer before downloading:

```bash
gdalinfo "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS"
```

## Bounded extract (recommended)

`gdalwarp` is the most ergonomic: it clips, reprojects and sets the pixel size in one call.

```bash
gdalwarp \
  -te 1.43 43.59 1.45 43.61 -te_srs EPSG:4326 \
  -t_srs EPSG:2154 -tr 0.5 0.5 \
  -of GTiff -co COMPRESS=DEFLATE \
  "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS" \
  ortho_toulouse.tif
```

- `-te xmin ymin xmax ymax` with `-te_srs` — target bounding box (here in degrees, lon/lat).
- `-t_srs` — output CRS; `-tr xres yres` — output pixel size (metres in EPSG:2154).
- The source WMTS is EPSG:3857, so GDAL reprojects 3857 → 2154 automatically.

`gdal_translate` is an alternative when you stay in the tile CRS (EPSG:3857):

```bash
gdal_translate \
  -projwin 1.43 43.61 1.45 43.59 -projwin_srs EPSG:4326 \
  -outsize 2000 0 -of GTiff \
  "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS" \
  ortho.tif
```

`-projwin` is `ulx uly lrx lry` (xmin ymax xmax ymin). `-outsize 2000 0` fixes the width and
keeps the aspect ratio.

## Controlling zoom / resolution

WMTS exposes one raster level per tile-matrix zoom. Pick the resolution instead of pulling
the finest level over a large area:

- with `gdalwarp`, set `-tr <xres> <yres>` (in the target CRS units);
- with `gdal_translate`, set `-outsize` or `-tr`;
- or pin a level in the connection string with `,zoom_level=<N>` or `,tilematrix=<ID>`.

## Other layers

Plan IGN (PNG base map):

```bash
gdalwarp -te 1.43 43.59 1.45 43.61 -te_srs EPSG:4326 \
  -t_srs EPSG:3857 -tr 2 2 -of GTiff \
  "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2" \
  planign.tif
```

## Troubleshooting

- **Output is enormous / never finishes** — no extent was set, or `-tr` is finer than
  needed. Add `-te`/`-projwin` and a coarser `-tr`/`-outsize`.
- **`Cannot find layer`** — wrong identifier; list them with
  `gdalinfo "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities"`.
- **`Missing Capabilities.Contents element` (HTTP 400)** — the connection string uses the
  bare endpoint; use `WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,...`.
- **Unexpected CRS** — most WMTS layers are EPSG:3857 (check with `gdalinfo`); use
  `gdalwarp -t_srs` to reproject.
- **`WMTS` driver not found** — check `gdalinfo --formats | grep -i WMTS`.
