# qgis-layer-styling

Create reusable vector QML and verify it in a fresh layer instance.

## Requirements

Existing QGIS/PyQGIS 3.34–3.x with compatible Qt; headless runs use `QT_QPA_PLATFORM=offscreen`.
If absent, the user can install QGIS (for configured Debian/Ubuntu repositories:
`sudo apt install qgis python3-qgis`). Agents never install dependencies.

## Install

```bash
npx skills add ignfab/geoskills --skill qgis-layer-styling
```

## Contents

- [SKILL.md](SKILL.md): workflow and validation.
- [style_layer.py](scripts/style_layer.py): single, categorized and explicit-break renderers.
- [Renderers](references/renderers.md) and [QML round-trip](references/qml-roundtrip.md).
- [French scenarios](../../../tests/qgis-layer-styling.md).

Scope is vector styles only, not labels, layouts or project composition. `qgis-project-builder`
can consume the QML but is not needed to create it. Sources are opened read-only; existing
outputs are refused. Missing PyQGIS is an explicit limitation, never a successful XML fallback.

Functional checks ran on QGIS 3.44.9 locally; dedicated CI also checks Ubuntu 24.04’s
QGIS 3.34 series. Custom graduated label formatting is set explicitly to survive QML reload.
