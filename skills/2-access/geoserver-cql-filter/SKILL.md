---
name: geoserver-cql-filter
description: Writes and debugs GeoServer cql_filter parameters using ECQL for WFS GetFeature and WMS GetMap requests. Use for attribute, spatial or temporal filters, URL encoding, multiple WMS layers, and WKT/EWKT geometries supplied in CRS:84 longitude/latitude. Not for SQL queries or OGC API CQL2 filters.
---

# GeoServer CQL filters

Produce an ECQL expression and, when requested, a correctly encoded GeoServer request.
`cql_filter` is a GeoServer vendor parameter; do not assume every WFS/WMS implements it.
Use the service URL provided by the user, not a default public server.

## Prerequisites

Writing a filter needs only the layer schema and geometry CRS. Sending the examples
requires `curl` and an accessible GeoServer endpoint. Check with `curl --version`.
If missing, give the user `sudo apt install curl` (Debian/Ubuntu) or
`conda install -c conda-forge curl`; **never install software yourself**.
Do not run interactive logins; ask the user to complete authentication separately.

## Discover before querying

Read GetCapabilities for service versions, layer names, supported CRSs and output formats.
Read WFS DescribeFeatureType for attribute names/types and the geometry property; do not
assume `geom` or `the_geom`. If WFS is unavailable, obtain equivalent published metadata.
User-supplied metadata is enough for an offline filter-writing task.

```bash
# Replace with the supplied endpoint; use unused output paths.
WFS_URL='https://example.org/geoserver/wfs'
curl --fail --show-error --get "$WFS_URL" \
  --data-urlencode 'service=WFS' --data-urlencode 'version=2.0.0' \
  --data-urlencode 'request=GetCapabilities' --output capabilities.xml
```

```bash
TYPE_NAME='workspace:layer' # replace with a name found in capabilities
curl --fail --show-error --get "$WFS_URL" \
  --data-urlencode 'service=WFS' --data-urlencode 'version=2.0.0' \
  --data-urlencode 'request=DescribeFeatureType' \
  --data-urlencode "typeNames=$TYPE_NAME" --output schema.xsd
```

## Build and send a filter

Use the discovered names and types. Quote strings with single quotes, identifiers needing
escaping with double quotes, and group mixed `AND`/`OR` conditions explicitly. Double an
apostrophe inside a string (`'King''s Park'`). ECQL is a predicate, not a SQL `SELECT`.

For a supplied CRS:84 polygon on GeoServer's usual longitude-first configuration, retain
**longitude, latitude** order and use `INTERSECTS(geometry_property, SRID=4326;POLYGON((...)))`.
Do not write `SRID=84` or `SRID=CRS:84`. Read [spatial filters](references/spatial-filters.md)
for the configuration check before mixing CRSs.

After confirming these example fields and JSON output support, request a bounded sample:

```bash
CQL="name = 'King''s Park' AND population >= 1000"
curl --fail --show-error --get "$WFS_URL" \
  --data-urlencode 'service=WFS' --data-urlencode 'version=2.0.0' \
  --data-urlencode 'request=GetFeature' --data-urlencode "typeNames=$TYPE_NAME" \
  --data-urlencode 'outputFormat=application/json' --data-urlencode 'count=10' \
  --data-urlencode "cql_filter=$CQL" --output sample.geojson
```

Pass raw ECQL to `--data-urlencode`; never pre-encode it or concatenate it into a URL.
Keep downloads in the foreground with curl's progress visible; do not pipe through
`head` or `tail`. See [requests](references/requests.md) for WMS and count-only probes.

## Validate the output

- Inspect the response body as well as HTTP status: an OGC exception can arrive with
  HTTP 200. A saved XML error is not a GeoJSON result or map image.
- Check returned features satisfy the attribute and spatial predicates, and that their
  count and extent are plausible. Investigate zero matches when matches are expected;
  do not silently broaden the filter or claim an empty result proves correctness.
- Check the response CRS/axis order from the negotiated format and `srsName`, separately
  from the filter geometry CRS. Compare a known location to catch swapped axes.
- `count=10` is a sample. Compare hits/counts and paging before claiming a complete export.
  For WMS, inspect the image and, where available, check matching features with WFS.
- If only writing a filter, say it has not been executed against the target server.

## Report the result

Report the source and edition/access date when known, output path and format, CRS and
units, extent and counts (or raster dimensions), processing choices and checks performed.
Separate failed checks, warnings and checks not performed; keep unknown metadata explicit.
For advice-only requests, report the recommendation and its evidence without inventing files.

## References

- [ECQL syntax](references/ecql.md) — attributes, strings, nulls, dates and predicates.
- [Spatial filters and CRS:84](references/spatial-filters.md) — EWKT, axes and fallbacks.
- [WFS and WMS requests](references/requests.md) — encoding, layer order and diagnostics.
