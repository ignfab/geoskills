---
name: map-illustration
description: Create lightweight cartographic illustrations from existing geodata, with a static PNG by default, optional SVG/PDF, and optional interactive HTML. Use when the user wants a map image for a report or slide, an export of an existing QGIS map, or a small interactive map with or without QGIS. Use qgis-layer-styling for QML alone, qgis-project-builder for QGZ/QGS assembly alone, and mapshaper-simplify for geometry simplification alone. Not for data analysis, atlases, or hosting a website.
---

# Map illustration

Make a readable map of an **existing result**. Default to a static PNG; produce interactive
HTML only when requested or useful for inspecting features. Select a renderer from the
available environment and source material, not from a requirement to use QGIS everywhere.

## Prerequisites

Check only the chosen route; never install software or run interactive setup/login.
If dependencies are absent, give the corresponding command for the user to run:

| Route | Check | User-run installation example |
| --- | --- | --- |
| Static without QGIS | `python3 -c "import geopandas, matplotlib, PIL"` | `python3 -m pip install geopandas matplotlib` |
| Interactive without QGIS | `python3 -c "import geopandas, folium"` | `python3 -m pip install geopandas folium` |
| Existing QGIS map | `python3 -c "from qgis.core import Qgis; print(Qgis.QGIS_VERSION)"` | `sudo apt install qgis python3-qgis` on configured Debian/Ubuntu repositories |
| Raster without QGIS | `python3 -c "import rasterio, matplotlib"` | `python3 -m pip install rasterio matplotlib` |

Helpers use GeoPandas ≥ 1.0, Matplotlib ≥ 3.7, Folium ≥ 0.16, or QGIS 3.34–3.x as relevant.
Numeric colours in HTML also use Matplotlib; a uniform HTML map does not need it.
QGIS runs use its own Python environment and `QT_QPA_PLATFORM=offscreen` when headless.

## Choose and render

1. Inspect actual layers, fields, CRS, extent, geometry, missing values and source/edition.
   Identify audience, main message, final display size and requested interaction. Prefer
   local data and no basemap when it adds no useful context. Do not compute new indicators
   to fill a map legend; use `spatial-aggregation` or `geospatial-descriptive-statistics` first.
2. Choose the [rendering route and size budget](references/design-and-size.md). Use
   GeoPandas/Matplotlib for simple static maps; reuse QGIS for existing project styles,
   labels or mixed raster/vector composition. Use Folium for a modest vector HTML map.
   Browser access to JavaScript/CSS or tiles is a separate dependency from file generation.
3. For a simple vector image, inspect/select a layer, then run this helper relative to
   the installed skill directory. Replace sample names/CRS with the inspected values:

```bash
python3 scripts/render_vector.py input.gpkg output/illustration --layer zones \
  --crs EPSG:2154 --title 'Study area' --source-note 'Source: supplied data; edition unknown'
```

Add `--column indicator --units 'documented unit'` for a continuous numeric colour scale.
Use `--formats png svg` for a small vector companion, or `--formats png html --tooltip id`
for both outputs. The helper requires a new directory, keeps nulls separate from zero and
exports only explicitly selected tooltip fields. Read [Python rendering](references/python-rendering.md)
for multiple layers, rasters and the limits of this intentionally small helper.
4. For an existing project, follow [QGIS export](references/qgis-export.md): export its
   visible layer order without saving changes to it. An image render is not a reusable QML
   or a newly assembled QGZ. Use `qgis-layer-styling` or `qgis-project-builder` for those outputs.
5. For HTML, follow [interactive delivery](references/interactive-html.md), including
   resource dependencies, tooltip selection and actual browser checks. No web framework,
   server, hosting or full QGIS project is needed for a small local HTML delivery.

## Validate the output

Reopen the actual PNG/SVG/PDF or HTML, not just its source data. Check nonempty content,
pixel/page dimensions, extent and expected features; verify display CRS and plausible
placement against the input. Inspect the image visually at its intended size: no clipped
title/legend, unreadable text, hidden features or nodata painted as a real value. A file
signature or nonwhite-pixel count alone is insufficient. Inspect PDF/SVG via a rendered
preview when needed; keep text/legend readable after size optimization.

For HTML, open the delivered file in a browser, test zoom, pan, layer visibility and a
tooltip, and check resource errors. Test without network before claiming offline support.
If a browser/render preview is unavailable, report that check as unperformed. Check all
exported properties, source hashes and file bytes. Preserve attribution; report renderer
version, input/source date, fields/units, CRS, dimensions, simplification/downsampling,
actual size, external dependencies and checks performed. An empty input needs an explicit
no-data illustration or explanation, not a plausible-looking empty basemap.

## References

- [Design and size](references/design-and-size.md): route selection and restrained map design.
- [Python rendering](references/python-rendering.md): static vectors, overlays and bounded raster previews.
- [QGIS export](references/qgis-export.md): existing project PNG and layout export.
- [Interactive delivery](references/interactive-html.md): lean Folium, browser QA and offline limits.
