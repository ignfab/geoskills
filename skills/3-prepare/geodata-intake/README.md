# Inspect an unfamiliar geospatial delivery

**Family:** [3. Prepare and check](../README.md).

Read-only inventory of formats, layers, metadata and missing CRS evidence.

## Requirements

GDAL/OGR CLI for vector/raster metadata and Python 3's standard library for CSV/JSON
recipes. CSV-only inspection needs no GDAL. No GeoPandas, QGIS or GDAL Python bindings
are required. Reuse existing tools. If absent, user-run Debian/Ubuntu commands are
`sudo apt install gdal-bin` or `sudo apt install python3`, only for the selected inputs.
For Conda, the corresponding packages are `libgdal-core` and `python`.
The agent never installs software itself.

## Install the skill

```bash
npx skills add ignfab/geoskills --skill geodata-intake
```

## Contents

- [SKILL.md](SKILL.md): workflow, prerequisites and validation.
- [references/inspection.md](references/inspection.md): detailed recipes and edge cases.
