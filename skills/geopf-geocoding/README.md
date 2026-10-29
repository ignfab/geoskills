# geopf-geocoding

Geocode French addresses, points of interest and cadastral parcels with the
[Géoplateforme geocoding API](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/)
(`data.geopf.fr/geocodage`). You can send one query at a time or a whole CSV file, and you
can reverse-geocode coordinates. Existing geocoded CSV files can also be reviewed locally
for weak or ambiguous matches, unexpected municipalities or match types, and unmatched rows.

## Requirements

`curl` (or any HTTP client). No API key is needed. Python 3 is needed for the CSV splitting
and quality-review helpers; they use only the standard library. `jq` and GDAL are optional,
for processing the results.

The user can install these tools with `sudo apt install curl python3` (Debian/Ubuntu),
and optionally `sudo apt install jq gdal-bin`. The agent never installs software itself.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-geocoding
```

## Contents

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Endpoints, minimal syntax, search, reverse and bulk CSV examples. |
| [references/api-parameters.md](references/api-parameters.md) | Common parameters, response fields, parcel and POI searches, using the results. |
| [references/batch-csv.md](references/batch-csv.md) | Bulk geocoding: form fields, output columns, quality checks, large files. |
| [references/quality-policy.md](references/quality-policy.md) | Explicit acceptance policy, ambiguity, municipality/type checks and unmatched rows. |
| [scripts/split_csv.py](scripts/split_csv.py) | Split UTF-8 CSV records by row count and byte size, preserving quoted fields. |
| [scripts/classify_results.py](scripts/classify_results.py) | Classify existing results as accepted, review or unmatched without another API call. |

## Example

```bash
curl --fail --show-error --max-time 300 -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv -F columns=adresse -F postcode=cp \
  -o adresses_geocodees.csv
```
