# geoserver-cql-filter

**Family:** [2. Access and extract](../README.md).

Write and troubleshoot GeoServer `cql_filter` parameters for vector WFS/WMS layers,
including geometries supplied in CRS:84 longitude/latitude. From the layer metadata, the
skill produces an ECQL expression and, when requested, a correctly encoded WFS GetFeature
or WMS GetMap request for the endpoint the user supplies, not a default public server.

## When to use it

- Prepare an encoded WFS 2.0 request that combines string, code and numeric conditions,
  with apostrophes, `&` and `%` handled correctly.
- Select the features that intersect a CRS:84 polygon on a layer stored in another CRS,
  with an EWKT `SRID=4326` literal.
- Build a WMS GetMap filter list for several layers, kept in layer order.
- Diagnose a filter that returns an OGC exception with HTTP 200, for example an EWKT
  literal the server does not support.
- Write attribute, spatial or temporal predicates (nulls, dates, `LIKE`, `IN`, `BBOX`,
  `DWITHIN`) from a discovered schema.

## When to use another skill

- Downloading a complete Géoplateforme WFS layer to a file: this skill builds predicates
  and bounded sample requests, not a complete downloader; use
  [`geopf-wfs-download`](../geopf-wfs-download/README.md).
- SQL queries, such as PostGIS SQL on a local database: not covered by any skill of this
  repository.
- OGC API Features filters in CQL2 or CQL2-JSON: not covered by any skill of this
  repository; the skill does not treat CQL2 as ECQL.

## What you get

- An ECQL expression built from the discovered attribute names, types and geometry
  property, and, on request, a `curl` command that passes the raw ECQL through
  `--data-urlencode` (never pre-encoded or concatenated into a URL).
- When executed, a bounded sample (`count=10`) or a count-only `resultType=hits` probe;
  for WMS, a map image.
- Before reporting, the agent inspects the response body as well as the HTTP status (an
  OGC exception can arrive with HTTP 200), checks that returned features satisfy the
  attribute and spatial predicates with a plausible count and extent, and investigates
  zero matches instead of silently broadening the filter.
- It checks the response CRS and axis order separately from the filter geometry CRS and
  compares a known location to catch swapped axes. Returned features are selected, not
  clipped.
- A `count=10` response is reported as a sample: hits and paging are compared before
  claiming a complete export. A filter that was only written is reported as not executed
  against the target server.
- It does not write `SRID=84` or `SRID=CRS:84`, strip an SRID without transforming the
  coordinates, or change server settings to make a query work.

## Requirements

- Layer metadata: service/version, qualified layer name, attributes and types, geometry
  property and declared CRS. Offline examples can use metadata supplied by the user.
- An existing GeoServer endpoint and `curl` for requests; no server installation is needed
  to write a filter. Check with `curl --version`. Users can install curl with
  `sudo apt install curl` (Debian/Ubuntu) or `conda install -c conda-forge curl`. The agent
  must not install software or log in interactively; the user completes authentication
  separately.
- EWKT support depends on the deployed GeoServer/GeoTools version. Check a small request
  on that deployment; a compatible parser alone does not validate its datastore behavior.

## Installation

```bash
npx skills add ignfab/geoskills --skill geoserver-cql-filter
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`.

## Example

> Prepare, without sending it, a GeoServer WFS 2.0 request for the layer `test:sites` at
> https://example.org/geoserver/wfs. Its schema has `nom` and `code` as text and
> `population` as an integer, and JSON output is available. I want the names starting
> with L'Haÿ & Parc, a code equal to 01 or 02 and a population of at least 1000. Limit
> the response to ten features. Write the filter and the command to output/filtre.md.

With `WFS_URL` and `TYPE_NAME` set from discovery, SKILL.md requests a bounded sample in
this form:

```bash
CQL="name = 'King''s Park' AND population >= 1000"
curl --fail --show-error --get "$WFS_URL" \
  --data-urlencode 'service=WFS' --data-urlencode 'version=2.0.0' \
  --data-urlencode 'request=GetFeature' --data-urlencode "typeNames=$TYPE_NAME" \
  --data-urlencode 'outputFormat=application/json' --data-urlencode 'count=10' \
  --data-urlencode "cql_filter=$CQL" --output sample.geojson
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Discovery, minimal WFS commands and output validation. |
| [references/ecql.md](references/ecql.md) | Common attribute, temporal and spatial syntax. |
| [references/spatial-filters.md](references/spatial-filters.md) | EWKT, CRS:84 and axes. |
| [references/requests.md](references/requests.md) | URL encoding, WMS layers and diagnostics. |

## Tests

- Agent scenarios: [tests/geoserver-cql-filter.md](../../../tests/geoserver-cql-filter.md)
  (French prompts with synthetic metadata, 4 positive + 2 negative).
- Offline: [test_cql_requests.py](../../../tests/test_cql_requests.py) runs the documented
  `curl` examples against a local HTTP recorder; it does not validate ECQL parsing.
- Live (opt-in): [test_live_enrichment.py](../../../tests/test_live_enrichment.py) sends real
  ECQL attribute and BBOX predicates and a malformed filter to the Géoplateforme WFS.

## Related skills

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) chooses the Géoplateforme
  access route and hands GeoServer ECQL filters to this skill where they are supported.
- [`geopf-wfs-download`](../geopf-wfs-download/README.md) downloads a Géoplateforme WFS
  layer and checks export completeness, including `resultType=hits` counts with the same
  ECQL filter.
