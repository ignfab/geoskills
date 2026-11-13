# municipality-building-profile

**Family:** [6. Solve a business need](../README.md).

The first business workflow in geoskills: a reproducible building portrait for one
municipality, from local inputs or bounded IGN extraction to indicators and optional QGIS.

## Requirements

Python 3.10+, GeoPandas ≥ 1.0, Shapely ≥ 2 and Pyogrio. The user can prepare an environment
with `python3 -m pip install 'geopandas>=1.0,<2' pyogrio`; agents never install software.
Online acquisition also needs GDAL/OGR and curl (`sudo apt install gdal-bin curl` on
Debian/Ubuntu). Optional projects need existing QGIS/PyQGIS 3.34–3.x.

## Install

```bash
npx skills add ignfab/geoskills --skill municipality-building-profile
```

## Contents

- [SKILL.md](SKILL.md): task routing, stages and result checks.
- [build_profile.py](scripts/build_profile.py): deterministic local indicator and bundle builder.
- [Acquisition](references/acquisition.md), [manifest](references/manifest.md),
  [indicators](references/indicators.md) and [delivery](references/delivery.md).
- [French scenarios](../../../tests/municipality-building-profile.md).

The core output is `profile.gpkg`, `indicators.csv`, `audit.json`, `report.md` and a
`qgis-project.json` handoff. It counts source objects whose whole footprints intersect
the municipality over a positive area. Coverage uses the union of clipped footprints;
heights and usage frequencies use the same object population. Inputs remain unchanged.
No inhabitants, dwellings, floor areas or volumes are inferred. No multi-municipality
allocation, automatic geometry repair or population redistribution is included.

## Related skills

[geopf-wfs-download](../../2-access/geopf-wfs-download/README.md) handles extraction;
[bdtopo-schema-guide](../../1-discover/bdtopo-schema-guide/README.md) explains supported
versions and fields. [spatial-aggregation](../../4-analyze/spatial-aggregation/README.md)
handles generic object-to-zone policies; [geospatial-descriptive-statistics](../../4-analyze/geospatial-descriptive-statistics/README.md)
handles standalone distributions. [qgis-layer-styling](../../5-publish/qgis-layer-styling/README.md)
and [qgis-project-builder](../../5-publish/qgis-project-builder/README.md) supply optional
cartographic delivery. Each remains independently installable.
