---
name: geopf-altimetry
description: Retrieves point elevations and elevation profiles from the French Géoplateforme Elevation API, preserving source metadata and missing values. Use to add terrain heights to coordinates or sample a profile along a path. Use a raster skill for downloading or processing a full DEM, and a CRS skill for converting vertical datums.
---

# Point elevations and profiles

Discover `https://data.geopf.fr/altimetrie/resources`, then inspect the chosen
`/altimetrie/resources/{id}`. Select terrain/surface product, coverage, resolution and
vertical reference from metadata. A catalogue bounding box does not guarantee coverage
at every point. Never treat terrain altitude as an ellipsoidal GNSS height.

## Prerequisites

Check `curl --version` and `python3 --version`. If missing, give the user
`sudo apt install curl python3` (Debian/Ubuntu) to run themselves.
**Never install software yourself.** Do not run interactive setup/login commands.

## Discover and query points

```bash
curl --fail --show-error --location --max-time 60 \
  https://data.geopf.fr/altimetrie/resources --output resources.json
```

Set `RESOURCE` to an advertised resource whose detail metadata fits the task. Reproject
input coordinates to geographic longitude/latitude if necessary; do not swap CSV columns
based on their position. This bounded example requests two points:

```bash
curl --fail --show-error --get --max-time 60 \
  https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json \
  --data-urlencode "resource=$RESOURCE" --data-urlencode 'lon=2.337306|2.367776' \
  --data-urlencode 'lat=48.849319|48.852891' --data-urlencode 'delimiter=|' \
  --data-urlencode zonly=false --data-urlencode measures=false --output elevations.json
```

For CSV input and profiles, read [the workflow reference](references/points-and-profiles.md).
Use bounded batches (at most the current documented limit, presently 5,000 points); keep
input IDs and order. Run requests in the foreground, cap transient retries at two and
honour `Retry-After`. Do not fill a whole raster by issuing millions of point requests.

## Validate the output

Require one returned point per submitted point and compare returned coordinates before
joining values by position. For a profile, validate the requested sample count separately.
Retain the `-99999` sentinel as missing data, never as a terrain height. Check finite
values, plausible magnitudes for the territory, and missing coverage. Two decimal places
do not establish centimetric accuracy. Keep source accuracy metadata when supplied.

## Report the result

Report resource/edition/access date, input/output count, coordinates in EPSG:4326, height
units and vertical reference (or unknown), sampling and missing values. Preserve the raw
response and the resulting CSV/GeoJSON. State whether heights represent terrain or surface.

## References

- [Points and profiles](references/points-and-profiles.md) — CSV join, nodata and profiles.
- [Official elevation guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/calcul-altimetrique/).
