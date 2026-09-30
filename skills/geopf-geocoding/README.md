# geopf-geocoding

Geocode French addresses, points of interest and cadastral parcels with the
[Géoplateforme geocoding API](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/)
(`data.geopf.fr/geocodage`). You can send one query at a time or a whole CSV file, and you
can reverse-geocode coordinates.

## Requirements

`curl` (or any HTTP client). No API key is needed. `jq` and GDAL are optional, for
processing the results.

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

| [scripts/split_csv.py](scripts/split_csv.py) | Split UTF-8 CSV records by row count and byte size, preserving quoted fields. |

## Example

```bash
curl -fsS --max-time 300 -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv -F columns=adresse -F postcode=cp \
  -o adresses_geocodees.csv
```
