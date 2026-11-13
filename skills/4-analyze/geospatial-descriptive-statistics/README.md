# geospatial-descriptive-statistics

**Family:** [4. Analyze and derive](../README.md).

Reproducible attribute distributions for one table; no spatial joins or raster statistics.

## Requirements

Python 3.9+ and Pandas for CSV summaries (`python3 -m pip install pandas` if missing).
Only vector inputs and metric geometry work additionally need GeoPandas/Shapely:
`python3 -m pip install 'geopandas>=1.0,<2'` includes those and Pandas. Use a Python version
supported by the selected package release. Agents reuse existing environments and never
install dependencies. CSV summaries do not need a GIS stack or plotting libraries.

## Install

```bash
npx skills add ignfab/geoskills --skill geospatial-descriptive-statistics
```

## Contents

- [SKILL.md](SKILL.md): inspection, execution and validation.
- [scripts/summarize.py](scripts/summarize.py): deterministic JSON/CSV/Markdown writer.
- [Numeric statistics](references/numeric-statistics.md), [categories](references/categorical-statistics.md)
  and [geometry units](references/geometry-units.md).
- [French scenarios](../../../tests/geospatial-descriptive-statistics.md).

The helper refuses an existing output directory. CSV contains `field,metric,value_json`:
parse the last cell as JSON to retain nested categories, nulls and leading-zero strings.
For territorial grouping use `spatial-aggregation`; for spatial primitives use
[geopandas-vector-analysis](../geopandas-vector-analysis/README.md).
