# Download ready-made IGN files

Paginated Atom discovery, edition selection, foreground transfers, safe resume and integrity checks.

## Requirements

curl, Python 3, GDAL and an archive reader matching the delivery. The user installs missing software; the agent does not.
For Debian/Ubuntu, a user-run installation command is:

```bash
sudo apt install curl python3 gdal-bin unzip
```

## Install the skill

```bash
npx skills add ignfab/geoskills --skill geopf-download-files
```

## Contents

- [SKILL.md](SKILL.md): workflow, prerequisites and validation.
- [references/transfers.md](references/transfers.md): detailed recipes and edge cases.

- [scripts/inspect_feed.py](scripts/inspect_feed.py): inspect a saved catalogue page (standard library only).
