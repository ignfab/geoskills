# Common ogr2ogr options

| Option                      | Description                      | Example |
|-----------------------------|----------------------------------|---------|
| `-limit N`                  | Maximum number of features       | `-limit 10000` |
| `-spat xmin ymin xmax ymax` | Bounding box filter (source SRS) | `-spat 1.4 43.5 1.6 43.7` |
| `-where "expr"`             | Attribute filter (SQL WHERE)     | `-where "usage_1='Résidentiel'"` |
| `-select f1,f2`             | Keep only these fields           | `-select cleabs,nature` |
| `-t_srs EPSG:xxxx`          | Reproject to a target SRS        | `-t_srs EPSG:4326` |
| `-nln <name>`               | Rename the output layer          | `-nln batiments` |
| `-progress`                 | Show a progress bar              | `-progress` |

## Filtering by extent

`-spat` is expressed in the **source** SRS, which depends on the layer. Check it before
guessing:

```bash
ogrinfo -so -nocount -noextent "WFS:https://data.geopf.fr/wfs/ows" "BDTOPO_V3:batiment"
```

Géoplateforme layers use a mix of SRS — mostly EPSG:4326, but also EPSG:2154 (Lambert-93)
and EPSG:3857 (Web Mercator) — so always confirm with `ogrinfo` before filtering. For a
layer served in EPSG:4326, the bounding box is given in degrees, **longitude first** (GDAL
normalises the WFS 2.0 lat/lon axis order to lon/lat):

```bash
ogr2ogr -f GPKG -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  batiments_toulouse.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

Explicit `-spat_srs` avoids depending on a layer's default CRS. It can also express the
bounding box in Lambert-93:

```bash
ogr2ogr -f GPKG \
  -spat 574000 6279000 575000 6280000 -spat_srs EPSG:2154 \
  batiments_extract.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Filtering by attribute

Inspect the schema and sample values before choosing a filter. For BD TOPO buildings,
primary residential use is `usage_1 = 'Résidentiel'` (checked on 2026-09-30); `nature`
describes the building kind and is a different classification.

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GPKG -where "usage_1 = 'Résidentiel'" \
  habitations.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Reprojecting

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GPKG -t_srs EPSG:2154 \
  batiments_l93.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

To choose the target CRS (CC zones, overseas territories), see the `crs-reprojection-france`
skill.

`-spat` selects intersecting features; it does not cut their geometry at the box.
Use clipping separately if the output geometry must stay inside the requested boundary.

## Selecting features inside a named area

A bounding box is only a coarse filter: it also returns features outside the area. For a
commune or a department, take the real boundary from ADMIN EXPRESS, use its bounding box
as a server-side filter, then select exactly. Example for Saint-Mandé (INSEE 94067):

```bash
# 1. The boundary, from its INSEE code
ogr2ogr -f GPKG -lco GEOMETRY_NAME=geom -nlt CONVERT_TO_LINEAR -nlt PROMOTE_TO_MULTI \
  zone.gpkg "WFS:https://data.geopf.fr/wfs/ows" "ADMINEXPRESS-COG.LATEST:commune" \
  -where "code_insee = '94067'" -nln zone

# 2. Its bounding box, read from the result (xmin ymin xmax ymax)
ogrinfo -so zone.gpkg zone | grep Extent
# Extent: (2.411472, 48.833712) - (2.428316, 48.849392)

# 3. Server-side filter on that box, into the same GeoPackage
ogr2ogr -f GPKG -update -lco GEOMETRY_NAME=geom -nlt CONVERT_TO_LINEAR -nlt PROMOTE_TO_MULTI \
  zone.gpkg "WFS:https://data.geopf.fr/wfs/ows" "BDTOPO_V3:batiment" \
  -spat 2.411472 48.833712 2.428316 48.849392 -spat_srs EPSG:4326 -nln batiment

# 4a. Keep the features that intersect the boundary
ogr2ogr -f GPKG batiments_saint_mande.gpkg zone.gpkg -nln batiment -dialect SQLite \
  -sql "SELECT b.* FROM batiment b JOIN zone z ON ST_Intersects(b.geom, z.geom) = 1"

# 4b. Or cut the geometries at the boundary
ogr2ogr -f GPKG batiments_decoupes.gpkg zone.gpkg batiment -clipsrc zone.gpkg -clipsrclayer zone
```

In September 2026, the box returned 2,634 buildings, of which 1,744 intersect the commune.

- `-nlt CONVERT_TO_LINEAR` is required before any SQL spatial function. Géoplateforme
  layers are declared as curved types (`MultiSurface`). The SQLite dialect cannot evaluate
  them, and `ST_Intersects` then returns `-1`, which SQLite treats as true: the selection
  silently keeps every feature. Compare the result with `= 1`, as above, so that an
  error keeps nothing instead of everything.
- `-lco GEOMETRY_NAME=geom` gives a predictable column name for SQL. Without it, the
  column keeps the WFS name (`geometrie`).

Check the boundary before using it (area in km², computed in Lambert-93):

```bash
ogrinfo zone.gpkg -dialect SQLite -sql "SELECT sum(ST_Area(ST_Transform(geom, 2154)))/1e6 AS km2 FROM zone"
# km2 (Real) = 0.9057
```

## Performance

- The WFS driver pages through the service; `--config OGR_WFS_PAGING_ALLOWED ON` and
  `--config OGR_WFS_PAGE_SIZE 5000` tune that behaviour.
- `--config GDAL_HTTP_TIMEOUT 120` avoids timeouts on slow layers.
- Probe with a small bounding box and `-limit`. `-progress` may request a feature count
  and is not a guarantee of a cheap probe.
- Check the output CRS, feature count and extent with `ogrinfo -so`; report any sampling
  limit or failed pages. Do not describe a truncated output as complete.

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GPKG -progress \
  --config OGR_WFS_PAGING_ALLOWED ON \
  --config OGR_WFS_PAGE_SIZE 5000 \
  batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Troubleshooting

- **`unable to find driver WFS`** — GDAL was built without WFS support; check with
  `ogrinfo --format WFS`. Follow the [tooling rule](../SKILL.md#tooling-rule): offer a
  suitable GDAL environment instead of switching to Python or installing packages.
- **Missing output driver** (for example Parquet) — check `ogrinfo --format Parquet`
  for vector creation support and use the [missing-driver options](formats.md#missing-gdal-or-parquet-support).
- **`Layer not found`** — the namespace prefix is missing, or the layer name changed. List
  the available layers with `ogrinfo "WFS:https://data.geopf.fr/wfs/ows"`.
- **Empty output** — the `-spat` bounding box is probably expressed in the wrong SRS; check
  the layer CRS with `ogrinfo -so -nocount -noextent "WFS:https://data.geopf.fr/wfs/ows" <typename>`.
- **Download never ends** — a nationwide layer is being fetched in full; add `-spat` or
  `-limit`.
