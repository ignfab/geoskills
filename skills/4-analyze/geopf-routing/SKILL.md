---
name: geopf-routing
description: Calculates routes and reachable areas by travel time or distance using the French Géoplateforme Navigation API, with discovered resources, profiles, units and direction. Use for pedestrian or car itineraries, isochrones and isodistances on the IGN road network. Use local geometry tools for straight-line buffers or custom network analysis.
---

# Routes and reachable areas

Discover `https://data.geopf.fr/navigation/getcapabilities`. Inspect the selected
resource's `availableOperations` and their `availableParameters`: profiles, optimization,
units and constraints differ by operation/resource. Never assume a resource from an old
example is still available. The API describes modelled network travel, not live traffic.

## Prerequisites

Check `curl --version` and `python3 --version`. GDAL or GeoPandas can inspect/export the
result. If missing, give the user `sudo apt install curl python3 gdal-bin` (Debian/Ubuntu).
**Never install software yourself.** Do not run interactive login/setup commands.

## Discover and calculate a route

```bash
curl --fail --show-error --location --max-time 60 \
  https://data.geopf.fr/navigation/getcapabilities --output capabilities.json
```

Set `RESOURCE` to an advertised resource supporting the requested options. This example
uses geographic longitude,latitude, a pedestrian profile, metres and seconds:

```bash
curl --fail --show-error --get --max-time 60 \
  https://data.geopf.fr/navigation/itineraire \
  --data-urlencode "resource=$RESOURCE" --data-urlencode 'start=2.337306,48.849319' \
  --data-urlencode 'end=2.367776,48.852891' --data-urlencode profile=pedestrian \
  --data-urlencode optimization=fastest --data-urlencode geometryFormat=geojson \
  --data-urlencode distanceUnit=meter --data-urlencode timeUnit=second \
  --data-urlencode getSteps=false --output route.json
```

Use [reachable areas and export](references/reachable-areas.md) for isochrones and saving
GeoJSON. Resolve ambiguous addresses before routing. State constraints and the allowed
snap distance if the task needs it. Run requests in the foreground, cap transient retries
at two and honour `Retry-After`; do not repeatedly retry an unreachable point.

## Validate the output

Check response errors even after HTTP success, resource/profile/units and nonempty
geometry. A route needs a line, positive plausible distance/duration, and endpoints near
the requested locations. Report network snapping and large deviations. A reachable area
needs a nonempty valid polygon/multipolygon, the requested cost, units and direction.
Inspect extent/CRS before GeoJSON export; never relabel projected coordinates as WGS84.

## Report the result

Report resource/version/date, input points, profile, optimization or cost/direction,
constraints, output CRS/geometry/count, units and validation. Preserve the raw response.
Do not claim a straight-line buffer, a timetable or real-time traffic result.

## References

- [Reachable areas and export](references/reachable-areas.md) — units, direction and GeoJSON.
- [Official routing guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/calcul-itineraire/).
