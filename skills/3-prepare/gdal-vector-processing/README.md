# gdal-vector-processing

**Family:** [3. Prepare and check](../README.md).

Convert, reproject, filter, clip and merge local vector files (Shapefile, GeoPackage,
GeoJSON, CSV, FlatGeobuf, GeoParquet, MapInfo, KML, GPX, EDIGÉO) with the GDAL
command-line tools `ogrinfo` and `ogr2ogr`, or the newer `gdal vector` commands. The skill
covers the traps met with French data: legacy Shapefiles without `.cpg`, field names cut
to 10 characters, GeoPackage layers lost when rewriting a file, and clip boxes given in
the wrong CRS.

## When to use it

- Convert a legacy Shapefile without `.cpg` to a GeoPackage while keeping accented names
  readable.
- Add a layer to an existing GeoPackage without losing the layers already in it.
- Clip features with a longitude/latitude box while the data are in Lambert-93, and compare
  areas before and after the clip.
- Export a Shapefile for legacy software, with an explicit encoding and a field-name
  mapping, or RFC 7946 GeoJSON for the web.
- Turn a CSV of coordinates into points, keeping codes as strings with their leading zeros.
- Select features and fields with SQL, dissolve, merge files or split a layer on the
  command line, without Python.

## When to use another skill

- Downloading layers from the Géoplateforme WFS:
  [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md).
- Python workflows, for example an area computed in a GeoDataFrame:
  [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md).
- Repairing invalid geometries: [`vector-data-quality`](../vector-data-quality/README.md).
- Choosing a CRS, or a file without a CRS or `.prj`, which must not be guessed:
  [`crs-reprojection-france`](../crs-reprojection-france/README.md).
- Simplifying geometries: [`mapshaper-simplify`](../../5-publish/mapshaper-simplify/README.md).
- A read-only inventory of an unknown delivery: [`geodata-intake`](../geodata-intake/README.md).

## What you get

- A result written to a **new** path, in the requested format; layers are added to an
  existing GeoPackage with `-update`, because a plain `ogr2ogr` recreates the file.
- Before reporting, the agent reopens the output with `ogrinfo -so -al` and checks:
  - the feature count against the source, or against the count expected after the filter
    or clip, and that every layer that should remain in the GeoPackage is listed;
  - the geometry type, `ID["EPSG",…]` and extent (an extent of a few units in Lambert-93
    means degrees were written as meters);
  - field names and types: codes stay strings with their leading zeros, and no name is
    truncated without a reported mapping;
  - conversion warnings (invalid UTF-8, laundered field names, geometry types not allowed by
    the GeoPackage specification) and accented text, by counting replacement and control
    characters;
  - for a clip, areas computed with SQLite SQL.
- A report with the source path and layer, output path, format, layer names, CRS, extent,
  feature count, options used (encoding, filters, clip, type promotion) and checks
  performed. Truncated or renamed fields and unresolved warnings are listed; an unknown
  encoding or CRS stays explicit rather than guessed.

## Requirements

GDAL 3.4 or later (`sudo apt install gdal-bin`, or
`conda install -c conda-forge gdal libgdal-arrow-parquet`). `ogrinfo -json` needs
GDAL ≥ 3.7, and the optional `gdal vector` commands GDAL ≥ 3.12. GeoParquet needs a GDAL
built with Arrow/Parquet support. Check with `ogrinfo --version` and `ogrinfo --formats`.
The user installs missing software; the agent does not.

With GDAL 3.13.0 to 3.13.3, `-where` combined with `-select` on a GeoPackage source keeps
every field: check the fields of the output. The skill works on local files and needs no
network service or API key.

## Installation

```bash
npx skills add ignfab/geoskills --skill gdal-vector-processing
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/3-prepare`.

## Example

> Convert `data/communes_sans_cpg/communes.shp` to a GeoPackage in `output/communes.gpkg`.
> The municipality names and the remarks must display correctly.

```bash
ogr2ogr -f GPKG -oo ENCODING=CP1252 -t_srs EPSG:2154 -nln communes communes.gpkg communes.shp
ogrinfo -so -al communes.gpkg
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Inspection, the commands covering most needs, validation and report. |
| [references/formats-and-encodings.md](references/formats-and-encodings.md) | Output formats, Shapefile limits, text encodings, geometry types, CSV, GPX, KML, MapInfo, EDIGÉO. |
| [references/filters-sql-and-merge.md](references/filters-sql-and-merge.md) | Attribute and spatial filters, clipping, SQL dialects, dissolve, merging and splitting. |
| [references/gdal-vector-cli.md](references/gdal-vector-cli.md) | The provisional `gdal vector` commands and pipelines (GDAL ≥ 3.12). |

## Tests

- Agent scenarios: [tests/gdal-vector-processing.md](../../../tests/gdal-vector-processing.md), in
  French (4 positive, 2 negative).
- Offline: [test_gdal_vector.py](../../../tests/test_gdal_vector.py) runs the `ogr2ogr`
  recipes (encoding, GeoPackage layers, clipping, CSV, RFC 7946, SQL, merge and split) and
  the `gdal vector` examples on GDAL ≥ 3.12. No live test.

## Related skills

- [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md) downloads the
  Géoplateforme layers that this skill then filters, clips and converts locally.
- [`crs-reprojection-france`](../crs-reprojection-france/README.md) settles the source and
  target CRS before a reprojection.
- [`vector-data-quality`](../vector-data-quality/README.md) audits and repairs the
  geometries of a converted layer.
- [`mapshaper-simplify`](../../5-publish/mapshaper-simplify/README.md) produces lighter
  boundaries for publication.
