---
name: vector-data-quality
description: "Audits and repairs vector geospatial data quality with GeoPandas, Shapely and GDAL: invalid or empty geometries, self-intersections, duplicate features, missing identifiers, schema issues, implausible extents and geometry-type changes after repair. Use when the user wants to check the quality of a vector layer, validate, clean or repair it, fix invalid geometries, remove duplicates, diagnose a TopologyException, or prepare GeoPackage, Shapefile or GeoJSON data before spatial analysis or publication."
---

# Vector data quality

Audit and repair vector data before joins, overlays, statistics or publication. Keep the
original file unchanged, record each decision, and validate the repaired output.

Use `geopandas-basics` for general vector processing and `crs-reprojection-france` when the
problem is a missing, wrong or unsuitable CRS rather than bad geometry.

## Prerequisites

- **GeoPandas ≥ 1.0** and **Shapely ≥ 2.0** for the Python workflow.
- **GDAL ≥ 3.1** for the optional `ogr2ogr -makevalid` CLI workflow.
- Check existing versions; if a tool is missing, give the user the install command but do
  not install it automatically.

## Audit first

```python
import geopandas as gpd

src = gpd.read_file("input.gpkg")
comparable_geometry = ~src.geometry.isna() & ~src.geometry.is_empty
duplicate_geometry = (
  comparable_geometry
  & src.geometry.normalize().duplicated(keep=False)
)
report = {
    "features": len(src),
    "crs": str(src.crs),
    "bounds": src.total_bounds.tolist(),
    "null_geometry": int(src.geometry.isna().sum()),
    "empty_geometry": int(src.geometry.is_empty.sum()),
    "invalid_geometry": int((~src.geometry.is_valid & ~src.geometry.isna()).sum()),
    "duplicate_id": int(src["id"].duplicated(keep=False).sum()),
    "duplicate_geometry": int(duplicate_geometry.sum()),
}
print(report)
```

Do not merge null and empty geometries: null means no geometry value; empty means a valid
geometry object containing no coordinates. Inspect invalidity reasons before repairing:

```python
bad = ~src.geometry.isna() & ~src.geometry.is_valid
print(src.loc[bad, ["id"]].assign(reason=src.geometry[bad].is_valid_reason()))
```

## Repair deliberately

```python
clean = src.copy()
quarantine_mask = clean.geometry.isna() | clean.geometry.is_empty
quarantine = clean.loc[quarantine_mask].copy()
clean = clean.loc[~quarantine_mask].copy()
bad = ~clean.geometry.is_valid
clean.loc[bad, "geometry"] = clean.geometry[bad].make_valid()
```

`make_valid()` may turn a Polygon into a MultiPolygon or GeometryCollection. Inspect the
result and decide whether those types fit the target schema; never discard components
silently. Preserve and review `quarantine` rather than dropping those records unnoticed.
For a format conversion without Python:

```bash
ogr2ogr -f GPKG repaired.gpkg input.gpkg -makevalid
```

See [references/geometry-validity.md](references/geometry-validity.md) for diagnosis,
repair strategies and topology pitfalls, and
[references/attributes-and-duplicates.md](references/attributes-and-duplicates.md) for
identifier, schema, duplicate and completeness checks.

## Validate the output

Write to a **new** file, reopen it, and repeat the audit:

```python
clean.to_file("repaired.gpkg", layer="features")
check = gpd.read_file("repaired.gpkg", layer="features")
assert len(check) == len(clean)
assert check.crs == clean.crs
assert not check.geometry.isna().any()
assert not check.geometry.is_empty.any()
assert check.geometry.is_valid.all()
assert check["id"].duplicated(keep=False).sum() == clean["id"].duplicated(keep=False).sum()
print(check.geom_type.value_counts())
```

Also compare bounds, feature counts and key aggregates with the source. A successful write
is not proof of correctness: investigate unexpected feature loss, geometry-type changes or
large area differences. Require `id.is_unique` only when the dataset contract says IDs
must be unique; shared identifiers can be legitimate for multipart or temporal records.

## References

- [references/geometry-validity.md](references/geometry-validity.md) — null/empty/invalid
  geometry, validity reasons, `make_valid`, precision, dimensional collapse and CLI repair.
- [references/attributes-and-duplicates.md](references/attributes-and-duplicates.md) — IDs,
  required fields, domains, exact and geometry duplicates, schema and audit reports.

## Additional resources

- GeoPandas validity methods: <https://geopandas.org/en/stable/docs/user_guide/geometric_manipulations.html>
- Shapely `make_valid`: <https://shapely.readthedocs.io/en/stable/reference/shapely.make_valid.html>
- GDAL `ogr2ogr`: <https://gdal.org/programs/ogr2ogr.html>
