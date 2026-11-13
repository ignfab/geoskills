#!/usr/bin/env python3
"""Render an existing QGIS project's visible map; never save changes to the project."""
import argparse
import json
import os
from pathlib import Path


def export_project(source, output, *, title, source_note, width=1400, height=1000, dpi=140):
    from osgeo import gdal
    from qgis.core import Qgis, QgsProject, QgsMapSettings, QgsMapRendererParallelJob, QgsCoordinateTransform
    from qgis.PyQt.QtCore import QSize, QRect
    from qgis.PyQt.QtGui import QColor, QFont, QImage, QPainter
    from qgis.PyQt.QtCore import Qt

    source, output = Path(source), Path(output)
    if not 33400 <= Qgis.QGIS_VERSION_INT < 40000:
        raise ValueError('Supported QGIS range: 3.34–3.x')
    if not source.is_file() or output.exists():
        raise ValueError('Expected an existing project and a new output directory')
    if not title.strip() or not source_note.strip() or not (400 <= width <= 4000 and 400 <= height <= 4000 and 72 <= dpi <= 600):
        raise ValueError('Supply a title/source note and bounded output dimensions')
    before = source.read_bytes()
    pam = gdal.GetConfigOption('GDAL_PAM_ENABLED')
    gdal.SetConfigOption('GDAL_PAM_ENABLED', 'NO')
    project = QgsProject()
    try:
        if not project.read(str(source)) or not project.crs().isValid():
            raise ValueError('Cannot open project with a valid CRS')
        root = project.layerTreeRoot()
        layers = [layer for layer in root.layerOrder() if root.findLayer(layer.id()).isVisible()]
        if not layers or any(not layer.isValid() for layer in layers):
            raise ValueError('Expected at least one visible, valid layer')
        box = project.viewSettings().defaultViewExtent()
        if box.isEmpty() or not box.isFinite() or not box.crs().isValid():
            raise ValueError('Set a verified project view extent before exporting')
        extent = QgsCoordinateTransform(box.crs(), project.crs(), project).transformBoundingBox(box)
        settings = QgsMapSettings()
        settings.setTransformContext(project.transformContext())
        settings.setDestinationCrs(project.crs())
        settings.setLayers(layers)
        settings.setBackgroundColor(QColor('white'))
        settings.setOutputSize(QSize(width, height-160))
        settings.setOutputDpi(dpi)
        settings.setExtent(extent)
        job = QgsMapRendererParallelJob(settings)
        job.start()
        job.waitForFinished()
        if job.errors():
            raise RuntimeError('Map renderer reported errors; inspect layer availability')
        rendered = job.renderedImage()
        if rendered.isNull():
            raise RuntimeError('Renderer returned an empty image')
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(QColor('white'))
        image.setDotsPerMeterX(round(dpi / .0254))
        image.setDotsPerMeterY(round(dpi / .0254))
        painter = QPainter(image)
        painter.drawImage(0, 75, rendered)
        painter.setPen(QColor('#172b3a'))
        font = QFont('DejaVu Sans')
        font.setPixelSize(24)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRect(30, 10, width-60, 60), Qt.TextWordWrap, title)
        font.setPixelSize(14)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(QRect(30, height-75, width-60, 65), Qt.TextWordWrap, source_note)
        painter.end()
        output.mkdir(parents=True)
        target = output / 'map.png'
        if not image.save(str(target), 'PNG') or QImage(str(target)).size() != QSize(width, height):
            raise RuntimeError('PNG write/reopen failed')
        visible = settings.visibleExtent()
        report = {'qgis_version': Qgis.QGIS_VERSION, 'crs': project.crs().authid(),
                  'layers_top_first': [layer.name() for layer in layers],
                  'pixels': [width, height], 'dpi': dpi, 'title': title, 'source_note': source_note,
                  'render_extent': [visible.xMinimum(), visible.yMinimum(), visible.xMaximum(), visible.yMaximum()],
                  'bytes': target.stat().st_size, 'renderer_errors': 0,
                  'legend': 'not generated; use an existing layout when a legend is required',
                  'visual_check': 'not performed by helper'}
        if source.read_bytes() != before:
            raise RuntimeError('Source project changed during export')
        (output / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
        return report
    finally:
        project.clear()
        gdal.SetConfigOption('GDAL_PAM_ENABLED', pam)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--title', required=True)
    parser.add_argument('--source-note', required=True)
    args = parser.parse_args()
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from qgis.core import QgsApplication
    app = QgsApplication([], False)
    app.initQgis()
    try:
        print(json.dumps(export_project(args.source, args.output, title=args.title, source_note=args.source_note), indent=2))
    finally:
        app.exitQgis()


if __name__ == '__main__':
    main()
