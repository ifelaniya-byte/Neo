#!/usr/bin/env python3
import os
import unittest
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".kaggle", "__pycache__", ".git", "weights_offline", "tests"}
# live token *values* — never a full KGAT_ + hex body in public docs
import re
KGAT_VALUE = re.compile(r"KGAT_[0-9a-fA-F]{20,}")


class SecretTests(unittest.TestCase):
    def test_no_live_token_fragments_in_public_files(self):
        hits = []
        for path in Path(BASE).rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP for part in path.parts):
                continue
            if path.name in {"access_token", ".env", ".netrc"}:
                continue
            if path.suffix not in {".md", ".html", ".json", ".py", ".ipynb", ".yml", ".yaml", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if KGAT_VALUE.search(text):
                hits.append(str(path))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
