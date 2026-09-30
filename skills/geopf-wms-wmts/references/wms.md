# WMS-R (GDAL WMS driver)

The raster WMS (`wms-r`) renders an image for an **arbitrary CRS, extent and size**, which
WMTS tile grids cannot. It is the right choice for a Lambert-93 GeoTIFF, a precise pixel
grid, or elevation values (32-bit float).

Endpoint: `https://data.geopf.fr/wms-r/wms`

Available CRS include EPSG:3857, EPSG:2154 (Lambert-93), EPSG:4326 and several
`IGNF:*` / overseas codes. Available formats include `image/png`, `image/jpeg`,
`image/geotiff`, `image/tiff` and `image/x-bil;bits=32`. The BIL format is raw data without
a header, which the GDAL WMS driver cannot decode: request elevation as `image/geotiff`.

## Listing layers

```bash
gdalinfo "WMS:https://data.geopf.fr/wms-r/wms?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities"
```

Each layer is reported as a subdataset. Copy the `SUBDATASET_n_NAME` of the layer you want
and pass it to `gdal_translate`, or build a `<GDAL_WMS>` XML as below.

## GDAL_WMS service description (recommended)

A small XML file pins the layer, CRS, extent, size and format deterministically. Save it as
`ortho_wms.xml`:

```xml
<GDAL_WMS>
  <Service name="WMS">
    <Version>1.3.0</Version>
    <ServerUrl>https://data.geopf.fr/wms-r/wms?</ServerUrl>
    <CRS>EPSG:2154</CRS>
    <ImageFormat>image/geotiff</ImageFormat>
    <Layers>ORTHOIMAGERY.ORTHOPHOTOS</Layers>
    <Styles></Styles>
  </Service>
  <DataWindow>
    <UpperLeftX>574000</UpperLeftX>
    <UpperLeftY>6280000</UpperLeftY>
    <LowerRightX>578000</LowerRightX>
    <LowerRightY>6276000</LowerRightY>
    <SizeX>8000</SizeX>
    <SizeY>8000</SizeY>
  </DataWindow>
  <BandsCount>3</BandsCount>
</GDAL_WMS>
```

Then read it like any raster:

```bash
gdal_translate -of GTiff -co COMPRESS=DEFLATE ortho_wms.xml ortho_l93.tif
```

- `DataWindow` is expressed in the `<CRS>` of the service: `UpperLeft` = (xmin, ymax),
  `LowerRight` = (xmax, ymin).
- `SizeX`/`SizeY` set the pixel grid (here 4000 m / 0.5 m = 8000 px).
- **Axis order:** for a projected CRS (EPSG:2154) the order is easting/northing, so no
  special handling. For **EPSG:4326 with WMS 1.3.0** the axis order is lat/lon — add
  `<BBoxOrder>yxYX</BBoxOrder>` inside `<Service>` if you use it.

## Elevation (32-bit float)

```xml
<GDAL_WMS>
  <Service name="WMS">
    <Version>1.3.0</Version>
    <ServerUrl>https://data.geopf.fr/wms-r/wms?</ServerUrl>
    <CRS>EPSG:2154</CRS>
    <ImageFormat>image/geotiff</ImageFormat>
    <Layers>ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES</Layers>
    <Styles></Styles>
  </Service>
  <DataWindow>
    <UpperLeftX>574000</UpperLeftX>
    <UpperLeftY>6280000</UpperLeftY>
    <LowerRightX>578000</LowerRightX>
    <LowerRightY>6276000</LowerRightY>
    <SizeX>800</SizeX>
    <SizeY>800</SizeY>
  </DataWindow>
  <BandsCount>1</BandsCount>
  <DataType>Float32</DataType>
</GDAL_WMS>
```

```bash
gdal_translate -of GTiff -co COMPRESS=DEFLATE -a_nodata -99999 mnt_wms.xml mnt_l93.tif
```

- `ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES` is the high-resolution RGE ALTI coverage.
  `ELEVATION.ELEVATIONGRIDCOVERAGE` is the national coverage, at a coarser resolution.
- Areas with no data are returned as `-99999`. Set it as the nodata value with
  `-a_nodata -99999`.

## Troubleshooting

- **Blank or shifted image with EPSG:4326** — WMS 1.3.0 axis order; add
  `<BBoxOrder>yxYX</BBoxOrder>`.
- **`IReadBlock failed` with `image/x-bil;bits=32`** — GDAL cannot decode headerless BIL;
  use `image/geotiff` with `<DataType>Float32</DataType>`.
- **`image/geotiff` not honoured** — some layers only expose `image/png` or `image/jpeg`;
  check the layer's formats in GetCapabilities.
- **Too large / slow** — reduce `SizeX`/`SizeY` or the `DataWindow`.
- **`WMS` driver not found** — check `gdalinfo --formats | grep -i WMS`.
