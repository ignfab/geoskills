---
name: gdal-vector-processing
description: Converts, reprojects, filters, clips and merges local vector data (Shapefile, GeoPackage, GeoJSON, CSV, FlatGeobuf, GeoParquet, MapInfo, KML, GPX, EDIGÉO) with the GDAL command-line tools ogrinfo and ogr2ogr or the newer gdal vector commands. Use when the user wants to convert a vector file, add a layer to a GeoPackage, reproject, filter or clip features on the command line without Python, fix garbled accents in a Shapefile, turn a CSV of coordinates into points, export a Shapefile or RFC 7946 GeoJSON, or run SQL on a vector file. For Géoplateforme WFS downloads, Python workflows or geometry repair, use geopf-wfs-download, geopandas-vector-analysis or vector-data-quality.
---

# GDAL vector processing

Process local vector files with the GDAL command-line tools:

| Tool | Use it to |
| --- | --- |
| `ogrinfo` | Inspect layers, geometry type, CRS, extent, fields and count; run read-only SQL |
| `ogr2ogr` | Convert, reproject, filter, select fields, clip, append and merge |
| `gdal vector` | The same operations as sub-commands and pipelines (GDAL ≥ 3.12, still provisional) |

## Prerequisites

- **GDAL** 3.4 or later; `ogrinfo -json` needs GDAL ≥ 3.7. Check with `ogrinfo --version`.
- Check that a driver is available before using it: `ogrinfo --formats`. GeoParquet needs a
  GDAL built with Arrow/Parquet support.
- Install: `sudo apt install gdal-bin` (Debian/Ubuntu) or
  `conda install -c conda-forge gdal libgdal-arrow-parquet`.
- If GDAL is missing, give the user the install command and let them run it; **never
  install software yourself**.

## Inspect first

Read the layer names, geometry type, feature count, extent, CRS, geometry column and
fields before choosing options. For a Shapefile, also read the encoding metadata:

```bash
ogrinfo -so -al communes.shp
ogrinfo -so -al -mdd all communes.shp | grep -i encoding
```

An empty `SOURCE_ENCODING` means that the Shapefile has no `.cpg` and no code page in its
`.dbf`: GDAL then reads the bytes without recoding. Take field names, layer names and the
geometry column (`Geometry Column = geom`) from this output, not from memory.

Write every result to a **new** path. Without `-update` or `-append`, `ogr2ogr` recreates
an existing output dataset: the other layers of a GeoPackage are lost without an error.

## Most common commands

Convert a legacy Shapefile whose accents are garbled (warnings such as
`Value of field 'nom' is not a valid UTF-8 string`). French legacy files are usually
`CP1252`:

```bash
ogr2ogr -f GPKG -oo ENCODING=CP1252 -nln communes projet.gpkg communes.shp
```

Add a layer to that GeoPackage without touching the existing one. `PROMOTE_TO_MULTI`
gives a single polygon type when the source mixes polygons and multipolygons:

```bash
ogr2ogr -update -nln parcels -nlt PROMOTE_TO_MULTI projet.gpkg parcels.geojson
```

Select features and fields with SQL. List the geometry column reported by `ogrinfo`, or the
result has no geometry; quote strings with single quotes:

```bash
ogr2ogr -nln communes \
  -sql "SELECT code_insee, nom, geom FROM communes WHERE code_insee LIKE '94%'" \
  communes_94.gpkg projet.gpkg
```

Clip to a longitude/latitude box while the data are in Lambert-93. `-spat_srs` states the
CRS of the box and `spat_extent` cuts the geometries along it:

```bash
ogr2ogr -spat 2.35975 48.82932 2.35998 48.82962 -spat_srs EPSG:4326 \
  -clipsrc spat_extent parcels_clip.gpkg projet.gpkg parcels
```

Build points from a CSV of longitudes and latitudes. Columns stay strings unless asked
otherwise, so codes keep their leading zeros:

```bash
ogr2ogr -oo X_POSSIBLE_NAMES=lon -oo Y_POSSIBLE_NAMES=lat -oo KEEP_GEOM_COLUMNS=NO \
  -a_srs EPSG:4326 -nln points points.gpkg points.csv
```

Export GeoJSON for the web. `RFC7946=YES` reprojects to WGS84 longitude/latitude and
rounds coordinates to 7 decimals:

```bash
ogr2ogr -lco RFC7946=YES parcels_web.geojson projet.gpkg parcels
```

## Rules of thumb

- `-t_srs` transforms coordinates; `-a_srs` only labels them. A file without a CRS is a
  question for the `crs-reprojection-france` skill, not a guess.
- `-spat` keeps whole features that touch the box; `-clipsrc` cuts them. A
  `-clipsrc xmin ymin xmax ymax` box is read in the **source** CRS: longitudes given to a
  Lambert-93 layer return no feature and no error. A clip dataset that declares its CRS is
  reprojected.
- Prefer GeoPackage to Shapefile. A Shapefile truncates field names to 10 characters,
  writes ISO-8859-1 by default and replaces characters such as `œ`, `’` or `–` with `?`;
  see [formats and encodings](references/formats-and-encodings.md).
- With `-dialect SQLite`, spatial functions such as `ST_Union` and `ST_Area` are available;
  use the geometry column name reported by `ogrinfo`.
- Show progress on long conversions with `-progress`; keep them in the foreground and do
  not pipe them through `head` or `tail`.

## Validate the output

Reopen the output and compare it with the inspection of the source:

```bash
ogrinfo -so -al projet.gpkg
```

- The feature count equals the source count, or the count expected after the filter or
  clip; every layer that should remain in the GeoPackage is still listed.
- The geometry type, `ID["EPSG",…]` and extent match the request. In Lambert-93, a
  metropolitan extent lies roughly between X 100 000–1 250 000 m and Y 6 000 000–7 200 000 m;
  an extent of a few units means degrees were written as metres.
- Field names and types are the expected ones: codes stay strings with their leading zeros,
  and no name was truncated without a reported mapping.
- Conversion warnings were read: invalid UTF-8, laundered field names, or a geometry type
  not allowed by the GeoPackage specification.
- Accented text is intact. This check counts replacement and control characters:

```bash
ogr2ogr -f CSV /vsistdout/ projet.gpkg communes | python3 -c '
import sys, unicodedata
text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
bad = [c for c in text if c == "\ufffd" or (unicodedata.category(c) == "Cc" and c not in "\r\n\t")]
print("suspicious characters:", len(bad))
sys.exit(1 if bad else 0)'
```

For a clip, also compare areas with
`ogrinfo -dialect SQLite -sql "SELECT count(*), sum(ST_Area(geom)) FROM parcels" parcels_clip.gpkg`.

## Report the result

Report the source path and layer, the output path, format, layer names, CRS, extent and
feature count, the options used (encoding, filters, clip, type promotion) and the checks
performed. List truncated or renamed fields and any warning left unresolved; keep an
unknown encoding or CRS explicit rather than guessed.

## References

- [references/formats-and-encodings.md](references/formats-and-encodings.md) — choosing an
  output format, Shapefile limits, text encodings, geometry types, CSV, GPX, KML, MapInfo
  and EDIGÉO.
- [references/filters-sql-and-merge.md](references/filters-sql-and-merge.md) — attribute and
  spatial filters, clipping, SQL dialects, dissolve, merging files and splitting layers.
- [references/gdal-vector-cli.md](references/gdal-vector-cli.md) — the `gdal vector`
  commands and pipelines of GDAL ≥ 3.12.

Related skills: `geopf-wfs-download` for Géoplateforme WFS layers, `geopandas-vector-analysis` for
Python workflows, `crs-reprojection-france` for CRS choice and missing `.prj` files,
`vector-data-quality` for invalid geometries, `mapshaper-simplify` for simplification and
`geodata-intake` for a read-only inventory of an unknown delivery.

## Additional resources

- ogr2ogr: <https://gdal.org/programs/ogr2ogr.html>
- ogrinfo: <https://gdal.org/programs/ogrinfo.html>
- Vector drivers: <https://gdal.org/drivers/vector/index.html>
