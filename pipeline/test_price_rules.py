import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from price_rules import comparison_eligible


class PriceRulesTests(unittest.TestCase):
    def offer(self, **changes):
        return {"label": "Adult kart", "class": "adult", "type": "session", **changes}

    def test_standard_rate_with_alternative_prices(self):
        self.assertTrue(comparison_eligible(self.offer(note="student 16 EUR; 5 tickets 89 EUR")))

    def test_race_and_child_karts_not_compared(self):
        for changes in ({"class": "race"}, {"class": "kids"}, {"label": "2 temps"},
                        {"label": "Kid Racer", "class": "electric"}):
            with self.subTest(changes=changes):
                self.assertFalse(comparison_eligible(self.offer(**changes)))

    def test_packages_extras_and_specials(self):
        for changes in ({"type": "package"}, {"extras": True},
                        {"label": "Student session"}, {"day": "off-peak"},
                        {"note": "members get discount"}, {"note": "5 tickets only"}):
            with self.subTest(changes=changes):
                self.assertFalse(comparison_eligible(self.offer(**changes)))

    def test_explicit_flag_does_not_override_kart_class(self):
        self.assertFalse(comparison_eligible(self.offer(comparison_eligible=False)))
        self.assertFalse(comparison_eligible(self.offer(**{"class": "race", "comparison_eligible": True})))
        self.assertTrue(comparison_eligible(self.offer(note="discount mentioned", comparison_eligible=True)))


if __name__ == "__main__":
    unittest.main()
