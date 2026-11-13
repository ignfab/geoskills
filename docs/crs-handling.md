# CRS handling

Skills must work with the coordinate reference systems of the task. Lambert-93
(EPSG:2154) is the default recommendation when a new projected CRS is needed for a
suitable metropolitan-France task and none has been requested. It is not a source-CRS
guess, a worldwide default or a mandatory intermediate transformation.

## Choose by role

| Role | Rule |
| --- | --- |
| Source | Read the full CRS definition from file/service metadata. Missing CRS stays unknown until verified; never assign 2154 merely because it is the default. |
| Analysis | Keep a suitable existing/requested CRS. For planar distances and areas, check area of use, distortion and linear units; convert units explicitly. For global or unsuitable planar extents, choose a justified geodesic/equal-area method. |
| Raster alignment | Transform zones to the raster's actual CRS. Match grids, pixel size and nodata when combining rasters. Avoid resampling a raster solely to match an example's CRS. |
| Service exchange | Use the service's advertised CRS and axis order. Transform an AOI before sending it; a protocol constraint does not set the analysis or delivery CRS. |
| Delivery/display | Honour the requested CRS or preserve a suitable input/project CRS. Formats such as RFC 7946 GeoJSON have their own coordinate convention. QGIS can display layers in different source CRSs without rewriting them. |

Projection does not imply metre units: feet and other linear units exist. A distance
uses the linear conversion factor, an area its square. Geographic angular units must
not be labelled as metres or square metres. Horizontal CRS and vertical datum/units are
separate decisions; a horizontal reprojection does not establish a height reference.

Use the full CRS definition when no authority code exists. Store WKT alongside authority
identifiers where needed for round-trip validation. Check transformed coordinates and
extent, not just whether the command returned successfully. A valid CRS can still be
unsuitable for the location or requested measurement.

## Current helpers and recipes

- Vector conversion and attribute-only statistics preserve the source CRS unless an
  output format or the request requires transformation. Spatial aggregation aligns
  objects to the zone CRS and preserves it in the result.
- GeoPandas zonal statistics read the raster CRS from metadata. Buffer/area examples use
  an explicit analysis CRS and inspect unit conversions.
- The municipal building helper accepts a suitable projected CRS with known linear
  units; its reported areas remain in m². It rejects geographic/Web Mercator area
  calculations and known area-of-use mismatches.
- Terrain screening uses an explicit projected metre grid and metre elevations for its
  slope/area recipe. Any suitable projected metre CRS can be used; source and requested
  delivery CRSs can differ. Reuse an already suitable grid.
- The map helper keeps the source CRS unless `--crs` is supplied. Static maps support
  projected linear units (converted for the metre scale bar) and geographic coordinates
  (without a misleading linear scale bar). The Leaflet route transforms its data to
  longitude/latitude and retains its documented extent limits.
- QGIS projects use the manifest's project CRS, including custom WKT definitions, and
  validate full CRS definitions after reopening.

The [French CRS guide](../skills/3-prepare/crs-reprojection-france/README.md) remains a
territory-specific reference, not a restriction on the generic processing skills.
Examples using EPSG:2154 are local examples; adapt their bounds, resolution and units
with the CRS. Keep each installed skill's relevant rules self-contained.
