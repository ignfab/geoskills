# Geometry validity and repair

## Classify geometry problems

```python
null = gdf.geometry.isna()
empty = gdf.geometry.is_empty
invalid = ~gdf.geometry.isna() & ~gdf.geometry.is_valid
reasons = gdf.geometry[invalid].is_valid_reason()
print(reasons.value_counts())
```

Typical reasons include `Self-intersection`, `Ring Self-intersection`, `Nested shells` and
`Hole lies outside shell`. Keep the feature identifier beside the reason so the repair is
auditable.

Null, empty and invalid are different:

- **null**: no geometry value; recover it from a source field or quarantine the row;
- **empty**: geometry object without coordinates; usually quarantine it;
- **invalid**: coordinates exist but violate the OGC geometry rules; repair may be possible.

## Repair with `make_valid`

```python
fixed = gdf.copy()
bad = ~fixed.geometry.isna() & ~fixed.geometry.is_valid
fixed.loc[bad, "geometry"] = fixed.geometry[bad].make_valid()
```

Do not use `buffer(0)` as a universal repair. It can drop polygon parts and makes the
chosen repair strategy implicit. `make_valid()` is explicit, but can still change geometry
type or split one geometry into several parts.

Compare types before and after:

```python
comparison = (
    gdf.loc[bad, ["id"]]
    .assign(before=gdf.geometry[bad].geom_type,
            after=fixed.geometry[bad].geom_type)
)
print(comparison)
```

A repaired Polygon may become MultiPolygon. A collapsed polygon may become a LineString or
GeometryCollection. If the target accepts polygons only, quarantine non-polygonal results
instead of silently deleting them:

```python
allowed = fixed.geom_type.isin(["Polygon", "MultiPolygon"])
quarantine = fixed.loc[~allowed]
fixed = fixed.loc[allowed]
```

## Explode multipart results only when required

```python
parts = fixed.explode(index_parts=False, ignore_index=True)
```

Exploding changes feature counts and may duplicate attributes. Create a stable source ID
first and validate the expected one-to-many relationship.

## Precision and near-coincident coordinates

Snapping coordinates to a precision grid can resolve tiny slivers, but it changes data and
may collapse narrow geometries. Choose the grid in CRS units and measure the effect:

```python
before_area = fixed.area.sum()
snapped = fixed.copy()
snapped["geometry"] = snapped.geometry.set_precision(0.01)  # 1 cm in a metre CRS
after_area = snapped.area.sum()
print(after_area - before_area)
```

Never use a metric precision, area or distance operation in EPSG:4326. Reproject first.

## GDAL command line

Inspect metadata and geometry types:

```bash
ogrinfo -al -so input.gpkg
```

When discarding lower-dimensional collection parts fits the requested output, repair
while writing a new GeoPackage:

```bash
ogr2ogr -f GPKG repaired.gpkg input.gpkg -makevalid -nlt PROMOTE_TO_MULTI
```

`ogr2ogr -makevalid` calls `MakeValid()` and then removes lower-dimensional components
from collections. A polygon with a collapsed spike may lose its LineString component;
`-nlt PROMOTE_TO_MULTI` does not prevent that loss or turn collapsed lines into polygons.
For a reviewable repair that retains those components, use the Python workflow above.
Check that the output layer schema accepts the resulting geometry types; a driver warning
about inserting a GeometryCollection into a Polygon layer is not a conformant export.

Reopen the result and inspect geometry types, empties, feature counts and components.
See the official [ogr2ogr documentation](https://gdal.org/en/stable/programs/ogr2ogr.html#cmdoption-ogr2ogr-makevalid).

## Topology between features

`is_valid` checks each feature independently. It does **not** detect gaps, overlaps between
separate polygons, duplicated boundaries or disconnected networks. For polygon coverage,
first detect overlaps with a self spatial join or overlay, and define an explicit tolerance
before treating small slivers as errors. Do not automatically dissolve overlaps unless the
business rule says adjacent features may merge.
