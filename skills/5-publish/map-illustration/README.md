# map-illustration

**Family:** [5. Represent and publish](../README.md).

Static-first cartographic illustrations, with optional interactive HTML. Reuse QGIS when
its styles or project are already useful; otherwise use a small Python rendering path.
No application server, web build pipeline or mandatory QGIS installation.

## Requirements

- Static vectors: GeoPandas ≥ 1.0 and Matplotlib ≥ 3.7 (includes Pillow).
- Interactive vectors: GeoPandas ≥ 1.0 and Folium ≥ 0.16; thematic colours also use Matplotlib.
- Existing QGIS project export: QGIS/PyQGIS 3.34–3.x and Qt.
- Optional raster preview without QGIS: Rasterio and Matplotlib.

For Python rendering the user can run `python3 -m pip install geopandas matplotlib folium`;
for QGIS on configured Debian/Ubuntu systems, `sudo apt install qgis python3-qgis`.
Agents check existing environments and never install dependencies themselves.

## Install

```bash
npx skills add ignfab/geoskills --skill map-illustration
```

## Contents

- [SKILL.md](SKILL.md): selection, rendering and visual checks.
- [render_vector.py](scripts/render_vector.py): PNG by default; optional SVG/PDF/HTML,
  continuous numeric scale, missing-value display, selected tooltips and size report.
- [export_qgis.py](scripts/export_qgis.py): existing project styles/visible layers to PNG.
- [Design/size](references/design-and-size.md), [Python rendering](references/python-rendering.md),
  [QGIS export](references/qgis-export.md), [interactive delivery](references/interactive-html.md).
- [French scenarios](../../../tests/map-illustration.md),
  [Python tests](../../../tests/test_map_illustration.py) and
  [QGIS tests](../../../tests/test_qgis_map_illustration.py).

Helpers keep input data unchanged and require a new output directory. They report file
sizes; a size budget is a delivery goal, not a guarantee. Visual/browser checks remain
separate from successful file generation. The HTML helper embeds selected geometry and
attributes but loads Leaflet JS/CSS externally; it is not an offline bundle.

## Boundaries

[qgis-layer-styling](../qgis-layer-styling/README.md) creates reusable QML;
[qgis-project-builder](../qgis-project-builder/README.md) assembles editable projects;
[mapshaper-simplify](../mapshaper-simplify/README.md) reduces vector complexity. This skill
renders existing data, not new indicators. Atlases, new complex print layouts, 3D scenes,
full web applications and hosting are outside its scope.
