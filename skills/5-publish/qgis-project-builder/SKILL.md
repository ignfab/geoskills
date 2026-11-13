---
name: qgis-project-builder
description: Assemble existing local vector and raster layers into a reopenable QGIS QGZ or QGS project with CRS, extent, groups, order, visibility, relative paths and optional existing QML or public basemap. Use for project creation and portable delivery; not standalone style generation, source editing, print layouts or atlases.
---

# QGIS project builder

Deliver a project and verification report from **existing** data. Creating new complex
QML belongs to `qgis-layer-styling` when available; basic project creation works without
it. `geodata-intake` can inspect unfamiliar inputs and `geopf-raster-download` can help discover
IGN services. Neither is an installation dependency.
For an image export of existing data/project or a small interactive HTML map, use
`map-illustration`.

## MCP servers

Optional. A QGIS MCP server drives the QGIS session the user has open. Its tools mention
QGIS (for example `get_project_info`, `get_layers`, `load_project`, `render_map`), and
their names differ between servers, so read the tool list. When one is connected, use it
first to list the layers loaded in the user's project when the request is to package what
they have open. Its tools may return names and types without the sources, the CRSs or the
order: then read them from the saved project file named by the project information, or ask
the user; never guess a path. Then inspect those sources as in step 1. Report a layer
without a file source (memory, database, remote service) as not packaged, by its name and
provider only: never copy its connection string, which can hold a password or a key, into
a message, a manifest or a project.

Build the project file with the helper below whenever standalone PyQGIS runs: it checks
the sources, the relative paths and the reopening.

Creating or loading a project through the server replaces the project the user has open
and discards its unsaved changes without a prompt: do it only when asked, for example to
show the verified project, after telling the user so and getting their agreement; never
save over their project, and say what you changed. A tool that executes code runs anything
in the user's QGIS: use it only with the user's agreement. If only the session is
available to build the project, say that it will turn the open session into the new
project and get the user's agreement first; then assemble it with the server's tools, save
it to a new path, reopen it and apply the checks of *Validate the output* by hand. Without
a QGIS MCP server, or when a call fails, use the helper only. Never install, configure or
start an MCP server or a QGIS plugin yourself.

## Prerequisites

Check installed PyQGIS with `python3 -c "from qgis.core import Qgis; print(Qgis.QGIS_VERSION)"`.
The helper supports QGIS 3.34–3.x and standalone Qt; use the Python supplied with QGIS and
`QT_QPA_PLATFORM=offscreen` on headless Linux. Never install software or run interactive
authentication. If missing, the user can install QGIS; on configured Debian/Ubuntu
repositories: `sudo apt install qgis python3-qgis`. Do not claim a project was verified
without actually opening it in QGIS/PyQGIS.

## Assemble

1. Discover local layer names, geometry types, declared CRSs, extents, fields and raster
   bands. Inspect GeoPackage sublayers instead of assuming the filename is a layer name.
   Reject invalid/missing sources and unknown CRS. Never edit source data to make them fit.
2. Prepare a [manifest](references/project-files.md) with explicit names, top-to-bottom
   order, groups, visibility, project CRS and optional extent **in that CRS**. Choose an
   unused project path. For a movable bundle, copy required inputs into its directory
   without changing originals and request `require_portable: true`.
   Honour a suitable requested/existing project CRS, including custom WKT. EPSG:2154 is
   only a metropolitan-France fallback; layers retain their own source CRSs. The helper
   records full WKT so a missing authority ID cannot hide a changed custom CRS.
3. Resolve the [helper](scripts/build_project.py) relative to this skill directory:

```bash
QT_QPA_PLATFORM=offscreen python3 scripts/build_project.py bundle/project.json bundle/map.qgz
QT_QPA_PLATFORM=offscreen python3 scripts/build_project.py project.json output/map.qgs
```

Source/QML paths in the manifest resolve relative to the manifest. Existing QML is optional;
validate its geometry and field compatibility before loading. New styles can be produced
separately or use QGIS defaults. For optional remote layers follow
[WMS/WMTS](references/wms-wmts-layers.md); public WMTS discovery is built into the helper.
Do not invent Plan IGN identifiers or embed credentials. Failed optional WMTS is omitted
with a warning while local layers remain usable.

## Validate the output

Follow [validation](references/validation.md). The helper reopens a staged project and
checks layer sources, order, names, groups, visibility, CRS, extent, relative-path setting
and vector renderers before publishing. Reopen the final project too, and test moving the
whole bundle when portability is claimed. Check local layer counts, raster size/vector
counts, nonempty extent and plausible placement. Provider validity and metadata checks do
not prove tile rendering: report remote availability separately. Give paths, QGIS version,
CRS, extent, relative-path scope, sources, existing styles and warnings; preserve source hashes.

## References

- [Project files](references/project-files.md): manifest and relative-path scope.
- [WMS/WMTS layers](references/wms-wmts-layers.md): discovery and remote limitations.
- [Validation](references/validation.md): reopening and movement checks.
