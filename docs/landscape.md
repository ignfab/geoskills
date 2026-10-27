# Geospatial agent skills landscape — 2026-10-27

This is a dated snapshot written for [issue #30](https://github.com/ignfab/geoskills/issues/30):
study the other geospatial skill collections and propose a target for this repository. Star
counts, skill counts and dates were observed on 2026-10-27 and are not kept up to date. The
proposed target in the last sections is a proposal for the maintainers, not a decision.

## Scope and method

- **Sources.**
  - GitHub repository search with the queries `geoskills`, `geospatial skills SKILL.md`,
    `gis agent skills`, `gdal skills claude`, `geospatial claude skills`,
    `geoplateforme agent`, `qgis skills agent` and `datagouv skill`.
  - The neighbors listed in the comparison table of
    [muend/geoai-skills](https://github.com/muend/geoai-skills#what-makes-this-different).
- **Reading.** For each repository: the README, the file tree and the `description` of each
  `SKILL.md`. Nothing was cloned, installed or run.
- **Criteria.** Purpose, number of skills, license, last push, installation route, evidence of
  testing or evaluation, data and services covered, and overlap with the skills of this
  repository.
- **Limits.**
  - Only GitHub search was used; the skills.sh registry was not crawled.
  - Stars measure visibility, not quality.
  - Testing evidence means that test or eval files are present; they were not run.

## Comparison

### Geospatial skill collections

| Repository | Stars | License | Last push | Skills | Focus | Testing and evaluation |
| --- | --- | --- | --- | --- | --- | --- |
| [ignfab/geoskills](https://github.com/ignfab/geoskills) (this repository) | 0 | MIT | 2026-10-27 | 10 | Géoplateforme services, French CRS, GDAL/PROJ, GeoPandas and Mapshaper recipes | 67 unit tests on 8 fixtures, opt-in live IGN tests, 58 manual scenarios (negatives included), documented A/B protocol |
| [dekart-xyz/geosql](https://github.com/dekart-xyz/geosql) | 682 | MIT | 2026-10-09 | 1 | Spatial SQL on PostGIS, BigQuery, Snowflake and Wherobots, with a Dekart map in the loop | Test and eval files |
| [maplibre/maplibre-agent-skills](https://github.com/maplibre/maplibre-agent-skills) | 155 | MIT | 2026-10-26 | 11 | MapLibre GL JS application code | Eval suite; separates eval-verified and provisional skills |
| [mapbox/mapbox-agent-skills](https://github.com/mapbox/mapbox-agent-skills) | 83 | MIT | 2026-10-26 | 20 | Mapbox platform application code | Eval files |
| [isaaccorley/geospatial-skills](https://github.com/isaaccorley/geospatial-skills) | 79 | Apache-2.0 | 2026-08-07 | 19 | Cloud-native tools: GDAL, GeoParquet, STAC, PMTiles, Zarr, Portolan, Overture | A few test files |
| [jaakla/openmapstack-skills](https://github.com/jaakla/openmapstack-skills) | 76 | MIT | 2026-10-27 | 4 | Reproducible GIS projects (`project.yaml`, pipeline, validation) on OSM, Overture, STAC, DuckDB, PostGIS, QGIS and MapLibre | Deterministic fixture evals, a validation CLI and a live-agent benchmark |
| [muend/geoai-skills](https://github.com/muend/geoai-skills) | 35 | MIT | 2026-10-17 | 18 | Method guardrails: when a geospatial claim is defensible, across open and proprietary stacks | Published routing benchmark (167 cases, held-out split), 92 paired behavior cases, known defects |
| [opengeos/geoai-skills](https://github.com/opengeos/geoai-skills) | 35 | MIT | 2026-10-12 | 8 | Claude Code plugin over the `geoai` Python library: inspection, STAC, NAIP, Overture, object detection | None found |
| [danmaps/gis-agent-skills](https://github.com/danmaps/gis-agent-skills) | 29 | Not detected by GitHub (README states MIT) | 2026-10-13 | 20 | ArcGIS Pro, ArcPy and ArcGIS Online workflows; readiness and QA checklists | A validator and one test file |
| [OpenCesium/SuperGIS-Skills](https://github.com/OpenCesium/SuperGIS-Skills) | 26 | Not detected | 2026-10-23 | 1 | Web map code from 6,262 official examples across 21 libraries | None found |
| [phuismann/geoskills](https://github.com/phuismann/geoskills) | 13 | MIT | 2026-03-14 | 7 | Short checklists: intake, CRS, QA, world CRS, ML, PostGIS, Snowflake | None found |
| [Kendrick-Oppong/geoskills](https://github.com/Kendrick-Oppong/geoskills) | 0 | Not detected | 2026-08-23 | 32 | WebGIS software engineering: rendering, tiles, APIs, architecture | None found |
| [shioo-gis/gis-kit](https://github.com/shioo-gis/gis-kit) | 0 | Apache-2.0 | 2026-10-26 | 1 | Toolbox of 40+ scripts behind one CLI: vector, raster, terrain, networks, map vectorization | Test suite |
| [GeoMaster in K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/geomaster) | 54,864 (whole library) | MIT | 2026-10-26 | 1 | One broad geospatial science reference inside a large science library | Not assessed |

### French public sector and IGN projects

| Repository | Stars | Kind | Relation to this repository |
| --- | --- | --- | --- |
| [ignfab/geocontext](https://github.com/ignfab/geocontext) | 29 | MCP server | Answers questions from live Géoplateforme data (geocoding, layer search, schemas, feature counts) without a local copy. Complementary: these skills produce local files and processing. |
| [ignfab/mcp-carto](https://github.com/ignfab/mcp-carto) | 7 | MCP App | Displays IGN maps in a chat client. No overlap. |
| [glaforge/ign-agentic](https://github.com/glaforge/ign-agentic) | 0 | IGN workshop (Java, MCP) | Ships one 119-line `ign-geoplateforme` skill on Géoplateforme APIs and CRS axis order. It is the closest overlap with `geopf-services`. The workshop tests its Java tools, not the skill. |
| [etalab-ia/skills](https://github.com/etalab-ia/skills) | 28 | Skills of the French State (DINUM) | Model for the repository layout ([#5](https://github.com/ignfab/geoskills/issues/5)). No geospatial skill. `datagouv-apis` searches the data.gouv.fr catalog; it does not query geodata services. |
| [datagouv/datagouv-skill](https://github.com/datagouv/datagouv-skill) | 65 | Official data.gouv.fr skill | Catalog access, same scope as `datagouv-apis`. |

### Homonym

[Cognitic-Labs/geoskills](https://github.com/Cognitic-Labs/geoskills) (31 stars) uses "GEO" for
*Generative Engine Optimization*. Its 8 skills deal with the visibility of a website in AI
search engines and are unrelated to geospatial data. Two other repositories are also named
`geoskills` (phuismann, Kendrick-Oppong).

## Overlap with our skills

"Generic" means that the studied repositories cover the underlying tool or topic, but not
French services or French data.

| Our skill | Closest coverage elsewhere | French or Géoplateforme specifics elsewhere |
| --- | --- | --- |
| `geopf-services` | Generic data discovery (openmapstack `geospatial-data-discovery`, muend `geo-data-engineering`) | `ign-geoplateforme` in glaforge/ign-agentic; the geocontext MCP |
| `geopf-wfs-download` | Generic OGC and GDAL guidance (Kendrick-Oppong `ogc-services-and-interop`, isaaccorley `gdal`) | ign-agentic and geocontext query BD TOPO, but produce no local file |
| `geopf-wms-wmts` | Generic OGC guidance (Kendrick-Oppong) | ign-agentic and mcp-carto, for display only |
| `geopf-geocoding` | Generic geocoding (Kendrick-Oppong `geocoding-and-address-matching`, openmapstack) | ign-agentic and geocontext geocode single addresses; none found covers bulk CSV geocoding |
| `geoserver-cql-filter` | Generic GeoServer interop (Kendrick-Oppong) | None found |
| `crs-reprojection-france` | Generic CRS skills (phuismann, Kendrick-Oppong, openmapstack); GeoMaster mentions Lambert-93 | None found covers NTF grids, NGF heights or overseas CRSs |
| `gdal-raster-basics` | isaaccorley `gdal`, opengeos `process-raster`, gis-kit, muend `terrain-hydrology` | None found |
| `geopandas-basics` | openmapstack processing references, muend `geo-data-engineering`, gis-kit | None found |
| `vector-data-quality` | phuismann and Kendrick-Oppong `geodata-qaqc`, danmaps `schema-smells` and `post-run-validation` | None found |
| `mapshaper-simplify` | Simplification inside broader skills (Kendrick-Oppong `computational-geometry-operations`, isaaccorley `parallel-geospatial`) | None found |

## What sets this repository apart

- **Géoplateforme depth.**
  - None of the studied collections covers Géoplateforme downloads, bulk geocoding or GeoServer
    CQL filters.
  - The only other Géoplateforme skill found is a single workshop file, without tests of its
    own.
- **French geodesy.**
  - Generalists name Lambert-93 at most.
  - `crs-reprojection-france` covers the CC zones, NTF and its grids, NGF heights and the
    overseas departments.
- **Commands that are tested.**
  - Most collections are prose or checklists.
  - Here, recipes run against fixtures in CI, live service tests exist, and every skill states
    how to validate its output.
  - openmapstack, muend and the MapLibre skills ship larger evaluation suites, and muend
    publishes its results. geosql and gis-kit also ship tests.
- **Agent conduct rules.** The agent never installs software, takes names from metadata and
  validates before reporting. Comparable rules appear in muend (claim gates), danmaps
  (`safety`) and openmapstack (approval-gated snapshots).

## Gaps worth borrowing

These are candidates for follow-up issues, not commitments.

| Idea | Seen in | Possible form here |
| --- | --- | --- |
| First-pass inspection of an unknown dataset, routing to the right skill | phuismann `geodata-intake`, opengeos `inspect-geo`, Kendrick-Oppong `geodata-formats-and-intake` | A `geodata-intake` skill; the existing fixtures without `.prj` and with swapped axes already make good test cases |
| Raster quality checks and severity levels (blocker, major, minor) | phuismann and Kendrick-Oppong `geodata-qaqc`, danmaps `post-run-validation` | A raster reference in `gdal-raster-basics`; severity levels in the `vector-data-quality` report |
| CRS choice beyond France (European LAEA, world maps, Web Mercator limits) | phuismann `global-crs-selection` | A reference in `crs-reprojection-france` |
| Machine-readable evals with published results | muend, openmapstack, MapLibre | Convert `tests/<skill>.md` scenarios to a structured format and publish one A/B campaign |
| Fixed report format at the end of a skill | phuismann, danmaps | A short template: output path, CRS, feature count, extent, limits |
| Skill template | phuismann, Kendrick-Oppong | `templates/skill/` with the required sections and the test checklist |
| Explicit verified and provisional status | MapLibre, etalab-ia `.experimental/` | Mark skills without a published A/B result as provisional |

## Proposed target

**Positioning.** This repository would be the tested execution layer for French public
geodata: skills that let an agent find, download, reproject, clean and convert Géoplateforme
data on the user's machine with open-source command-line tools. It would complement two
neighbors rather than compete with them:

- **The geocontext MCP** answers live questions without a download.
- **Generalist collections** (openmapstack, muend, isaaccorley) cover method guardrails and
  global, cloud-native stacks.

**Audience.** Developers, data analysts and agent builders who work with IGN data or other
French public geodata, in French or in English.

**In scope.**

- Géoplateforme services: discovery, WFS, WMS/WMTS, geocoding, extraction and calculation
  APIs.
- GeoServer behavior behind these services, such as CQL filters.
- French coordinate reference systems and heights, including overseas territories.
- Open-source processing (GDAL/OGR, PROJ, GeoPandas, Mapshaper, data quality), as far as it is
  needed on French data, with French fixtures and examples.

**Out of scope (proposed).**

- Proprietary platforms (ArcGIS, Google Earth Engine): covered by danmaps and muend.
- Cloud data warehouses: covered by geosql and openmapstack.
- Web map frameworks: covered by the MapLibre and Mapbox skill collections. This is consistent
  with the removal of the OpenLayers skill in [#8](https://github.com/ignfab/geoskills/pull/8).
- GeoAI, machine learning and satellite imagery pipelines: covered by opengeos, isaaccorley
  and muend.

**Quality bar.**

- Every skill keeps `## Prerequisites`, `## Validate the output`, fixture tests and scenarios,
  negatives included.
- A skill is called stable only after a published A/B campaign shows that it helps.

## Open questions for maintainers

1. **Generic skills.**
   - `gdal-raster-basics` and `geopandas-basics` overlap generalist collections.
   - Should they stay, as long as they carry French specifics and tests, or point users to
     those collections?
2. **Name and description.**
   - `geoskills` is shared with three unrelated repositories, and the current GitHub
     description ("Some spatial related skills for LLM agents") does not mention France or the
     Géoplateforme.
   - A description naming the Géoplateforme would help discovery. A rename could be settled
     together with [#3](https://github.com/ignfab/geoskills/issues/3) ("Move to IGNF?").
3. **Skills and MCP.**
   - Should a skill tell agents when to call geocontext tools instead of downloading data?
   - If so, should that be a new skill or a section of `geopf-services`?
4. **Published evidence.** Should one A/B campaign be run and published before the
   exploratory status is lifted?
