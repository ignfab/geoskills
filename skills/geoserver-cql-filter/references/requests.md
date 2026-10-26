# WFS and WMS requests

## Encoding

Keep the raw ECQL separate from the URL. `curl --get --data-urlencode "cql_filter=$CQL"`
encodes spaces, apostrophes, `%`, `+`, `&` and EWKT semicolons as parameter data. Do not
encode it first: `%27` would become `%2527`. In an application, use its URL-parameter
builder with the raw value. Shell quoting and ECQL string escaping solve different problems.

All URLs, layer names, fields and extents below are illustrative. Replace them with
user-provided endpoints and discovered metadata; use unused output paths.

## WFS count-only probe

Use the same `WFS_URL`, `TYPE_NAME` and raw `CQL` as the sample in [SKILL.md](../SKILL.md).

```bash
curl --fail --show-error --get "$WFS_URL" \
  --data-urlencode 'service=WFS' --data-urlencode 'version=2.0.0' \
  --data-urlencode 'request=GetFeature' --data-urlencode "typeNames=$TYPE_NAME" \
  --data-urlencode 'resultType=hits' --data-urlencode "cql_filter=$CQL" \
  --output hits.xml
```

Inspect `numberMatched` in the WFS 2.0 response; `unknown` is not zero. A count does not
prove geometric correctness and a large-area hits query may still be expensive. Start
with a small known area. WFS 1.x uses `typeName` and `maxFeatures` instead of the 2.0
`typeNames` and `count`; select a version advertised by the service.
For a large geometry that exceeds URL limits, use an appropriate POST XML Filter
Encoding request. Do not assume arbitrary form POSTs accept the same vendor parameters.

## WMS layers and filters

GetMap returns an image. Supply one filter per requested layer, in the same order,
separated by semicolons; use `INCLUDE` for a layer that should remain unfiltered.
The semicolon inside an EWKT literal belongs to that literal. Do not split filter lists
with a naive string split; let the ECQL parser handle the complete parameter value (see
the [upstream filter-list test](https://github.com/geotools/geotools/blob/bc1e66fa2d0a84d99ba2fb6e3b5a92b89284a153/modules/library/cql/src/test/java/org/geotools/filter/text/ecql/ECQLTest.java#L361)).

The example assumes capabilities advertise WMS 1.3.0, both layers and `CRS:84`, and that
the first layer's geometry property is `shape`, and the server's EWKT interpretation is
longitude-first as described in [spatial filters](spatial-filters.md):

```bash
WMS_URL='https://example.org/geoserver/wms'
LAYERS='workspace:sites,workspace:roads'
CQL='INTERSECTS(shape, SRID=4326;POLYGON((2.34 48.84,2.36 48.84,2.36 48.86,2.34 48.86,2.34 48.84)));INCLUDE'
curl --fail --show-error --get "$WMS_URL" \
  --data-urlencode 'service=WMS' --data-urlencode 'version=1.3.0' \
  --data-urlencode 'request=GetMap' --data-urlencode "layers=$LAYERS" \
  --data-urlencode 'styles=,' --data-urlencode 'crs=CRS:84' \
  --data-urlencode 'bbox=2.34,48.84,2.36,48.86' \
  --data-urlencode 'width=256' --data-urlencode 'height=256' \
  --data-urlencode 'format=image/png' --data-urlencode "cql_filter=$CQL" \
  --output map.png
```

Keep the map BBOX axis order separate from ECQL geometry order. A blank map can result
from styling, scale, extent or permissions as well as zero matches. For layer groups,
first inspect their composition instead of assuming a filter maps to every child layer.

## Diagnostics

| Symptom | Check |
| --- | --- |
| Parse error | Raw ECQL, quoting, balanced parentheses and deployed parser support |
| Unknown property | DescribeFeatureType, case and the actual geometry field |
| Valid response, wrong area | Input geometry CRS, EWKT SRID, axes and layer declaration |
| Missing features | Predicate semantics, null values, access restrictions and paging |
| Filter appears ignored | GeoServer vendor support, parameter encoding, WMS layer order |
| HTTP 200 with unusable file | OGC `ExceptionReport`/`ServiceExceptionReport` in the body |

## Sources

- [GeoServer WFS reference](https://docs.geoserver.org/stable/en/user/services/wfs/reference/).
- [GeoServer WFS vendor parameters](https://docs.geoserver.org/stable/en/user/services/wfs/vendor/).
- [GeoServer WMS vendor parameters](https://docs.geoserver.org/stable/en/user/services/wms/vendor/#cql_filter).
