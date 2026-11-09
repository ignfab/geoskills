# Polygon coverage: gaps and overlaps

A coverage is a set of polygons meant to tile an area without overlapping: communes,
cadastral parcels, land-cover classes. Each polygon can be valid while the set is not.
Repair per-feature validity first (see [geometry-validity.md](geometry-validity.md)): the
checks below expect valid polygons. Work in a projected CRS, because widths and areas are
in CRS units.

## Check the coverage

GeoPandas ≥ 1.1 with Shapely ≥ 2.1:

```python
edges = gdf.geometry.invalid_coverage_edges()
flagged = gdf.loc[~edges.is_empty, ["id"]].assign(invalid_edges=edges[~edges.is_empty])
print(gdf.geometry.is_valid_coverage(), len(flagged))
```

A coverage is valid when no two polygons overlap and every shared edge has the same
vertices on both sides. Polygons digitized or clipped separately often fail the second
rule without any visible overlap: report those as unmatched edges, not as overlaps.
Features without an invalid edge get an empty geometry, hence the `is_empty` filter.

For example, on 2026-10-28 the 47 ADMIN EXPRESS communes of Val-de-Marne formed a valid
coverage. The 187 Parcellaire Express parcels of a small area of Saint-Mandé were all
valid, but three of them had invalid edges and one pair overlapped by 0.04 m². Data
updates change such results.

## Find overlapping pairs

This also works with GeoPandas 1.0. Measure each pair once and keep an explicit tolerance:

```python
import pandas as pd

left, right = gdf.sindex.query(gdf.geometry, predicate="intersects")
once = left < right
left, right = left[once], right[once]
overlap_area = (gdf.geometry.iloc[left]
                .intersection(gdf.geometry.iloc[right], align=False).area.to_numpy())
pairs = pd.DataFrame({"left_id": gdf["id"].iloc[left].to_numpy(),
                      "right_id": gdf["id"].iloc[right].to_numpy(),
                      "overlap_area": overlap_area})
overlaps = pairs[pairs["overlap_area"] > 0.01]  # m²
print(overlaps)
```

Neighbors that only share an edge have an overlap area of zero. The tolerance separates
digitizing noise from real overlaps; state it in the report.

## Find gaps

Enclosed gaps are holes of the union that no polygon fills:

```python
import geopandas as gpd
from shapely.geometry import Polygon

union = gdf.geometry.union_all()
parts = getattr(union, "geoms", [union])
holes = gpd.GeoSeries([Polygon(ring) for part in parts for ring in part.interiors],
                      crs=gdf.crs)
print(len(holes), holes.area.sum())
```

A hole can be legitimate: a lake, or an area outside the scope of the dataset. A gap open
to the outside, such as a thin strip between two neighbors on the edge of the coverage,
is not a hole. Detect gaps narrower than a given width:

```python
narrow = gdf.geometry.invalid_coverage_edges(gap_width=0.1)  # 10 cm in a metre CRS
print(gdf.loc[~narrow.is_empty, "id"].tolist())
```

With `gap_width`, the result also contains the overlaps and unmatched edges. It also
contains the outer edge of any feature thinner than `gap_width` on the boundary of the
coverage, such as a sliver. Inspect each flagged edge before calling it a gap.

## GDAL command line

With GDAL ≥ 3.12:

```bash
gdal vector check-coverage --maximum-gap-width 0.1 input.gpkg coverage_errors.gpkg
```

The output holds the invalid edges as lines, the same edges as `invalid_coverage_edges`,
without the source attributes. Join them back to the features spatially.

## Repair policy

Do not repair a coverage automatically. Each overlap or gap needs a rule: which neighbor
keeps the disputed area, and which width counts as a digitizing error. Ask the user when
the data contract does not say.

`gdal vector clean-coverage` (GDAL ≥ 3.12) snaps vertices and assigns overlaps and gaps
to a neighbor (`--snapping-distance`, `--merge-strategy`, `--maximum-gap-width`). Use it
only with an explicit rule, write a new file, and compare identifiers and per-feature areas
with the source: with the default strategy, the whole overlap goes to one of the two
neighbors. To simplify a coverage while keeping shared edges, use `mapshaper-simplify`.

See the official [`gdal vector check-coverage`](https://gdal.org/en/stable/programs/gdal_vector_check_coverage.html)
and [`gdal vector clean-coverage`](https://gdal.org/en/stable/programs/gdal_vector_clean_coverage.html)
documentation.
