#!/usr/bin/env python3
"""Report non-overlapping local source sizes; no credentials are read."""
import argparse, json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SKIP = {'.git', '__pycache__', '.venv', 'venv', '.cache', '.pytest_cache', '.mypy_cache', '.ruff_cache'}

def tree_bytes(root, skip=set()):
    return sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not any(x in skip for x in p.relative_to(root).parts))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--release-dir', type=Path); ap.add_argument('--output', type=Path)
    a=ap.parse_args()
    source=tree_bytes(BASE, SKIP)
    git=tree_bytes(BASE / '.git') if (BASE / '.git').is_dir() else 0
    release=0
    if a.release_dir and a.release_dir.is_dir():
        release=sum(p.stat().st_size for p in a.release_dir.iterdir() if p.is_file() and p.name.startswith('council-'))
    data={'schema_version':1,'source_payload':{'bytes':source,'includes_git':False,'includes_releases':False},'git_metadata':{'bytes':git},'release_evidence_outside_source':{'bytes':release},'external_model_artifacts':{'bytes_present':0,'bytes_expected':988097824},'caches':{'bytes':0,'scope_complete':False},'total_present_nonoverlapping_bytes':source+git+release}
    text=json.dumps(data,indent=2)+'\n'
    if a.output: a.output.write_text(text,encoding='utf-8')
    print(text,end='')
if __name__=='__main__': main()
