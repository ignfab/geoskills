---
name: geopf-wfs-download
description: Downloads WFS data from the French Géoplateforme (data.geopf.fr) to various formats using ogr2ogr. Use when the user wants to download or export GPF/IGN WFS layers (BD TOPO, ADMIN EXPRESS, cadastre) to GeoJSON, GeoPackage, Shapefile, GeoParquet, GML or another vector format from https://data.geopf.fr/wfs/ows.
---

# Géoplateforme WFS download (ogr2ogr)

Download WFS layers from the French Géoplateforme (data.geopf.fr) and convert them to
vector formats using **ogr2ogr**.

To process the downloaded layers in Python (joins, buffers, overlays), see the
`geopandas-vector-analysis` skill. The WFS serves vector features only: for orthophotos and other map
images, use `geopf-raster-download`.

## MCP servers

Optional. The download and the conversion always use `ogr2ogr` (see the tooling rule). A
connected [Geocontext](https://github.com/ignfab/geocontext) MCP server (tools often
prefixed `mcp__geocontext__`) comes first for what surrounds them:

- **Find the layer and its fields:** `gpf_search_types` with French keywords, then
  `gpf_describe_type` for the property names, types and allowed values. They come from a
  schema catalogue bundled with the server, not from the service itself: confirm the layer
  and the fields you will use with `ogrinfo -so`, as in *Discover before querying*, before
  writing `-where` or `-select`. A layer that the search does not return can still be on
  the WFS: look for it in GetCapabilities before saying that it does not exist.
- **Identify a named municipality:** `geocode` then `adminexpress` give its INSEE code and
  a `feature_ref` usable as a spatial filter of the count. The first `geocode` candidate
  can be a namesake elsewhere or another object of the right municipality: check
  `fulltext` and `kind` as well as `city` and `zipcode`. When they do not match, add the
  postcode to the text, not the department name, or take another candidate. Check the unit
  returned by `adminexpress` against the request before using its code in `-where`.
- **Know the expected order of magnitude before downloading:** `gpf_count_features` with
  the same filter as the download, for example the same bounding box, and report it next
  to the exported count. A few objects of difference at the edge are normal, because
  `ogr2ogr -spat` tests the box again on the client (2,636 counted, 2,634 written for the
  Saint-Mandé box on 2026-11-13); a large gap needs the completeness checks of the
  references. An intersection with a municipality is not a bounding box.
- **Answer without a file** (a count, a few attributes): `gpf_count_features`, or
  `gpf_get_features`, which returns attributes without geometry, 100 objects by default
  and 5,000 at most. Check that `numberReturned` equals `numberMatched`.

Geocontext 0.9 names these tools `gpf_wfs_search_types`, `gpf_wfs_describe_type` and
`gpf_wfs_get_features`, counts with `result_type: "hits"` and names the filter parameters
differently: follow the tool list and the input schemas of the connected server.
Geometries, including the boundary of a named area, still come from `ogr2ogr`: do not
replace a requested file export with these tools, even with a layer tool that returns
geometries, since its output stops at 5,000 objects. Without Geocontext, or when a call
fails, discover with the commands below. Never install, configure or start an MCP server
yourself.

## Prerequisites

- Working **GDAL** CLI tools (`ogr2ogr` and `ogrinfo`) from the same environment, with
  WFS read support and an output driver that can create the requested vector format.
- `curl` for discovery/count requests; Python 3 for the optional GeoPackage completeness
  helper (standard library only). If missing, user-run commands are `sudo apt install curl`
  and, only for the helper, `sudo apt install python3`.
- Check capabilities before downloading. For GeoParquet, use the following commands;
  replace `Parquet` with the requested driver for other formats (e.g. `GPKG`, `GeoJSON`):

```bash
ogr2ogr --version
ogrinfo --format WFS
ogrinfo --format Parquet
```

The output driver must report vector support and `Create()` capability, not merely
appear in the driver list. A GDAL version number alone does not prove driver availability.

Install: `sudo apt install gdal-bin` (Ubuntu/Debian) or
`conda install -c conda-forge libgdal-core` for native CLI tools.
For a requested GeoParquet export with a missing driver, offer only the corresponding
plugin: `conda install -c conda-forge libgdal-arrow-parquet` in the compatible environment.
Reuse an existing capable GDAL before proposing a
[full container](references/formats.md#missing-gdal-or-parquet-support).

## Tooling rule

- Use `ogr2ogr` for downloads and conversions. Do not silently substitute Python
  (GeoPandas, Fiona, pyogrio, PyArrow), `uv`, or a different output format.
- If the tool cannot run, WFS support is missing, or the requested driver cannot write,
  stop the download/conversion and explain the missing capability. Offer a suitable GDAL
  installation or container and ask which option the user wants, unless they already
  chose one. Recheck capabilities in that environment before continuing.
- **Never install software yourself**, including packages pulled implicitly by `uv` or
  a container command. Provide installation/image-pull commands for the user to run;
  do not start an interactive installer or login.
- A Python fallback is a last resort when neither a suitable GDAL environment nor a GDAL
  container is usable: explain the tradeoff and obtain the user's agreement before using
  existing Python packages. An explicit user request for Python takes precedence.

## WFS endpoint

- **Géoplateforme WFS**: `https://data.geopf.fr/wfs/ows` (WFS 2.0).
- GetCapabilities: `https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities`
- Layer names include a namespace prefix, e.g. `BDTOPO_V3:batiment`, `ADMINEXPRESS-COG.LATEST:region`.
- Discover layers with Geocontext when it is connected (see [MCP servers](#mcp-servers)),
  or from GetCapabilities as shown below.

## Discover before querying

Do not guess layer or field names: they change between editions (`ADMINEXPRESS-COG.2025`
became `ADMINEXPRESS-COG.LATEST`), and a wrong field name in `-where` fails or returns
nothing. Read them from the service first:

```bash
# Layer names matching a theme (a few seconds; listing every layer with ogrinfo takes minutes)
curl -fsS "https://data.geopf.fr/wfs/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities" \
  | grep -o "<Name>[^<]*ADMINEXPRESS-COG.LATEST[^<]*</Name>"
# Fields, geometry type and CRS of one layer
ogrinfo -so -nocount -noextent "WFS:https://data.geopf.fr/wfs/ows" "ADMINEXPRESS-COG.LATEST:commune"
```

For a named area (commune, department), take its boundary from ADMIN EXPRESS instead of
typing a bounding box from memory: see *Selecting features inside a named area* in
[references/ogr2ogr-options.md](references/ogr2ogr-options.md).

## Basic syntax

```bash
ogr2ogr -f <FORMAT> <output_file> "WFS:https://data.geopf.fr/wfs/ows" <typename>
```

Download a small Toulouse extract to GeoPackage, the recommended default format:

```bash
ogr2ogr -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 -f GPKG batiments.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

**Bound nationwide layers** such as `BDTOPO_V3:batiment` to the requested area. A full
download is several gigabytes. Add `-limit` only for a sample; it can truncate an extract
and must not be presented as a complete dataset:

```bash
ogr2ogr -f GeoJSON -lco RFC7946=YES -limit 5000 \
  -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  batiments_extract.geojson \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Validate the output

Before reporting a download as complete:

- Reopen the output with the same capable GDAL environment/container used to create it;
  the host's `ogrinfo` may lack the driver even when the container has it.
- Run `ogrinfo -so <output> <layer>`: the feature count must be non-zero, the CRS the one
  expected, and the extent must cover the requested area.
- Compare with an order of magnitude you know. For polygons, compute the total area in
  a suitable projected CRS with verified linear units, converting area to the reported
  units. Lambert-93 is a fallback for suitable metropolitan-France data only (see
  *Selecting features inside a named area* in the options reference).
- Say explicitly when the result is a sample (`-limit`) or when pages failed.
- Run long downloads in the foreground, with `-progress`. Do not pipe `ogr2ogr` through
  `head` or `tail`, which hides progress and can cut the output.

## Report the result

Report the source and edition/access date when known, output path and format, CRS and
units, extent and counts (or raster dimensions), processing choices and checks performed.
Separate failed checks, warnings and checks not performed; keep unknown metadata explicit.
For advice-only requests, report the recommendation and its evidence without inventing files.

## References

- [references/completeness.md](references/completeness.md) — verify export counts and
  source IDs; handle incomplete or interrupted jobs.
- [references/formats.md](references/formats.md) — output formats, `-f` driver names and
  examples, including missing-driver options and one-file-per-layer GeoParquet exports.
- [references/ogr2ogr-options.md](references/ogr2ogr-options.md) — filtering, reprojection,
  field selection, performance and troubleshooting.

## Additional resources

- GDAL WFS driver: <https://gdal.org/drivers/vector/wfs.html>
- ogr2ogr: <https://gdal.org/programs/ogr2ogr.html>
- Géoplateforme diffusion: <https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/>
