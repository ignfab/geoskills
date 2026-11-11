# Output reports

Use the same vocabulary across skills while scaling detail to the task. Keep the compact
report instructions in each skill itself: single-skill installations do not include this
repository's `docs/` directory. This is a contributor convention, not a runtime dependency.

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

## Evidence by output type

Keep the shared fields above, then add the checks that make the specific output usable.
The linked skill guides define the full workflows and supported formats.

| Output | Additional evidence |
| --- | --- |
| [Descriptive statistics](../skills/4-analyze/geospatial-descriptive-statistics/README.md) | Selected fields and units, row/valid/missing counts, invalid or infinite values, standard-deviation and quantile conventions. Preserve valid zeroes; identify source-specific sentinels explicitly. |
| [Territorial indicators](../skills/4-analyze/spatial-aggregation/README.md) | Stable zone IDs, spatial predicate, multiple-match policy, unmatched objects, empty zones and reconciliation of counts. Explain denominator and null rules for ratios. |
| [QGIS vector style](../skills/5-publish/qgis-layer-styling/README.md) | QML path, source layer, renderer, fields, symbol units, categories or class breaks, null/fallback handling and successful reload into a fresh layer. |
| [QGIS project](../skills/5-publish/qgis-project-builder/README.md) | Project path, source inventory, project CRS/extent, order/groups/visibility, relative-path scope and reopening result. Record relocation checks and remote-layer availability separately. |
| [BD TOPO schema advice](../skills/1-discover/bdtopo-schema-guide/README.md) | Model version, document revision, class/field, format, official source and pages. State the limits of the bundled subset and any unverified mapping. |

A saved QGZ does not embed its source data. Relative paths alone do not establish that a
project can be moved; the declared bundle and relocation check determine that claim.
A valid remote-layer provider does not prove that tiles were rendered. Report whether
rendering was checked, failed or not performed.

Return to the [documentation guide](README.md).
