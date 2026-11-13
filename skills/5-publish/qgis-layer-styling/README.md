# qgis-layer-styling

**Family:** [5. Represent and publish](../README.md).

Create reusable vector QML for an existing local layer and verify it in a fresh layer
instance. The agent inspects the layer, writes a rendering specification and runs a PyQGIS
helper that builds a single-symbol, categorized or graduated renderer, saves it as a new
`.qml` and reloads it to confirm that the renderer survives the round trip.

## When to use it

- Give a polygon layer an outline without fill, or set colors, line widths, marker sizes
  and transparency, and save the result as a reusable QML.
- Color a layer by the values of a categorical field, with an explicit category for
  missing or unseen values.
- Classify a numeric field into graduated classes with stated breaks, for example three
  equal intervals, and report the values left unrendered.
- Prepare QML that `qgis-project-builder` can later load into a project.

## When to use another skill

- Assemble layers into a QGIS project, set its extent or layer order, without creating a
  new style: [`qgis-project-builder`](../qgis-project-builder/README.md).
- Simplify geometries for display: [`mapshaper-simplify`](../mapshaper-simplify/README.md).
- A rendered map image or an interactive HTML map: [`map-illustration`](../map-illustration/README.md).
- Labels, rule-based renderers, SLD, print layouts and atlases are not covered by any
  skill yet (see [Not covered yet](../README.md#not-covered-yet)).

## What you get

- A new `.qml` file. Existing outputs are refused; the helper has no overwrite switch, so
  an overwrite request gets a new path and the old style is preserved.
- A JSON report on stdout: source, output, QGIS version, feature count, CRS, renderer,
  field, specification, symbol units, null count and null policy.
- Three renderers: single symbol (color, outline, no fill, size, opacity, units in `mm`
  or map units); categorized from the actual non-null values, with a final
  `Missing / other` category for null and unseen values (at most 100 categories); and
  graduated from explicit, strictly increasing breaks that cover every observed value,
  where null values are not rendered and are counted.
- Checks before reporting: the helper saves a temporary QML, reloads it into a fresh layer
  and compares the serialized renderer before and after. The agent also inspects the
  requested properties and the source feature count and CRS, and checks that source bytes
  are unchanged.

Missing fields, empty layers, non-numeric fields for graduated classes, infinite values
and breaks that do not strictly increase or cover the observed values are rejected; field
names are discovered, never assumed. Without PyQGIS the
agent reports the limitation instead of writing QML from memory. A nonempty QML alone does
not prove correctness, and a headless round trip does not establish cartographic
readability at every scale. The skill never edits geometries or attributes.

## Requirements

- An existing QGIS/PyQGIS 3.34–3.x with compatible Qt, used through the Python supplied with
  QGIS. QGIS 4 needs separate API verification. Check with
  `python3 -c "from qgis.core import Qgis; print(Qgis.QGIS_VERSION)"`.
- Headless runs use `QT_QPA_PLATFORM=offscreen`.
- No network service or API key: the helper works on local vector files.

If QGIS is absent, the user can install it (for configured Debian/Ubuntu repositories:
`sudo apt install qgis python3-qgis`). The agent never installs software or runs
interactive setup.

## Installation

```bash
npx skills add ignfab/geoskills --skill qgis-layer-styling
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/5-publish`.

## Example

> Apply a red outline without fill to `data/saint_mande.geojson` and save a reusable QGIS
> QML style under `output/`. Check that it reloads without modifying the source.

```bash
QT_QPA_PLATFORM=offscreen python3 scripts/style_layer.py input.geojson output/style.qml --spec style.json
QT_QPA_PLATFORM=offscreen python3 scripts/style_layer.py 'input.gpkg|layername=discovered_name' output/style.qml --spec style.json
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Workflow and validation. |
| [scripts/style_layer.py](scripts/style_layer.py) | Single, categorized and explicit-break renderers, with QML reload check. |
| [references/renderers.md](references/renderers.md) | Rendering specifications, null policies and classification choices. |
| [references/qml-roundtrip.md](references/qml-roundtrip.md) | Saving, reusing and verifying QML, with API sources. |

## Tests

[Scenarios](../../../tests/qgis-layer-styling.md): French agent prompts, 2 positive +
1 negative. [test_qgis_layer_styling.py](../../../tests/test_qgis_layer_styling.py) reloads
helper QML on independent layers and needs PyQGIS ([QGIS integration](../../../tests/README.md#qgis-integration)).
Functional checks ran on QGIS 3.44.9 locally; dedicated CI also checks Ubuntu 24.04’s
QGIS 3.34 series. Custom graduated label formatting is set explicitly to survive QML reload.

## Related skills

- [`qgis-project-builder`](../qgis-project-builder/README.md) can consume the QML in a
  project, but is not needed to create it.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  uses this skill for the optional map of its building portrait.
