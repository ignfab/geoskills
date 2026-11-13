# Calculate routes and reachable areas

**Family:** [4. Analyze and derive](../README.md).

Discover navigation resources, choose units/direction and export route or isochrone geometry.

## Requirements

curl for requests and Python 3's standard library for response/GeoJSON handling.
Final spatial validation needs either existing GDAL or GeoPandas, not both; discovery
and raw responses do not. Missing spatial checks must remain explicit.

If absent, the user can install only the needed tool: `sudo apt install curl`,
`sudo apt install python3`, `sudo apt install gdal-bin` (Debian/Ubuntu), or
`python3 -m pip install 'geopandas>=1.0,<2'` for the Python GIS route.
The agent never installs software itself.

## Install the skill

```bash
npx skills add ignfab/geoskills --skill geopf-routing
```

## Contents

- [SKILL.md](SKILL.md): workflow, prerequisites and validation.
- [references/reachable-areas.md](references/reachable-areas.md): detailed recipes and edge cases.
