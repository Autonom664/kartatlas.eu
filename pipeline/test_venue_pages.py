import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from venue_pages import external_link, generate


class VenuePageTests(unittest.TestCase):
    def test_source_schemes(self):
        for value in ["javascript:alert(1)", "data:text/html,test", "file:///etc/passwd", "https://user:password@example.com", "https://"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                external_link(value, "Source")
        self.assertIn('href="https://example.com/"', external_link("example.com/", "<Source>"))
        self.assertIn("&lt;Source&gt;", external_link("HTTPS://example.com/", "<Source>"))

    def test_origin_validation(self):
        for origin in ["http://example.com", "https://example.com/path", "https://user:secret@example.com", "https://example.com/?query=1"]:
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                generate(Path("unused"), origin)

    def test_escaping_and_removed_venues(self):
        with tempfile.TemporaryDirectory(prefix="kartatlas-pages-") as temporary:
            base = Path(temporary) / "pipeline"
            base.mkdir()
            (base / "countries.json").write_text(json.dumps({"DK": {"name": "Denmark"}}))
            (base / "rates_meta.json").write_text(json.dumps({"date": "2026-10-08"}))
            tracks = [{"o": "node/1", "n": '<img src=x onerror="alert(1)">', "cc": "DK", "w": "https://example.com/"}]
            (base / "tracks.json").write_text(json.dumps(tracks))
            generate(base, "https://example.com")
            page = (base.parent / "public" / "venues" / "node-1" / "index.html").read_text()
            self.assertIn("&lt;img", page)
            self.assertNotIn("<img", page)
            self.assertIn("No eligible public adult session verified", page)
            (base / "tracks.json").write_text("[]")
            generate(base, "https://example.com")
            self.assertFalse((base.parent / "public" / "venues" / "node-1").exists())

    def test_invalid_venue_id(self):
        with tempfile.TemporaryDirectory(prefix="kartatlas-pages-") as temporary:
            base = Path(temporary) / "pipeline"
            base.mkdir()
            for name, value in [("countries", {}), ("rates_meta", {"date": "2026-10-08"}), ("tracks", [{"o": "way/1/../../escape"}])]:
                (base / f"{name}.json").write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError, "Unexpected venue ID"):
                generate(base, "https://example.com")


if __name__ == "__main__":
    unittest.main()
