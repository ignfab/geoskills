# gdal-vector-processing

**Family:** [3. Prepare and check](../README.md).

Convert, reproject, filter, clip and merge local vector files (Shapefile, GeoPackage,
GeoJSON, CSV, FlatGeobuf, GeoParquet, MapInfo, KML, GPX, EDIGÉO) with the GDAL
command-line tools `ogrinfo` and `ogr2ogr`, or the newer `gdal vector` commands. The skill
covers the traps met with French data: legacy Shapefiles without `.cpg`, field names cut
to 10 characters, GeoPackage layers lost when rewriting a file, and clip boxes given in
the wrong CRS.

To download vector layers from the Géoplateforme, see
[geopf-wfs-download](../../2-access/geopf-wfs-download/README.md); for Python workflows,
[geopandas-vector-analysis](../../4-analyze/geopandas-vector-analysis/README.md).

## Requirements

GDAL 3.4 or later (`sudo apt install gdal-bin`, or
`conda install -c conda-forge gdal libgdal-arrow-parquet`). `ogrinfo -json` needs
GDAL ≥ 3.7, and the optional `gdal vector` commands GDAL ≥ 3.12. GeoParquet needs a GDAL
built with Arrow/Parquet support. The user installs missing software; the agent does not.

## Installation

```bash
npx skills add ignfab/geoskills --skill gdal-vector-processing
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Inspection, the commands covering most needs, validation and report. |
| [references/formats-and-encodings.md](references/formats-and-encodings.md) | Output formats, Shapefile limits, text encodings, geometry types, CSV, GPX, KML, MapInfo, EDIGÉO. |
| [references/filters-sql-and-merge.md](references/filters-sql-and-merge.md) | Attribute and spatial filters, clipping, SQL dialects, dissolve, merging and splitting. |
| [references/gdal-vector-cli.md](references/gdal-vector-cli.md) | The provisional `gdal vector` commands and pipelines (GDAL ≥ 3.12). |

## Example

```bash
ogr2ogr -f GPKG -oo ENCODING=CP1252 -t_srs EPSG:2154 -nln communes communes.gpkg communes.shp
ogrinfo -so -al communes.gpkg
```
