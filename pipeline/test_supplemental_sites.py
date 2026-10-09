import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SupplementalSiteTests(unittest.TestCase):
    def prepare(self, original, supplemental):
        with tempfile.TemporaryDirectory(prefix="kartatlas-sites-") as temporary:
            base = Path(temporary)
            (base / "geo").mkdir()
            for name, data in [
                ("sites_IT", original),
                ("sites_supplemental", supplemental),
                ("overrides", {}),
                ("geo/world", {"objects": {"countries": {"geometries": []}}, "arcs": []}),
            ]:
                (base / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
            subprocess.run(
                [sys.executable, "-I", str(Path(__file__).with_name("prep.py")), str(base), "IT"],
                check=True, capture_output=True,
            )
            return json.loads((base / "tracks.json").read_text(encoding="utf-8"))

    def site(self, ids, name="Pista Winner", country="IT"):
        return {
            "name": name, "lat": 44.784555, "lon": 8.375178, "kind": "outdoor",
            "len": None, "city": "Nizza Monferrato", "state": "Piemonte", "addr": None,
            "web": "https://www.pistawinner.it/", "phone": None, "hours": None,
            "osm": ids, "geo": None, "cc": country,
        }

    def test_addition_survives_preparation_and_respects_country(self):
        rows = self.prepare([], [self.site(["way/444163257"]), self.site(["node/2"], country="DE")])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["o"], "way/444163257")
        self.assertEqual(rows[0]["cc"], "IT")
        self.assertIsNone(rows[0]["g"])

    def test_future_extract_with_osm_alias_does_not_duplicate_addition(self):
        rows = self.prepare(
            [self.site(["node/1", "way/444163257"], name="Extracted venue")],
            [self.site(["way/444163257"])],
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["n"], "Extracted venue")
        self.assertEqual(rows[0]["o"], "node/1")


if __name__ == "__main__":
    unittest.main()
