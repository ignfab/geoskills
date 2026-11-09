---
name: geopf-geocoding
description: Geocodes addresses, points of interest and parcels with the French Géoplateforme API, reverse-geocodes coordinates, and reviews already geocoded CSV results. Use to locate French addresses or parcels, geocode a CSV, or classify geocoding matches by score, ambiguity, municipality and match type while retaining unmatched rows. Quality review of an existing result requires no new API request.
---

# Géoplateforme geocoding

Geocode French addresses (Base Adresse Nationale), points of interest and cadastral parcels
with the IGN Géoplateforme geocoding API. No API key is needed.

## Prerequisites

- `curl` (or any HTTP client). No API key is needed.
- Python 3 for the optional CSV splitting and quality-review helpers (standard library only).
- Optional: `jq` to extract fields, GDAL (`ogr2ogr`) to convert the results.
- If a tool is missing, give the user the install command and let them run it; do not install software yourself.

Install: `sudo apt install curl python3` (Ubuntu/Debian); optional tools:
`sudo apt install jq gdal-bin`. Do not run interactive setup. Inspect the input CSV
headers and `/getcapabilities` before choosing columns or index-specific filters.

## Endpoints

Base URL: `https://data.geopf.fr/geocodage`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/search` | GET | Text → coordinates |
| `/reverse` | GET | Coordinates → nearest address, POI or parcel |
| `/search/csv` | POST | Bulk geocoding of a CSV file (UTF-8, max 50 MB / 200,000 rows) |
| `/reverse/csv` | POST | Bulk reverse geocoding of a CSV file with `lon`/`lat` columns |
| `/completion/` | GET | Autocompletion for search-as-you-type |
| `/getcapabilities` | GET | Geocoding indexes, fields and parameters, as JSON |
| `/completion/getcapabilities` | GET | Autocomplete resources and parameters |

Responses from `/search` and `/reverse` are GeoJSON `FeatureCollection`s in **WGS84
(lon, lat)**. Response fields depend on the operation and index: a structured parcel
search may have no `score`. When present, the score is from 0 to 1 and must be interpreted
in the context of that operation. Address features also carry `x`/`y`
in the legal projection of the territory (Lambert-93 in mainland France, UTM overseas).

## Minimal syntax

Search for an address. `index` defaults to `address`; the other values are `poi` and `parcel`:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/search?q=73+avenue+de+paris+saint-mande&limit=1"
```

Restrict the results with filters: `postcode`, `citycode` (INSEE code), `depcode`, `city`, and
`type=housenumber|street|locality|municipality`:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/search?q=avenue+de+paris&citycode=94067&type=street"
```

Reverse geocode a point. The index can be `address`, `poi` or `parcel`:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/reverse?lon=2.4245&lat=48.8451&index=parcel&limit=1"
```

Geocode a CSV file in bulk. `columns` lists the columns that are joined into the query text;
repeat it once per column:

```bash
curl --fail --show-error --max-time 300 -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv \
  -F columns=numero -F columns=voie -F columns=commune \
  -F postcode=code_postal \
  -o adresses_geocodees.csv
```

The output CSV generally keeps the input columns and adds `longitude`, `latitude`,
`result_score`, `result_label`, `result_citycode`, and so on. Existing `longitude` and
`latitude` columns are overwritten in forward geocoding; rename them first if they must
be preserved. See the batch reference before choosing output columns.

## Good practice

- Check HTTP success, then handle an empty `features` array or a non-`ok` CSV status.
- Review low `score` / `result_score` values (0.5 is a starting heuristic, not a probability
  or a universal threshold). Compare the returned town and `type` / `result_type` with
  the query: a street result for a requested house number needs review.
- Use `postcode` or `citycode` filters whenever the data has them. They remove most
  mismatches between towns that share a street name.
- For more than a few hundred addresses, use `/search/csv` rather than looping over `/search`.
- Stay under **50 requests per second** per IP address for geocoding and **10** for
  autocomplete. On HTTP 429, respect `Retry-After`
  when provided and use bounded retries; do not retry invalid requests unchanged.
- For CSV encoding, splitting and error statuses, read the batch reference before uploading
  a large file. Compare echoed input fields with the source, including accents.

## Validate the output

- For a single query, check that `features` is non-empty or report no match. Verify
  longitude/latitude order and plausible coordinates for the requested territory,
  including overseas locations; do not interpret API coordinates as Lambert-93.
- For a CSV, compare input and output record counts and IDs before reporting completion.
- Count the results by status (`ok`, `not-found`, `skipped`, `error`) and report the counts.
  Never drop unmatched rows silently.
- When the input has a postcode or an INSEE code, check that `result_postcode` or
  `result_citycode` matches it.
- Check that accented names are echoed intact in bulk results: garbled names mean the
  service misread the encoding (see the batch reference).

## Report the result

Report the source and edition/access date when known, output path and format, CRS and
units, extent and counts (or raster dimensions), processing choices and checks performed.
Separate failed checks, warnings and checks not performed; keep unknown metadata explicit.
For advice-only requests, report the recommendation and its evidence without inventing files.

## References

- [references/quality-policy.md](references/quality-policy.md) — classify every CSV row
  as accepted, review or unmatched with explicit reasons.
- [references/api-parameters.md](references/api-parameters.md) — common parameters, the
  response fields, the parcel and POI indexes, and loading results into GDAL.
- [references/batch-csv.md](references/batch-csv.md) — bulk geocoding in detail (form fields,
  output columns, large files, converting to GeoPackage).

## Additional resources

- API documentation: <https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/>
- OpenAPI specification: <https://data.geopf.fr/geocodage/openapi.yaml>
