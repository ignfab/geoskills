# geopf-wfs-download

**Family:** [2. Access and extract](../README.md).

Download WFS layers from the French
[Géoplateforme](https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/)
(`data.geopf.fr`) and convert them to GeoPackage, GeoJSON, GeoParquet, Shapefile or GML
using `ogr2ogr`. Layer and field names come from the service capabilities, extracts are
bounded to the requested area, and an optional helper audits a GeoPackage export against
WFS counts and source IDs.

## When to use it

- Download every BD TOPO building intersecting a bounding box to a GeoPackage.
- Get a small, labeled sample of features as RFC 7946 GeoJSON, without downloading the
  national layer.
- Add an ADMIN EXPRESS layer to an existing GeoPackage under a new layer name.
- Select features inside a named municipality or department, using its ADMIN EXPRESS
  boundary rather than a bounding box typed from memory.
- Export layers to GeoParquet (one file per layer), or plan the GDAL environment when
  `ogr2ogr` or the output driver is missing, without installing anything.
- Decide whether an export is complete from WFS counts and source IDs.

## When to use another skill

- Orthophotos, Plan IGN and other map images (the WFS serves vector features only):
  [`geopf-raster-download`](../geopf-raster-download/README.md).
- Bulk coverage as ready-made Download API packages:
  [`geopf-file-download`](../geopf-file-download/README.md).

## What you get

- A vector file in the requested format: GeoPackage (the recommended default), GeoJSON
  (RFC 7946 with `-lco RFC7946=YES`), GeoParquet (one file per layer), Shapefile (a
  directory) or GML. Extra layers can be added to an existing GeoPackage with
  `-update -nln`.
- Features selected with `-spat` keep their whole geometry; they are clipped at a
  boundary only when clipping is requested.
- Optionally, a JSON completeness report from `check_export.py`: status `consistent` or
  `unverified`, with issues such as missing or duplicate source IDs, a changed or unknown
  expected count, or a count mismatch. Equal counts alone do not prove completeness.
- Before reporting, the agent reopens the output with the same GDAL environment that
  created it and runs `ogrinfo -so`: the feature count must be non-zero, the CRS the
  expected one and the extent must cover the requested area. It compares the result with
  a known order of magnitude (for polygons, the total area in Lambert-93).
- It says explicitly when the result is a sample (`-limit`) or when pages failed, keeps a
  failed export under a partial filename with its logs, and never suppresses a failed
  page to report success. It does not silently switch to Python, `uv` or another output
  format when a capability is missing.

## Requirements

- GDAL CLI tools (`ogr2ogr`, `ogrinfo`) from one environment, with WFS read support **and a
  driver that can create the requested output format**. Check `ogr2ogr --version`,
  `ogrinfo --format WFS` and `ogrinfo --format <output-driver>` before downloading: the
  driver must report vector support and `Create()` capability.
- `curl` for discovery/count requests; Python 3 (standard library only) for the optional
  completeness helper, which audits an export while downloads still use `ogr2ogr`.
- User-run installs: `sudo apt install gdal-bin` or `conda install -c conda-forge gdal`,
  and `sudo apt install curl python3`. GeoParquet may need
  `conda install -c conda-forge gdal libgdal-arrow-parquet`; distribution builds do not
  necessarily include it. An official GDAL `ubuntu-full` container is another option; see
  [missing-driver options](references/formats.md#missing-gdal-or-parquet-support).
- The agent never installs software itself (including packages pulled by `uv` or a
  container image) and asks for an environment choice when a capability is missing.
- Network: the Géoplateforme WFS 2.0 endpoint `https://data.geopf.fr/wfs/ows`; the documented
  requests carry no API key.

## Installation

```bash
npx skills add ignfab/geoskills --skill geopf-wfs-download
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/2-access`.

## Example

> Download all BD TOPO buildings intersecting the box 1.443, 43.603, 1.446, 43.606
> (WGS84 longitude/latitude) to output/batiments.gpkg.

The same command shape on a wider box in central Toulouse:

```bash
ogr2ogr -f GPKG -spat 1.43 43.59 1.45 43.61 -spat_srs EPSG:4326 \
  batiments_toulouse.gpkg \
  "WFS:https://data.geopf.fr/wfs/ows" \
  "BDTOPO_V3:batiment"
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Tool/driver checks, tooling rule, endpoint, download recipes and validation. |
| [references/formats.md](references/formats.md) | Output formats, missing-driver options and GeoParquet layer limits. |
| [references/ogr2ogr-options.md](references/ogr2ogr-options.md) | Filtering, reprojection, performance, troubleshooting. |
| [references/completeness.md](references/completeness.md) | Compare WFS counts before/after export, check source IDs and handle interrupted jobs. |
| [scripts/check_export.py](scripts/check_export.py) | Audit GeoPackage counts and source IDs against saved WFS hits responses. |

## Tests

- Agent scenarios: [tests/geopf-wfs-download.md](../../../tests/geopf-wfs-download.md)
  (French prompts, 7 positive + 1 negative).
- Offline: [test_enrichment.py](../../../tests/test_enrichment.py) (export completeness).
- Live (opt-in): [test_live.py](../../../tests/test_live.py) and
  [test_live_enrichment.py](../../../tests/test_live_enrichment.py) (paging).

## Related skills

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) chooses the access route
  before a download.
- [`bdtopo-schema-guide`](../../1-discover/bdtopo-schema-guide/README.md) explains BD TOPO
  classes and fields before extraction; layer names still come from live metadata.
- [`geoserver-cql-filter`](../geoserver-cql-filter/README.md) writes GeoServer ECQL filters
  for WFS requests.
- [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md) chooses
  the target CRS (CC zones, overseas territories).
- [`gdal-vector-processing`](../../3-prepare/gdal-vector-processing/README.md) filters, clips and
  queries the downloaded files locally.
- [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md) processes the downloaded
  layers in Python (joins, buffers, overlays). It replaces `ogr2ogr` only as a last resort
  the user agrees to, when no suitable GDAL installation or container is usable.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  uses this skill to acquire data for a full municipal building portrait.
