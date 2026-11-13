# map-illustration

**Family:** [5. Represent and publish](../README.md).

Static-first cartographic illustrations of existing geodata: a PNG by default, an optional
SVG or PDF, and an optional interactive HTML map. The skill reuses QGIS when an existing
project already holds useful styles, labels or a layout; otherwise it uses a small Python
path with GeoPandas, Matplotlib and Folium. No application server, web build pipeline or
mandatory QGIS installation is involved, and input data stay unchanged.

## When to use it

- Make a map image of an existing vector result for a report or slide, with a title, a
  source note and, for a numeric field, a continuous color scale with its units.
- Render a PNG with QGIS, from local layers with simple requested symbols or from an
  existing project's visible layers and styles, when only the image is wanted, not a
  project or style file.
- Export an existing QGIS print layout to PDF, PNG or SVG when a legend or scale is needed.
- Create a small interactive HTML map without a basemap, with zoom, pan, layer visibility
  and only selected attributes in tooltips.
- Preview an existing raster, such as elevations, without QGIS, keeping nodata separate.

## When to use another skill

- Reusable QML style only, without an image: [`qgis-layer-styling`](../qgis-layer-styling/README.md).
- Editable, portable QGZ/QGS project only: [`qgis-project-builder`](../qgis-project-builder/README.md).
- Geometry simplification only, such as lighter GeoJSON with shared borders kept:
  [`mapshaper-simplify`](../mapshaper-simplify/README.md).
- Indicators a legend would show: [`spatial-aggregation`](../../4-analyze/spatial-aggregation/README.md)
  or [`geospatial-descriptive-statistics`](../../4-analyze/geospatial-descriptive-statistics/README.md)
  first; this skill renders existing values and computes nothing new.
- Zones of a DEM selected by altitude thresholds, with candidate polygons:
  [`terrain-elevation-screening`](../../6-workflows/terrain-elevation-screening/README.md).

Atlases, new complex print layouts, 3D scenes, full web applications and hosting are out
of scope.

## What you get

- `render_vector.py` writes to a new directory (an existing one is refused) `map.png` by
  default, plus `map.svg`, `map.pdf` or `map.html` on request. The default canvas is
  1400 × 1000 pixels at 140 dpi with title, source note and a meter scale bar; `--column`
  adds a continuous Viridis scale, with missing values in gray, separate from zero. Its
  `report.json` records features, CRSs, field, units, range, null count, dimensions,
  library versions and file bytes. It does no simplification or statistics.
- `export_qgis.py` writes `map.png` and `report.json` (QGIS version, CRS, layers, render
  extent, bytes, renderer errors) from the project's visible layers, styles and stored view
  extent. The project is never saved; this quick PNG has no thematic legend or scale bar.
- HTML embeds only the selected tooltip fields and an internal display color, in EPSG:4326,
  with no tiles. It loads Leaflet JS/CSS from the URLs listed in `report.json`, which marks
  the file as not offline.
- Checks before reporting: the actual PNG, SVG, PDF or HTML is reopened and inspected at
  its intended size (nonempty content, dimensions, extent, expected features, display CRS,
  readable title and legend, nodata not painted as a value). HTML is opened in a browser to
  test zoom, pan, layer visibility, a tooltip and resource errors. A check that could not
  be run is reported as not performed.
- 2 MB per image and 5 MB per HTML file are review budgets, not guarantees; actual bytes
  are reported. Offline support is never claimed without a network-disabled test. An empty
  input gets an explicit no-data illustration or explanation, not an empty basemap.

## Requirements

Check only the chosen route. Agents never install software or run interactive setup; when
a dependency is missing they give the user the command to run.

| Route | Needs | Check | User-run installation |
| --- | --- | --- | --- |
| Static vector map | GeoPandas ≥ 1.0, Matplotlib ≥ 3.7, Pillow | `python3 -c "import geopandas, matplotlib, PIL"` | `python3 -m pip install geopandas matplotlib` |
| Interactive HTML | GeoPandas ≥ 1.0, Folium ≥ 0.16; Matplotlib for numeric colors | `python3 -c "import geopandas, folium"` | `python3 -m pip install geopandas folium` |
| Existing QGIS map | QGIS/PyQGIS 3.34–3.x and Qt | `python3 -c "from qgis.core import Qgis; print(Qgis.QGIS_VERSION)"` | `sudo apt install qgis python3-qgis` (configured Debian/Ubuntu) |
| Raster preview | Rasterio, Matplotlib | `python3 -c "import rasterio, matplotlib"` | `python3 -m pip install rasterio matplotlib` |

QGIS runs use their own Python environment, with `QT_QPA_PLATFORM=offscreen` when headless.
Creating the files needs no network service. Opening the HTML fetches Leaflet assets, and
loading a QGIS project can access remote providers; a no-network request uses local data.

## Installation

```bash
npx skills add ignfab/geoskills --skill map-illustration
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/5-publish`.

## Example

> Without QGIS or network access, illustrate `data/admin_units_synthetic.geojson` for a
> report. Use the metadata in `data/README.md`. Provide a 1,400 × 1,000 pixel PNG and an
> SVG, with a title, the source and a color scale of the population field in fictitious
> inhabitants. Aim for less than 2 MB per file and state the actual sizes.

Expected: all three synthetic areas kept, both files reopened and inspected, PNG dimensions
checked and actual bytes reported, with no unrequested HTML or tiles. The helper call, with
sample names and CRS replaced by the inspected values:

```bash
python3 scripts/render_vector.py input.gpkg output/illustration --layer zones \
  --crs EPSG:2154 --title 'Study area' --source-note 'Source: supplied data; edition unknown'
```

Add `--column indicator --units 'documented unit'` for the color scale and
`--formats png svg` for the SVG companion.

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Route selection, rendering and visual checks. |
| [scripts/render_vector.py](scripts/render_vector.py) | One vector layer to PNG, SVG, PDF or HTML, with color scale, missing values, selected tooltips and size report. |
| [scripts/export_qgis.py](scripts/export_qgis.py) | Existing QGIS project's visible layers and styles to PNG, without saving the project. |
| [references/design-and-size.md](references/design-and-size.md) | Route choice, size budgets, restrained design and size reduction. |
| [references/python-rendering.md](references/python-rendering.md) | Static vectors, multiple layers and bounded raster previews. |
| [references/qgis-export.md](references/qgis-export.md) | Existing project to PNG and existing layout export. |
| [references/interactive-html.md](references/interactive-html.md) | Lean Folium maps, external dependencies, offline limits and browser checks. |

## Tests

- [French agent scenarios](../../../tests/map-illustration.md): 4 positive + 3 negative.
- Offline: [test_map_illustration.py](../../../tests/test_map_illustration.py) (`render_vector.py`
  outputs, HTML assets, invalid inputs, raster recipe) and
  [test_qgis_map_illustration.py](../../../tests/test_qgis_map_illustration.py) (`export_qgis.py`,
  needs PyQGIS). No live test.

## Related skills

- [`spatial-aggregation`](../../4-analyze/spatial-aggregation/README.md) and
  [`geospatial-descriptive-statistics`](../../4-analyze/geospatial-descriptive-statistics/README.md)
  produce the indicators to map.
- [`mapshaper-simplify`](../mapshaper-simplify/README.md) simplifies a display copy of
  polygons with shared borders before rendering; analytical inputs stay intact.
- [`qgis-layer-styling`](../qgis-layer-styling/README.md) and
  [`qgis-project-builder`](../qgis-project-builder/README.md) create reusable styles and
  projects; neither is needed to export an existing project.
