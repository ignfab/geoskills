# Retrieve point elevations and profiles

Discover terrain/surface resources, preserve missing elevations, join CSV rows and sample profiles.

## Requirements

curl and Python 3; GDAL/PROJ only if inputs need reprojection. The user installs missing software; the agent does not.
For Debian/Ubuntu, a user-run installation command is:

```bash
sudo apt install curl python3
```

## Install the skill

```bash
npx skills add ignfab/geoskills --skill geopf-altimetry
```

## Contents

- [SKILL.md](SKILL.md): workflow, prerequisites and validation.
- [references/points-and-profiles.md](references/points-and-profiles.md): detailed recipes and edge cases.
