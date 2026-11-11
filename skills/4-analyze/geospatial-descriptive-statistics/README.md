# geospatial-descriptive-statistics

Reproducible attribute distributions for one table; no spatial joins or raster statistics.

## Requirements

Python 3.9+, Pandas; GeoPandas/Shapely for vector data and metric geometry work. If missing,
the user can run `python3 -m pip install pandas geopandas`; agents never install dependencies.

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
[geopandas-basics](../geopandas-basics/README.md).
