---
name: geopf-geocoding
description: Geocodes addresses, points of interest and cadastral parcels with the French Géoplateforme geocoding API (data.geopf.fr/geocodage), one query at a time or in bulk from a CSV file, and reverse-geocodes coordinates. Use when the user wants to geocode an address or a CSV file of addresses, run reverse geocoding, find the coordinates of a French address (BAN), a locality or a cadastral parcel, or find the address at a given point.
---

# Géoplateforme geocoding

Geocode French addresses (Base Adresse Nationale), points of interest and cadastral parcels
with the IGN Géoplateforme geocoding API. No API key is needed.

## Prerequisites

- `curl` (or any HTTP client). No API key is needed.
- Optional: `jq` to extract fields, GDAL (`ogr2ogr`) to convert the results.
- If a tool is missing, give the user the install command and let them run it; do not install software yourself.

## Endpoints

Base URL: `https://data.geopf.fr/geocodage`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/search` | GET | Text → coordinates |
| `/reverse` | GET | Coordinates → nearest address, POI or parcel |
| `/search/csv` | POST | Bulk geocoding of a CSV file (UTF-8, max 50 MB / 200,000 rows) |
| `/reverse/csv` | POST | Bulk reverse geocoding of a CSV file with `lon`/`lat` columns |
| `/completion` | GET | Autocompletion for search-as-you-type |
| `/getCapabilities` | GET | Indexes, fields and parameters, as JSON |

Responses from `/search` and `/reverse` are GeoJSON `FeatureCollection`s in **WGS84
(lon, lat)**. Each feature has a `score` from 0 to 1. Address features also carry `x`/`y`
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
curl -fsS --max-time 300 -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv \
  -F columns=numero -F columns=voie -F columns=commune \
  -F postcode=code_postal \
  -o adresses_geocodees.csv
```

The output CSV keeps the input columns and adds `longitude`, `latitude`, `result_score`,
`result_label`, `result_citycode`, and so on.

## Good practice

- Check HTTP success, then handle an empty `features` array or a non-`ok` CSV status.
- Review low `score` / `result_score` values (0.5 is a starting heuristic, not a probability
  or a universal threshold). Compare the returned town and `type` / `result_type` with
  the query: a street result for a requested house number needs review.
- Use `postcode` or `citycode` filters whenever the data has them. They remove most
  mismatches between towns that share a street name.
- For more than a few hundred addresses, use `/search/csv` rather than looping over `/search`.
- Stay under **50 requests per second** per IP address. On HTTP 429, respect `Retry-After`
  when provided and use bounded retries; do not retry invalid requests unchanged.
- For CSV encoding, splitting and error statuses, read the batch reference before uploading
  a large file. Compare echoed input fields with the source, including accents.

## Validate the output

- Count the results by status (`ok`, `not-found`, `skipped`, `error`) and report the counts.
  Never drop unmatched rows silently.
- When the input has a postcode or an INSEE code, check that `result_postcode` or
  `result_citycode` matches it.
- Check that accented names are echoed intact in bulk results: garbled names mean the
  service misread the encoding (see the batch reference).

## References

- [references/api-parameters.md](references/api-parameters.md) — common parameters, the
  response fields, the parcel and POI indexes, and loading results into GDAL.
- [references/batch-csv.md](references/batch-csv.md) — bulk geocoding in detail (form fields,
  output columns, large files, converting to GeoPackage).

## Additional resources

- API documentation: <https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/>
- OpenAPI specification: <https://data.geopf.fr/geocodage/openapi.yaml>
