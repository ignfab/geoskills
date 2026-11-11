# Save, reuse and verify

Use QGIS APIs, not a hand-built QML schema. The
[vector cookbook](https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/vector.html)
and [standalone application guide](https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/intro.html)
cover renderer objects and application initialization. This helper targets the QGIS 3 API;
record the actual runtime version rather than assuming that the documentation version is
installed. The dedicated CI job checks the installed runtime and renderer behavior.

`saveNamedStyle(path)` and `loadNamedStyle(path)` return `(message, success)` in PyQGIS.
Check the boolean; a message string is not a success flag. Save to a temporary QML, load
it into a new `QgsVectorLayer` from the same source and compare the renderer serialization
before publishing to an unused final file. The helper does this without editing features.

To reuse QML on another layer, independently verify geometry type and each referenced
field/type first. Load it with `message, ok = other.loadNamedStyle(qml_path)`, then check
`ok`, renderer type, symbols and class attribute. Inspect colors, fill, width/size and
units against the request, not just against the generated style. For categorized styles,
inspect missing/new values; for graduated styles, verify coverage and null exclusions.

Record original hashes for source files (including relevant Shapefile sidecars) and compare
afterward. QML is reusable symbology, not a data container or a complete QGIS project.
A visible preview in an existing QGIS session is useful when available; a headless renderer
round-trip verifies properties but does not establish cartographic readability at every scale.
