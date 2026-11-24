"""Local HTTP integration tests for the deployed-byte audit; no external network."""
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from verify_live import ROOT, ROUTES, ROBOTS_PREFIX, verify, verify_one
from src.archive.runtime_assets import RUNTIME_NAMES, runtime_path
from hashlib import sha256


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/good")
            self.end_headers()
            return
        if self.path == "/missing":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain" if self.path in {"/wrongtype", "/robots.txt"} else "text/html")
        self.send_header("Age", "120")
        self.end_headers()
        if self.path == "/robots.txt":
            self.wfile.write(ROBOTS_PREFIX.read_bytes() + (ROOT / "robots.txt").read_bytes())
        else:
            self.wfile.write(b"outdated" if self.path == "/stale" else b"<h1>Release</h1>")

    def log_message(self, *args):
        pass


class LiveAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_inventory_exists(self):
        for route, path in ROUTES.items():
            with self.subTest(route=route):
                self.assertTrue((ROOT / path).is_file())

    def test_runtime_routes_match_content(self):
        for name in RUNTIME_NAMES:
            data = (ROOT / "assets" / name).read_bytes()
            stem, suffix = name.split(".")
            expected = f"assets/{stem}.{sha256(data).hexdigest()}.{suffix}"
            self.assertEqual(runtime_path(name), expected)
            self.assertEqual(ROUTES["/" + expected], expected)
            self.assertEqual((ROOT / expected).read_bytes(), data)
            self.assertEqual(ROUTES["/assets/" + name], "assets/" + name)

    def test_managed_robots(self):
        self.assertIsNone(verify_one(self.base, "/robots.txt", ROOT / "robots.txt"))
        with tempfile.TemporaryDirectory() as directory:
            wrong = Path(directory) / "robots.txt"
            wrong.write_bytes(b"User-agent: *\nDisallow: /\n")
            self.assertIn("SHA-256 mismatch", verify_one(self.base, "/robots.txt", wrong))

    def test_actual_http(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "index.html"
            page.write_bytes(b"<h1>Release</h1>")
            self.assertIsNone(verify_one(self.base, "/good", page))
            stale = verify_one(self.base, "/stale", page)
            self.assertIn("SHA-256 mismatch", stale)
            self.assertIn("Age='120'", stale)
            self.assertIn("media type", verify_one(self.base, "/wrongtype", page))
            self.assertIn("302", verify_one(self.base, "/redirect", page))
            self.assertIn("404", verify_one(self.base, "/missing", page))
            self.assertEqual(verify(self.base, root, {"/good": "index.html"}, 1, 0), 0)
            self.assertEqual(verify(self.base, root, {"/stale": "index.html"}, 2, 0), 1)


    def test_full_confirmation_after_retry(self):
        calls = {"/a": 0, "/b": 0}

        def rotating(base, route, local):
            calls[route] += 1
            if route == "/a":
                return None if calls[route] == 1 else "/a: stale again"
            return "/b: stale" if calls[route] == 1 else None

        with patch("verify_live.verify_one", side_effect=rotating):
            self.assertEqual(verify(self.base, ROOT, {"/a": "index.html", "/b": "index.html"}, 2, 0), 1)
        self.assertEqual(calls, {"/a": 2, "/b": 3})

    def test_full_confirmation_recovers(self):
        calls = {"/a": 0, "/b": 0}

        def recovering(base, route, local):
            calls[route] += 1
            return "/b: stale" if route == "/b" and calls[route] == 1 else None

        with patch("verify_live.verify_one", side_effect=recovering):
            self.assertEqual(verify(self.base, ROOT, {"/a": "index.html", "/b": "index.html"}, 2, 0), 0)
        self.assertEqual(calls, {"/a": 2, "/b": 3})


if __name__ == "__main__":
    unittest.main()
