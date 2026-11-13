# Geometry measurements

Inspect declared CRS, geometry types, missing/empty/invalid geometries and coverage first.
Do not repair geometry silently; use `vector-data-quality` if repair is requested. Stop
metric calculations when CRS is unknown. `set_crs` assigns a known CRS; it does not transform.

For mainland France a suitably covered Lambert-93 dataset can use EPSG:2154; overseas and
large/global datasets need a justified local/equal-area/geodesic method. Do not default to
Web Mercator for area. Explain projection distortion and whether a length is a polygon
perimeter or a line length. Areas are planar 2D, not roof or terrain surface area.

After choosing `metric_crs` from metadata and the task extent:

```python
import math
if gdf.crs is None or gdf.geometry.isna().any() or gdf.geometry.is_empty.any():
    raise ValueError('Known CRS and nonempty geometries are required')
if not gdf.geometry.is_valid.all():
    raise ValueError('Repair requires a separate explicit decision')
measured = gdf.to_crs(metric_crs).copy()
axes = measured.crs.axis_info[:2]
if (not measured.crs.is_projected or len(axes) != 2
        or any(not math.isfinite(a.unit_conversion_factor) or a.unit_conversion_factor <= 0 for a in axes)
        or not math.isclose(axes[0].unit_conversion_factor, axes[1].unit_conversion_factor, rel_tol=1e-12)):
    raise ValueError('Choose a suitable projected CRS with known compatible linear units')
if not measured.geom_type.isin(['Polygon', 'MultiPolygon']).all():
    raise ValueError('Area requires polygon features')
if 'area_m2' in measured:
    raise ValueError('Use an unused derived-field name')
measured['area_m2'] = measured.area * axes[0].unit_conversion_factor ** 2
```

Summarize the derived column in memory with `summarize(..., units={'area_m2': 'm²'})`;
record source CRS and calculation CRS in the source metadata/report. A 10 m square must
have area 100 m². Never label square degrees as m². Do not write back to the source.
