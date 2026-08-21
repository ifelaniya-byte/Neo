#!/usr/bin/env python3
import json
import os
import unittest
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NotebookTests(unittest.TestCase):
    def test_notebooks_have_no_saved_outputs(self):
        for path in Path(BASE).glob("*.ipynb"):
            notebook = json.loads(path.read_text(encoding="utf-8"))
            for i, cell in enumerate(notebook.get("cells", [])):
                self.assertFalse(cell.get("outputs"), f"saved output in {path} cell {i}")
                self.assertIsNone(cell.get("execution_count"))


if __name__ == "__main__":
    unittest.main()
