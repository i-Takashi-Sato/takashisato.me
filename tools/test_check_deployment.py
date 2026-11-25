"""Deterministic tests for release checking; no public requests."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from check_deployment import (
    Finding, Resource, compare, exit_status, inventory, local_file,
)


class DeploymentCheckTests(unittest.TestCase):
    def test_comparison_states(self):
        item = Resource("/", b"release")
        self.assertEqual(compare(item, lambda _: b"release").state, "match")
        self.assertEqual(compare(item, lambda _: b"previous").state, "different")

        def offline(_):
            raise OSError("offline")

        self.assertEqual(compare(item, offline).state, "unavailable")
        self.assertEqual(exit_status([Finding("/", "match")]), 0)
        self.assertEqual(exit_status([Finding("/", "different")]), 1)
        self.assertEqual(exit_status([Finding("/", "different"), Finding("/a", "unavailable")]), 2)

    def test_path_boundaries(self):
        for route in ("https://other.example/", "/../secret", "//external", "/a?b=c", "/a/./b"):
            with self.subTest(route=route), self.assertRaises(ValueError):
                local_file(Path("/tmp"), route)

    def test_inventory_and_fingerprint(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            css = "/assets/site." + sha256(b"css").hexdigest() + ".css"
            js = "/assets/site." + sha256(b"js").hexdigest() + ".js"
            local_file(root, css).write_bytes(b"css")
            local_file(root, js).write_bytes(b"js")
            (root / "index.html").write_text(
                f'<link rel="stylesheet" href="{css}"><script src="{js}"></script>',
                encoding="utf-8",
            )
            (root / "sitemap.xml").write_text(
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://takashisato.me/</loc></url></urlset>',
                encoding="utf-8",
            )
            for name in ("site.webmanifest", "feed.xml", "research-index.json", "llms.txt", "publications.json"):
                (root / name).write_text("fixture", encoding="utf-8")
            routes = {item.route for item in inventory(root)}
            self.assertEqual(len(routes), 9)
            self.assertIn("/publications.json", routes)
            local_file(root, css).write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                inventory(root)


if __name__ == "__main__":
    unittest.main()
