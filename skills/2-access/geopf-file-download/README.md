# geopf-file-download

**Family:** [2. Access and extract](../README.md).

Download ready-made IGN files from the Géoplateforme Download API: paginated Atom
discovery, edition selection, foreground transfers, safe resume and integrity checks. The
skill finds a product's resources, then their edition and territory folders, then the
advertised file links, and selects territory, edition, format and CRS from that metadata.
A territory or polygon filter selects packages; it does not clip their contents.

## When to use it

- List the archives offered for a product, such as ADMIN EXPRESS, with the editions,
  formats, territories and links actually found in the catalogue.
- Choose a territory, edition, format and CRS from the Download API metadata.
- Download a bulk IGN delivery or an offline product package, with a manifest of source
  URLs and timestamps.
- Resume or restart an interrupted transfer without mixing two editions.
- Check a downloaded package's size, checksum and archive integrity before use.

## When to use another skill

- Get filtered features, such as a few buildings around a place:
  [`geopf-wfs-download`](../geopf-wfs-download/README.md)
- Get map images: [`geopf-raster-download`](../geopf-raster-download/README.md)

## What you get

- A JSON summary of each saved catalogue page from `scripts/inspect_feed.py` (no network):
  page, page size, total, next page and entries with their identifiers, titles and links.
  HTML, exceptions, invalid pagination, duplicate entries and truncated pages are refused.
- The selected file, downloaded in the foreground to a `.part` file with its response
  headers, and renamed to an unused final name only after it passes the checks.
- A manifest per file: resource, folder and file URLs, edition, territory, format, CRS,
  published size or hash, download timestamp and final response headers.
- A report of source, edition and date, selected files, bytes, format, CRS, coverage,
  validation results and partial or unavailable packages.

Before reporting, the agent compares the byte length with the whole object's advertised
length and any published checksum, tests the archive with its reader (`unzip -t`,
`7zz t`), then inspects the expected layers or tiles with GDAL for non-empty content, CRS,
extent and a plausible count or resolution. A missing checksum means authenticity was not
checked that way; a locally computed hash is only a local fingerprint.

The skill never assembles a product filename from memory and never claims that the first
catalogue page is the full catalogue. It resumes only against the original immutable URL
or with the original strong ETag (`If-Range`); otherwise it restarts into a new partial
file rather than appending bytes from an updated edition. It does not extract into an
existing dataset or overwrite user files, rejects archive members with absolute paths,
parent traversal or escaping links, and never executes downloaded scripts.

## Requirements

curl, Python 3, GDAL and an archive reader matching the delivery. Check with
`curl --version` and `python3 --version`. The user installs missing software; the agent
does not, and it runs no interactive setup or login command. For Debian/Ubuntu, a user-run
installation command is:

```bash
sudo apt install curl python3 gdal-bin unzip
```

For 7z archives, the corresponding user-run package is `7zip` on recent Debian/Ubuntu.
The service is the Download API at `https://data.geopf.fr/telechargement/capabilities`;
the documented commands carry no API key.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-file-download
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`.

## Example

> Find the ADMIN EXPRESS archives offered by the Géoplateforme. In `output/catalogue.md`,
> present the editions, formats, territories and links you actually found. Limit discovery
> to three pages and do not download any large archive.

```bash
curl --fail --show-error --location --max-time 60 \
  'https://data.geopf.fr/telechargement/capabilities?page=1&limit=10' \
  --output capabilities.xml
python3 scripts/inspect_feed.py capabilities.xml
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Workflow, prerequisites and validation. |
| [references/transfers.md](references/transfers.md) | Detailed recipes and edge cases: resume, archive checks, safe extraction and manifests. |
| [scripts/inspect_feed.py](scripts/inspect_feed.py) | Inspects a saved catalogue page (standard library only). |

## Tests

French agent scenarios: [tests/geopf-file-download.md](../../../tests/geopf-file-download.md)
(2 positive + 1 negative). Offline: [test_enrichment.py](../../../tests/test_enrichment.py)
(catalogue pages) and [test_download_transfers.py](../../../tests/test_download_transfers.py)
(integrity, byte-exact resume, refusal to append a changed edition). Live:
[test_live.py](../../../tests/test_live.py) and [test_live_enrichment.py](../../../tests/test_live_enrichment.py).

## Related skills

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) compares ready-made
  downloads, WFS and custom extraction before you choose this route.
- [`geodata-intake`](../../3-prepare/geodata-intake/README.md) inventories the formats,
  layers, CRSs and fields of a received delivery.
- [`gdal-vector-processing`](../../3-prepare/gdal-vector-processing/README.md) and
  [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md) convert, clip and
  reproject the downloaded files.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  uses dated deliveries from this skill when an exact historical edition is needed.
- [`terrain-elevation-screening`](../../6-workflows/terrain-elevation-screening/README.md)
  can use DEM tiles downloaded with this skill.
