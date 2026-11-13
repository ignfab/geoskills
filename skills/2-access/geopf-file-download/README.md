# Download ready-made IGN files

**Family:** [2. Access and extract](../README.md).

Paginated Atom discovery, edition selection, foreground transfers, safe resume and integrity checks.

## Requirements

curl for transfers and Python 3's standard library for the catalogue helper. Reuse GDAL
for spatial content checks and only the archive reader matching the selected delivery.
ZIP checks can use existing Python's `zipfile` module or `unzip`; 7z needs `7zz`.
Direct GeoTIFF/GeoPackage files do not need an archive reader. Missing spatial/archive
checks must be reported; a downloaded file alone is not a validated dataset.

User-run Debian/Ubuntu commands, only when the corresponding stage needs a missing tool:
`sudo apt install curl`, `sudo apt install python3`, `sudo apt install gdal-bin`,
`sudo apt install unzip` or `sudo apt install 7zip` (recent releases).
The agent never installs software itself.

## Install the skill

```bash
npx skills add ignfab/geoskills --skill geopf-file-download
```

## Contents

- [SKILL.md](SKILL.md): workflow, prerequisites and validation.
- [references/transfers.md](references/transfers.md): detailed recipes and edge cases.

- [scripts/inspect_feed.py](scripts/inspect_feed.py): inspect a saved catalogue page (standard library only).
