# Géocodage API parameters

Full specification: <https://data.geopf.fr/geocodage/openapi.yaml>. Live list of indexes and
fields: `curl -s https://data.geopf.fr/geocodage/getCapabilities`.

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
| `autocomplete` | all | Default `true`. Set to `false` for exact queries on complete strings |
| `departmentcode`, `municipalitycode`, `oldmunicipalitycode`, `districtcode`, `section`, `sheet`, `number` | parcel | Cadastral parcel filters |

`/reverse` takes the same filters. `lon`/`lat` give the query point, or `searchgeom` gives a
GeoJSON geometry (Point, LineString or Polygon) to search by intersection.

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

Parcel (`_type: "parcel"`): `id` (14 characters: département + commune + ancienne commune +
section + number, for example `940670000D0050`), `departmentcode`, `municipalitycode`,
`section`, `sheet`, `number` and `city`.

## Examples

Find a parcel from its cadastral reference:

```bash
curl -s "https://data.geopf.fr/geocodage/search?index=parcel&departmentcode=94&municipalitycode=067&section=0D&number=0050&returntruegeometry=true"
```

The filters accept both short and zero-padded values (`section=D` or `0D`, `number=50` or
`0050`). The parcel `id` always uses the padded form: a two-character section and a
four-digit number.

Find a POI and get its real geometry as well:

```bash
curl -s "https://data.geopf.fr/geocodage/search?q=gare+de+lyon&index=poi&city=paris&limit=1&returntruegeometry=true"
```

Find a municipality and its INSEE code:

```bash
curl -s "https://data.geopf.fr/geocodage/search?q=saint-mande&type=municipality&limit=1"
```

Autocompletion, as used by search boxes (note the different parameter names):

```bash
curl -s "https://data.geopf.fr/geocodage/completion?text=73+av+de+paris&maximumResponses=5"
```

## Using the results

Extract the fields you need with `jq`:

```bash
curl -s "https://data.geopf.fr/geocodage/search?q=8+bd+du+port+cergy&limit=1" \
  | jq -r '.features[0] | [.properties.label, .properties.score, .geometry.coordinates[0], .geometry.coordinates[1]] | @csv'
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
curl -s "https://data.geopf.fr/geocodage/search?index=parcel&departmentcode=94&municipalitycode=067&section=0D&number=0050&returntruegeometry=true" \
  | python3 -c '
import json, sys
fc = json.load(sys.stdin)
for f in fc["features"]:
    f["geometry"] = f["properties"].pop("truegeometry")
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
feature = r.json()["features"][0]
lon, lat = feature["geometry"]["coordinates"]
score = feature["properties"]["score"]
```
