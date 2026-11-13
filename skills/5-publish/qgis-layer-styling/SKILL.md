---
name: qgis-layer-styling
description: Create and validate reusable QGIS QML styles for an existing local vector layer, including single symbols, categorized fields and graduated numeric classes. Use for vector symbology, colors, outlines, transparency and classification; not project assembly, labels, layouts or geometry editing.
---

# QGIS layer styling

Deliver a `.qml` and a renderer report for an existing layer. Project assembly belongs to
`qgis-project-builder`; geometry simplification belongs to `mapshaper-simplify`. Do not
edit geometries/attributes or promise labels, rule engines, SLD, layouts or atlases.
For a rendered map image or interactive HTML deliverable, use `map-illustration`.

## Prerequisites

Use the Python supplied with an **existing** QGIS installation. Check with
`python3 -c "from qgis.core import Qgis; print(Qgis.QGIS_VERSION)"`.
The helper checks QGIS 3.34–3.x; QGIS 4 needs separate API verification. Standalone Linux
runs use `QT_QPA_PLATFORM=offscreen`. Never install software or run interactive setup.
If absent, give the user the appropriate installation instructions; on configured
Debian/Ubuntu repositories the user can run `sudo apt install qgis python3-qgis`.
Do not substitute an XML file guessed from memory for a validated QGIS style.

## Inspect and create

1. Discover the actual file layer names, then load the selected local OGR URI. Inspect
   `isValid()`, `featureCount()`, `wkbType()`, `crs()`, `fields()` and `renderer().type()`.
   Read requested field values, missingness and range before choosing classification.
2. Write a rendering specification using [renderers](references/renderers.md). State
   symbol units, opacity, category/null policy and class method. Reject missing fields,
   empty layers and incompatible numeric types. Never assume a BD TOPO field name.
3. Resolve the [helper](scripts/style_layer.py) relative to this skill directory:

```bash
QT_QPA_PLATFORM=offscreen python3 scripts/style_layer.py input.geojson output/style.qml --spec style.json
QT_QPA_PLATFORM=offscreen python3 scripts/style_layer.py 'input.gpkg|layername=discovered_name' output/style.qml --spec style.json
```

Keep the command in the foreground. Save stdout as a separate, unused JSON report path
if needed. Output QML must be new. For an explicit overwrite request, preserve the old
style and choose a new path; the helper intentionally has no overwrite switch.

## Validate the output

Follow [QML round-trip](references/qml-roundtrip.md): a fresh compatible layer must load
the QML and retain renderer type, field, symbols, units, categories and ordered breaks.
The helper compares serialized renderer properties before/after reload. Independently
inspect the requested properties and source feature count/CRS; ensure source bytes are
unchanged. Report QGIS version, source/layer, output, geometry, units, classification,
nulls, unrendered values and limitations. A nonempty QML alone does not prove correctness.

## References

- [Renderers](references/renderers.md): specifications and classification choices.
- [QML round-trip](references/qml-roundtrip.md): reuse, verification and API sources.
