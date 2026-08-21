#!/usr/bin/env python3
"""Build a deterministic, source-only handoff ZIP and external v2 manifest.

The archive is never extracted or executed by this tool. Member hashes in the
external manifest are calculated from bytes read back from the completed ZIP,
not from the mutable source tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

EXCLUDED_PARTS = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache", ".mypy_cache", ".ruff_cache", "build", "dist", "out", ".arena", ".cache"}
EXCLUDED_NAMES = {".env", ".env.local", ".env.production", ".netrc", ".git-credentials", "access_token", "kaggle.json", "credentials", "credentials.json", "service-account.json", "id_rsa", "id_ed25519"}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx"}
WEIGHT_SUFFIXES = {".safetensors", ".bin", ".pt", ".pth", ".ckpt", ".onnx", ".gguf"}
FIXED_TIME = (2026, 8, 13, 0, 0, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def included_files(root: Path, outputs: set[Path]):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if path in outputs or any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix.lower() in SENSITIVE_SUFFIXES | WEIGHT_SUFFIXES:
            continue
        if path.is_symlink():
            print(f"SKIP_SYMLINK {rel.as_posix()}", file=sys.stderr)
            continue
        if path.is_file():
            yield path, rel.as_posix()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--release-id", required=True)
    ap.add_argument("--previous-release-id")
    args = ap.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = list(included_files(root, {output, manifest_path}))

    print(f"HANDOFF_RELEASE {args.release_id}")
    print("SOURCE_ROOT [REDACTED_PROJECT_ROOT]")
    print("POLICY source-only; excludes VCS/caches/env files/credential filenames/private-key suffixes/symlinks/weight extensions")
    print(f"INPUT_FILES {len(files)}")
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9, strict_timestamps=True) as zf:
        for path, arcname in files:
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    with zipfile.ZipFile(output) as zf:
        bad = zf.testzip()
        members = []
        for info in zf.infolist():
            data = zf.read(info.filename)
            members.append({"path": info.filename, "uncompressed_bytes": info.file_size,
                            "compressed_bytes": info.compress_size, "sha256": sha256_bytes(data)})
    if bad:
        raise RuntimeError(f"ZIP CRC verification failed: {bad}")
    manifest = {
        "schema_version": 2,
        "release_id": args.release_id,
        "previous_release_id": args.previous_release_id,
        "release_kind": "source-only",
        "weights_included": False,
        "canonical_commit": canonical_commit(root),
        "archive": output.name,
        "archive_bytes": output.stat().st_size,
        "archive_sha256": sha256_path(output),
        "zip_crc_verification": "PASS",
        "member_count": len(members),
        "uncompressed_payload_bytes": sum(m["uncompressed_bytes"] for m in members),
        "compressed_member_bytes": sum(m["compressed_bytes"] for m in members),
        "members": members,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"ARCHIVE {output.name}")
    print(f"ARCHIVE_BYTES {manifest['archive_bytes']}")
    print(f"ARCHIVE_SHA256 {manifest['archive_sha256']}")
    print(f"PAYLOAD_UNCOMPRESSED_BYTES {manifest['uncompressed_payload_bytes']}")
    print(f"MEMBER_COUNT {manifest['member_count']}")
    print("CRC_CHECK PASS")
    print(f"MANIFEST {manifest_path.name}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
