# spatial-aggregation

**Family:** [4. Analyze and derive](../README.md).

Vector objects to polygon-zone indicators, with explicit assignment and reconciliation.

## Requirements

GeoPandas ≥ 1.0, Pandas, Shapely and vector I/O. The user can run
`python3 -m pip install 'geopandas>=1.0,<2'` if needed; agents never install software.

## Install

```bash
npx skills add ignfab/geoskills --skill spatial-aggregation
```

## Contents

- [SKILL.md](SKILL.md): discovery, matching and verification.
- [aggregate.py](scripts/aggregate.py): count/sum/mean/ratio and GeoPackage/CSV/audit export.
- [Predicates](references/spatial-predicates.md), [policies](references/aggregation-policies.md)
  and [validation](references/validation-and-reconciliation.md).
- [French scenarios](../../../tests/spatial-aggregation.md).

Outputs keep zone IDs and geometry and add indicators; source datasets remain unchanged.
Existing output directories are refused. No raster processing, automatic repair or areal
interpolation. [geopandas-vector-analysis](../geopandas-vector-analysis/README.md) covers general spatial
operations; [geospatial-descriptive-statistics](../geospatial-descriptive-statistics/README.md)
covers one-table distributions. Neither is a runtime dependency.
