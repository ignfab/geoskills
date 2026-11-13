---
name: geospatial-descriptive-statistics
description: Produce reproducible numeric and categorical attribute summaries for one geographic layer or table, including missingness, quantiles and measurement units. Use for descriptive statistics of building heights, categories or geometric measures; not object-to-zone aggregation, raster zonal statistics or inference.
---

# Geospatial descriptive statistics

Summarize **one** table without modifying it. Cross-layer territorial indicators belong to
`spatial-aggregation`; vector operations and raster zonal statistics to `geopandas-vector-analysis`
or `gdal-raster-processing`. No imputation, causal conclusions or automatic charts.

## MCP servers

Optional. When the table to summarize is in a PostGIS database and a PostGIS MCP server is
connected (a server giving SQL access to that database; its name or tools mention
`postgis`, `postgres` or `sql`, and tool names differ between servers, so read the tool
list), compute the summary there first instead of exporting the table. Read the column
types and the row count, then use `SELECT` aggregates with the conventions of the helper:
missing and non-finite values counted apart, `stddev_samp` for the sample standard
deviation and `percentile_cont` for linear quartiles. Check the count identities of
*Validate the output* on the result. Run read-only queries: `SELECT` without `INTO`, and
no function that changes data, schema or SRID. Aggregate in the database and bound
exploratory queries with `LIMIT`. For files, use the helper below. Without such a server,
or when a query fails, ask the user for an export and use the helper on it; never ask for
database credentials, and never take them from a configuration file or the environment to
connect another way. Never install, configure or start an MCP server yourself.

## Prerequisites

Check the selected Python environment: `python3 -c "import pandas; print(pandas.__version__)"`.
CSV summaries need only Pandas: if missing, give the user `python3 -m pip install pandas`.
For vector inputs or geometry measurements, also check GeoPandas and Shapely; the user-run
command is `python3 -m pip install 'geopandas>=1.0,<2'` (includes Pandas and Shapely).
Never install software or run interactive setup. Only a missing dependency of the chosen
input/workflow blocks execution; do not require GeoPandas, GDAL or QGIS for a CSV summary.

## Inspect and summarize

1. For CSV, inspect headers and rows with Pandas or Python's `csv` module; no layer
   discovery or GeoPandas is needed. For vector files, discover actual layer names
   (`geopandas.list_layers(path)`), fields, types, CRS and row count, then load only the
   selected layer. Record source, edition if known and units from metadata; unknown
   units stay unknown. Preserve string IDs and zeroes.
2. Choose requested numeric/categorical fields explicitly. Numeric strings may be parsed,
   but invalid text and infinities must be counted separately from missing values.
   For geometry measurements first read [geometry units](references/geometry-units.md).
3. Use the bundled [helper](scripts/summarize.py), resolved relative to this skill folder:

```bash
python3 scripts/summarize.py input.csv output/summary --numeric height --categorical code
python3 scripts/summarize.py input.gpkg output/summary --layer buildings --numeric height --units '{"height":"m"}'
```

Replace example names with inspected names. The helper creates a **new directory** and
writes JSON, a long-form CSV and Markdown. It uses sample standard deviation (`ddof=1`),
linear quartiles, finite observations only, and categorical frequencies over all rows.
Missing categories are separate; all-null/empty numeric summaries are null, including sum.
Use `--ddof 0` only for a stated population convention. No spatial matching is performed.

## Validate the output

Reopen JSON with a strict parser and CSV with string types. For each numeric field check
`valid + missing + invalid_text + infinite = total`; category counts must sum to total.
A zero-row dataset is an explicit empty result, never a successful substantive analysis.
Check min ≤ median/mean ≤ max, quantile order, units and plausible magnitudes. JSON must
contain no NaN/Infinity; CSV's `value_json` preserves null versus zero and string codes.
Report source/edition, selected fields, CRS, versions, methods, output paths and warnings.
For derived areas/lengths report calculation CRS and units, independently check a sample,
and confirm input files were unchanged. A missing CRS does not prevent attribute-only work.

## References

- [Numeric statistics](references/numeric-statistics.md): counts, standard deviation and quantiles.
- [Categorical statistics](references/categorical-statistics.md): identifiers and denominators.
- [Geometry units](references/geometry-units.md): projected measurements and validity.
