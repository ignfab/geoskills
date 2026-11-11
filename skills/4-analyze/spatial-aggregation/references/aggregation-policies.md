# Assignment and statistical conventions

Use `error` for ambiguous assignments until the user/request supplies a policy. `all`
counts every distinct object-zone pair; totals can exceed the number of matched objects.
`lowest-id` picks the lexically smallest zone ID deterministically, **not** the largest
intersection or closest center. Use it only as an explicit tie-break rule. Unmatched
objects are listed and excluded from zone statistics under every policy.

The helper preserves every zone ID and geometry; output attributes are IDs and derived
statistics only. Original object IDs are checked for uniqueness, or positional row IDs
are created after resetting the source index. Duplicate DataFrame index labels are not
object IDs. No geometry repair or deduplication is implicit.

`count` counts assigned objects, regardless of the measure's missingness. `valid` counts
finite numeric measures, `missing = count - valid`, `sum` uses `min_count=1`, and `mean`
uses valid measures only. A zone with no objects has count 0, sum 0, mean null; a zone with
objects but all-null measures has a null sum and mean. Infinite measures and nonnumeric
dtypes are rejected. Do not replace missing heights with zero.

Ratios divide the chosen count or sum by an explicit nonnegative numeric zone attribute.
State what the denominator measures, its edition and units. Zero or missing denominators
produce null and are counted in the audit; an absent denominator is never inferred from
geometry or population guesses. Rates need a separately stated multiplier, such as 1000.

Area weighting is not implemented by the helper. If explicitly requested, first decide
whether the variable is extensive (a count/total that might be apportioned) or intensive
(a mean/rate requiring its denominator). Do not apply area fractions to a height or ratio
as if it were a conserved total. Advanced areal interpolation is outside this skill.

Before summarizing a producer-specific field, verify documented sentinel values. Declare
any sentinel-to-null conversion in a derived in-memory column and report its count; keep
the original field. `bdtopo-schema-guide` can clarify BD TOPO semantics but is optional.
