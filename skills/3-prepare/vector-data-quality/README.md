# vector-data-quality

**Family:** [3. Prepare and check](../README.md).

Audit and repair vector geospatial data before analysis or publication: invalid, null and
empty geometries, self-intersections, gaps and overlaps between polygons, slivers, duplicate
features, missing identifiers, schema issues and unexpected geometry-type changes.

This complements [geopandas-vector-analysis](../../4-analyze/geopandas-vector-analysis/README.md), which covers general
vector processing, and [crs-reprojection-france](../crs-reprojection-france/README.md),
which covers CRS diagnosis and conversion.

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

## Installation

```bash
npx skills add ignfab/geoskills --skill vector-data-quality
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Audit-first workflow, deliberate repair and output validation. |
| [references/geometry-validity.md](references/geometry-validity.md) | Geometry diagnosis, repair methods, suspicious valid geometries and CLI audit. |
| [references/coverage-topology.md](references/coverage-topology.md) | Gaps, overlaps and unmatched shared edges between polygons. |
| [references/attributes-and-duplicates.md](references/attributes-and-duplicates.md) | IDs, required fields, domains, duplicates and audit reports with severity levels. |

## Example

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
