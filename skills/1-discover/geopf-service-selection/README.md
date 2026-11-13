# geopf-service-selection

**Family:** [1. Discover and select](../README.md).

An orientation guide to the French
[Géoplateforme services](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/).
It helps an agent choose an API by the expected output: metadata, maps, vector features,
dataset files, coordinates, elevation, routes, reachable areas or standards-validation
reports. It distinguishes WMS-R/WMS-V, WMTS, TMS and WFS, explains when to prefer
ready-made downloads or authenticated extraction, and links to current official service
guides. Implementation goes to `geopf-wfs-download`, `geopf-raster-download`, `geopf-geocoding`,
`geopf-file-download`, `geopf-altimetry`, `geopf-routing` or `apicarto-query` when installed.

## When to use it

- Get an overview of the services by deliverable, with entry points and main limits.
- Compare WMS-V, WMTS, TMS and WFS (styled display tiles cannot give exact building areas;
  WFS features or dataset files can).
- Choose between ready-made archives, a bounded WFS query and an authenticated extraction.
- Pick search and calculation services (autocomplete, reverse geocoding, elevation,
  routing, isochrones) and the metadata to check for each.
- Find a dataset whose name is unknown through the catalogue, CSW and search service.
- Choose a display service (WMS, WMTS, vector tiles) to show data without downloading it.

## When to use another skill

- Reproject a local file: [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md)
- Convert local files: [`gdal-vector-processing`](../../3-prepare/gdal-vector-processing/README.md)
  or [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md)
- Export features once the WFS is chosen: [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md)
- Download ready-made archives: [`geopf-file-download`](../../2-access/geopf-file-download/README.md)
- Geocode addresses: [`geopf-geocoding`](../../2-access/geopf-geocoding/README.md)
- Get point elevations or a profile: [`geopf-altimetry`](../../4-analyze/geopf-altimetry/README.md)
- Calculate a route or a reachable area: [`geopf-routing`](../../4-analyze/geopf-routing/README.md)

## What you get

- A recommendation: the service, its expected output, the discovery URL, access or volume
  caveats, and the next skill or official guide, with the metadata source and access date.
- Documented capabilities kept apart from requests actually tested; unreachable metadata
  reported as a limitation.
- Optionally, saved discovery responses (such as `wfs-capabilities.xml`), each checked to
  be non-empty, parseable XML or JSON of the expected type, not HTML, an OGC exception or
  an API error. An empty list is not evidence of a successful selection.
- For an asynchronous job, success means a completed job and an inspected file or report;
  a job identifier, HTTP 200 or finished validation job alone does not prove that the data
  is complete or conforms to the standard.

Layer names, fields, formats, CRSs and parameters come from metadata or the official API
schema, never from memory. Advice gets no fabricated file or validation result, and a
first page is never reported as a complete dataset.

## Requirements

- No local tools for conceptual guidance; web access for official documentation and live
  metadata checks.
- Optional `curl` for the discovery examples (check with `curl --version`). User-run
  installation: `sudo apt install curl` (Debian/Ubuntu) or `brew install curl` (macOS).
  The agent never installs software.
- Services: `https://data.geopf.fr` for most APIs; API Carto lives on another host
  (`https://apicarto.ign.fr`).
- Extraction, standards validation and usage statistics require an account and appropriate
  access. The skill does not automate account creation or interactive login; the user
  completes authentication outside the agent.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-service-selection
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/1-discover`. Install
the other service skills, or the whole repository, for their execution workflows; the
overview remains usable on its own through the official documentation links.

## Example

> I am new to the Géoplateforme services. Which services should I choose to display a map,
> retrieve vector features, download files, look up an address and run geographic
> calculations? Give an overview with the entry points and the main limits, without
> starting any download.

A discovery request that exports no user data:

```bash
curl --fail --show-error --location --max-time 60 \
  --output wfs-capabilities.xml \
  'https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities'
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Service selection, discovery, handoff and validation |
| [references/data-delivery.md](references/data-delivery.md) | Map images, tiles, vector features, file downloads and extraction |
| [references/search-and-processing.md](references/search-and-processing.md) | CSW, dataset search, geocoding, elevation, navigation, validation and usage statistics |

The references are an original summary of the official guides, checked on 2026-10-27,
not a frozen API specification. Resource availability, permissions and limits must be
checked at use time.

## Tests

French agent scenarios for service choice and handoff: [tests/geopf-service-selection.md](../../../tests/geopf-service-selection.md)
(5 positive + 2 negative). No offline test (advice only); [test_live.py](../../../tests/test_live.py)
runs the WFS, navigation and download-catalogue discovery requests.

## Related skills

- [`geopf-raster-download`](../../2-access/geopf-raster-download/README.md) downloads WMS-R and WMTS
  rasters once a map service is chosen; WMS-V and TMS details stay in this skill.
- [`apicarto-query`](../../2-access/apicarto-query/README.md) answers parcel, urban-planning,
  protected-area and RPG questions at a point or in an area.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  uses this skill with `geopf-wfs-download` when building data must be fetched online.
