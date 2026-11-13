# mapshaper-simplify

**Family:** [5. Represent and publish](../README.md).

Simplify administrative polygons for cartographic display and smaller web-map files,
keeping shared borders consistent. Includes percentage-based and metric-distance recipes,
GeoJSON/TopoJSON exports, and checks for feature loss and geometric changes.

## When to use it

- Reduce the vertices and file size of administrative boundaries for a web map.
- Simplify with a retained percentage or a distance tolerance in metres.
- Keep small polygon features, such as islands, from disappearing altogether.
- Compare several retention levels by file size, vertices, areas and retained islands.
- Export simplified neighboring layers as TopoJSON with shared arcs, or as WGS84 GeoJSON.

## When to use another skill

- Repair self-intersections or other invalid geometries without reducing detail:
  [`vector-data-quality`](../../3-prepare/vector-data-quality/README.md).
- Reduce the resolution of a raster, such as a 1 m elevation model resampled to 10 m:
  [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md).

## What you get

- A new simplified file at an unused path: WGS84 GeoJSON from the percentage and metric
  recipes, TopoJSON with shared arcs for several input files, or a Shapefile kept in a
  projected CRS. Source files stay unchanged.
- Before reporting, the agent reopens the output and compares it with the source: nonzero
  feature count, unchanged identifiers and properties, valid nonempty polygons, expected
  CRS and plausible bounds, area compared in a projected CRS (never square degrees), and
  coincident common borders without new gaps or overlaps.
- Measured vertex and file-size reductions, per-unit area changes, and multipart or hole
  losses, with failed checks, warnings and checks not performed reported separately.
  `-info` alone is not a validity or coverage check; GeoPandas/Shapely is used when available.

Simplification changes geometry and area. `keep-shapes` does not preserve every island
or hole, and a retained percentage is not a positional accuracy guarantee. When checks
fail, the agent reduces simplification or investigates the source; it does not add
`-clean`, snapping, coordinate rounding, `no-topology` or `no-repair` to make a run pass.

## Requirements

- Mapshaper CLI and Node.js. Automated command tests use Mapshaper 0.7.83 with Node.js 22;
  this Mapshaper version requires Node.js ≥ 20.11.0. Check with `node --version`.
- Optional GeoPandas ≥ 1.0 and Shapely ≥ 2.0 for the detailed validation example and tests.
- No network service or API key: the skill works on local files.

With compatible Node.js already installed, the **user** can install Mapshaper:

```bash
npm install --global mapshaper@0.7.83
mapshaper -version
```

The agent checks availability and never installs software itself, including through an
auto-installing `npx` call. The [browser application](https://mapshaper.org/) is an
alternative for manual previews.

## Installation

```bash
npx skills add ignfab/geoskills --skill mapshaper-simplify
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/5-publish`.

## Example

> Lighten the boundaries in data/admin_units_synthetic.geojson with Mapshaper for a web
> map, keeping 20% of removable vertices. Keep the three features and their identifiers,
> keep the shared borders and write to output/units.geojson.

```bash
mapshaper units.geojson \
  -simplify 20% weighted keep-shapes \
  -proj wgs84 \
  -o format=geojson units-simplified.geojson
```

Other example uses:

- Prepare an ADMIN EXPRESS extract for a web map: download the required neighboring
  units with `geopf-wfs-download`, audit them with `vector-data-quality`, then simplify
  the display layer while preserving identifiers for joins to statistical data.
- Compare 50%, 20% and 5% retention at the intended display scale. Generate each variant
  from the same original dataset and report vertices, file bytes, per-unit area changes
  and lost parts or holes before choosing the tradeoff.
- Export neighboring layers together as TopoJSON so shared borders use common arcs,
  or as WGS84 GeoJSON for a viewer that expects independent features.

Keep the original geometry for measurements and spatial analysis; join computed results
to the simplified display layer by identifier. Simplification does not create vector tiles
or provide different detail levels automatically.

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Inspection, two simplification recipes and output validation. |
| [references/simplification.md](references/simplification.md) | Shared topology across files, format choices, multipart limitations and a Python validation example. |

## Tests

[Scenarios](../../../tests/mapshaper-simplify.md): French agent prompts and expected
behavior, 4 positive + 2 negative. [Automated tests](../../../tests/test_mapshaper.py): real
CLI runs on synthetic polygons (offline); there is no live test.

## Related skills

- [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md) downloads the
  neighboring administrative units to simplify together.
- [`vector-data-quality`](../../3-prepare/vector-data-quality/README.md) audits the source
  geometries before simplification.
- [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md) helps choose
  a suitable metric CRS for a distance tolerance.
- [`map-illustration`](../map-illustration/README.md) renders a static or interactive map of
  the simplified layer.
