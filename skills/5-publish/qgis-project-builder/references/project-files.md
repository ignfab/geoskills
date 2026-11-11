# Project manifest and bundle

A manifest beside a `data/` folder and optional `styles/` folder:

```json
{
  "crs": "EPSG:2154",
  "require_portable": true,
  "layers": [
    {"kind":"vector","source":"data/boundary.geojson","name":"Boundary","group":"Study","visible":true,"qml":"styles/boundary.qml"},
    {"kind":"raster","source":"data/elevation.tif","name":"Elevation","group":"Study","visible":false}
  ]
}
```

These are example filenames/CRS only. Use a declared, suitable project CRS. For GeoPackage
include `"layer":"<discovered layer name>"`. GeoJSON and GeoTIFF need no sublayer option.
All local layers must have valid declared CRSs. Layer order is top to bottom; members of
each named group must be consecutive. Names must be unique so validation is unambiguous.

Omit `qml` for default QGIS symbology. Existing QML is read into project symbology; the
QML file itself is not required to reopen the saved project, but external SVG/raster/font
resources referenced by a style are separate dependencies. Copy or document them before
claiming a self-contained delivery; the helper checks renderer fields/symbol geometry,
not arbitrary external artwork. Unsupported complex styles need additional inspection.

Optional `extent: [xmin, ymin, xmax, ymax]` is in the project CRS, with positive dimensions.
Without it the helper transforms local layer extents into the project CRS and adds 5%.
A degenerate point-only extent requires an explicit box. Remote coverage never replaces
the local study extent. Reprojection here affects the view, not the source coordinates.

The helper sets `Qgis.FilePathType.Relative`. Relative paths can contain `../`, so they
are not by themselves proof that moving only the project file will work. `require_portable`
requires local source files below the project directory; move **that entire directory**.
Sidecars, style artwork and remote services still need separate accounting. A new `.qgz`
compresses project XML; it does not automatically embed geodata. `.qgs` is the XML form.

QGIS [project read/write](https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/loadproject.html)
returns success booleans that must be checked. The helper uses an independent `QgsProject`,
so it does not clear or rewrite the user's open desktop project.
