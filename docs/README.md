# Documentation guide

Use the [skill catalog](../README.md#skills) for the current list and installation commands.
Family pages describe each skill's purpose, related skills and remaining gaps. Inside a
skill, `README.md` is the human guide, `SKILL.md` gives agent instructions and `references/`
contains details loaded only when needed.

## Choose the output first

| Need | Start with | Boundary |
| --- | --- | --- |
| Choose a Géoplateforme service | [geopf-service-selection](../skills/1-discover/geopf-service-selection/README.md) | Route to the relevant extraction or calculation skill once the service is known. |
| Understand a BD TOPO class or attribute | [bdtopo-schema-guide](../skills/1-discover/bdtopo-schema-guide/README.md) | The bundled guide covers a sourced building/road subset; unknown versions and mappings remain unverified. |
| Produce a municipal building portrait | [municipality-building-profile](../skills/6-workflows/municipality-building-profile/README.md) | One municipality, shared building population, union footprint area and optional QGIS; no population or dwelling estimates. |
| Screen terrain by altitude and slope | [terrain-elevation-screening](../skills/6-workflows/terrain-elevation-screening/README.md) | AOI-wide DEM filtering and candidate polygons with coverage checks; no helicopter landing suitability conclusion. |
| Inspect an unfamiliar delivery | [geodata-intake](../skills/3-prepare/geodata-intake/README.md) | Identify files, layers and missing metadata before converting or analyzing them. |
| Summarize one layer's values | [geospatial-descriptive-statistics](../skills/4-analyze/geospatial-descriptive-statistics/README.md) | Numeric and categorical distributions; no spatial assignment. |
| Count or summarize objects by polygon zone | [spatial-aggregation](../skills/4-analyze/spatial-aggregation/README.md) | Declare border/overlap policies and reconcile unmatched or multiply matched objects. |
| Perform general vector operations | [geopandas-vector-analysis](../skills/4-analyze/geopandas-vector-analysis/README.md) | Spatial joins, overlays and buffers; use [gdal-vector-processing](../skills/3-prepare/gdal-vector-processing/README.md) for command-line conversion and filtering. |
| Compute raster zonal statistics | [gdal-raster-processing](../skills/3-prepare/gdal-raster-processing/README.md) | Account for grids, nodata and units; vector object counts are a different operation. |
| Illustrate existing data | [map-illustration](../skills/5-publish/map-illustration/README.md) | Static images by default, optional HTML, QGIS when useful; verify rendering and size, not new analysis. |
| Create a reusable vector style | [qgis-layer-styling](../skills/5-publish/qgis-layer-styling/README.md) | Produces verified QML; it does not assemble a project or create a print layout. |
| Assemble existing layers into a QGIS project | [qgis-project-builder](../skills/5-publish/qgis-project-builder/README.md) | Produces QGS/QGZ, optionally using existing QML; portability requires the data bundle as well. |

The skills are independently installable. Related skills can complement one another;
installing a whole family is not a prerequisite for using one skill. The
[workflow family](../skills/6-workflows/README.md) contains the municipal building portrait and terrain screening
and lists further candidate chains that are not yet implemented.

## Contributor and validation guides

| Document | Purpose |
| --- | --- |
| [Contributing conventions](../CLAUDE.md) | Layout, language, agent conduct and the checklist for a new skill. Also exposed through `AGENTS.md`. |
| [Skill names and families](skill-naming.md) | Naming convention, review of all 24 skills and old-to-current name correspondence. |
| [Runtime dependencies](dependencies.md) | Minimal requirements by family, conditional packages and reuse of existing environments. |
| [Output reports](output-reports.md) | Shared terminology and evidence to include with different artifact types. |
| [Test guide](../tests/README.md) | Current test inventory, prerequisites, offline checks, dedicated QGIS checks and opt-in live tests. |
| [Fixture metadata](../tests/data/README.md) | Provenance, coordinate systems and intentional traps in test inputs. |
| [A/B protocol](../tests/ab-testing.md) | Compare agent behavior with and without skills, and across models; a protocol is not a completed campaign. |
| [Experimental prompts](../tests/prompts/README.md) | Catalog and append-only record of exploratory agent runs. |

## Dated evidence

Reviews preserve what was checked at their stated date. Use the current test guide to run
new checks; do not reinterpret an earlier partial run as a later success. Historical skill
names remain as recorded; see the [name correspondence](skill-naming.md) for current names.

| Document | Scope |
| --- | --- |
| [2026-11-12 review](../tests/review-2026-11-12.md) | Scenario and test audit: standard scenario format, fixtures tied to their tests, structure checks and model-sensitivity checks. |
| [2026-11-12 municipal workflow review](../tests/review-municipality-building-profile-2026-11-12.md) | First workflow, independently checked building indicators and a portable QGIS forward pilot. |
| [2026-11-11 review](../tests/review-2026-11-11.md) | Five complementary skills, issues/merged PRs, QGIS integration, discovery and actual agent pilots. |
| [2026-10-28 review](../tests/review-2026-10-28.md) | Intake, downloads, elevation, routing and report conventions. |
| [2026-10-27 review](../tests/review-2026-10-27.md) | Test coverage audit, edge cases and limits. |
| [2026-10-12 review](../tests/review-2026-10-12.md) | Earlier skill defects, fixes and validation. |
| [Landscape study](landscape.md) | Comparison observed on 2026-10-27, with dated implementation follow-ups. |

Return to the [repository README](../README.md).
