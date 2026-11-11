# Validate territorial indicators

Preserve source hashes and load outputs from disk, not only the in-memory result.
GeoPackage and CSV must have exactly the original zone IDs, including leading zeroes;
read CSV IDs as strings with `keep_default_na=False` so a literal `NA` remains an ID.
Blank statistic cells represent undefined values, not zero. Verify unchanged geometry
and output CRS against the zones, and all expected derived fields after reopening.

The audit defines **matched_objects** before tie-breaking, **multiple_match_ids** before
resolution and **assignments** after applying the chosen policy:

- `matched_objects + len(unmatched_ids) == input objects` (no invalid geometry is silently excluded).
- `sum(zone count) == assignments`.
- For `error`/`lowest-id`, `assignments == matched_objects`.
- For `all`, `assignments >= matched_objects`; excess assignments explain double counting.
- For each measured zone, `valid + missing == count`; mean/sum are undefined when all
  assigned measures are null. Empty-zone sum is explicitly zero by convention.

Check finite sums and means against a manually calculated small subset; check a shared
border, an overlapping zone and an unmatched object. For ratios verify the supplied
numerator and denominator and null results for zero/missing denominators. Check extents
and geographic coverage if all objects are unmatched; do not call such an output correct
merely because the file opens.

Report editions and input layer names, spatial predicate, assignment rule, unmatched and
ambiguous IDs/counts, null numeric measures, units and software versions. The helper writes
`audit.json`; add source editions/units and interpretation that cannot be inferred from files.
