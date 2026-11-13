# Python rendering without QGIS

## Vector helper

Resolve `scripts/render_vector.py` relative to this skill. It accepts one inspected local
vector layer, a new output directory, a short title and a source note. Omit `--crs` to keep
the input CRS or set `DISPLAY_CRS` to the requested/suitable display definition (authority
code or WKT). EPSG:2154 is only a fallback for a suitable metropolitan-France map.
Projected maps convert linear units, including feet, for a metre scale bar; this is a
grid-distance scale, subject to projection distortion. Geographic maps use equal angular
axis spacing without a linear scale bar; they are illustrations, not distance measurements.
It preserves all input features and does no simplification or statistics.

`--crs` applies to static output. The HTML route converts a display copy to EPSG:4326
GeoJSON and uses Leaflet's EPSG:3857 view, reported as `html.data_crs` and
`html.display_crs`; it does not change the analytic/source CRS.

```bash
python3 scripts/render_vector.py zones.gpkg output/map --layer zones --crs "$DISPLAY_CRS" \
  --title 'Observed indicator' --source-note 'Source: supplied survey, edition 2024' \
  --column indicator --units 'documented unit' --formats png svg
```

The numeric column must already mean what the map claims. Decode source-specific sentinels
on an explicit display copy first; the helper treats valid zero as zero and null as missing.
It rejects non-finite values and all-null thematic fields. Constant data are reported as
such in the range; prefer a single symbol or a labelled constant rather than implying
variation. `report.json` contains source note, display CRS, range/null count, dimensions,
versions, scale-bar conversion/omission and file sizes. A source date left unknown must
remain unknown. Inspect polar/antimeridian extents before choosing this simple renderer.

PNG is the default. `--formats png pdf` also makes a PDF; `svg` retains vector paths/text.
Check a rendered preview of both formats. Matplotlib [savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)
supports these outputs; more DPI does not reduce geometric complexity in a vector file.

For multiple layers, adapt [GeoPandas plotting](https://geopandas.org/en/stable/docs/user_guide/mapping.html)
on the same Matplotlib axes: explicitly reproject each layer to the display CRS and set
`zorder` (context first, subject above). Specify `vmin`/`vmax` when comparing maps so that
identical colours retain identical meanings. For polygon overlays, set `facecolor='none'`
when only an outline is intended. Build a legend from the actual displayed artists.
Do not drop outlying features merely to get a more attractive default extent.

## Bounded raster preview

Use Rasterio only when an existing numerical/image raster needs illustration without QGIS.
Read a window for a large AOI request, not an entire national raster. The following recipe
expects a **previously clipped**, north-up, single-band raster whose CRS, nodata, scale and
offset have been checked. Set `raster_path`, `output_png`, `title` and `unit_label` first.
For masks/classes use `Resampling.nearest` and a discrete legend instead of the continuous
example. This is a display preview, not a new analysis raster.

```python
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import array_bounds
from affine import Affine
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

if Path(output_png).exists():
    raise ValueError('Choose a new output path')
with rasterio.open(raster_path) as src:
    if src.crs is None or src.count != 1 or src.transform.b or src.transform.d:
        raise ValueError('Expected one band, a known CRS and an unrotated grid')
    factor = min(1, 1400 / max(src.width, src.height))
    out_width, out_height = max(1, round(src.width*factor)), max(1, round(src.height*factor))
    values = src.read(1, out_shape=(out_height, out_width), masked=True,
                      resampling=Resampling.average)
    values = values.astype(float) * src.scales[0] + src.offsets[0]
    if not values.count() or not np.isfinite(values.compressed()).all():
        raise ValueError('No valid finite raster values')
    transform = src.transform * Affine.scale(src.width/out_width, src.height/out_height)
    west, south, east, north = array_bounds(out_height, out_width, transform)
fig = Figure(figsize=(10, 7), dpi=140)
FigureCanvasAgg(fig)
ax = fig.add_subplot(111)
im = ax.imshow(values, extent=(west, east, south, north), origin='upper', cmap='terrain')
fig.colorbar(im, ax=ax, label=unit_label)
ax.set_title(title)
ax.set_aspect('equal')
ax.set_axis_off()
fig.savefig(output_png, dpi=140)
```

Add the source/date as a caption, or compose it in the figure for a standalone image.
This preview preserves the raster CRS and draws no distance scale. A geographic preview
uses angular coordinates; do not label its horizontal units as metres. Reproject only
when the requested display needs it, with an explicit resampling choice.
Record original versus displayed pixel dimensions and resampling. A resampled elevation
preview must not be used to claim that small obstacles or local peaks are absent.
