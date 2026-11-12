# 6. Solve a business need

**Question:** how do I chain the steps to reach an objective?

A skill in this family chains acquisition, preparation, analysis and delivery to answer a
business question. It defines the shared method and checks across those stages; specialized
skills remain independently useful for narrower requests.

| Skill | Use it to |
| --- | --- |
| [municipality-building-profile](municipality-building-profile/README.md) | Produce one municipality's building counts, union footprint coverage, height/usage summaries and optional portable QGIS delivery, with explicit source and boundary rules. |

## Further workflow candidates

| Use case | Building blocks available today |
| --- | --- |
| Territorial diagnosis | `geopf-wfs-download` (boundaries, BD TOPO), `apicarto` (urban planning, protected areas), `geopf-altimetry`, `geopandas-basics` (overlays), `spatial-aggregation` (territorial indicators), `geospatial-descriptive-statistics` (attribute distributions) |
| Accessibility | `geopf-geocoding` (starting points), `geopf-routing` (isochrones), `geopandas-basics` (overlay with the area of interest) |
| Exposure | `geopf-geocoding`, `apicarto` (zones, easements, protected areas), `geopandas-basics` (spatial joins) |
| Change monitoring | `geopf-download-files` (editions), `vector-data-quality`, `geopandas-basics` (comparison) |

These broader chains are explored with the business-need prompts of the
[experimental prompt catalog](../../tests/prompts/catalog.md); their runs are logged in
[runs.md](../../tests/prompts/runs.md). One documented chain is in
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

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/6-workflows
```

Previous: [5. Represent and publish](../5-publish/README.md) · [All families](../../README.md#skills)
