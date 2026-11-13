# vector-data-quality

**Family:** [3. Prepare and check](../README.md).

Audit and repair vector geospatial data before analysis or publication: invalid, null and
empty geometries, self-intersections, gaps and overlaps between polygons, slivers, duplicate
features, missing identifiers, schema issues, implausible extents and unexpected
geometry-type changes. The skill works with GeoPandas, Shapely and GDAL, keeps the source
unchanged and writes repairs to a new file.

## When to use it

- Audit a layer for self-intersecting, empty and null geometries, then repair the invalid
  ones into a new GeoPackage without modifying the source.
- Detect duplicate geometries, even when their vertices are ordered differently, without
  counting null geometries as duplicates.
- Check that parcels or administrative units neither overlap nor leave gaps, and list the
  problems in a CSV.
- Diagnose a `TopologyException` before a join, overlay or statistic.
- Check identifiers, required fields and the schema before publication.

## When to use another skill

- General vector processing, such as an ordinary spatial join, when no data-quality failure
  is reported: [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md).
- A missing, wrong or unsuitable CRS rather than bad geometry, including points that land in
  the wrong place because latitude and longitude are swapped:
  [`crs-reprojection-france`](../crs-reprojection-france/README.md).
- Simplifying a coverage: [`mapshaper-simplify`](../../5-publish/mapshaper-simplify/README.md).

## What you get

- An audit that keeps null, empty and invalid geometries apart, with invalidity reasons by
  feature, duplicates, CRS, bounds and geometry types; issue flags can be exported to CSV
  with blocker, major and minor severity levels.
- For a coverage, overlap pairs with their identifiers and area, and gaps found with a
  stated `gap_width` tolerance; a thin feature on the boundary is checked before being
  called a gap.
- A repaired layer in a new file, plus a quarantine of null and empty records kept for
  review rather than dropped. Every input feature ends up in one or the other.
- Before reporting, the agent reopens the output and repeats the audit: counts reconcile
  with the source and the quarantine, the CRS is unchanged, no geometry is null, empty or
  invalid, and geometry types and areas (in a projected CRS) are compared with the source.
- The agent does not repair, snap or dissolve a coverage without an explicit rule, does not
  discard repair components silently, and does not invent a business identifier when none
  exists. If the CRS is missing or the data lie outside its area of use, it stops and
  points to `crs-reprojection-france`.
- A report with features read, written and quarantined, issues by class and severity,
  repairs applied and unresolved choices.

## Requirements

GeoPandas ≥ 1.0 and Shapely ≥ 2.0; GeoPandas ≥ 1.1 with Shapely ≥ 2.1 for coverage checks
and the `structure` repair method. GDAL ≥ 3.1 is optional for the `ogr2ogr -makevalid`
workflow, and GDAL ≥ 3.12 for `gdal vector check-geometry`, `check-coverage` and
`make-valid`.

Choose the Python or CLI route that covers the requested checks; both are not required.
The base Python command is `python3 -m pip install 'geopandas>=1.0,<2'` if missing.
Only coverage checks or advanced repair methods need the higher versions above:
`python3 -m pip install 'geopandas>=1.1,<2' 'shapely>=2.1'` if necessary.
The CLI route uses `sudo apt install gdal-bin` (Debian/Ubuntu). Check existing versions
before selecting a recipe; do not upgrade for unused features. These commands are for
the user; the agent never installs software itself.

Local processing needs no network service or API key.

## Installation

```bash
npx skills add ignfab/geoskills --skill vector-data-quality
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/3-prepare`.

## Example

> Using Python, audit a layer that contains self-intersecting polygons, empty geometries and
> null geometries. Repair the invalid geometries into a new GeoPackage without modifying the
> source file.

```python
import geopandas as gpd

src = gpd.read_file("input.gpkg", layer="features")
bad = ~src.geometry.isna() & ~src.geometry.is_valid
print(src.geometry[bad].is_valid_reason())

clean = src.copy()
quarantine = clean.loc[clean.geometry.isna() | clean.geometry.is_empty].copy()
clean = clean.loc[~clean.geometry.isna() & ~clean.geometry.is_empty].copy()
bad = ~clean.geometry.is_valid
clean.loc[bad, "geometry"] = clean.geometry[bad].make_valid()
clean.to_file("repaired.gpkg", layer="features")
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Audit-first workflow, deliberate repair and output validation. |
| [references/geometry-validity.md](references/geometry-validity.md) | Geometry diagnosis, repair methods, suspicious valid geometries and CLI audit. |
| [references/coverage-topology.md](references/coverage-topology.md) | Gaps, overlaps and unmatched shared edges between polygons. |
| [references/attributes-and-duplicates.md](references/attributes-and-duplicates.md) | IDs, required fields, domains, duplicates and audit reports with severity levels. |

## Tests

- Agent scenarios: [tests/vector-data-quality.md](../../../tests/vector-data-quality.md), in
  French (3 positive, 2 negative).
- Offline: [test_vector_quality.py](../../../tests/test_vector_quality.py) covers geometry
  classes, repair methods, quarantine, duplicates, the severity report and coverage checks,
  plus `gdal vector check-geometry`/`check-coverage` on GDAL ≥ 3.12. No live test.

## Related skills

- [`geodata-intake`](../geodata-intake/README.md) inventories a delivery and points to this
  skill when a geometry audit is needed.
- [`crs-reprojection-france`](../crs-reprojection-france/README.md) settles the CRS before
  the audit, repairs or area measurements.
- [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md) runs the joins and
  overlays once the geometries are valid.
- [`mapshaper-simplify`](../../5-publish/mapshaper-simplify/README.md) then simplifies an
  audited coverage while keeping shared borders.
