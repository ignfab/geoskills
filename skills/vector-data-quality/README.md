# vector-data-quality

Audit and repair vector geospatial data before analysis or publication: invalid, null and
empty geometries, self-intersections, duplicate features, missing identifiers, schema
issues and unexpected geometry-type changes.

This complements [geopandas-basics](../geopandas-basics/README.md), which covers general
vector processing, and [crs-reprojection-france](../crs-reprojection-france/README.md),
which covers CRS diagnosis and conversion.

## Requirements

GeoPandas ≥ 1.0 and Shapely ≥ 2.0. GDAL ≥ 3.1 is optional for the `ogr2ogr -makevalid`
workflow.

## Installation

```bash
npx skills add ignfab/geoskills --skill vector-data-quality
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Audit-first workflow, deliberate repair and output validation. |
| [references/geometry-validity.md](references/geometry-validity.md) | Geometry diagnosis, repair and topology pitfalls. |
| [references/attributes-and-duplicates.md](references/attributes-and-duplicates.md) | IDs, required fields, domains, duplicates and audit reports. |

## Example

```python
import geopandas as gpd

src = gpd.read_file("input.gpkg")
bad = ~src.geometry.isna() & ~src.geometry.is_valid
print(src.geometry[bad].is_valid_reason())

clean = src.copy()
quarantine = clean.loc[clean.geometry.isna() | clean.geometry.is_empty].copy()
clean = clean.loc[~clean.geometry.isna() & ~clean.geometry.is_empty].copy()
bad = ~clean.geometry.is_valid
clean.loc[bad, "geometry"] = clean.geometry[bad].make_valid()
clean.to_file("repaired.gpkg")
```
