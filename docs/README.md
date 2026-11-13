# Documentation guide

This guide explains how the skills work, how to install them, which skill fits which
request, what each one needs on your machine and how to check what it produces. The
[repository README](../README.md) keeps the short catalog; each skill's own `README.md`
gives its details.

`geoskills` is a collection of agent skills created by [IGN](https://www.ign.fr/) for
geomatics and geospatial data processing, with a focus on the Géoplateforme, French
coordinate systems and open-source GIS tools. It aims to serve as a reference collection
and is still experimental: see [Limits and status](#limits-and-status).

## Contents

1. [How the skills work](#how-the-skills-work)
2. [Get started](#get-started)
3. [Choose a skill](#choose-a-skill)
4. [Chain skills into a workflow](#chain-skills-into-a-workflow)
5. [Tools and services each skill needs](#tools-and-services-each-skill-needs)
6. [Check the results](#check-the-results)
7. [Troubleshooting](#troubleshooting)
8. [Limits and status](#limits-and-status)
9. [Repository map](#repository-map)
10. [Contribute and validate](#contribute-and-validate)
11. [Dated evidence](#dated-evidence)

## How the skills work

A skill is a folder of instructions that a coding agent (Claude Code, Cursor, OpenCode or
another agent supported by the Skills CLI) loads when a request needs it. The agent then
runs ordinary commands on your machine (`ogr2ogr`, `gdalwarp`, `curl`, Python with
GeoPandas, PyQGIS) with the tools you already have.

| File | Read by | Content |
| --- | --- | --- |
| `SKILL.md` | The agent | A `name` and a `description` in its header, then the endpoint or entry command, the minimal syntax, the prerequisites and how to validate the output. |
| `references/*.md` | The agent, only when needed | Long-form details: formats, edge cases, service parameters. |
| `scripts/*.py` | The agent runs them | Tested helpers for steps that are easy to get wrong, such as paging an API or auditing an export. |
| `README.md` | You | When to use the skill and when to use another, what you get and how it is checked, requirements, installation, an example, contents and tests. |

An agent uses a skill in three steps:

1. When a session starts, it sees only the `name` and `description` of each installed skill.
2. When a request matches a description, it reads that skill's `SKILL.md`.
3. It opens a reference file or runs a helper script only when the task needs it.

The description is therefore what selects a skill. A request that states the expected
output ("download the BD TOPO buildings of Saint-Mandé to a GeoPackage") is matched more
reliably than a vague one ("get me some IGN data"). You can also name the skill in the
request: "use `geopf-wfs-download`".

Skills are written in English, but requests in other languages work: the test scenarios
are written in French to check that a French request selects the right English skill.

### What every skill makes the agent do

| Rule | What you will see |
| --- | --- |
| Never install software | When a tool is missing, the agent gives you the install command and stops; you run it yourself. |
| No interactive commands | Logins and setup wizards are left to you. |
| Discover before querying | Layer names, fields and CRSs come from the service or file metadata, not from memory. |
| Validate before reporting | The agent checks that the output is non-empty, in the expected CRS and of a plausible magnitude before calling it done. |
| Keep long commands visible | Downloads run in the foreground with progress, not hidden behind a filter. |
| Report what was done | Source, output, processing, validation and remaining issues, in the vocabulary of [output reports](output-reports.md). |
| Prefer a connected MCP server, never require one | When Geocontext, a PostGIS server or a QGIS server is connected and covers a step, the agent uses it first; otherwise it runs the documented commands. It never installs or configures a server. See [MCP servers](mcp-servers.md). |

## Get started

### 1. Install the skills

The skills are installed with the [Vercel Skills CLI](https://github.com/vercel-labs/skills),
which runs with Node.js (`npx`) and reads them directly from GitHub.

| Goal | Command |
| --- | --- |
| See the available skills | `npx skills add ignfab/geoskills --list` |
| Install every skill | `npx skills add ignfab/geoskills` |
| Install one skill | `npx skills add ignfab/geoskills --skill geopf-wfs-download` |
| Install one family | `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access` |
| Install for one agent | `npx skills add ignfab/geoskills -a claude-code` |
| Install for your whole user account | Add `-g` to any of the commands above |
| List installed skills | `npx skills list` |
| Update installed skills | `npx skills update` |
| Remove a skill | `npx skills remove geopf-wfs-download` |

Skills are installed in the current project by default. Each one lands in its own folder,
`<agent>/skills/<skill-name>/` (for Claude Code, `.claude/skills/<skill-name>/`); the family
folders only organize this repository. Start a new agent session after installing so that
the agent sees the new skills.

Seven skills were renamed on 2026-11-13 (for example `geopf-wms-wmts` became
`geopf-raster-download`). An installed copy keeps its old name until you install the new
one; the old names are not aliases. The [naming guide](skill-naming.md) lists the old and
current names.

Installing every skill is the simplest choice: the agent reads only the skills a request
needs. Install a family or single skills to keep the list short. Each skill works on its
own; related skills complement it but are not prerequisites.

### 2. Check the tools

Installing a skill does not install GDAL, GeoPandas, QGIS or Mapshaper. Check only the
tools for the requested operation and reuse an existing compatible environment. The
commands below are alternatives, not a bundle to install. See the
[dependency guide](dependencies.md) and
[Tools and services each skill needs](#tools-and-services-each-skill-needs).

| Toolset | Check | Install (you run it) |
| --- | --- | --- |
| GDAL and PROJ command-line tools | `gdalinfo --version`, `ogrinfo --version`, `projinfo EPSG:4326`, as needed | `sudo apt install gdal-bin` or `sudo apt install proj-bin` (Debian/Ubuntu); Conda alternatives: `conda install -c conda-forge libgdal-core` or `conda install -c conda-forge proj` |
| Python with GeoPandas | `python3 -c "import geopandas; print(geopandas.__version__)"` | `python3 -m pip install 'geopandas>=1.0,<2'` or `conda install -c conda-forge 'geopandas-base>=1.0,<2' pyogrio pyproj` |
| QGIS with its Python bindings (PyQGIS) | `python3 -c "from qgis.core import Qgis; print(Qgis.QGIS_VERSION)"` | `sudo apt install qgis python3-qgis` on configured Debian/Ubuntu repositories |

The service skills also use `curl` and Python 3. `mapshaper-simplify` needs the Mapshaper
CLI: `npm install --global mapshaper@0.7.83`, with Node.js 20.11 or later.
Add format drivers, transformation grids, raster statistics or rendering packages only
when the selected operation needs them. CSV summaries can use pandas without GeoPandas.

### 3. Ask for an outcome

Describe the result you want with the constraints that matter: area, format, CRS, output
folder. Some requests and the skill they should select:

| Request | Skill |
| --- | --- |
| "Download the BD TOPO buildings of Saint-Mandé to a GeoPackage in Lambert-93." | `geopf-wfs-download` |
| "Export the orthophoto over this bounding box to a GeoTIFF at 50 cm." | `geopf-raster-download` |
| "Which cadastral parcels and urban-planning zone lie at this point?" | `apicarto-query` |
| "Geocode the addresses of this CSV and list the doubtful matches." | `geopf-geocoding` |
| "What do these files I received contain, and are they ready to use?" | `geodata-intake` |
| "These GPS points land in the wrong place once converted to Lambert-93." | `crs-reprojection-france` |
| "Check that these parcels neither overlap nor leave gaps." | `vector-data-quality` |
| "Count the buildings and compute their mean height per municipality." | `spatial-aggregation` |
| "Compute the mean elevation of each municipality from this DEM." | `gdal-raster-processing` |
| "Simplify these administrative boundaries for a web map without breaking shared borders." | `mapshaper-simplify` |
| "Make a map image of these indicators for my report." | `map-illustration` |
| "Produce a building portrait of this municipality, with a QGIS project." | `municipality-building-profile` |
| "Within this area, find the terrain below 800 m with a slope under 10 %." | `terrain-elevation-screening` |

The [scenario files](../tests/README.md#agent-scenarios) contain more requests (in French),
each with its expected skill and a checklist of what a correct answer contains.

### 4. Check the result

Each skill ends with a validation step, and the agent's report says which checks passed,
failed or were not performed. Open the output yourself before relying on it: see
[Check the results](#check-the-results).

## Choose a skill

The skills are grouped into six families, one per question. Find the line that matches the
output you need; the last column names the skill to use instead when the request falls
outside the skill's scope.

### 1. Discover and select: which data should be used for this request?

| You want to | Skill | Not for |
| --- | --- | --- |
| Choose the Géoplateforme service for a need, or compare WMS, WMTS, WFS and TMS | [geopf-service-selection](../skills/1-discover/geopf-service-selection/README.md) | Running the task itself: use the dedicated access or calculation skill once the service is known. |
| Understand a BD TOPO class, attribute, type or special value for a given version | [bdtopo-schema-guide](../skills/1-discover/bdtopo-schema-guide/README.md) | Downloading layers (`geopf-wfs-download`), validating a whole production schema or computing indicators. The bundled guide covers a sourced building and road subset. |

### 2. Access and extract: how do I retrieve the right subset?

| You want to | Skill | Not for |
| --- | --- | --- |
| Download ready-made archives or tiles by territory, edition, format and CRS | [geopf-file-download](../skills/2-access/geopf-file-download/README.md) | Filtered features (`geopf-wfs-download`) or map images (`geopf-raster-download`). |
| Download filtered vector features (BD TOPO, ADMIN EXPRESS, cadastre) to GeoPackage, GeoJSON, GeoParquet, Shapefile or GML | [geopf-wfs-download](../skills/2-access/geopf-wfs-download/README.md) | Whole national products delivered as archives (`geopf-file-download`). |
| Export orthophotos, Plan IGN maps or elevation rasters to GeoTIFF | [geopf-raster-download](../skills/2-access/geopf-raster-download/README.md) | Vector features (`geopf-wfs-download`) or elevations at a few points (`geopf-altimetry`). |
| Write or debug a GeoServer `cql_filter` (attribute, spatial or temporal) for WFS or WMS | [geoserver-cql-filter](../skills/2-access/geoserver-cql-filter/README.md) | SQL queries or OGC API CQL2 filters. |
| Find the cadastral parcels, urban-planning zones, easements, protected areas or RPG crops at a point, in an area or by code | [apicarto-query](../skills/2-access/apicarto-query/README.md) | Address geocoding (`geopf-geocoding`), bulk national layers (`geopf-file-download`, `geopf-wfs-download`) or map images (`geopf-raster-download`). |
| Geocode addresses, places or parcels, reverse-geocode coordinates or review an already geocoded CSV | [geopf-geocoding](../skills/2-access/geopf-geocoding/README.md) | Reviewing an existing result needs no new request to the service. |

The Géoplateforme offers three routes to the same products; the right one depends on the
output:

| Route | Delivers | Skill |
| --- | --- | --- |
| Download API | Complete archives or tiles of a product, by territory and edition | `geopf-file-download` |
| WFS | Vector features filtered by area, attribute or layer, converted to the format you choose | `geopf-wfs-download` |
| WMS-R and WMTS | Raster images and grids (orthophotos, maps, elevation) over an extent | `geopf-raster-download` |

### 3. Prepare and check: is the data usable and compatible?

| You want to | Skill | Not for |
| --- | --- | --- |
| Inventory a delivery you received: formats, layers, CRSs, fields, extents and missing metadata | [geodata-intake](../skills/3-prepare/geodata-intake/README.md) | An already specified conversion, reprojection or repair: go straight to the skills below. |
| Choose a French CRS, reproject, convert GPS coordinates or heights, or diagnose a missing or wrong projection | [crs-reprojection-france](../skills/3-prepare/crs-reprojection-france/README.md) | — |
| Convert, reproject, filter, clip or merge vector files on the command line, fix garbled accents in a Shapefile, turn a CSV into points or run SQL | [gdal-vector-processing](../skills/3-prepare/gdal-vector-processing/README.md) | WFS downloads (`geopf-wfs-download`), Python workflows (`geopandas-vector-analysis`) or geometry repair (`vector-data-quality`). |
| Clip, reproject, resample, mosaic or convert rasters, build a COG or compute zonal statistics per polygon | [gdal-raster-processing](../skills/3-prepare/gdal-raster-processing/README.md) | Elevations at a few points (`geopf-altimetry`), counts of vector objects per zone (`spatial-aggregation`) or a full altitude and slope screening with candidate polygons (`terrain-elevation-screening`). |
| Audit and repair geometries, overlaps and gaps between polygons, duplicates, identifiers and schema | [vector-data-quality](../skills/3-prepare/vector-data-quality/README.md) | — |

### 4. Analyze and derive: what information should be computed?

| You want to | Skill | Not for |
| --- | --- | --- |
| Join, intersect, buffer, dissolve or clip layers in Python, or compute zonal statistics with rasterstats | [geopandas-vector-analysis](../skills/4-analyze/geopandas-vector-analysis/README.md) | Command-line work without Python (`gdal-vector-processing`). |
| Get terrain elevations at points or along a profile | [geopf-altimetry](../skills/4-analyze/geopf-altimetry/README.md) | Downloading or processing a full DEM (`gdal-raster-processing`), filtering a whole area by altitude (`terrain-elevation-screening`) or converting vertical datums (`crs-reprojection-france`). |
| Compute routes, isochrones or isodistances on the IGN road network | [geopf-routing](../skills/4-analyze/geopf-routing/README.md) | Straight-line buffers or network analysis on your own data (`geopandas-vector-analysis` or other local tools). |
| Describe one layer's attributes: distributions, categories, missing values, quantiles and units | [geospatial-descriptive-statistics](../skills/4-analyze/geospatial-descriptive-statistics/README.md) | Object-to-zone aggregation (`spatial-aggregation`), raster zonal statistics (`gdal-raster-processing`) or statistical inference. |
| Count, sum or average objects per polygon zone, or compute ratios with an explicit denominator | [spatial-aggregation](../skills/4-analyze/spatial-aggregation/README.md) | One-table summaries (`geospatial-descriptive-statistics`), generic overlays (`geopandas-vector-analysis`) or raster zonal statistics (`gdal-raster-processing`). |

### 5. Represent and publish: how do I make the result usable?

| You want to | Skill | Not for |
| --- | --- | --- |
| Simplify polygon boundaries while keeping shared borders, and export GeoJSON or TopoJSON for a web map | [mapshaper-simplify](../skills/5-publish/mapshaper-simplify/README.md) | Measurements and spatial analysis: keep the original geometry for those. |
| Create a reusable QGIS style (QML): single symbol, categories or graduated classes | [qgis-layer-styling](../skills/5-publish/qgis-layer-styling/README.md) | Project assembly (`qgis-project-builder`), a rendered map image or HTML map (`map-illustration`), labels or print layouts. |
| Assemble existing layers into a QGIS project (QGZ or QGS) that can be reopened and moved | [qgis-project-builder](../skills/5-publish/qgis-project-builder/README.md) | Creating a style on its own (`qgis-layer-styling`), an image export or a small HTML map (`map-illustration`), editing sources, print layouts or atlases. |
| Make a map image for a report or a slide (PNG by default, SVG or PDF), export an existing QGIS map, or a small interactive HTML map | [map-illustration](../skills/5-publish/map-illustration/README.md) | Computing the indicators it shows (`spatial-aggregation`, `geospatial-descriptive-statistics`), a reusable style (`qgis-layer-styling`), a new project (`qgis-project-builder`) or geometry simplification (`mapshaper-simplify`). |

### 6. Solve a business need: how do I chain the steps to reach an objective?

| You want to | Skill | Not for |
| --- | --- | --- |
| Produce the building portrait of one municipality: building count, built footprint without double counting, share of the territory built, heights and usages, optional QGIS project | [municipality-building-profile](../skills/6-workflows/municipality-building-profile/README.md) | Download alone (`geopf-wfs-download`), one-table statistics (`geospatial-descriptive-statistics`), indicators for several zones (`spatial-aggregation`) or project assembly alone (`qgis-project-builder`). |
| Filter an area of interest by altitude, optionally slope and connected area, and deliver candidate polygons with a coverage report | [terrain-elevation-screening](../skills/6-workflows/terrain-elevation-screening/README.md) | Elevations at a few points or along a profile (`geopf-altimetry`) or DEM clipping alone (`gdal-raster-processing`). It never concludes that a site is safe or suitable for a helicopter landing. |

Each [family page](../README.md#skills) also lists the skills of other families that serve
its question, and the gaps that remain.

## Chain skills into a workflow

A request can need several skills in sequence. The families follow the usual order:
discover, access, prepare, analyze, publish. Skip the stages a task does not need: a
delivery you already have starts at preparation, and a simple export stops after access.

When you ask for a chain, state the final output and the constraints that hold throughout
(area, CRS, formats, output folder). Ask the agent to keep the intermediate files and to
stop after a stage if you want to inspect it before the next one.

### Implemented workflows

`municipality-building-profile` fixes the methodological choices of a municipal building
portrait so that its numbers can be reconciled. It checks the municipal boundary, counts
each building once (including those crossing the border), measures the union of the
clipped footprints so that overlapping buildings do not inflate the built area, and
summarizes heights and usages only when their meaning is documented. It delivers a
GeoPackage, a CSV, a Markdown report and an audit JSON, and can hand over to
`qgis-layer-styling` and `qgis-project-builder` for a QGIS project.

`terrain-elevation-screening` keeps one extent, grid, vertical reference and missing-data
rule from DEM acquisition to delivery. It clips the elevations, optionally derives slope,
applies the thresholds you state (there is no default altitude), vectorizes the selected
cells and reports coverage, so that "no candidate" and "no data" stay distinct. It
delivers an elevation GeoTIFF, a selection mask, candidate polygons in a GeoPackage and a
short report. Its polygons are terrain-screening candidates: altitude alone does not show
that ground is flat, obstacle-free or usable for a landing.

### Typical chains

| Goal | Chain |
| --- | --- |
| Make a received delivery usable | `geodata-intake`, then `crs-reprojection-france`, `vector-data-quality`, `gdal-vector-processing` or `gdal-raster-processing`, depending on what the inventory finds |
| Boundaries for a web map | `geopf-wfs-download` (ADMIN EXPRESS) → `vector-data-quality` → `mapshaper-simplify`, as described in the [mapshaper-simplify guide](../skills/5-publish/mapshaper-simplify/README.md) |
| Mean elevation per municipality | `geopf-wfs-download` (boundaries) and a DEM from `geopf-file-download` or `geopf-raster-download` → `gdal-raster-processing` (zonal statistics) |
| Territorial indicators in QGIS | `spatial-aggregation` → `qgis-layer-styling` → `qgis-project-builder` |
| Indicator map for a report | `spatial-aggregation` or `geospatial-descriptive-statistics` → `map-illustration` |

### Candidate workflows

The [workflow family page](../skills/6-workflows/README.md) lists chains that have building
blocks but no dedicated skill yet: territorial diagnosis, accessibility, exposure and
change monitoring. You can already ask for them; the agent combines the existing skills,
but no skill fixes the method. Check the choices it reports: which objects are counted,
which spatial predicate is used, which denominator a ratio relies on.

## Tools and services each skill needs

The [family dependency tables](dependencies.md#by-family) distinguish base routes from
conditional additions. Tools listed as alternatives are not all required together.

| Skill | Local tools | Network |
| --- | --- | --- |
| `geopf-service-selection` | None; `curl` for optional discovery requests | Official guides and service metadata |
| `bdtopo-schema-guide` | None; Python 3 (standard library) for the optional lookup | None; official sources can be checked online |
| `geopf-file-download` | `curl`, standard-library Python; an archive reader matching the format (Python can test ZIP); GDAL for spatial validation | Géoplateforme Download API |
| `geopf-wfs-download` | GDAL with WFS support and the requested output driver, `curl`; standard-library Python for the GeoPackage audit | Géoplateforme WFS |
| `geopf-raster-download` | GDAL with the WMTS and WMS drivers | Géoplateforme WMTS and WMS-R |
| `geoserver-cql-filter` | None to write a filter; `curl` to send it | The GeoServer you query |
| `apicarto-query` | `curl`, Python 3; GDAL to convert and check results | API Carto; a key only for the wine appellation module (`aoc`) |
| `geopf-geocoding` | `curl`; Python 3 for the helpers; `jq` and GDAL optional | Géoplateforme geocoding API; none to review an existing result |
| `geodata-intake` | Reader matching the input: GDAL for GIS files or standard-library Python for CSV/JSON; archive reader only for archives | None |
| `crs-reprojection-france` | GDAL, PROJ command-line tools or pyproj, according to the operation | Only for online metadata or a required missing transformation grid; fetch its exact filename |
| `gdal-vector-processing` | GDAL ≥ 3.4 (≥ 3.7 for `ogrinfo -json`; Arrow/Parquet support for GeoParquet) | None |
| `gdal-raster-processing` | GDAL CLI ≥ 3.1 (≥ 3.12 for `gdal raster zonal-stats`, ≥ 3.13 for COG validation); matching Python bindings/utilities only for recipes using them | None, except for remote rasters |
| `vector-data-quality` | GeoPandas ≥ 1.0 and Shapely ≥ 2.0 (≥ 1.1 and ≥ 2.1 for coverage checks); GDAL optional (≥ 3.12 for `gdal vector check-geometry`) | None |
| `geopandas-vector-analysis` | GeoPandas ≥ 1.0; pyarrow for GeoParquet; rasterstats for zonal statistics | None, except to read WFS data |
| `geopf-altimetry` | `curl`, Python 3 | Géoplateforme Elevation API |
| `geopf-routing` | `curl`, standard-library Python for JSON; GDAL or GeoPandas for spatial checks or format conversion | Géoplateforme Navigation API |
| `geospatial-descriptive-statistics` | pandas; GeoPandas and Shapely for vector inputs | None |
| `spatial-aggregation` | GeoPandas ≥ 1.0, pandas, Shapely | None |
| `map-illustration` | GeoPandas ≥ 1.0 with Matplotlib ≥ 3.7 for static vectors, or with Folium ≥ 0.16 for HTML (Matplotlib also for numeric colours); Rasterio/Matplotlib for raster previews; existing PyQGIS 3.34–3.x for QGIS maps | None for local files; HTML loads external browser resources, and QGIS projects may use remote providers |
| `mapshaper-simplify` | Mapshaper CLI (0.7.83 tested) and Node.js ≥ 20.11 | None; the [Mapshaper web application](https://mapshaper.org/) is a manual alternative |
| `qgis-layer-styling` | PyQGIS from QGIS 3.34–3.x | None |
| `qgis-project-builder` | PyQGIS from QGIS 3.34–3.x | Only for an optional public basemap |
| `municipality-building-profile` | GeoPandas ≥ 1.0, Shapely ≥ 2, Pyogrio; GDAL and `curl` for online extraction; PyQGIS only for a QGIS project | Géoplateforme WFS, only when data is extracted online |
| `terrain-elevation-screening` | GDAL ≥ 3.3 with matching Python bindings and NumPy (`gdaldem`, `gdal_calc.py`, `gdal_polygonize.py`); `curl` for online discovery | Géoplateforme services, only when the DEM is discovered online |

The requests documented by the skills use public endpoints without credentials; only the
API Carto `aoc` module needs a key. Some other Géoplateforme APIs (extraction, standards
validation, usage statistics) require authentication: `geopf-service-selection` describes
them, and the agent leaves any login to you. Behind a proxy, `curl`, GDAL and Python read
the standard `http_proxy` and `https_proxy` variables; make sure the agent's shell has
them. On a machine without a display, run the QGIS skills with `QT_QPA_PLATFORM=offscreen`.

### Optional MCP servers

Most skills use a connected MCP server first for part of their work, and their
commands otherwise: [Geocontext](https://github.com/ignfab/geocontext) for Géoplateforme
reference data (a place, an elevation, what lies at a point, the schema or a count of a
WFS layer), a PostGIS server for data already in a database, and a QGIS server for the
QGIS session you have open. No server is required, and the agent never installs or
configures one: connecting a server is your decision. [MCP servers](mcp-servers.md) lists
what each skill does with which server, what stays with its commands, and how to connect
Geocontext.

## Check the results

The agent's report should cover five points for each output, described in
[output reports](output-reports.md):

| Point | What to look for |
| --- | --- |
| Source | Input file or service, dataset or layer, edition and access date when known |
| Output | Actual path, format, CRS and units, extent, feature or row count, raster size |
| Processing | Selection, transformations and the parameters needed to reproduce the result |
| Validation | Checks performed and observed values, marked passed, failed or not performed |
| Issues | Errors, warnings to review, missing metadata and open choices |

Some words have a precise meaning. `consistent` means that counts and identifiers agree,
not that a download is transactionally complete. `accepted` means that a geocoding result
meets the stated policy, not that the address is proven correct. `unknown` means that the
metadata does not establish a value: the skills do not invent a CRS, date, licence or
expected count. In the same way, a QGIS project is not declared valid before it has been
reopened, and a remote layer is not declared rendered before rendering was checked.

Quick checks you can run yourself:

| Output | Command | Look for |
| --- | --- | --- |
| Vector file | `ogrinfo -so -al output.gpkg` | Feature count, CRS, extent and fields |
| Raster | `gdalinfo output.tif` | Size, CRS, pixel size, nodata value and extent |
| CSV | `head -5 output.csv` | Expected columns, identifiers kept as text (leading zeros intact) |
| QGIS project | Open it in QGIS | Every layer present, no missing-source warning |
| Map image or HTML map | Open it at its intended size, or in a browser | Readable title and legend, expected features, working zoom and tooltips |

Check coordinates against the declared CRS, units and area of use; coordinate ranges
alone do not identify a CRS. For example, Lambert-93 (EPSG:2154) uses metres, roughly
100,000 to 1,250,000 east and 6,050,000 to 7,110,000 north over mainland France.
Small values can suggest longitude/latitude but require confirmation from metadata or
control points. Preserve a suitable requested or existing CRS; Lambert-93 is a conditional
default for applicable metropolitan-France tasks. See [CRS handling](crs-handling.md).

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| The agent does not use any skill | The skills are not installed for this agent or scope, or the session started before the installation | Run `npx skills list`, install with the right `-a` or `-g` option, then start a new session |
| The agent picks a neighboring skill | The request does not state the expected output clearly | State the output (file, format, indicator) or name the skill; see [Choose a skill](#choose-a-skill) |
| The agent stops and prints an install command | A required tool is missing; skills never install software | Run the command yourself, or point the agent to an existing environment, then ask again |
| `gdalinfo --version` fails, for example with an undefined `sqlite3_total_changes64` symbol | A broken GDAL/SQLite installation | Repair it or use a clean environment, such as a conda-forge GDAL |
| A GDAL driver (GeoParquet, WFS, WMTS) is reported missing | Your GDAL build does not include it | See the requirements in the skill README; for a missing GeoParquet driver in an existing Conda GDAL environment: `conda install -c conda-forge libgdal-arrow-parquet` |
| A Géoplateforme request returns HTTP 5xx or times out | The service is temporarily unavailable, or a proxy blocks the request | Retry later and check the proxy variables; the skills are written to report the failure, not to present a partial result as complete |
| Accents are garbled after reading a Shapefile | The `.cpg` file is missing and the text is in CP1252 | Ask for `gdal-vector-processing`, which detects and sets the encoding |
| Points land in the wrong place | Latitude and longitude are swapped, or the source CRS is wrong or missing | Ask for `crs-reprojection-france`, which checks axis order and diagnoses missing projections |
| An installed skill still has an old name, such as `geopf-services` or `apicarto` | The skill was renamed on 2026-11-13; installed copies are not renamed automatically | Install the current name, then remove the old copy after checking it has no local changes; see the [naming guide](skill-naming.md) |
| The agent runs commands although an MCP server is connected | The server's tools are not in this session, or the skill keeps that step for its commands (file exports, bulk data, validated styles and projects) | Check that the tools appear in the agent's tool list, then see [MCP servers](mcp-servers.md) for what each skill does with a server |
| A QGIS skill fails on a server | No display, or the Python used is not the one supplied with QGIS | Use the QGIS Python and set `QT_QPA_PLATFORM=offscreen` |

## Limits and status

- **Experimental.** Automated tests and agent pilots exist, but no full A/B campaign has
  yet measured what each skill adds; see the [A/B protocol](../tests/ab-testing.md).
- **Live services change.** Results recorded against Géoplateforme services describe the
  date of the run. Rerun the [live tests](../tests/README.md#live-tests) before relying on
  a service's current behavior.
- **France first.** Service, CRS and data-model skills target French data. The GDAL,
  GeoPandas, QGIS, Mapshaper and map illustration skills apply to data from anywhere.
- **Licences.** Check the licence of each dataset you download; a report records it only
  when the metadata states it.
- **MCP routes are not measured yet.** The scenarios run without MCP servers. Geocontext
  is a prototype whose tools change between versions, and the PostGIS route is guidance
  without tested SQL recipes; see [MCP servers](mcp-servers.md).
- **Gaps.** Not covered yet: comparing candidate products by resolution and edition;
  change detection between editions; network analysis on local data; terrain derivatives
  beyond the `gdaldem` one-liners; processing inside a PostGIS database as a skill of its
  own; styles other than vector QML; print layouts, atlases
  and delivery metadata; dedicated workflows for territorial diagnosis, accessibility,
  exposure and change monitoring. The family pages keep this list up to date.

## Repository map

```text
README.md                  Catalog, installation and French summary
CLAUDE.md                  Contributor conventions (also exposed as AGENTS.md)
docs/                      This guide, MCP servers, report conventions, naming guide, landscape study
skills/<family>/README.md  Family page: question, skills, how to choose, tools, related skills, gaps
skills/<family>/<skill>/   One skill: SKILL.md, README.md, references/, scripts/
tests/                     Automated tests, scenario files, fixtures, A/B protocol, reviews
tests/prompts/             Experimental prompts and the log of their runs
.github/                   Validator, CI workflows and pull request template
```

## Contribute and validate

| Document | Purpose |
| --- | --- |
| [Contributing conventions](../CLAUDE.md) | Layout, families, language, agent conduct and the checklist for a new skill. Also exposed as `AGENTS.md`. |
| [Skill names and families](skill-naming.md) | Naming convention, review of all skills and the correspondence between old and current names. |
| [MCP servers](mcp-servers.md) | The optional Geocontext, PostGIS and QGIS servers: the rule, what each skill does with them and how to connect one. |
| [Output reports](output-reports.md) | Shared terminology and the evidence to include for each kind of output. |
| [Test guide](../tests/README.md) | The kinds of tests, which ones to run for a given change, what CI runs, how to read the skips, coverage by skill, fixtures and a glossary. |
| [Fixture metadata](../tests/data/README.md) | Provenance, coordinate systems and intentional traps of the test inputs. |
| [A/B protocol](../tests/ab-testing.md) | Compare agent behavior with and without the skills, and across models; a protocol is not a completed campaign. |
| [Runtime dependencies](dependencies.md) | Minimal requirements by family, conditional packages and reuse of existing environments. |
| [CRS handling](crs-handling.md) | Source, analysis and delivery CRSs; conditional Lambert-93 default, units and custom definitions. |
| [Experimental prompts](../tests/prompts/README.md) | Catalog and append-only record of exploratory agent runs. |

Before proposing a change, run the validator and the offline tests from the repository
root:

```bash
python3 -m pip install -r tests/requirements.txt
python3 .github/validate-skills.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

Report a problem or propose a skill in the
[GitHub issues](https://github.com/ignfab/geoskills/issues).

## Dated evidence

Reviews preserve what was checked at their stated date. Use the current test guide to run
new checks; do not reinterpret an earlier partial run as a later success. Historical skill
names remain as recorded; see the [name correspondence](skill-naming.md) for current names.

| Document | Scope |
| --- | --- |
| [2026-11-13 MCP review](../tests/review-mcp-servers-2026-11-13.md) | Optional MCP routes: checks against the live Geocontext service, paper simulations with a small model, defects fixed and limits. |
| [2026-11-12 review](../tests/review-2026-11-12.md) | Scenario and test audit: standard scenario format, fixtures tied to their tests, structure checks and model-sensitivity checks. |
| [2026-11-12 municipal workflow review](../tests/review-municipality-building-profile-2026-11-12.md) | First workflow, independently checked building indicators and a portable QGIS forward pilot. |
| [2026-11-11 review](../tests/review-2026-11-11.md) | Five complementary skills, issues and merged PRs, QGIS integration, discovery and actual agent pilots. |
| [2026-10-28 review](../tests/review-2026-10-28.md) | Intake, downloads, elevation, routing and report conventions. |
| [2026-10-27 review](../tests/review-2026-10-27.md) | Test coverage audit, edge cases and limits. |
| [2026-10-12 review](../tests/review-2026-10-12.md) | Earlier skill defects, fixes and validation. |
| [Landscape study](landscape.md) | Comparison observed on 2026-10-27, with dated implementation follow-ups. |

Return to the [repository README](../README.md).
