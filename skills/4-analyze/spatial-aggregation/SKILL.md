---
name: spatial-aggregation
description: Aggregate vector objects into polygon zones to produce territorial counts, sums, means and explicit-denominator ratios, with audited unmatched and multiple matches. Use for buildings per municipality or object-to-zone indicators; not single-table descriptive summaries, generic overlays or raster zonal statistics.
---

# Spatial aggregation

Produce one row per zone, including empty zones. Use `geospatial-descriptive-statistics`
for one-table summaries and `gdal-raster-processing` or `geopandas-vector-analysis` for raster zonal
statistics. This skill does not redistribute populations or repair input geometry.

## MCP servers

Optional. Use a connected MCP server first when it already holds the data.

- **PostGIS:** when both layers are tables of a PostGIS database and a PostGIS MCP server
  is connected (a server giving SQL access to that database; its name or tools mention
  `postgis`, `postgres` or `sql`, and tool names differ between servers, so read the tool
  list), aggregate there instead of exporting the tables. Read the schemas, geometry
  columns, SRIDs and row counts first. Express the predicate and the assignment policy
  chosen in step 3 in SQL (`ST_Within`, `ST_Intersects`), keep empty zones with a left
  join from the zones, count missing and non-finite measures apart, and run the
  reconciliation of *Validate the output* on the query result. Run read-only queries:
  `SELECT` without `INTO`, and no function that changes data, schema or SRID. Aggregate in
  the database and bound exploratory queries with `LIMIT`. Create a result table only on
  request, under a name you checked is unused; never drop, replace, alter or update an
  existing table.
- **Geocontext** ([ignfab/geocontext](https://github.com/ignfab/geocontext), tools often
  prefixed `mcp__geocontext__`): for a single count of Géoplateforme reference objects in
  one administrative unit, with no file output. Get the `feature_ref` of the unit with
  `geocode` then `adminexpress`, checking that it is the unit requested, find the type
  with `gpf_search_types`, then count with `gpf_count_features` filtered by intersection
  with that `feature_ref`. In Geocontext 0.9 the same tools are `gpf_wfs_search_types` and
  `gpf_wfs_get_features` with `result_type: "hits"` and
  `spatial_operator: "intersects_feature"`: read the input schema of the connected server.
  Say that it counts the objects sharing an area with the unit, including those that cross
  its boundary; objects that only touch it were left out on 2026-11-13. Name the type and
  the date. Geocontext gives only that single count: several zones with a border policy,
  sums, means or ratios need the PostGIS route above or the helper.

For files, use the helper below. Without these servers, or when a call fails, use the
helper on files: get Géoplateforme layers with `geopf-wfs-download`, and ask the user for
an export of database tables; never ask for database credentials. Never install, configure
or start an MCP server yourself.

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
   The helper aligns objects to the zones' declared CRS and preserves that output CRS;
   it does not need EPSG:2154 for counts/sums. Handle polar/antimeridian topology explicitly.
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
