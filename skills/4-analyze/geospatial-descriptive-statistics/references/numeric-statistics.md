# Numeric conventions

Use the requested fields, not every numeric column: an identifier is not a measure.
The helper parses numeric strings, counts invalid nonmissing text separately, excludes
positive/negative infinity and retains valid zeroes. Missingness is null/NaN only.
Its denominator for missing fraction is all rows; an empty denominator gives null.

Pandas provides [standard deviation](https://pandas.pydata.org/docs/reference/api/pandas.Series.std.html)
with explicit `ddof`, [linear quantiles](https://pandas.pydata.org/docs/reference/api/pandas.Series.quantile.html)
and [sum with min_count](https://pandas.pydata.org/docs/reference/api/pandas.Series.sum.html).
Use `sum(min_count=1)` so an entirely missing series does not become zero. Standard deviation
is undefined with at most `ddof` observations. Record interpolation, selected quantiles,
exclusions and units; a mean of a coded category is meaningless.

For `[0, 10, 20, null]`: total 4, finite 3, missing 1, sum 30, mean/median 10,
quartiles 5 and 15, sample standard deviation 10. These values form an independent check.
Extreme magnitudes can overflow floating-point statistics: inspect any unexpected null
statistic despite finite observations and do not report it as an ordinary missing value.

A documented source-specific sentinel is not a valid zero: for example a BD TOPO height
may use 0 for unknown/not significant. Verify the applicable model with `bdtopo-schema-guide`
or producer metadata, declare the exclusion, preserve the original column and report
sentinel counts separately from originally missing observations. Never replace all zeroes
across unrelated measures. The generic helper does not guess such source-specific rules.
