# 5. Represent and publish

**Question:** how do I make the result usable?

Turn a result into something others can read or reuse: lighter geometries for web maps,
delivery formats, maps, styles and metadata.

| Skill | Use it to |
| --- | --- |
| [map-illustration](map-illustration/README.md) | Produce lightweight map images by default, optional interactive HTML, or reuse QGIS project rendering; verify readability, bytes and external dependencies. |
| [mapshaper-simplify](mapshaper-simplify/README.md) | Simplify polygon boundaries with Mapshaper, preserve shared borders and export lighter GeoJSON or TopoJSON. |
| [qgis-layer-styling](qgis-layer-styling/README.md) | Create and reload reusable vector QML: single symbols, categorized fields and graduated numeric classes. |
| [qgis-project-builder](qgis-project-builder/README.md) | Assemble existing vector/raster data into reopenable QGIS projects, with relative paths, QML inputs and optional verified public basemaps. |

## Choose between them

- Lighter boundaries for a web map, with shared borders kept: `mapshaper-simplify`. Keep
  the original geometry for measurements and analysis.
- A reusable style for one vector layer, saved as QML: `qgis-layer-styling`.
- A QGIS project that gathers existing layers, optionally with existing QML styles:
  `qgis-project-builder`. A style alone needs no project, and the project builder does
  not create new styles.
- A map image for a report or a slide, an export of an existing QGIS map, or a small
  interactive HTML map: `map-illustration`. It renders existing results; indicators are
  computed beforehand with `spatial-aggregation` or `geospatial-descriptive-statistics`.

## What they need

Choose one rendering or simplification route. Installing this family does not require
QGIS, Python plotting and Node together; see the [dependency guide](../../docs/dependencies.md).

| Skill | Base route | Conditional additions | Network |
| --- | --- | --- | --- |
| `map-illustration` | Static vectors: GeoPandas + Matplotlib; uniform HTML: GeoPandas + Folium; existing QGIS project: its own PyQGIS environment | Matplotlib for numeric HTML colours; Rasterio + Matplotlib for a raster preview without QGIS | None for the files; an HTML map may load browser resources or tiles |
| `mapshaper-simplify` | Existing Node.js and Mapshaper CLI | GeoPandas/Shapely only for the documented additional Python validation | None |
| `qgis-layer-styling` | Existing QGIS/PyQGIS and matching Qt | No separate GeoPandas or plotting stack | None |
| `qgis-project-builder` | Existing QGIS/PyQGIS, matching Qt and its GDAL bindings | Network access only for requested remote layers/basemaps | Only for an optional public basemap |

Static images need no browser libraries at viewing time. HTML external assets and tile
requests are a separate delivery choice: disclose them when an interactive map is requested.

Use the Python supplied with QGIS; on a machine without a display, set
`QT_QPA_PLATFORM=offscreen`.

## Also relevant

- [municipality-building-profile](../6-workflows/municipality-building-profile/README.md)
  combines source interpretation, analysis and optional QGIS delivery for one municipality.
- [gdal-raster-processing](../3-prepare/gdal-raster-processing/README.md) writes Cloud Optimized
  GeoTIFFs (COG) with overviews for delivery.
- [gdal-vector-processing](../3-prepare/gdal-vector-processing/README.md) exports RFC 7946 GeoJSON
  for the web, Shapefiles and GeoPackages.
- [geopf-service-selection](../1-discover/geopf-service-selection/README.md) covers the Géoplateforme display
  services (WMS, WMTS, vector tiles), which show data without downloading it.

## Not covered yet

- Styles outside vector QML (for example SLD).
- Print layouts and atlases.
- Metadata for a delivery.

## Install this family

```bash
npx skills add https://github.com/ignfab/geoskills/tree/main/skills/5-publish
```

Previous: [4. Analyze and derive](../4-analyze/README.md) ·
Next: [6. Solve a business need](../6-workflows/README.md) · [All families](../../README.md#skills)
