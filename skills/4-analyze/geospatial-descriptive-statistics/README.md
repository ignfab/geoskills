# geospatial-descriptive-statistics

**Family:** [4. Analyze and derive](../README.md).

Reproducible attribute distributions for one table; no spatial joins or raster statistics.
The skill summarizes numeric and categorical fields of one geographic layer or table,
with missingness, quantiles and measurement units, without modifying the source. Its
bundled helper writes the summary as JSON, a long-form CSV and Markdown in a new directory.

## When to use it

- Summarize building heights: mean, median, quartiles, sum, standard deviation and
  missing rate, in JSON, CSV and Markdown reports.
- Count the categories of a coded field and their frequencies without losing leading
  zeros (`01001`), keeping missing values as their own category.
- Summarize geometric measures such as areas, computed in a projected CRS with meter axes.
- Summarize the fields of a CSV, or of a discovered layer in a vector file such as a GeoPackage.

## When to use another skill

- Raster zonal statistics, such as the mean elevation per municipality joined to the
  polygons: [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md) or
  [`geopandas-vector-analysis`](../geopandas-vector-analysis/README.md).
- Counts, sums or ratios of objects from one layer per zone of another (cross-layer
  territorial indicators): [`spatial-aggregation`](../spatial-aggregation/README.md).
- Vector operations such as joins and overlays: [`geopandas-vector-analysis`](../geopandas-vector-analysis/README.md).
- Geometry repair before measuring: [`vector-data-quality`](../../3-prepare/vector-data-quality/README.md).

## What you get

- A new directory (an existing one is refused) holding `summary.json` (canonical, with no
  NaN or Infinity), `summary.csv` and `summary.md`. The CSV contains
  `field,metric,value_json`: parse the last cell as JSON to retain nested categories,
  nulls and leading-zero strings.
- Per numeric field: total, missing, invalid text and infinite counts, valid count, min,
  max, mean, median, sum, standard deviation and quartiles, with the declared unit
  (`unspecified` if none). Per categorical field: count and frequency of each value.
- Stated conventions: sample standard deviation (`ddof=1`; `--ddof 0` only for a stated
  population convention), linear quartiles, finite observations only, categorical
  frequencies over all rows, all-null or empty numeric summaries left null, including sum.
- Checks before reporting: JSON reopened with a strict parser and CSV with string types;
  `valid + missing + invalid_text + infinite = total` for each numeric field; category
  counts summing to the total; min ≤ median/mean ≤ max, quantile order, units and
  plausible magnitudes. A zero-row dataset is reported as an explicit empty result.
- For derived areas or lengths: the calculation CRS and units, an independent check of a
  sample, and confirmation that the input files were unchanged.
- The skill performs no imputation, causal conclusions or automatic charts. It does not
  guess source-specific sentinels, label square degrees as m², measure geometry with an
  unknown CRS or repair geometry silently. A missing CRS does not prevent attribute-only work.

## Requirements

Python 3.9+ and Pandas for CSV summaries (`python3 -m pip install pandas` if missing).
Only vector inputs and metric geometry work additionally need GeoPandas/Shapely:
`python3 -m pip install 'geopandas>=1.0,<2'` includes those and Pandas. Use a Python version
supported by the selected package release. Agents reuse existing environments and never
install dependencies. CSV summaries do not need a GIS stack or plotting libraries.

Check with `python3 -c "import pandas; print(pandas.__version__)"`; inspect GeoPandas/Shapely only for vector inputs. No network service is used.

## Installation

```bash
npx skills add ignfab/geoskills --skill geospatial-descriptive-statistics
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/4-analyze`.

## Example

> Summarize the heights 0, 10, 20 and one missing value in a synthetic table. Give the
> mean, median, quartiles, sum, standard deviation and missing rate in JSON, CSV and
> Markdown reports under `output/`.

Expected: 3 valid values and 1 missing (25%); mean and median 10, sum 30, sample standard
deviation 10, quartiles 5 and 15. The helper, with names replaced by inspected ones:

```bash
python3 scripts/summarize.py input.csv output/summary --numeric height --categorical code
python3 scripts/summarize.py input.gpkg output/summary --layer buildings --numeric height --units '{"height":"m"}'
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Inspection, execution and validation. |
| [scripts/summarize.py](scripts/summarize.py) | Deterministic JSON/CSV/Markdown writer. |
| [references/numeric-statistics.md](references/numeric-statistics.md) | Numeric statistics: counts, standard deviation, quantiles and sentinels. |
| [references/categorical-statistics.md](references/categorical-statistics.md) | Categories: string identifiers and denominators. |
| [references/geometry-units.md](references/geometry-units.md) | Geometry units: projected measurements and validity. |

## Tests

- [French agent scenarios](../../../tests/geospatial-descriptive-statistics.md): 2 positive + 2 negative.
- Offline: [test_geospatial_descriptive_statistics.py](../../../tests/test_geospatial_descriptive_statistics.py)
  (`summarize.py` on known values, CLI round trip, geometry areas). No live test.

## Related skills

- [`bdtopo-schema-guide`](../../1-discover/bdtopo-schema-guide/README.md) checks documented
  special values before statistics, for example a BD TOPO height of 0 that may mean
  unknown or not significant.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  produces a full municipal building portrait and points to this skill for additional
  distributions.
- [`map-illustration`](../../5-publish/map-illustration/README.md) maps existing values for a
  report; it does not compute statistics itself.
