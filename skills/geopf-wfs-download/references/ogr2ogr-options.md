# Common ogr2ogr options

| Option                      | Description                      | Example |
|-----------------------------|----------------------------------|---------|
| `-limit N`                  | Maximum number of features       | `-limit 10000` |
| `-spat xmin ymin xmax ymax` | Bounding box filter (source SRS) | `-spat 1.4 43.5 1.6 43.7` |
| `-where "expr"`             | Attribute filter (SQL WHERE)     | `-where "nature='Habitation'"` |
| `-select f1,f2`             | Keep only these fields           | `-select id,nom` |
| `-t_srs EPSG:xxxx`          | Reproject to a target SRS        | `-t_srs EPSG:4326` |
| `-nln <name>`               | Rename the output layer          | `-nln batiments` |
| `-progress`                 | Show a progress bar              | `-progress` |

## Filtering by extent

`-spat` is expressed in the **source** SRS, which depends on the layer. Check it before
guessing:

```bash
ogrinfo -al -so "WFS:https://data.geopf.fr/wfs/ows" "BDTOPO_V3:batiment"
```

Géoplateforme layers use a mix of SRS — mostly EPSG:4326, but also EPSG:2154 (Lambert-93)
and EPSG:3857 (Web Mercator) — so always confirm with `ogrinfo` before filtering. For a
layer served in EPSG:4326, the bounding box is given in degrees, **longitude first** (GDAL
normalises the WFS 2.0 lat/lon axis order to lon/lat):

```bash
ogr2ogr -f GPKG -spat 1.4 43.5 1.6 43.7 \
  batiments_toulouse.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

Use `-spat_srs` to give the bounding box in another SRS, for instance Lambert-93:

```bash
ogr2ogr -f GPKG \
  -spat 650000 6150000 660000 6160000 -spat_srs EPSG:2154 \
  batiments_extract.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Filtering by attribute

```bash
ogr2ogr -f GPKG -where "nature = 'Habitation'" \
  habitations.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Reprojecting

```bash
ogr2ogr -f GPKG -t_srs EPSG:2154 \
  batiments_l93.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Performance

- The WFS driver pages through the service; `--config OGR_WFS_PAGING_ALLOWED ON` and
  `--config OGR_WFS_PAGE_SIZE 5000` tune that behaviour.
- `--config GDAL_HTTP_TIMEOUT 120` avoids timeouts on slow layers.
- `-progress` combined with `-limit` is the quickest way to probe a layer before a large
  download.

```bash
ogr2ogr -f GPKG -progress \
  --config OGR_WFS_PAGING_ALLOWED ON \
  --config OGR_WFS_PAGE_SIZE 5000 \
  batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Troubleshooting

- **`unable to find driver WFS`** — GDAL was built without WFS support; check with
  `ogr2ogr --formats | grep -i WFS`.
- **`Layer not found`** — the namespace prefix is missing, or the layer name changed. List
  the available layers with `ogrinfo "WFS:https://data.geopf.fr/wfs/ows"`.
- **Empty output** — the `-spat` bounding box is probably expressed in the wrong SRS; check
  the layer extent with `ogrinfo -al -so "WFS:https://data.geopf.fr/wfs/ows" <typename>`.
- **Download never ends** — a nationwide layer is being fetched in full; add `-spat` or
  `-limit`.
