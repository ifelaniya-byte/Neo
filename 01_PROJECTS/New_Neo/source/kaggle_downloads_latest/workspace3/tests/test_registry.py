#!/usr/bin/env python3
import unittest
import seat_registry


class RegistryTests(unittest.TestCase):
    def test_seat_statuses_sum_to_total(self):
        counts = seat_registry.counts()
        total = sum(counts[k] for k in (
            "verified-checkpoint", "verified-api",
            "community-quarantine", "logical-emulated"))
        self.assertEqual(total, counts["n"])

    def test_status_labels_valid(self):
        for s in seat_registry.SEATS:
            self.assertIn(s["status"], seat_registry.STATUSES)
            self.assertIn(s["domain"], seat_registry.DOMAINS)

    def test_no_duplicate_keys(self):
        keys = [s["key"] for s in seat_registry.SEATS]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
