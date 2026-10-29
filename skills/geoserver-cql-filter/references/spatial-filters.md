# Spatial filters, EWKT and CRS:84

## Keep three coordinate systems separate

Record the layer's declared CRS and geometry property from metadata, the input geometry's
CRS from its source, and the requested response CRS. A WFS `srsName` changes the output;
it does not label an unreferenced geometry embedded in `cql_filter`. Likewise, the WMS
map `CRS`/`SRS` does not assign a CRS to that ECQL geometry.

Plain WKT carries no CRS. Use it only after expressing its coordinates in the queried
layer's CRS. EWKT labels a literal as `SRID=<numeric EPSG code>;<WKT>`, so the server can
transform it for the comparison. Adding a label never transforms the supplied numbers.

## Input in CRS:84 (longitude, latitude)

GeoServer normally uses `org.geotools.referencing.forceXY=true`, which makes its internal
EPSG:4326 coordinates longitude-first. The ECQL parser
[decodes the SRID through that configuration](https://github.com/geotools/geotools/blob/bc1e66fa2d0a84d99ba2fb6e3b5a92b89284a153/modules/library/cql/src/main/java/org/geotools/filter/text/ecql/ECQLFilterBuilder.java#L298);
it does not independently force an axis order. The upstream
[referenced-geometry test](https://github.com/geotools/geotools/blob/bc1e66fa2d0a84d99ba2fb6e3b5a92b89284a153/modules/library/cql/src/test/java/org/geotools/filter/text/ecql/ECQLGeoOperationTest.java#L188)
asserts `CRS.decode("EPSG:4326", true)` for `SRID=4326;POINT(1 2)`.
Under this usual configuration, a CRS:84 input can keep its longitude/latitude coordinates
in an ECQL `SRID=4326` literal. Verify the deployment with a known location or its SRS
metadata; a non-default axis configuration needs an explicit conversion to the order it
expects. Do not change server settings to make a query work. This is not a general claim
that all EPSG:4326 protocols use longitude/latitude.

After confirming the geometry field is `shape`, a small illustrative Paris box becomes:

```text
INTERSECTS(shape, SRID=4326;POLYGON((2.34 48.84,2.36 48.84,2.36 48.86,2.34 48.86,2.34 48.84)))
```

Use the user's real geometry; the box is not a city boundary. Close each polygon ring,
preserve holes and multipart structure, and check validity before querying. Do not wrap
the EWKT in quotes: it is a geometry literal, not a string. `SRID=84` and `SRID=CRS:84`
are not substitutes for the numeric EPSG code.

For an envelope, ECQL also accepts a CRS string as its last BBOX argument:

```text
BBOX(shape, 2.34, 48.84, 2.36, 48.86, 'CRS:84')
```

The order is `minx, miny, maxx, maxy`; verify that the deployment accepts the CRS alias.
This is the ECQL BBOX predicate, not the separate WMS/WFS request `bbox` parameter.
For WMS 1.3.0 maps, `CRS=EPSG:4326` uses latitude/longitude in the request's map BBOX;
`CRS=CRS:84` uses longitude/latitude when advertised. Do not swap the EWKT coordinates
just because the map request uses WMS 1.3.0.

## Compatibility and distance

Test EWKT on the target deployment using a small sample and a feature known to intersect
the supplied geometry. Check an outside feature too. Compare with a known-good query in
the layer CRS; a valid parse or HTTP 200 alone does not prove correct reprojection.
An HTTP 500 with an empty body also leaves EWKT support unverified. Keep the failed
expression and CRS in the diagnostic; do not infer support from successful attribute
filters. An explicit-CRS BBOX can test envelope intersection, but cannot replace an
arbitrary polygon predicate without changing its meaning.

If the server rejects EWKT, report that limitation. Transform the geometry into the
layer's discovered CRS with an already available CRS-aware tool, then use plain WKT,
or use OGC XML Filter Encoding with an explicit geometry `srsName`. Follow that encoding's
axis rules. Do not remove the SRID while leaving coordinates in a different CRS, change
the server configuration, or install tools implicitly.

`DWITHIN(geom, geometry, distance, meters)` declares distance units, but execution and
geographic-distance handling depend on the datastore. Check a known-distance case before
promising a metric radius. A numeric buffer on longitude/latitude is not a metre buffer;
for a dependable local distance, construct a buffer in a suitable projected CRS with an
existing tool and filter against its explicitly referenced polygon.

## Sources

- [GeoServer ECQL geometry literals and spatial predicates](https://docs.geoserver.org/stable/en/user/filter/ecql_reference/).
- [GeoServer WFS reprojection](https://docs.geoserver.org/stable/en/user/services/wfs/vendor/#reprojection).
- [GeoServer WFS axis ordering](https://docs.geoserver.org/stable/en/user/services/wfs/axis_order/).
- [GeoServer WMS basics](https://docs.geoserver.org/stable/en/user/services/wms/basics/).
