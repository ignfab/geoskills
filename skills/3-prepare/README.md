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
