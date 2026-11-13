# geopf-routing

**Family:** [4. Analyze and derive](../README.md).

Calculate routes and reachable areas (isochrones and isodistances) by travel time or
distance with the French Géoplateforme Navigation API, on the IGN road network. The skill
discovers navigation resources, profiles, units and direction from the service
capabilities, then exports the route or isochrone geometry as a GeoJSON
FeatureCollection. Results describe modeled network travel, not live traffic.

## When to use it

- Calculate a pedestrian or car route between two coordinates, save it as GeoJSON and
  report its distance, duration and endpoint offsets.
- Produce the area from which a point can be reached on foot in five minutes (an arrival
  isochrone), or the area reachable from it (departure).
- Compute an isodistance, a reachable area bounded by distance rather than time.

## When to use another skill

- Straight-line (geometric) buffer around local points, or custom network analysis on
  local data: [`geopandas-vector-analysis`](../geopandas-vector-analysis/README.md) or other local geometry
  tools. This skill relies on the IGN service only.

## What you get

- The raw responses (`capabilities.json`, `route.json`, `isochrone.json`), preserved.
- A new GeoJSON FeatureCollection with one Feature: a LineString or MultiLineString route,
  or a Polygon or MultiPolygon reachable area. Its properties keep the version, units and
  travel parameters returned by the service.
- Checks before reporting: response errors even after HTTP success, resource, profile and
  units, and a nonempty geometry. A route needs a positive, plausible distance and duration
  and endpoints near the requested locations, with snapping measured in meters. A
  reachable area needs a valid polygon with the requested cost, units and direction; its
  area is assessed in a projected CRS.
- The export refuses a response whose CRS is not confirmed as EPSG:4326; projected
  coordinates are never relabeled as WGS84. The written file is reopened with GDAL or
  GeoPandas to check finite coordinates, valid geometry and geographic extent.
- A report of resource, version and date, input points, profile, optimization or
  cost/direction, constraints, output CRS, geometry and count, units and validation.
- The skill does not claim a straight-line buffer, a timetable or a real-time traffic
  result, and does not replace a network area (which may have holes or disconnected parts)
  with a circular buffer. It never assumes a resource from an old example is still
  available.

## Requirements

curl for requests and Python 3's standard library for response/GeoJSON handling.
Final spatial validation needs either existing GDAL or GeoPandas, not both; discovery
and raw responses do not. Missing spatial checks must remain explicit.

Check the request tools with `curl --version` and `python3 --version`; check the selected GIS tool only for the spatial stage.

If absent, the user can install only the needed tool: `sudo apt install curl`,
`sudo apt install python3`, `sudo apt install gdal-bin` (Debian/Ubuntu), or
`python3 -m pip install 'geopandas>=1.0,<2'` for the Python GIS route.
The agent never installs software itself.

Network: the Géoplateforme Navigation API (`https://data.geopf.fr/navigation/`); the
documented requests use no API key. Requests run in the foreground, transient retries are
capped at two, `Retry-After` is honored and an unreachable point is not retried repeatedly.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-routing
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/4-analyze`.

## Example

> Using the Géoplateforme, calculate a pedestrian route between longitude 2.337306,
> latitude 48.849319 and longitude 2.367776, latitude 48.852891. Save a GeoJSON in
> `output/` and give the distance in meters, the duration in seconds and any offsets of
> the endpoints from the requested points.

The route request from [SKILL.md](SKILL.md), once `RESOURCE` is set from the capabilities:

```bash
curl --fail --show-error --get --max-time 60 \
  https://data.geopf.fr/navigation/itineraire \
  --data-urlencode "resource=$RESOURCE" --data-urlencode 'start=2.337306,48.849319' \
  --data-urlencode 'end=2.367776,48.852891' --data-urlencode profile=pedestrian \
  --data-urlencode optimization=fastest --data-urlencode geometryFormat=geojson \
  --data-urlencode distanceUnit=meter --data-urlencode timeUnit=second \
  --data-urlencode getSteps=false --output route.json
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Workflow, prerequisites and validation. |
| [references/reachable-areas.md](references/reachable-areas.md) | Detailed recipes and edge cases: isochrone units and direction, GeoJSON export. |

## Tests

- [French agent scenarios](../../../tests/geopf-routing.md): 2 positive + 1 negative.
- Offline: [test_enrichment.py](../../../tests/test_enrichment.py) (GeoJSON export). Live,
  opt-in with `GEOSKILLS_LIVE=1`: [test_live.py](../../../tests/test_live.py) (navigation
  discovery) and [test_live_enrichment.py](../../../tests/test_live_enrichment.py) (a short
  pedestrian route and a five-minute isochrone).

## Related skills

- [`geopf-geocoding`](../../2-access/geopf-geocoding/README.md) locates addresses as
  starting points; ambiguous addresses are resolved before routing.
- [`geopandas-vector-analysis`](../geopandas-vector-analysis/README.md) overlays a reachable area with an
  area of interest.
- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) selects a Géoplateforme API
  by the required output; an explicit navigation task comes straight to this skill.
