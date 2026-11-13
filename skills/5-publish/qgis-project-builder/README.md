# qgis-project-builder

**Family:** [5. Represent and publish](../README.md).

Assemble existing geodata into verified QGZ/QGS projects with explicit relative-path scope.

## Requirements

QGIS/PyQGIS 3.34–3.x, compatible Qt and installed vector/raster providers. For configured
Debian/Ubuntu repositories the user can run `sudo apt install qgis python3-qgis` if needed;
agents never install dependencies. Public basemaps optionally require network access.

## Install

```bash
npx skills add ignfab/geoskills --skill qgis-project-builder
```

## Contents

- [SKILL.md](SKILL.md): inspection, assembly and validation.
- [build_project.py](scripts/build_project.py): manifest-based local projects and optional public WMTS.
- [Project files](references/project-files.md), [WMS/WMTS](references/wms-wmts-layers.md)
  and [validation](references/validation.md).
- [French scenarios](../../../tests/qgis-project-builder.md).

[QGIS layer styling](../qgis-layer-styling/README.md) can supply new QML, but is optional.
No source edits, print layouts, atlases or authentication setup. A QGZ does not embed data;
move the entire validated bundle. Optional remote failure is reported as local-only success.
