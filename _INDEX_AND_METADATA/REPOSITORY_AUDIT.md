# Neo Repository Audit

**Date:** 2026-08-21  
**Audited ref:** `main` @ `bbc60d5e44ae99ce70c2198b21d44a34e2dd066c`  
**Working branch:** `reorg/exhaustive-architecture-pass`

## Scope

This audit uses the Git-tracked repository tree, file search, repository metadata, the initial commit diff, and targeted source/documentation inspection. The repository contains substantially more material than can be safely treated as one homogeneous application.

## Findings

### 1. The repository is an archive of multiple layers, not one application

The top level already separates projects, systems, knowledge/data, documentation, configuration, utilities, and indexes. That separation is useful and should remain the high-level contract.

### 2. New Neo contains multiple generations/snapshots

`01_PROJECTS/New_Neo/source/` contains active-looking Python modules alongside `BOOTSTRAP/`, `_mini_llm_separated/`, `council_extracted/`, `kaggle_files/`, and multiple `kaggle_downloads_latest/` workspaces. Search results also show repeated files such as `worker_entry.py` and `program_census.py` in several extracted trees. These should not be assumed to be independent implementations.

**Rule:** preserve imported snapshots, but do not treat every extracted copy as production source. The canonical runtime source must eventually be identified from imports, entry points, tests, and dependency manifests.

### 3. Documentation contains stale claims

The initial commit and `REORGANIZATION_COMPLETE.md` describe thousands of files, archives, credentials, and directories that are not equivalent to the current Git-tracked tree. `EXECUTIVE_SUMMARY.md` also contains dated business assumptions and a Claw OS SaaS recommendation. These are useful historical strategy artifacts, not runtime specifications.

**Rule:** date and classify strategic/historical documents rather than letting them define current architecture.

### 4. Architecture documentation is aspirational in places

`_INDEX_AND_METADATA/SYSTEM_MAP.md` describes components and paths that do not all correspond to the currently observed tree. It should be treated as an architecture hypothesis until validated against code.

**Rule:** architecture maps must distinguish `implemented`, `partial`, `planned`, `historical`, and `unverified`.

### 5. Claw OS has a concrete Docker layout defect

The tracked project places Python implementation under `01_PROJECTS/Claw_OS/source/`, while `docker/docker-compose.yml` uses `docker/` as the build context and the Dockerfile attempts to `COPY requirements.txt`, `claw_os_headless.py`, and `.env.example` from that context. Those files are not in the Docker context as written.

**Action:** make the Docker context the Claw OS project root and address source files explicitly, or move the Docker assets. The safer change is to make the project root the context so source remains canonical.

### 6. Claw OS documentation references a missing environment template

The README and manuals instruct users to copy `.env.example`, but the observed project tree shown in the repository does not contain a top-level `01_PROJECTS/Claw_OS/.env.example`.

**Action:** add a non-secret `.env.example` containing variable names and safe placeholders.

### 7. The two Claw OS implementations duplicate substantial logic

`source/claw_os.py` and `source/claw_os_headless.py` each define their own AI agent, X uploader, watcher, and processing logic. This creates behavioral drift risk.

**Rule:** the eventual canonical design should extract shared services into a package and leave GUI/headless modules as thin entry points.

### 8. The root `.gitignore` is overly broad in one place

It ignores `agent_runner.py` globally. Because `agent_runner.py` is an important-looking New Neo runtime component, a global filename rule can hide future source files unintentionally.

**Action:** scope ignore rules to generated/unwanted artifacts instead of globally ignoring meaningful source names.

### 9. Generated/compiled artifacts should be kept out of canonical source

The historical documentation claims thousands of Python files and compiled bytecode. The current search also reveals repeated extracted workspaces. These are valuable for provenance but should be separated from canonical source once dependency/reference analysis is complete.

## Reorganization target

The target is not a destructive purge. It is a layered repository:

```text
Neo/
├── 00_START_HERE/                 orientation
├── 01_PROJECTS/                   active applications
│   ├── Claw_OS/
│   └── New_Neo/
├── 02_SYSTEMS/                    reusable frameworks
├── 03_MODELS_AND_WEIGHTS/         model artifacts/metadata
├── 04_KNOWLEDGE_AND_DATA/         data and imported knowledge
├── 05_DOCUMENTATION/              current docs + historical strategy
├── 06_CONFIGURATION/              templates/non-secret config
├── 07_UTILITIES_AND_TOOLS/        verification/automation/maintenance
├── 08_ARCHIVES_AND_BACKUPS/       historical packages
└── _INDEX_AND_METADATA/           manifests, maps, audit trail
```

Within each active project, use:

```text
project/
├── src/            canonical implementation
├── tests/          executable tests
├── scripts/        developer/ops scripts
├── docs/           project-specific docs
├── config/         non-secret configuration
└── README.md
```

Do not perform large-scale moves until import/reference analysis proves that paths can change safely.

## Verification policy

A component is marked **verified** only after:

1. its entry points are identified;
2. imports resolve;
3. dependency declarations are present;
4. tests or smoke tests execute;
5. configuration requirements are documented;
6. documentation matches observed behavior.

## Immediate fixes made on this branch

- Added a canonical root `README.md`.
- Added this audit record.
- Created an isolated reorganization branch so `main` remains untouched.

## Next pass

1. Enumerate every tracked path and classify it.
2. Trace New Neo entry points and duplicate extracted trees.
3. Extract/compare dependency manifests.
4. Validate Claw OS locally where execution is possible.
5. Correct Docker and environment-template paths.
6. Update architecture/index documents from verified facts.
7. Move only proven-safe files.
8. Add automated repository hygiene checks.
