# Transfers and integrity

Keep the resource/folder/file URL, edition, territory, format, CRS, published size/hash,
download timestamp and final HTTP response headers with each selected file. Headers may
contain several redirect responses: use the final response's values. Link relations and
MIME types distinguish catalogue feeds from downloadable files; inspect them before use.

## Resume an interrupted transfer

Resume only against the original immutable edition URL, or with the original **strong**
ETag (not one beginning `W/`). Keep the partial file and its original headers together.
Set `ETAG` to the complete original quoted ETag and `FILE_URL` to the original URL:

```bash
curl --fail --show-error --location --connect-timeout 20 --max-time 3600 \
  --continue-at - --header "If-Range: $ETAG" --dump-header resume.headers \
  --output package.zip.part "$FILE_URL"
```

Require a successful resumed range response and validate the resulting whole file. If
the resource changed, the server ignores ranges or the validator is unavailable, restart
to a **new** partial file; do not concatenate responses or suppress curl's range error.
A 416 response does not prove completion: check advertised length and archive integrity.
Keep total retries bounded (two retries), with backoff and `Retry-After` for 429/5xx.

## Check and extract

Compare the final byte count with the whole object's advertised length, not the resumed
response's remaining length. Check a published checksum using its advertised algorithm.
Test ZIPs with `unzip -t`, 7z with `7zz t`, or the existing reader appropriate to the format.
For a direct GeoTIFF/GeoPackage, inspect it with GDAL instead of treating it as an archive.

List archive members and uncompressed sizes before extracting. Reject absolute paths,
parent traversal and links escaping the new destination directory. Preserve Shapefile
sidecars. Never execute downloaded scripts. Check disk space for the expanded delivery.

Only after transfer and content checks succeed, rename the partial file to an unused
final name. For a multi-file delivery, record every expected and obtained file; a valid
single archive cannot establish that all advertised tiles were downloaded.
