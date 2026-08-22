# SROS Engineer-Verified Pass — 2026-08-21

## Governing rule

This pass is evidence-first. No implementation change is authorized merely because it is plausible, attractive, or present in an older roadmap. A change is eligible only when the engineer evidence supports it and the change preserves SROS's explicit validation/abstention contract.

## Collected evidence

The repository contains prior stationary/non-stationary double-pass records. The stationary records verify syntax/structure, arithmetic identity, finite values, and contradiction checks; the non-stationary records verify serialization, copy-isolated mutation probes, size bounds, and NaN/Inf exclusion. The recorded final double-pass verdict for tested artifacts is PASS.

A prior engineer self-upgrade artifact contains 11 proposals: 10 accepted and 1 blocked. Accepted themes are:

- enforce schemas at event/packet/label boundaries;
- dimensional consistency through constants data;
- optional formal identity checks;
- repeated-failure lookup through the ledger;
- mandatory adversarial CI;
- regime-specific calibration hooks;
- parallel double-pass batches;
- attach settled evidence to engineer reports;
- promotion queues for repeated human-confirmed patterns;
- differential audits across identical decision IDs.

The blocked proposal was to absorb "complete conclusive world physics". It is explicitly rejected and must not be implemented.

## Fresh SROS inspection

The current SROS implementation exposes four source modules: `models.py`, `engineers.py`, `solver.py`, and package initialization. The current test suite covers stationary default resolution, non-stationary abstention when no transition probe is bound, and explicit regime classification.

The stationary engineer is deliberately deterministic and conservative: without an external proposer it uses the declared operation vocabulary and validates that proposed operations are declared. The non-stationary engineer additionally requires a transition probe; without one it returns unresolved. This is a sound safety property and is preserved.

The current solver, however, allows a failed selected regime to fall back to the other regime. This is inconsistent with a strict evidence-first acceptance contract for non-stationary problems: a dynamic problem should not become resolved simply because the stationary engineer can produce a weaker reference proposal. The engineer evidence supports explicit verification and abstention, not silent weakening of the regime requirement.

## Verified changes authorized by this pass

1. **Remove unsafe cross-regime fallback by default.** The default policy now requires the selected regime's validation to pass. Fallback remains an explicit opt-in policy setting for controlled experiments.
2. **Strengthen the acceptance contract.** A result is resolved only when validation passes and the confidence is finite and within [0, 1].
3. **Add a provenance record to each resolution result.** The result identifies that acceptance came from the selected engineer and records the policy mode, without inventing domain correctness.
4. **Add engineer-focused tests for the above invariants.**
5. **Do not integrate Atlas, UAIR, New Neo, or other existing systems yet.** Their existing evidence is useful for candidate selection, but it is not sufficient proof of compatibility with the current SROS contracts.

## Explicitly not authorized

- no claim of general intelligence;
- no claim of complete physics/world knowledge;
- no automatic promotion of historical components into SROS;
- no live trading or autonomous external action;
- no removal of double-pass verification;
- no deletion of repository snapshots solely because they are duplicated.

## Final-review filter

After implementation, review every changed file against:

- engineer evidence above;
- SROS acceptance contract;
- stationary/non-stationary distinction;
- tests;
- repository architecture;
- security rules.

If a change cannot be justified by verified evidence, revert it rather than rationalize it.
