---
name: geopf-geocoding
description: Geocodes addresses, points of interest and cadastral parcels with the French Géoplateforme geocoding API (data.geopf.fr/geocodage), one query at a time or in bulk from a CSV file, and reverse-geocodes coordinates. Use when the user wants to géocoder une adresse, faire du géocodage inverse, géocoder un fichier CSV en masse, find the coordinates of a French address (BAN), a lieu-dit or a parcelle cadastrale, or find the address at a given point.
---

# Géoplateforme geocoding

Geocode French addresses (Base Adresse Nationale), points of interest and cadastral parcels
with the IGN Géoplateforme geocoding API. No API key is needed.

## Prerequisites

- `curl` (or any HTTP client). No API key is needed.
- Optional: `jq` to extract fields, GDAL (`ogr2ogr`) to convert the results.

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
curl -s "https://data.geopf.fr/geocodage/search?q=73+avenue+de+paris+saint-mande&limit=1"
```

Restrict the results with filters: `postcode`, `citycode` (INSEE code), `depcode`, `city`, and
`type=housenumber|street|locality|municipality`:

```bash
curl -s "https://data.geopf.fr/geocodage/search?q=avenue+de+paris&citycode=94067&type=street"
```

Reverse geocode a point. The index can be `address`, `poi` or `parcel`:

```bash
curl -s "https://data.geopf.fr/geocodage/reverse?lon=2.4245&lat=48.8451&index=parcel&limit=1"
```

Geocode a CSV file in bulk. `columns` lists the columns that are joined into the query text;
repeat it once per column:

```bash
curl -s -X POST https://data.geopf.fr/geocodage/search/csv \
  -F data=@adresses.csv \
  -F columns=numero -F columns=voie -F columns=commune \
  -F postcode=code_postal \
  -o adresses_geocodees.csv
```

The output CSV keeps the input columns and adds `longitude`, `latitude`, `result_score`,
`result_label`, `result_citycode`, and so on.

## Good practice

- **Always check `score`** (or `result_score`). A score below about 0.5 is usually a wrong
  match. Also compare `result_type` with what you expected: a result of type `street` or
  `municipality` means the house number was not found.
- Use `postcode` or `citycode` filters whenever the data has them. They remove most
  mismatches between towns that share a street name.
- For more than a few hundred addresses, use `/search/csv` rather than looping over `/search`.
- Stay under **50 requests per second** per IP address. Beyond that, the service rejects
  requests.

## References

- [references/api-parameters.md](references/api-parameters.md) — every parameter, the
  response fields, the parcel and POI indexes, and loading results into GDAL.
- [references/batch-csv.md](references/batch-csv.md) — bulk geocoding in detail (form fields,
  output columns, large files, converting to GeoPackage).

## Additional resources

- API documentation: <https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/geocodage/>
- OpenAPI specification: <https://data.geopf.fr/geocodage/openapi.yaml>
