# mapshaper-simplify

Simplify administrative polygons for cartographic display and smaller web-map files,
keeping shared borders consistent. Includes percentage-based and metric-distance recipes,
GeoJSON/TopoJSON exports, and checks for feature loss and geometric changes.

## Example uses

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

## Requirements

- Mapshaper CLI and Node.js. Automated command tests use Mapshaper 0.7.83 with Node.js 22;
  this Mapshaper version requires Node.js ≥ 20.11.0.
- Optional GeoPandas ≥ 1.0 and Shapely ≥ 2.0 for the detailed validation example and tests.

With compatible Node.js already installed, the **user** can install Mapshaper:

```bash
npm install --global mapshaper@0.7.83
mapshaper -version
```

The agent checks availability and never installs software itself. The
[browser application](https://mapshaper.org/) is an alternative for manual previews.

## Install the skill

```bash
npx skills add ignfab/geoskills --skill mapshaper-simplify
```

## Contents

- [SKILL.md](SKILL.md): inspection, two simplification recipes and output validation.
- [references/simplification.md](references/simplification.md): shared topology across
  files, format choices, multipart limitations and a Python validation example.
- [Manual scenarios](../../tests/mapshaper-simplify.md): French prompts and expected behavior.
- [Automated tests](../../tests/test_mapshaper.py): real CLI runs on synthetic polygons.

Simplification changes geometry and area. `keep-shapes` does not preserve every island
or hole, and a retained percentage is not a positional accuracy guarantee.
