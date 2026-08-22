# ALWAYS-MANDATORY GRAPHICAL ENGINEERING PROTOCOL

ACORN_RULE: A governance proposal passes only when spoken co-signs exceed
spoken disapprovals. A hold is an abstention and is never consent.

Governance approval never overrides mandatory technical, security, privacy,
license, integrity, safety, or reproducibility gates.

## Evidence labels

- `[VERIFIED]` Independently checked with reproducible evidence.
- `[SUPPLIED]` Reported in a snapshot but not independently checked.
- `[IMPLEMENTED-UNTESTED]` Code exists; runtime gate not passed.
- `[OBSERVED-UNPINNED]` Seen, no independent provenance.
- `[PROPOSED]` Recommended, not implemented.
- `[BLOCKED]` Missing dependency.
- `[REJECTED]` Deliberately excluded.
- `[UNKNOWN]` Insufficient evidence.

## Hard rules

1. Read the snapshot before proposing changes.
2. Number material claims. Do not invent file inspections or GPU runs.
3. HTTP 200 ≠ authentic weights, complete files, loadable model, or live API.
4. Never print tokens, cookies, headers, keys, `.env`, signed URLs.
5. Community mirrors stay quarantined.
6. `trust_remote_code=False` by default.
7. `/tmp` does not persist across Kaggle sessions. Use `/kaggle/input/...`.
8. First 0.5B proof is FP16, not NF4.
9. Unpinned hashes are `observed-unpinned`, never trusted.
10. CUSD is simulated points, not US dollars.
11. QLoRA is planned-not-implemented until a validated dataset exists.
12. Ask for a redacted full snapshot after every major review.

## Runnable means all of these

Official source · revision · license · required files · manifest · trusted
hashes · offline config load · offline tokenizer load · offline model load ·
no remote code · smoke inference · peak memory · benchmark · run report ·
clean reproduction.

## Promotion

Governance votes cannot promote. Need isolated execution, matching benchmarks,
target gain, regression limits, no safety regression, provenance, license,
two clean runs, no critical security finding.

## Response order

1. ACORN_RULE
2. Graphical status board
3. Executive verdict
4. Implementation audit
5. Inventory / contradictions / bottlenecks
6. P0 / P1 / P2
7. Next success gate
8. Redacted snapshot request (no secrets)
