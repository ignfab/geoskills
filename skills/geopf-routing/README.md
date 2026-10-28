# Calculate routes and reachable areas

Discover navigation resources, choose units/direction and export route or isochrone geometry.

## Requirements

curl and Python 3; GDAL/GeoPandas for spatial validation. The user installs missing software; the agent does not.
For Debian/Ubuntu, a user-run installation command is:

```bash
sudo apt install curl python3 gdal-bin
```

## Install the skill

```bash
npx skills add ignfab/geoskills --skill geopf-routing
```

## Contents

- [SKILL.md](SKILL.md): workflow, prerequisites and validation.
- [references/reachable-areas.md](references/reachable-areas.md): detailed recipes and edge cases.
