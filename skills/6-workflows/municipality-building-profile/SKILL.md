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
   with `geopf-services` and `geopf-wfs-download`. Retrieve **whole building polygons**
   covering the boundary; do not clip them before this workflow. Record source, edition or
   unknown, access date and extraction completeness evidence.
2. Inspect local layers, fields, CRSs and geometry (`geodata-intake`, `vector-data-quality`).
   Do not guess a CRS, convert an ambiguous ID, repair geometry or deduplicate silently.
   Choose a suitable projected metre CRS using `crs-reprojection-france`; Lambert-93 is
   suitable for metropolitan France, not a default for overseas municipalities.
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
assignment belongs to `spatial-aggregation`, and overlays to `geopandas-basics`.
6. If requested, follow [delivery and QGIS](references/delivery.md): optional
   `qgis-layer-styling` creates QML and `qgis-project-builder` consumes the generated
   `qgis-project.json`. These skills are not hard installation dependencies. Finish the
   analytic bundle even when optional QGIS is unavailable, and report that limitation.

## Validate the output

Reopen `profile.gpkg`: municipality, selected buildings and union footprint must have the
declared metric CRS; the municipality layer has one row even for an empty building set.
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
