# Neo Repository Architecture

## Canonical ownership model

Neo is organized by responsibility, not by chronology or the source of an imported archive.

| Layer | Canonical responsibility |
|---|---|
| Projects | User-facing applications and experiments being actively developed |
| Systems | Reusable infrastructure shared by projects |
| Models | Weights and model metadata only |
| Knowledge/Data | Training corpora, datasets, embeddings, world-model material |
| Documentation | Human/agent-readable specifications and guides |
| Configuration | Non-secret configuration and templates |
| Utilities | Validation, automation, profiling, migration and maintenance |
| Archives | Historical snapshots that are not runtime dependencies |
| Index/Metadata | Inventory, provenance, audit and navigation |

## Project layout standard

Every project that becomes canonical should converge on:

```text
<project>/
├── src/          implementation
├── tests/        executable tests
├── scripts/      developer/ops tooling
├── docs/         project-specific documentation
├── config/       non-secret configuration
└── README.md
```

Legacy directories may remain temporarily when a move would break imports or provenance. In that case, they must be explicitly labeled as legacy/imported/snapshot material.

## New Neo rule

`01_PROJECTS/New_Neo/source/` currently contains several apparent generations and extracted workspaces. The canonical implementation must be selected by evidence: entry points, imports, tests, dependency manifests, and actual runtime behavior. A directory name such as `latest`, `clean`, `enhanced`, or `final` is not sufficient evidence of canonical status.

Repeated extracted files such as `worker_entry.py` and `program_census.py` are treated as snapshots until proven otherwise.

## Systems rule

`02_SYSTEMS/` contains reusable frameworks. A system must not be described as an integration dependency merely because an architecture document draws an arrow to it. Integration claims require code-level evidence.

## Data rule

Training data and imported source snapshots are knowledge/provenance artifacts unless a runtime module explicitly consumes them. Do not silently turn raw archives into runtime dependencies.

## Documentation rule

Documentation is classified as one of:

- **Specification:** defines current intended behavior.
- **Guide:** tells users/operators how to use verified behavior.
- **Research:** records an experiment or investigation.
- **Strategy:** records business/product direction.
- **Historical:** records an earlier state or migration.
- **Unverified:** contains claims that have not yet been validated.

Current architecture documents should not mix these categories without labels.

## Configuration rule

Only templates and non-secret defaults belong in Git. Real API keys, cookies, access tokens, private certificates, and production environment files remain local/secret.

## Archive rule

Archives are provenance, not executable source. If an archive contains the only copy of a required component, extract and validate that component before declaring the archive a dependency.

## Verification states

Use these states in indexes:

- `VERIFIED` — tested and observed.
- `IMPLEMENTED` — source exists but runtime verification is incomplete.
- `PARTIAL` — incomplete implementation.
- `EXPERIMENTAL` — intentionally unstable/research code.
- `HISTORICAL` — retained for provenance.
- `PLANNED` — documentation only.
- `UNVERIFIED` — claimed capability not yet demonstrated.

This vocabulary prevents optimistic documentation from being mistaken for executable capability.
