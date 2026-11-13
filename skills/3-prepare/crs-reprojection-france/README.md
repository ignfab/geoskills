# crs-reprojection-france

**Family:** [3. Prepare and check](../README.md).

Choose the right coordinate reference system for French data (Lambert-93, CC zones, NTF,
the overseas UTM systems) and reproject vectors, rasters and points with GDAL, PROJ and
pyproj, without the usual pitfalls. The skill also converts GPS heights to NGF altitudes
and diagnoses a missing or incorrect projection before any CRS is assigned.

## When to use it

- Convert GPS points to Lambert-93 (EPSG:2154), flagging the points outside its area of
  use and proposing a suitable CRS for them, such as RGR92 / UTM 40S for Réunion.
- Convert legacy extended Lambert II (NTF, EPSG:27572) coordinates to Lambert-93 as
  accurately as possible, with the IGN grid.
- Fix a Shapefile without `.prj` that displays in the wrong place: confirm its CRS, assign
  it, then export to another CRS.
- Convert an ellipsoidal GPS height to an NGF-IGN69 altitude with the IGN geoid grid.
- Choose an EPSG code for mainland France, the CC42–CC50 conic zones or an overseas
  territory.
- Compute an area or a distance in a projected CRS rather than in degrees or Web Mercator.

## When to use another skill

- Resampling and nodata choices when reprojecting a raster:
  [`gdal-raster-processing`](../gdal-raster-processing/README.md).
- Invalid geometries, gaps or overlaps, when the CRS is not the problem:
  [`vector-data-quality`](../vector-data-quality/README.md).
- A first inventory of an unfamiliar delivery, before any CRS decision:
  [`geodata-intake`](../geodata-intake/README.md).
- A task that leaves coordinates untouched, such as sorting a CSV by name, needs no CRS
  work: the coordinates are copied unchanged.

## What you get

- Reprojected vector files (`ogr2ogr`), rasters (`gdalwarp`, with compression) or point
  coordinates (`gdaltransform`, `cs2cs`, pyproj), or, for advice-only requests, the
  recommended EPSG code and its evidence without invented files.
- A suspected CRS is confirmed from producer metadata or a known control point before it is
  assigned: coordinate ranges are clues, not proof. The skill distinguishes assigning a CRS
  (`-a_srs`) from reprojecting (`-t_srs`, or `-s_srs` with `-t_srs`).
- Before reporting, the agent transforms a control point with known coordinates (Notre-Dame
  de Paris: 2.3499, 48.8530 in EPSG:4326 gives 652296.97, 6861636.36 in EPSG:2154), checks
  the output extent against the usual ranges of the target CRS, and states the units.
- No area or distance computed in degrees or in EPSG:3857 is reported.
- For NTF and height transformations, the selected operation and grid availability are
  inspected: without the IGN grid, PROJ silently falls back to a less accurate
  transformation, and the agent reports the fallback or the missing grid instead of
  claiming centimetric accuracy or fabricating an altitude.
- A report with source, output path and format, CRS and units, extent, counts or raster
  dimensions, processing choices and checks, separating failed checks, warnings and checks
  not performed.

Preserve suitable requested/existing CRSs. Lambert-93 is a fallback for applicable
metropolitan-France tasks; other authority codes and custom WKT definitions remain valid.
This guide's French scope does not restrict the generic tools; see
[CRS handling](../../../docs/crs-handling.md).

## Requirements

Choose an existing route: GDAL for vector/raster files (`sudo apt install gdal-bin`),
PROJ for CLI coordinate operations (`sudo apt install proj-bin`), or pyproj for Python
points (`python3 -m pip install pyproj`). These user-run commands are alternatives by
task; metadata inspection may also use `projinfo`. The agent never installs software.

Accurate datum/altitude transformations may need grids: inspect the selected operation,
then download only its missing grid files, not the entire IGN collection or `proj-data`.
See [targeted downloads](references/pitfalls.md#3-ntf--rgf93-legacy-lambert-i-ii-iii-iv).

Check only the chosen route (`ogrinfo --version`, `gdalinfo --version`, `projinfo`, or a pyproj import). Network access is needed only for missing grids or online metadata; no API key is needed. Never run interactive setup.

## Installation

```bash
npx skills add ignfab/geoskills --skill crs-reprojection-france
```

The whole family installs with
`npx skills add https://github.com/ignfab/geoskills/tree/main/skills/3-prepare`.

## Example

> Convert the points in `data/points_gps.csv` to Lambert-93. Flag the points outside its
> area of use and propose a suitable system for those.

```bash
echo "2.3522 48.8566" | gdaltransform -s_srs EPSG:4326 -t_srs EPSG:2154
# 652469.02 6862035.26
```

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | EPSG codes for France, reprojection commands, sanity checks. |
| [references/pitfalls.md](references/pitfalls.md) | Axis order, assign versus reproject, NTF grids, RGF93 v2b, altitudes, Web Mercator. |
| [references/overseas.md](references/overseas.md) | Systems for each overseas territory: geographic, projected and vertical CRSs, legacy systems and multi-territory datasets. |

## Tests

- Agent scenarios: [tests/crs-reprojection-france.md](../../../tests/crs-reprojection-france.md),
  in French (5 positive, 1 negative).
- Offline: [test_workflows.py](../../../tests/test_workflows.py) checks axis order, overseas
  CRSs, the missing `.prj`, area, and NTF and vertical transformations with the IGN grids.
  No live test.

## Related skills

- [`geodata-intake`](../geodata-intake/README.md) reports a missing CRS before this skill
  confirms and assigns it.
- [`gdal-vector-processing`](../gdal-vector-processing/README.md) converts, filters and clips vector
  files once the CRS is settled.
- [`gdal-raster-processing`](../gdal-raster-processing/README.md) adds resampling, nodata and COG
  options to a raster reprojection.
- [`geopf-wfs-download`](../../2-access/geopf-wfs-download/README.md) downloads Géoplateforme
  layers, mostly served in EPSG:4326, whose CRS is checked with `ogrinfo -so` before
  filtering.
