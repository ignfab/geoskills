# Output reports

Use the same vocabulary across skills while scaling detail to the task. Keep the compact
report instructions in each skill itself: single-skill installations do not include this
repository's `docs/` directory. This is a contributor convention, not a runtime dependency.
For users, it also says what a complete report from an agent should contain.

| Field | What to record |
| --- | --- |
| Source | Input path or public service, dataset/layer/resource, edition and access date when known |
| Output | Actual file path, format, CRS and units, extent, feature/row count or raster dimensions |
| Processing | Selection, transformations, key parameters and tool versions relevant to reproducibility |
| Validation | Checks performed and observed values; distinguish passed, failed and not performed |
| Issues | Errors preventing use, warnings requiring review, missing metadata and unresolved choices |

Use `consistent` for a count/ID comparison; it is not a claim of transactional completeness.
Use `accepted` for a geocoding policy; it is not proof that an address is correct.
Do not invent a date, CRS, licence or expected count to fill the report. State `unknown`
when metadata does not establish it. Do not expose credentials in service URLs or logs.
An advice-only task needs the recommended service and its rationale, not a fabricated
file report. A small operation can be reported in a few sentences; use JSON/CSV when the
user needs a reusable manifest or the workflow already produces one.

## Report shape

A compact report for a file output follows the five fields. The angle brackets mark
values that come from the actual run:

```text
Source      Géoplateforme WFS, layer <layer name from the capabilities>, accessed <date>
Output      <path>.gpkg, GeoPackage, EPSG:2154 (metres), <n> features, extent <xmin ymin xmax ymax>
Processing  ogr2ogr, bounding box given in EPSG:4326, reprojected to EPSG:2154, GDAL <version>
Validation  passed: non-zero count, expected CRS, extent covers the request
            not performed: comparison with a published total
Issues      none
```

When a check could not run, say so under Validation rather than leaving it out; when a
result is a sample or a first page, say so under Issues.

## Evidence by output type

Keep the shared fields above, then add the checks that make the specific output usable.
The linked skill guides define the full workflows and supported formats.

### Discover and select

| Output | Additional evidence |
| --- | --- |
| [Service advice](../skills/1-discover/geopf-service-selection/README.md) | The recommended service produces the requested kind of output; the official guide is cited; documented capabilities are kept apart from availability verified live. A discovery response is non-empty, parseable and of the expected type, not HTML or an OGC exception. |
| [BD TOPO schema advice](../skills/1-discover/bdtopo-schema-guide/README.md) | Model version, document revision, class/field, format, official source and pages. State the limits of the bundled subset and any unverified mapping. |

### Access and extract

| Output | Additional evidence |
| --- | --- |
| [Downloaded archive or tiles](../skills/2-access/geopf-file-download/README.md) | Byte length and any published checksum, archive integrity test, expected layers or tiles, CRS, extent and plausible count or resolution. A missing checksum means authenticity was not checked that way; nothing is extracted over existing data. |
| [WFS vector extract](../skills/2-access/geopf-wfs-download/README.md) | Output reopened with the GDAL environment that wrote it: non-zero feature count, expected CRS, extent covering the requested area, order of magnitude compared with a known value. State a sample (`-limit`) or failed pages. |
| [Raster extract](../skills/2-access/geopf-raster-download/README.md) | Exit code, requested CRS, pixel size and dimensions, statistics that are not all zero or nodata. Report transient HTTP errors, retries and an incomplete download. For elevation, plausible values (about −10 to 4,810 m in mainland France) and `-99999` kept as nodata. |
| [Filtered GeoServer request](../skills/2-access/geoserver-cql-filter/README.md) | Response body checked as well as the HTTP status (an OGC exception can arrive with HTTP 200), returned features satisfying the predicates, response CRS and axis order, sample versus complete count. A filter that was only written is reported as not executed. |
| [API Carto result](../skills/2-access/apicarto-query/README.md) | A `FeatureCollection`, not an error body; feature count equal to `numberMatched`; unique identifiers; extent in the expected territory. For zoning, the planning document and its approval date with each zone. |
| [Geocoding result](../skills/2-access/geopf-geocoding/README.md) | Input and output record counts and identifiers, counts by status (`ok`, `not-found`, `skipped`, `error`), postcode or INSEE code agreement when the input has one, accented names intact. Unmatched rows are kept and counted. |

### Prepare and check

| Output | Additional evidence |
| --- | --- |
| [Delivery inventory](../skills/3-prepare/geodata-intake/README.md) | Every supplied file reconciled, including unreadable or empty ones; layer names, schema, CRS or `unknown`, extent, count or dimensions and file size; source files unchanged. An inventory is not a geometry audit. |
| [CRS transformation](../skills/3-prepare/crs-reprojection-france/README.md) | A control point with known coordinates transformed and compared, output extent within the usual range of the target CRS, units stated. No area or distance computed in degrees or in EPSG:3857. |
| [Vector conversion](../skills/3-prepare/gdal-vector-processing/README.md) | Feature count equal to the source or to the count expected after the filter or clip, layers still present, geometry type, CRS and extent, field names and types (codes kept as strings with leading zeros, no unreported truncation), conversion warnings read, accented text intact. |
| [Raster processing](../skills/3-prepare/gdal-raster-processing/README.md) | Requested CRS, pixel size and extent, nodata value or mask, valid-data coverage and plausible minimum and maximum. For a COG, the layout check and, when available, the structural validator. |
| [Quality audit and repair](../skills/3-prepare/vector-data-quality/README.md) | Repaired data written to a new file, reopened and audited again; repaired plus quarantined features equal to the source count; geometry-type changes, bounds and areas before and after, measured in a projected CRS. |

### Analyze and derive

| Output | Additional evidence |
| --- | --- |
| [Spatial join or overlay](../skills/4-analyze/geopandas-vector-analysis/README.md) | Non-zero count, CRS, bounds, geometry types and required fields of the reopened output; unmatched features and multiple matches per source feature; areas and distances in a suitable projected CRS. For zonal statistics, valid pixel counts. |
| [Elevations](../skills/4-analyze/geopf-altimetry/README.md) | One returned point per submitted point, coordinates compared before values are joined by position, the requested sample count for a profile, `-99999` kept as missing, plausible magnitudes and source accuracy metadata when supplied. |
| [Route or reachable area](../skills/4-analyze/geopf-routing/README.md) | Resource, profile, units and direction; a line with plausible distance and duration and endpoints near the requested locations (snapping reported), or a valid polygon for the requested cost; CRS inspected before export. |
| [Descriptive statistics](../skills/4-analyze/geospatial-descriptive-statistics/README.md) | Selected fields and units, row/valid/missing counts, invalid or infinite values, standard-deviation and quantile conventions. Preserve valid zeroes; identify source-specific sentinels explicitly. |
| [Territorial indicators](../skills/4-analyze/spatial-aggregation/README.md) | Stable zone IDs, spatial predicate, multiple-match policy, unmatched objects, empty zones and reconciliation of counts. Explain denominator and null rules for ratios. |

### Represent and publish

| Output | Additional evidence |
| --- | --- |
| [Simplified boundaries](../skills/5-publish/mapshaper-simplify/README.md) | Feature count, identifiers and properties unchanged, valid polygons, multipart and hole losses, output CRS, per-unit area compared in a projected CRS, measured vertex and size reduction, shared borders still coinciding. |
| [Map illustration](../skills/5-publish/map-illustration/README.md) | The delivered PNG, SVG, PDF or HTML reopened and inspected at its intended size: non-empty content, dimensions, extent and expected features, display CRS, no clipped title or legend, nodata not painted as a value. For HTML, zoom, pan, layer visibility and a tooltip tested in a browser, external resources listed, offline use claimed only after a test without network. Renderer version, source date, fields and units, simplification or downsampling and actual file size. |
| [QGIS vector style](../skills/5-publish/qgis-layer-styling/README.md) | QML path, source layer, renderer, fields, symbol units, categories or class breaks, null/fallback handling and successful reload into a fresh layer. |
| [QGIS project](../skills/5-publish/qgis-project-builder/README.md) | Project path, source inventory, project CRS/extent, order/groups/visibility, relative-path scope and reopening result. Record relocation checks and remote-layer availability separately. |

### Solve a business need

| Output | Additional evidence |
| --- | --- |
| [Municipal building portrait](../skills/6-workflows/municipality-building-profile/README.md) | Declared projected analysis CRS and linear units, with areas converted to m²; selected, touch-only and outside objects reconciled with the input count; union area not above the summed clipped areas or the municipality area; coverage between 0 and 100 %; completeness status, field semantics, cross-boundary identifiers and input hashes. A partial extract stays partial after successful file validation. |
| [Terrain screening](../skills/6-workflows/terrain-elevation-screening/README.md) | Projected CRS, identical raster grids, AOI extent, metre elevations, slope convention (degrees or percent) and mask values (`1` selected, `0` rejected, `255` unknown or outside); selected, rejected and unknown cells reconciled with the AOI cell count; polygons inside the AOI with holes kept; source, edition, vertical reference, thresholds and coverage. An empty selection with coverage is valid; an all-nodata AOI is insufficient data. Never a statement that a site is safe or suitable for landing. |

A saved QGZ does not embed its source data. Relative paths alone do not establish that a
project can be moved; the declared bundle and relocation check determine that claim.
A valid remote-layer provider does not prove that tiles were rendered. Report whether
rendering was checked, failed or not performed.

Return to the [documentation guide](README.md).
