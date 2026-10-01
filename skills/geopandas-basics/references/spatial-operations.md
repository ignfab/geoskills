# Spatial operations

All the operations below require the layers to share the same CRS: align them first with
`b = b.to_crs(a.crs)`. For buffers and areas, use a projected CRS (metres), e.g. EPSG:2154.

## Spatial join

Attach the attributes of the polygon containing each point:

```python
joined = gpd.sjoin(points, communes[["code_insee", "nom", "geometry"]],
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
nearest = gpd.sjoin_nearest(points, gares, how="left", distance_col="dist_m")
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
gdf_l93 = gdf.to_crs(2154)          # metres — NOT degrees
zone_100m = gdf_l93.buffer(100)     # GeoSeries of polygons
```

Calling `.buffer()` on a layer in EPSG:4326 buffers in **degrees** and triggers
`UserWarning: Geometry is in a geographic CRS`. Reproject first.

`buffer` returns a GeoSeries; to keep the attributes, assign it back:

```python
tampon = gdf_l93.copy()
tampon["geometry"] = tampon.buffer(100)
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
gdf_l93 = gdf.to_crs(2154)
gdf_l93["surface_m2"] = gdf_l93.area
gdf_l93["perimetre_m"] = gdf_l93.length
centres = gdf_l93.centroid
```

All in CRS units — reproject to EPSG:2154 first, same warning as `buffer` otherwise.
