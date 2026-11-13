# geopf-altimetry

**Family:** [4. Analyze and derive](../README.md).

Retrieve point elevations and elevation profiles from the French Géoplateforme Elevation
API. The skill discovers terrain/surface resources and their metadata, preserves missing
elevations, joins returned heights to CSV rows and samples profiles along a path. It
keeps the raw response and writes a CSV or GeoJSON with the resource, units and vertical
reference (or `unknown`).

## When to use it

- Produce a terrain profile of a given number of samples between two coordinates, with
  the chosen resource, units and missing values.
- Add terrain heights to the points of a CSV, keeping every row, its identifiers and order.
- Join a saved Elevation API response to its input points without a network call, flagging
  missing elevations.
- Choose an elevation resource (terrain or surface product, coverage, resolution, vertical
  reference) from the API metadata.

## When to use another skill

- Download, mosaic or process a full DEM locally: [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md).
- Convert between vertical datums: [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md).
- Filter a whole area by altitude, optionally slope, and deliver candidate polygons:
  [`terrain-elevation-screening`](../../6-workflows/terrain-elevation-screening/README.md).

## What you get

- The raw API response, preserved, and a resulting CSV or GeoJSON.
- For a CSV join: the input rows, read as strings, plus `elevation_m`, `elevation_status`
  (`ok` or `nodata`), `elevation_accuracy`, `elevation_resource` and `vertical_reference`.
  The file is written only after all batches pass; failed batches are kept and the job is
  reported as partial.
- For a profile: sample index, coordinates, chainage in meters (projected or geodesic
  distance, not degrees), height/status and resource metadata. Nodata samples are left out
  of ascent/descent calculations.
- For GeoJSON: longitude/latitude geometry, with altitude and vertical reference as
  properties rather than a third ordinate, unless a compatible vertical datum is explicitly
  requested.
- Checks before reporting: one returned point per submitted point, returned coordinates
  compared with the input before joining by position, the requested profile sample count,
  finite values, plausible magnitudes for the territory and missing coverage.
- A report of resource, edition and access date, input/output counts, coordinates in
  EPSG:4326, height units and vertical reference (or unknown), sampling, missing values and
  whether heights represent terrain or surface.
- The skill keeps the `-99999` sentinel as missing data, never as a height. It does not
  treat terrain altitude as an ellipsoidal GNSS height, claim centimetric accuracy from two
  decimal places, or fill a whole raster with millions of point requests.

## Requirements

`curl` and Python 3; GDAL/PROJ only if inputs need reprojection. Check with
`curl --version` and `python3 --version`. The user installs missing software; the agent
does not. For Debian/Ubuntu, a user-run installation command is:

```bash
sudo apt install curl python3
```

Network: the Géoplateforme Elevation API (`https://data.geopf.fr/altimetrie/`); the
documented requests use no API key. Batches stay within the documented limit (presently
5,000 points), transient retries are capped at two and `Retry-After` is honored.

## MCP servers

Optional. With the [Geocontext](https://github.com/ignfab/geocontext) MCP server
connected, the agent first uses its `altitude` tool for one point or a few points, and
reports that the tool does not state the elevation resource. The Elevation API remains the
route for a chosen resource, many points, CSV joins and profiles. Without the server,
nothing changes. See [MCP servers](../../../docs/mcp-servers.md).

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-altimetry
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/4-analyze`.

## Example

> Using the Géoplateforme, produce in `output/` a twenty-point terrain profile between
> longitude 2.337306, latitude 48.849319 and longitude 2.367776, latitude 48.852891. State
> the chosen resource, the units and any missing values.

Every calculation starts from resource discovery (from [SKILL.md](SKILL.md)):

```bash
curl --fail --show-error --location --max-time 60 \
  https://data.geopf.fr/altimetrie/resources --output resources.json
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Workflow, prerequisites and validation. |
| [references/points-and-profiles.md](references/points-and-profiles.md) | Detailed recipes and edge cases: CSV join, nodata and profiles. |

## Tests

- [French agent scenarios](../../../tests/geopf-altimetry.md): 2 positive + 1 negative.
- Offline: [test_enrichment.py](../../../tests/test_enrichment.py) (joins, missing values,
  including the ALT-02 fixtures). Live, opt-in with `GEOSKILLS_LIVE=1`:
  [test_live_enrichment.py](../../../tests/test_live_enrichment.py) (two points and a
  20-sample profile).

## Related skills

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) selects a Géoplateforme API
  by the required output; an explicit elevation task comes straight to this skill.
