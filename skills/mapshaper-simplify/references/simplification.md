# Shared topology, formats and validation

## Adjacent polygons and multiple files

Mapshaper identifies coincident input edges and represents them with shared arcs. A shared
arc is simplified once, keeping both sides consistent. Import neighboring units together;
simplifying each unit in a separate run can produce gaps and overlaps.

When neighboring units arrive in multiple files with the same known CRS, combine them
into a dataset with separate layers and shared topology:

```bash
mapshaper -i west.geojson east.geojson combine-files \
  -simplify 20% weighted keep-shapes \
  -proj wgs84 \
  -o target=* format=topojson no-quantization units-simplified.topojson
```

`-simplify` operates across polygon/polyline layers in that dataset. Inspect the layer
names with `-info`; `target=*` exports all layers. Separate files processed in batch mode
do not share topology. Slightly mismatched boundaries are not automatically identical:
diagnose source gaps or overlaps before considering any repair or snapping tolerance.

Do not use `no-topology` for this workflow. Leave the simplifier's intersection repair
enabled; `no-repair` disables it. `-clean` is a separate geometry-changing operation, not
mandatory preparation. Review changes to area and coverage if repair is required.

## Choose the output format deliberately

- **GeoJSON** is convenient for web maps. Explicitly run `-proj wgs84` for standard
  longitude/latitude output. Preserve original properties and string identifiers.
- **TopoJSON** stores shared arcs once. The example uses `no-quantization` to avoid an
  additional rounding step while assessing simplification. Default quantization may make
  delivery files smaller, but changes coordinates: validate that export separately.
- **Shapefile** can retain a projected CRS: omit the final WGS84 transformation and use
  `-o format=shapefile units-100m.shp`. Keep all sidecars, including `.prj`, together.
  Account for field-name/type limits. Mapshaper's Shapefile workflow discards Z/M values;
  do not use it when preserving those dimensions is required.

Avoid `-o force` and output paths that already exist. Do not add `precision=` just to
shrink files: rounding can collapse small features or invalidate them independently of
simplification. Record method, percentage/interval, working CRS and export options.

## Inspect geometric changes

This optional example needs existing GeoPandas/Shapely. Discover the actual identifier
field and suitable metric CRS first; `unit_id` and EPSG:2154 below are example choices.
The example assumes one unique identifier per feature and inputs with known CRS.

```python
from pathlib import Path

import geopandas as gpd
from pandas.testing import assert_frame_equal
from shapely import get_num_coordinates

source_path = Path("units.geojson")
result_path = Path("units-simplified.geojson")
source = gpd.read_file(source_path)
result = gpd.read_file(result_path)
assert source.crs is not None and result.crs is not None
assert result.crs.to_epsg() == 4326
assert len(result) == len(source) > 0
assert source["unit_id"].notna().all() and source["unit_id"].is_unique
assert result["unit_id"].notna().all() and result["unit_id"].is_unique
assert set(result["unit_id"]) == set(source["unit_id"])
assert not result.geometry.isna().any()
assert not result.geometry.is_empty.any()
assert result.geometry.is_valid.all()
assert result.geom_type.isin(["Polygon", "MultiPolygon"]).all()

before = source.set_index("unit_id").sort_index().to_crs(2154)
after = result.set_index("unit_id").sort_index().to_crs(2154)
assert_frame_equal(
    before.drop(columns=before.geometry.name),
    after.drop(columns=after.geometry.name),
    check_like=True, check_dtype=False, check_exact=True,
)
assert before.geometry.is_valid.all() and (before.area > 0).all()
print("Bounds before/after:", before.total_bounds, after.total_bounds)
vertices_before = int(get_num_coordinates(before.geometry).sum())
vertices_after = int(get_num_coordinates(after.geometry).sum())
bytes_before, bytes_after = source_path.stat().st_size, result_path.stat().st_size
print("Vertices before/after:", vertices_before, vertices_after)
print("Vertex reduction (%):", 100 * (1 - vertices_after / vertices_before))
print("File bytes before/after:", bytes_before, bytes_after)
print("File-size reduction (%):", 100 * (1 - bytes_after / bytes_before))
print("Area change (%):", 100 * (after.area - before.area) / before.area)

def parts_and_holes(geometry):
    parts = list(geometry.geoms) if geometry.geom_type == "MultiPolygon" else [geometry]
    return len(parts), sum(len(part.interiors) for part in parts)

print("Parts/holes before:", before.geometry.map(parts_and_holes).to_dict())
print("Parts/holes after:", after.geometry.map(parts_and_holes).to_dict())
```

The attribute comparison ignores column order and reader-inferred dtype differences,
but checks exact values, including string identifiers. The vertex totals count ring
closures and shared coordinates in each polygon; they are not Mapshaper's percentage of
removable arc vertices. File-size changes also depend on formatting and output format,
so fewer vertices do not guarantee a smaller file. Compare equivalent encodings when
choosing a delivery format.

Inspect originally adjacent pairs: their boundary intersection should remain a line,
without new overlaps or gaps. For large coverages,
use a spatial index rather than all pairs. Individual polygon validity does not establish
coverage validity. Evaluate changes relative to source quality and the intended scale;
there is no universal acceptable area-loss percentage. If the dataset includes all of
France, partition by suitable regional CRSs before measuring areas or distances.

For multipart features, `keep-shapes` protects only the part with the largest original
bounding box. Raise the retained percentage or reduce the distance interval when required
islands or holes disappear. Exact cadastral measurement generally requires the original
geometry rather than a generalized display layer.

## Sources

- [Official topology guide](https://mapshaper.org/docs/guides/topology.html).
- [Official command reference](https://mapshaper.org/docs/reference.html).
- [Official GeoJSON guide](https://mapshaper.org/docs/formats/geojson.html).
