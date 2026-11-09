# Formats and encodings

Behaviors below were checked with GDAL 3.8 and 3.13 on 2026-10-29; the Shapefile encoding
behavior also with GDAL 3.7 and 3.10. Check `ogrinfo --formats` before relying on a driver.

## Choose an output format

| Format | Use it for | Limits |
| --- | --- | --- |
| GeoPackage (`GPKG`) | Default exchange and working format | One file holds several layers; rewriting without `-update` replaces them all |
| Shapefile | Software that reads nothing else | See [Shapefile limits](#shapefile-limits) |
| GeoJSON | Small layers for the web or an API | One layer; with `RFC7946=YES`, WGS84 longitude/latitude only |
| GeoJSON Sequence (`GeoJSONSeq`) | Streaming one feature per line | No layer-level metadata |
| FlatGeobuf | Large single layers read by extent | One layer per file |
| GeoParquet (`Parquet`) | Columnar analysis, cloud storage | Needs a GDAL with Arrow/Parquet support |
| CSV | Tables with X/Y or WKT columns | No CRS stored; state it in the report |
| KML | Google Earth | Written in WGS84 longitude/latitude |
| GPX | GPS devices | WGS84 only; fixed schema, see [GPX](#gpx-and-kml) |
| MapInfo (`MapInfo File`) | MapInfo users (`.tab` or `.mif`/`.mid`) | Field and style limits of MapInfo |

## Shapefile limits

- Field names are cut to 10 characters. GDAL warns
  `Normalized/laundered field name: 'nom_officiel' to 'nom_offici'`, and colliding names
  become meaningless (`nom_officiel_en_majuscules` → `nom_offi_1`).
- Strings are limited to 254 bytes, dates lose their time, and each `.shp` or `.dbf` file
  is limited to 2 GB.
- One file holds one layer and one geometry family; a `Polygon` Shapefile can contain
  multipolygons.
- By default GDAL writes ISO-8859-1 without a `.cpg`. Characters outside ISO-8859-1, such
  as `œ`, `’` or `–`, become `?`, with a single warning:
  `One or several characters couldn't be converted correctly from UTF-8 to ISO-8859-1`.

Export with explicit short names and a `.cpg`. Writing to a directory name creates it and
names the files after `-nln`:

```bash
ogr2ogr -f "ESRI Shapefile" -lco ENCODING=UTF-8 -nln communes \
  -sql "SELECT code_insee, nom_officiel AS nom, nom_officiel_en_majuscules AS nom_maj, remarque FROM communes_points" \
  export communes_points.geojson
```

Report the field mapping (`nom_officiel` → `nom`, `nom_officiel_en_majuscules` →
`nom_maj`). Use `-lco ENCODING=CP1252` instead only for software that cannot read UTF-8:
it keeps `œ`, `’` and `–`, but not characters outside CP1252.

## Fix the text encoding on read

GDAL decodes a Shapefile `.dbf` with its `.cpg` file or with the code page byte of the
`.dbf`. When neither exists, `SOURCE_ENCODING` is empty and GDAL passes the bytes through:
UTF-8 files read correctly, legacy Windows files show `Saint-Mand�`. Writing them then
produces invalid UTF-8 with the warning `Value of field 'nom' is not a valid UTF-8 string`
and exit status 0.

Inspect `ogrinfo -so -al -mdd all input.shp | grep -i encoding` and the warnings, then
read with an explicit encoding. French legacy files are usually `CP1252`; prefer it to
`ISO-8859-1`, which silently turns `œ`, `’` and `–` into control characters:

```bash
ogr2ogr -f GPKG -oo ENCODING=CP1252 -nln communes communes.gpkg communes.shp
```

- If the text shows `Ã©` instead of `é`, the file is UTF-8 read as a single-byte encoding:
  use `-oo ENCODING=UTF-8`.
- A `.cpg` that contradicts the content is overridden by `-oo ENCODING`.
- Run the suspicious-character check from `SKILL.md` on the output and record the
  encoding chosen.

`--config SHAPE_ENCODING CP1252` applies the same choice to every Shapefile of a command.

## Geometry types

- `-nlt PROMOTE_TO_MULTI` writes a single multi type. Without it, polygons and
  multipolygons from a Shapefile go into a GeoPackage `Polygon` layer with the warning
  `not normally allowed by the GeoPackage specification`, and mixed GeoJSON becomes a layer
  of type `Unknown (any)`.
- `-explodecollections` writes one feature per part: the count grows, so report it. Combine
  it with `-nlt POLYGON` (or the matching single type) to get a typed layer.
- `-dim XY` drops Z values, for example from BD TOPO buildings; keep them unless the target
  cannot store them.
- `-makevalid` exists, but invalid geometries need the audit of the `vector-data-quality`
  skill before any repair.

## CSV

Reading:

- `-oo X_POSSIBLE_NAMES=lon -oo Y_POSSIBLE_NAMES=lat` builds points from coordinate
  columns; `-oo GEOM_POSSIBLE_NAMES=wkt` reads a WKT column. Assign the CRS with `-a_srs`
  after checking the column order and magnitudes.
- Columns are strings by default. `-oo AUTODETECT_TYPE=YES` infers types but keeps values
  with leading zeros, such as `01053`, as strings. A `.csvt` file next to the CSV fixes the
  types explicitly (`"String","Real","Real"`).
- A CSV opened and saved in a spreadsheet may already have lost leading zeros or changed
  decimal separators; check a few values against the source.

Writing: `-lco GEOMETRY=AS_XY` adds `X` and `Y` columns, `-lco GEOMETRY=AS_WKT` a WKT
column. The CSV keeps no CRS.

## GPX and KML

- A GPX file has five layers: `waypoints`, `routes`, `tracks`, `route_points` and
  `track_points`. Name the one to convert: `ogr2ogr -f GPKG trace.gpkg trace.gpx tracks`.
- Writing GPX needs WGS84 (`-t_srs EPSG:4326`) and, for fields outside the GPX schema,
  `-dsco GPX_USE_EXTENSIONS=YES`. Without it, the conversion stops with
  `Field of name 'code_insee' is not supported in GPX schema`. Read back, extension fields
  are prefixed with `ogr_` and typed again: `02201` becomes the integer `2201`.
- The KML driver writes WGS84 longitude/latitude whatever the source CRS.

## MapInfo

Open the `.tab` file (with its `.dat`, `.map` and `.id`) or the `.mif` file (with its
`.mid`). The charset is declared in the file header; check accented values after
conversion as for a Shapefile. Write MIF/MID with `-f "MapInfo File" -dsco FORMAT=MIF`.

## EDIGÉO cadastre

EDIGÉO is the exchange format of the French cadastral plan (PCI). GDAL reads it but cannot
write it.

- Open the `.THF` file. GDAL reads the `.DIC`, `.GEO`, `.SCD`, `.QAL` and `.VEC` files next
  to it.
- An exchange usually covers one cadastral sheet. Convert each sheet, then merge them with
  `-append` (see [filters, SQL and merging](filters-sql-and-merge.md)).
- The layer CRS comes from IGNF definitions; check it in `ogrinfo` before reprojecting.
- Label layers are named `xxx_LABEL`; disable them with
  `--config OGR_EDIGEO_CREATE_LABEL_LAYERS NO`.
- The whole exchange is parsed in memory.

For whole municipalities, IGN's Parcellaire Express in GeoPackage or Shapefile is often
simpler. It is available from the `geopf-download-files` skill; for parcels around a point
or in a small area, use the `apicarto` skill.

Driver reference: <https://gdal.org/drivers/vector/edigeo.html>
