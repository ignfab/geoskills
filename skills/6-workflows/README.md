# 6. Solve a business need

**Question:** how do I chain the steps to reach an objective?

A skill in this family chains acquisition, preparation, analysis and delivery to answer a
business question. It defines the shared method and checks across those stages; specialized
skills remain independently useful for narrower requests.

| Skill | Use it to |
| --- | --- |
| [terrain-elevation-screening](terrain-elevation-screening/README.md) | Filter terrain over an area by altitude, optional slope and connected area, with candidate polygons and explicit coverage; supports preliminary helicopter terrain screening without validating landing suitability. |
| [municipality-building-profile](municipality-building-profile/README.md) | Produce one municipality's building counts, union footprint coverage, height/usage summaries and optional portable QGIS delivery, with explicit source and boundary rules. |

## Choose between them

- Use `municipality-building-profile` for the full building portrait of one municipality.
  It fixes which buildings are counted, how the built area is measured and which heights
  and usages can be summarized, so that its numbers can be reconciled.
- Use `terrain-elevation-screening` to filter an area of interest by altitude, optionally
  slope and connected area, from DEM discovery to candidate polygons and a coverage report.
  A DEM filter never establishes that a site is safe or suitable for a helicopter landing.
- For a single step, use the building block directly: a download (`geopf-wfs-download`),
  statistics on one table (`geospatial-descriptive-statistics`), indicators for several
  zones (`spatial-aggregation`) or project assembly (`qgis-project-builder`); elevations
  at a few points (`geopf-altimetry`) or DEM clipping alone (`gdal-raster-processing`).

## What they need

Check only the workflow stages that will run; referenced skills are not a requirement to
install their entire families. See the [dependency guide](../../docs/dependencies.md).

| Skill | Base route | Conditional additions | Network |
| --- | --- | --- | --- |
| `municipality-building-profile` | GeoPandas ≥ 1.0 with Shapely/Pyogrio for the analytic bundle | GDAL + curl for online extraction; existing QGIS/PyQGIS only for a requested project | Géoplateforme WFS, only when data is extracted online |
| `terrain-elevation-screening` | GDAL ≥ 3.3, matching Python bindings/utilities and NumPy | curl for online acquisition; existing QGIS/PyQGIS only for a requested map/project | Géoplateforme services, only when the DEM is discovered online |

Local inputs avoid acquisition dependencies. Missing optional QGIS leaves the analytic
bundle usable; report the requested cartographic delivery as outstanding if it cannot run.

**Optional MCP server.** With [Geocontext](https://github.com/ignfab/geocontext)
connected, both workflows use it first to identify the municipality when it is named, and
the building portrait also uses it to find the layer and to cross-check its count. See
[MCP servers](../../docs/mcp-servers.md).

## Further workflow candidates

| Use case | Building blocks available today |
| --- | --- |
| Territorial diagnosis | `geopf-wfs-download` (boundaries, BD TOPO), `apicarto-query` (urban planning, protected areas), `geopf-altimetry`, `geopandas-vector-analysis` (overlays), `spatial-aggregation` (territorial indicators), `geospatial-descriptive-statistics` (attribute distributions) |
| Accessibility | `geopf-geocoding` (starting points), `geopf-routing` (isochrones), `geopandas-vector-analysis` (overlay with the area of interest) |
| Exposure | `geopf-geocoding`, `apicarto-query` (zones, easements, protected areas), `geopandas-vector-analysis` (spatial joins) |
| Change monitoring | `geopf-file-download` (editions), `vector-data-quality`, `geopandas-vector-analysis` (comparison) |

These broader chains are explored with the business-need prompts of the
[experimental prompt catalog](../../tests/prompts/catalog.md); their runs are logged in
[runs.md](../../tests/prompts/runs.md). One documented chain is in
[mapshaper-simplify](../5-publish/mapshaper-simplify/README.md): download boundaries with
`geopf-wfs-download`, audit them with `vector-data-quality`, then simplify them.

## Also relevant

- [map-illustration](../5-publish/map-illustration/README.md) turns existing workflow
  outputs into report images or small interactive maps, with QGIS optional.
- [bdtopo-schema-guide](../1-discover/bdtopo-schema-guide/README.md) resolves building/road
  concepts and special values before data extraction or statistics.
- [spatial-aggregation](../4-analyze/spatial-aggregation/README.md) produces reconciled
  territorial indicators from vector objects and zones.
- [geospatial-descriptive-statistics](../4-analyze/geospatial-descriptive-statistics/README.md)
  describes one layer's attributes without spatial matching.
- [qgis-layer-styling](../5-publish/qgis-layer-styling/README.md) creates reusable QML;
  [qgis-project-builder](../5-publish/qgis-project-builder/README.md) packages existing
  results into a verified QGIS project.

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/6-workflows
```

Previous: [5. Represent and publish](../5-publish/README.md) · [All families](../../README.md#skills)
