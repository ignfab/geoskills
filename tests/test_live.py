"""Opt-in bounded calls to public IGN services. See README before enabling."""
import csv
import io
import json
import os
import unittest
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from test_workflows import DATA, GDALCase

LIVE = os.environ.get("GEOSKILLS_LIVE") == "1"
BASE = "https://data.geopf.fr/geocodage/"


def get_json(endpoint, **parameters):
    with urlopen(BASE + endpoint + "?" + urlencode(parameters), timeout=30) as response:
        return json.load(response)


def post_csv(data, fields):
    boundary = "geoskills-fixture-boundary"
    body = bytearray()
    for name, value in fields:
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="data"; filename="fixture.csv"\r\nContent-Type: text/csv; charset=utf-8\r\n\r\n'.encode())
    body.extend(data)
    body.extend(f"\r\n--{boundary}--\r\n".encode())
    request = Request(BASE + "search/csv", data=bytes(body),
                      headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urlopen(request, timeout=60) as response:
        if "csv" not in response.headers.get("Content-Type", ""):
            raise AssertionError("Expected a CSV response")
        return list(csv.DictReader(io.StringIO(response.read().decode("utf-8-sig"))))


@unittest.skipUnless(LIVE, "Set GEOSKILLS_LIVE=1 to call public IGN services")
class LiveGeocodingTests(unittest.TestCase):
    def test_address(self):
        result = get_json("search", q="73 avenue de Paris Saint-Mandé", citycode="94067",
                          autocomplete="0", limit=1)
        self.assertEqual(result["type"], "FeatureCollection")
        self.assertEqual(len(result["features"]), 1)
        feature = result["features"][0]
        lon, lat = feature["geometry"]["coordinates"][:2]
        self.assertAlmostEqual(lon, 2.424573, delta=0.002)
        self.assertAlmostEqual(lat, 48.845726, delta=0.002)
        self.assertEqual(feature["properties"]["citycode"], "94067")
        self.assertTrue(0 <= feature["properties"]["score"] <= 1)

    def test_csv_preserves_input_and_quality_columns(self):
        data = (DATA / "adresses.csv").read_bytes()
        rows = post_csv(b"\xef\xbb\xbf" + data, [
            ("columns", "numero"), ("columns", "voie"), ("columns", "commune"),
            ("postcode", "code_postal"),
            *[("result_columns", name) for name in (
                "longitude", "latitude", "result_status", "result_score", "result_type",
                "result_label", "result_score_next", "result_citycode")]])
        original = list(csv.DictReader(io.StringIO(data.decode("utf-8"))))
        self.assertEqual(len(rows), len(original))
        for before, after in zip(original, rows):
            for field, value in before.items():
                self.assertEqual(after[field], value, f"Input field changed: {field}")
        self.assertEqual(rows[0]["result_status"], "ok")
        self.assertEqual(rows[0]["result_citycode"], "94067")
        self.assertLess(float(rows[5]["latitude"]), 0)  # Overseas point stays in Réunion.
        self.assertEqual(rows[6]["result_status"], "not-found")
        self.assertEqual(rows[7]["result_status"], "skipped")
        # The documented quality check must run even with explicit result_columns.
        bad = [r for r in rows if r["result_status"] != "ok" or float(r["result_score"] or 0) < 0.5]
        self.assertTrue({"7", "8"}.issubset({r["id"] for r in bad}))

    def test_reverse_points(self):
        with (DATA / "points.csv").open(encoding="utf-8", newline="") as handle:
            points = list(csv.DictReader(handle))
        for point in points:
            with self.subTest(id=point["id"]):
                result = get_json("reverse", lon=point["lon"], lat=point["lat"], index="address", limit=1)
                self.assertTrue(result["features"])
                feature = result["features"][0]
                lon, lat = feature["geometry"]["coordinates"][:2]
                self.assertAlmostEqual(lon, float(point["lon"]), delta=0.01)
                self.assertAlmostEqual(lat, float(point["lat"]), delta=0.01)
                self.assertLess(feature["properties"]["distance"], 1000)

    def test_parcel_true_geometry(self):
        result = get_json("search", index="parcel", departmentcode="94", municipalitycode="067",
                          section="0D", number="0050", returntruegeometry="true")
        self.assertEqual(len(result["features"]), 1)
        feature = result["features"][0]
        self.assertEqual(feature["properties"]["id"], "940670000D0050")
        geometry = feature["properties"].pop("truegeometry", None)
        self.assertIsNotNone(geometry)
        self.assertIn(geometry["type"], ("Polygon", "MultiPolygon"))
        feature["geometry"] = geometry
        self.assertTrue(feature["geometry"]["coordinates"])


@unittest.skipUnless(LIVE, "Set GEOSKILLS_LIVE=1 to download bounded IGN extracts")
class LiveDownloadTests(GDALCase):
    def setUp(self):
        super().setUp()
        self.env.update(GDAL_HTTP_TIMEOUT="30", GDAL_HTTP_MAX_RETRY="0")

    def test_wfs_sample(self):
        target = self.output / "buildings.geojson"
        self.run_tool("ogr2ogr", "-f", "GeoJSON", "-lco", "RFC7946=YES", "-limit", "5",
                      "-spat", "1.443", "43.603", "1.446", "43.606", "-spat_srs", "EPSG:4326",
                      "-where", "usage_1 = 'Résidentiel'",
                      "--config", "OGR_WFS_PAGING_ALLOWED", "OFF", target,
                      "WFS:https://data.geopf.fr/wfs/ows?VERSION=2.0.0&COUNT=5&TYPENAME=BDTOPO_V3:batiment",
                      "BDTOPO_V3:batiment", timeout=120)
        features = json.loads(target.read_text())["features"]
        self.assertGreater(len(features), 0)
        self.assertLessEqual(len(features), 5)
        for feature in features:
            self.assertIn(feature["geometry"]["type"], ("Polygon", "MultiPolygon"))
            self.assertEqual(feature["properties"]["usage_1"], "Résidentiel")
        crs = self.run_tool("gdalsrsinfo", "-o", "epsg", target)
        self.assertTrue("EPSG:4326" in crs or "EPSG:4979" in crs, crs)
        for feature in features:
            geometry = feature["geometry"]
            polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
            for polygon in polygons:
                for ring in polygon:
                    for point in ring:
                        self.assertTrue(1.40 < point[0] < 1.49 and 43.58 < point[1] < 43.63)

    def test_wmts_orthophoto(self):
        target = self.output / "ortho.tif"
        self.run_tool("gdalwarp", "-te", "574107", "6279371", "574607", "6279871",
                      "-t_srs", "EPSG:2154", "-tr", "0.5", "0.5", "-of", "GTiff",
                      "-co", "COMPRESS=DEFLATE",
                      "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=ORTHOIMAGERY.ORTHOPHOTOS",
                      target, timeout=120)
        info = self.info(target)
        self.assert_crs(target, 2154)
        self.assertEqual(info["size"], [1000, 1000])
        self.assertIn(len(info["bands"]), (3, 4))
        self.assertTrue(any(band["maximum"] > band["minimum"] for band in info["bands"][:3]))
        self.assertEqual(info["metadata"]["IMAGE_STRUCTURE"]["COMPRESSION"], "DEFLATE")

    def test_wms_elevation(self):
        source = self.output / "dem.xml"
        source.write_text('''<GDAL_WMS>
  <Service name="WMS">
    <Version>1.3.0</Version><ServerUrl>https://data.geopf.fr/wms-r/wms?</ServerUrl>
    <CRS>EPSG:2154</CRS><ImageFormat>image/geotiff</ImageFormat>
    <Layers>ELEVATION.ELEVATIONGRIDCOVERAGE.HIGHRES</Layers><Styles></Styles>
  </Service>
  <DataWindow>
    <UpperLeftX>656795</UpperLeftX><UpperLeftY>6861200</UpperLeftY>
    <LowerRightX>658045</LowerRightX><LowerRightY>6859450</LowerRightY>
    <SizeX>250</SizeX><SizeY>350</SizeY>
  </DataWindow>
  <BandsCount>1</BandsCount><DataType>Float32</DataType>
</GDAL_WMS>''')
        target = self.output / "dem.tif"
        self.run_tool("gdal_translate", "-of", "GTiff", "-co", "COMPRESS=DEFLATE",
                      "-a_nodata", "-99999", source, target, timeout=120)
        info = self.info(target)
        self.assert_crs(target, 2154)
        self.assertEqual(info["size"], [250, 350])
        self.assertEqual(info["geoTransform"], [656795, 5, 0, 6861200, 0, -5])
        self.assertEqual(len(info["bands"]), 1)
        band = info["bands"][0]
        self.assertEqual(band["type"], "Float32")
        self.assertEqual(band["noDataValue"], -99999)
        self.assertGreater(band["minimum"], 20)
        self.assertLess(band["maximum"], 100)
        self.assertGreater(band["maximum"], band["minimum"])

    def test_wmts_plan(self):
        target = self.output / "plan.tif"
        self.run_tool("gdalwarp", "-te", "1.43", "43.59", "1.45", "43.61", "-te_srs", "EPSG:4326",
                      "-t_srs", "EPSG:3857", "-tr", "10", "10", "-co", "COMPRESS=DEFLATE",
                      "WMTS:https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetCapabilities,layer=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2",
                      target, timeout=120)
        self.assert_crs(target, 3857)
        info = self.info(target)
        self.assertTrue(all(0 < size < 1000 for size in info["size"]))
        self.assertTrue(any(band["maximum"] > band["minimum"] for band in info["bands"][:3]))


if __name__ == "__main__":
    unittest.main()
