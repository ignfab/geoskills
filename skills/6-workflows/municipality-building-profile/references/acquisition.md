# Discover and retrieve the inputs

## Local inputs first

Inspect supplied files with `geopandas.list_layers(path)` or `ogrinfo -so`. Discover the
boundary ID and building ID, source CRS, available fields and geometry types. Select one
municipality by an exact string ID, not a fuzzy name. Keep leading zeros. Require unique
IDs and a single Polygon/MultiPolygon municipality feature; multipart geometry is allowed.
If a municipality is split across records, prepare a documented dissolved copy first.

Inputs must contain **whole building geometries**. Clipping upstream would hide which
buildings cross the boundary. A local subset is supported, but completeness is `unknown`
unless there is evidence that it covers the entire municipality. An unverified empty
file is not proof of an empty building stock. Keep source data and sidecars untouched.

## When online extraction is needed

Use `geopf-services` and `geopf-wfs-download` if available. The fallback discovery entry is:

```bash
curl --fail --show-error --location --max-time 60 --get https://data.geopf.fr/wfs/ows --data-urlencode SERVICE=WFS --data-urlencode VERSION=2.0.0 --data-urlencode REQUEST=GetCapabilities --output capabilities.xml
```

From that response select the advertised municipality and building types; inspect each
with `ogrinfo -so -nocount -noextent 'WFS:https://data.geopf.fr/wfs/ows' '<discovered-type>'`
and, if needed, DescribeFeatureType. Do not assume example BD TOPO/ADMIN EXPRESS layer
names or SQL field names remain current. Retrieve the selected municipality first using
its discovered ID field and properly quoted string identifier.

Derive its bounding box from the actual boundary and request the buildings with
`ogr2ogr -progress -spat xmin ymin xmax ymax -spat_srs <boundary-CRS> ...` using discovered
types and supported output drivers. Keep the full polygons: **no `-clipsrc`**, `-clipdst`
or geometry intersection in the download. The profile helper performs the exact clip.
Never download a national building layer for a single municipality.

Verify service count and unique exported IDs for the **same spatial/attribute filter**;
use WFS `resultType=hits` and the completeness guidance in `geopf-wfs-download` when
available. An exported bounding-box extract can contain objects later excluded by the
exact municipal boundary. Do not compare those different populations as though they
should have equal counts. Unstable counts, failed pages or `-limit` imply a partial or
unknown inventory. Record the evidence instead of labelling a successful command complete.

Use dated deliveries (`geopf-download-files`) when an exact historical edition is needed;
do not relabel current WFS data as a historical edition. Record differing boundary and
building dates and their interpretation limits. Run transfers in the foreground with
visible progress; stop on persistent errors instead of silently switching source or scope.
