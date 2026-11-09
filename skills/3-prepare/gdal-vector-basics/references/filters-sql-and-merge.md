# Filters, SQL and merging

The examples continue from `SKILL.md`: `projet.gpkg` holds a `communes` point layer and a
`parcels` polygon layer in Lambert-93. Behaviors were checked with GDAL 3.8 and 3.13 on
2026-10-29.

## Attribute filters

- `-where` takes a SQL condition. Quote strings with single quotes and double an apostrophe
  inside them: `-where "nom = 'L''Haÿ-les-Roses'"`. Quote unusual field names with double
  quotes.
- The SQL engine depends on the source. On a GeoPackage, `LIKE 'saint%'` matches
  `Saint-Mandé` (SQLite ignores the case of ASCII letters); on a Shapefile, the OGR SQL
  `LIKE` respects case. `ILIKE` ignores case on both.
- `-select code_insee,nom` keeps the geometry and the listed fields, in this order.
- With GDAL 3.13.0 to 3.13.3, `-where` combined with `-select` on a GeoPackage source
  ignored `-select` and kept every field; GDAL 3.8 and 3.10 did not. Check the fields of
  the output; `--config OGR2OGR_USE_ARROW_API NO` or a `-sql` selection avoids it.
- `-fid 3` reads one feature by its identifier; use it to inspect, not to filter a batch.

## Spatial filters and clipping

| Option | Keeps | Coordinates of the box or shape |
| --- | --- | --- |
| `-spat xmin ymin xmax ymax` | Whole features whose envelope touches the box | Layer CRS, or `-spat_srs` |
| `-clipsrc xmin ymin xmax ymax` | Features cut along the box | **Source** CRS, no `-spat_srs` |
| `-clipsrc spat_extent` | Features cut along the `-spat` box | As given to `-spat` / `-spat_srs` |
| `-clipsrc zone.gpkg` | Features cut along the polygons of a dataset | Reprojected when the dataset declares a CRS |
| `-clipdst …` | Features cut after reprojection | Target CRS |

Cut the parcels along a polygon stored in WGS84:

```bash
ogr2ogr -clipsrc zone.geojson parcels_zone_clip.gpkg projet.gpkg parcels
```

Use `-clipsrclayer` and `-clipsrcwhere` to choose the clip layer and features in a
multi-layer dataset. Clipping cuts geometries: report the area before and after, and
expect `-nlt PROMOTE_TO_MULTI` to be needed when a cut splits a polygon.

To keep **whole** features that intersect a polygon, put the polygon in the same
GeoPackage and select with SQLite. Take both geometry column names from `ogrinfo`:

```bash
ogr2ogr -update -nln zone -t_srs EPSG:2154 projet.gpkg zone.geojson
ogr2ogr -nln parcels_zone -dialect SQLite \
  -sql "SELECT p.* FROM parcels p, zone z WHERE ST_Intersects(p.geom, z.geom)" \
  parcels_zone.gpkg projet.gpkg
```

## SQL dialects

- Without `-dialect`, a GeoPackage, PostGIS or SQLite source runs its own SQL; other
  formats use OGR SQL, which has no spatial functions.
- `-dialect SQLite` runs SQLite on any source and adds SpatiaLite functions (`ST_Union`,
  `ST_Area`, `ST_Intersects`, `ST_Buffer`) when GDAL is built with SpatiaLite. If a
  function is reported as unknown, the build lacks SpatiaLite: use GeoPandas instead.
- Areas and lengths are in the units of the layer CRS: compute them in Lambert-93 or another
  projected CRS, never in degrees.
- Name the geometry column of a SQL result with an alias, and add `-nln` to name the output
  layer.

Dissolve features with `ST_Union`; add a `GROUP BY` on an attribute to dissolve per value.
The union area is smaller than the sum of the areas when features overlap:

```bash
ogr2ogr -nln dissolved -nlt PROMOTE_TO_MULTI -dialect SQLite \
  -sql "SELECT count(*) AS n, ST_Union(geom) AS geom FROM parcels" \
  dissolved.gpkg projet.gpkg
```

## Merge files

Append files with the same schema into one layer. `-append` creates the output on the
first call; `-addfields` adds fields missing from the first file:

```bash
for f in sheets/*.gpkg; do
  ogr2ogr -update -append -addfields -nln parcels merged.gpkg "$f" parcels
done
```

Record the number of input files and compare the merged count with the sum of the input
counts. Add a source column when the user needs to trace each feature:

```bash
ogr2ogr -update -append -nln parcels_traced \
  -sql "SELECT *, 'sheet_1' AS source FROM parcels" merged_traced.gpkg sheets/sheet_1.gpkg
```

With GDAL ≥ 3.12, `gdal vector concat` does both in one command; see
[the gdal vector commands](gdal-vector-cli.md).

## Split a layer

List the distinct values first, then write one file per value with `-where`. With
GDAL ≥ 3.12, `gdal vector partition --field` writes the files directly.

```bash
ogr2ogr -f CSV /vsistdout/ -sql "SELECT DISTINCT code_insee FROM communes" projet.gpkg
```

## Large files and archives

- Add `-progress` and keep the command in the foreground.
- For large GeoPackage writes, `-gt 65536` groups features into fewer transactions.
- Read inside a ZIP archive without extracting it: `ogrinfo -so /vsizip/archive.zip/communes.shp`.
  Check the archive listing first (`unzip -l`); see the `geopf-download-files` skill for
  IGN archives.
