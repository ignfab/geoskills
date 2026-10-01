# Attributes, schema and duplicates

## Stable identifiers

```python
assert "id" in gdf.columns
missing_id = gdf["id"].isna()
duplicate_id = gdf["id"].duplicated(keep=False)
print(gdf.loc[missing_id | duplicate_id, ["id"]])
```

Do not generate replacement IDs until you know whether duplicate rows represent accidental
copies, multipart pieces or legitimate repeated observations.

## Required fields and domains

```python
required = ["id", "name", "status"]
missing_columns = sorted(set(required) - set(gdf.columns))
null_counts = gdf[[c for c in required if c in gdf]].isna().sum()
unknown_status = ~gdf["status"].isin({"active", "inactive"})
```

For numeric values, check ranges and units rather than only dtypes:

```python
bad_height = gdf["height_m"].notna() & ~gdf["height_m"].between(0, 500)
```

Keep domain rules close to their authoritative source. A generic skill cannot decide that a
negative value, missing name or repeated identifier is always invalid.

## Exact row duplicates

Ignore the dataframe index when comparing records:

```python
exact = gdf.duplicated(keep=False)
print(gdf.loc[exact].sort_values("id"))
```

## Geometry duplicates

Equivalent geometries can have a different ring start point or coordinate order. Normalize
before comparison:

```python
normalized = gdf.geometry.normalize()
comparable = ~gdf.geometry.isna() & ~gdf.geometry.is_empty
duplicate_geometry = comparable & normalized.duplicated(keep=False)
print(gdf.loc[duplicate_geometry, ["id", "geometry"]])
```

Geometry duplicates are not necessarily duplicate features: stacked addresses, temporal
observations and administrative records may legitimately share geometry. Compare business
keys and relevant attributes before deleting anything.

A conservative exact-feature key:

```python
keys = ["source", "source_id", "status"]
feature_key = gdf[keys].astype("string").fillna("<NULL>").agg("\x1f".join, axis=1)
duplicate_feature = feature_key.duplicated(keep=False) & duplicate_geometry
```

## Schema and format constraints

Before writing, inspect:

```python
print(gdf.dtypes)
print(gdf.geom_type.value_counts(dropna=False))
print(gdf.crs)
print(gdf.total_bounds)
```

Prefer GeoPackage or GeoParquet for modern workflows. Shapefile truncates field names,
has limited data types and splits one dataset across several files. Reopen the output to
catch schema coercion:

```python
gdf.to_file("checked.gpkg", layer="features")
roundtrip = gpd.read_file("checked.gpkg", layer="features")
assert list(roundtrip.columns) == list(gdf.columns)
assert len(roundtrip) == len(gdf)
```

## Produce an audit report

Keep issue flags rather than only printing totals:

```python
report = gdf[["id"]].copy()
report["null_geometry"] = gdf.geometry.isna()
report["empty_geometry"] = gdf.geometry.is_empty
report["invalid_geometry"] = ~gdf.geometry.isna() & ~gdf.geometry.is_valid
report["duplicate_id"] = gdf["id"].duplicated(keep=False)
comparable = ~gdf.geometry.isna() & ~gdf.geometry.is_empty
report["duplicate_geometry"] = (
    comparable & gdf.geometry.normalize().duplicated(keep=False)
)
report.to_csv("quality_report.csv", index=False)
```

This makes exclusions and repairs reviewable and reproducible.
