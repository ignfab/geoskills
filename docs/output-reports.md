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
