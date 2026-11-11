# 4. Analyze and derive

**Question:** what information should be computed?

Derive new information from prepared data: spatial joins and overlays, buffers and zonal
statistics, elevations and profiles, routes and reachable areas. The Géoplateforme
calculation services (elevation, routing) sit here because they produce derived values,
not a subset of an existing dataset.

| Skill | Use it to |
| --- | --- |
| [geopandas-basics](geopandas-basics/README.md) | Process vector data in Python with GeoPandas: I/O, reprojection, spatial joins, overlay, buffers, zonal statistics. |
| [geopf-altimetry](geopf-altimetry/README.md) | Discover terrain/surface resources, preserve missing elevations, join CSV rows and sample profiles. |
| [geopf-routing](geopf-routing/README.md) | Discover navigation resources, choose units/direction and export route or isochrone geometry. |
| [geospatial-descriptive-statistics](geospatial-descriptive-statistics/README.md) | Summarize numeric attributes, categories and missingness in one layer with explicit units and statistical conventions. |
| [spatial-aggregation](spatial-aggregation/README.md) | Compute vector object-to-zone counts, sums, means and ratios with explicit border/overlap policies and audited totals. |

## Also relevant

- [gdal-raster-basics](../3-prepare/gdal-raster-basics/README.md) computes zonal
  statistics with `gdal raster zonal-stats` and terrain one-liners (hillshade, slope) with
  `gdaldem`.
- [apicarto](../2-access/apicarto/README.md) intersects a point or an area with parcels,
  urban-planning zones, easements and protected areas on the server.
- [gdal-vector-basics](../3-prepare/gdal-vector-basics/README.md) dissolves features and
  computes areas with SQL on the command line.

## Not covered yet

- Change detection between two editions of a dataset.
- Network analysis on local data: `geopf-routing` relies on the IGN service only.
- Terrain derivatives beyond the `gdaldem` one-liners.

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/4-analyze
```

Previous: [3. Prepare and check](../3-prepare/README.md) ·
Next: [5. Represent and publish](../5-publish/README.md) · [All families](../../README.md#skills)
