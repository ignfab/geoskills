# spatial-aggregation

**Family:** [4. Analyze and derive](../README.md).

Vector objects to polygon-zone indicators, with explicit assignment and reconciliation.
The skill aggregates objects (points, lines or polygons such as buildings) into zones such
as municipalities to produce counts, sums, means and explicit-denominator ratios, with an
audit of unmatched and multiple matches. Its bundled helper writes one row per zone,
including empty zones, to a GeoPackage, a CSV and an audit JSON; source data stay intact.

## When to use it

- Count points or buildings per municipality, keeping empty zones and listing the objects
  that fall in no zone.
- Compute the sum and mean of a numeric field (such as `height`) per zone, with missing
  measures counted as missing rather than zero.
- Decide how objects on shared borders are assigned (strict containment, or every zone
  touched) and report multiple assignments.
- Compute a ratio per zone with an explicit denominator field of the zone layer.

## When to use another skill

- Descriptive statistics of one layer, without any zone join:
  [`geospatial-descriptive-statistics`](../geospatial-descriptive-statistics/README.md).
- Raster zonal statistics, such as the mean of a DEM per polygon:
  [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md) or
  [`geopandas-vector-analysis`](../geopandas-vector-analysis/README.md).
- Generic overlays and other spatial operations: [`geopandas-vector-analysis`](../geopandas-vector-analysis/README.md).
- Repair of null, empty or invalid geometry, which stops the aggregation:
  [`vector-data-quality`](../../3-prepare/vector-data-quality/README.md).

None of these skills is a runtime dependency of `spatial-aggregation`.

## What you get

- A new directory (an existing one is refused) with `indicators.gpkg` (layer
  `indicators`), `indicators.csv` and `audit.json`.
- One row per zone with its ID and unchanged geometry, in the zones' CRS, plus `count`;
  `--field` adds `valid`, `missing`, `sum` and `mean`, and `--denominator` adds `ratio`.
  An empty zone has count 0, sum 0 and a null mean; zero or missing denominators give null.
- An audit of input, matched and unmatched objects, multiple-match IDs, assignments,
  predicate, policy, CRSs, undefined ratios and GeoPandas/pandas versions.
- Checks before reporting: both files reopened with every zone ID (as strings, leading
  zeros kept), geometry and CRS; matched plus unmatched objects equal to the input rows;
  zone counts summing to the assignments; representative magnitudes checked independently.
  A nonempty output where every count is zero is still investigated.
- Explicit choices: the default `within` predicate leaves points on borders unmatched;
  the default `error` policy stops on multiple matches; `all` and `lowest-id` are used only
  when that decision is explicit.
- The skill never assigns a guessed CRS, picks an arbitrary winner to make totals look
  plausible, replaces missing measures with zero or infers a denominator. It performs no
  raster processing, automatic geometry repair, population redistribution or areal
  interpolation.

## Requirements

GeoPandas ≥ 1.0, pandas, Shapely and a functioning vector I/O engine. Check with
`python3 -c "import geopandas, pandas, shapely; print(geopandas.__version__, pandas.__version__, shapely.__version__)"`.
The user can run `python3 -m pip install 'geopandas>=1.0,<2'` if needed; agents never
install software. No network service is used.

## Installation

```bash
npx skills add ignfab/geoskills --skill spatial-aggregation
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/4-analyze`.

## Example

> Count the points of `data/aggregation_objects.geojson` per zone of
> `data/aggregation_zones.geojson`, with the strict containment predicate. Keep empty
> zones, report points without a zone and export a GeoPackage and a CSV to `output/`.

Expected: counts 2/1/0 for zones `001`/`002`/`NA`, with the border point and the outside
point unmatched. The helper, with example identifiers replaced by discovered names:

```bash
python3 scripts/aggregate.py objects.gpkg zones.gpkg output/indicators --objects-layer buildings --zones-layer municipalities --zone-id code --predicate within --policy error
python3 scripts/aggregate.py objects.gpkg zones.gpkg output/summary --objects-layer buildings --zones-layer municipalities --zone-id code --object-id id --field height --predicate intersects --policy all
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Discovery, matching and verification. |
| [scripts/aggregate.py](scripts/aggregate.py) | Count/sum/mean/ratio and GeoPackage/CSV/audit export. |
| [references/spatial-predicates.md](references/spatial-predicates.md) | Predicates: borders and geometry choices. |
| [references/aggregation-policies.md](references/aggregation-policies.md) | Policies: ambiguity, nulls and ratios. |
| [references/validation-and-reconciliation.md](references/validation-and-reconciliation.md) | Validation: totals and round trips. |

## Tests

- [French agent scenarios](../../../tests/spatial-aggregation.md): 2 positive + 2 negative.
- Offline: [test_spatial_aggregation.py](../../../tests/test_spatial_aggregation.py)
  (`aggregate.py` on border, overlap, null and ratio cases, and the SPA-01 and SPA-02
  references on their fixtures). No live test.

## Related skills

- [`bdtopo-schema-guide`](../../1-discover/bdtopo-schema-guide/README.md) clarifies BD TOPO
  special values before a producer-specific field is summarized.
- [`vector-data-quality`](../../3-prepare/vector-data-quality/README.md) repairs geometry
  when that separate decision is taken.
- [`municipality-building-profile`](../../6-workflows/municipality-building-profile/README.md)
  produces the building portrait of one municipality and leaves generic multi-zone
  assignment to this skill.
- [`map-illustration`](../../5-publish/map-illustration/README.md) maps the indicators once
  they are computed; it does not compute indicators itself.
