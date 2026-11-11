# Reopen and move

Open the final output in a new `QgsProject()` and check `read(path)` before examining it.
Check `mapLayers()` count and each `layer.isValid()`; inspect raster dimensions/bands and
vector feature counts rather than assuming a provider opening proves nonempty data.
Compare project CRS and `viewSettings().defaultViewExtent()` with the intended values.

Walk `layerTreeRoot().findLayers()` in order and compare each node's layer name, parent
group and `itemVisibilityChecked()`. Verify effective group visibility as well when editing
an existing tree. Inspect the renderer type, attribute, categories/ranges and requested
symbol properties for every QML input. No new QML skill is required for loading an existing
style. Check project XML (`.qgs` or the `.qgs` member inside `.qgz`) for relative local
`datasource` values; a resolved provider URI can be absolute even when storage is relative.

Copy/move the **whole** bundle into a fresh directory, make the original location
unavailable in that test context, reopen the moved project and check every local layer.
Inspect resolved paths: they must point into the moved directory rather than silently
fall back to originals. Include external style dependencies or qualify portability.

Compare original source hashes before/after. Verify that the final output is nonempty and
no existing project was overwritten. If a requested public basemap fails, explicitly list
it as omitted/unverified and confirm that local layers still open. Report provider metadata
validation separately from visible tile rendering. Do not infer a remote service outage
from a local QGIS/Qt/PROJ initialization problem.
