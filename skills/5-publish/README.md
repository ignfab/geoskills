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

## Also relevant

- [municipality-building-profile](../6-workflows/municipality-building-profile/README.md)
  combines source interpretation, analysis and optional QGIS delivery for one municipality.
- [gdal-raster-basics](../3-prepare/gdal-raster-basics/README.md) writes Cloud Optimized
  GeoTIFFs (COG) with overviews for delivery.
- [gdal-vector-basics](../3-prepare/gdal-vector-basics/README.md) exports RFC 7946 GeoJSON
  for the web, Shapefiles and GeoPackages.
- [geopf-services](../1-discover/geopf-services/README.md) covers the Géoplateforme display
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
