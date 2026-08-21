# SROS Engineer Verification Record

**Date:** 2026-08-21  
**Branch:** `sros/engineer-verified-pass-2026-08-21`

## Purpose

This record supersedes no prior architecture decision. It records the evidence filter used for this implementation pass and identifies exactly which changes were admitted.

## Collected repository evidence

The existing engineer ledger records stationary and non-stationary checks using a double-pass protocol. Stationary checks include AST parsing, structural definitions, arithmetic identity, finite numeric values, and contradiction checks. Non-stationary checks include serialization, mutation-isolation probes, bounded size, and NaN/Inf exclusion. The ledger records PASS outcomes for the inspected artifacts.

The existing self-upgrade brainstorm contains 11 proposals: 10 accepted and 1 blocked. Accepted proposals center on verification, provenance, calibration, adversarial testing, evidence attachment, and differential auditing. The blocked proposal would claim complete world physics and is explicitly excluded.

## Current SROS inspection

The SROS package contains explicit models, stationary/non-stationary engineer protocols, a solver, and tests. The stationary reference engineer validates operation vocabulary. The non-stationary reference engineer requires a transition probe and abstains when it is unavailable.

The prior solver permitted fallback from a failed regime to the alternate regime by default. This was identified as a contract weakness because a dynamic state could be silently converted into a stationary resolution. The verified pass changes this behavior to opt-in fallback.

## Admitted changes

### A. Strict regime acceptance

`ResolutionPolicy.allow_fallback` now defaults to `False`. Explicit fallback remains available for controlled experiments.

### B. Acceptance-bound confidence

SROS now requires validation to pass and confidence to be finite and in the closed interval `[0, 1]` before reporting `resolved`.

### C. Acceptance provenance

The validation report receives an explicit acceptance note identifying whether the result was accepted by the SROS contract.

### D. Contract tests

Tests now cover:

- finite confidence and acceptance notes;
- non-stationary abstention;
- absence of default cross-regime fallback;
- explicit opt-in fallback;
- stationary rejection of undeclared operations;
- non-stationary transition-probe requirement;
- successful non-stationary validation when a transition probe is bound.

## Deliberately unchanged

No Atlas, UAIR, New Neo, Claw OS, model, world-model, or historical snapshot was promoted into SROS by this pass. Their existence is evidence for future collection, not proof of compatibility.

No broad repository moves or deletions were made.

## Review verdict

The implementation changes are narrow and directly traceable to the existing engineer verification principle: strengthen verification and abstention without weakening the double-pass contract or making unsupported completeness claims.
