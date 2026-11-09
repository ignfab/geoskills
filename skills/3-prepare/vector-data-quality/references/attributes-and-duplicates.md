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

### Duplicate features

Compare the business attributes and normalized geometry **together**, on the same rows:

```python
keys = ["source", "source_id", "status"]
feature_key = gdf[keys].copy()
feature_key["geometry_wkb"] = gdf.geometry.normalize().to_wkb()
comparable = ~gdf.geometry.isna() & ~gdf.geometry.is_empty
duplicate_feature = comparable & feature_key.duplicated(keep=False)
```

Choose `keys` from the actual schema and reserve `geometry_wkb` for the comparison.
Separate duplicate-attribute and duplicate-geometry masks may refer to different pairs
of rows: intersecting those masks produces false positives. Keep native attribute values;
joining strings with a separator or replacing nulls with a literal can create collisions.
Normalization handles coordinate ordering, not every topologically equivalent geometry
(for example, one with additional collinear vertices).

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

### Severity levels

Rank issues so the user sees first what blocks the requested use:

- **blocker**: stops the analysis or publication (null, empty or invalid geometry before an
  overlay, missing CRS);
- **major**: gives wrong results unless resolved (duplicate identifiers where the contract
  requires unique ones, overlaps in a coverage);
- **minor**: worth reporting, without effect at the intended scale (slivers, repeated
  points, shared geometries with distinct attributes).

```python
severity = {"null_geometry": "blocker", "empty_geometry": "blocker",
            "invalid_geometry": "blocker", "duplicate_id": "major",
            "duplicate_geometry": "minor"}
issues = (report.melt(id_vars="id", var_name="issue", value_name="flagged")
          .query("flagged").drop(columns="flagged"))
issues["severity"] = issues["issue"].map(severity)
print(issues.groupby(["severity", "issue"]).size())
issues.to_csv("quality_issues.csv", index=False)
```

This mapping is a default: adapt it to the data contract and the requested use, and state
the changes in the report. A duplicate geometry is minor for stacked addresses but major
for a parcel layer.
