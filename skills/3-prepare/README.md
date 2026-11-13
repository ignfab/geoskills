# 3. Prepare and check

**Question:** is the data usable and compatible?

Inspect what was received, settle the CRS, convert formats and encodings, and audit
geometry quality, so that the next step works on consistent inputs.

| Skill | Use it to |
| --- | --- |
| [geodata-intake](geodata-intake/README.md) | Read-only inventory of formats, layers, metadata and missing CRS evidence. |
| [crs-reprojection-france](crs-reprojection-france/README.md) | French CRS (Lambert-93, CC zones, NTF, overseas territories): EPSG codes, reprojection and pitfalls. |
| [gdal-vector-processing](gdal-vector-processing/README.md) | Convert, reproject, filter, clip and merge vector files with `ogr2ogr` and `gdal vector`, including legacy Shapefile encodings and GeoPackage layers. |
| [gdal-raster-processing](gdal-raster-processing/README.md) | Clip, reproject, mosaic and convert rasters with GDAL; check coverage, grids and COG structure, and compute zonal statistics. |
| [vector-data-quality](vector-data-quality/README.md) | Audit and repair invalid, empty or duplicate vector features, and gaps or overlaps between polygons, before analysis or publication. |

## Choose between them

- Start with `geodata-intake` when you do not yet know what a delivery contains: it
  inventories files, layers and missing metadata without modifying anything, before you
  choose the next step.
- CRS questions (which EPSG code, a missing or wrong projection, GPS coordinates to
  Lambert-93, heights): `crs-reprojection-france`.
- Command-line work on vector files (convert, reproject, filter, clip, merge, fix encodings,
  run SQL): `gdal-vector-processing`.
- Rasters (clip, reproject, resample, mosaic, COG, zonal statistics): `gdal-raster-processing`.
- Geometry and attribute quality (invalid geometries, gaps and overlaps, duplicates):
  `vector-data-quality`. The audit comes first; repair is a deliberate, reported step.

## What they need

Reuse existing tools and choose the route for the requested operation. Installing this
family does not require all routes; see the [dependency guide](../../docs/dependencies.md).

| Skill | Base route | Conditional additions | Network |
| --- | --- | --- | --- |
| `geodata-intake` | GDAL CLI for vector/raster metadata; standard-library Python for CSV/JSON | Reader matching any archive that must be opened; CSV-only inspection needs no GDAL | None |
| `crs-reprojection-france` | GDAL for files, PROJ CLI or pyproj for point coordinates | Only the selected transformation's missing grids; operation inspection with projinfo or pyproj | Only to fetch a required missing grid |
| `gdal-vector-processing` | GDAL native CLI and the requested vector drivers | Arrow/Parquet plugin only for GeoParquet; newer versions only for chosen commands | None |
| `gdal-raster-processing` | GDAL CLI and requested raster drivers | Matching Python bindings for Python utilities/full COG validation; newer GDAL for zonal stats | None, except for remote rasters |
| `vector-data-quality` | GeoPandas/Shapely or the relevant GDAL CLI recipe | Higher GeoPandas/Shapely versions only for coverage/advanced repair; no need for both routes | None |

## Also relevant

- [terrain-elevation-screening](../6-workflows/terrain-elevation-screening/README.md)
  prepares a common terrain grid before altitude/slope screening and polygon delivery.
- [geopf-geocoding](../2-access/geopf-geocoding/README.md) reviews an already geocoded CSV
  (scores, ambiguity, unmatched rows) without sending new requests.
- [geopandas-vector-analysis](../4-analyze/geopandas-vector-analysis/README.md) reads, writes and reprojects
  vector data in Python scripts.

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/3-prepare
```

Previous: [2. Access and extract](../2-access/README.md) ·
Next: [4. Analyze and derive](../4-analyze/README.md) · [All families](../../README.md#skills)
