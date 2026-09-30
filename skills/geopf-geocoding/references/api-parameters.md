# Geocoding API parameters

Parameters checked against the live OpenAPI specification on 2026-09-30.

Full specification: <https://data.geopf.fr/geocodage/openapi.yaml>. Live list of indexes and
fields: `curl -fsS --max-time 30 https://data.geopf.fr/geocodage/getCapabilities`.

## `/search` parameters

| Parameter | Index | Description |
|-----------|-------|-------------|
| `q` | all | Free text to search for |
| `index` | — | `address` (default), `poi`, `parcel`, or a comma-separated list such as `poi,address` |
| `limit` | all | Maximum number of results: default 10, max 50 (max 20 with `returntruegeometry`) |
| `lon`, `lat` | all | Favour candidates close to this point |
| `type` | address | `housenumber`, `street`, `locality` or `municipality` |
| `postcode` | address, poi | Postcode filter. Takes several comma-separated values |
| `citycode` | address, poi | INSEE code filter. Takes several comma-separated values |
| `depcode` | address, poi | Département code filter |
| `city` | address, poi | Town name filter |
| `category` | poi | POI category, such as `administratif` or `cimetière` |
| `returntruegeometry` | poi, parcel | Add the real geometry (such as a parcel polygon) in a `truegeometry` property. The feature geometry stays a point |
| `autocomplete` | all | Default `1`. Set to `0` to disable completion for a complete query; this does not enforce an exact match |
| `departmentcode`, `municipalitycode`, `oldmunicipalitycode`, `districtcode`, `section`, `sheet`, `number` | parcel | Cadastral parcel filters |

`/reverse` supports index-specific filters, but not the text query or autocomplete mode.
`lon`/`lat` give the query point, or `searchgeom` gives a geometry (Point, LineString,
Polygon, or the API's Circle extension) to search by intersection. Check the OpenAPI
specification for the parameters accepted by each operation.

## Response fields

Address (`_type: "address"`):

| Field | Meaning |
|-------|---------|
| `label` | Full address, ready to display |
| `score` | Relevance from 0 to 1 |
| `type` | `housenumber`, `street`, `locality` or `municipality` |
| `housenumber`, `street`, `name` | Number with any suffix (bis, ter), street name, number and street |
| `postcode`, `citycode`, `city`, `depcode` | Postcode, INSEE code, town, département |
| `oldcitycode`, `oldcity` | Former municipality, after a merger |
| `district` | Arrondissement (Paris, Lyon, Marseille) |
| `context` | Département number and name, region |
| `id`, `banId` | BAN interoperability key and BAN UUID |
| `x`, `y` | Coordinates in the legal projection (Lambert-93 in mainland France) |
| `distance` | Distance in metres to the query point (`/reverse` only) |

POI (`_type: "poi"`): `toponym`, `category`, `postcode`, `citycode`, `city` and `depcode`. Most
of these are **arrays**, because one POI can span several towns. `extrafields.cleabs` is the
BD TOPO identifier.

Parcel (`_type: "parcel"`): `id` (14 characters: département + commune + cadastral prefix +
section + number, for example `940670000D0050`), `departmentcode`, `municipalitycode`,
`section`, `sheet`, `number` and `city`.

## Examples

Find a parcel from its cadastral reference:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/search?index=parcel&departmentcode=94&municipalitycode=067&section=0D&number=0050&returntruegeometry=true"
```

The filters accept both short and zero-padded values (`section=D` or `0D`, `number=50` or
`0050`). The parcel `id` always uses the padded form: a two-character section and a
four-digit number.

Find a POI and get its real geometry as well:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/search?q=gare+de+lyon&index=poi&city=paris&limit=1&returntruegeometry=true"
```

Find a municipality and its INSEE code:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/search?q=saint-mande&type=municipality&limit=1"
```

Autocompletion, as used by search boxes (note the different parameter names):

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/completion?text=73+av+de+paris&maximumResponses=5"
```

## Using the results

In Bash pipelines, use `set -o pipefail` so an HTTP failure also fails the pipeline.
Extract the fields you need with `jq`:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/search?q=8+bd+du+port+cergy&limit=1" \
  | jq -er 'if (.features | length) == 0 then error("No match") else .features[0] end | [.properties.label, .properties.score, .geometry.coordinates[0], .geometry.coordinates[1]] | @csv'
```

The response is valid GeoJSON, so GDAL can read it directly. The geometry is the point;
POI attributes that are arrays become JSON strings:

```bash
ogr2ogr -f GPKG mairie.gpkg \
  "https://data.geopf.fr/geocodage/search?q=mairie&index=poi&citycode=94067"
```

To keep the real geometry returned by `returntruegeometry=true`, promote the
`truegeometry` property to the feature geometry before writing the file:

```bash
curl -fsS --max-time 30 "https://data.geopf.fr/geocodage/search?index=parcel&departmentcode=94&municipalitycode=067&section=0D&number=0050&returntruegeometry=true" \
  | python3 -c '
import json, sys
fc = json.load(sys.stdin)
if not fc.get("features"):
    raise SystemExit("No parcel found")
for f in fc["features"]:
    geometry = f["properties"].pop("truegeometry", None)
    if not geometry or geometry.get("type") not in ("Polygon", "MultiPolygon"):
        raise SystemExit("Parcel boundary missing from response")
    f["geometry"] = geometry
json.dump(fc, sys.stdout)
' > parcelle.geojson
```

Python, with `requests`:

```python
import requests

r = requests.get(
    "https://data.geopf.fr/geocodage/search",
    params={"q": "73 avenue de Paris", "postcode": "94160", "limit": 1},
    timeout=30,
)
r.raise_for_status()
features = r.json()["features"]
if not features:
    raise SystemExit("No address matched the query")
feature = features[0]
lon, lat = feature["geometry"]["coordinates"]
score = feature["properties"]["score"]
```
