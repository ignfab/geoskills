# Skill tests

A skill is useful only if two things hold: the commands it documents work, and an agent
loads it when it should and follows it. No single kind of test checks both. This folder
holds five kinds of tests, from cheap and automatic to slow and paid. A green unit-test
run does not prove that an agent will select the right skill.

Current scenarios and helper paths use the [current skill names](../docs/skill-naming.md).
Dated reviews and recorded runs retain the names actually tested. Scenario identifiers
remain stable across renames so historical results can still be matched to the same task.

## Contents

1. [The five kinds of tests](#the-five-kinds-of-tests)
2. [Which tests to run](#which-tests-to-run)
3. [Quick start](#quick-start): commands, CI, environment variables and skips
4. [Coverage by skill](#coverage-by-skill)
5. [Offline tests](#offline-tests) and [QGIS integration](#qgis-integration)
6. [Live tests](#live-tests)
7. [Agent scenarios](#agent-scenarios)
8. [Fixtures](#fixtures)
9. [Add or change a test](#add-or-change-a-test)
10. [Reviews and reports](#reviews-and-reports)
11. [Glossary](#glossary)

## The five kinds of tests

| Kind | Question it answers | Files | How it runs | Cost |
| --- | --- | --- | --- | --- |
| Offline tests | Do the documented commands, scripts and fixtures give the expected result? | `test_*.py`, except `test_live*` | `unittest`, on every push in CI | Free, no network |
| Live tests | Do the public IGN services still answer as the skills say? | `test_live*.py` | Only with `GEOSKILLS_LIVE=1` | Small bounded requests to IGN services |
| Agent scenarios | Does an agent load the right skill, and is its result correct? | `<skill-name>.md`, one per skill | By hand, or with the A/B runner of [ab-testing.md](ab-testing.md) | Paid agent calls |
| Model sweep | Does a skill work as well with a smaller model as with a larger one? | The agent scenarios | The runner's [model sweep](ab-testing.md#model-sensitivity) | Paid agent calls, per model |
| Experimental prompts | What does an agent do with a new or chained request? | [prompts/](prompts/README.md) | Same as scenarios, then logged in `prompts/runs.md` | Paid agent calls |

The scenario prompts are in French on purpose: they check that a French request triggers
a skill whose `description` is written in English.

## Which tests to run

Start from what you changed or want to know:

| You changed, or want to check | Run | What it catches |
| --- | --- | --- |
| A `SKILL.md` description or body | `python3 .github/validate-skills.py`, then `test_skill_robustness.py` and `test_scenarios.py` | Broken metadata and links, a missing `Use when …` clause, vague skill names, a tested boundary that the skill does not state |
| A command or code block in a skill | The offline test of that skill, from [Coverage by skill](#coverage-by-skill) | Many tests execute the documented block itself, so a broken recipe fails |
| A helper script under `scripts/` | The offline test of that skill | Wrong values, unsafe overwrites, lost identifiers |
| A scenario file or `ab-testing.md` | `test_scenarios.py` and `test_ab_runner.py` | Missing prompt, expected skill or checklist; numbering gaps; missing fixtures; A/B lists, matrix and run counts out of date |
| A fixture in `data/` | The tests listed for it under [Fixtures](#fixtures) | Reference values that no longer match |
| A QGIS skill | `test_qgis*.py`, with PyQGIS (see [QGIS integration](#qgis-integration)) | Styles, projects or renders that QGIS does not reopen as expected |
| Whether the IGN services still behave as documented | The [live tests](#live-tests) | Changed endpoints, layers or responses |
| Whether an agent picks and follows a skill | One [agent scenario](#agent-scenarios) by hand | Selection and conduct, which unit tests cannot show |
| How much a skill adds, or whether it depends on the model | The A/B campaign or the model sweep of [ab-testing.md](ab-testing.md) | Paid; starting one is a separate decision |
| Anything, before a pull request | The validator and the whole offline suite (below) | What CI runs on every push |

## Quick start

From the repository root, with Python ≥ 3.9:

Reuse an existing environment first. The geospatial requirements below are a broad,
optional contributor/CI set spanning several skills, not an installation prerequisite
for one skill or family. Focused checks need only their relevant packages; see the
[runtime dependency guide](../docs/dependencies.md). Installation commands are for the user.

```bash
python3 -m pip install -r tests/requirements.txt              # PyYAML, for the validator
python3 -m pip install -r tests/requirements-geospatial.txt   # optional: GeoPandas, Matplotlib, Folium tests
python3 .github/validate-skills.py                            # layout, metadata, links
python3 -m unittest discover -s tests -p 'test_*.py' -v       # every offline test
```

One file, or one test:

```bash
python3 -m unittest discover -s tests -p 'test_geopandas.py' -v
cd tests && python3 -m unittest test_geopandas.GeoPandasTests.test_spatial_join -v
```

The test modules import each other by name (`skill_examples`, `test_workflows`), so
`python3 -m unittest tests.test_geopandas` from the root fails: use `discover -s tests`
or run from `tests/`.

A run ends with `OK (skipped=N)` when everything that could run passed. The skips are the
tests whose optional tools are missing on your machine; [Reading the skips](#reading-the-skips)
says which tool each one needs.

### What CI runs

| Workflow | When | What it runs |
| --- | --- | --- |
| [Validate skills](../.github/workflows/validate-skills.yml) | Every push and pull request | Installs Python 3.11, Node.js 22, GDAL and Mapshaper 0.7.83, then runs the validator and every offline test with `GEOSKILLS_REQUIRE_GDAL=1` and `GEOSKILLS_REQUIRE_MAPSHAPER=1`, so a missing tool fails instead of skipping |
| Validate skills, started by hand | **Actions → Validate skills → Run workflow**, with *Also run bounded requests to public IGN services* ticked | The same, plus the live tests |
| [QGIS integration](../.github/workflows/qgis.yml) | Every push and pull request | Installs `python3-qgis` on Ubuntu 24.04 and runs the `test_qgis*.py` modules with `GEOSKILLS_REQUIRE_QGIS=1` |

Agent scenarios, A/B campaigns and model sweeps never run in CI.

### Environment variables

| Variable | Effect |
| --- | --- |
| `GEOSKILLS_LIVE=1` | Enables the live tests, which are skipped otherwise. |
| `GEOSKILLS_REQUIRE_GDAL=1` | A missing GDAL/PROJ command fails the run instead of skipping. CI sets it. |
| `GEOSKILLS_REQUIRE_MAPSHAPER=1` | Same for Mapshaper and its Python dependencies. CI sets it. |
| `GEOSKILLS_REQUIRE_QGIS=1` | Same for PyQGIS. Only the dedicated QGIS workflow sets it. |

### Reading the skips

Missing tools or packages give an explicit skip; a tool that is installed but cannot start
is an error. If `gdalinfo --version` fails (for example with an undefined
`sqlite3_total_changes64` symbol), repair the GDAL/SQLite environment or use a clean one:
the tests deliberately do not hide a broken installation.

| Skip message | What is missing | To run it |
| --- | --- | --- |
| `Set GEOSKILLS_LIVE=1 …` | Nothing: live tests are opt-in | See [Live tests](#live-tests) |
| `Missing GDAL/PROJ tools: …` | GDAL ≥ 3.1 and PROJ command-line tools | Install GDAL and PROJ |
| `Missing GDAL Python utilities: …` | `gdal_calc.py` and `gdal_polygonize.py`, used by the terrain screening recipes | `sudo apt install gdal-bin python3-gdal python3-numpy` (Debian/Ubuntu) |
| `Install tests/requirements-geospatial.txt …`, `Pandas is not installed`, `GeoPandas is not installed` | pandas, GeoPandas, `rasterstats`, `pyarrow` | `python3 -m pip install -r tests/requirements-geospatial.txt` |
| `Map illustration tests need geopandas, matplotlib, folium and Pillow` | The map rendering libraries | `python3 -m pip install -r tests/requirements-geospatial.txt` |
| `Raster preview needs rasterio` | rasterio, for the raster map preview | `python3 -m pip install rasterio` |
| `Missing Mapshaper test dependencies: …` | Mapshaper CLI | With Node.js: `npm install --global mapshaper@0.7.83` (the version CI uses) |
| `… need GDAL >= 3.12` | The `gdal vector …` and `gdal raster zonal-stats` commands | GDAL ≥ 3.12 |
| `Full COG validation requires GDAL >= 3.13 …` | `gdal driver cog validate` and matching Python bindings | GDAL ≥ 3.13 |
| `Needs GeoPandas >= 1.1 with Shapely >= 2.1` | Coverage functions | Newer GeoPandas and Shapely |
| `Accurate NTF transformation needs an installed IGN grid` | `fr_ign_ntf_r93.tif` (or an equivalent NTF grid) | Inspect with `projinfo`, then fetch only that grid with `projsync --file <complete-grid-filename>` |
| `PyQGIS is not installed; …` | QGIS 3.34–3.x with its Python bindings | The dedicated [QGIS workflow](../.github/workflows/qgis.yml) runs them; locally, `sudo apt install python3-qgis` |
| `Vertical check needs the installed RAF18 grid` | `fr_ign_RAF18.tif` | `projsync --file fr_ign_RAF18.tif` |

The tests use temporary directories, turn PROJ networking off and never modify the
fixtures in `data/`.

## Coverage by skill

Each skill has a scenario file named after it. Scenario identifiers use the prefix of
that file: `-01`, `-02`… for positive scenarios and `-N1`, `-N2`… for negative ones. A
prefix stays the same when a skill is renamed, which is why `gdal-vector-processing`
scenarios start with `GVB` and `geopf-raster-download` scenarios with `WMS`.

| Family | Skill | Scenarios (positive + negative) | Offline tests | Live tests |
| --- | --- | --- | --- | --- |
| 1. Discover | `bdtopo-schema-guide` | [BTS](bdtopo-schema-guide.md): 2 + 2 | `test_bdtopo_schema_guide.py` | — |
| 1. Discover | `geopf-service-selection` | [GSV](geopf-service-selection.md): 5 + 2 | — (advice only) | `test_live.py` (discovery commands) |
| 2. Access | `apicarto-query` | [APC](apicarto-query.md): 3 + 1 | `test_apicarto.py` | `test_live_apicarto.py` |
| 2. Access | `geopf-file-download` | [DLF](geopf-file-download.md): 2 + 1 | `test_enrichment.py` (catalogue pages), `test_download_transfers.py` | `test_live.py`, `test_live_enrichment.py` |
| 2. Access | `geopf-geocoding` | [GEO](geopf-geocoding.md): 6 + 1 | `test_enrichment.py` (review policy), `test_split_csv.py` | `test_live.py` (address, CSV, reverse, parcel) |
| 2. Access | `geopf-raster-download` | [WMS](geopf-raster-download.md): 5 + 1 | — | `test_live.py` (WMTS, WMS-R) |
| 2. Access | `geopf-wfs-download` | [WFS](geopf-wfs-download.md): 7 + 1 | `test_enrichment.py` (export completeness) | `test_live.py`, `test_live_enrichment.py` (paging) |
| 2. Access | `geoserver-cql-filter` | [CQL](geoserver-cql-filter.md): 4 + 2 | `test_cql_requests.py` | `test_live_enrichment.py` (real ECQL) |
| 3. Prepare | `crs-reprojection-france` | [CRS](crs-reprojection-france.md): 5 + 1 | `test_workflows.py` | — |
| 3. Prepare | `gdal-raster-processing` | [RAS](gdal-raster-processing.md): 6 + 1 | `test_workflows.py`, `test_raster_quality.py` | — |
| 3. Prepare | `gdal-vector-processing` | [GVB](gdal-vector-processing.md): 4 + 2 | `test_gdal_vector.py` | — |
| 3. Prepare | `geodata-intake` | [INT](geodata-intake.md): 2 + 1 | `test_raster_quality.py` (intake recipes) | — |
| 3. Prepare | `vector-data-quality` | [VDQ](vector-data-quality.md): 3 + 2 | `test_vector_quality.py` | — |
| 4. Analyze | `geopandas-vector-analysis` | [GPD](geopandas-vector-analysis.md): 4 + 1 | `test_geopandas.py` | — |
| 4. Analyze | `geopf-altimetry` | [ALT](geopf-altimetry.md): 2 + 2 | `test_enrichment.py` (joins, missing values) | `test_live_enrichment.py` |
| 4. Analyze | `geopf-routing` | [RTE](geopf-routing.md): 2 + 1 | `test_enrichment.py` (GeoJSON export) | `test_live.py`, `test_live_enrichment.py` |
| 4. Analyze | `geospatial-descriptive-statistics` | [GDS](geospatial-descriptive-statistics.md): 2 + 2 | `test_geospatial_descriptive_statistics.py` | — |
| 4. Analyze | `spatial-aggregation` | [SPA](spatial-aggregation.md): 2 + 2 | `test_spatial_aggregation.py` | — |
| 5. Publish | `map-illustration` | [MAP](map-illustration.md): 4 + 3 | `test_map_illustration.py`, `test_qgis_map_illustration.py` (needs PyQGIS) | — |
| 5. Publish | `mapshaper-simplify` | [MS](mapshaper-simplify.md): 4 + 2 | `test_mapshaper.py` | — |
| 5. Publish | `qgis-layer-styling` | [QLS](qgis-layer-styling.md): 2 + 1 | `test_qgis_layer_styling.py` (needs PyQGIS) | — |
| 5. Publish | `qgis-project-builder` | [QPB](qgis-project-builder.md): 2 + 1 | `test_qgis_project_builder.py` (needs PyQGIS) | — |
| 6. Workflows | `municipality-building-profile` | [MBP](municipality-building-profile.md): 3 + 3 | `test_municipality_building_profile.py` (GeoPandas) | — |
| 6. Workflows | `terrain-elevation-screening` | [TES](terrain-elevation-screening.md): 3 + 2 | `test_terrain_elevation_screening.py` (GDAL recipes) | — |

`geopf-service-selection` and `geopf-raster-download` have no offline test: their value is
advice and remote requests, so only the live tests and the agent scenarios exercise them.

## Offline tests

Many offline tests do not copy commands: they **execute the code blocks of the skill
files** through [skill_examples.py](skill_examples.py) (`read_example` for Bash,
`run_example` for Python). Editing such an example changes the code under test, so a
documentation change that breaks a recipe fails CI. The other tests exercise
representative workflows, not every documented command.

| File | Skill | What it proves |
| --- | --- | --- |
| [test_workflows.py](test_workflows.py) | `crs-reprojection-france`, `gdal-raster-processing` | GDAL/PROJ recipes on the fixtures: axis order, overseas CRS, missing `.prj`, area, mosaic, clip and COG, weighted averaging, hillshade, zonal statistics (GDAL ≥ 3.12), nodata conversion that keeps valid zeros, NTF and vertical transformations (IGN grids). |
| [test_raster_quality.py](test_raster_quality.py) | `gdal-raster-processing`, `geodata-intake` | Categorical resampling on the RAS-06 fixture (values, grid, nodata, 75 % coverage), full COG validation (GDAL ≥ 3.13), read-only intake that keeps a missing CRS unknown and writes no sidecar. |
| [test_gdal_vector.py](test_gdal_vector.py) | `gdal-vector-processing` | `ogr2ogr` recipes on a CP1252 Shapefile without `.cpg` (encoding detection, suspicious characters), GeoPackage layer addition and silent replacement, field selection, clipping in a stated CRS, CSV points, RFC 7946, Shapefile field laundering, SQL, dissolve, merge and split; `gdal vector` examples on GDAL ≥ 3.12. With GDAL 3.13.0 to 3.13.3, `-where` with `-select` on a GeoPackage keeps every field. |
| [test_geopandas.py](test_geopandas.py) | `geopandas-vector-analysis` | Spatial joins (boundaries, unmatched and multiple matches), metric nearest joins and buffers, overlay areas, CRS and format round trips with nullable fields and string IDs, zonal statistics attached by position with filtered or repeated indices. |
| [test_vector_quality.py](test_vector_quality.py) | `vector-data-quality` | Null, empty and invalid geometries kept apart, repair methods, quarantine, duplicates, suspicious valid geometries, severity report, coverage overlaps and gaps on the VDQ-03 fixture; `gdal vector check-geometry`/`check-coverage` on GDAL ≥ 3.12. |
| [test_mapshaper.py](test_mapshaper.py) | `mapshaper-simplify` | Percentage and metric simplification, small-feature retention, shared borders across layers, TopoJSON arcs, CRS and attributes kept. |
| [test_enrichment.py](test_enrichment.py) | `geopf-wfs-download`, `geopf-geocoding`, `geopf-file-download`, `geopf-altimetry`, `geopf-routing` | The bundled scripts and recipes: WFS export completeness (missing or repeated pages, duplicate IDs), geocoding review policy (including the GEO-06 fixture), Atom catalogue pages, elevation joins (including the ALT-02 fixtures), route and isochrone export. |
| [test_split_csv.py](test_split_csv.py) | `geopf-geocoding` | `split_csv.py`: record and byte limits, BOM, multiline and quoted fields, leading zeros, malformed input, existing files kept. |
| [test_download_transfers.py](test_download_transfers.py) | `geopf-file-download` | Real `curl` downloads against a loopback archive server: integrity, byte-exact resume, refusal to append a changed edition. |
| [test_cql_requests.py](test_cql_requests.py) | `geoserver-cql-filter` | The documented `curl` commands against a local recorder: parameter encoding, EWKT kept, WFS sampling, WMS layer order. Does not validate ECQL parsing on a real GeoServer. |
| [test_apicarto.py](test_apicarto.py) | `apicarto-query` | The paging script and documented requests against a loopback server: `_start` paging, POSTed geometries, repeated IDs, changing or incomplete counts, errors with HTTP 200, 400 or 500, existing outputs kept. |
| [test_geospatial_descriptive_statistics.py](test_geospatial_descriptive_statistics.py) | `geospatial-descriptive-statistics` | `summarize.py` on known values: missing, infinite and invalid numbers, empty and single-value columns, string categories with leading zeros, bad column selection, CLI round trip without overwrite, geometry areas in a metric CRS with a geographic CRS refused (GeoPandas). |
| [test_spatial_aggregation.py](test_spatial_aggregation.py) | `spatial-aggregation` | `aggregate.py`: empty zones, null measures and reconciliation, border predicates and policies, overlapping zones, mixed known CRSs, bad IDs, missing CRS, invalid geometry, ratios with zero denominators, round trip without touching the sources; the SPA-01 and SPA-02 references on their fixtures (GeoPandas). |
| [test_bdtopo_schema_guide.py](test_bdtopo_schema_guide.py) | `bdtopo-schema-guide` | `lookup.py` and the versioned snapshot: building height with its special zero, road field aliases and enum, unknown versions, revisions, fields or formats never inferred, no network or GIS needed, every entry traced to a source. |
| [test_map_illustration.py](test_map_illustration.py) | `map-illustration` | Real PNG, SVG and PDF outputs reopened: dimensions, numeric and missing values kept apart, only the selected HTML tooltip attributes, external assets listed, and a bounded raster preview (needs rasterio). Uses Matplotlib and Folium from `requirements-geospatial.txt`. Browser and visual checks stay separate author or agent checks. |
| [test_qgis_map_illustration.py](test_qgis_map_illustration.py) | `map-illustration` | Export of the visible layers of an existing QGIS project. Needs PyQGIS ([QGIS integration](#qgis-integration)). |
| [test_qgis_layer_styling.py](test_qgis_layer_styling.py) | `qgis-layer-styling` | `style_layer.py` QML files reloaded on independent PyQGIS layers: red outline without fill and source unchanged, point and line units, categories with the null/other fallback, graduated ranges and shared breaks, unknown fields, bad breaks and existing outputs refused. Needs PyQGIS ([QGIS integration](#qgis-integration)). |
| [test_qgis_project_builder.py](test_qgis_project_builder.py) | `qgis-project-builder` | `build_project.py` projects reopened in PyQGIS: vector and raster layers, CRS, extent (including aligned points), layer-tree order, groups and visibility, optional QML, relative paths after moving the whole bundle with the original removed, source bytes and directory inventory unchanged, WMTS provider URI and an omitted remote basemap on failure. Needs PyQGIS ([QGIS integration](#qgis-integration)). |
| [test_municipality_building_profile.py](test_municipality_building_profile.py) | `municipality-building-profile` | `build_profile.py` checked against independent area and count oracles: overlapping buildings counted once in the union, border-crossing and border-touching buildings, height and usage semantics, missing or partial inputs, string codes, sources unchanged and GeoPackage/CSV/JSON report round trips (GeoPandas). |
| [test_terrain_elevation_screening.py](test_terrain_elevation_screening.py) | `terrain-elevation-screening` | The documented GDAL commands on synthetic rasters: inclusive and negative altitudes, a valid zero, nodata and slope borders, empty outputs, holes, connectivity, exact AOI clipping before area filtering and unchanged sources. Needs the GDAL Python utilities next to the GDAL CLI. These numerical checks do not validate helicopter landing sites. |
| [test_skill_robustness.py](test_skill_robustness.py) | every skill | The wording that keeps selection from depending on the model: each description says when to use the skill, stays within 1024 characters and names other skills exactly (not "the WFS skill"); each boundary tested by a negative scenario is written in the skill to exclude. See [Model sensitivity](#model-sensitivity). |
| [test_validation.py](test_validation.py) | the validator | [validate-skills.py](../.github/validate-skills.py): YAML, required sections, family layout, unique names, complete indexes, links that stay inside a skill. |
| [test_scenarios.py](test_scenarios.py) | every scenario | Each scenario has a French prompt, an `**Expected skill:**` line and a checklist; numbering has no gap; fixtures named in prompts exist; the lists, matrix, score table and run count of `ab-testing.md` follow the scenario files. |
| [test_ab_runner.py](test_ab_runner.py) | the A/B runner | The runner of `ab-testing.md` with a fake `claude`: every scenario prepared in isolation, prerequisite outputs copied, reruns refused, failures and contamination reported; the model sweep calls each model in its own campaign and `ab_sensitivity` scores selection, hand results and the spread threshold. No paid call. |
| [test_prompt_log.py](test_prompt_log.py) | `prompts/` | Experimental prompt identifiers, families, expected skills, statuses and run-log rows. |

### QGIS integration

The three QGIS modules (`test_qgis_layer_styling.py`, `test_qgis_project_builder.py` and
`test_qgis_map_illustration.py`) skip when PyQGIS is absent. The dedicated
[QGIS workflow](../.github/workflows/qgis.yml) provisions its own Ubuntu 24.04 worker and
runs them with `GEOSKILLS_REQUIRE_QGIS=1`, so a missing runtime fails that job. Locally,
with an existing QGIS/PyQGIS 3.34–3.x, use its Python interpreter and require the runtime
so that a missing installation cannot pass for a successful run:

```bash
GEOSKILLS_REQUIRE_QGIS=1 QT_QPA_PLATFORM=offscreen GDAL_PAM_ENABLED=NO python3 -m unittest discover -s tests -p 'test_qgis*.py' -v
```

The [five-skill review](review-2026-11-11.md) records the QGIS versions tested.

## Live tests

Use a working GDAL/PROJ environment, `curl`, `bash` and the optional Python dependencies;
the navigation and paginated WFS checks need GeoPandas.

```bash
GEOSKILLS_LIVE=1 python3 -m unittest discover -s tests -p 'test_live*.py' -v
```

| File | What it sends |
| --- | --- |
| [test_live.py](test_live.py) | The eight addresses of `data/adresses.csv` to the public geocoder, three reverse-geocoding points and a cadastral parcel; small WFS, WMS and WMTS extracts; WFS, navigation and download-catalogue discovery. |
| [test_live_enrichment.py](test_live_enrichment.py) | An advertised Atom page, two elevation points, a 20-sample profile, a short pedestrian route, a five-minute isochrone, three communes with one feature per WFS page, real ECQL attribute and BBOX predicates and a malformed filter. |
| [test_live_apicarto.py](test_live_apicarto.py) | The API Carto module description, an unpadded parcel code (HTTP 400 expected), every Saint-Mandé parcel in pages of 500, both Natura 2000 networks at a point, an urban-planning zone. |

Network or service failures are failures, never silent passes. The calls have timeouts
and small extents. The real ECQL tests do not establish universal EWKT compatibility.
Do not replace the fixtures with private data for a live run. In GitHub Actions, run
**Validate skills → Run workflow → Also run bounded requests to public IGN services**;
pushes and pull requests never enable it.

Live values (scores, labels, layer lists, parcel counts) drift. The scenario files date
them ("on 2026-11-09"); a test must not require a service to reproduce a historical
value or bug.

## Agent scenarios

### Anatomy of a scenario

```markdown
## CRS-05 — Area of a municipality                  ← identifier and English title

> Calcule la superficie de la commune de Saint-Mandé  ← prompt, in French, sent as is
> à partir de data/saint_mande.geojson.

**Expected skill:** `crs-reprojection-france`        ← the skill the agent must load

**Expected result:** about **90.6 ha** (0.906 km²),   ← reference values and tolerances
computed in Lambert-93.

- [ ] reprojects to EPSG:2154 (or uses a geodesic    ← checklist: what a correct run does,
  area) before measuring                                and the traps it must avoid
- [ ] does not measure in EPSG:4326 degrees, nor in
  EPSG:3857 (209 ha, about 2.3 times too large)
```

Some scenarios add a **Reference result** (a live value observed on a date) or a short
note on how the automated tests cover the same case.

### Kinds of scenarios

| Kind | Identifier | What it checks | A/B modes |
| --- | --- | --- | --- |
| Positive | `<PREFIX>-01`, `-02`… | The skill of the file is loaded and the result is right. | With and without the skills |
| Negative | `<PREFIX>-N1`, `-N2`… | A neighboring request does **not** load the skill of the file, which the **Expected skill** line names after "not": its description does not over-trigger. | With the skills only |
| Control | positive, marked *control* in the [matrix](ab-testing.md#scenario-matrix) | A task an agent should solve without the skill. If every scenario of a skill is a control, the skill adds nothing measurable. | Both |
| Chained | WFS-03 | Starts from the output of WFS-01; the runner copies it. | Both |

The *Watch in B* column of the matrix names the trap the skill is meant to prevent: if
the skill is useful, runs without it fail there.

### When a scenario passes

A scenario passes when the expected skill is loaded (or, for a negative one, the excluded
skill is not), the result matches the expected values within their tolerance, and every
checklist item is met. A conduct violation fails the run whatever the result: a software
installation, a download piped through `head` or `tail`, or an invented layer or field
name. [ab-testing.md](ab-testing.md#score-a-run) gives the scoring grid.

### Run one scenario by hand

Run scenarios **outside the repository**. Claude Code also reads the `CLAUDE.md` files of
parent directories, so a session started inside the clone sees the contributor guide and
can open `skills/` directly: acceptable for a quick trigger check, not for scoring.

The A/B runner prepares an isolated directory without calling an agent: save its block
from [ab-testing.md](ab-testing.md#runner) as `ab.sh` outside the repository, then:

```bash
source ab.sh
cd "$(AB_DRY=1 ab_run CRS-05 with manual)"   # copies the skills, data/ and an empty output/
cat prompt.txt
claude                                        # paste the prompt in a new session
```

Then check the skill loaded, compare `output/` with the expected result and go through
the checklist. Use a new identifier (`manual2`…) for each run: the runner refuses to
reuse a directory, which avoids stale files. To avoid statistics sidecars on source
rasters, use `GDAL_PAM_ENABLED=NO` for read-only inspection.

To install the skills with the Skills CLI instead (Node.js required):

```bash
npx skills add /path/to/geoskills -a claude-code -y              # from a local clone
npx skills add "ignfab/geoskills#<branch>" -a claude-code -y     # from a pushed branch
```

The CLI may use shared directories or symbolic links; refresh a copied installation
after editing a skill. To check discovery without installing anything:

```bash
npx skills add . --list                 # every skill, in family order
npx skills add ./skills/2-access --list # the skills of one family only
```

The scenarios need, depending on the case, GDAL/PROJ, `curl`, and optionally GeoPandas,
`rasterstats`, `pyarrow`, Matplotlib, Folium or PyQGIS; the
[scenario matrix](ab-testing.md#scenario-matrix) lists the needs of each one, and each
skill's README its supported environment. The BD TOPO lookup runs offline with the Python
standard library. Agents must not install a missing dependency. `gdal raster zonal-stats`
requires GDAL ≥ 3.12; older GDAL can use a masked single-zone crop or `rasterstats`.

### Measure what a skill adds

[ab-testing.md](ab-testing.md) runs every positive scenario with (A) and without (B) the
skills, three times each, and scores the difference. Starting a paid campaign is a
separate decision; `AB_DRY=1` prepares every directory for free.

### Model sensitivity

Skills installed with the Skills CLI are read by many agents and models. A skill that only
works because a large model guesses what it leaves implicit is model-sensitive. Two
layers check this:

- [test_skill_robustness.py](test_skill_robustness.py) runs on every push. It checks the
  text that a smaller model needs in order to choose correctly: a `Use when …` clause,
  exact skill names, and the way out at each tested boundary. For example, RAS-N1 expects
  `geopf-altimetry`, not `gdal-raster-processing`, for the elevation of one point, so
  `gdal-raster-processing` must name `geopf-altimetry`.
- The [model sweep](ab-testing.md#model-sensitivity) of the A/B runner is paid and runs on
  demand. It runs the same scenarios with several models (by default `haiku`, `sonnet`
  and `opus`), scores skill selection automatically and flags the skills whose score
  differs between models.

### Clean up

Offline tests remove their temporary directories. After a manual run, remove only the
directories and skill installations created for it; avoid `skills remove --all` when
unrelated skills are installed. Agent directories created under `tests/` are ignored by
git (see [.gitignore](.gitignore)).

## Fixtures

Small files in `data/`. The [fixture catalog](data/README.md) is the authoritative
description of their provenance, CRS, licences and traps; the table below maps each file
to the scenarios and tests that read it. Write generated files outside `data/`.
`saint_mande.geojson` and `mnt_dalles/` are extracts of IGN data (ADMIN EXPRESS, RGE ALTI),
under the [Licence Ouverte 2.0](https://www.data.gouv.fr/pages/legal/licences/etalab-2-0);
the synthetic files are invented.

| File | Content | Scenarios | Tests |
| --- | --- | --- | --- |
| `adresses.csv` | 8 addresses split across columns: valid, without postcode, overseas, unknown, empty | GEO-02, GEO-N1 | `test_live.py` |
| `points.csv` | 3 points (lon, lat) to reverse-geocode | GEO-03, GPD-01 | `test_geopandas.py`, `test_gdal_vector.py`, `test_live.py` |
| `points_gps.csv` | 3 GPS points, **latitude before longitude**, one of them in Réunion | CRS-01, CRS-N1, INT-02, VDQ-N2 | `test_workflows.py` |
| `points_lambert2e.csv` | 2 points in NTF extended Lambert II (EPSG:27572) | CRS-02 | `test_workflows.py` |
| `monuments_sans_prj/` | Shapefile of 3 Paris monuments in Lambert-93, **without a `.prj`** | CRS-03, GPD-02, INT-01 | `test_workflows.py`, `test_geopandas.py`, `test_raster_quality.py` |
| `saint_mande.geojson` | Boundary of Saint-Mandé (INSEE 94067), EPSG:4326, from ADMIN EXPRESS | CRS-05, RAS-02, RAS-05, WMS-02, GPD-01, GPD-03, GVB-N1, INT-N1, QLS-01, QPB-02, MAP-02, MAP-N1, TES-N2 | `test_workflows.py`, `test_geopandas.py`, `test_qgis_layer_styling.py` |
| `mnt_dalles/` | 10 m DEM of Saint-Mandé (RGE ALTI) in 2 ESRI ASCII tiles, **without a `.prj`** | RAS-01 to RAS-05, GPD-03, INT-01, ALT-N1, TES-N2 | `test_workflows.py`, `test_raster_quality.py`, `test_geopandas.py` |
| `admin_units_synthetic.geojson` | Three invented EPSG:4326 polygons: two neighbors with a detailed shared border and a small island | MS-01, MS-02, MS-04, MAP-01, MAP-03, MAP-N3 | `test_mapshaper.py`, `test_map_illustration.py` |
| `coverage_synthetic.geojson` | Nine invented EPSG:2154 parcels, each valid, with an overlap, an enclosed gap, a narrow gap and a sliver | VDQ-03, GVB-02, GVB-03 | `test_vector_quality.py`, `test_gdal_vector.py` |
| `communes_sans_cpg/` | Shapefile of 3 municipality points in Lambert-93, **CP1252 text without a `.cpg`** | GVB-01, GVB-02 | `test_gdal_vector.py` |
| `communes_points.geojson` | The same 3 points in EPSG:4326, with field names longer than 10 characters | GVB-04 | `test_gdal_vector.py` |
| `classes_synthetic.asc` | Invented 2 × 2 categorical grid, EPSG:2154, classes 0/1/5 and nodata 255 | RAS-06 | `test_raster_quality.py` |
| `geocoded_synthetic.csv` | Seven invented geocoding results: accepted, to review and unmatched | GEO-06 | `test_enrichment.py` |
| `elevation_points.csv`, `elevations_synthetic.json` | Two invented points with string IDs and their elevations, one missing | ALT-02, TES-N1 | `test_enrichment.py` |
| `aggregation_objects.geojson`, `aggregation_zones.geojson` | Five invented EPSG:2154 points (one on a border, one outside, one height missing) and three zones (one empty) | SPA-01, SPA-02, QPB-01, MAP-N2 | `test_spatial_aggregation.py` |
| `building_profile_municipalities.geojson`, `building_profile_buildings.geojson`, `building_profile_input.json` | Two invented 100 × 100 m EPSG:2154 municipalities and six buildings (an overlap, one crossing and one touching the border, one outside), with the manifest that points to them | MBP-01, MBP-02, MBP-03, MBP-N2, MBP-N3 | `test_municipality_building_profile.py` |
| `terrain_screening.asc`, `terrain_screening_aoi.geojson` | Invented 7 × 7 terrain grid with 10 m cells (EPSG:2154, no `.prj`, a valid zero and a nodata cell) and its 70 × 70 m area of interest | TES-01, TES-02, TES-03, ALT-N2, MAP-04 | `test_terrain_elevation_screening.py` |

The original references were supplied for GDAL 3.13; the stored fixture values were
also checked with GDAL 3.10.3 / PROJ 9.6.2 on 2026-09-30. Local checks use explicit
tolerances.

## Add or change a test

The checklist of the [contributor guide](../CLAUDE.md#checklist-for-a-new-skill) is the
reference. In short:

- **New skill:** create `tests/<skill-name>.md` with at least one positive and one
  negative scenario in the format above, add it to the [coverage table](#coverage-by-skill),
  then add its identifiers to `POSITIVE`/`NEGATIVE`, the matrix, the score table and the
  run count of [ab-testing.md](ab-testing.md). `test_scenarios.py` and `test_ab_runner.py`
  say what is missing.
- **Renamed skill:** rename its scenario file and update the `**Expected skill:**` lines,
  this guide and [ab-testing.md](ab-testing.md); keep the scenario identifiers and the
  French prompts, and record the old name in the [naming guide](../docs/skill-naming.md).
- **Offline test:** test the documented example itself with `read_example` or
  `run_example`, so that the skill text and the test cannot drift apart. Read inputs from
  `data/` rather than copying them inline, write only to a temporary directory and assert
  values with explicit tolerances.
- **New fixture:** keep it small, describe it in [data/README.md](data/README.md) and in
  the table above, and never put private data in it.
- **Live value:** date it in the scenario and compare runs of the same day.
- **Exploratory prompt:** add it to [prompts/catalog.md](prompts/catalog.md) before running
  it, then log each run in [prompts/runs.md](prompts/runs.md).

## Reviews and reports

The dated reviews record the checks and limits observed at the time, with the skill names
of that date. Use the commands above for a new run: a past pass is not a current guarantee
for live services.

| File | Content |
| --- | --- |
| [review-2026-10-12.md](review-2026-10-12.md) | Recent-skill review, reproduced defects, fixes and validation limits |
| [review-2026-10-27.md](review-2026-10-27.md) | Test audit, added edge cases and remaining coverage limits |
| [review-2026-10-28.md](review-2026-10-28.md) | Four added skills, workflow checks, live evidence and an agent pilot (not a full A/B evaluation) |
| [review-2026-11-11.md](review-2026-11-11.md) | Five new skills: executed fixtures, QGIS integration, family discovery and agent pilots (not a full A/B evaluation) |
| [review-2026-11-12.md](review-2026-11-12.md) | Audit of the scenarios and tests: standard scenario format, fixtures now tested, structure checks, model-sensitivity checks and sweep |
| [review-municipality-building-profile-2026-11-12.md](review-municipality-building-profile-2026-11-12.md) | First workflow: municipal indicator regressions and an independent portable-QGIS forward pilot |
| [reports/](reports/) | Machine-readable summaries of agent runs: the 2026-10-28 pilot, the 2026-11-11 five-skill pilots and the 2026-11-12 municipal building profile pilot, with environments and discovery checks |

## Glossary

| Term | Meaning |
| --- | --- |
| Scenario | A French prompt with its expected skill, expected result and checklist, in `tests/<skill-name>.md` |
| Positive / negative scenario | A request that must load the skill of its file / a neighboring request that must not |
| Mode A / mode B | A run with the skills of this repository installed / the same run without them |
| Control | A positive scenario an agent should pass even without the skill |
| Fixture | A small input file in `data/`, read by scenarios and tests |
| Skip | A test that did not run because an optional tool is missing; it is reported, not counted as a pass |
| Live test | A test that sends bounded requests to public IGN services, only with `GEOSKILLS_LIVE=1` |
| Model sweep | The same scenarios run with several models to find skills whose effect depends on the model |
| Experimental prompt | An exploratory request (`XP-NN`) logged in [prompts/](prompts/README.md) before it becomes a scenario |
