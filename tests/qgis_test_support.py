"""Shared optional headless QGIS test environment; require it explicitly in QGIS CI."""
import importlib.util
import json
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = None


def qgis_app():
    global APP
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    try:
        from qgis.core import Qgis, QgsApplication
    except ImportError:
        if os.environ.get('GEOSKILLS_REQUIRE_QGIS') == '1':
            raise RuntimeError('QGIS integration job requires PyQGIS')
        raise unittest.SkipTest('PyQGIS is not installed; dedicated QGIS CI runs these tests')
    if not 33400 <= Qgis.QGIS_VERSION_INT < 40000:
        raise RuntimeError(f'Unsupported test runtime: {Qgis.QGIS_VERSION}')
    if APP is None:
        from osgeo import gdal
        gdal.SetConfigOption('GDAL_PAM_ENABLED', 'NO')
        APP = QgsApplication([], False)
        APP.initQgis()
        print('QGIS integration runtime:', Qgis.QGIS_VERSION)
    return APP


def load_helper(name, family, script):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), ROOT/'skills'/family/name/'scripts'/script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def vector_fixture(path, kind='Point', values=(0, 10, 20, None)):
    coords = {'Point': [2.4, 48.8], 'LineString': [[2.4, 48.8], [2.41, 48.81]],
              'Polygon': [[[2.4, 48.8], [2.41, 48.8], [2.41, 48.81], [2.4, 48.8]]]}
    payload = {'type': 'FeatureCollection', 'features': [
        {'type': 'Feature', 'properties': {'value': value, 'category': None if value is None else str(value)},
         'geometry': {'type': kind, 'coordinates': coords[kind]}} for value in values]}
    path.write_text(json.dumps(payload))
    return str(path)
