"""Run documented curl recipes on loopback; this is not an ECQL/GeoServer emulator."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
import unittest
from urllib.parse import parse_qs, urlsplit


SKILL = Path(__file__).resolve().parents[1] / "skills/geoserver-cql-filter"


class Recorder(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests.append(urlsplit(self.path))
        self.send_response(self.server.response_status)
        self.end_headers()
        self.wfile.write(b"recorded request; not a GeoServer result")

    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which("curl") and shutil.which("bash"), "curl and bash required")
class CQLRequestTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="geoskills-cql-")
        self.addCleanup(self.directory.cleanup)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Recorder)
        self.server.requests = []
        self.server.response_status = 200
        self.addCleanup(self.server.server_close)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.thread.join, 5)
        self.addCleanup(self.server.shutdown)
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def run_recipe(self, filename, index, *, cql="INCLUDE", expect_success=True):
        text = (SKILL / filename).read_text(encoding="utf-8")
        recipe = re.findall(r"^```bash\n(.*?)^```", text, re.M | re.S)[index]
        recipe = recipe.replace("https://example.org/geoserver", self.url)
        env = dict(os.environ, WFS_URL=self.url + "/wfs", TYPE_NAME="test:sites", CQL=cql,
                   NO_PROXY="127.0.0.1", no_proxy="127.0.0.1", CURL_HOME=self.directory.name)
        result = subprocess.run(["bash", "-eu", "-c", recipe], cwd=self.directory.name,
                                env=env, capture_output=True, text=True, timeout=10)
        if expect_success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.server.requests)
        request = self.server.requests[-1]
        return request, parse_qs(request.query, keep_blank_values=True)

    def test_discovery_requests_use_the_supplied_service(self):
        request, query = self.run_recipe("SKILL.md", 0)
        self.assertEqual(request.path, "/wfs")
        self.assertEqual(query["request"], ["GetCapabilities"])
        self.assertTrue((Path(self.directory.name) / "capabilities.xml").is_file())
        _, query = self.run_recipe("SKILL.md", 1)
        self.assertEqual(query["request"], ["DescribeFeatureType"])
        self.assertEqual(query["typeNames"], ["workspace:layer"])
        self.assertNotIn("cql_filter", query)

    def test_wfs_sample_preserves_escaped_apostrophe_and_limit(self):
        _, query = self.run_recipe("SKILL.md", 2)
        self.assertEqual(query["cql_filter"], ["name = 'King''s Park' AND population >= 1000"])
        self.assertEqual(query["count"], ["10"])
        self.assertEqual(query["typeNames"], ["test:sites"])
        self.assertEqual(query["outputFormat"], ["application/json"])
        self.assertTrue((Path(self.directory.name) / "sample.geojson").is_file())

    def test_hits_encodes_unicode_wildcards_and_ewkt_exactly_once(self):
        cql = ("name LIKE 'L''Haÿ & Parc+%' AND code = '01' AND "
               "INTERSECTS(shape, SRID=4326;POINT(2.35 48.85))")
        _, query = self.run_recipe("references/requests.md", 0, cql=cql)
        self.assertEqual(query["cql_filter"], [cql])
        self.assertEqual(query["resultType"], ["hits"])
        self.assertEqual(set(query), {"service", "version", "request", "typeNames",
                                     "resultType", "cql_filter"})

    def test_wms_keeps_ewkt_and_layer_filters_in_one_parameter(self):
        request, query = self.run_recipe("references/requests.md", 1)
        self.assertEqual(request.path, "/wms")
        self.assertEqual(query["layers"], ["workspace:sites,workspace:roads"])
        self.assertEqual(query["cql_filter"], [
            "INTERSECTS(shape, SRID=4326;POLYGON((2.34 48.84,2.36 48.84,"
            "2.36 48.86,2.34 48.86,2.34 48.84)));INCLUDE"])
        self.assertEqual(query["crs"], ["CRS:84"])
        self.assertEqual(query["bbox"], ["2.34,48.84,2.36,48.86"])
        self.assertEqual(query["styles"], [","])
        self.assertEqual(query["width"], ["256"])
        self.assertEqual(query["height"], ["256"])

    def test_http_error_is_a_command_failure(self):
        self.server.response_status = 400
        self.run_recipe("SKILL.md", 2, expect_success=False)


if __name__ == "__main__":
    unittest.main()
