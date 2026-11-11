# Predicates and geometry

With objects on the left and zones on the right,
[GeoPandas sjoin](https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin.html)
creates a row for each match. It does not itself enforce one zone per object.

| Choice | Consequence |
| --- | --- |
| `within` | Point on the zone boundary is unmatched; a crossing polygon is not wholly within either zone. |
| `intersects` | Touching boundaries count; neighboring or overlapping zones can match the same object. |
| `covered_by` | Includes objects wholly covered by the zone, including its boundary; inspect spatial-index support. |
| zone `covers` object | Reverse orientation of `covered_by`; do not silently swap the sjoin operands. |
| centroid/representative point | Changes the question to point-based assignment; requires an explicitly chosen method. |

The helper deliberately implements only `within` and `intersects`. For centroid assignment,
derive points in a suitable projected CRS in a separate in-memory copy, retain source IDs,
and record the transformation. A centroid may lie outside a concave polygon;
`representative_point()` lies inside but expresses a different rule. Do not substitute one
for the other without explaining the decision.

Known mismatched CRSs can be transformed; unknown CRS must be resolved first. Predicates
are planar, ignore height and do not require area calculation. Weighting does require
appropriate projected/equal-area units and a different, justified method.
