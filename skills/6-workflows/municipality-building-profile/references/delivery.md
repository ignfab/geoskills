# Delivery and optional QGIS

The helper creates a new directory:

| File | Purpose |
| --- | --- |
| `profile.gpkg` | `municipality` (one feature and indicators), `buildings` (clipped polygons, IDs and derived measures), `footprint` (union, empty when no buildings). |
| `indicators.csv` | `section,indicator,value_json`; parse the last column as JSON to retain nulls, categories and their string codes. |
| `audit.json` | Method, input manifest, source hashes, completeness declaration, versions, excluded IDs and file validation. |
| `report.md` | Human-readable indicators, sources, height/usage summaries, checks and limits. |
| `qgis-project.json` | Optional project-builder manifest referring to the local GeoPackage. This is not a QGIS project. |

Input attributes are represented by selected IDs and normalized height/usage values, not
a full copy of the source schema. Original source files remain available unchanged; the
audit retains their hashes, paths and chosen field names. Existing output directories are
refused. If writing fails, a partial directory may remain; inspect it and choose a new
output path for a rerun, without overwriting user files.

File validation does not prove dataset completeness. Distinguish `complete`, `partial`
and `unknown` input coverage and identify missing sources/editions. Give actual output
paths and explain any missing optional height, usage or cartographic deliverable.

## Optional map/project handoff

When the user requests a map, use `qgis-layer-styling` if available to create QML for
`municipality` and `buildings`: an unfilled boundary and a visible building fill make
coverage interpretable. Discover output fields before styling; use `usage` or `height_m`
only when those fields were produced, and keep missing values identifiable.

With `qgis-project-builder`, resolve its installed helper and pass this workflow's
`qgis-project.json` and a new `map.qgz` path **inside the same bundle directory**. Add
optional relative `qml` paths to its layer entries before building. The manifest places
buildings above the boundary and hides the overlapping union layer by default.

If that skill is unavailable but PyQGIS exists, create a `QgsProject`, add the three
GeoPackage layers using discovered names, set the analysis CRS and municipal extent,
and use `Qgis.FilePathType.Relative`. Check each `QgsVectorLayer.isValid()`, save to a new
path and independently reopen it. For a portable delivery, move a copy of the complete
bundle to a fresh location and verify its sources resolve there while the original is
unavailable. Include the actual QGIS version and verification result in the final report.
Do not install QGIS to obtain this optional deliverable, and do not claim a JSON manifest
is a QGZ. No live basemap is necessary; a requested remote layer needs its own discovery
and availability checks.
