"""IndexNow request and release guard tests; no external calls."""
import unittest
from unittest.mock import patch
from indexnow import KEY, KEY_PATH, PUBLIC_PAGES, SITE, payload, submit
from verify_live import ROOT, ROUTES


class IndexNowTests(unittest.TestCase):
    def test_payload(self):
        self.assertEqual(payload(["/", "/papers/", "/"])["urlList"],
                         [SITE + "/", SITE + "/papers/"])
        self.assertEqual(payload(["/"])["keyLocation"], SITE + KEY_PATH)
        self.assertEqual(payload(["/publications/"])["urlList"], [SITE + "/publications/"])
        for paths in ([], ["/demo/"], ["https://example.org/"], ["/papers/?x=1"]):
            with self.assertRaises(ValueError):
                payload(paths)

    def test_reviewed_notice(self):
        paths = (ROOT / '.github/indexnow-notice.txt').read_text().splitlines()
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(payload(paths)['urlList'])

    def test_key(self):
        self.assertEqual((ROOT / ROUTES[KEY_PATH]).read_text().strip(), KEY)
        self.assertTrue(all(path in ROUTES for path in PUBLIC_PAGES))

    @patch("indexnow.build_opener")
    @patch("indexnow.verify_one", return_value="stale release")
    def test_stale_release_never_submitted(self, verify, opener):
        with self.assertRaises(RuntimeError):
            submit(["/"])
        opener.assert_not_called()

    @patch("indexnow.build_opener")
    @patch("indexnow.verify_one", return_value=None)
    def test_accepted_submission(self, verify, opener):
        response = opener.return_value.open.return_value.__enter__.return_value
        response.status = 202
        submit(["/", "/papers/"])
        self.assertEqual(verify.call_count, 3)
        opener.return_value.open.assert_called_once()


if __name__ == "__main__":
    unittest.main()
