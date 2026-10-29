# Reachable areas and export

## Five-minute walking area

Choose a resource whose `isochrone` operation supports the options below. `costType=time`
with `timeUnit=second` makes `300` five minutes; `costType=distance` uses `distanceUnit`.
`departure` means reachable from the point; `arrival` means able to reach the point.

```bash
curl --fail --show-error --get --max-time 60 \
  https://data.geopf.fr/navigation/isochrone \
  --data-urlencode "resource=$RESOURCE" --data-urlencode 'point=2.337306,48.849319' \
  --data-urlencode profile=pedestrian --data-urlencode direction=departure \
  --data-urlencode costType=time --data-urlencode costValue=300 \
  --data-urlencode timeUnit=second --data-urlencode distanceUnit=meter \
  --data-urlencode geometryFormat=geojson --output isochrone.json
```

Confirm the returned CRS: these examples use the service's geographic default. If a
different CRS is needed, consult the operation's current schema; discovery and older
guides can differ in how a projection parameter is named. Validate/reproject the actual
returned coordinates before writing RFC 7946 GeoJSON.

## Export the response geometry

The API wraps its geometry in a response object; saving that object with a `.geojson`
extension does not turn it into a FeatureCollection. For a parsed `response` already
confirmed in EPSG:4326, set `operation` to `route` or `isochrone` and use:

```python
import math
if response.get("crs") != "EPSG:4326":
    raise ValueError("Confirm/reproject the response CRS before GeoJSON export")
expected = {"route": {"LineString", "MultiLineString"}, "isochrone": {"Polygon", "MultiPolygon"}}
geometry = response.get("geometry", {})
if geometry.get("type") not in expected[operation] or not geometry.get("coordinates"):
    raise ValueError("Missing or wrong geometry type")
if operation == "route":
    for key in ("distance", "duration"):
        value = float(response[key])
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Nonpositive or invalid route metric")
properties = {key: value for key, value in response.items()
              if key not in {"geometry", "bbox", "portions", "crs"}}
collection = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": geometry, "properties": properties}]}
```

Serialize `collection` with `json.dump(..., allow_nan=False)` to a new GeoJSON. Reopen
with GDAL/GeoPandas, check finite coordinates, valid nonempty geometry and geographic
extent, then compare requested and returned options. Preserve version, units and travel
parameters in properties. For routes, measure snapping in metres, not coordinate degrees.
For polygons, assess area in an appropriate projected CRS. A network area may contain
holes or disconnected parts; do not replace it with a circular buffer.

Official reference: [Isochrone/isodistance guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/calcul-isochrone-isodistance/).
