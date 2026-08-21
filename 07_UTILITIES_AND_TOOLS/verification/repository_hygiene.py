#!/usr/bin/env python3
"""Static repository hygiene checks for Neo.

This script intentionally performs no network access and no destructive changes.
It validates the structural assumptions documented by the repository audit.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
ERRORS = []

REQUIRED_DIRS = [
    "00_START_HERE",
    "01_PROJECTS",
    "02_SYSTEMS",
    "03_MODELS_AND_WEIGHTS",
    "04_KNOWLEDGE_AND_DATA",
    "05_DOCUMENTATION",
    "06_CONFIGURATION",
    "07_UTILITIES_AND_TOOLS",
    "08_ARCHIVES_AND_BACKUPS",
    "_INDEX_AND_METADATA",
]

for rel in REQUIRED_DIRS:
    if not (ROOT / rel).is_dir():
        ERRORS.append(f"missing required directory: {rel}")

# The Claw OS Dockerfile must reference the source tree, not files that only
# exist inside docker/.
dockerfile = ROOT / "01_PROJECTS/Claw_OS/docker/Dockerfile"
if dockerfile.exists():
    text = dockerfile.read_text(encoding="utf-8")
    if "COPY source/requirements.txt" not in text:
        ERRORS.append("Claw OS Dockerfile does not copy source/requirements.txt")
    if "COPY source/claw_os_headless.py" not in text:
        ERRORS.append("Claw OS Dockerfile does not copy source/claw_os_headless.py")

compose = ROOT / "01_PROJECTS/Claw_OS/docker/docker-compose.yml"
if compose.exists():
    text = compose.read_text(encoding="utf-8")
    if "context: .." not in text:
        ERRORS.append("Claw OS compose file does not use the project-root build context")

# Documentation links should not reference the old imaginary top-level layout.
for doc in (ROOT / "00_START_HERE").rglob("*.md"):
    text = doc.read_text(encoding="utf-8", errors="replace")
    if "Intelligence_Restructured/" in text:
        ERRORS.append(f"stale root name in {doc.relative_to(ROOT)}")

if ERRORS:
    print("Repository hygiene: FAIL")
    for error in ERRORS:
        print(f"- {error}")
    sys.exit(1)

print("Repository hygiene: PASS")
print(f"Checked root: {ROOT}")
