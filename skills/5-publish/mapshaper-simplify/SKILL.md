---
name: mapshaper-simplify
description: "Simplifies polygon boundaries with Mapshaper while preserving shared topology. Use when the user wants to reduce vertices or file size for administrative boundaries, choose a simplification percentage or distance tolerance, keep small polygon features, or export simplified GeoJSON or TopoJSON for a web map."
---

# Simplify polygons with Mapshaper

Simplify adjacent polygons together so their common borders remain coincident. This is
cartographic generalization: areas, holes and small islands can change. Use
`vector-data-quality` for geometry repair and `gdal-raster-basics` for raster processing.

## Prerequisites

- Existing **Mapshaper CLI** and a compatible **Node.js**. CI tests Mapshaper **0.7.83**
  with Node.js **22**; that Mapshaper release requires Node.js ≥ 20.11.0.
- Check `node --version` and `mapshaper -version`. If missing, give the user
  `npm install --global mapshaper@0.7.83` to run after setting up compatible Node.js.
  **Never install software yourself**, including through an auto-installing `npx` call.
- Do not start interactive installers or local GUI servers. The user can instead open
  [the browser application](https://mapshaper.org/) and import their files manually.

## Inspect the source

```bash
mapshaper units.geojson -info
mapshaper -h simplify
```

Discover the layer names, geometry types, fields, feature count, bounds and CRS. Keep
Shapefile `.shp`, `.shx`, `.dbf` and `.prj` together. Resolve missing or contradictory CRS
metadata from the producer before transforming; do not guess from coordinates alone.
Record identifiers (including leading zeros), multipart features and holes before editing.

Use all neighboring units in the same dataset. For several files, see
[shared topology and formats](references/simplification.md). Keep source files unchanged,
choose unused output paths and run commands in the foreground without truncating logs.

## Simplify by retained percentage

For a first preview, retain 20% of removable vertices using weighted Visvalingam:

```bash
mapshaper units.geojson \
  -simplify 20% weighted keep-shapes \
  -proj wgs84 \
  -o format=geojson units-simplified.geojson
```

Lower percentages remove more detail. The percentage is **not** a feature count, final
file-size ratio or distance tolerance. Compare previews at the intended map scale before
choosing a value. `weighted` is the default method, made explicit here.

`keep-shapes` protects a polygon feature from disappearing altogether. For multipart
features, it only guarantees retention of the part with the largest original bounding
box; other islands and holes may disappear. If every part must survive, compare part and
hole counts and use a less aggressive setting; do not promise preservation from this flag.

## Simplify with a metric tolerance

For data confirmed to be in **mainland France**, project to Lambert-93 and use
Douglas-Peucker with a 100 m tolerance, then export longitude/latitude GeoJSON:

```bash
mapshaper units.geojson \
  -proj EPSG:2154 \
  -simplify dp interval=100 keep-shapes \
  -proj wgs84 \
  -o format=geojson units-100m.geojson
```

Choose a suitable metric CRS for other regions; Lambert-93 is not an overseas CRS.
`dp` gives the distance-based criterion; a weighted Visvalingam interval does not express
the same error bound. Geographic input is simplified on a sphere by default. `planar`
does not reproject coordinates and would treat longitude/latitude as flat degree units.

## Validate the output

```bash
mapshaper units-simplified.geojson -info
```

Reopen the exported file and compare with the source:

- Nonzero feature count, unchanged identifiers and properties, valid and nonempty polygon
  geometries. Inspect multipart and hole losses separately, even with `keep-shapes`.
- Expected CRS and plausible bounds: the GeoJSON recipes output WGS84 longitude/latitude.
  Compare area in the same suitable projected CRS, never square degrees.
- Fewer vertices and measured output size; report the actual reduction. Compare per-unit
  area and boundary displacement against the user's accuracy requirement.
- Common borders still coincide; check for new gaps or overlaps and visually inspect
  small features at the intended map scale. A successful command or `-info` is not a
  geometry-validity or coverage check; use GeoPandas/Shapely when available.

If checks fail, reduce simplification or investigate source quality. Do not automatically
add `-clean`, snapping, coordinate rounding, `no-topology` or `no-repair` to make a run pass.
See the reference for a concrete validation snippet and export caveats.

## Report the result

Report the source and edition/access date when known, output path and format, CRS and
units, extent and counts (or raster dimensions), processing choices and checks performed.
Separate failed checks, warnings and checks not performed; keep unknown metadata explicit.
For advice-only requests, report the recommendation and its evidence without inventing files.

## References

- [Shared topology, export formats and validation](references/simplification.md).
- [Official simplification guide](https://mapshaper.org/docs/guides/simplification.html).
- [Official command reference](https://mapshaper.org/docs/reference.html).
- [Administrative-boundary example by mborne](https://mborne.github.io/outils/mapshaper/)
  — the motivating workflow for this skill.
