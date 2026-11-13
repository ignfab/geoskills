# terrain-elevation-screening

**Family:** [6. Solve a business need](../README.md).

A business workflow that finds the parts of an area of interest meeting terrain elevation
thresholds, with optional slope and minimum connected area filters. From a supplied or
discovered DEM, it produces an elevation raster, a selection mask, candidate polygons and
a report of thresholds, coverage and limitations. It owns the common extent, grid,
vertical reference and missing-data rules across acquisition, filtering and delivery.

## When to use it

- Find the zones of an area above, below or between altitude limits, for example 0 to
  100 m inclusive, from a local DEM and AOI.
- Prepare a preliminary helicopter landing-site terrain screen with the user's own
  altitude, slope and minimum area criteria, and list what remains to be checked.
- Show whether any terrain meets the thresholds, keeping "no qualifying zone" distinct
  from missing data.
- Discover and acquire a terrain model covering the AOI when none is supplied, then screen
  it on one common metric grid.

## When to use another skill

- Ground elevation at a few points or along a profile:
  [`geopf-altimetry`](../../4-analyze/geopf-altimetry/README.md).
- Raster clipping or conversion alone, without thresholds or zone search:
  [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md).

Obstacle heights, height above ground, aircraft performance and landing authorization are
outside this skill: a terrain DEM does not establish them.

## What you get

- In a new output directory: `elevation.tif` (clipped elevations, nodata `-9999`),
  `selection.tif` (`1` selected, `0` rejected, `255` unknown or outside the AOI),
  `slope.tif` only when a slope limit was requested, and `candidates.gpkg` (layer
  `candidates`, one polygon per part with `area_m2`), clipped to the exact AOI.
- A report of source, edition and access date, vertical reference, numeric criteria and
  comparison operators, resampling, coverage, cell counts and areas, and the checks actually
  performed. Inputs stay unchanged.
- Thresholds come only from the request: there is no default altitude or helicopter
  criterion. Cells touching only at a corner do not form one candidate, holes are kept and
  nodata is never filled or selected; zero and negative altitudes can be valid.
- Checks before reporting: rasters and GeoPackage reopened; projected CRS, identical
  raster grids, AOI extent, meter elevations, slope unit and mask codes verified. Selected,
  rejected and unknown cells reconcile with the AOI cell count (outside cells counted
  separately); the extra unknown border of a slope screen is reported on its own; polygons
  lie within the AOI and satisfy any area limit.
- An empty selection with valid coverage is a valid result (empty layer, CRS kept); an
  all-nodata AOI is reported as insufficient data. Criteria are never relaxed to get a
  result.
- Polygons are labeled terrain-screening candidates. The skill never calls a result safe,
  approved or suitable for landing, never presents pixel size as vertical accuracy, and
  never infers the absence of obstacles, a usable footprint or surface condition; these
  stay with the qualified pilot or operator using current site evidence.

## Requirements

- GDAL ≥ 3.3 with matching Python bindings and NumPy. Check with `gdalinfo --version`,
  `ogrinfo --version`, `gdaldem --help`, `gdal_calc.py --help` and
  `gdal_polygonize.py --help`. On Debian/Ubuntu the user can run
  `sudo apt install gdal-bin python3-gdal python3-numpy`.
- Online discovery also needs curl (`sudo apt install curl`). It reads the capabilities of
  the Géoplateforme download service at `https://data.geopf.fr/telechargement/capabilities`;
  local data need no network.
- QGIS is optional for a requested map, not required for the analytic result. Agents
  never install software or run interactive setup or login commands.

## Installation

```bash
npx skills add ignfab/geoskills --skill terrain-elevation-screening
```

The whole family installs with `npx skills add https://github.com/ignfab/geoskills/tree/main/skills/6-workflows`.

## Example

> With `data/terrain_screening.asc` and `data/terrain_screening_aoi.geojson`, find the
> zones with an altitude between 0 and 100 meters, bounds included. The metadata are in
> `data/README.md`. Provide the altitude raster, the mask, the polygons and a coverage
> summary in `output/terrain/`, without network access or changes to the sources.

Expected: 49 AOI cells, 48 valid elevations; the mask has 27 selected, 21 rejected and
1 unknown cell, for a selected area of 2,700 m². The elevation clip and altitude-only
mask of the local processing recipe, with `RES_M`, `Z_MIN_M` and `Z_MAX_M` set to the
verified cell size and the user's bounds:

```bash
export GDAL_PAM_ENABLED=NO
gdalwarp -cutline aoi_metric.gpkg -cl aoi -crop_to_cutline \
  -tr "$RES_M" "$RES_M" -tap -r near -ot Float32 -dstnodata -9999 \
  -co COMPRESS=DEFLATE dem_metric.tif elevation.tif
gdal_calc.py -A elevation.tif \
  --calc="(A >= $Z_MIN_M) & (A <= $Z_MAX_M)" \
  --type=Byte --NoDataValue=255 --co=COMPRESS=DEFLATE --outfile=selection.tif
```

The optional slope mask, candidate polygons and coverage checks follow in
[references/local-processing.md](references/local-processing.md).

## Contents

| File | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Screening definition, workflow, helicopter boundary and output checks. |
| [references/sources.md](references/sources.md) | Local-first DEM acquisition, terrain versus surface models, vertical references and the common metric grid. |
| [references/local-processing.md](references/local-processing.md) | GDAL recipes: clip, altitude and slope masks, candidate polygons, coverage checks. |
| [references/helicopter-handoff.md](references/helicopter-handoff.md) | What a terrain screen establishes and what remains for the pilot or operator. |

## Tests

- [French agent scenarios](../../../tests/terrain-elevation-screening.md): 3 positive + 2 negative.
- Offline: [test_terrain_elevation_screening.py](../../../tests/test_terrain_elevation_screening.py)
  runs the documented GDAL recipes on synthetic fixtures (inclusive bounds, slope, empty
  and all-nodata selections, negative elevations, holes, diagonal cells, clipping before
  the area filter). No live test.

## Related skills

Each is optional and independently installable; the local recipe works with GDAL alone.

- [`geopf-file-download`](../../2-access/geopf-file-download/README.md) retrieves DEM tiles;
  [`geopf-raster-download`](../../2-access/geopf-raster-download/README.md) obtains a verified
  numeric elevation extract for a small AOI.
- [`crs-reprojection-france`](../../3-prepare/crs-reprojection-france/README.md) chooses a
  projected meter CRS or a justified vertical conversion.
- [`gdal-raster-processing`](../../3-prepare/gdal-raster-processing/README.md) prepares one
  common grid when needed.
- [`qgis-layer-styling`](../../5-publish/qgis-layer-styling/README.md) and
  [`qgis-project-builder`](../../5-publish/qgis-project-builder/README.md) style and
  package a requested map of the results.
