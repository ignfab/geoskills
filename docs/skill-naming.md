# Skill names and family membership

Names identify the tool or domain and the operation or result. Family membership is
shown separately in the catalog and at the top of every skill README. This keeps names
short while making both the purpose and the place in the workflow visible.

## Convention

- Prefer `<tool-or-service>-<operation>` or `<domain>-<result>`, adding an object when it
  distinguishes related skills: `geopf-wfs-download`, `gdal-vector-processing`,
  `municipality-building-profile`.
- Keep a recognizable tool/service prefix when the skill depends on it. A prefix such
  as `geopf-` identifies a provider, not a family: selection, access and calculation
  belong to different stages.
- State what the skill does. A service name alone (`apicarto`) or a level (`basics`)
  leaves its output unclear. Protocol names still belong in descriptions and references
  so agents can match requests about WMS, WMTS or WFS.
- Do not prepend family names or numbers. Choose the family by the main output and
  record secondary uses under **Also relevant** on other family pages.
- Retain a clear existing name instead of changing it for grammatical symmetry alone.
  For example, `qgis-project-builder` already identifies its output and stays unchanged.

## Alignment review — 2026-11-13

All 24 skills were checked against their instructions, primary output and family.
Seven names change; seventeen remain unchanged. No skill moves to a different family,
and none of the processing methods or service endpoints changes.

| Family | Current skill | Main function or output | Former name |
| --- | --- | --- | --- |
| `1-discover` | [bdtopo-schema-guide](../skills/1-discover/bdtopo-schema-guide/README.md) | Explain versioned BD TOPO fields and meanings | — |
| `1-discover` | [geopf-service-selection](../skills/1-discover/geopf-service-selection/README.md) | Choose the Géoplateforme service for a request | `geopf-services` |
| `2-access` | [apicarto-query](../skills/2-access/apicarto-query/README.md) | Query API Carto and retrieve all matching features | `apicarto` |
| `2-access` | [geopf-file-download](../skills/2-access/geopf-file-download/README.md) | Retrieve ready-made dataset files and archives | `geopf-download-files` |
| `2-access` | [geopf-geocoding](../skills/2-access/geopf-geocoding/README.md) | Geocode locations and review matches | — |
| `2-access` | [geopf-wfs-download](../skills/2-access/geopf-wfs-download/README.md) | Retrieve filtered vector features through WFS | — |
| `2-access` | [geopf-raster-download](../skills/2-access/geopf-raster-download/README.md) | Retrieve raster subsets through WMS-R or WMTS | `geopf-wms-wmts` |
| `2-access` | [geoserver-cql-filter](../skills/2-access/geoserver-cql-filter/README.md) | Build GeoServer attribute and spatial filters | — |
| `3-prepare` | [crs-reprojection-france](../skills/3-prepare/crs-reprojection-france/README.md) | Choose French CRSs and transform coordinates | — |
| `3-prepare` | [gdal-raster-processing](../skills/3-prepare/gdal-raster-processing/README.md) | Inspect, clip, reproject, mosaic and convert rasters | `gdal-raster-basics` |
| `3-prepare` | [gdal-vector-processing](../skills/3-prepare/gdal-vector-processing/README.md) | Convert, filter, clip and merge local vectors | `gdal-vector-basics` |
| `3-prepare` | [geodata-intake](../skills/3-prepare/geodata-intake/README.md) | Inventory an unfamiliar data delivery | — |
| `3-prepare` | [vector-data-quality](../skills/3-prepare/vector-data-quality/README.md) | Audit and repair vector data | — |
| `4-analyze` | [geopandas-vector-analysis](../skills/4-analyze/geopandas-vector-analysis/README.md) | Derive joins, overlays, buffers and zonal statistics in Python | `geopandas-basics` |
| `4-analyze` | [geopf-altimetry](../skills/4-analyze/geopf-altimetry/README.md) | Compute point elevations and elevation profiles | — |
| `4-analyze` | [geopf-routing](../skills/4-analyze/geopf-routing/README.md) | Compute routes and reachable areas | — |
| `4-analyze` | [geospatial-descriptive-statistics](../skills/4-analyze/geospatial-descriptive-statistics/README.md) | Summarize one layer's attributes and missing values | — |
| `4-analyze` | [spatial-aggregation](../skills/4-analyze/spatial-aggregation/README.md) | Aggregate vector objects into polygon zones | — |
| `5-publish` | [map-illustration](../skills/5-publish/map-illustration/README.md) | Render static or interactive maps of existing results | — |
| `5-publish` | [mapshaper-simplify](../skills/5-publish/mapshaper-simplify/README.md) | Reduce polygon complexity for delivery | — |
| `5-publish` | [qgis-layer-styling](../skills/5-publish/qgis-layer-styling/README.md) | Create reusable QGIS vector styles | — |
| `5-publish` | [qgis-project-builder](../skills/5-publish/qgis-project-builder/README.md) | Assemble portable QGIS projects | — |
| `6-workflows` | [municipality-building-profile](../skills/6-workflows/municipality-building-profile/README.md) | Chain acquisition, building indicators and municipal delivery | — |
| `6-workflows` | [terrain-elevation-screening](../skills/6-workflows/terrain-elevation-screening/README.md) | Chain DEM preparation, terrain filtering and candidate-area delivery | — |

The three `basics` names become operations. Service selection and API Carto querying gain
an explicit action. Raster download names the retrieved data instead of only its protocols.
`geopf-file-download` uses the same object/action order as `geopf-wfs-download` and
`geopf-raster-download`; it still covers ready-made archives rather than raster-service
requests. GeoPandas keeps I/O and reprojection as supporting steps for its analysis recipes.
The broad GDAL skills remain in preparation, with their analysis and delivery uses linked
from the other families.

Validation on this revision: the metadata/link validator and Skills CLI discover 24 skills,
including all seven new identifiers and no superseded identifier. Every skill README has
the correct family. The offline suite completes 204 tests with 26 optional/live skips,
including the A/B runner's isolated dry campaigns; all 17 dedicated QGIS tests pass
separately on QGIS 3.44.9. Helper scripts, historical evidence and quoted French prompts
were compared with the preceding revision and remain unchanged.

## Existing installations and historical evidence

The seven new names are the canonical directory names, frontmatter `name` values and
`--skill` identifiers. The old names are not aliases. Installing from a checkout containing
these changes uses the new name, for example:

```bash
npx skills add /path/to/geoskills --skill geopf-raster-download
```

Existing installed copies keep their old names until the user updates them. Review local
customizations before removing a superseded copy through the agent's skill management or
its installation directory. This repository change does not remove or update installed
skills automatically. Duplicate compatibility skills would obscure selection and are not
provided.

Current instructions, installation examples, test paths and expected skill names use the
new identifiers. Scenario IDs and French prompts stay unchanged. Dated reviews, evidence
JSON and append-only run rows preserve the names actually tested at their recorded commit;
use the table above to relate them to the current catalog. These checks do not establish
that renaming improves automatic agent selection; that requires a new agent evaluation.
