# geoserver-cql-filter

Write and troubleshoot GeoServer `cql_filter` parameters for vector WFS/WMS layers,
including geometries supplied in CRS:84 longitude/latitude.

## Requirements

- Layer metadata: service/version, qualified layer name, attributes and types, geometry
  property and declared CRS. Offline examples can use metadata supplied by the user.
- An existing GeoServer endpoint and `curl` for requests; no server installation is needed
  to write a filter. Users can install curl with `sudo apt install curl` (Debian/Ubuntu)
  or `conda install -c conda-forge curl`. The agent must not install software or log in
  interactively.
- EWKT support depends on the deployed GeoServer/GeoTools version. Check a small request
  on that deployment; a compatible parser alone does not validate its datastore behavior.

## Installation

```bash
npx skills add ignfab/geoskills --skill geoserver-cql-filter
```

## Contents

- [SKILL.md](SKILL.md): discovery, minimal WFS commands and output validation.
- [references/ecql.md](references/ecql.md): common attribute, temporal and spatial syntax.
- [references/spatial-filters.md](references/spatial-filters.md): EWKT, CRS:84 and axes.
- [references/requests.md](references/requests.md): URL encoding, WMS layers and diagnostics.
- [Manual scenarios](../../tests/geoserver-cql-filter.md): French prompts and expected decisions.
- [Request tests](../../tests/test_cql_requests.py): curl examples exercised on a local HTTP recorder.

This skill builds predicates for GeoServer. It does not administer a server, implement a
complete downloader, translate PostGIS SQL, or treat OGC API CQL2 as ECQL.
