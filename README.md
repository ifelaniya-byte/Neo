# Neo — Intelligence System

Neo is a repository for experimental AI systems, agent infrastructure, verification systems, research, training data, and deployment projects.

## Repository status

**Audit branch:** `reorg/exhaustive-architecture-pass`  
**Base:** `main` @ `bbc60d5e44ae99ce70c2198b21d44a34e2dd066c`  
**Audit date:** 2026-08-21

The repository's original commit describes a much larger source archive than the files actually tracked by Git. This branch treats the tracked repository as the source of truth and separates verified implementation from historical plans, experiments, and imported snapshots.

## Start here

1. [`00_START_HERE/README.md`](00_START_HERE/README.md) — existing orientation guide.
2. [`_INDEX_AND_METADATA/REPOSITORY_AUDIT.md`](_INDEX_AND_METADATA/REPOSITORY_AUDIT.md) — current audit findings and reorganization rules.
3. [`05_DOCUMENTATION/Architecture/REPOSITORY_ARCHITECTURE.md`](05_DOCUMENTATION/Architecture/REPOSITORY_ARCHITECTURE.md) — canonical architecture and ownership rules.
4. [`01_PROJECTS/Claw_OS/README.md`](01_PROJECTS/Claw_OS/README.md) — deployable Claw OS project.
5. [`01_PROJECTS/New_Neo/source/README.md`](01_PROJECTS/New_Neo/source/README.md) — New Neo implementation notes.

## Top-level contract

| Area | Purpose |
|---|---|
| `00_START_HERE/` | Human/agent orientation and entry points |
| `01_PROJECTS/` | Deployable or actively developed applications |
| `02_SYSTEMS/` | Reusable frameworks and system components |
| `03_MODELS_AND_WEIGHTS/` | Model artifacts and model metadata |
| `04_KNOWLEDGE_AND_DATA/` | Datasets, training material, and world-model data |
| `05_DOCUMENTATION/` | Architecture, strategy, setup, and reference documentation |
| `06_CONFIGURATION/` | Non-secret configuration and environment templates |
| `07_UTILITIES_AND_TOOLS/` | Verification, automation, profiling, and maintenance tools |
| `08_ARCHIVES_AND_BACKUPS/` | Historical archives; not runtime dependencies |
| `_INDEX_AND_METADATA/` | Repository indexes, manifests, and audit history |

## Important distinction

A document claiming that a component is "production ready" is not treated as proof that it is executable. Runtime readiness is established by source inspection, dependency inspection, and repeatable tests.

The current audit already found a concrete Claw OS container-layout defect: the Docker build context is `docker/`, while the Dockerfile copies `requirements.txt` and `claw_os_headless.py` as though they were in that context even though the tracked implementation is under `source/`. This branch fixes that path mismatch and adds the missing environment template.

## Security

Do not commit API keys, cookies, access tokens, model credentials, or real `.env` files. Use templates and local environment injection. The existing `.gitignore` contains secret patterns, but repository hygiene still requires reviewing tracked files before publication.
