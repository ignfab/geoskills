# QGIS export

Prefer this path when a supplied project already contains useful layer styles, labels or
mixed raster/vector composition. Inspect its sources and external dependencies first;
loading a project can access remote providers. For a no-network request, use local data
and omit remote layers before rendering. Do not recreate a validated QML in Matplotlib.

## Existing project to PNG

With only existing local layers, create a temporary in-memory `QgsProject`, set the
requested simple symbols and a verified extent, then render with `QgsMapSettings` and
`QgsMapRendererParallelJob`. A temporary QGS may be passed to the helper below; it is not
a required deliverable. Reuse the requested source style rather than building a new QML.

```bash
QT_QPA_PLATFORM=offscreen python3 scripts/export_qgis.py existing.qgz output/preview \
  --title 'Study area' --source-note 'Source: supplied project; edition unknown'
```

Use the existing QGIS environment, including its matching Qt/PROJ/GDAL resources. A broken
environment is not evidence that the source project is invalid. This helper reads the
project, preserves visible layer order and styling, uses its stored view extent, waits for
rendering, checks renderer errors and reopens the PNG. It does not save the input project.
The aspect ratio may expand the visible extent; the report records the actual render bounds.
QGIS's [rendering cookbook](https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/composer.html)
describes the map-settings/render-job and layout alternatives.

The quick PNG contains a title and source note, but generates **no thematic legend or scale
bar**. Use it for a locator/context image whose symbols need no additional interpretation,
or add a clearly supplied caption. When a thematic legend, scale or print page is required,
reuse a checked existing layout instead. New complex layouts and atlases are outside scope.
Project assembly alone belongs to `qgis-project-builder`; QML creation alone to
`qgis-layer-styling`. Their installation is not needed to export an existing project.

## Reuse an existing layout

Read the project, inspect `project.layoutManager().layouts()` and select a layout by its
actual name. Verify page sizes, layer references, text, legends, scales and missing items.
For an already loaded `layout` and a new `output_pdf` path:

```python
from pathlib import Path
from qgis.core import QgsLayoutExporter
if Path(output_pdf).exists():
    raise ValueError('Choose a new output path')
exporter = QgsLayoutExporter(layout)
settings = QgsLayoutExporter.PdfExportSettings()
settings.dpi = 150
status = exporter.exportToPdf(str(output_pdf), settings)
if status != QgsLayoutExporter.Success:
    raise RuntimeError('QGIS layout export failed')
```

Use `exportToImage` with image settings for PNG, or `exportToSvg` with SVG settings for a
small vector layout. Do not force vectors for imagery or complex blend effects: inspect
the actual result and size. Reopen/rasterize the final artifact for visual inspection;
successful return codes and provider validity do not establish visible content. Preserve
original project/data bytes and source-directory inventory, including GDAL sidecars.
