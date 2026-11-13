# geopf-geocoding

**Family:** [2. Access and extract](../README.md).

Geocode French addresses, points of interest and cadastral parcels with the
[Géoplateforme geocoding API](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/)
(`data.geopf.fr/geocodage`). You can send one query at a time or a whole CSV file, and you
can reverse-geocode coordinates. Existing geocoded CSV files can also be reviewed locally
for weak or ambiguous matches, unexpected municipalities or match types, and unmatched rows.

## When to use it

- Get the coordinates of one address, point of interest or municipality (including its
  INSEE code with `type=municipality`).
- Geocode a CSV of addresses in bulk with one `POST /search/csv` request and flag the
  doubtful rows.
- Find the nearest address, point of interest or parcel for each point of a CSV
  (`/reverse` or `POST /reverse/csv`).
- Locate a cadastral parcel from its reference and save its polygon
  (`index=parcel` with `returntruegeometry=true`).
- Classify an already geocoded CSV as accepted, review or unmatched under an explicit
  policy (score, margin over the second candidate, match type, municipality code),
  without any new API request.

## When to use another skill

- Official parcel area (`contenance`), every parcel of a municipality or cadastral
  section, or the parcels in an area: [`apicarto-query`](../apicarto-query/README.md).
- Reformatting an address table without geocoding it (for example CSV to Excel): no
  geocoding is needed, so this skill does not apply.

## What you get

- Single queries: a GeoJSON `FeatureCollection` in WGS84 (longitude, latitude). Address
  features also carry `x`/`y` in the legal projection of the territory (Lambert-93 in
  mainland France, UTM overseas). When present, the score is from 0 to 1; a structured
  parcel search may have none.
- Bulk geocoding: a CSV that keeps the input columns and adds `longitude`, `latitude`,
  `result_score`, `result_label`, `result_citycode`, `result_status` and similar columns.
  It can be converted to a GeoPackage in EPSG:4326 with `ogr2ogr`.
- Review: a new UTF-8 CSV with `review_status` and `review_reason` columns, plus a JSON
  report of the counts and the policy used. The helper refuses an existing output,
  duplicate headers and pre-existing review columns.
- Before reporting, the agent checks that `features` is non-empty (or reports no match),
  that longitude and latitude are in the right order and plausible for the territory,
  including overseas, and never reads API coordinates as Lambert-93.
- For a CSV, it compares input and output record counts and IDs, reports the counts by
  status (`ok`, `not-found`, `skipped`, `error`), never drops unmatched rows silently,
  checks `result_postcode` or `result_citycode` against the input, and checks that
  accented names are echoed intact (garbled names mean the service misread the encoding).
- A score of 0.5 is a starting heuristic, not a probability. `accepted` means a row passes
  the stated policy, not that the address was verified.

## Requirements

`curl` (or any HTTP client). No API key is needed. Python 3 is needed for the CSV splitting
and quality-review helpers; they use only the standard library. `jq` and GDAL are optional,
for processing the results.

On Debian/Ubuntu, the user can install only the missing tool for the selected route:
`sudo apt install curl`, `sudo apt install python3` (CSV helpers), `sudo apt install jq`
(jq recipes) or `sudo apt install gdal-bin` (conversion). Existing Python can inspect
JSON without jq. The agent never installs software itself.

Network service: `https://data.geopf.fr/geocodage`. Bulk files must be UTF-8 and stay below
50 MB and 200,000 rows per request. Stay under 50 requests per second per IP address for
geocoding and 10 for autocomplete. Reviewing an existing CSV needs no network access.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-geocoding
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`.

## Example

> Geocode the file `data/adresses.csv` (columns `numero`, `voie`, `code_postal`, `commune`)
> and write the result to `output/adresses_geocodees.csv`. Flag the doubtful rows.

With the address in a single `adresse` column and the postcode in `cp` (repeat `columns`
once per column when the address is split, as in the request above):

```bash
curl --fail --show-error --max-time 300 -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv -F columns=adresse -F postcode=cp \
  -o adresses_geocodees.csv
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Endpoints, minimal syntax, search, reverse and bulk CSV examples. |
| [references/api-parameters.md](references/api-parameters.md) | Common parameters, response fields, parcel and POI searches, using the results. |
| [references/batch-csv.md](references/batch-csv.md) | Bulk geocoding: form fields, output columns, quality checks, large files. |
| [references/quality-policy.md](references/quality-policy.md) | Explicit acceptance policy, ambiguity, municipality/type checks and unmatched rows. |
| [scripts/split_csv.py](scripts/split_csv.py) | Split UTF-8 CSV records by row count and byte size, preserving quoted fields. |
| [scripts/classify_results.py](scripts/classify_results.py) | Classify existing results as accepted, review or unmatched without another API call. |

## Tests

- Agent scenarios: [tests/geopf-geocoding.md](../../../tests/geopf-geocoding.md) (French
  prompts, 6 positive + 1 negative).
- Offline: [test_enrichment.py](../../../tests/test_enrichment.py) (review policy, including
  the GEO-06 fixture) and [test_split_csv.py](../../../tests/test_split_csv.py).
- Live (opt-in): [test_live.py](../../../tests/test_live.py) (address, CSV, reverse, parcel).

## Related skills

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) chooses the Géoplateforme
  access route before this skill runs.
- [`geopf-routing`](../../4-analyze/geopf-routing/README.md) computes isochrones from
  geocoded starting points (accessibility).
- [`apicarto-query`](../apicarto-query/README.md) finds urban-planning zones, easements and protected
  areas at geocoded locations (exposure).
- [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md) joins geocoded points
  with an area of interest or other layers.
