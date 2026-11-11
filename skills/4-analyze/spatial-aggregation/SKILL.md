---
name: spatial-aggregation
description: Aggregate vector objects into polygon zones to produce territorial counts, sums, means and explicit-denominator ratios, with audited unmatched and multiple matches. Use for buildings per municipality or object-to-zone indicators; not single-table descriptive summaries, generic overlays or raster zonal statistics.
---

# Spatial aggregation

Produce one row per zone, including empty zones. Use `geospatial-descriptive-statistics`
for one-table summaries and `gdal-raster-basics` or `geopandas-basics` for raster zonal
statistics. This skill does not redistribute populations or repair input geometry.

## Prerequisites

Check `python3 -c "import geopandas, pandas, shapely; print(geopandas.__version__, pandas.__version__, shapely.__version__)"`.
Use GeoPandas ≥ 1.0 with a functioning vector I/O engine. If missing, give the user
`python3 -m pip install 'geopandas>=1.0,<2'` for their chosen environment. Never install
software or run interactive setup. Existing compatible environments may be selected.

## Match and summarize

1. Discover layers (`geopandas.list_layers(path)`), fields, types, geometry and declared
   CRSs in **both** sources. Select unique non-null string zone IDs and stable object IDs;
   otherwise use zero-based source row positions and name that limitation.
2. Check null/empty/invalid geometry and polygon zones. Stop on defects; geometry repair
   requires a separate decision (`vector-data-quality`). Transform known CRSs to a common
   CRS in memory; never assign a guessed CRS. State units for any requested measurements.
3. Select the [predicate](references/spatial-predicates.md) and
   [assignment policy](references/aggregation-policies.md) from the request. Default
   `within` excludes points on borders; `error` stops on multiple matches. Explain these
   choices. Do not choose an arbitrary winner to make totals look plausible.
4. Resolve the [helper](scripts/aggregate.py) from this skill folder and replace all
   example identifiers with discovered names:

```bash
python3 scripts/aggregate.py objects.gpkg zones.gpkg output/indicators --objects-layer buildings --zones-layer municipalities --zone-id code --predicate within --policy error
python3 scripts/aggregate.py objects.gpkg zones.gpkg output/summary --objects-layer buildings --zones-layer municipalities --zone-id code --object-id id --field height --predicate intersects --policy all
```

Use `--policy all` or `lowest-id` only when that decision is explicit. Ratios additionally
require `--denominator <zone-field>` and `--numerator count|sum`, a documented denominator
meaning and compatible units. Zero/missing denominators produce null, never infinity.
Output is a new directory containing GeoPackage, CSV and audit JSON; source data stay intact.

## Validate the output

Apply [reconciliation](references/validation-and-reconciliation.md). Reopen both files;
verify every zone ID, geometry and CRS, zero counts for empty zones and null means. Compare
count totals with assignments, and matched plus unmatched objects with input rows. Explicitly
report duplicated assignments under `all`, missing measures, zero denominators, source
editions, predicates, policies, units, versions and output paths. Check representative
magnitudes independently. A nonempty output with all counts zero still needs investigation.

## References

- [Spatial predicates](references/spatial-predicates.md): borders and geometry choices.
- [Aggregation policies](references/aggregation-policies.md): ambiguity, nulls and ratios.
- [Validation and reconciliation](references/validation-and-reconciliation.md): totals and round-trips.
