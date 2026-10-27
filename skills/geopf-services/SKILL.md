---
name: geopf-services
description: Explains the French Géoplateforme (GPF/IGN, data.geopf.fr) services and selects an API by the required output. Use for a service overview, WMS/WMTS/WFS/TMS comparisons, or choosing between dataset discovery, downloads, extraction, geocoding and geographic calculations. For an explicit WFS download, WMS/WMTS raster request or geocoding task, use the corresponding specialized skill directly.
---

# Géoplateforme services overview

Use this skill to choose a service, not to download every advertised dataset. Start with
the [official service guide](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/).
The endpoint host is `https://data.geopf.fr`; the paths below are discovery entry points,
not evidence that a particular dataset is available.

## Prerequisites

No local software is needed for an explanation. Use web access to read the official
guides and current service metadata when confirming availability.

For optional command-line discovery, check `curl --version`. If missing, give the user
`sudo apt install curl` (Debian/Ubuntu) or `brew install curl` (macOS) to run themselves.
**Never install software yourself.** Do not launch interactive setup or login commands;
ask the user to complete authentication outside the agent when required.

## Choose by the required output

| User needs | Service | Discovery on `https://data.geopf.fr` |
|------------|---------|-------------------------------------|
| Dataset descriptions, provenance, licence and access links | CSW metadata catalogue | `/csw`, CSW 2.0.2 `GetCapabilities`, then paginated `GetRecords` |
| A map image with a chosen extent, size and supported CRS | WMS-R for raster sources; WMS-V for vector sources | `/wms-r` or `/wms-v/ows`, WMS `GetCapabilities` |
| Fast display of precomputed image tiles | WMTS | `/wmts`, WMTS `GetCapabilities` |
| Vector tiles with client-side styling | TMS | `/tms/1.0.0`, then layer `metadata.json` |
| Queryable vector geometries and attributes | WFS | `/wfs/ows`, WFS `GetCapabilities`, then `DescribeFeatureType` |
| Ready-made dataset archives or tiles for offline work | Download API | `/telechargement/capabilities` (paginated Atom feed) |
| A custom vector export by tables, fields, extent, CRS and format | Extraction API (authenticated, OGC API Processes) | `/extraction`; accessible data via the warehouse API |
| Coordinates from an address, place or parcel, or reverse lookup | Geocoding | `/geocodage/getcapabilities` |
| Suggestions while typing an address or place | Autocomplete | `/geocodage/completion/getcapabilities` |
| Point elevations or an elevation profile | Elevation API | `/altimetrie/resources` |
| A route between locations | Routing API | `/navigation/getcapabilities` |
| A reachable area by travel time or distance | Isochrone/isodistance API | `/navigation/getcapabilities` |
| Conformance of an archive to a supported data standard | Validation API (authenticated) | `/validation/swagger-ui/index.html` |

For searching published offerings or inspecting usage statistics, see the
[search and processing reference](references/search-and-processing.md). Dataset search
and CSW metadata discovery are distinct from looking up an address with the geocoder.

WMS-V still returns **images**, not an editable vector dataset. WFS returns features;
TMS returns zoom-dependent vector tiles, not a substitute for a complete analysis
dataset. WMTS uses advertised tile grids, not an arbitrary output extent/resolution.
For numeric elevations, choose the elevation API or a documented numeric raster
resource, not a coloured relief image.

## Workflow

1. Identify the deliverable: map, features, files, coordinates, calculation or validation
   report. Ask only for missing choices that change the service: display versus analysis,
   area, volume, output CRS/format, or whether authenticated access is available.
2. Use the table to recommend a service based on its output and relevant tradeoffs.
   For bulk data, compare ready-made downloads and custom extraction before proposing
   a nationwide WFS query. Do not promise access to every dataset through every service.
3. Read the relevant reference below and the current official guide. Discover layer names,
   fields, resources, formats, CRSs, coverage and limits from metadata, never from memory.
   Check dataset access conditions and licence separately from API availability.
4. Hand off execution to `geopf-wfs-download`, `geopf-wms-wmts` or `geopf-geocoding` when
   applicable and available. WMS-V and TMS details are in the delivery reference, not in
   the raster download skill. For services without a specialized skill, consult their
   official API schema rather than inventing parameters. Do not install missing skills.
5. Return the recommended service, expected output, discovery URL, any access/volume
   caveat, and the next skill or official guide. An overview alone needs no data request.

## Minimal discovery commands

Run only the discovery needed for the task. These requests do not export user data:

```bash
curl --fail --show-error --location --max-time 60 \
  --output wfs-capabilities.xml \
  'https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities'
```

```bash
curl --fail --show-error --location --max-time 60 \
  --output navigation-capabilities.json \
  'https://data.geopf.fr/navigation/getcapabilities'
```

```bash
curl --fail --show-error --location --max-time 60 \
  --output download-capabilities.xml \
  'https://data.geopf.fr/telechargement/capabilities?page=1&limit=10'
```

Choose unused output paths. Inspect the saved response; HTTP success alone is not
validation. Downloads must stay in the foreground with progress visible (`-progress`
where available); never pipe them through `head` or `tail`.

## Validate the output

- For advice, check that the proposed service produces the requested kind of output.
  Cite the official guide and distinguish documented capabilities from live-verified
  availability. If metadata is unreachable, report that limitation explicitly.
- For discovery, require a non-empty, parseable XML/JSON response of the expected type,
  not HTML, an OGC exception or an API error. Confirm the requested resource and its
  coverage, formats and CRSs; an empty list is not evidence of a successful selection.
- For a subsequent data request, follow the specialized skill's checks: non-empty output,
  expected CRS and axis order, plausible extent and feature/pixel count. For calculations,
  check units, coverage, plausible values and no-data markers. A sample or the first page
  must not be reported as a complete dataset.
- For asynchronous jobs, require successful completion and inspect the resulting file or
  report. A job identifier, HTTP 200 response or finished validation job does not by itself
  prove that the requested data is complete or conforms to the standard.

## References

- [Data delivery](references/data-delivery.md): WMS-R/V, WMTS, TMS, WFS, downloads and extraction.
- [Search, calculations and validation](references/search-and-processing.md): CSW, dataset
  search, geocoding, elevation, navigation, validation, usage statistics and access.
