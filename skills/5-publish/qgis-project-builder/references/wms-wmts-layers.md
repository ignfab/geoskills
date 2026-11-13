# Optional public basemaps

Discover advertised names from capabilities; a historical Plan IGN identifier is not
proof of present availability. Use `geopf-raster-download` if installed, or inspect the public
service metadata directly. Never add passwords, tokens, API keys or QGIS authcfg references
to a deliverable intended to be public. Interactive authentication is outside this skill.

## WMTS helper interface

Add `wmts` entries to the manifest after discovery:

```json
{"wmts":[{"name":"Public basemap","url":"https://data.geopf.fr/wmts","layer":"<advertised identifier>","style":"<advertised style>","format":"image/png","tile_matrix_set":"<linked matrix set>","crs":"<advertised matrix CRS>"}]}
```

The helper accepts public HTTPS endpoints without userinfo, query strings or fragments.
It fetches capabilities with a 15-second timeout and an 8 MiB limit, checks the WMTS XML
root, layer, style, format, linked matrix set, matrix definitions and CRS, then creates a
QGIS raster layer with the `wms` provider. Its `url` parameter contains the **full WMTS
GetCapabilities URL**, encoded by `QgsDataSourceUri`; a bare endpoint can be interpreted
as WMS by QGIS. Do not apply generic `urlencode` to the entire provider URI: encoding the
CRS/format scalars can leave an invalid provider CRS or double-encode tile parameters. It places basemaps below local layers. A metadata
or provider failure omits the optional basemap and reports a generic warning without
printing URLs or provider errors that might contain credentials.

Inspect the report: omission is **local-only success**, not successful basemap delivery.
A provider can be valid while later tile requests fail. Verify a small rendered extent
when the network is available, or explicitly report tile rendering unverified. Cached
metadata or a schema-valid test fixture does not establish live service availability.

## WMS alternative

The helper implements WMTS; an existing PyQGIS environment can also add public WMS:
inspect GetCapabilities and inherited CRS/style declarations, select the advertised layer,
format and CRS, and build a URL-encoded provider URI with `url`, `layers`, `styles`,
`format` and `crs` (no `tileMatrixSet`). Construct `QgsRasterLayer(uri, name, 'wms')` and
check validity. Use the same project placement, save/reopen and remote rendering checks.
The [QGIS layer-loading guide](https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/loadlayer.html)
describes the provider. Keep WMS image requests distinct from WMTS tile-matrix selection.
Do not claim the helper supports WMS manifests or silently treat WMS as WMTS.

Offline CI tests local projects and optional remote failure without network. A live Plan
IGN integration is separate: report the date, discovered parameters and tile/provider
results, including unavailable services, without making ordinary tests depend on them.
