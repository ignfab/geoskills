---
name: apicarto-query
description: Queries IGN's API Carto (apicarto.ign.fr) for cadastral parcels and municipalities, urban-planning documents, zones and easements from the Géoportail de l'Urbanisme (PLU, PLUi, SUP), protected natural areas (Natura 2000, ZNIEFF, nature reserves, national and regional parks), RPG agricultural parcels and administrative units, by code or by intersecting GeoJSON geometry, with complete pagination. Use when the user asks which parcels, PLU zone, easements, protected areas or crops lie at a point or within an area in France, or wants every parcel of a municipality or cadastral section with its official area. For address geocoding use geopf-geocoding, for bulk national layers geopf-file-download or geopf-wfs-download, and for map images geopf-raster-download.
---

# API Carto

API Carto answers "what lies here?" questions on French reference data. The base URL is
`https://apicarto.ign.fr/api`. Each module publishes its OpenAPI description at
`https://apicarto.ign.fr/api/doc/<module>.yml`: read the paths, parameters and patterns
there, not from memory. Responses are GeoJSON `FeatureCollection`s in WGS84
longitude/latitude, with `numberMatched` and `numberReturned`.

## MCP servers

Optional. When the [Geocontext](https://github.com/ignfab/geocontext) MCP server is
connected (tools often prefixed `mcp__geocontext__`), use it first for a question about
**one point**; this route needs no local tool. When the user names a place, get the
coordinates with `geocode`. The first `geocode` candidate can be a namesake elsewhere or
another object of the right municipality: check `fulltext` and `kind` as well as `city`
and `zipcode`. When they do not match, add the postcode to the text, not the department
name, or take another candidate.

| Question at a point | Geocontext tool | What it returns |
| --- | --- | --- |
| Parcel, cadastral sheet, municipality | `cadastre` | The nearest cadastral objects within 10 m, at most one per type; nothing beyond that distance |
| Urban-planning document, zone, prescriptions | `urbanisme` | Géoportail de l'Urbanisme objects at or near the point, including the zone of the plan |
| Public-utility easements (SUP) | `assiette_sup` | Easement areas at or near the point |
| Municipality, department, region, EPCI | `adminexpress` | The administrative units covering the point, with their INSEE codes |

`cadastre`, `urbanisme` and `assiette_sup` give a `distance` in metres between the point
and each object: **report it**, and say that an object is near the point, not at it, when
the distance is above 0. A `cadastre` result without a `parcelle` object means that no
parcel lies within 10 m, as on a road or a public space, where the municipality and the
cadastral sheet are still returned: say so, and query API Carto with a small area if a
parcel is still needed. An empty `urbanisme` result does not mean that no rule applies:
query `gpu/municipality` with API Carto and report `is_rnu` (national rules) before
answering.

Use API Carto, below, for an area, a whole municipality or section, parcels by code,
complete paginated listings, protected natural areas, RPG parcels and file outputs. Check
an answer before reporting it (no error returned, objects in the municipality requested);
the reporting rules of this skill apply to both routes. Without Geocontext, or when a call
fails, use API Carto for every case. Never install, configure or start an MCP server
yourself.

## Prerequisites

Check only the selected stage: the pagination helper uses Python 3's standard library;
the manual HTTP examples use curl. Reuse existing GDAL (`ogrinfo --version`) for the
documented spatial validation and format conversion. If missing, give the user the
corresponding Debian/Ubuntu command: `sudo apt install python3`, `sudo apt install curl`
or `sudo apt install gdal-bin`. Do not require GDAL just to inspect API metadata or run
the helper; without it, report the outstanding spatial checks before claiming validation.
**Never install software yourself.** No API key is needed, except for the wine appellation
module (`aoc`): ask the user to provide a key outside the chat and never print it in logs.

## Choose the module

| Need | Endpoint (under `/api/`) | Main parameters |
| --- | --- | --- |
| Parcels of a municipality or section, or at a point or in an area | `cadastre/parcelle` | `code_insee`, `section`, `numero`, `code_arr`, `geom` |
| Municipality boundary, cadastral sheets, parcel points | `cadastre/commune`, `cadastre/feuille`, `cadastre/localisant` | `code_insee`, `section`, `geom` |
| Urban-planning document and its zones | `gpu/document`, `gpu/zone-urba`, `gpu/secteur-cc` | `geom` or `partition` |
| Prescriptions and information of a plan | `gpu/prescription-surf`, `-lin`, `-pct`; `gpu/info-surf`, `-lin`, `-pct` | `geom` or `partition` |
| Public-utility easements (SUP) | `gpu/assiette-sup-s`, `-l`, `-p`; `gpu/generateur-sup-s`, `-l`, `-p` | `geom` or `partition` |
| Whether a municipality has its own plan | `gpu/municipality` | `insee` or `geom` |
| Protected areas | `nature/natura-habitat`, `natura-oiseaux`, `znieff1`, `znieff2`, `rnn`, `rnc`, `pn`, `pnr`, `rncf` | `geom` |
| Agricultural parcels of a year | `rpg/v2` (2015 onward), `rpg/v1` (2010–2014) | `annee`, `geom` (required) |
| Municipality, department or region at a point | `limites-administratives/commune`, `departement`, `region` | `lon` and `lat`, or `geom` |
| Any Géoplateforme WFS layer intersecting a geometry | `wfs-geoportail/search` | `source` (WFS typename), `geom` |

`codes-postaux/communes/<postcode>` returns a JSON list, not GeoJSON. Details, field
meanings and caveats are in the [cadastre](references/cadastre.md) and
[other modules](references/modules.md) references.

## Query

`geom` is a GeoJSON **geometry** (not a Feature) in longitude, latitude order. Discover
the module first, then query a point:

```bash
curl --fail --show-error --location --max-time 60 \
  --output nature.yml https://apicarto.ign.fr/api/doc/nature.yml
curl --show-error --get --max-time 60 https://apicarto.ign.fr/api/nature/natura-habitat \
  --data-urlencode 'geom={"type":"Point","coordinates":[2.6458,48.4038]}' \
  --output natura-habitat.json
```

Without `--fail`, a 400 or 500 response is saved so that its JSON message can be read.
Natura 2000 has two networks: query both `natura-habitat` and `natura-oiseaux`.

A response holds 1000 features by default, and the `next` links of the responses point to
`http://localhost`. Use the bundled script, which pages with `_start`, rejects error
responses, repeated identifiers and incomplete counts, and never overwrites a file:

```bash
python3 scripts/fetch_features.py cadastre/parcelle parcelles.geojson --param code_insee=94067
python3 scripts/fetch_features.py gpu/zone-urba zones.geojson --geometry zone.geojson
```

`--geometry` takes a GeoJSON file with one longitude/latitude geometry and sends it by
POST. Simplify a long boundary or query by code instead: the service expects a
"reasonable" number of points. Run requests in the foreground; retry a 5xx error at most
twice, a few seconds apart, and report it if it persists.

## Rules

- Codes are strings. `section` has 2 characters and `numero` 4 (`J` 182 → `0J` and
  `0182`); otherwise the API answers HTTP 400. Paris, Lyon and Marseille parcels need the
  municipality code with `code_arr` (`75056` with `101`, not `75101`).
- An empty collection is an answer only for a query inside the module's coverage. Swapped
  coordinates also return HTTP 200 with no feature: check the order and the place first.
- `contenance` is the official cadastral area in m²; it differs from the area computed
  from the geometry. RPG `surf_parc` is in hectares.
- A `gpu/municipality` result with `is_rnu` true means that national rules apply (no local
  plan), so no zone is expected.
- For a whole department or region, use the `geopf-file-download` or `geopf-wfs-download`
  skill rather than thousands of API Carto pages.

## Validate the output

- The response is a `FeatureCollection`, not `{"code": 400, …}` or `{"type": "error", …}`;
  the script exits with status 2 on those.
- The number of features equals `numberMatched` (`"status": "complete"` in the script
  summary), identifiers are unique and the geometries have the expected type.
- Reopen the file: `ogrinfo -so -al parcelles.geojson` reports EPSG:4326 and an extent in
  France (metropolitan longitudes about −5 to 10, latitudes about 41 to 51.5). Overseas
  data have their own ranges. For areas, use a suitable analysis CRS and verify units;
  Lambert-93 is a metropolitan-France fallback, not an API/output requirement.
- A GeoJSON whose `crs` member is `urn:ogc:def:crs:CRS::84` (nature module) makes GDAL print
  `crs not found: CRS:84`; the coordinates are still longitude/latitude. Check the extent.
- For zoning, report the document (`partition`, `idurba`, `du_type`) and its approval date
  (`datvalid`) with each zone.

## Report the result

Report the module and endpoint, the query (codes or geometry and its source), the access
date, `numberMatched` and the number of features written, the output path and CRS, and the
fields the answer relies on (zone code and document, site codes, `contenance`). Say that
API Carto returns data for information: the regulation and graphic documents of the
approved plan remain the reference for urban planning, and the cadastre does not prove
ownership or boundaries. Report service errors as such; never substitute an answer from
memory.

## References

- [references/cadastre.md](references/cadastre.md) — identifiers, sections, arrondissements,
  sheets, pagination and parcel fields.
- [references/modules.md](references/modules.md) — urban planning (GPU), protected areas,
  RPG, administrative units, postcodes, generic WFS search and appellations.
- [API Carto documentation](https://apicarto.ign.fr/api/doc/) and the
  [Géoplateforme guide](https://geoservices.ign.fr/documentation/services/api-et-services-ogc/api-carto-rest).
