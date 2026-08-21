# Accepted Engineer Upgrades — Implementation Map

The engineer self-upgrade record contains 10 accepted roadmap items and one blocked item. All 10 accepted items are represented in the SROS pass as follows.

| Accepted item | Implementation | Gate/status |
|---|---|---|
| schema registry enforcement | `verification.SchemaRegistry` + SROS boundary schemas | Runtime |
| dimensional consistency via constants DB | `verification.ConstantsDB` | Explicit opt-in utility |
| optional SymPy identity checks | `verification.optional_sympy_identity` + formal-expression hook | Optional; abstains if unavailable |
| repeated failure ledger queries | `FailureLedger` + solver failure recording/query | Runtime |
| adversarial suite in CI | `adversarial_suite` + mandatory workflow stage | CI |
| regime-specific calibration | `CalibrationPolicy` in `ResolutionPolicy` | Runtime |
| parallel double-pass batches | `parallel_double_pass` | Utility |
| settled RAG evidence attachment | `attach_evidence` into validation metadata | Runtime metadata |
| promotion queue from human-confirmed patterns | `PromotionQueue` requires explicit human confirmation and minimum confirmations | Queue only; no auto-deploy |
| differential same-decision audit | `decision_fingerprint` / `differential_check` | Utility |

## Deliberately excluded

The only rejected proposal remains rejected: absorbing complete, conclusive world physics. The engineer record explicitly marks it BLOCKED.

## Safety interpretation

"Implemented" does not mean every mechanism automatically overrides domain validation. Optional formal checks, calibration, promotion, and differential tools remain explicit controls. Promotion never deploys code by itself. No live trading or autonomous external action was enabled.
