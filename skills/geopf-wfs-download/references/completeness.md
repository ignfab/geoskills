# Check a complete WFS export

A nonempty file and a successful process are necessary but do not establish completeness.
Use this procedure for an export the user expects to be complete, after discovering the
layer, stable source identifier, CRS and filter. Keep a bounded area; hits queries can
also be expensive. Use the same service version, layer and filter for every request.

## Count before and after

For a GeoServer ECQL filter, set `WFS_URL`, `TYPE_NAME` and `CQL` from discovery. Preserve
the raw filter in the job report. Do not mix an ECQL hits query with an unrelated OGR
client-side filter. A spatial filter must use the same geometry, CRS and axis order.

```bash
curl --fail --show-error --get --max-time 60 "$WFS_URL" \
  --data-urlencode service=WFS --data-urlencode version=2.0.0 \
  --data-urlencode request=GetFeature --data-urlencode "typeNames=$TYPE_NAME" \
  --data-urlencode resultType=hits --data-urlencode "cql_filter=$CQL" \
  --output hits-before.xml
```

Export with GDAL paging, retain the stable source ID, and capture the exit status and
diagnostics. Do not use `-limit` or `-skipfailures` for a complete export. Then repeat the
same hits request to `hits-after.xml`. Where ECQL is unavailable, use a supported WFS
Filter Encoding/BBOX query consistently instead; do not silently discard a filter.

## Audit the GeoPackage

Run the bundled helper with the **source** identifier discovered in the schema, not the
GeoPackage's newly generated `fid`. Paths to scripts are relative to this skill directory.

```bash
python3 scripts/check_export.py extract.gpkg --layer features --id-field source_id \
  --hits-before hits-before.xml --hits-after hits-after.xml > completeness.json
```

Exit 0 means counts and unique, nonblank IDs are consistent. Exit 1 means unverified;
exit 2 means invalid inputs. `numberMatched="unknown"`, changing counts, duplicate IDs
and missing pages must remain visible in the report. Zero matching features can be a
valid empty query; explain it rather than calling it a nonempty deliverable.

Count equality cannot prove snapshot consistency: records can change while the count
stays constant. Record query times and the product edition, use stable ordering when the
service supports it, and disclose the absence of a snapshot guarantee. If source IDs
are not exposed, report that the uniqueness check is unavailable.

Check the intermediate selection **before** exact polygon clipping or other processing
that intentionally changes counts. After clipping, validate the final CRS, extent and
geometries separately.

## Interrupted jobs

Keep a failed export under a partial filename and retain its logs; do not deliver it as
complete. Retry a bounded request at most twice for transient 429/5xx errors, honouring
`Retry-After`. If the source offers no stable snapshot/order, restart into a new file
instead of appending blindly to the partial export. For bulk coverage, consider the
ready-made Download API packages. Never suppress a failed page to report success.
