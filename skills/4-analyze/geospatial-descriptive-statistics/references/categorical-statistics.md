# Categories and string identifiers

Read CSV identifiers as strings **before** type inference loses leading zeroes. For example,
`pd.read_csv(path, dtype='string', keep_default_na=False, na_values=[''])` keeps `01001`
and the literal category `NA`; only blank cells become missing. Confirm the source's actual
missing-value markers before changing that policy. Do not turn missing into the string
`"nan"`, merge it with a real `"Unknown"` category, or normalize case without a request.

The helper uses string category labels, sorted lexically, and one JSON null category.
Counts include missing; frequency uses **all rows**, so frequencies sum to one for a
nonempty column. If valid-only percentages are requested, name that different denominator
and report the missing count separately. Empty inputs have no categories or frequencies.
CSV readers should parse the `value_json` column as JSON, not infer category types.
