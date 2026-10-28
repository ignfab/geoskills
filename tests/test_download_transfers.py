"""Real curl transfers on loopback, including safe range resume and changed editions."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest
import zipfile

from skill_examples import read_example


class ArchiveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.requests.append(dict(self.headers))
        content = self.server.archive
        range_header = self.headers.get("Range")
        if range_header and self.headers.get("If-Range") == self.server.etag:
            start = int(range_header.removeprefix("bytes=").removesuffix("-"))
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{len(content)-1}/{len(content)}")
            content = content[start:]
        else:
            self.send_response(200)
        self.send_header("ETag", self.server.etag)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


@unittest.skipUnless(shutil.which("curl") and shutil.which("bash"), "curl and bash required")
class TransferTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("data.csv", "id,value\n01,42\n")
        self.archive = buffer.getvalue()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), ArchiveServer)
        self.server.archive, self.server.etag, self.server.requests = self.archive, '"edition-1"', []
        self.addCleanup(self.server.server_close)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(self.server.shutdown)

    def run_recipe(self, resume=False):
        reference, heading = (("references/transfers.md", "## Resume an interrupted transfer") if resume
                              else ("SKILL.md", "## Download a selected file"))
        recipe = read_example("geopf-download-files/" + reference, heading, language="bash")
        env = dict(os.environ, FILE_URL=f"http://127.0.0.1:{self.server.server_port}/archive.zip",
                   ETAG='"edition-1"', NO_PROXY="127.0.0.1", no_proxy="127.0.0.1")
        return subprocess.run(["bash", "-eu", "-c", recipe], cwd=self.output, env=env,
                              capture_output=True, text=True, timeout=15)

    def test_download_and_archive_integrity(self):
        result = self.run_recipe()
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.output / "package.zip.part"
        self.assertEqual(target.read_bytes(), self.archive)
        with zipfile.ZipFile(target) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.read("data.csv"), b"id,value\n01,42\n")

    def test_resume_matches_original_bytes(self):
        target = self.output / "package.zip.part"
        target.write_bytes(self.archive[:50])
        result = self.run_recipe(resume=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(target.read_bytes(), self.archive)
        self.assertEqual(self.server.requests[-1]["Range"], "bytes=50-")
        self.assertEqual(self.server.requests[-1]["If-Range"], '"edition-1"')

    def test_changed_edition_cannot_be_appended_to_partial_file(self):
        target = self.output / "package.zip.part"
        target.write_bytes(self.archive[:50])
        self.server.etag = '"edition-2"'
        result = self.run_recipe(resume=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_bytes(), self.archive[:50])
