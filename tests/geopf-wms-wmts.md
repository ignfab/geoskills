# geopf-wms-wmts

## WMS-01 — Orthophoto extract in Lambert-93

> Télécharge l'orthophoto sur 500 m × 500 m autour du Capitole de Toulouse, à 50 cm, en
> GeoTIFF Lambert 93, dans output/ortho_capitole.tif.

**Expected skill:** `geopf-wms-wmts`

**Expected result:** GeoTIFF in EPSG:2154, 0.5 m pixels, about 1000 × 1000 pixels, centred
near 574357 / 6279621. It has 3 bands (WMS-R) or 4 bands, RGB + alpha (WMTS).

- [ ] WMTS: uses `WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS`.
  The bare `WMTS:https://data.geopf.fr/wmts` fails with HTTP 400.
- [ ] or WMS-R: a `<GDAL_WMS>` description with `EPSG:2154` and `image/geotiff`
- [ ] restricts the extent (`-te`/`-te_srs`, `-projwin` or `DataWindow`) and sets the
  resolution
- [ ] compresses the output (JPEG or DEFLATE)
- [ ] checks that the output is not empty (`gdalinfo -stats`, alpha band). On a transient
  HTTP 502 or 400 from the tile server, GDAL can still write a file with empty blocks; the
  agent must inspect the error, retry transient failures a bounded number of times, and
  report an incomplete download if it still fails. HTTP 400 requires checking the request.

## WMS-02 — Elevation values

> Récupère le MNT haute résolution (RGE ALTI) à 5 m sur l'emprise de
> data/saint_mande.geojson, en GeoTIFF Float32 Lambert 93, dans output/mnt_5m.tif.

**Expected skill:** `geopf-wms-wmts`

**Reference result:** Float32, EPSG:2154, 5 m pixels, extent about 656795–658045 /
6859450–6861200 (250 × 350 pixels), nodata `-99999`, values from about 38.5 to 54.9 m,
mean ≈ 50.1 m.

- [ ] uses WMS-R with `ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES`
- [ ] requests `image/geotiff` with `<DataType>Float32</DataType>`. `image/x-bil;bits=32`
  fails in GDAL.
- [ ] does not download a rendered, coloured image (a PNG or JPEG of the elevation)
- [ ] sets nodata (`-99999` for this service); checks that valid elevations exist
- [ ] does not require exact extrema or dimensions if a different valid grid alignment
  was selected; API data can change

## WMS-03 — Plan IGN in Web Mercator

> Fais-moi une image Plan IGN du centre de Toulouse (de 1.43, 43.59 à 1.45, 43.61) en Web
> Mercator, dans output/planign.tif.

**Expected skill:** `geopf-wms-wmts`

**Expected result:** GeoTIFF in EPSG:3857 from the WMTS layer
`GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2`.

- [ ] uses the WMTS connection string with the full GetCapabilities URL
- [ ] checks that valid pixels exist and the image is not uniform; the exact colour mean
  depends on the current map style and resolution
- [ ] gives the box in lon/lat with `-te_srs EPSG:4326` (or `-projwin_srs`)

## WMS-04 — List the available layers

> Quelles couches d'orthophotos sont disponibles en WMTS sur la Géoplateforme ?

**Expected skill:** `geopf-wms-wmts`

**Expected result:** a list derived from current capabilities, including
`ORTHOIMAGERY.ORTHOPHOTOS` if still advertised. `HR.ORTHOIMAGERY.ORTHOPHOTOS` is an example
observed previously, not a permanently required identifier.

- [ ] uses `gdalinfo "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities"`
  or reads the GetCapabilities document

## WMS-N1 — Negative: vector data

> Télécharge les bâtiments BD TOPO du centre de Toulouse en GeoPackage.

**Expected skill:** `geopf-wfs-download`, not `geopf-wms-wmts`.

## WMS-05 — Check availability before downloading a named product

> Télécharge le SCAN 25 sur le centre de Toulouse.

**Expected result:** the agent checks current public capabilities. If no usable SCAN 25
layer is advertised, it explains that limitation; it does not invent a layer name or
return an empty image. If a suitable layer has become available, a bounded download with
its actual identifier is valid. Absence observed previously is not a permanent API contract.
