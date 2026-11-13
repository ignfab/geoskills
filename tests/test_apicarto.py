"""Run the API Carto helper and documented requests against a loopback server."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock
from urllib.parse import parse_qs, urlsplit

from skill_examples import read_example, skill_dir

SCRIPT = skill_dir("apicarto-query") / "scripts/fetch_features.py"
SPEC = importlib.util.spec_from_file_location("fetch_features", SCRIPT)
FETCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FETCH)
POINT = {"type": "Point", "coordinates": [2.419441, 48.841526]}


def feature(identifier, **properties):
    return {"type": "Feature", "id": identifier, "properties": properties, "geometry": POINT}


def collection(features, matched):
    return {"type": "FeatureCollection", "features": features, "numberMatched": matched,
            "numberReturned": len(features),
            "links": [{"rel": "next", "href": "http://localhost/api/next"}]}


class Service(BaseHTTPRequestHandler):
    def do_GET(self):
        self.answer(None)

    def do_POST(self):
        self.answer(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))

    def answer(self, body):
        url = urlsplit(self.path)
        query = {key: values[0] for key, values in parse_qs(url.query).items()}
        params = body if body is not None else query
        self.server.requests.append((self.command, url.path, params))
        status, payload = self.server.respond(url.path, params)
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def pages(features, matched=None, *, repeat_second=False):
    """Serve features in pages of the requested size, like API Carto."""
    matched = len(features) if matched is None else matched

    def respond(path, params):
        start, limit = int(params["_start"]), int(params["_limit"])
        batch = features[start:start + limit]
        if repeat_second and start:
            batch = features[:limit]
        return 200, collection(batch, matched)
    return respond


class LoopbackCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="geoskills-apicarto-")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Service)
        self.server.requests = []
        self.server.respond = pages([])
        self.addCleanup(self.server.server_close)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(self.server.shutdown)
        self.base = f"http://127.0.0.1:{self.server.server_port}/api"
        bypass = {"NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"}
        patcher = mock.patch.dict(os.environ, bypass)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.env = dict(os.environ, CURL_HOME=self.temp.name)

    def fetch(self, *params, geometry=None, output="out.geojson", **options):
        return FETCH.fetch_all("cadastre/parcelle", self.directory / output, params, geometry,
                               base_url=self.base, **options)


class FetchFeaturesTests(LoopbackCase):
    def test_pages_by_start_until_the_matched_count(self):
        self.server.respond = pages([feature(f"parcelle.{i}", code_insee="02201") for i in range(5)])
        result = self.fetch("code_insee=02201", page_size=2)
        self.assertEqual((result["pages"], result["features"], result["status"]), (3, 5, "complete"))
        self.assertEqual([(r[2]["_start"], r[2]["_limit"]) for r in self.server.requests],
                         [("0", "2"), ("2", "2"), ("4", "2")])
        self.assertTrue(all(r[2]["code_insee"] == "02201" for r in self.server.requests))
        written = json.loads((self.directory / "out.geojson").read_text(encoding="utf-8"))
        self.assertEqual([f["id"] for f in written["features"]], [f"parcelle.{i}" for i in range(5)])
        self.assertNotIn("crs", written)

    def test_geometry_is_posted_from_a_single_feature_collection(self):
        path = self.directory / "zone.geojson"
        path.write_text(json.dumps({"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": POINT}]}))
        self.server.respond = pages([feature("zone_urba.1")])
        result = self.fetch(geometry=path)
        method, _, body = self.server.requests[0]
        self.assertEqual(method, "POST")
        self.assertEqual(body["geom"], POINT)
        self.assertEqual((body["_start"], body["_limit"]), (0, 1000))
        self.assertEqual(result["geometry_vertices"], 1)

    def test_inconsistent_pages_fail_without_writing(self):
        features = [feature(f"parcelle.{i}") for i in range(4)]
        cases = (pages(features, repeat_second=True), pages(features[:2], matched=4),
                 lambda path, params: (200, collection(features[:2], 4 if params["_start"] == "0" else 5)))
        for respond in cases:
            with self.subTest(respond=respond), self.assertRaises(ValueError):
                self.server.respond = respond
                self.fetch(page_size=2)
            self.assertFalse((self.directory / "out.geojson").exists())

    def test_error_bodies_are_reported(self):
        cases = {
            (400, b'{"code":400,"message":{"section":{"msg":"Le num\xc3\xa9ro de section est sur 2 caract\xc3\xa8res"}}}'): "HTTP 400",
            (500, b'{"type":"error","message":"<ows:ExceptionReport/>"}'): "ExceptionReport",
            (200, b'{"code":400,"message":"Ann\xc3\xa9e Invalide"}'): "not a FeatureCollection",
            (500, b"<html><pre>Error: Unknown Type: Feature</pre></html>"): "HTTP 500",
        }
        for (status, body), expected in cases.items():
            with self.subTest(status=status, body=body[:30]):
                self.server.respond = lambda path, params, s=status, b=body: (s, b)
                with self.assertRaisesRegex(ValueError, expected):
                    self.fetch()

    def test_existing_output_is_never_replaced(self):
        target = self.directory / "out.geojson"
        target.write_text("previous result")
        self.server.respond = pages([feature("parcelle.1")])
        with self.assertRaises(FileExistsError):
            self.fetch()
        self.assertEqual(target.read_text(), "previous result")

    def test_empty_result_carries_a_warning(self):
        result = self.fetch()
        self.assertEqual(result["features"], 0)
        self.assertIn("longitude, latitude", result["warning"])

    def test_invalid_inputs_are_rejected_before_any_request(self):
        projected = self.directory / "projected.geojson"
        projected.write_text(json.dumps({"type": "Point", "coordinates": [657390.27, 6860320.79]}))
        declared = self.directory / "declared.geojson"
        declared.write_text(json.dumps({"type": "FeatureCollection", "features": [],
                                        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::2154"}}}))
        two = self.directory / "two.geojson"
        two.write_text(json.dumps({"type": "FeatureCollection", "features": [feature("a"), feature("b")]}))
        for kwargs in (dict(geometry=projected), dict(geometry=declared), dict(geometry=two),
                       dict(page_size=1001)):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.fetch(**kwargs)
        for params in (("geom={}",), ("_start=5",), ("code_insee",), ("a=1", "a=2")):
            with self.subTest(params=params), self.assertRaises(ValueError):
                self.fetch(*params)
        with self.assertRaises(ValueError):
            FETCH.fetch_all("../cadastre", self.directory / "x.geojson", base_url=self.base)
        self.assertEqual(self.server.requests, [])

    def test_cli_exit_status(self):
        self.server.respond = lambda path, params: (500, {"type": "error", "message": "pool timeout"})
        result = subprocess.run([sys.executable, str(SCRIPT), "--base-url", self.base, "gpu/zone-urba",
                                 "out.geojson", "--param", "partition=DU_94067"], cwd=self.directory,
                                capture_output=True, text=True, timeout=30, env=self.env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("pool timeout", result.stderr)


@unittest.skipUnless(shutil.which("curl") and shutil.which("bash"), "curl and bash required")
class DocumentedRequestTests(LoopbackCase):
    def recipe(self, reference, heading, example=0):
        code = read_example(reference, heading, language="bash", example=example)
        code = code.replace("https://apicarto.ign.fr/api", self.base)
        code = code.replace("python3 scripts/fetch_features.py",
                            f"{sys.executable} {SCRIPT} --base-url {self.base}")
        result = subprocess.run(["bash", "-eu", "-c", code], cwd=self.directory, env=self.env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_skill_point_query_keeps_the_geometry_parameter(self):
        self.server.respond = lambda path, params: (200, collection([feature("natura.1")], 1))
        self.recipe("apicarto-query/SKILL.md", "## Query", 0)
        paths = [(r[0], r[1]) for r in self.server.requests]
        self.assertEqual(paths, [("GET", "/api/doc/nature.yml"), ("GET", "/api/nature/natura-habitat")])
        self.assertEqual(json.loads(self.server.requests[1][2]["geom"]),
                         {"type": "Point", "coordinates": [2.6458, 48.4038]})
        self.assertTrue((self.directory / "natura-habitat.json").is_file())

    def test_skill_and_reference_script_commands(self):
        (self.directory / "zone.geojson").write_text(json.dumps(POINT))
        self.server.respond = pages([feature(f"parcelle.{i}", code_insee="94067") for i in range(3)])
        self.recipe("apicarto-query/SKILL.md", "## Query", 1)
        self.assertEqual(self.server.requests[0][:2], ("GET", "/api/cadastre/parcelle"))
        self.assertEqual(self.server.requests[-1][:2], ("POST", "/api/gpu/zone-urba"))
        self.assertEqual(len(json.loads((self.directory / "parcelles.geojson").read_text())["features"]), 3)
        self.server.requests.clear()
        self.recipe("apicarto-query/references/cadastre.md", "## Find parcels", 1)
        self.assertEqual(self.server.requests[0][2]["_limit"], "500")
        self.assertTrue((self.directory / "parcelles_94067.geojson").is_file())

    def test_reference_lookups_send_padded_codes(self):
        self.server.respond = lambda path, params: (200, collection([feature("parcelle.1")], 1))
        self.recipe("apicarto-query/references/cadastre.md", "## Find parcels", 0)
        self.assertEqual(self.server.requests[-1][2],
                         {"code_insee": "94067", "section": "0J", "numero": "0182"})
        self.recipe("apicarto-query/references/cadastre.md", "## Find parcels", 2)
        self.assertEqual(self.server.requests[-1][1], "/api/cadastre/feuille")


if __name__ == "__main__":
    unittest.main()
