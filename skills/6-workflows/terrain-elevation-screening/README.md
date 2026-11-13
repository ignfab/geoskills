# terrain-elevation-screening

**Family:** [6. Solve a business need](../README.md).

A business workflow for finding parts of an area that meet terrain elevation thresholds,
with optional slope and minimum connected area filters. It produces elevation and
selection rasters, candidate polygons and a coverage/method report.

## Requirements

GDAL ≥ 3.3, its matching Python bindings and NumPy. On Debian/Ubuntu the user can run
`sudo apt install gdal-bin python3-gdal python3-numpy`; online discovery additionally
needs curl (`sudo apt install curl`). Agents never install software or run interactive
setup. QGIS is optional for a requested map, not required for the analytic result.

## Install

```bash
npx skills add ignfab/geoskills --skill terrain-elevation-screening
```

## Contents

- [SKILL.md](SKILL.md): inputs, workflow, boundaries and output checks.
- [Source selection](references/sources.md): DEM acquisition and height references.
- [Local processing](references/local-processing.md): executable GDAL recipes.
- [Helicopter handoff](references/helicopter-handoff.md): what a terrain screen can establish.
- [French scenarios](../../../tests/terrain-elevation-screening.md) and
  [recipe tests](../../../tests/test_terrain_elevation_screening.py).

The altitude limit and optional slope/area criteria come from the request. There are no
default aviation thresholds. Outputs describe raster-scale terrain candidates, not
validated landing sites. Missing coverage stays unknown, including cells where slope
cannot be computed. No obstacle inventory, aircraft performance calculation, operational
authorization or site inspection is inferred from an elevation raster.

## Related skills

[geopf-altimetry](../../4-analyze/geopf-altimetry/README.md) retrieves a few elevations or
profiles; [gdal-raster-processing](../../3-prepare/gdal-raster-processing/README.md) handles raster
operations alone; [geopf-file-download](../../2-access/geopf-file-download/README.md)
and [geopf-raster-download](../../2-access/geopf-raster-download/README.md) acquire source data.
[qgis-project-builder](../../5-publish/qgis-project-builder/README.md) can package results.
These skills remain independently installable.
