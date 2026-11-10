# Review a geocoded CSV

Keep every input row and its stable ID, including service errors and unmatched rows.
Select `result_status`, `result_score`, `result_score_next`, `result_type`,
`result_citycode`, `longitude` and `latitude` in the API response. Preserve the expected
municipality code separately; a postcode is not an INSEE code.

## Apply an explicit policy

The bundled helper writes a new UTF-8 CSV with `review_status` and `review_reason`.
Choose thresholds for the task and inspect a sample of accepted and rejected rows.
These example thresholds are heuristics, not calibrated probabilities:

```bash
python3 scripts/classify_results.py geocoded.csv reviewed.csv \
  --min-score 0.7 --min-margin 0.1 --city-column expected_citycode \
  --accepted-type housenumber > quality-report.json
```

Paths to scripts are relative to the skill directory; adapt data paths to the workspace.
Omit `--city-column` only when the input has no expected municipality; report that this
check was unavailable. Omit `--accepted-type` when any granularity is acceptable, or
repeat it for each allowed type found in service metadata.

- `accepted`: passes the selected policy, including finite, in-range coordinates.
- `review`: ambiguous/low scores, wrong municipality or granularity, service errors,
  skipped rows, malformed scores or missing coordinates. Reasons are retained.
- `unmatched`: the service explicitly returned `not-found`.

A blank second score is treated as no second candidate reported. It is not evidence of
uniqueness. Administrative changes and legitimate street-level matches can require human
review. Never describe `accepted` as a verified address, and never retry `not-found`
indefinitely. Correct query inputs before retrying `skipped`; cap transient-error retries.

## Validate

Re-read the CSV, check IDs and row order against the input, and require the category totals
to sum to the original row count. Keep input columns unchanged, including leading zeros.
Report thresholds, counts, omitted checks and reasons requiring review. The helper refuses
an existing output, duplicate headers and pre-existing review columns.
