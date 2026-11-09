# 6. Solve a business need

**Question:** how do I chain the steps to reach an objective?

A skill in this family will chain skills from the other families to answer a business
question end to end. None exists yet. A workflow skill is written only once its chain works
reliably with the skills it depends on.

| Use case | Building blocks available today |
| --- | --- |
| Territorial diagnosis | `geopf-wfs-download` (boundaries, BD TOPO), `apicarto` (urban planning, protected areas), `geopf-altimetry`, `geopandas-basics` (overlays, statistics) |
| Accessibility | `geopf-geocoding` (starting points), `geopf-routing` (isochrones), `geopandas-basics` (overlay with the area of interest) |
| Exposure | `geopf-geocoding`, `apicarto` (zones, easements, protected areas), `geopandas-basics` (spatial joins) |
| Change monitoring | `geopf-download-files` (editions), `vector-data-quality`, `geopandas-basics` (comparison) |

The only chain documented so far is in
[mapshaper-simplify](../5-publish/mapshaper-simplify/README.md): download boundaries with
`geopf-wfs-download`, audit them with `vector-data-quality`, then simplify them.

Previous: [5. Represent and publish](../5-publish/README.md) · [All families](../../README.md#skills)
