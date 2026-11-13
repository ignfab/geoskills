# Spatial operations

All the operations below require the layers to share the same CRS: align them first with
`b = b.to_crs(a.crs)`. Keep a suitable existing/requested CRS. For planar measurements,
choose `metric_crs` for the territory and accuracy, then inspect its linear units.
EPSG:2154 is only a fallback for suitable metropolitan-France tasks; local joins do not
require it. The recipes below also accept custom CRS definitions and convert linear units.

## Spatial join

Attach the attributes of the polygon containing each point:

```python
joined = gpd.sjoin(points, communes[["code_insee", "nom_officiel", "geometry"]],
                   predicate="within", how="left")
```

- `predicate`: `intersects` (default), `within`, `contains`, `overlaps`, `touches`, …
- `how="left"` keeps unmatched features (attributes become `NaN`); `"inner"` drops them.
- With an unnamed right index, its values arrive as `index_right`; a named index keeps
  its name. Inspect the columns before another join to avoid index-name collisions.
- `within` excludes points exactly on the polygon boundary. Use `covered_by` when those
  points should match; overlapping polygons or shared boundaries can produce several
  rows per point. Check multiplicity before aggregating.

Nearest-neighbour join with distance:

```python
if not points.crs.is_projected or points.crs != gares.crs:
    raise ValueError('Align both layers in a suitable projected CRS first')
nearest = gpd.sjoin_nearest(points, gares, how="left", distance_col="dist_crs_units")
nearest['dist_m'] = nearest['dist_crs_units'] * points.crs.axis_info[0].unit_conversion_factor
```

`distance_col` is in CRS units — metres in EPSG:2154, **degrees** in EPSG:4326.

## Overlay

Geometric combination of two polygon layers (geometries are cut):

```python
inter = gpd.overlay(zones, communes, how="intersection")
diff  = gpd.overlay(zones, communes, how="difference")
union = gpd.overlay(zones, communes, how="union")
```

`sjoin` answers "which features relate?" (geometries unchanged); `overlay` computes the new
geometries.

## Clip

Cut a layer to a boundary (faster than `overlay` for a simple mask):

```python
clipped = gpd.clip(batiments, commune)
```

## Buffer

```python
measured = gdf.to_crs(metric_crs)
if not measured.crs.is_projected:
    raise ValueError('Choose a suitable projected analysis CRS')
metres_per_unit = measured.crs.axis_info[0].unit_conversion_factor
zone_100m = measured.buffer(100 / metres_per_unit)  # GeoSeries of polygons
```

Calling `.buffer()` on a layer in EPSG:4326 buffers in **degrees** and triggers
`UserWarning: Geometry is in a geographic CRS`. Reproject first.

`buffer` returns a GeoSeries; to keep the attributes, assign it back:

```python
tampon = measured.copy()
tampon["geometry"] = zone_100m
```

## Dissolve

Merge features by attribute (the vector equivalent of GROUP BY):

```python
departements = communes.dissolve(by="code_dept", aggfunc={"population": "sum"})
```

Without `by`, everything merges into a single feature.

## Explode

Split multi-part geometries into single parts:

```python
parts = gdf.explode(index_parts=False)
```

## Areas, lengths, centroids

```python
measured = gdf.to_crs(metric_crs)
if not measured.crs.is_projected:
    raise ValueError('Choose a suitable projected analysis CRS')
metres_per_unit = measured.crs.axis_info[0].unit_conversion_factor
measured["surface_m2"] = measured.area * metres_per_unit ** 2
measured["perimetre_m"] = measured.length * metres_per_unit
centres = measured.centroid
```

These planar operations need a justified projection; an arbitrary projected CRS is not
proof of measurement accuracy. Require two horizontal axes with the same known positive
unit conversion. For unsuitable large/global extents use a justified geodesic method.
