# municipality-building-profile

**Family:** [6. Solve a business need](../README.md).

The first business workflow in geoskills: a reproducible building portrait for one
municipality, from local inputs or bounded IGN extraction to indicators and optional QGIS.
It owns building selection, the common statistical population and reconciliation
across stages, and delivers a GeoPackage, an indicator CSV, a Markdown report and an audit.

## When to use it

- Build a building portrait of one municipality from local boundary and building files,
  or from whole building polygons retrieved from the Géoplateforme WFS.
- Count buildings, measure the built-up footprint and share without counting overlaps
  twice, and summarize heights and usages for the same buildings.
- Add a styled, portable QGIS project to the portrait.
- Deliver the indicators the data support when extract coverage or field definitions are
  unknown, and state the limits.

## When to use another skill

- Download buildings only, without indicators or a portrait:
  [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md).
- Statistics on one table, without a municipal boundary:
  [`geospatial-descriptive-statistics`](../../4-analyze/geospatial-descriptive-statistics/README.md).
- Indicators for several zones, or exclusive assignment of objects across zones:
  [`spatial-aggregation`](../../4-analyze/spatial-aggregation/README.md).
- Assemble existing layers into a QGIS project without computing indicators:
  [`qgis-project-builder`](../../5-publish/qgis-project-builder/README.md).
- Generic overlays: [`geopandas-vector-analysis`](../../4-analyze/geopandas-vector-analysis/README.md).

## What you get

The core output is `profile.gpkg`, `indicators.csv`, `audit.json`, `report.md` and a
`qgis-project.json` handoff. It counts source objects whose whole footprints intersect
the municipality over a positive area. Coverage uses the union of clipped footprints;
heights and usage frequencies use the same object population. Inputs remain unchanged.
No inhabitants, dwellings, floor areas or volumes are inferred. No multi-municipality
allocation, automatic geometry repair or population redistribution is included.

- `profile.gpkg` holds the `municipality` (one feature with its indicators), clipped
  `buildings` and union `footprint` layers in the declared metric CRS. `qgis-project.json`
  is a manifest for `qgis-project-builder`, not a QGIS project.
- Indicators: municipality area, building count, union footprint area, observed footprint
  share, overlap excess, unweighted height summary (min, mean, median, quartiles, max) and
  usage distribution with a missing category.
- Checks before reporting: selected + touch-only + outside objects reconcile with the
  input count; height status and usage counts reconcile with the selected count; union
  area ≤ summed clipped areas and ≤ municipality area; coverage lies in [0, 100]. The
  helper reopens every layer and the CSV/JSON and checks input hashes.
- Input coverage is recorded as `complete`, `partial` or `unknown`. A partial extract stays
  partial after file validation, and zero observed buildings does not prove absence.
  Unverified height or usage fields stay uncomputed. A QGIS project is reported as
  validated only after it was reopened and the full bundle relocated.

## Requirements

- GeoPandas ≥ 1.0, Shapely ≥ 2 and Pyogrio. Check with
  `python3 -c "import geopandas, pandas, shapely, pyogrio; print(geopandas.__version__)"`.
  The user can prepare an environment with `python3 -m pip install 'geopandas>=1.0,<2' pyogrio`.
- Online acquisition also needs GDAL/OGR (`ogrinfo`, `ogr2ogr`) and curl
  (`sudo apt install gdal-bin curl` on Debian/Ubuntu). It queries the public Géoplateforme
  WFS at `https://data.geopf.fr/wfs/ows`; the documented requests carry no API key. Local
  inputs need no network.
- Optional projects need existing QGIS/PyQGIS 3.34–3.x.

Agents never install software or run interactive setup; a missing tool is a reported limitation.

## Installation

```bash
npx skills add ignfab/geoskills --skill municipality-building-profile
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/6-workflows`.

## Example

> Build the building portrait of the fictitious municipality 00001 with the files and rules
> described in `data/building_profile_input.json`. Give the number of buildings, the
> built-up area without counting overlaps twice, the share of the territory that is built
> up, the heights and the usages. Save the data and reports in `output/portrait/`, without
> network access.

```bash
python3 scripts/build_profile.py profile-input.json output/building-profile
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Task routing, stages and result checks. |
| [scripts/build_profile.py](scripts/build_profile.py) | Deterministic local indicator and bundle builder. |
| [references/acquisition.md](references/acquisition.md) | Local-first routing and bounded WFS extraction. |
| [references/manifest.md](references/manifest.md) | Input manifest: discovered fields, source semantics and completeness. |
| [references/indicators.md](references/indicators.md) | Indicator definitions, boundary and overlap rules, empty inputs and reconciliation. |
| [references/delivery.md](references/delivery.md) | Output files, artifact checks and optional QGIS handoff. |

## Tests

[Scenarios](../../../tests/municipality-building-profile.md): French agent prompts,
3 positive + 3 negative. [test_municipality_building_profile.py](../../../tests/test_municipality_building_profile.py)
checks the helper against independent area and count oracles (GeoPandas, offline); no live test.

## Related skills

Each remains independently installable.

- [`geopf-service-selection`](../../1-discover/geopf-service-selection/README.md) and
  [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md) handle discovery and
  extraction; [`geopf-file-download`](../../2-access/geopf-file-download/README.md)
  provides dated deliveries when an exact historical edition is needed.
- [`geodata-intake`](../../3-prepare/geodata-intake/README.md) and
  [`vector-data-quality`](../../3-prepare/vector-data-quality/README.md) inspect inputs;
  [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md) helps choose
  the projected metre CRS.
- [`bdtopo-schema-guide`](../../1-discover/bdtopo-schema-guide/README.md) explains supported
  versions and fields, including height special values.
- [`geospatial-descriptive-statistics`](../../4-analyze/geospatial-descriptive-statistics/README.md)
  adds further distributions.
- [`qgis-layer-styling`](../../5-publish/qgis-layer-styling/README.md) and
  [`qgis-project-builder`](../../5-publish/qgis-project-builder/README.md) supply optional
  cartographic delivery.
