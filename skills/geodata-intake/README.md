# Inspect an unfamiliar geospatial delivery

Read-only inventory of formats, layers, metadata and missing CRS evidence.

## Requirements

GDAL/OGR and Python 3. The user installs missing software; the agent does not.
For Debian/Ubuntu, a user-run installation command is:

```bash
sudo apt install gdal-bin python3
```

## Install the skill

```bash
npx skills add ignfab/geoskills --skill geodata-intake
```

## Contents

- [SKILL.md](SKILL.md): workflow, prerequisites and validation.
- [references/inspection.md](references/inspection.md): detailed recipes and edge cases.
