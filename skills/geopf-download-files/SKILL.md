---
name: geopf-download-files
description: Discovers and downloads ready-made dataset archives and tiles from the French Géoplateforme Download API, selecting territory, edition, format and CRS and checking partial transfers. Use for bulk IGN file deliveries or offline product packages. Use the WFS skill for filtered features and the WMS/WMTS skill for map images.
---

# Download Géoplateforme files

Entry point: `https://data.geopf.fr/telechargement/capabilities` (Atom). Discover resources,
their edition/territory folders, then advertised file links. A territory/polygon filter
selects packages; it does not clip their contents to that polygon.

## Prerequisites

Check `curl --version` and `python3 --version`; inspect downloaded geodata with existing
GDAL tools and archives with an appropriate existing reader. If missing, give the user
`sudo apt install curl python3 gdal-bin unzip` (Debian/Ubuntu; ZIP reader) to run.
For 7z archives, the corresponding user-run package is `7zip` on recent Debian/Ubuntu.
**Never install software yourself.** Do not launch interactive setup or login commands.

## Discover before downloading

```bash
curl --fail --show-error --location --max-time 60 \
  'https://data.geopf.fr/telechargement/capabilities?page=1&limit=10' \
  --output capabilities.xml
python3 scripts/inspect_feed.py capabilities.xml
```

Script paths are relative to this skill directory. Follow the advertised resource and
folder links, retaining the query filters when advancing pages. Read `gpf_dl:page`,
`pagesize` and `totalentries`; page numbers start at 1, limit is at most 50. Do not claim
the first page is the full catalogue. Use a bounded search and narrow it if necessary.

Confirm edition, coverage, format, CRS, licence and expected size from metadata before
choosing file links. Never assemble a product filename from memory. Download only the
requested selection and retain its source URLs and timestamps in a manifest.

## Download a selected file

Set `FILE_URL` to the advertised HTTPS file link. Choose an unused local basename.
Run in the foreground; the progress meter remains visible:

```bash
curl --fail --show-error --location --connect-timeout 20 --max-time 3600 \
  --retry 2 --retry-max-time 120 --dump-header package.headers \
  --output package.zip.part "$FILE_URL"
```

Use the actual archive extension from metadata. Validate before renaming `.part` to the
final name. For interrupted transfers and safe resume, read the reference below; do not
blindly append bytes from an updated edition. Honour `Retry-After` and stop after bounded
retries. A failed transfer remains partial, even if a file exists.

## Validate the output

Compare byte length and any published checksum, test archive integrity with its reader
(for example `unzip -t package.zip.part`), then inspect the expected layers/tiles with
GDAL. Verify nonempty content, CRS, extent and a plausible count/resolution. Missing
checksums mean authenticity was not checked that way; a locally computed hash is only
a local fingerprint. Do not extract into an existing dataset or overwrite user files.

## Report the result

Report source/edition/date, selected files, bytes, format/CRS/coverage, validation results
and partial or unavailable packages. Preserve the manifest for later reproducibility.

## References

- [Transfers and integrity](references/transfers.md) — resume, archive checks and manifests.
- [Official Download API guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/telechargement/).
