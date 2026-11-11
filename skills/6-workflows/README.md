# 6. Solve a business need

**Question:** how do I chain the steps to reach an objective?

A skill in this family will chain skills from the other families to answer a business
question end to end. None exists yet. A workflow skill is written only once its chain works
reliably with the skills it depends on.

| Use case | Building blocks available today |
| --- | --- |
| Territorial diagnosis | `geopf-wfs-download` (boundaries, BD TOPO), `apicarto` (urban planning, protected areas), `geopf-altimetry`, `geopandas-basics` (overlays), `spatial-aggregation` (territorial indicators), `geospatial-descriptive-statistics` (attribute distributions) |
| Accessibility | `geopf-geocoding` (starting points), `geopf-routing` (isochrones), `geopandas-basics` (overlay with the area of interest) |
| Exposure | `geopf-geocoding`, `apicarto` (zones, easements, protected areas), `geopandas-basics` (spatial joins) |
| Change monitoring | `geopf-download-files` (editions), `vector-data-quality`, `geopandas-basics` (comparison) |

These chains are explored first with the business-need prompts of the
[experimental prompt catalog](../../tests/prompts/catalog.md); their runs are logged in
[runs.md](../../tests/prompts/runs.md). The only chain documented so far is in
[mapshaper-simplify](../5-publish/mapshaper-simplify/README.md): download boundaries with
`geopf-wfs-download`, audit them with `vector-data-quality`, then simplify them.

## Also relevant

- [bdtopo-schema-guide](../1-discover/bdtopo-schema-guide/README.md) resolves building/road
  concepts and special values before data extraction or statistics.
- [spatial-aggregation](../4-analyze/spatial-aggregation/README.md) produces reconciled
  territorial indicators from vector objects and zones.
- [geospatial-descriptive-statistics](../4-analyze/geospatial-descriptive-statistics/README.md)
  describes one layer's attributes without spatial matching.
- [qgis-layer-styling](../5-publish/qgis-layer-styling/README.md) creates reusable QML;
  [qgis-project-builder](../5-publish/qgis-project-builder/README.md) packages existing
  results into a verified QGIS project.

Previous: [5. Represent and publish](../5-publish/README.md) · [All families](../../README.md#skills)
