---
name: terrain-elevation-screening
description: Screen an area of interest by terrain elevation, optionally slope and contiguous area, from DEM discovery and clipping to candidate polygons and a coverage report. Use when the user wants elevations over an area and zones above, below or between altitude thresholds, including preliminary helicopter landing-site terrain screening. This does not establish landing suitability. For point elevations or profiles use geopf-altimetry; for raster clipping or conversion alone use gdal-raster-processing.
---

# Terrain elevation screening

Deliver an elevation GeoTIFF, a selection mask, candidate polygons in a GeoPackage and
a short report of thresholds, coverage and limitations. Add a slope raster only when
requested. This workflow owns the common extent, grid, vertical reference and missing-data
rules across acquisition, filtering and delivery. Related skills are optional helpers;
the [local recipe](references/local-processing.md) works with GDAL alone.

## Prerequisites

Check `gdalinfo --version`, `ogrinfo --version`, `gdaldem --help`,
`gdal_calc.py --help` and `gdal_polygonize.py --help`.
Use GDAL ≥ 3.3 with matching Python bindings and NumPy. If missing, give the user
`sudo apt install gdal-bin python3-gdal python3-numpy` (Debian/Ubuntu) to run themselves.
Online discovery also needs `curl` (user-run command: `sudo apt install curl`).
**Never install software yourself.** Do not launch interactive setup or login commands.

## Define the screening

1. Identify the polygon or bounding box **and its CRS**. Resolve ambiguous places and
   inspect supplied layers before selecting the AOI. Clarify whether “height” means
   terrain altitude in a vertical datum, height above ground, obstacle height, or local
   relief. A terrain DEM supplies the first, not the others. If meaning, threshold units
   or vertical reference are unresolved, inspect the data but do not silently filter.
2. Record the user's comparison (`<`, `<=`, `>=`, or an interval), altitude limits and
   units. Ask for missing limits; there is no default altitude or helicopter criterion.
   Optional slope limits need degrees or percent; optional minimum connected area needs
   square metres. State which criteria were actually applied.
3. Prefer supplied terrain data. Otherwise follow [source selection](references/sources.md):
   discover a numeric terrain model covering the AOI and, for slope, a surrounding halo.
   Use `geopf-file-download` for tiles or `geopf-raster-download` for a verified numeric extract.
   Use `geopf-altimetry` for a few points or a profile, not a dense grid of API requests.
4. Inspect the DEM and AOI with `gdalinfo` and `ogrinfo`. Verify terrain versus surface,
   edition, horizontal CRS, vertical datum, units, scale/offset, resolution and nodata.
   Use `crs-reprojection-france` for an appropriate projected metre CRS or a justified
   vertical conversion. A horizontal reprojection alone does not establish matching
   height references. Prepare one common grid with `gdal-raster-processing` if needed.
   Preserve an already suitable requested/source grid; Lambert-93 is only a conditional
   metropolitan-France fallback. This recipe's metre requirement is for slope/area units,
   not a required EPSG code. Keep a separate requested delivery CRS explicit.
5. Run the [local processing recipe](references/local-processing.md) in a new output
   directory, in the foreground. It clips elevations, optionally derives slope before
   clipping, applies explicit thresholds and vectorizes selected cells with four-neighbour
   connectivity. Nodata stays unknown; zero and negative altitudes can be valid.
6. Deliver the actual outputs and report. For a requested map, optionally use
   `qgis-layer-styling` and `qgis-project-builder`; finish the data delivery if QGIS is
   unavailable. Label the polygons **terrain-screening candidates**.

## Helicopter example

For “find terrain below my altitude limit within this area so a helicopter can land”,
perform the geographic screen, then apply slope/size criteria only if supplied.
Altitude alone cannot establish a usable landing site; low elevation does not imply flat
or obstacle-free ground. Follow the [helicopter handoff](references/helicopter-handoff.md)
to describe unchecked obstacles, usable footprint, surface, approaches and operational
conditions. Never label a result safe, approved or suitable for landing from DEM filters.
Actual assessment remains with the qualified pilot/operator using current site evidence.

## Validate the output

Reopen the rasters and GeoPackage. Verify the expected projected CRS, identical raster
grids, AOI extent, metre elevations, degree/percent slope convention and mask values
(`1` selected, `0` rejected, `255` unknown/outside). Check finite valid values and plausible
elevation ranges for the source and territory. Count cells inside the AOI separately from
outside cells, then reconcile selected + rejected + unknown with the AOI cell count.
When slope is used, report its extra unknown border and nodata neighbourhoods separately.
Check polygons lie within the AOI, preserve holes, and satisfy any area limit. Before
vector clipping, selected area equals cell count × cell area; clipping can reduce it.
Do not present pixel size as vertical accuracy or infer the absence of small obstacles.
An empty selection is valid when coverage exists; an all-nodata AOI is insufficient data.
Report both explicitly, with source/edition/access date, vertical reference, thresholds,
resampling, coverage, counts/areas and checks actually performed. Keep inputs unchanged.

## References

- [Source selection](references/sources.md): local-first acquisition and vertical semantics.
- [Local processing](references/local-processing.md): aligned grids, thresholds and polygons.
- [Helicopter handoff](references/helicopter-handoff.md): scope of preliminary terrain screening.
