# qgis-project-builder

**Family:** [5. Represent and publish](../README.md).

Assemble existing geodata into verified QGZ/QGS projects with explicit relative-path scope.
From a JSON manifest that lists existing local vector and raster layers, a PyQGIS helper
builds a new project with its CRS, initial extent, layer order, groups, visibility,
optional existing QML and optional public WMTS basemap, then reopens it before publishing.

## When to use it

- Assemble existing local layers into a new QGIS project with a chosen CRS and initial
  extent.
- Control top-to-bottom layer order, groups and visibility, for example points above zones.
- Deliver a portable bundle with relative paths, checked by reopening it after moving the
  whole folder.
- Add a public basemap such as Plan IGN when available, keeping the local data valid if the
  service fails.
- Load existing QML styles into the project layers.

## When to use another skill

- Save only a QML style for a layer, without creating a project:
  [`qgis-layer-styling`](../qgis-layer-styling/README.md).
- An image export of existing data or of an existing project, or a small interactive HTML
  map: [`map-illustration`](../map-illustration/README.md).
- Source editing, print layouts, atlases and authentication setup are outside this skill;
  print layouts and atlases are not covered by any skill yet (see
  [Not covered yet](../README.md#not-covered-yet)).

## What you get

- A new `.qgz` or `.qgs` at an unused path, with relative path storage. Without an
  explicit extent, the helper unions the local layer extents in the project CRS and adds
  5%. Optional WMTS basemaps are placed below local layers.
- A JSON report on stdout: output, QGIS version, local layer count, remote layers and their
  status, portable-bundle flag, warnings and the validated layer snapshot.
- Checks before publishing: the helper writes a staged project, reopens it in a fresh
  `QgsProject` and compares layer sources, order, names, groups, visibility, CRS, extent,
  relative-path setting and vector renderers. Existing QML must reference only the layer's
  fields and match its geometry type.
- Checks before reporting: the agent reopens the final project, checks layer counts, raster
  size or vector feature counts, a nonempty extent and plausible placement, and preserves
  source hashes. When portability is claimed, it moves the whole bundle, makes the
  original location unavailable and checks that layers resolve inside the moved directory.

A QGZ does not embed data; move the entire validated bundle. `require_portable: true`
requires every local source below the project directory. Optional remote failure is
reported as local-only success, and a valid WMTS provider is not presented as proof that
tiles render. The agent never edits source data, never invents Plan IGN identifiers or
embeds credentials, and never claims a project was verified without opening it in
QGIS/PyQGIS.

## Requirements

- QGIS/PyQGIS 3.34–3.x, compatible Qt and installed vector/raster providers. Check with
  `python3 -c "from qgis.core import Qgis; print(Qgis.QGIS_VERSION)"`, using the Python
  supplied with QGIS and `QT_QPA_PLATFORM=offscreen` on headless Linux.
- For configured Debian/Ubuntu repositories the user can run
  `sudo apt install qgis python3-qgis` if needed; agents never install dependencies or run
  interactive authentication.
- Public basemaps optionally require network access. The helper accepts only public HTTPS
  WMTS endpoints without credentials and reads their capabilities with a 15-second timeout;
  no API key is used. Local projects need no network.

## MCP servers

Optional. With a QGIS MCP server connected to the QGIS session you have open, the agent
first lists the layers you have open when you ask to package them, and reads their sources
from your saved project file or asks you for them when the server does not give them. The
project file is still built by the helper whenever standalone PyQGIS runs. Opening a
project replaces the one you have open and drops its unsaved changes, so the agent does it
only when asked, after telling you and getting your agreement, and never saves over yours.
Without such a server, or when a call fails, nothing changes. See
[MCP servers](../../../docs/mcp-servers.md).

## Installation

```bash
npx skills add ignfab/geoskills --skill qgis-project-builder
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/5-publish`.

## Example

> Assemble `data/aggregation_objects.geojson` and `data/aggregation_zones.geojson` into a
> portable QGIS project under `output/bundle/`, with the points above the zones and relative
> paths. Check that it reopens after moving the whole folder.

```bash
QT_QPA_PLATFORM=offscreen python3 scripts/build_project.py bundle/project.json bundle/map.qgz
QT_QPA_PLATFORM=offscreen python3 scripts/build_project.py project.json output/map.qgs
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Inspection, assembly and validation. |
| [scripts/build_project.py](scripts/build_project.py) | Manifest-based local projects and optional public WMTS. |
| [references/project-files.md](references/project-files.md) | Manifest format, extent, QML inputs and relative-path scope. |
| [references/wms-wmts-layers.md](references/wms-wmts-layers.md) | Optional public basemaps: WMTS discovery, the WMS alternative and remote limitations. |
| [references/validation.md](references/validation.md) | Reopening, bundle relocation and source checks. |

## Tests

[Scenarios](../../../tests/qgis-project-builder.md): French agent prompts, 2 positive +
1 negative. [test_qgis_project_builder.py](../../../tests/test_qgis_project_builder.py)
reopens helper projects, including after relocation, and checks an omitted remote basemap
without network; it needs PyQGIS ([QGIS integration](../../../tests/README.md#qgis-integration)).

## Related skills

- [`qgis-layer-styling`](../qgis-layer-styling/README.md) can supply new QML, but is optional.
- [`geodata-intake`](../../3-prepare/geodata-intake/README.md) can inspect unfamiliar inputs
  before assembly.
- [`geopf-raster-download`](../../2-access/geopf-raster-download/README.md) can help discover IGN
  basemap services.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  writes a `qgis-project.json` manifest that this skill turns into a project.
