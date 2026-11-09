# Points and profiles

## Attach point elevations

For an input CSV already in EPSG:4326 with `longitude` and `latitude` columns, submit those
columns in row order. Read the CSV as strings, keeping IDs and other attributes. For each
batch, run this check before writing the merged CSV. Here `rows` is the list of input
dictionaries and `response` is the parsed JSON returned with `zonly=false, measures=false`.
Set `resource` and `vertical_reference` from discovery (`unknown` if not established).

```python
import math
elevations = response.get("elevations")
if not isinstance(elevations, list) or len(elevations) != len(rows):
    raise ValueError("Missing or unexpected elevation results")
reserved = {"elevation_m", "elevation_status", "elevation_accuracy", "elevation_resource", "vertical_reference"}
if any(reserved.intersection(row) for row in rows):
    raise ValueError("Output columns already exist")
result = []
for row, point in zip(rows, elevations):
    for source, returned, lower, upper in (("longitude", "lon", -180, 180), ("latitude", "lat", -90, 90)):
        wanted, actual = float(row[source]), float(point[returned])
        if not (math.isfinite(wanted) and math.isfinite(actual) and lower <= wanted <= upper):
            raise ValueError("Invalid coordinates")
        if abs(wanted - actual) > 1e-7:
            raise ValueError("Results are reordered or refer to different points")
    z = float(point["z"])
    if not math.isfinite(z):
        raise ValueError("Invalid elevation")
    result.append(dict(row, elevation_m="" if z == -99999 else z,
                       elevation_status="nodata" if z == -99999 else "ok",
                       elevation_accuracy=point.get("acc", "unknown"),
                       elevation_resource=resource, vertical_reference=vertical_reference))
```

Write `result` with `csv.DictWriter` to a new file only after all batches pass; preserve
failed batches and report the job as partial. For GeoJSON, keep longitude/latitude as
the geometry and altitude/vertical reference as properties unless a compatible vertical
datum is explicitly requested. A third GeoJSON ordinate has ellipsoidal-height semantics
([RFC 7946, section 4](https://www.rfc-editor.org/rfc/rfc7946#section-4)).

## Sample a profile

Use `elevationLine.json` for a connected path, not a list of unrelated survey points.
The following example samples 20 positions along a two-vertex path:

```bash
curl --fail --show-error --get --max-time 60 \
  https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevationLine.json \
  --data-urlencode "resource=$RESOURCE" --data-urlencode 'lon=2.337306|2.367776' \
  --data-urlencode 'lat=48.849319|48.852891' --data-urlencode 'delimiter=|' \
  --data-urlencode sampling=20 --data-urlencode profile_mode=simple \
  --data-urlencode zonly=false --data-urlencode measures=false --output profile.json
```

Keep the original vertex order, choose sampling from path length and purpose, and verify
the returned point count (20 here), endpoints and elevation/nodata values. The current
documented sampling range is 2–5,000; `accurate` can change sampling behaviour, so use its
schema when requested. Compute chainage in metres using an appropriate projected or
geodesic distance, not Euclidean degrees. Export sample index, coordinates, chainage,
height/status and resource metadata. Exclude nodata from ascent/descent calculations;
sampling and noise affect those aggregates and should be reported.
