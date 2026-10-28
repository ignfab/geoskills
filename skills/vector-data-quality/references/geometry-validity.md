# Geometry validity and repair

## Classify geometry problems

```python
null = gdf.geometry.isna()
empty = gdf.geometry.is_empty
invalid = ~gdf.geometry.isna() & ~gdf.geometry.is_valid
reasons = gdf.geometry[invalid].is_valid_reason()
reason_type = reasons.str.replace(r"\[.*\]$", "", regex=True)
print(reason_type.value_counts())
```

`is_valid_reason()` appends the location, for example `Self-intersection[1 1]`: strip it
before counting, and keep the full text beside the feature identifier so the repair is
auditable.

Null, empty and invalid are different:

- **null**: no geometry value; recover it from a source field or quarantine the row;
- **empty**: geometry object without coordinates; usually quarantine it;
- **invalid**: coordinates exist but violate the OGC geometry rules; repair may be possible.

Reasons reported by GEOS:

| Reason | Usual cause | Action |
| --- | --- | --- |
| `Self-intersection` | Bowtie polygon, or rings crossing each other | `make_valid()`; check the type and area |
| `Ring Self-intersection` | A ring touching itself at a vertex | `make_valid()` |
| `Hole lies outside shell` | Hole digitized outside its shell | Both methods keep it as an extra polygon; check whether it is real |
| `Holes are nested` | Hole inside another hole | Methods disagree; compare the areas |
| `Interior is disconnected` | Holes that cut the polygon in pieces | `make_valid()` returns a MultiPolygon |
| `Nested shells` | Multipolygon part inside another part | Methods disagree; often a duplicate digitization |
| `Too few points in geometry component` | Collapsed ring or line, often after rounding | Quarantine; repair returns a lower dimension |
| `Invalid Coordinate` | NaN or infinite coordinate | Quarantine and fix the source; `make_valid()` cannot recover a coordinate |

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
GeometryCollection. If the target accepts polygons only, quarantine null, empty and
non-polygonal results instead of silently deleting them. A `Polygon EMPTY` still has a
polygon type, so checking `geom_type` alone is insufficient:

```python
allowed = (fixed.geom_type.isin(["Polygon", "MultiPolygon"])
           & ~fixed.geometry.isna() & ~fixed.geometry.is_empty)
quarantine = fixed.loc[~allowed]
fixed = fixed.loc[allowed]
```

### Choose the repair method

GeoPandas ≥ 1.1 with Shapely ≥ 2.1 offers two methods:

- **`linework`** (default) nodes every ring and rebuilds polygons from the lines. It keeps
  all input vertices and may return lines or collections, which suits a review of what
  collapsed.
- **`structure`** repairs each shell and hole, unions the shells and subtracts the holes.
  With `keep_collapsed=False` it returns polygons only.

```python
fixed = gdf.copy()
bad = ~fixed.geometry.isna() & ~fixed.geometry.is_valid
fixed.loc[bad, "geometry"] = fixed.geometry[bad].make_valid(
    method="structure", keep_collapsed=False)
```

A fully collapsed polygon then becomes `POLYGON EMPTY`, and a spike disappears from its
polygon: apply the polygon filter above again. The methods disagree on overlapping rings:
for nested shells, `linework` turns the inner shell into a hole while `structure` merges it
into the outer shell. Compare areas before and after, and say which method was used.

## Explode multipart results only when required

```python
parts = fixed.explode(index_parts=False, ignore_index=True)
```

Exploding changes feature counts and may duplicate attributes. Create a stable source ID
first and validate the expected one-to-many relationship.

## Valid but suspicious

Valid geometries can still be errors. Flag them for review; do not delete them. Measure in a
projected CRS (Lambert-93 for metropolitan France; see `crs-reprojection-france` elsewhere)
and adapt the thresholds to the scale of the data:

```python
import numpy as np
from shapely import get_num_coordinates

area = gdf.area
compactness = 4 * np.pi * area / gdf.length ** 2  # Polsby-Popper: 1 for a disc
flags = gdf[["id"]].assign(
    tiny=area < 1.0,  # m²
    thin=compactness < 0.05,
    repeated_points=get_num_coordinates(gdf.geometry)
    - get_num_coordinates(gdf.geometry.remove_repeated_points()),
    has_z=gdf.geometry.has_z,
)
print(flags[flags["tiny"] | flags["thin"] | (flags["repeated_points"] > 0)])
```

The area and compactness flags apply to polygon layers. A long strip of land or a road
parcel can be thin and legitimate; a thin polygon along a neighbor is more likely a sliver.
Validity is evaluated in 2D: Z values (for example on BD TOPO buildings) are not checked.

Compare the geometry type declared by the layer with the actual types:

```python
print(gpd.list_layers("input.gpkg"))  # declared geometry_type per layer
print(gdf.geom_type.value_counts(dropna=False))
```

A Polygon layer that holds MultiPolygons or collections is not conformant, even if the
driver accepted the write with a warning. GeoJSON (RFC 7946) expects counterclockwise
exterior rings; `gdf.orient_polygons()` (GeoPandas ≥ 1.1) fixes the orientation without
changing validity.

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

With GDAL ≥ 3.12, audit validity without Python. The output holds one point per invalid
feature, with the GEOS reason in an `error` field:

```bash
gdal vector check-geometry --include-field id input.gpkg validity_errors.gpkg
```

When discarding lower-dimensional collection parts fits the requested output, repair
while writing a new GeoPackage:

```bash
ogr2ogr -f GPKG repaired.gpkg input.gpkg -makevalid -nlt PROMOTE_TO_MULTI
```

`ogr2ogr -makevalid` calls `MakeValid()` and then removes lower-dimensional components
from collections. A polygon with a collapsed spike may lose its LineString component;
`-nlt PROMOTE_TO_MULTI` does not prevent that loss or turn collapsed lines into polygons.
Check that the output layer schema accepts the resulting geometry types; a driver warning
about inserting a GeometryCollection into a Polygon layer is not a conformant export.

With GDAL ≥ 3.12, keep those components for review in a layer that accepts any geometry
type:

```bash
gdal vector pipeline read input.gpkg ! make-valid --keep-lower-dim \
  ! set-geom-type --layer-only --geometry-type GEOMETRY ! write repaired_review.gpkg
```

`gdal vector make-valid` also takes `--method structure`. Without `set-geom-type`, it
writes MultiPolygons and collections into the Polygon layer of the input, with the same
warning.

Reopen the result and inspect geometry types, empties, feature counts and components.
See the official [ogr2ogr documentation](https://gdal.org/en/stable/programs/ogr2ogr.html#cmdoption-ogr2ogr-makevalid)
and [`gdal vector make-valid`](https://gdal.org/en/stable/programs/gdal_vector_make_valid.html).

## Topology between features

`is_valid` checks each feature independently. Gaps, overlaps and unmatched shared edges
between polygons are covered in [coverage-topology.md](coverage-topology.md).
