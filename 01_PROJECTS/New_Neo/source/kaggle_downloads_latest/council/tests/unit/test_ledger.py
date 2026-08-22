#!/usr/bin/env python3
import json
import os
import unittest

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LedgerTests(unittest.TestCase):
    def test_ledger_balances(self):
        path = os.path.join(BASE, "usd_people.json")
        with open(path, encoding="utf-8") as f:
            ledger = json.load(f)
        people = ledger["people"]
        minted_sum = sum(int(p.get("minted", p.get("earned_usd", 0))) for p in people)
        available_sum = sum(int(p.get("available", p.get("available_usd", 0))) for p in people)
        self.assertEqual(minted_sum, ledger["global_minted"])
        self.assertEqual(available_sum, ledger.get("global_available", available_sum))
        self.assertGreaterEqual(ledger["escrow_locked"], 0)
        self.assertTrue(ledger.get("integrity_ok", minted_sum == ledger["global_minted"]))
        self.assertIn("not redeemable", (ledger.get("unit") or "").lower()
                      + (ledger.get("policy") or "").lower())

    def test_canonical_ledger_matches_people(self):
        with open(os.path.join(BASE, "usd_people.json"), encoding="utf-8") as f:
            people = json.load(f)
        with open(os.path.join(BASE, "usd_ledger.json"), encoding="utf-8") as f:
            raw = json.load(f)
        self.assertEqual(people["global_minted"], raw["global_minted"])
        self.assertEqual(
            sum(w["earned"] for w in raw["wallets"].values()),
            raw["global_minted"])


if __name__ == "__main__":
    unittest.main()
