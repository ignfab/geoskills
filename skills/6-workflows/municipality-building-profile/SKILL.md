---
name: municipality-building-profile
description: Produce a one-municipality building portrait from local or discovered IGN data, combining a checked boundary, building counts, union footprint coverage, height and usage summaries, and optional QGIS delivery. Use when the user wants a municipal building diagnosis with data and indicators. For downloads alone use geopf-wfs-download; for one-table statistics use geospatial-descriptive-statistics; for multi-zone indicators use spatial-aggregation; for project assembly alone use qgis-project-builder.
---

# Municipality building profile

Deliver a coherent building portrait for **one identified municipality**: GeoPackage,
indicator CSV, Markdown report and audit JSON; optionally a styled QGIS project. Count
source building objects, never infer dwellings, inhabitants, floor area or building volume.
This workflow owns the selection, common statistical population and reconciliation across
stages. Use related skills when available; the local helper works independently of them.

## MCP servers

Optional. Supplied local files come first (step 1). When step 1 needs online discovery and
the [Geocontext](https://github.com/ignfab/geocontext) MCP server is connected (tools
often prefixed `mcp__geocontext__`), use it first:

- `geocode`, then `adminexpress` at that point, identify the municipality: its INSEE code
  and a reusable `feature_ref`. The first `geocode` candidate can be a namesake elsewhere
  or another object of the right municipality: check `fulltext` and `kind` as well as
  `city` and `zipcode`. When they do not match, add the postcode to the text, not the
  department name, or take another candidate.
- `gpf_search_types` and `gpf_describe_type` give the building layer and its property
  names, from a schema catalogue bundled with the server, not from the service itself:
  confirm them on the service before the download.
- `gpf_count_features`, filtered by intersection with that `feature_ref`, counts the
  buildings intersecting the municipality. Use it as a cross-check of the helper's
  selected count: it matched exactly on Saint-Mandé on 2026-11-13 (1,741), leaving out the
  3 buildings that only touch the boundary. Report both numbers. It is not the
  completeness evidence of the bounding-box extract, which needs a count for the same
  filter.

Tool and parameter names differ in Geocontext 0.9 (`gpf_wfs_search_types`,
`gpf_wfs_describe_type`, `gpf_wfs_get_features` with `result_type: "hits"` and
`spatial_operator: "intersects_feature"`): read the tool list and the input schemas of the
connected server. Still download the municipality boundary and the whole building polygons
with `geopf-wfs-download`, even when a Geocontext layer tool could return geometries: its
output stops at 5,000 objects and is meant for map display, not for a checked extract.
Without Geocontext, or when a call fails, follow step 1 as written. Never install,
configure or start an MCP server yourself.

## Prerequisites

Check `python3 -c "import geopandas, pandas, shapely, pyogrio; print(geopandas.__version__)"`.
The helper needs GeoPandas ≥ 1.0, Shapely ≥ 2 and Pyogrio. If missing, give the user
`python3 -m pip install 'geopandas>=1.0,<2' pyogrio`; **never install software yourself** or
run interactive setup. Online extraction additionally needs working `ogrinfo`, `ogr2ogr`
and `curl` (user-run Debian/Ubuntu command: `sudo apt install gdal-bin curl`). QGIS/PyQGIS
3.34–3.x is needed only for a requested project; give a missing-tool limitation, not a fake QGZ.

## Build the portrait

1. Identify the municipality by its **string identifier**, resolving ambiguous names.
   Prefer supplied local files. Otherwise follow [discovery and acquisition](references/acquisition.md)
   with `geopf-service-selection` and `geopf-wfs-download`. Retrieve **whole building polygons**
   covering the boundary; do not clip them before this workflow. Record source, edition or
   unknown, access date and extraction completeness evidence.
2. Inspect local layers, fields, CRSs and geometry (`geodata-intake`, `vector-data-quality`).
   Do not guess a CRS, convert an ambiguous ID, repair geometry or deduplicate silently.
   Preserve a suitable requested/existing projected analysis CRS with known linear units.
   The helper converts squared units to m², including feet; it accepts custom definitions.
   Lambert-93 is only a fallback for suitable metropolitan-France tasks. Use
   `crs-reprojection-france` for French/overseas choices; do not force it on other regions.
3. Prepare the [input manifest](references/manifest.md) from that metadata. Verify height
   units, missing-value codes and usage definitions before selecting fields. For BD TOPO,
   use `bdtopo-schema-guide` when its versioned subset applies; otherwise consult the
   delivery's documentation. Omit unverified optional measures and explain the omission.
4. Apply the [indicator method](references/indicators.md): count unique IDs with a
   **positive-area intersection**, exclude touch-only objects, clip footprints and union
   them before measuring coverage. Height/usage distributions describe that same set of
   whole source objects. Report boundary-crossing counts as non-additive across municipalities.
5. Resolve the helper relative to this installed skill directory and run in the foreground:

```bash
python3 scripts/build_profile.py profile-input.json output/building-profile
```

The output directory must be new. Empty inputs and partial extracts are reported explicitly;
zero observed buildings does not prove that the municipality contains no buildings.
For additional distributions use `geospatial-descriptive-statistics`; generic multi-zone
assignment belongs to `spatial-aggregation`, and overlays to `geopandas-vector-analysis`.
6. If requested, follow [delivery and QGIS](references/delivery.md): optional
   `qgis-layer-styling` creates QML and `qgis-project-builder` consumes the generated
   `qgis-project.json`. These skills are not hard installation dependencies. Finish the
   analytic bundle even when optional QGIS is unavailable, and report that limitation.

## Validate the output

Reopen `profile.gpkg`: municipality, selected buildings and union footprint must have the
declared analysis CRS with correctly converted m² fields; the municipality layer has one
row even for an empty building set.
Reconcile selected + touch-only + outside objects with input count, height status counts
and usage frequencies with selected count. Check union area ≤ summed clipped areas and
municipality area; coverage must lie in [0, 100]. The helper reopens every layer and the
CSV/JSON and checks input hashes. Inspect the map/extent and representative indicators too.
Report source editions, completeness status, field semantics, cross-boundary IDs, overlap
excess, duplicate geometries and missing measures. A partial extract stays partial after
successful file validation. For QGIS, reopen the actual project and relocate the full
bundle before claiming portability. Never report an uncreated project as validated.
After that optional stage, enrich the audit/report with the actual project checks so the
initial analytic-only status does not contradict the final delivery.

## References

- [Discovery and acquisition](references/acquisition.md): local-first routing and bounded WFS extraction.
- [Input manifest](references/manifest.md): discovered fields, source semantics and completeness.
- [Indicator method](references/indicators.md): population, boundary/overlap rules and empty inputs.
- [Delivery and QGIS](references/delivery.md): artifact checks and optional cartographic handoff.
