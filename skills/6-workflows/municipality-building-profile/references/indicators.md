# Indicator definitions and reconciliation

The helper treats source objects as buildings only to the extent supported by their
source definition. Distinct objects can represent parts of one physical building.

| Indicator | Definition |
| --- | --- |
| Municipality area | Area of the selected municipal polygon in the analysis CRS, including its holes. |
| Building count | Unique source IDs with strictly positive intersection area. A boundary touch alone does not count. |
| Footprint area | Area of the union of all selected footprints clipped to the municipality. |
| Observed footprint share | 100 × union footprint area / municipality area. Full-inventory interpretation requires complete input coverage. |
| Overlap excess | Sum of clipped object areas minus their union area. This is repeated area counting, not necessarily an input defect. |
| Height summary | Unweighted min, mean, median, linear 25th/75th quantiles and max of usable metre heights of selected whole objects. |
| Usage distribution | Counts and percentages of the selected usage field, including a missing category; denominator is all selected objects. |

No geometry repair or silent deduplication occurs. Duplicate IDs fail. Identical geometry
with different IDs is flagged; it can indicate duplicate records or distinct source
objects. Investigate before interpreting the count. The union prevents overlap from
inflating area without erasing source IDs from the audit.

The positive-area rule includes a building even when most of it is outside the boundary.
Report crossing IDs. Such counts are **not additive across neighboring municipalities**;
for exclusive assignment across several zones use `spatial-aggregation` with an explicitly
chosen policy. Heights/usages remain whole-object attributes, not fractions apportioned
by clipped area. Crossing detection compares outside area against max(1e-8 m², original
object area × 1e-10) to avoid reporting numerical noise as a crossing.

All geometry calculations are planar and two-dimensional; Z is discarded in derived
footprints, never used as building height. Holes and multipart polygons are preserved.
See the [Shapely manual](https://shapely.readthedocs.io/en/stable/manual.html#spatial-analysis-methods)
for intersection/union and [GeoPandas reprojection](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_crs.html)
for coordinate transforms. Assigning a CRS is not reprojection.

## Checks

- Input count = selected + touch-only + outside. These groups are disjoint.
- Every selected ID appears once in the output; municipality ID remains a string.
- 0 ≤ union area ≤ sum of clipped areas, and union area ≤ municipality area.
- Height valid + missing + sentinel + invalid = selected count; no valid heights means
  null statistics, not zero. Usage counts sum to selected count.
- Empty building input produces count/area/share zero, null height statistics and an
  empty usage distribution when requested. Keep the municipality layer and report the
  empty-input warning. Only established complete coverage permits an absence claim.
- Missing/unverified optional fields remain uncomputed; no default height, usage,
  inhabitants or dwelling count fills the gap.

Check geometry placement and representative magnitudes independently. A technically
valid but displaced layer can still produce an implausible all-zero portrait.
