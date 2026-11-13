# 4. Analyze and derive

**Question:** what information should be computed?

Derive new information from prepared data: attribute summaries, territorial indicators,
spatial joins and overlays, buffers and zonal statistics, elevations and profiles,
routes and reachable areas. The Géoplateforme calculation services (elevation, routing)
sit here because they produce derived values,
not a subset of an existing dataset.

| Skill | Use it to |
| --- | --- |
| [geopandas-vector-analysis](geopandas-vector-analysis/README.md) | Process vector data in Python with GeoPandas: I/O, reprojection, spatial joins, overlay, buffers, zonal statistics. |
| [geopf-altimetry](geopf-altimetry/README.md) | Discover terrain/surface resources, preserve missing elevations, join CSV rows and sample profiles. |
| [geopf-routing](geopf-routing/README.md) | Discover navigation resources, choose units/direction and export route or isochrone geometry. |
| [geospatial-descriptive-statistics](geospatial-descriptive-statistics/README.md) | Summarize numeric attributes, categories and missingness in one layer with explicit units and statistical conventions. |
| [spatial-aggregation](spatial-aggregation/README.md) | Compute vector object-to-zone counts, sums, means and ratios with explicit border/overlap policies and audited totals. |

## Choose between them

- Statistics on one layer's attributes, without spatial matching:
  `geospatial-descriptive-statistics`.
- Indicators per zone (counts, sums, means or ratios of objects in polygons):
  `spatial-aggregation`.
- General vector operations in Python (joins, overlays, buffers, dissolve, clip):
  `geopandas-vector-analysis`.
- Raster values summarized per polygon: zonal statistics with `gdal-raster-processing`, in
  [3. Prepare and check](../3-prepare/README.md).
- Elevations at points or along a line from the IGN service: `geopf-altimetry`; a full DEM
  is processed with `gdal-raster-processing`.
- Routes and reachable areas on the IGN road network: `geopf-routing`; straight-line
  buffers stay with `geopandas-vector-analysis`.

## What they need

Choose the service, tabular or spatial route; these do not require a combined environment.
Reuse installed packages; see the [dependency guide](../../docs/dependencies.md).

| Skill | Base route | Conditional additions | Network |
| --- | --- | --- | --- |
| `geopandas-vector-analysis` | GeoPandas with Pyogrio and pyproj for vectors | PyArrow for GeoParquet; rasterstats for raster zonal statistics | None, except to read WFS data |
| `geopf-altimetry` | curl and Python 3 standard library | Existing GDAL/PROJ or pyproj only for input reprojection | Géoplateforme Elevation API |
| `geopf-routing` | curl and Python 3 standard library for API responses | Either GDAL or GeoPandas for final spatial validation and metric checks | Géoplateforme Navigation API |
| `geospatial-descriptive-statistics` | Pandas for CSV summaries | GeoPandas/Shapely for vector inputs and geometry measurements | None |
| `spatial-aggregation` | GeoPandas with its vector I/O and geometry dependencies | No plotting, raster or QGIS packages for the analytic outputs | None |

## Also relevant

- [terrain-elevation-screening](../6-workflows/terrain-elevation-screening/README.md)
  chains DEM acquisition, altitude/slope filtering and candidate-area delivery over an AOI.
- [municipality-building-profile](../6-workflows/municipality-building-profile/README.md)
  combines source interpretation, analysis and optional QGIS delivery for one municipality.
- [bdtopo-schema-guide](../1-discover/bdtopo-schema-guide/README.md) explains source-specific
  special values before BD TOPO statistics.
- [gdal-raster-processing](../3-prepare/gdal-raster-processing/README.md) computes zonal
  statistics with `gdal raster zonal-stats` and terrain one-liners (hillshade, slope) with
  `gdaldem`.
- [apicarto-query](../2-access/apicarto-query/README.md) intersects a point or an area with parcels,
  urban-planning zones, easements and protected areas on the server.
- [gdal-vector-processing](../3-prepare/gdal-vector-processing/README.md) dissolves features and
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
