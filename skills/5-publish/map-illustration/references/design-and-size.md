# Design and size

## Choose the smallest useful delivery

| Need | Preferred route | Cost/tradeoff |
| --- | --- | --- |
| One map for a report or slide | GeoPandas + Matplotlib PNG | No QGIS, web runtime or basemap needed; fixed resolution |
| Simple editable/vector artwork | SVG or PDF from the same figure | Crisp text/lines; complex geometry can make files larger than PNG |
| Existing QML, project labels or mixed rasters/vectors | PyQGIS project render | Reuses symbology; requires an existing QGIS runtime |
| Existing composed QGIS layout | `QgsLayoutExporter` | Preserves legend/scale; validate existing layout before export |
| Zoom, pan and selected attributes | Folium HTML | Data embedded; Leaflet assets and optional tiles may still need network |

Default starting point: a 1400 × 1000 pixel PNG, 140 dpi, white background, title, source
note and a legend/colour scale when values need interpretation. For print, choose physical
size first, then pixels = inches × dpi; 300 dpi is useful only if the intended print needs
it. Avoid enormous images “for quality”. A PNG map can be lighter than a complex SVG.

Treat 2 MB per static image and 5 MB per interactive HTML as initial **review budgets**,
not technical limits or guarantees. Respect a user-specified limit instead. Report actual
bytes and any dependency bundle size. A 10 kB HTML that loads large assets is not a 10 kB
offline deliverable. There is no need to generate every format for every task.

## Keep the message readable

Choose one main subject, subdued context and sufficient contrast. Use a sequential palette
for ordered magnitudes, a diverging palette only around a meaningful stated centre, and
categorical colours for nominal classes. Use normalised indicators rather than implying
that large polygons' absolute counts represent density. State units and class boundaries;
missing values need a separate treatment from zero. The helper uses continuous Viridis,
with missing values in grey. It does not invent categories or meaningful thresholds.

Use a justified display CRS, preserving a suitable requested/input/project CRS. A projected
CRS supports a grid-distance scale bar after converting its linear units; geographic maps
need a geodesic scale or no bar. EPSG:3857 is a web display projection, not a general
measurement CRS. Do not add a decorative north
arrow that misrepresents grid versus true north. A title, readable legend and source/date
usually matter more than ornamental frames, graticules or a detailed basemap.

## Reduce size in this order

1. Limit the map to the intended AOI and necessary layers/attributes. Retain analytical
   originals and say when displayed features are a subset.
2. Match raster read resolution to the final image; keep nodata/masks and source units.
3. Simplify a **display copy** at a tolerance justified by the map scale. For shared polygon
   boundaries, use `mapshaper-simplify` or a verified topology-preserving approach, then
   check holes, islands and category boundaries. Never simplify analytical inputs in place.
4. Use PNG for dense geometry or rasterize only the dense artists in an SVG/PDF, retaining
   text and legend as vectors. See [Matplotlib rasterization](https://matplotlib.org/stable/gallery/misc/rasterization_demo.html).
5. In HTML, avoid embedding the full attribute table, thousands of DOM markers, base64
   full-resolution rasters or unnecessary UI libraries. For large layers, select/aggregate
   explicitly or use a proper tiled workflow beyond this small illustration skill.

Compare readability and geographic meaning before/after optimisation. Record changes and
measure the final file; do not claim a size target solely from configuration values.
