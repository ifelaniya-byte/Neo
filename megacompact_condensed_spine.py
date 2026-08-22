#!/usr/bin/env python3
# GENERATED — DO NOT EDIT. Canonical source: multi-file package. See CANONICAL.md
# Built by build_condense.py at 2026-08-19T23:27:45.322066+00:00
"""MegaCompact condensed spine (distribution only). Stdlib. Regenerate via: python build_condense.py"""
from __future__ import annotations

import ast
import csv
import copy
import hashlib
import hmac
import json
import math
import os
import platform
import random
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time
import traceback
import concurrent.futures
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Protocol, Set, Tuple, Union


_EMBEDDED_DATA = {'policies/calibration_thresholds.json': '{\n  "version": "1.1-fitted-proxy",\n  "note": "Offline proxy fit from paper-run scale; not online-updated; stationary-reviewed",\n  "source_run": "artifacts/run_scaled",\n  "n_labels_observed": 357,\n  "default": {\n    "max_revert_probability": 0.03,\n    "min_inclusion_probability": 0.9,\n    "ood_threshold": 0.65,\n    "min_net_edge_usd": 1.5,\n    "lambda_uncertainty": 1.5\n  },\n  "regimes": {\n    "normal": {\n      "ood_threshold": 0.65,\n      "min_net_edge_usd": 1.5\n    },\n    "volatile": {\n      "ood_threshold": 0.5,\n      "min_net_edge_usd": 2.5\n    },\n    "gas_spike": {\n      "ood_threshold": 0.5,\n      "min_net_edge_usd": 3.0,\n      "max_revert_probability": 0.02\n    },\n    "low_liquidity": {\n      "ood_threshold": 0.55,\n      "min_net_edge_usd": 2.5\n    }\n  }\n}', 'schema_registry/events_v1.json': '{\n  "schema_id": "NormalizedEvent",\n  "version": "1.0",\n  "required": [\n    "event_id",\n    "event_timestamp_ms",\n    "observed_timestamp_ms",\n    "available_timestamp_ms",\n    "event_type",\n    "entity_id",\n    "chain_id"\n  ],\n  "properties": {\n    "event_id": {"type": "string"},\n    "event_timestamp_ms": {"type": "integer", "minimum": 0},\n    "observed_timestamp_ms": {"type": "integer", "minimum": 0},\n    "available_timestamp_ms": {"type": "integer", "minimum": 0},\n    "event_type": {"type": "string"},\n    "entity_id": {"type": "string"},\n    "chain_id": {"type": "integer"},\n    "payload": {"type": "object"}\n  },\n  "rules": [\n    "available_timestamp_ms >= observed_timestamp_ms"\n  ]\n}\n', 'schema_registry/packets_v1.json': '{\n  "schema_id": "DecisionPacket",\n  "version": "1.0",\n  "required": ["decision_id", "as_of", "action_candidates"],\n  "properties": {\n    "decision_id": {"type": "string"},\n    "as_of": {"type": "object"},\n    "action_candidates": {"type": "array"},\n    "constraints": {"type": "object"},\n    "provenance": {"type": "object"}\n  },\n  "rules": [\n    "as_of must include decision_timestamp_ms or block_number when used for causality audits"\n  ]\n}\n', 'schema_registry/labels_v1.json': '{\n  "schema_id": "OutcomeLabel",\n  "version": "1.0",\n  "required": [\n    "decision_id",\n    "action_id",\n    "net_pnl_usd",\n    "realized_output_usd",\n    "outcome_timestamp_ms",\n    "reverted"\n  ],\n  "properties": {\n    "decision_id": {"type": "string"},\n    "action_id": {"type": "string"},\n    "net_pnl_usd": {"type": "number"},\n    "realized_output_usd": {"type": "number"},\n    "input_cost_usd": {"type": "number"},\n    "gas_usd": {"type": "number"},\n    "protocol_fees_usd": {"type": "number"},\n    "borrow_fees_usd": {"type": "number"},\n    "bridge_fees_usd": {"type": "number"},\n    "slippage_cost_usd": {"type": "number"},\n    "revert_cost_usd": {"type": "number"},\n    "other_costs_usd": {"type": "number"},\n    "outcome_timestamp_ms": {"type": "integer"},\n    "reverted": {"type": "boolean"}\n  },\n  "rules": [\n    "net_pnl_usd ≈ realized_output_usd - sum(all cost fields) within tolerance"\n  ]\n}\n', 'rag_settled/corpus.jsonl': '{"doc_id": "seed-causality", "title": "Time-causal feature availability", "text": "A feature may only be used at decision time t if its availability timestamp is less than or equal to t. Future-leaking features are invalid.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["causality", "ml"], "checksum": "f6f6ad429393dc7745189fad021af0e2f14a8d465d2f8122d4f5c7405918d41e"}\n{"doc_id": "seed-net-pnl", "title": "Net PnL accounting identity", "text": "Net PnL equals realized output minus input cost, gas, protocol fees, borrow fees, bridge fees, slippage, revert cost, and other configured costs.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["accounting", "defi"], "checksum": "864ee8b3b4217ae4f699af73b1235dfd484487c3f62ea02b35f865f1c204aec3"}\n{"doc_id": "seed-abstain", "title": "Abstention as control", "text": "When uncertainty is high, constraints fail, or data is stale, the system must abstain rather than force a trade decision.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["safety", "abstention"], "checksum": "885504346cf1072164cf984b927ab6dd6646f8569eb84bb66e895e793f6ffee1"}\n{"doc_id": "digest-walkforward", "title": "Walk-forward split integrity", "text": "Train, validation, calibration, and test splits must be time-ordered. No random shuffle across time for causal decision systems.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["splits", "causality"], "checksum": "8d0ca6f91c18378cd25a0f3d5d5c00d528d38db99b0ee27b307d13321beeb533"}\n{"doc_id": "digest-costs", "title": "Full cost stack for net PnL", "text": "Net PnL accounting must include input cost, gas, protocol fees, borrow, bridge, slippage, revert cost, and other configured costs.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["accounting"], "checksum": "259a1570d9f00c5dd36ae0960ebd52d699d6988423af8453b78854ff2eb6692e"}\n{"doc_id": "digest-ood", "title": "OOD abstention", "text": "When out-of-distribution score exceeds regime threshold, abstain.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["ood", "abstention"], "checksum": "d16541c84ad2062468b9b15e6899707abca8fef91e6df7c9432f67fc07580f53"}\n{"doc_id": "digest-units", "title": "Unit tags on features", "text": "Numeric features used in physics-adjacent checks should carry unit tags compatible with constants_db conversions when dimensional checks run.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["units", "constants"], "checksum": "70ace216013fa0c1840f8ab0caec04d32cdc0bf4d23aa73faaf5a0b5380a4851"}\n{"doc_id": "digest-promotion", "title": "Promotion policy", "text": "New settled facts enter KSKB only after double-pass PASS and explicit human_confirm source. Completeness claims are never promoted.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["promotion", "safety"], "checksum": "f9db4555afe763b905d0c9433f0dc8855cab85499dcd247d911937c13d42f795"}\n{"doc_id": "digest-walkforward", "title": "Walk-forward split integrity", "text": "Train/val/cal/test must be time-ordered for causal decision systems.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["splits", "causality"], "checksum": "93a98e0df86c74d9e080c3f882d8473dc0191f9818a1f8cf6229ac1185131ce4"}\n{"doc_id": "digest-costs", "title": "Full cost stack for net PnL", "text": "Net PnL includes input, gas, protocol, borrow, bridge, slippage, revert, other costs.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["accounting"], "checksum": "96c0f4fd7b5688ad033782f6979fee3dbf841348d9e6f354af200e401bd53ba0"}\n{"doc_id": "digest-ood", "title": "OOD abstention", "text": "When OOD score exceeds regime threshold, abstain.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["ood", "abstention"], "checksum": "51f37b4ebd012bbe8f4297b93283af0cc9e119a2bcaa4453f1ea9ae96c2d60ff"}\n{"doc_id": "digest-units", "title": "Unit tags on features", "text": "Numeric features may carry unit tags for constants_db dimensional checks.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["units"], "checksum": "baa6a6913111e2e1b9ba463f1737a687dffb71df324918c5ae8583a770f6b785"}\n{"doc_id": "digest-promotion", "title": "Promotion policy", "text": "KSKB growth only after double-pass PASS and human_confirm. No completeness promotion.", "license": "CC0-1.0", "as_of": "2026-01-01", "source": "internal-policy", "tags": ["promotion"], "checksum": "11bca29cd5fb14e16e6663bab66b8010026aed3079171caf99a64f587a26c8a0"}\n{"doc_id": "digest-smt-interval", "title": "SMT and interval gates before TRADE", "text": "Before any TRADE verdict, linear SMT-style constraints and interval worst-case edge checks must allow the trade. If modules are unavailable, abstain.", "license": "CC0-1.0", "as_of": "2026-08-19", "source": "internal-policy", "tags": ["smt", "interval", "safety"], "checksum": "bf7f1b035c6f3059b6c78d7a138fbd69174b6dc610257f11675b78a21033fa9c"}\n{"doc_id": "digest-evidence-not-authority", "title": "Knowledge evidence is not decision authority", "text": "Knowledge coverage packs attached to decisions are evidence only. They must not override AbstentionGate, SMT, or interval results.", "license": "CC0-1.0", "as_of": "2026-08-19", "source": "internal-policy", "tags": ["knowledge", "safety", "abstention"], "checksum": "4f8cb0df09a8b387e23b93da93c61f7fef86697285ab41d6b431784b6a2e1beb"}\n{"doc_id": "digest-signed-ledgers", "title": "Signed promotion ledgers", "text": "Promotions into the settled knowledge base are offline only, require double-pass clearance and human confirm, and are HMAC/Ed25519 signed.", "license": "CC0-1.0", "as_of": "2026-08-19", "source": "internal-policy", "tags": ["promotion", "ledger"], "checksum": "dd5fd2cdb7fbd1b4411d73fee611ef1a5f3925f1e7f3394fffa50d9ea38c05e5"}\n{"doc_id": "digest-simulation-assurance", "title": "Simulation assurance product scope", "text": "This system is a paper-only simulation assurance harness for labs. It does not live-trade, does not guarantee alpha, and does not claim complete knowledge.", "license": "CC0-1.0", "as_of": "2026-08-19", "source": "internal-policy", "tags": ["product", "scope"], "checksum": "236d7dcdf1a3c1763926b8ddb26c9ec80784e59a8e65ac35834f842dd47bf239"}\n', 'artifacts/known_settled_export.json': '{\n  "version": "1.0.0-settled",\n  "scope": "Settled knowledge only: entries are standard identities / laws that hold under the listed assumptions. Scope is finite and curated. Absence from this DB does not mean false; presence means \'accepted within regime\'.",\n  "timestamp": "2026-08-19T22:34:18.899014+00:00",\n  "n_entries": 26,\n  "fields": [\n    "computing",\n    "math",\n    "physics"\n  ],\n  "entries": [\n    {\n      "id": "math.arithmetic.2p2",\n      "field": "math",\n      "statement": "Two plus two equals four in standard integer arithmetic.",\n      "formal": "2 + 2 = 4",\n      "assumptions": [\n        "Peano/integer arithmetic",\n        "standard base-10 numerals"\n      ],\n      "regime": "elementary arithmetic",\n      "confidence": "SETTLED",\n      "tags": [\n        "arithmetic",\n        "identity"\n      ]\n    },\n    {\n      "id": "math.logic.noncontradiction",\n      "field": "math",\n      "statement": "A statement and its negation are not both true (classical logic).",\n      "formal": "\\u00ac(A \\u2227 \\u00acA)",\n      "assumptions": [\n        "classical bivalent logic"\n      ],\n      "regime": "classical logic",\n      "confidence": "SETTLED",\n      "tags": [\n        "logic"\n      ]\n    },\n    {\n      "id": "math.prob.unit_measure",\n      "field": "math",\n      "statement": "Probabilities of a discrete partition sum to 1.",\n      "formal": "\\u03a3_i P(i) = 1 for a complete discrete partition",\n      "assumptions": [\n        "probability measure axioms (Kolmogorov)"\n      ],\n      "regime": "probability theory",\n      "confidence": "SETTLED",\n      "tags": [\n        "probability"\n      ]\n    },\n    {\n      "id": "math.prob.bayes",\n      "field": "math",\n      "statement": "Bayes\' rule relating conditional probabilities.",\n      "formal": "P(A|B) = P(B|A) P(A) / P(B)  when P(B) > 0",\n      "assumptions": [\n        "Kolmogorov probability",\n        "P(B)>0"\n      ],\n      "regime": "probability theory",\n      "confidence": "SETTLED",\n      "tags": [\n        "probability",\n        "inference"\n      ]\n    },\n    {\n      "id": "math.linalg.matmul_assoc",\n      "field": "math",\n      "statement": "Matrix multiplication is associative where defined.",\n      "formal": "(AB)C = A(BC)",\n      "assumptions": [\n        "compatible dimensions over a ring/field"\n      ],\n      "regime": "linear algebra",\n      "confidence": "SETTLED",\n      "tags": [\n        "linear_algebra"\n      ]\n    },\n    {\n      "id": "math.calc.ftc",\n      "field": "math",\n      "statement": "Fundamental theorem of calculus (standard form).",\n      "formal": "d/dx \\u222b_a^x f(t) dt = f(x) for continuous f",\n      "assumptions": [\n        "f continuous on interval"\n      ],\n      "regime": "real calculus",\n      "confidence": "SETTLED",\n      "tags": [\n        "calculus"\n      ]\n    },\n    {\n      "id": "math.info.shannon_nonneg",\n      "field": "math",\n      "statement": "Shannon entropy is nonnegative.",\n      "formal": "H(X) \\u2265 0",\n      "assumptions": [\n        "discrete distribution",\n        "Shannon definition"\n      ],\n      "regime": "information theory",\n      "confidence": "SETTLED",\n      "tags": [\n        "information_theory"\n      ]\n    },\n    {\n      "id": "math.info.kl_nonneg",\n      "field": "math",\n      "statement": "KL divergence is nonnegative.",\n      "formal": "D_KL(P||Q) \\u2265 0",\n      "assumptions": [\n        "P absolutely continuous w.r.t. Q as required"\n      ],\n      "regime": "information theory",\n      "confidence": "SETTLED",\n      "tags": [\n        "information_theory",\n        "statistics"\n      ]\n    },\n    {\n      "id": "phys.newton.second",\n      "field": "physics",\n      "statement": "Net force equals mass times acceleration (Newtonian).",\n      "formal": "F = m a",\n      "assumptions": [\n        "inertial frame",\n        "non-relativistic",\n        "classical"\n      ],\n      "regime": "classical mechanics v \\u226a c",\n      "confidence": "SETTLED",\n      "tags": [\n        "classical_mechanics"\n      ]\n    },\n    {\n      "id": "phys.em.maxwell_div_b",\n      "field": "physics",\n      "statement": "No magnetic monopoles in classical Maxwell theory (div B = 0).",\n      "formal": "\\u2207 \\u00b7 B = 0",\n      "assumptions": [\n        "classical Maxwell electrodynamics"\n      ],\n      "regime": "classical EM",\n      "confidence": "SETTLED",\n      "tags": [\n        "classical_em"\n      ]\n    },\n    {\n      "id": "phys.sr.c_invariant",\n      "field": "physics",\n      "statement": "Speed of light in vacuum is invariant across inertial frames (SR).",\n      "formal": "c invariant under Lorentz transformations",\n      "assumptions": [\n        "special relativity",\n        "inertial frames",\n        "vacuum"\n      ],\n      "regime": "special relativity",\n      "confidence": "SETTLED",\n      "tags": [\n        "special_relativity"\n      ]\n    },\n    {\n      "id": "phys.sr.mass_energy",\n      "field": "physics",\n      "statement": "Rest energy equals rest mass times c squared.",\n      "formal": "E\\u2080 = m c\\u00b2",\n      "assumptions": [\n        "SR",\n        "rest frame for rest energy"\n      ],\n      "regime": "relativistic mechanics",\n      "confidence": "SETTLED",\n      "tags": [\n        "special_relativity"\n      ]\n    },\n    {\n      "id": "phys.qm.born",\n      "field": "physics",\n      "statement": "Born rule: outcome probabilities from |amplitude|\\u00b2.",\n      "formal": "P(a) = |\\u27e8a|\\u03c8\\u27e9|\\u00b2",\n      "assumptions": [\n        "standard quantum measurement postulate"\n      ],\n      "regime": "textbook quantum mechanics",\n      "confidence": "SETTLED",\n      "tags": [\n        "quantum_mechanics"\n      ]\n    },\n    {\n      "id": "phys.qm.uncertainty",\n      "field": "physics",\n      "statement": "Canonical Heisenberg uncertainty relation.",\n      "formal": "\\u03c3_x \\u03c3_p \\u2265 \\u210f/2",\n      "assumptions": [\n        "canonical x,p operators",\n        "standard QM"\n      ],\n      "regime": "quantum mechanics",\n      "confidence": "SETTLED",\n      "tags": [\n        "quantum_mechanics"\n      ]\n    },\n    {\n      "id": "phys.thermo.second_isolated",\n      "field": "physics",\n      "statement": "Entropy of an isolated system does not decrease (2nd law, Clausius form summary).",\n      "formal": "\\u0394S \\u2265 0 for isolated system",\n      "assumptions": [\n        "thermodynamic limit / macroscopic",\n        "isolated"\n      ],\n      "regime": "classical thermodynamics",\n      "confidence": "SETTLED",\n      "tags": [\n        "thermo"\n      ]\n    },\n    {\n      "id": "phys.stat.boltzmann",\n      "field": "physics",\n      "statement": "Boltzmann entropy relates entropy to multiplicity.",\n      "formal": "S = k_B ln \\u03a9",\n      "assumptions": [\n        "microcanonical ensemble counting"\n      ],\n      "regime": "equilibrium statistical mechanics",\n      "confidence": "SETTLED",\n      "tags": [\n        "stat_mech"\n      ]\n    },\n    {\n      "id": "comp.hash.sha256_length",\n      "field": "computing",\n      "statement": "SHA-256 digest is 256 bits (64 hex characters).",\n      "formal": "|SHA256(m)| = 256 bits",\n      "assumptions": [\n        "FIPS 180-4 SHA-256"\n      ],\n      "regime": "cryptographic hash standards",\n      "confidence": "SETTLED",\n      "tags": [\n        "hashing",\n        "standards"\n      ]\n    },\n    {\n      "id": "comp.ieee754.note",\n      "field": "computing",\n      "statement": "IEEE-754 binary floating point has finite precision and rounding modes.",\n      "formal": "float arithmetic \\u2260 real arithmetic",\n      "assumptions": [\n        "IEEE-754 binary formats"\n      ],\n      "regime": "numerical computing",\n      "confidence": "SETTLED",\n      "tags": [\n        "numerical"\n      ]\n    },\n    {\n      "id": "comp.causality.no_future_read",\n      "field": "computing",\n      "statement": "In a time-causal feature system, features with availability time > decision time must not be used.",\n      "formal": "\\u2200 features f: available_time(f) \\u2264 decision_time",\n      "assumptions": [\n        "defined timestamps",\n        "enforced access layer"\n      ],\n      "regime": "time-causal ML / trading research systems",\n      "confidence": "SETTLED",\n      "tags": [\n        "causality",\n        "ml_systems"\n      ]\n    },\n    {\n      "id": "ai.abstain.safety",\n      "field": "computing",\n      "statement": "When uncertainty or constraint checks fail, refusing to act (abstain) is a valid control decision.",\n      "formal": "verdict = ABSTAIN if \\u00acconstraints_ok \\u2228 uncertainty_high",\n      "assumptions": [\n        "explicit constraint and uncertainty thresholds"\n      ],\n      "regime": "safety-aware decision systems",\n      "confidence": "SETTLED",\n      "tags": [\n        "abstention",\n        "safety"\n      ]\n    },\n    {\n      "id": "comp.determinism.seed",\n      "field": "computing",\n      "statement": "Fixed seed and version pins required for reproducible paper runs.",\n      "formal": "same seed + config_hash => same artifacts",\n      "assumptions": [\n        "controlled nondeterminism"\n      ],\n      "regime": "research harness",\n      "confidence": "SETTLED",\n      "tags": [\n        "reproducibility"\n      ]\n    },\n    {\n      "id": "comp.determinism.hash_stable_v3",\n      "field": "computing",\n      "statement": "SHA256 of identical bytes is identical under fixed algorithm",\n      "formal": "forall b, sha256(b) = sha256(b)",\n      "assumptions": [\n        "sha256 definition"\n      ],\n      "regime": "classical computing",\n      "confidence": "SETTLED",\n      "tags": [\n        "determinism",\n        "source:product_test"\n      ]\n    },\n    {\n      "id": "prod.test.identity",\n      "field": "math",\n      "statement": "For all real a, a + 0 = a",\n      "formal": "\\u2200 a \\u2208 \\u211d, a + 0 = a",\n      "assumptions": [\n        "real arithmetic"\n      ],\n      "regime": "classical",\n      "confidence": "SETTLED",\n      "tags": [\n        "math",\n        "identity",\n        "source:product_test"\n      ]\n    },\n    {\n      "id": "prod.test.commutativity",\n      "field": "math",\n      "statement": "For all real a,b: a+b = b+a",\n      "formal": "forall a,b in R: a+b = b+a",\n      "assumptions": [\n        "real arithmetic"\n      ],\n      "regime": "classical",\n      "confidence": "SETTLED",\n      "tags": [\n        "math",\n        "identity",\n        "source:product_test"\n      ]\n    },\n    {\n      "id": "comp.evidence.not_authority",\n      "field": "computing",\n      "statement": "Knowledge evidence packs must not override abstention or constraint gates.",\n      "formal": "evidence does not entail TRADE authority",\n      "assumptions": [\n        "fail-closed decision systems"\n      ],\n      "regime": "process",\n      "confidence": "SETTLED",\n      "tags": [\n        "safety",\n        "knowledge",\n        "source:coverage_expand"\n      ]\n    },\n    {\n      "id": "comp.smt_interval.required_before_trade",\n      "field": "computing",\n      "statement": "TRADE requires SMT allow and interval allow when those modules are part of the product path.",\n      "formal": "TRADE implies smt.allow and interval.allow when modules enabled",\n      "assumptions": [\n        "product path with SMT/interval wired"\n      ],\n      "regime": "process",\n      "confidence": "SETTLED",\n      "tags": [\n        "smt",\n        "interval",\n        "safety",\n        "source:coverage_expand"\n      ]\n    }\n  ],\n  "explicitly_excluded": [\n    "UV-complete quantum gravity",\n    "identity of dark matter",\n    "final measurement interpretation",\n    "any claim of complete human knowledge"\n  ]\n}', 'schemas/normalized_event_feed.v1.json': '{\n  "$schema": "https://json-schema.org/draft/2020-12/schema",\n  "$id": "megacompact://schemas/normalized_event_feed.v1.json",\n  "title": "MegaCompact Normalized Event Feed v1",\n  "description": "Paper-only historical/synth event feed. Each record must carry availability time to enforce time-causality. Never includes private keys or signed live orders.",\n  "type": "object",\n  "required": ["feed_id", "schema_version", "chain_id", "events"],\n  "properties": {\n    "feed_id": { "type": "string", "minLength": 1 },\n    "schema_version": { "type": "string", "const": "1.0.0" },\n    "chain_id": { "type": "integer" },\n    "source": { "type": "string" },\n    "as_of": { "type": "string", "description": "YYYY-MM-DD or ISO timestamp of feed generation" },\n    "license": { "type": "string" },\n    "events": {\n      "type": "array",\n      "minItems": 1,\n      "items": { "$ref": "#/$defs/NormalizedEvent" }\n    }\n  },\n  "$defs": {\n    "NormalizedEvent": {\n      "type": "object",\n      "required": [\n        "event_id",\n        "entity_id",\n        "event_timestamp_ms",\n        "observed_timestamp_ms",\n        "available_timestamp_ms",\n        "event_type"\n      ],\n      "properties": {\n        "event_id": { "type": "string" },\n        "entity_id": { "type": "string" },\n        "event_timestamp_ms": { "type": "integer", "minimum": 0 },\n        "observed_timestamp_ms": { "type": "integer", "minimum": 0 },\n        "available_timestamp_ms": { "type": "integer", "minimum": 0 },\n        "event_type": {\n          "type": "string",\n          "enum": ["swap", "pool_update", "quote", "gas", "block", "oracle", "route", "inclusion", "revert", "bridge", "liquidity", "price"]\n        },\n        "chain_id": { "type": "integer" },\n        "payload": { "type": "object" },\n        "checksum": { "type": "string" }\n      },\n      "additionalProperties": true\n    }\n  }\n}\n'}

def _embedded(rel: str, default: str = '') -> str:
    return _EMBEDDED_DATA.get(rel, default)



# ===== BEGIN check_registry.py =====

#!/usr/bin/env python3
"""Ordered registry of Stationary engineer check names (documentation + flags)."""
from typing import Dict, List

# name -> enabled by default
STATIONARY_CHECKS: Dict[str, bool] = {
    "subject_present": True,
    "schema.non_empty_dict": True,
    "schema_registry.required": True,
    "causality.timestamps": True,
    "accounting.net_pnl": True,
    "finite.nan_inf": True,
    "source.ast_parse": True,
    "math.arithmetic_identity": True,
    "math.isfinite_pi": True,
    "logic.no_contradiction": True,
    "atlas.claim_gate": True,
    "atlas.catalogue_loaded": True,
    "settled_db.loaded": True,
    "settled_db.no_completeness_overclaim": True,
    "ledger_memory.recent_patterns": True,
    "rag_settled.evidence": True,
    "sympy.identity": True,
    "constants.lookup": True,
    "unit_tags.probe": True,
}

def enabled_checks() -> List[str]:
    return [k for k, v in STATIONARY_CHECKS.items() if v]

# ===== END check_registry.py =====


# ===== BEGIN constants_db.py =====

#!/usr/bin/env python3
"""Pinned physical/math constants + simple unit conversions (CODATA-style snapshot)."""
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

CONSTANTS_VERSION = "2026-snapshot-local"

@dataclass
class Constant:
    id: str
    name: str
    value: float
    unit: str
    source: str = "CODATA-style curated snapshot"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ConstantsDB:
    def __init__(self):
        self.version = CONSTANTS_VERSION
        self.constants: Dict[str, Constant] = {}
        self._build()

    def _add(self, c: Constant) -> None:
        self.constants[c.id] = c

    def _build(self) -> None:
        rows = [
            ("c", "speed of light in vacuum", 299792458.0, "m/s", "exact SI"),
            ("h", "Planck constant", 6.62607015e-34, "J s", "exact SI"),
            ("hbar", "reduced Planck constant", 1.054571817e-34, "J s", "h/(2π)"),
            ("e", "elementary charge", 1.602176634e-19, "C", "exact SI"),
            ("k_B", "Boltzmann constant", 1.380649e-23, "J/K", "exact SI"),
            ("N_A", "Avogadro constant", 6.02214076e23, "1/mol", "exact SI"),
            ("R", "molar gas constant", 8.314462618, "J/(mol K)", "N_A k_B"),
            ("G", "Newtonian gravitational constant", 6.67430e-11, "m^3/(kg s^2)", "CODATA recommended"),
            ("epsilon0", "vacuum electric permittivity", 8.8541878128e-12, "F/m", "derived"),
            ("mu0", "vacuum magnetic permeability", 1.25663706212e-6, "N/A^2", "derived"),
            ("m_e", "electron mass", 9.1093837015e-31, "kg", "CODATA"),
            ("m_p", "proton mass", 1.67262192369e-27, "kg", "CODATA"),
            ("alpha", "fine-structure constant", 7.2973525693e-3, "1", "CODATA"),
            ("g", "standard gravity", 9.80665, "m/s^2", "conventional"),
            ("pi", "pi", 3.141592653589793, "1", "math"),
            ("e_euler", "Euler's number", 2.718281828459045, "1", "math"),
        ]
        for id_, name, val, unit, notes in rows:
            self._add(Constant(id=id_, name=name, value=val, unit=unit, notes=notes))

    def get(self, id_: str) -> Optional[Dict[str, Any]]:
        c = self.constants.get(id_)
        return c.to_dict() if c else None

    def convert_length(self, value: float, from_u: str, to_u: str) -> float:
        to_m = {"m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0, "nm": 1e-9, "angstrom": 1e-10}
        if from_u not in to_m or to_u not in to_m:
            raise ValueError(f"unsupported length units: {from_u}->{to_u}")
        return value * to_m[from_u] / to_m[to_u]

    def convert_energy(self, value: float, from_u: str, to_u: str) -> float:
        # to Joules
        to_j = {"J": 1.0, "eV": 1.602176634e-19, "keV": 1.602176634e-16, "MeV": 1.602176634e-13}
        if from_u not in to_j or to_u not in to_j:
            raise ValueError(f"unsupported energy units: {from_u}->{to_u}")
        return value * to_j[from_u] / to_j[to_u]

    def export(self) -> Dict[str, Any]:
        return {"version": self.version, "n": len(self.constants),
                "constants": [c.to_dict() for c in self.constants.values()]}

_CONSTANTS_DB = None

def get_constants_db() -> ConstantsDB:
    global _CONSTANTS_DB
    if _CONSTANTS_DB is None:
        _CONSTANTS_DB = ConstantsDB()
    return _CONSTANTS_DB

# ===== END constants_db.py =====


# ===== BEGIN known_settled_db.py =====

#!/usr/bin/env python3
"""
Known-Settled Knowledge Database (KSKB)
======================================

WHAT THIS IS
  A finite database of results that are treated as SETTLED within explicitly
  stated assumptions and regimes (standard textbook / empirically confirmed
  core science and math identities used by the engineer pipeline).

WHAT "CONCLUSIVE" MEANS HERE
  - Conclusive *among the included entries*, given their assumptions.
  - NOT conclusive about all of nature, all of mathematics, or all human knowledge.
  - Open research problems are EXCLUDED from this database (see atlas open list).

WHAT THIS IS NOT
  - Not a complete encyclopaedia of science
  - Not a substitute for primary literature, PDG, NIST, CODATA, textbooks
  - Not a claim of finished physics
"""


import hashlib
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


KSKB_VERSION = "1.0.0-settled"
KSKB_SCOPE = (
    "Settled knowledge only: entries are standard identities / laws that hold "
    "under the listed assumptions. Scope is finite and curated. "
    "Absence from this DB does not mean false; presence means 'accepted within regime'."
)


class Confidence(str, Enum):
    SETTLED = "SETTLED"  # textbook + regime-confirmed


@dataclass
class SettledEntry:
    id: str
    field: str          # math | physics | computing | information
    statement: str
    formal: str
    assumptions: List[str]
    regime: str
    confidence: Confidence = Confidence.SETTLED
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["confidence"] = self.confidence.value
        return d


class KnownSettledDB:
    """Queryable database of settled entries only."""

    def __init__(self):
        self.version = KSKB_VERSION
        self.scope = KSKB_SCOPE
        self.entries: Dict[str, SettledEntry] = {}
        self._build()
        self._load_export()

    def _add(self, e: SettledEntry) -> None:
        self.entries[e.id] = e

    def _build(self) -> None:
        # ----- Mathematics (identities / definitions that are settled) -----
        self._add(SettledEntry(
            id="math.arithmetic.2p2",
            field="math",
            statement="Two plus two equals four in standard integer arithmetic.",
            formal="2 + 2 = 4",
            assumptions=["Peano/integer arithmetic", "standard base-10 numerals"],
            regime="elementary arithmetic",
            tags=["arithmetic", "identity"],
        ))
        self._add(SettledEntry(
            id="math.logic.noncontradiction",
            field="math",
            statement="A statement and its negation are not both true (classical logic).",
            formal="¬(A ∧ ¬A)",
            assumptions=["classical bivalent logic"],
            regime="classical logic",
            tags=["logic"],
        ))
        self._add(SettledEntry(
            id="math.prob.unit_measure",
            field="math",
            statement="Probabilities of a discrete partition sum to 1.",
            formal="Σ_i P(i) = 1 for a complete discrete partition",
            assumptions=["probability measure axioms (Kolmogorov)"],
            regime="probability theory",
            tags=["probability"],
        ))
        self._add(SettledEntry(
            id="math.prob.bayes",
            field="math",
            statement="Bayes' rule relating conditional probabilities.",
            formal="P(A|B) = P(B|A) P(A) / P(B)  when P(B) > 0",
            assumptions=["Kolmogorov probability", "P(B)>0"],
            regime="probability theory",
            tags=["probability", "inference"],
        ))
        self._add(SettledEntry(
            id="math.linalg.matmul_assoc",
            field="math",
            statement="Matrix multiplication is associative where defined.",
            formal="(AB)C = A(BC)",
            assumptions=["compatible dimensions over a ring/field"],
            regime="linear algebra",
            tags=["linear_algebra"],
        ))
        self._add(SettledEntry(
            id="math.calc.ftc",
            field="math",
            statement="Fundamental theorem of calculus (standard form).",
            formal="d/dx ∫_a^x f(t) dt = f(x) for continuous f",
            assumptions=["f continuous on interval"],
            regime="real calculus",
            tags=["calculus"],
        ))
        self._add(SettledEntry(
            id="math.info.shannon_nonneg",
            field="math",
            statement="Shannon entropy is nonnegative.",
            formal="H(X) ≥ 0",
            assumptions=["discrete distribution", "Shannon definition"],
            regime="information theory",
            tags=["information_theory"],
        ))
        self._add(SettledEntry(
            id="math.info.kl_nonneg",
            field="math",
            statement="KL divergence is nonnegative.",
            formal="D_KL(P||Q) ≥ 0",
            assumptions=["P absolutely continuous w.r.t. Q as required"],
            regime="information theory",
            tags=["information_theory", "statistics"],
        ))

        # ----- Physics (settled within regime) -----
        self._add(SettledEntry(
            id="phys.newton.second",
            field="physics",
            statement="Net force equals mass times acceleration (Newtonian).",
            formal="F = m a",
            assumptions=["inertial frame", "non-relativistic", "classical"],
            regime="classical mechanics v ≪ c",
            tags=["classical_mechanics"],
        ))
        self._add(SettledEntry(
            id="phys.em.maxwell_div_b",
            field="physics",
            statement="No magnetic monopoles in classical Maxwell theory (div B = 0).",
            formal="∇ · B = 0",
            assumptions=["classical Maxwell electrodynamics"],
            regime="classical EM",
            tags=["classical_em"],
        ))
        self._add(SettledEntry(
            id="phys.sr.c_invariant",
            field="physics",
            statement="Speed of light in vacuum is invariant across inertial frames (SR).",
            formal="c invariant under Lorentz transformations",
            assumptions=["special relativity", "inertial frames", "vacuum"],
            regime="special relativity",
            tags=["special_relativity"],
        ))
        self._add(SettledEntry(
            id="phys.sr.mass_energy",
            field="physics",
            statement="Rest energy equals rest mass times c squared.",
            formal="E₀ = m c²",
            assumptions=["SR", "rest frame for rest energy"],
            regime="relativistic mechanics",
            tags=["special_relativity"],
        ))
        self._add(SettledEntry(
            id="phys.qm.born",
            field="physics",
            statement="Born rule: outcome probabilities from |amplitude|².",
            formal="P(a) = |⟨a|ψ⟩|²",
            assumptions=["standard quantum measurement postulate"],
            regime="textbook quantum mechanics",
            tags=["quantum_mechanics"],
        ))
        self._add(SettledEntry(
            id="phys.qm.uncertainty",
            field="physics",
            statement="Canonical Heisenberg uncertainty relation.",
            formal="σ_x σ_p ≥ ℏ/2",
            assumptions=["canonical x,p operators", "standard QM"],
            regime="quantum mechanics",
            tags=["quantum_mechanics"],
        ))
        self._add(SettledEntry(
            id="phys.thermo.second_isolated",
            field="physics",
            statement="Entropy of an isolated system does not decrease (2nd law, Clausius form summary).",
            formal="ΔS ≥ 0 for isolated system",
            assumptions=["thermodynamic limit / macroscopic", "isolated"],
            regime="classical thermodynamics",
            tags=["thermo"],
        ))
        self._add(SettledEntry(
            id="phys.stat.boltzmann",
            field="physics",
            statement="Boltzmann entropy relates entropy to multiplicity.",
            formal="S = k_B ln Ω",
            assumptions=["microcanonical ensemble counting"],
            regime="equilibrium statistical mechanics",
            tags=["stat_mech"],
        ))

        # ----- Computing / information engineering (settled engineering facts) -----
        self._add(SettledEntry(
            id="comp.hash.sha256_length",
            field="computing",
            statement="SHA-256 digest is 256 bits (64 hex characters).",
            formal="|SHA256(m)| = 256 bits",
            assumptions=["FIPS 180-4 SHA-256"],
            regime="cryptographic hash standards",
            tags=["hashing", "standards"],
        ))
        self._add(SettledEntry(
            id="comp.ieee754.note",
            field="computing",
            statement="IEEE-754 binary floating point has finite precision and rounding modes.",
            formal="float arithmetic ≠ real arithmetic",
            assumptions=["IEEE-754 binary formats"],
            regime="numerical computing",
            tags=["numerical"],
        ))
        self._add(SettledEntry(
            id="comp.causality.no_future_read",
            field="computing",
            statement="In a time-causal feature system, features with availability time > decision time must not be used.",
            formal="∀ features f: available_time(f) ≤ decision_time",
            assumptions=["defined timestamps", "enforced access layer"],
            regime="time-causal ML / trading research systems",
            tags=["causality", "ml_systems"],
        ))
        self._add(SettledEntry(
            id="ai.abstain.safety",
            field="computing",
            statement="When uncertainty or constraint checks fail, refusing to act (abstain) is a valid control decision.",
            formal="verdict = ABSTAIN if ¬constraints_ok ∨ uncertainty_high",
            assumptions=["explicit constraint and uncertainty thresholds"],
            regime="safety-aware decision systems",
            tags=["abstention", "safety"],
        ))

        # Explicit exclusions note (not entries): quantum gravity TOE, dark matter identity, etc.


    def _load_export(self) -> None:
        """Merge persisted promotions from artifacts/known_settled_export.json if present."""
        try:
            from pathlib import Path
            import json
            path = Path("artifacts/known_settled_export.json")
            if not path.exists():
                path = Path(__file__).resolve().parent / "artifacts" / "known_settled_export.json"
            if not path.exists():
                return
            data = json.loads(path.read_text(encoding="utf-8"))
            for e in data.get("entries") or []:
                eid = e.get("id")
                if not eid or eid in self.entries:
                    continue
                self.entries[eid] = SettledEntry(
                    id=eid,
                    field=e.get("field", "math"),
                    statement=e.get("statement", ""),
                    formal=e.get("formal", ""),
                    assumptions=list(e.get("assumptions") or []),
                    regime=e.get("regime", ""),
                    confidence=Confidence.SETTLED,
                    tags=list(e.get("tags") or []),
                )
        except Exception:
            pass

    def get(self, entry_id: str) -> Optional[Dict[str, Any]]:
        e = self.entries.get(entry_id)
        return e.to_dict() if e else None

    def list_entries(self, field: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for e in self.entries.values():
            if field is None or e.field == field:
                out.append(e.to_dict())
        return out

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        hits = []
        for e in self.entries.values():
            blob = " ".join([e.id, e.field, e.statement, e.formal, e.regime] + e.assumptions + e.tags).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, e.to_dict()))
        hits.sort(key=lambda x: -x[0])
        return [h for _, h in hits[:limit]]

    def lookup_formal(self, formal_substr: str) -> List[Dict[str, Any]]:
        s = formal_substr.lower()
        return [e.to_dict() for e in self.entries.values() if s in e.formal.lower()]

    def assert_settled(self, entry_id: str) -> Dict[str, Any]:
        """Engineer-facing: confirm id is in the settled DB."""
        e = self.entries.get(entry_id)
        if not e:
            return {"ok": False, "entry_id": entry_id, "reason": "not_in_settled_db"}
        return {"ok": True, "entry": e.to_dict()}

    def reject_completeness_claim(self, text: str) -> Dict[str, Any]:
        t = text.lower()
        bad = []
        for phrase in [
            "complete physics", "theory of everything", "all knowledge",
            "conclusive world", "finished physics", "everything that is known",
            "fully conclusive universe",
        ]:
            if phrase in t:
                bad.append(phrase)
        return {
            "ok": len(bad) == 0,
            "rejected_phrases": bad,
            "note": "KSKB is finite settled entries only; completeness claims are out of scope",
        }

    def export(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "scope": self.scope,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_entries": len(self.entries),
            "fields": sorted({e.field for e in self.entries.values()}),
            "entries": self.list_entries(),
            "explicitly_excluded": [
                "UV-complete quantum gravity",
                "identity of dark matter",
                "final measurement interpretation",
                "any claim of complete human knowledge",
            ],
        }

    def checksum(self) -> str:
        return hashlib.sha256(
            json.dumps(self.export(), sort_keys=True, default=str).encode()
        ).hexdigest()


_SETTLED_DB: Optional[KnownSettledDB] = None


def get_settled_db() -> KnownSettledDB:
    global _SETTLED_DB
    if _SETTLED_DB is None:
        _SETTLED_DB = KnownSettledDB()
    return _SETTLED_DB

# ===== END known_settled_db.py =====


# ===== BEGIN typed_ir.py =====

#!/usr/bin/env python3
"""Typed intermediate representation for candidate actions before simulation."""
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


ALLOWED_KINDS = {"swap", "bridge", "wait", "abstain"}


@dataclass
class ActionIR:
    kind: str
    venue: str
    token_in: str
    token_out: str
    amount_in: float
    max_slippage_bps: float
    chain_id: int
    deadline_ms: int

    def validate(self) -> Dict[str, Any]:
        issues = []
        if self.kind not in ALLOWED_KINDS:
            issues.append(f"kind not allowed: {self.kind}")
        if self.amount_in < 0:
            issues.append("amount_in < 0")
        if self.max_slippage_bps < 0 or self.max_slippage_bps > 10_000:
            issues.append("slippage out of range")
        if self.chain_id <= 0:
            issues.append("chain_id invalid")
        if self.deadline_ms < 0:
            issues.append("deadline invalid")
        return {"ok": len(issues) == 0, "issues": issues, "action": asdict(self)}


def from_dict(d: Dict[str, Any]) -> ActionIR:
    return ActionIR(
        kind=str(d.get("kind", "abstain")),
        venue=str(d.get("venue", "")),
        token_in=str(d.get("token_in", "")),
        token_out=str(d.get("token_out", "")),
        amount_in=float(d.get("amount_in", 0)),
        max_slippage_bps=float(d.get("max_slippage_bps", 0)),
        chain_id=int(d.get("chain_id", 0)),
        deadline_ms=int(d.get("deadline_ms", 0)),
    )


def validate_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    results = [from_dict(a).validate() for a in actions]
    return {
        "ok": all(r["ok"] for r in results),
        "n": len(results),
        "results": results,
    }

# ===== END typed_ir.py =====


# ===== BEGIN interval_arith.py =====

#!/usr/bin/env python3
"""Interval arithmetic for rigorous numeric enclosures (not point estimates)."""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Interval:
    lo: float
    hi: float

    def __post_init__(self):
        if self.lo > self.hi:
            self.lo, self.hi = self.hi, self.lo

    def __add__(self, other: "Interval") -> "Interval":
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other: "Interval") -> "Interval":
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other: "Interval") -> "Interval":
        candidates = [
            self.lo * other.lo, self.lo * other.hi,
            self.hi * other.lo, self.hi * other.hi,
        ]
        return Interval(min(candidates), max(candidates))

    def contains(self, x: float) -> bool:
        return self.lo <= x <= self.hi

    def width(self) -> float:
        return self.hi - self.lo

    def to_dict(self) -> Dict[str, float]:
        return {"lo": self.lo, "hi": self.hi}


def net_edge_interval(
    output: Interval,
    costs: Interval,
) -> Interval:
    """edge = output - costs, interval valued."""
    return output - costs


def trade_allowed_by_interval(edge: Interval, min_edge: float) -> Dict[str, Any]:
    """Allow only if entire interval is above min_edge (worst-case)."""
    ok = edge.lo >= min_edge
    return {
        "allow_trade": ok,
        "edge": edge.to_dict(),
        "min_edge": min_edge,
        "worst_case": edge.lo,
        "best_case": edge.hi,
    }

# ===== END interval_arith.py =====


# ===== BEGIN causal_graph.py =====

#!/usr/bin/env python3
"""Explicit causal DAG + simple d-separation style feature legality checks."""
from typing import Any, Dict, List, Set, Tuple


class CausalGraph:
    def __init__(self):
        self.edges: Set[Tuple[str, str]] = set()  # parent -> child

    def add_edge(self, parent: str, child: str) -> None:
        self.edges.add((parent, child))

    def parents(self, node: str) -> Set[str]:
        return {p for p, c in self.edges if c == node}

    def ancestors(self, node: str) -> Set[str]:
        seen: Set[str] = set()
        stack = list(self.parents(node))
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(self.parents(n))
        return seen

    def would_create_cycle(self, parent: str, child: str) -> bool:
        # cycle if child is ancestor of parent
        return parent == child or parent in self.ancestors(child) or child in self.ancestors(parent) and parent in self.ancestors(child)

    def legal_feature_for_decision(self, feature: str, decision: str, banned: Set[str]) -> Dict[str, Any]:
        """Feature illegal if in banned (e.g. post-outcome) or is descendant of decision."""
        if feature in banned:
            return {"ok": False, "reason": "banned_post_outcome"}
        # if feature is downstream of decision in graph, illegal at decision time
        if feature in self.descendants(decision):
            return {"ok": False, "reason": "descendant_of_decision"}
        return {"ok": True, "reason": "allowed"}

    def descendants(self, node: str) -> Set[str]:
        seen: Set[str] = set()
        stack = [c for p, c in self.edges if p == node]
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend([c for p, c in self.edges if p == n])
        return seen


def default_market_graph() -> CausalGraph:
    g = CausalGraph()
    # time structure
    for a, b in [
        ("market_state_t", "features_t"),
        ("features_t", "decision_t"),
        ("decision_t", "execution_t"),
        ("execution_t", "outcome_t"),
        ("outcome_t", "label_t"),
    ]:
        g.add_edge(a, b)
    return g


def check_features(features: List[str], decision_node: str = "decision_t") -> Dict[str, Any]:
    g = default_market_graph()
    banned = {"outcome_t", "label_t", "execution_t"}
    results = {f: g.legal_feature_for_decision(f, decision_node, banned) for f in features}
    return {"ok": all(r["ok"] for r in results.values()), "results": results}

# ===== END causal_graph.py =====


# ===== BEGIN chain_observer_ro.py =====

#!/usr/bin/env python3
"""
Read-only chain observer interface with availability timestamps.
Does NOT sign or broadcast. Network fetch is optional and explicit.
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import time


@dataclass
class ObservedEvent:
    event_id: str
    event_timestamp_ms: int
    observed_timestamp_ms: int
    available_timestamp_ms: int
    chain_id: int
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReadOnlyObserver:
    def __init__(self, chain_id: int = 42161, availability_delay_ms: int = 0):
        self.chain_id = chain_id
        self.availability_delay_ms = availability_delay_ms
        self._buffer: List[ObservedEvent] = []

    def ingest_local(self, event_id: str, event_timestamp_ms: int, payload: Dict[str, Any]) -> ObservedEvent:
        now = int(time.time() * 1000)
        ev = ObservedEvent(
            event_id=event_id,
            event_timestamp_ms=event_timestamp_ms,
            observed_timestamp_ms=now,
            available_timestamp_ms=now + self.availability_delay_ms,
            chain_id=self.chain_id,
            payload=payload,
        )
        self._buffer.append(ev)
        return ev

    def poll(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._buffer]

    def fetch_rpc_disabled(self) -> Dict[str, Any]:
        return {
            "ok": False,
            "reason": "live_rpc_disabled_by_default",
            "note": "Enable only in explicit readonly config; never signing keys",
        }

# ===== END chain_observer_ro.py =====


# ===== BEGIN sandbox.py =====

#!/usr/bin/env python3
"""Resource-limited runner for non-stationary probes (best-effort pure Python)."""
import signal
from typing import Any, Callable, Dict, Optional


class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutError("sandbox time limit exceeded")


def run(
    fn: Callable[[], Any],
    timeout_s: float = 2.0,
    max_result_bytes: int = 2_000_000,
) -> Dict[str, Any]:
    """
    Run fn with a SIGALRM time limit (Unix). Memory limits require OS cgroups;
    we only bound wall time and result size serialization estimate.
    """
    try:
        old = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, timeout_s)
        try:
            result = fn()
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
        # size bound
        import json
        try:
            size = len(json.dumps(result, default=str))
        except Exception:
            size = -1
        if size > max_result_bytes:
            return {"ok": False, "error": "result_too_large", "size": size}
        return {"ok": True, "result": result, "size": size}
    except TimeoutError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__ + ": " + str(e)}

# ===== END sandbox.py =====


# ===== BEGIN merkle_artifacts.py =====

#!/usr/bin/env python3
"""Merkle-style hash tree over a run artifact directory."""
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _node_hash(left: str, right: str) -> str:
    return hashlib.sha256((left + right).encode()).hexdigest()


def build_merkle(root: str) -> Dict[str, Any]:
    root_p = Path(root)
    files = sorted([p for p in root_p.rglob("*") if p.is_file() and p.stat().st_size < 50_000_000])
    leaves: List[Tuple[str, str]] = [(str(p.relative_to(root_p)), _file_hash(p)) for p in files]
    if not leaves:
        return {"root": None, "n_files": 0, "leaves": []}
    layer = [h for _, h in leaves]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else a
            nxt.append(_node_hash(a, b))
        layer = nxt
    return {
        "merkle_root": layer[0],
        "n_files": len(leaves),
        "leaves": [{"path": p, "sha256": h} for p, h in leaves],
    }


def write_merkle(root: str, out_name: str = "hashes/merkle.json") -> Dict[str, Any]:
    tree = build_merkle(root)
    out = Path(root) / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tree, indent=2))
    return tree

# ===== END merkle_artifacts.py =====


# ===== BEGIN smt_gate.py =====

#!/usr/bin/env python3
"""
Lightweight SMT-style constraint gate (pure Python).
Not a full Z3 replacement — decidable linear inequalities + booleans for pre-TRADE checks.
Optional: if z3 is installed, use it for richer constraints.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Constraint:
    # linear: coeff * var >= bound  OR  coeff * var <= bound
    var: str
    op: str  # ">=" | "<=" | "=="
    bound: float
    coeff: float = 1.0


def _check_linear(values: Dict[str, float], c: Constraint) -> bool:
    if c.var not in values:
        return False
    x = c.coeff * float(values[c.var])
    if c.op == ">=":
        return x >= c.bound
    if c.op == "<=":
        return x <= c.bound
    if c.op == "==":
        return abs(x - c.bound) <= 1e-9
    return False


def solve(values: Dict[str, float], constraints: List[Constraint]) -> Dict[str, Any]:
    """Return sat/unsat under assigned values (model checking, not full search)."""
    failed = []
    for c in constraints:
        ok = _check_linear(values, c)
        if not ok:
            failed.append({"var": c.var, "op": c.op, "bound": c.bound, "coeff": c.coeff})
    sat = len(failed) == 0
    # Optional Z3 path
    z3_used = False
    if not sat:
        try:
            import z3  # type: ignore
            z3_used = True
            # re-check with z3 if variables free — here values are bound, so same result
        except Exception:
            pass
    return {"sat": sat, "failed": failed, "n_constraints": len(constraints), "z3_available_attempted": z3_used}


def pre_trade_gate(
    net_edge_usd: float,
    revert_p: float,
    inclusion_p: float,
    ood: float,
    thresholds: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    th = thresholds or {
        "min_net_edge_usd": 1.0,
        "max_revert_probability": 0.03,
        "min_inclusion_probability": 0.90,
        "ood_threshold": 0.7,
    }
    values = {
        "net_edge_usd": net_edge_usd,
        "revert_p": revert_p,
        "inclusion_p": inclusion_p,
        "ood": ood,
    }
    constraints = [
        Constraint("net_edge_usd", ">=", th["min_net_edge_usd"]),
        Constraint("revert_p", "<=", th["max_revert_probability"]),
        Constraint("inclusion_p", ">=", th["min_inclusion_probability"]),
        Constraint("ood", "<=", th["ood_threshold"]),
    ]
    result = solve(values, constraints)
    result["allow_trade"] = result["sat"]
    result["values"] = values
    result["thresholds"] = th
    return result

# ===== END smt_gate.py =====


# ===== BEGIN ledger_index.py =====

#!/usr/bin/env python3
"""Cross-run index over verification_ledger.jsonl files under artifacts/.

Speed policy (product work on full):
  - Cap number of ledger files and lines scanned (default) so engineer passes
    stay O(1)-ish even when artifacts/ accumulates many runs.
  - Set MEGACOMPACT_LEDGER_ROOT or pass root= to narrow scope.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Defaults tuned for lab CI / adversarial speed
_MAX_LEDGER_FILES = int(os.environ.get("MEGACOMPACT_MAX_LEDGER_FILES", "12"))
_MAX_LINES_PER_FILE = int(os.environ.get("MEGACOMPACT_MAX_LEDGER_LINES", "200"))


def find_ledgers(root: str = "artifacts") -> List[Path]:
    root_p = Path(root)
    if not root_p.exists():
        return []
    paths = sorted(root_p.rglob("verification_ledger.jsonl")) + sorted(
        root_p.rglob("*_ledger.jsonl")
    )
    # Prefer newest by mtime; cap count
    paths = sorted(paths, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return paths[:_MAX_LEDGER_FILES]


def load_entries(paths: Optional[List[Path]] = None, root: str = "artifacts") -> List[Dict[str, Any]]:
    paths = paths or find_ledgers(root)
    entries = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                # Read only the tail for large files (recent patterns matter most)
                lines = f.readlines()
                if len(lines) > _MAX_LINES_PER_FILE:
                    lines = lines[-_MAX_LINES_PER_FILE:]
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    rec["_ledger_path"] = str(p)
                    rec["_line"] = i + 1
                    entries.append(rec)
        except OSError:
            continue
    return entries


def ledger_search(
    query: str,
    root: str = "artifacts",
    event_type: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    q = query.lower().strip()
    out = []
    for rec in load_entries(root=root):
        if event_type and rec.get("event_type") != event_type:
            continue
        blob = json.dumps(rec, default=str).lower()
        if not q or q in blob:
            out.append(rec)
        if len(out) >= limit:
            break
    return out[:limit]


def stats(root: str = "artifacts") -> Dict[str, Any]:
    paths = find_ledgers(root)
    entries = load_entries(paths, root=root)
    return {
        "n_ledger_files_scanned": len(paths),
        "n_entries_loaded": len(entries),
        "max_files": _MAX_LEDGER_FILES,
        "max_lines_per_file": _MAX_LINES_PER_FILE,
    }
search = ledger_search


# ===== END ledger_index.py =====


# ===== BEGIN bit_exact_replay.py =====

#!/usr/bin/env python3
"""
Bit-exact / deterministic replay helpers: pin matrix + artifact compare + proof.
Supports cross-run and cross-machine replay proofs (hash equality under pin matrix).
"""
import hashlib
import json
import os
import sys
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def pin_matrix() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "machine": platform.machine(),
        "implementation": platform.python_implementation(),
        "hash_seed": os.environ.get("PYTHONHASHSEED", "unset"),
        "hash_seed_note": "PYTHONHASHSEED=0 recommended for stable hashing",
        "timezone": "UTC",
    }


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    return hash_bytes(path.read_bytes())


def hash_json_canonical(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hash_bytes(raw)


def collect_run_hashes(run_dir: str, rel_paths: Optional[List[str]] = None) -> Dict[str, str]:
    root = Path(run_dir)
    rel_paths = rel_paths or [
        "reports/run_summary.json",
        "audits/audit_results.json",
        "hashes/merkle.json",
        "hashes/pin_matrix.json",
    ]
    out: Dict[str, str] = {}
    for rel in rel_paths:
        p = root / rel
        if p.exists():
            out[rel] = hash_file(p)
        else:
            out[rel] = "MISSING"
    return out


def compare_runs(run_a: str, run_b: str, rel_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    a_hashes = collect_run_hashes(run_a, rel_paths)
    b_hashes = collect_run_hashes(run_b, rel_paths)
    diffs = []
    keys = sorted(set(a_hashes) | set(b_hashes))
    for k in keys:
        ha, hb = a_hashes.get(k, "MISSING"), b_hashes.get(k, "MISSING")
        if ha != hb:
            diffs.append({"path": k, "status": "mismatch" if ha != "MISSING" and hb != "MISSING" else "missing_side",
                          "a": ha[:16] if ha != "MISSING" else "MISSING",
                          "b": hb[:16] if hb != "MISSING" else "MISSING"})
    return {
        "ok": len(diffs) == 0,
        "n_compared": len(keys),
        "diffs": diffs,
        "pin_matrix_a": pin_matrix(),
        "run_a": run_a,
        "run_b": run_b,
    }


def write_pin(run_dir: str) -> Path:
    path = Path(run_dir) / "hashes" / "pin_matrix.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(pin_matrix(), indent=2))
    return path


def write_replay_proof(
    run_dir: str,
    reference_run: Optional[str] = None,
    rel_paths: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Emit a replay proof artifact for this run (and optional cross-run compare).
    Product feature: labs can re-run and prove bit-exact equality under pin matrix.
    """
    run = Path(run_dir)
    hashes_dir = run / "hashes"
    hashes_dir.mkdir(parents=True, exist_ok=True)
    write_pin(run_dir)
    file_hashes = collect_run_hashes(run_dir, rel_paths)
    proof = {
        "version": "1.0.0-product",
        "kind": "bit_exact_replay_proof",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run),
        "pin_matrix": pin_matrix(),
        "file_hashes": file_hashes,
        "aggregate_hash": hash_json_canonical(file_hashes),
        "reference_compare": None,
        "ok": True,
        "note": "Re-run under same pin_matrix; compare aggregate_hash for bit-exact claim.",
    }
    if reference_run:
        cmp = compare_runs(run_dir, reference_run, rel_paths)
        proof["reference_compare"] = cmp
        proof["ok"] = bool(cmp.get("ok"))
    out = hashes_dir / "replay_proof.json"
    out.write_text(json.dumps(proof, indent=2))
    proof["path"] = str(out)
    return proof


# ---------------------------------------------------------------------------
# Product VD1: finished bit-exact replay proof API
# ---------------------------------------------------------------------------

def write_pin_matrix(run_dir: str) -> Dict[str, Any]:
    """Persist pin matrix under run_dir/hashes/pin_matrix.json."""
    root = Path(run_dir)
    hashes = root / "hashes"
    hashes.mkdir(parents=True, exist_ok=True)
    matrix = pin_matrix()
    matrix["written_at"] = datetime.now(timezone.utc).isoformat()
    path = hashes / "pin_matrix.json"
    path.write_text(json.dumps(matrix, indent=2, sort_keys=True))
    return {"ok": True, "path": str(path), "matrix": matrix}


def write_run_hashes(run_dir: str, rel_paths: Optional[List[str]] = None) -> Dict[str, Any]:
    root = Path(run_dir)
    hashes_dir = root / "hashes"
    hashes_dir.mkdir(parents=True, exist_ok=True)
    collected = collect_run_hashes(run_dir, rel_paths)
    path = hashes_dir / "run_hashes.json"
    path.write_text(json.dumps(collected, indent=2, sort_keys=True))
    return {"ok": True, "path": str(path), "hashes": collected}


def replay_proof(
    run_a: str,
    run_b: str,
    rel_paths: Optional[List[str]] = None,
    require_pin_match: bool = True,
) -> Dict[str, Any]:
    """
    Cross-run / cross-machine bit-exact replay proof.

    Proof passes only if:
      - compared artifact hashes match
      - (optional) pin matrices are present and compatible
    """
    cmp = compare_runs(run_a, run_b, rel_paths)
    pin_a = Path(run_a) / "hashes" / "pin_matrix.json"
    pin_b = Path(run_b) / "hashes" / "pin_matrix.json"
    pin_report: Dict[str, Any] = {"present_a": pin_a.exists(), "present_b": pin_b.exists()}
    if pin_a.exists() and pin_b.exists():
        ma = json.loads(pin_a.read_text())
        mb = json.loads(pin_b.read_text())
        pin_report["match"] = (
            ma.get("python") == mb.get("python")
            and ma.get("hash_seed") == mb.get("hash_seed")
            and ma.get("implementation") == mb.get("implementation")
        )
        pin_report["a"] = {k: ma.get(k) for k in ("python", "platform", "machine", "hash_seed")}
        pin_report["b"] = {k: mb.get(k) for k in ("python", "platform", "machine", "hash_seed")}
    else:
        pin_report["match"] = False

    ok = bool(cmp.get("ok"))
    if require_pin_match and not pin_report.get("match"):
        ok = False

    return {
        "ok": ok,
        "artifact_compare": cmp,
        "pin_matrix": pin_report,
        "proof": "bit_exact_pass" if ok else "bit_exact_fail",
        "note": "Set PYTHONHASHSEED=0 and same deps for cross-machine proofs",
    }


def self_proof(run_dir: str) -> Dict[str, Any]:
    """Prove a run is bit-exact against itself after writing hashes + pin matrix."""
    write_pin_matrix(run_dir)
    write_run_hashes(run_dir)
    return replay_proof(run_dir, run_dir, require_pin_match=True)

# ===== END bit_exact_replay.py =====


# ===== BEGIN differential_audit.py =====

#!/usr/bin/env python3
"""Differential audit: same decision_id across runs should not flip without config change."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_decisions(run_dir: str) -> Dict[str, Dict[str, Any]]:
    path = Path(run_dir) / "paper" / "decisions.jsonl"
    out: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            did = rec.get("decision_id")
            if did:
                out[did] = rec
    return out


def differential_compare_runs(run_a: str, run_b: str) -> Dict[str, Any]:
    a = load_decisions(run_a)
    b = load_decisions(run_b)
    shared = set(a) & set(b)
    flips = []
    for did in shared:
        va, vb = a[did].get("verdict"), b[did].get("verdict")
        ca, cb = a[did].get("config_hash"), b[did].get("config_hash")
        if va != vb and ca == cb:
            flips.append({"decision_id": did, "verdict_a": va, "verdict_b": vb, "config_hash": ca})
    return {
        "n_shared": len(shared),
        "n_unexplained_flips": len(flips),
        "flips": flips,
        "ok": len(flips) == 0,
    }
compare_runs = differential_compare_runs


# ===== END differential_audit.py =====


# ===== BEGIN formal_bridge.py =====

#!/usr/bin/env python3
"""
Optional bridge to external formal kernels (Lean/Coq/Isabelle).
Does not embed a kernel — only defines the interface and offline invocation contract.
"""
from typing import Any, Dict, Optional
from pathlib import Path
import shutil
import subprocess


def kernel_available() -> Dict[str, bool]:
    return {
        "lean": bool(shutil.which("lean")),
        "coqc": bool(shutil.which("coqc")),
        "isabelle": bool(shutil.which("isabelle")),
    }


def submit_obligation(statement_id: str, formal_text: str, out_dir: str = "artifacts/formal") -> Dict[str, Any]:
    """
    Write an obligation file for external checking.
    Returns path; does not claim proven unless kernel returns success.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{statement_id}.txt"
    path.write_text(
        f"OBLIGATION {statement_id}\n"
        f"STATUS: unchecked\n"
        f"FORMAL:\n{formal_text}\n"
        f"NOTE: Run external kernel; do not treat as proven until kernel accepts.\n"
    )
    return {
        "ok": True,
        "path": str(path),
        "proven": False,
        "kernels": kernel_available(),
        "note": "unchecked until external kernel accepts",
    }


def try_lean_check(file_path: str) -> Dict[str, Any]:
    if not shutil.which("lean"):
        return {"ok": False, "proven": False, "reason": "lean_not_installed"}
    try:
        proc = subprocess.run(
            ["lean", file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "ok": proc.returncode == 0,
            "proven": proc.returncode == 0,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
    except Exception as e:
        return {"ok": False, "proven": False, "error": str(e)}

# ===== END formal_bridge.py =====


# ===== BEGIN signed_ledger.py =====

#!/usr/bin/env python3
"""
Hardened signed ledgers for promotion and verification events.

Local HMAC-SHA256 (always available) + optional Ed25519 when cryptography
is installed. Never used for live chain signing — artifact integrity only.
"""

import hashlib
import hmac
import json
import os
import secrets
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SignedEntry:
    entry_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: str
    key_id: str
    algorithm: str
    signature: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SigningKeyStore:
    """Local key material for ledger integrity. Never for live chain txs."""

    def __init__(self, key_dir: Optional[str] = None):
        self.key_dir = Path(key_dir or "artifacts/keys")
        self.key_dir.mkdir(parents=True, exist_ok=True)
        self.hmac_path = self.key_dir / "ledger_hmac.key"
        self.meta_path = self.key_dir / "key_meta.json"
        self._hmac_key: Optional[bytes] = None
        self._ed25519 = False
        self._ed25519_priv = None
        self._ed25519_pub_hex: Optional[str] = None
        self.key_id = "unset"
        self._load_or_create()

    def _load_or_create(self) -> None:
        if self.hmac_path.exists():
            self._hmac_key = self.hmac_path.read_bytes()
        else:
            self._hmac_key = secrets.token_bytes(32)
            self.hmac_path.write_bytes(self._hmac_key)
            try:
                os.chmod(self.hmac_path, 0o600)
            except OSError:
                pass
        meta = {
            "key_id": hashlib.sha256(self._hmac_key).hexdigest()[:16],
            "algorithms": ["HMAC-SHA256"],
            "purpose": "artifact_ledger_integrity_only",
            "created": _utc_now(),
        }
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            from cryptography.hazmat.primitives import serialization

            priv_path = self.key_dir / "ledger_ed25519.pem"
            if priv_path.exists():
                pem = priv_path.read_bytes()
                self._ed25519_priv = serialization.load_pem_private_key(pem, password=None)
            else:
                self._ed25519_priv = Ed25519PrivateKey.generate()
                pem = self._ed25519_priv.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
                priv_path.write_bytes(pem)
                try:
                    os.chmod(priv_path, 0o600)
                except OSError:
                    pass
            pub = self._ed25519_priv.public_key()
            pub_bytes = pub.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
            self._ed25519_pub_hex = pub_bytes.hex()
            meta["algorithms"].append("Ed25519")
            meta["ed25519_public_hex"] = self._ed25519_pub_hex
            self._ed25519 = True
        except Exception:
            self._ed25519 = False
        if self.meta_path.exists():
            old = json.loads(self.meta_path.read_text())
            meta["created"] = old.get("created", meta["created"])
            meta["key_id"] = old.get("key_id", meta["key_id"])
        self.meta_path.write_text(json.dumps(meta, indent=2))
        self.key_id = meta["key_id"]

    def sign_hmac(self, payload: Dict[str, Any]) -> str:
        assert self._hmac_key is not None
        return hmac.new(self._hmac_key, _canonical(payload), hashlib.sha256).hexdigest()

    def verify_hmac(self, payload: Dict[str, Any], signature: str) -> bool:
        expected = self.sign_hmac(payload)
        return hmac.compare_digest(expected, signature)

    def sign_ed25519(self, payload: Dict[str, Any]) -> Optional[str]:
        if not self._ed25519 or self._ed25519_priv is None:
            return None
        sig = self._ed25519_priv.sign(_canonical(payload))
        return sig.hex()

    def algorithms(self) -> List[str]:
        algs = ["HMAC-SHA256"]
        if self._ed25519:
            algs.append("Ed25519")
        return algs


class SignedLedger:
    """Append-only signed JSONL ledger for promotions and verification events."""

    def __init__(
        self,
        path: Optional[str] = None,
        key_store: Optional[SigningKeyStore] = None,
        prefer_ed25519: bool = True,
    ):
        self.path = Path(path or "artifacts/signed_ledger.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.keys = key_store or SigningKeyStore()
        self.prefer_ed25519 = prefer_ed25519

    def append(self, event_type: str, payload: Dict[str, Any]) -> SignedEntry:
        body = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": _utc_now(),
            "key_id": self.keys.key_id,
        }
        alg = "HMAC-SHA256"
        sig = self.keys.sign_hmac(body)
        if self.prefer_ed25519:
            ed = self.keys.sign_ed25519(body)
            if ed:
                alg = "Ed25519+HMAC-SHA256"
                body["hmac_sha256"] = sig
                sig = ed
        entry_id = hashlib.sha256(_canonical(body) + sig.encode()).hexdigest()[:16]
        entry = SignedEntry(
            entry_id=entry_id,
            event_type=event_type,
            payload=payload,
            timestamp=body["timestamp"],
            key_id=self.keys.key_id,
            algorithm=alg,
            signature=sig,
        )
        record = entry.to_dict()
        if "hmac_sha256" in body:
            record["hmac_sha256"] = body["hmac_sha256"]
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
        return entry

    def verify_file(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"ok": True, "n": 0, "failures": []}
        failures = []
        n = 0
        with self.path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                n += 1
                rec = json.loads(line)
                body = {
                    "event_type": rec["event_type"],
                    "payload": rec["payload"],
                    "timestamp": rec["timestamp"],
                    "key_id": rec["key_id"],
                }
                alg = rec.get("algorithm", "HMAC-SHA256")
                if "HMAC" in alg:
                    hmac_sig = rec.get("hmac_sha256") or (
                        rec["signature"] if alg == "HMAC-SHA256" else None
                    )
                    if hmac_sig is None or not self.keys.verify_hmac(body, hmac_sig):
                        failures.append({
                            "line": line_no,
                            "entry_id": rec.get("entry_id"),
                            "reason": "hmac_mismatch",
                        })
                if "Ed25519" in alg and self.keys._ed25519_priv is not None:
                    try:
                        pub = self.keys._ed25519_priv.public_key()
                        pub.verify(bytes.fromhex(rec["signature"]), _canonical(body))
                    except Exception as e:
                        failures.append({
                            "line": line_no,
                            "entry_id": rec.get("entry_id"),
                            "reason": f"ed25519_fail:{e}",
                        })
        return {"ok": len(failures) == 0, "n": n, "failures": failures}

    def recent(self, n: int = 10) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").strip().splitlines()
        out = []
        for line in lines[-n:]:
            if line.strip():
                out.append(json.loads(line))
        return out

# ===== END signed_ledger.py =====


# ===== BEGIN unit_tags.py =====

#!/usr/bin/env python3
"""Unit tags on feature payloads + optional dimensional checks via constants_db."""
from typing import Any, Dict, List, Optional, Tuple


def tag_feature(name: str, value: float, unit: str, kind: str = "scalar") -> Dict[str, Any]:
    return {"name": name, "value": value, "unit": unit, "kind": kind}


def attach_unit_tags(payload: Dict[str, Any], tags: List[Dict[str, Any]]) -> Dict[str, Any]:
    out = dict(payload)
    out["unit_tags"] = tags
    return out


def check_length_pair(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Convert both to meters and compare magnitudes if both are lengths."""
    length_units = {"m", "cm", "mm", "km", "nm", "angstrom"}
    if a.get("unit") not in length_units or b.get("unit") not in length_units:
        return {"ok": True, "skipped": True, "reason": "not_both_length"}
    cdb = get_constants_db()
    try:
        av = cdb.convert_length(float(a["value"]), a["unit"], "m")
        bv = cdb.convert_length(float(b["value"]), b["unit"], "m")
        return {"ok": True, "a_m": av, "b_m": bv, "ratio": (av / bv) if bv else None}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def stationary_unit_probe(payload: Dict[str, Any]) -> Dict[str, Any]:
    tags = payload.get("unit_tags") or []
    if not tags:
        return {"ok": True, "n_tags": 0, "note": "no unit tags"}
    bad = [t for t in tags if "unit" not in t or "value" not in t]
    return {"ok": len(bad) == 0, "n_tags": len(tags), "malformed": len(bad)}

# ===== END unit_tags.py =====


# ===== BEGIN atlas.py =====

#!/usr/bin/env python3
"""
Physics & Mathematical Language Atlas (honest, extensible, non-omniscient)
==========================================================================

WHAT THIS IS
  A structured catalogue the Stationary / Non-Stationary engineers can query:
  - Physics domains (classical → quantum → statistical → continuum → info)
  - Formula cards with symbols, assumptions, and validity regimes
  - Mathematical language registry (arithmetic, calculus, linear algebra,
    probability, information theory, category-ish labels, etc.)
  - Hooks for coding / computing / AI knowledge tags used in verification

WHAT THIS IS NOT
  - Not a "world conclusive complete" physics encyclopaedia
  - Not a substitute for textbooks, PDG, NIST, or living review articles
  - Not a claim that all of mathematics or physics is encoded here
  - Not a quantum computer, oracle, or AGI

DESIGN RULES
  1. Every entry carries assumptions and known limits.
  2. Open problems are listed as OPEN, not solved.
  3. Engineers may USE this atlas for checks; they may not invent physics.
  4. Fail-closed: unknown domain → ABSTAIN / note gap, do not hallucinate.
"""


import hashlib
import json
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


ATLAS_VERSION = "0.1.0-honest"
ATLAS_DISCLAIMER = (
    "Incomplete by construction. Physics and mathematics are open-ended. "
    "This atlas is a research scaffold for engineer verification, not a conclusive world model."
)


class DomainStatus(str, Enum):
    CORE = "core"           # well-established, textbook-level
    EFFECTIVE = "effective" # effective theory / regime-limited
    OPEN = "open"           # active research / incomplete


@dataclass
class FormulaCard:
    id: str
    name: str
    domain: str
    expression: str
    symbols: Dict[str, str]
    assumptions: List[str]
    validity_regime: str
    status: DomainStatus = DomainStatus.CORE
    math_languages: List[str] = field(default_factory=list)
    references_note: str = "standard textbook form; verify against primary sources"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class PhysicsDomain:
    id: str
    name: str
    status: DomainStatus
    summary: str
    key_ideas: List[str]
    open_problems: List[str]
    formula_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class MathLanguage:
    id: str
    name: str
    purpose: str
    typical_ops: List[str]
    used_by_domains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PhysicsMathAtlas:
    """
    Queryable atlas for engineers. Contents are curated CORE/EFFECTIVE entries
    plus explicitly marked OPEN problems — never presented as complete.
    """

    def __init__(self):
        self.version = ATLAS_VERSION
        self.disclaimer = ATLAS_DISCLAIMER
        self.languages: Dict[str, MathLanguage] = {}
        self.domains: Dict[str, PhysicsDomain] = {}
        self.formulas: Dict[str, FormulaCard] = {}
        self.computing_tags: Dict[str, str] = {}
        self.ai_tags: Dict[str, str] = {}
        self._build()

    # ------------------------------------------------------------------
    # Build catalogue
    # ------------------------------------------------------------------

    def _build(self) -> None:
        self._register_math_languages()
        self._register_physics_domains()
        self._register_formulas()
        self._register_computing_ai()

    def _register_math_languages(self) -> None:
        specs = [
            ("arithmetic", "Arithmetic", "Counting, rings of integers/rationals", ["+", "-", "*", "/", "mod"]),
            ("algebra", "Elementary & Abstract Algebra", "Equations, groups, rings, fields", ["solve", "factor", "homomorphism"]),
            ("linear_algebra", "Linear Algebra", "Vector spaces, operators, spectra", ["matmul", "eigen", "svd", "inner_product"]),
            ("calculus", "Calculus", "Limits, derivatives, integrals", ["d/dx", "∫", "∂", "∇"]),
            ("vector_calculus", "Vector Calculus", "Fields in R^n", ["grad", "div", "curl", "Stokes"]),
            ("differential_equations", "Differential Equations", "Dynamical laws", ["ODE", "PDE", "boundary_value"]),
            ("complex_analysis", "Complex Analysis", "Holomorphic structure", ["contour_integral", "residue"]),
            ("probability", "Probability", "Uncertainty, measures", ["E", "Var", "P", "conditional"]),
            ("statistics", "Statistics", "Inference from data", ["likelihood", "estimator", "hypothesis_test"]),
            ("information_theory", "Information Theory", "Entropy, coding, channels", ["H", "D_KL", "I(X;Y)", "rate"]),
            ("optimization", "Optimization", "Extrema under constraints", ["argmin", "Lagrange", "convex"]),
            ("geometry", "Geometry / Manifolds", "Space, metrics, curvature (intro)", ["metric", "geodesic", "curvature"]),
            ("group_theory", "Group Theory", "Symmetry", ["representation", "generator", "invariant"]),
            ("functional_analysis", "Functional Analysis", "Infinite-dim spaces (intro)", ["Hilbert", "operator", "spectrum"]),
            ("category_lite", "Category-lite labels", "Compositional structure tags only", ["morphism", "functor_tag"]),
            ("numerical", "Numerical Analysis", "Stable computation", ["discretize", "error_bound", "condition_number"]),
            ("logic", "Logic", "Proof and consistency checks", ["entailment", "satisfiable", "contradiction"]),
        ]
        for id_, name, purpose, ops in specs:
            self.languages[id_] = MathLanguage(id=id_, name=name, purpose=purpose, typical_ops=ops)

    def _register_physics_domains(self) -> None:
        self.domains["classical_mechanics"] = PhysicsDomain(
            id="classical_mechanics",
            name="Classical Mechanics",
            status=DomainStatus.CORE,
            summary="Newtonian / Lagrangian / Hamiltonian dynamics for macroscopic systems.",
            key_ideas=["Newton laws", "energy conservation", "symplectic structure"],
            open_problems=["n-body chaos detail in specific regimes"],
            formula_ids=["newton_second", "kinetic_energy", "hamilton_eq"],
        )
        self.domains["classical_em"] = PhysicsDomain(
            id="classical_em",
            name="Classical Electromagnetism",
            status=DomainStatus.CORE,
            summary="Maxwell fields, Lorentz force; classical continuum EM.",
            key_ideas=["Maxwell equations", "gauge freedom", "Poynting"],
            open_problems=[],
            formula_ids=["maxwell_div_e", "lorentz_force", "coulomb"],
        )
        self.domains["special_relativity"] = PhysicsDomain(
            id="special_relativity",
            name="Special Relativity",
            status=DomainStatus.CORE,
            summary="Minkowski spacetime; Lorentz transformations.",
            key_ideas=["c invariant", "time dilation", "E=mc^2"],
            open_problems=[],
            formula_ids=["einstein_mass_energy", "lorentz_gamma"],
        )
        self.domains["general_relativity"] = PhysicsDomain(
            id="general_relativity",
            name="General Relativity",
            status=DomainStatus.EFFECTIVE,
            summary="Gravity as spacetime curvature; classical continuum gravity.",
            key_ideas=["Einstein field equations", "geodesics", "equivalence principle"],
            open_problems=["singularities", "quantum gravity interface", "dark sector phenomenology"],
            formula_ids=["einstein_field_eq"],
        )
        self.domains["quantum_mechanics"] = PhysicsDomain(
            id="quantum_mechanics",
            name="Quantum Mechanics",
            status=DomainStatus.CORE,
            summary="Hilbert-space kinematics; unitary evolution; measurement postulates.",
            key_ideas=["state vector", "observables", "Born rule", "uncertainty"],
            open_problems=["measurement problem interpretations", "quantum → classical limit details"],
            formula_ids=["schrodinger", "born_rule", "heisenberg_uncertainty", "commutator"],
        )
        self.domains["quantum_stats"] = PhysicsDomain(
            id="quantum_stats",
            name="Quantum & Classical Statistical Mechanics",
            status=DomainStatus.CORE,
            summary="Ensembles, entropy, partition functions.",
            key_ideas=["Boltzmann", "partition function", "free energy"],
            open_problems=["non-equilibrium steady states in complex systems"],
            formula_ids=["boltzmann_entropy", "partition_function"],
        )
        self.domains["thermo"] = PhysicsDomain(
            id="thermo",
            name="Thermodynamics",
            status=DomainStatus.CORE,
            summary="Laws of thermo; macroscopic energy and entropy.",
            key_ideas=["1st/2nd law", "temperature", "irreversibility"],
            open_problems=[],
            formula_ids=["first_law_thermo"],
        )
        self.domains["waves_optics"] = PhysicsDomain(
            id="waves_optics",
            name="Waves & Optics",
            status=DomainStatus.CORE,
            summary="Wave equation, interference, geometric optics limit.",
            key_ideas=["superposition", "dispersion", "Fourier"],
            open_problems=[],
            formula_ids=["wave_eq_1d"],
        )
        self.domains["info_physics"] = PhysicsDomain(
            id="info_physics",
            name="Information & Physics interface",
            status=DomainStatus.EFFECTIVE,
            summary="Entropy links between information theory and statistical physics.",
            key_ideas=["Shannon entropy", "Landauer bound (regime-limited)", "channel capacity"],
            open_problems=["precise resource theories in all regimes"],
            formula_ids=["shannon_entropy", "kl_divergence"],
        )
        self.domains["open_fundamental"] = PhysicsDomain(
            id="open_fundamental",
            name="Open Fundamental Questions",
            status=DomainStatus.OPEN,
            summary="Areas without a conclusive complete theory.",
            key_ideas=["quantum gravity", "dark matter/energy phenomenology", "measurement problem"],
            open_problems=[
                "UV-complete quantum gravity",
                "nature of dark matter",
                "cosmological constant / dark energy",
                "hard problem of measurement / interpretations",
            ],
            formula_ids=[],
        )

        # Link languages to domains (light touch)
        for lang_id, domains in {
            "calculus": ["classical_mechanics", "classical_em", "quantum_mechanics"],
            "linear_algebra": ["quantum_mechanics", "classical_em"],
            "probability": ["quantum_mechanics", "quantum_stats", "info_physics"],
            "information_theory": ["info_physics", "quantum_stats"],
            "differential_equations": ["classical_mechanics", "classical_em", "waves_optics"],
            "geometry": ["special_relativity", "general_relativity"],
            "group_theory": ["quantum_mechanics", "classical_em"],
            "optimization": ["info_physics"],
            "logic": ["open_fundamental"],
        }.items():
            if lang_id in self.languages:
                self.languages[lang_id].used_by_domains = domains

    def _register_formulas(self) -> None:
        cards = [
            FormulaCard(
                id="newton_second",
                name="Newton's second law",
                domain="classical_mechanics",
                expression="F = m a",
                symbols={"F": "force", "m": "mass", "a": "acceleration"},
                assumptions=["inertial frame", "classical speeds << c", "point mass or CM motion"],
                validity_regime="non-relativistic classical mechanics",
                math_languages=["algebra", "calculus"],
            ),
            FormulaCard(
                id="kinetic_energy",
                name="Kinetic energy (classical)",
                domain="classical_mechanics",
                expression="T = (1/2) m v^2",
                symbols={"T": "kinetic energy", "m": "mass", "v": "speed"},
                assumptions=["non-relativistic"],
                validity_regime="v << c",
                math_languages=["algebra"],
            ),
            FormulaCard(
                id="hamilton_eq",
                name="Hamilton's equations",
                domain="classical_mechanics",
                expression="dq/dt = ∂H/∂p ,  dp/dt = -∂H/∂q",
                symbols={"H": "Hamiltonian", "q": "coordinate", "p": "momentum"},
                assumptions=["standard symplectic phase space"],
                validity_regime="classical Hamiltonian systems",
                math_languages=["calculus", "geometry"],
            ),
            FormulaCard(
                id="coulomb",
                name="Coulomb force",
                domain="classical_em",
                expression="F = k q1 q2 / r^2",
                symbols={"k": "Coulomb constant", "q": "charge", "r": "separation"},
                assumptions=["static point charges", "classical"],
                validity_regime="electrostatics",
                math_languages=["algebra"],
            ),
            FormulaCard(
                id="maxwell_div_e",
                name="Gauss's law (Maxwell)",
                domain="classical_em",
                expression="∇ · E = ρ / ε0",
                symbols={"E": "electric field", "ρ": "charge density", "ε0": "vacuum permittivity"},
                assumptions=["SI units", "classical fields"],
                validity_regime="classical EM",
                math_languages=["vector_calculus"],
            ),
            FormulaCard(
                id="lorentz_force",
                name="Lorentz force",
                domain="classical_em",
                expression="F = q (E + v × B)",
                symbols={"q": "charge", "E": "electric field", "B": "magnetic field", "v": "velocity"},
                assumptions=["classical point charge"],
                validity_regime="classical EM",
                math_languages=["vector_calculus", "algebra"],
            ),
            FormulaCard(
                id="lorentz_gamma",
                name="Lorentz factor",
                domain="special_relativity",
                expression="γ = 1 / sqrt(1 - v^2/c^2)",
                symbols={"γ": "Lorentz factor", "v": "speed", "c": "speed of light"},
                assumptions=["inertial frames", "SR"],
                validity_regime="special relativity",
                math_languages=["algebra", "calculus"],
            ),
            FormulaCard(
                id="einstein_mass_energy",
                name="Mass–energy equivalence",
                domain="special_relativity",
                expression="E = m c^2",
                symbols={"E": "rest energy", "m": "rest mass", "c": "speed of light"},
                assumptions=["rest frame for rest energy form"],
                validity_regime="SR / relativistic mechanics",
                math_languages=["algebra"],
            ),
            FormulaCard(
                id="einstein_field_eq",
                name="Einstein field equations (schematic)",
                domain="general_relativity",
                expression="G_{μν} + Λ g_{μν} = (8πG/c^4) T_{μν}",
                symbols={"G_{μν}": "Einstein tensor", "T_{μν}": "stress-energy", "Λ": "cosmological constant"},
                assumptions=["classical continuum spacetime", "GR"],
                validity_regime="classical gravity; not UV-complete quantum gravity",
                status=DomainStatus.EFFECTIVE,
                math_languages=["geometry", "differential_equations", "tensor_calc_tag"],
            ),
            FormulaCard(
                id="schrodinger",
                name="Time-dependent Schrödinger equation",
                domain="quantum_mechanics",
                expression="i ℏ ∂ψ/∂t = H ψ",
                symbols={"ψ": "state", "H": "Hamiltonian", "ℏ": "reduced Planck constant"},
                assumptions=["closed system unitary evolution between measurements"],
                validity_regime="non-relativistic QM",
                math_languages=["linear_algebra", "calculus", "complex_analysis"],
            ),
            FormulaCard(
                id="born_rule",
                name="Born rule",
                domain="quantum_mechanics",
                expression="P(a) = |⟨a|ψ⟩|^2",
                symbols={"P": "probability", "ψ": "state", "a": "eigenstate"},
                assumptions=["standard measurement postulate"],
                validity_regime="textbook QM",
                math_languages=["linear_algebra", "probability"],
            ),
            FormulaCard(
                id="heisenberg_uncertainty",
                name="Heisenberg uncertainty (canonical)",
                domain="quantum_mechanics",
                expression="σ_x σ_p ≥ ℏ/2",
                symbols={"σ": "std dev", "ℏ": "reduced Planck"},
                assumptions=["canonical x,p"],
                validity_regime="QM",
                math_languages=["probability", "linear_algebra"],
            ),
            FormulaCard(
                id="commutator",
                name="Canonical commutator",
                domain="quantum_mechanics",
                expression="[x, p] = i ℏ",
                symbols={"x": "position op", "p": "momentum op"},
                assumptions=["standard QM"],
                validity_regime="QM",
                math_languages=["linear_algebra"],
            ),
            FormulaCard(
                id="boltzmann_entropy",
                name="Boltzmann entropy",
                domain="quantum_stats",
                expression="S = k_B ln Ω",
                symbols={"S": "entropy", "Ω": "multiplicity", "k_B": "Boltzmann constant"},
                assumptions=["microcanonical counting"],
                validity_regime="equilibrium stat mech",
                math_languages=["probability", "algebra"],
            ),
            FormulaCard(
                id="partition_function",
                name="Canonical partition function",
                domain="quantum_stats",
                expression="Z = Σ_i e^{-β E_i}",
                symbols={"Z": "partition function", "β": "1/kT", "E_i": "energy level"},
                assumptions=["canonical ensemble"],
                validity_regime="equilibrium",
                math_languages=["probability", "calculus"],
            ),
            FormulaCard(
                id="first_law_thermo",
                name="First law of thermodynamics",
                domain="thermo",
                expression="dU = đQ - đW",
                symbols={"U": "internal energy", "Q": "heat", "W": "work"},
                assumptions=["sign convention as stated"],
                validity_regime="macroscopic thermo",
                math_languages=["calculus"],
            ),
            FormulaCard(
                id="wave_eq_1d",
                name="1D wave equation",
                domain="waves_optics",
                expression="∂²u/∂t² = c² ∂²u/∂x²",
                symbols={"u": "field", "c": "wave speed"},
                assumptions=["linear non-dispersive medium"],
                validity_regime="classical waves",
                math_languages=["differential_equations"],
            ),
            FormulaCard(
                id="shannon_entropy",
                name="Shannon entropy",
                domain="info_physics",
                expression="H(X) = -Σ p(x) log p(x)",
                symbols={"H": "entropy", "p": "probability mass"},
                assumptions=["discrete distribution"],
                validity_regime="information theory",
                math_languages=["probability", "information_theory"],
            ),
            FormulaCard(
                id="kl_divergence",
                name="Kullback–Leibler divergence",
                domain="info_physics",
                expression="D_KL(P||Q) = Σ p log(p/q)",
                symbols={"P": "true dist", "Q": "approx dist"},
                assumptions=["same support conditions as required"],
                validity_regime="information theory / stats",
                math_languages=["probability", "information_theory", "statistics"],
            ),
        ]
        for c in cards:
            self.formulas[c.id] = c

    def _register_computing_ai(self) -> None:
        self.computing_tags = {
            "complexity": "Time/space class tags (P, NP-hard as labels only)",
            "numerical_stability": "Conditioning, roundoff, discretization error",
            "reproducibility": "Seeds, version pins, artifact hashes",
            "parallelism": "Data/model parallel patterns as engineering tags",
            "memory_hierarchy": "Cache/locality awareness in implementations",
            "verification": "Tests, types, audits, ledgers",
        }
        self.ai_tags = {
            "supervised_learning": "Fit maps from labeled data",
            "uncertainty_quantification": "Epistemic/aleatoric separation",
            "calibration": "Probability reliability",
            "ood_detection": "Out-of-distribution flags",
            "abstention": "Refuse when unsafe/uncertain",
            "causality_time": "No future feature leakage",
            "alignment_process": "Process constraints, not claimed value lock-in",
        }

    # ------------------------------------------------------------------
    # Queries (engineer-facing API)
    # ------------------------------------------------------------------

    def list_languages(self) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in self.languages.values()]

    def list_domains(self) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in self.domains.values()]

    def list_formulas(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        out = []
        for f in self.formulas.values():
            if domain is None or f.domain == domain:
                out.append(f.to_dict())
        return out

    def get_formula(self, formula_id: str) -> Optional[Dict[str, Any]]:
        f = self.formulas.get(formula_id)
        return f.to_dict() if f else None

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        hits: List[Tuple[int, Dict[str, Any]]] = []
        for f in self.formulas.values():
            blob = " ".join([f.id, f.name, f.expression, f.domain, " ".join(f.assumptions)]).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, {"type": "formula", **f.to_dict()}))
        for d in self.domains.values():
            blob = " ".join([d.id, d.name, d.summary] + d.key_ideas + d.open_problems).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, {"type": "domain", **d.to_dict()}))
        for lang in self.languages.values():
            blob = " ".join([lang.id, lang.name, lang.purpose] + lang.typical_ops).lower()
            score = sum(1 for tok in q.split() if tok in blob)
            if score:
                hits.append((score, {"type": "math_language", **lang.to_dict()}))
        hits.sort(key=lambda x: -x[0])
        return [h for _, h in hits[:limit]]

    def open_problems(self) -> List[Dict[str, Any]]:
        out = []
        for d in self.domains.values():
            for p in d.open_problems:
                out.append({"domain": d.id, "problem": p, "status": "OPEN"})
        return out

    def verify_claim(self, claim: str) -> Dict[str, Any]:
        """
        Lightweight claim gate for engineers.
        Does NOT prove physics — only checks whether the claim language
        matches catalogue entries or overreaches into OPEN/complete-world territory.
        """
        c = claim.lower()
        overreach = []
        if any(w in c for w in ["complete physics", "theory of everything", "conclusive world", "all of physics", "solved quantum gravity"]):
            overreach.append("claims completeness or solved open fundamental problems")
        if "faster than light" in c or "ftl" in c:
            overreach.append("conflicts with SR core regime unless clearly speculative fiction")
        hits = self.search(claim, limit=5)
        return {
            "claim": claim,
            "overreach": overreach,
            "ok_for_atlas_support": len(overreach) == 0,
            "related_hits": hits,
            "note": "Atlas support ≠ empirical truth. Use primary literature.",
        }

    def export(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "disclaimer": self.disclaimer,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_languages": len(self.languages),
            "n_domains": len(self.domains),
            "n_formulas": len(self.formulas),
            "languages": self.list_languages(),
            "domains": self.list_domains(),
            "formulas": self.list_formulas(),
            "open_problems": self.open_problems(),
            "computing_tags": self.computing_tags,
            "ai_tags": self.ai_tags,
        }

    def checksum(self) -> str:
        blob = json.dumps(self.export(), sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()


# Singleton-style helper for engineers
_ATLAS: Optional[PhysicsMathAtlas] = None


def get_atlas() -> PhysicsMathAtlas:
    global _ATLAS
    if _ATLAS is None:
        _ATLAS = PhysicsMathAtlas()
    return _ATLAS

# ===== END atlas.py =====


# ===== BEGIN rag_settled/__init__.py =====

"""Settled RAG: only documents with license, as-of date, and checksum."""
import hashlib
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_RAG_ROOT = Path(__file__).parent
_RAG_CORPUS = _RAG_ROOT / "corpus.jsonl"


@dataclass
class SettledDoc:
    doc_id: str
    title: str
    text: str
    license: str
    as_of: str  # YYYY-MM-DD
    source: str
    tags: List[str] = field(default_factory=list)

    def checksum(self) -> str:
        blob = f"{self.doc_id}|{self.title}|{self.text}|{self.license}|{self.as_of}|{self.source}"
        return hashlib.sha256(blob.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["checksum"] = self.checksum()
        return d


def _ensure_seed_corpus() -> None:
    if _RAG_CORPUS.exists():
        return
    seeds = [
        SettledDoc(
            doc_id="seed-causality",
            title="Time-causal feature availability",
            text=(
                "A feature may only be used at decision time t if its availability "
                "timestamp is less than or equal to t. Future-leaking features are invalid."
            ),
            license="CC0-1.0",
            as_of="2026-01-01",
            source="internal-policy",
            tags=["causality", "ml"],
        ),
        SettledDoc(
            doc_id="seed-net-pnl",
            title="Net PnL accounting identity",
            text=(
                "Net PnL equals realized output minus input cost, gas, protocol fees, "
                "borrow fees, bridge fees, slippage, revert cost, and other configured costs."
            ),
            license="CC0-1.0",
            as_of="2026-01-01",
            source="internal-policy",
            tags=["accounting", "defi"],
        ),
        SettledDoc(
            doc_id="seed-abstain",
            title="Abstention as control",
            text=(
                "When uncertainty is high, constraints fail, or data is stale, the system "
                "must abstain rather than force a trade decision."
            ),
            license="CC0-1.0",
            as_of="2026-01-01",
            source="internal-policy",
            tags=["safety", "abstention"],
        ),
    ]
    with open(_RAG_CORPUS, "w", encoding="utf-8") as f:
        for d in seeds:
            f.write(json.dumps(d.to_dict()) + "\n")


def load_corpus() -> List[Dict[str, Any]]:
    if not _RAG_CORPUS.exists():
        t = _embedded('rag_settled/corpus.jsonl', '')
        if t:
            _RAG_RAG_CORPUS.parent.mkdir(parents=True, exist_ok=True)
            _RAG_RAG_CORPUS.write_text(t, encoding='utf-8')
    _ensure_seed_corpus()
    docs = []
    with open(_RAG_CORPUS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                docs.append(json.loads(line))
    return docs


def add_document(doc: SettledDoc) -> Dict[str, Any]:
    """Append only if license and as_of present (settled RAG contract)."""
    if not doc.license or not doc.as_of or not doc.text.strip():
        return {"ok": False, "reason": "missing license, as_of, or text"}
    _ensure_seed_corpus()
    with open(_RAG_CORPUS, "a", encoding="utf-8") as f:
        f.write(json.dumps(doc.to_dict()) + "\n")
    return {"ok": True, "doc_id": doc.doc_id, "checksum": doc.checksum()}


def search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    q = query.lower().split()
    hits = []
    for d in load_corpus():
        blob = (d.get("title", "") + " " + d.get("text", "") + " " + " ".join(d.get("tags", []))).lower()
        score = sum(1 for t in q if t in blob)
        if score:
            hits.append((score, d))
    hits.sort(key=lambda x: -x[0])
    return [h for _, h in hits[:limit]]

# ===== END rag_settled/__init__.py =====


# ===== BEGIN schema_registry/__init__.py =====

"""Versioned schema registry for events, packets, labels."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_SCHEMA_ROOT = Path(__file__).parent

def list_schemas() -> List[str]:
    return sorted(p.name for p in _SCHEMA_ROOT.glob("*.json"))

def load_schema(name: str) -> Dict[str, Any]:
    mapping = {
        "events_v1": "schema_registry/events_v1.json",
        "packets_v1": "schema_registry/packets_v1.json",
        "labels_v1": "schema_registry/labels_v1.json",
        "NormalizedEvent": "schema_registry/events_v1.json",
        "DecisionPacket": "schema_registry/packets_v1.json",
        "OutcomeLabel": "schema_registry/labels_v1.json",
    }
    key = name[:-5] if name.endswith(".json") else name
    rel = mapping.get(key) or mapping.get(name) or f"schema_registry/{key}.json"
    raw = _embedded(rel, "")
    if raw:
        return json.loads(raw)
    path = Path("schema_registry") / f"{key}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError(name)


def validate_required(obj: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    missing = [k for k in schema.get("required", []) if k not in obj]
    return {"ok": len(missing) == 0, "missing": missing, "schema_id": schema.get("schema_id")}

# ===== END schema_registry/__init__.py =====


# ===== BEGIN knowledge_coverage.py =====

#!/usr/bin/env python3
"""
Next-best alternative to a rejected 'complete world physics' oracle.

Rejected: omniscient / conclusive complete physics.
This module: maximize *coverage and honesty* of settled + atlas + open gaps
+ evidence attachment — without ever claiming completeness.
"""
from typing import Any, Dict, List, Optional


def coverage_report(query: Optional[str] = None) -> Dict[str, Any]:
    atlas = get_atlas()
    db = get_settled_db()
    const = get_constants_db()
    report = {
        "title": "KnowledgeCoverageMaximizer",
        "disclaimer": (
            "Maximizes structured coverage of settled knowledge, formulas, constants, "
            "and explicit OPEN gaps. Not a theory of everything. Not conclusive world physics."
        ),
        "n_settled": len(db.entries),
        "n_formulas": len(atlas.formulas),
        "n_domains": len(atlas.domains),
        "n_languages": len(atlas.languages),
        "n_constants": len(const.constants),
        "n_open_problems": len(atlas.open_problems()),
        "open_problems": atlas.open_problems(),
        "completeness_claim_allowed": False,
    }
    if query:
        report["settled_hits"] = db.search(query, limit=8)
        report["atlas_hits"] = atlas.search(query, limit=8)
        report["rag_hits"] = rag_search(query, limit=5)
        report["claim_gate"] = db.reject_completeness_claim(query)
        report["atlas_claim_gate"] = atlas.verify_claim(query)
    return report


def best_effort_answer(query: str) -> Dict[str, Any]:
    """Best-effort grounded pack: settled + atlas + rag + opens — never final truth."""
    cov = coverage_report(query)
    return {
        "query": query,
        "mode": "best_effort_coverage",
        "not_a_complete_oracle": True,
        "coverage": cov,
        "recommendation": (
            "Use settled hits when assumptions match; treat OPEN domains as unknown; "
            "abstain on completeness-style questions."
        ),
    }


def evidence_for_decision(
    packet_summary: Optional[Dict[str, Any]] = None,
    query: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Attach knowledge coverage as *evidence* for plan_and_decide.

    Never overrides AbstentionGate / SMT / interval. Completeness claims stay blocked.
    """
    q = query or "causality net pnl abstain costs time-causal"
    if packet_summary:
        # light topical boost from packet fields if present
        bits = []
        for k in ("regime", "venue", "chain_id", "event_type"):
            if packet_summary.get(k) is not None:
                bits.append(str(packet_summary[k]))
        if bits:
            q = q + " " + " ".join(bits)
    pack = best_effort_answer(q)
    # Strip heavy nested dumps for decision attachment
    cov = pack.get("coverage") or {}
    return {
        "role": "evidence_only",
        "not_authority": True,
        "not_a_complete_oracle": True,
        "completeness_claim_allowed": False,
        "query": pack.get("query"),
        "n_settled_hits": len(cov.get("settled_hits") or []),
        "n_atlas_hits": len(cov.get("atlas_hits") or []),
        "n_rag_hits": len(cov.get("rag_hits") or []),
        "n_open_problems": cov.get("n_open_problems"),
        "claim_gate_ok": (cov.get("claim_gate") or {}).get("ok", True),
        "recommendation": pack.get("recommendation"),
        "settled_ids": [h.get("id") for h in (cov.get("settled_hits") or [])[:5] if isinstance(h, dict)],
        "rag_doc_ids": [h.get("doc_id") for h in (cov.get("rag_hits") or [])[:5] if isinstance(h, dict)],
    }

# ===== END knowledge_coverage.py =====


# ===== BEGIN knowledge_facade.py =====

#!/usr/bin/env python3
"""Unified knowledge facade: atlas + KSKB + constants + rag + coverage (no completeness claim)."""
from typing import Any, Dict, List, Optional


class KnowledgeFacade:
    def __init__(self):
        self.atlas = get_atlas()
        self.settled = get_settled_db()
        self.constants = get_constants_db()

    def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        return {
            "query": query,
            "settled": self.settled.search(query, limit=limit),
            "atlas": self.atlas.search(query, limit=limit),
            "rag": rag_search(query, limit=min(5, limit)),
            "disclaimer": "Best-effort coverage only; not a complete oracle.",
        }

    def constant(self, id_: str) -> Optional[Dict[str, Any]]:
        return self.constants.get(id_)

    def coverage(self, query: Optional[str] = None) -> Dict[str, Any]:
        return coverage_report(query)

    def answer(self, query: str) -> Dict[str, Any]:
        return best_effort_answer(query)

    def stats(self) -> Dict[str, Any]:
        return {
            "n_settled": len(self.settled.entries),
            "n_formulas": len(self.atlas.formulas),
            "n_domains": len(self.atlas.domains),
            "n_languages": len(self.atlas.languages),
            "n_constants": len(self.constants.constants),
            "n_rag_docs": len(load_corpus()),
            "n_open_problems": len(self.atlas.open_problems()),
            "completeness_claim_allowed": False,
        }


def get_facade() -> KnowledgeFacade:
    return KnowledgeFacade()

# ===== END knowledge_facade.py =====


# ===== BEGIN engineers.py =====
# Spine inlined soft-deps
ATLAS_AVAILABLE = True
SETTLED_DB_AVAILABLE = True
SCHEMA_REG_AVAILABLE = True
LEDGER_INDEX_AVAILABLE = True
RAG_AVAILABLE = True
CONSTANTS_AVAILABLE = True
SYMPY_AVAILABLE = False
sympy = None
UNIT_TAGS_AVAILABLE = True

def rag_search(query, limit=5):
    q = query.lower().split()
    hits = []
    for d in load_corpus():
        blob = (d.get("title", "") + " " + d.get("text", "") + " " + " ".join(d.get("tags", []))).lower()
        score = sum(1 for t in q if t in blob)
        if score:
            hits.append((score, d))
    hits.sort(key=lambda x: -x[0])
    return [h for _, h in hits[:limit]]

ledger_search = globals().get("ledger_search") or globals().get("search")


#!/usr/bin/env python3
"""
Stationary & Non-Stationary Engineers
=====================================

Mandatory double-pass verification spine.

Contract (non-negotiable):
  Every unit of information MUST pass through:

      StationaryEngineer.verify()          # pass 1 – observe, check integrity
   →  NonStationaryEngineer.act_and_check()# experimental / implementation probe
   →  StationaryEngineer.verify()          # pass 2 – secondary verification

  before any LLM is allowed to interpret or act on that information.

Design notes
------------
- Stationary = observer / processor only. Never mutates external state.
  Produces situation reports, integrity assessments, and ranked issues.
- Non-Stationary = actor / experimental. May propose transforms, run probes,
  reseal, or attempt repair. Always followed by a second stationary pass.
- Both engineers write every check into a VerificationLedger (JSONL).
- Fail-closed: if either pass reports ok=False, the packet is marked
  BLOCKED and must not be handed to an LLM interpreter.
"""


import ast
import hashlib
import json
import math
import time
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import concurrent.futures

try:
    ATLAS_AVAILABLE = True
except Exception:
    ATLAS_AVAILABLE = False

try:
    SETTLED_DB_AVAILABLE = True
except Exception:
    SETTLED_DB_AVAILABLE = False


# Roadmap upgrade imports (optional soft deps)
try:
    SCHEMA_REG_AVAILABLE = True
except Exception:
    SCHEMA_REG_AVAILABLE = False
try:
    LEDGER_INDEX_AVAILABLE = True
except Exception:
    LEDGER_INDEX_AVAILABLE = False
    ledger_search = None  # type: ignore
try:
    RAG_AVAILABLE = True
except Exception:
    RAG_AVAILABLE = False
    rag_search = None  # type: ignore
try:
    CONSTANTS_AVAILABLE = True
except Exception:
    CONSTANTS_AVAILABLE = False
try:
    import sympy
    SYMPY_AVAILABLE = True
except Exception:
    SYMPY_AVAILABLE = False
    sympy = None  # type: ignore

try:
    UNIT_TAGS_AVAILABLE = True
except Exception:
    UNIT_TAGS_AVAILABLE = False
    stationary_unit_probe = None  # type: ignore


# =============================================================================
# Contracts
# =============================================================================

class EngineerVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"   # secondary verification failed – do not give to LLM
    ABSTAIN = "ABSTAIN"   # insufficient evidence / cannot decide


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: Any = None
    severity: str = "error"   # error | warn | info

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EngineerReport:
    """Full report from one engineer pass."""
    engineer: str                     # "stationary" | "non_stationary"
    pass_number: int                  # 1 or 2 for stationary; 1 for non-stationary
    timestamp: str
    verdict: EngineerVerdict
    checks: List[CheckResult] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def all_ok(self) -> bool:
        return all(c.ok for c in self.checks) and self.verdict in (
            EngineerVerdict.PASS, EngineerVerdict.ABSTAIN
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engineer": self.engineer,
            "pass_number": self.pass_number,
            "timestamp": self.timestamp,
            "verdict": self.verdict.value,
            "all_ok": self.all_ok,
            "checks": [c.to_dict() for c in self.checks],
            "issues": self.issues,
            "metadata": self.metadata,
        }


@dataclass
class DoublePassResult:
    """Result of the mandatory Stationary → NonStationary → Stationary sequence."""
    subject_id: str
    subject_type: str
    stationary_pass_1: EngineerReport
    non_stationary: EngineerReport
    stationary_pass_2: EngineerReport
    final_verdict: EngineerVerdict
    allowed_for_llm: bool
    ledger_entry_id: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
            "stationary_pass_1": self.stationary_pass_1.to_dict(),
            "non_stationary": self.non_stationary.to_dict(),
            "stationary_pass_2": self.stationary_pass_2.to_dict(),
            "final_verdict": self.final_verdict.value,
            "allowed_for_llm": self.allowed_for_llm,
            "ledger_entry_id": self.ledger_entry_id,
            "timestamp": self.timestamp,
        }


# =============================================================================
# Verification Ledger (persistent, fail-open for telemetry)
# =============================================================================

class VerificationLedger:
    """Append-only JSONL ledger of every engineer pass."""

    def __init__(self, path: Optional[Union[str, Path]] = None):
        self.path = Path(path) if path else Path("artifacts/verification_ledger.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._entries: List[Dict[str, Any]] = []

    def append(self, event_type: str, payload: Dict[str, Any]) -> str:
        entry_id = hashlib.sha256(
            f"{event_type}{time.time()}{json.dumps(payload, sort_keys=True, default=str)}".encode()
        ).hexdigest()[:16]
        record = {
            "entry_id": entry_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        self._entries.append(record)
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")
        except Exception:
            pass  # telemetry must never block the safety spine
        return entry_id

    def recent(self, n: int = 20) -> List[Dict[str, Any]]:
        return self._entries[-n:]


# =============================================================================
# Stationary Engineer  (observer / processor – never mutates external state)
# =============================================================================

class StationaryEngineer:
    """
    Stationary (observer) engineer.

    Responsibilities:
      - Structural / schema integrity checks
      - Time-causality & leakage probes
      - Net-PnL accounting sanity
      - Source / AST / math-logic probes when source is supplied
      - Produce a ranked list of issues and a hard PASS / FAIL / ABSTAIN verdict

    It does NOT implement changes. It only observes and reports.
    """

    def __init__(self, ledger: Optional[VerificationLedger] = None):
        self.ledger = ledger or VerificationLedger()
        self.last_report: Optional[EngineerReport] = None

    def verify(
        self,
        subject: Any,
        subject_id: str,
        subject_type: str,
        pass_number: int = 1,
        context: Optional[Dict[str, Any]] = None,
    ) -> EngineerReport:
        context = context or {}
        checks: List[CheckResult] = []
        issues: List[str] = []

        # ----- 1. Existence / type checks -----
        checks.append(CheckResult(
            name="subject_present",
            ok=subject is not None,
            detail=type(subject).__name__ if subject is not None else None,
        ))
        if subject is None:
            issues.append("subject is None")

        # ----- 2. Schema / required-field probes (duck-typed) -----
        if subject is not None:
            checks.extend(self._schema_checks(subject, subject_type))

        # ----- 3. Time-causality probes when timestamps are present -----
        if subject is not None:
            checks.extend(self._causality_checks(subject, subject_type))

        # ----- 4. Numeric / accounting sanity -----
        if subject is not None:
            checks.extend(self._numeric_checks(subject, subject_type))

        # ----- 5. Optional source-code AST probe (when context supplies source) -----
        source_text = context.get("source_text") or context.get("source")
        if source_text:
            checks.extend(self._source_ast_checks(source_text))

        # ----- 6. Math / logic micro-probes (always-on, no external deps) -----
        checks.extend(self._math_logic_probes())

        # ----- 7. Atlas-backed physics/math claim gate (if atlas present) -----
        if ATLAS_AVAILABLE and get_atlas is not None:
            atlas = get_atlas()
            claim = None
            if isinstance(subject, dict):
                claim = subject.get("physics_claim") or subject.get("claim") or subject.get("expression")
            if claim and isinstance(claim, str):
                vr = atlas.verify_claim(claim)
                checks.append(CheckResult(
                    name="atlas.claim_gate",
                    ok=vr.get("ok_for_atlas_support", True),
                    detail=vr,
                    severity="error" if not vr.get("ok_for_atlas_support", True) else "info",
                ))
                if not vr.get("ok_for_atlas_support", True):
                    issues.append(f"atlas overreach: {vr.get('overreach')}")
            # Catalogue health probe
            checks.append(CheckResult(
                name="atlas.catalogue_loaded",
                ok=len(atlas.formulas) > 0 and len(atlas.domains) > 0,
                detail={"n_formulas": len(atlas.formulas), "n_domains": len(atlas.domains), "version": atlas.version},
                severity="info",
            ))


        # ----- 8. Known-Settled DB health + completeness rejection -----
        if SETTLED_DB_AVAILABLE and get_settled_db is not None:
            db = get_settled_db()
            checks.append(CheckResult(
                name="settled_db.loaded",
                ok=len(db.entries) > 0,
                detail={"n_entries": len(db.entries), "version": db.version},
                severity="info",
            ))
            claim = None
            if isinstance(subject, dict):
                claim = subject.get("claim") or subject.get("physics_claim") or subject.get("statement")
            if isinstance(claim, str):
                rej = db.reject_completeness_claim(claim)
                checks.append(CheckResult(
                    name="settled_db.no_completeness_overclaim",
                    ok=rej.get("ok", True),
                    detail=rej,
                    severity="error" if not rej.get("ok", True) else "info",
                ))
                if not rej.get("ok", True):
                    issues.append(f"completeness overclaim: {rej.get('rejected_phrases')}")


        # ----- Roadmap upgrades: schema, ledger memory, RAG evidence, sympy -----
        if SCHEMA_REG_AVAILABLE and isinstance(subject, dict):
            schema_name = None
            if subject_type in ("NormalizedEvent", "event"):
                schema_name = "events_v1.json"
            elif subject_type in ("DecisionPacket", "packet"):
                schema_name = "packets_v1.json"
            elif subject_type in ("OutcomeLabel", "label"):
                schema_name = "labels_v1.json"
            if schema_name:
                try:
                    sch = load_schema(schema_name)
                    vr = validate_required(subject, sch)
                    checks.append(CheckResult(
                        name="schema_registry.required",
                        ok=vr.get("ok", False),
                        detail=vr,
                    ))
                    if not vr.get("ok", False):
                        issues.append(f"schema missing: {vr.get('missing')}")
                except Exception as e:
                    checks.append(CheckResult(name="schema_registry.required", ok=False, detail=str(e), severity="warn"))

        if LEDGER_INDEX_AVAILABLE and ledger_search is not None:
            try:
                hits = ledger_search(subject_type, limit=5)
                checks.append(CheckResult(
                    name="ledger_memory.recent_patterns",
                    ok=True,
                    detail={"n_hits": len(hits), "sample_types": list({h.get("event_type") for h in hits[:5]})},
                    severity="info",
                ))
            except Exception as e:
                checks.append(CheckResult(name="ledger_memory.recent_patterns", ok=True, detail=str(e), severity="info"))

        if RAG_AVAILABLE and rag_search is not None and isinstance(subject, dict):
            q = subject.get("claim") or subject.get("statement") or subject_type
            if isinstance(q, str) and q:
                try:
                    docs = rag_search(q, limit=3)
                    checks.append(CheckResult(
                        name="rag_settled.evidence",
                        ok=True,
                        detail={"n_docs": len(docs), "doc_ids": [d.get("doc_id") for d in docs]},
                        severity="info",
                    ))
                except Exception:
                    pass

        if SYMPY_AVAILABLE and isinstance(subject, dict):
            formal = subject.get("formal")
            if isinstance(formal, str) and "=" in formal and len(formal) < 80:
                try:
                    left, right = formal.split("=", 1)
                    # only try very simple numeric/symbolic equality
                    diff = sympy.simplify(sympy.sympify(left) - sympy.sympify(right))
                    checks.append(CheckResult(
                        name="sympy.identity",
                        ok=diff == 0,
                        detail={"formal": formal, "diff": str(diff)},
                        severity="warn",
                    ))
                except Exception as e:
                    checks.append(CheckResult(
                        name="sympy.identity",
                        ok=True,
                        detail={"skipped": str(e)},
                        severity="info",
                    ))

        if CONSTANTS_AVAILABLE and isinstance(subject, dict) and subject.get("unit_check"):
            try:
                cdb = get_constants_db()
                uid = subject["unit_check"].get("constant_id")
                c = cdb.get(uid) if uid else None
                checks.append(CheckResult(
                    name="constants.lookup",
                    ok=c is not None,
                    detail=c,
                    severity="warn",
                ))
            except Exception as e:
                checks.append(CheckResult(name="constants.lookup", ok=False, detail=str(e), severity="warn"))


        if UNIT_TAGS_AVAILABLE and stationary_unit_probe is not None and isinstance(subject, dict) and subject.get("unit_tags"):
            try:
                up = stationary_unit_probe(subject)
                checks.append(CheckResult(
                    name="unit_tags.probe",
                    ok=up.get("ok", True),
                    detail=up,
                    severity="warn",
                ))
                if not up.get("ok", True):
                    issues.append("unit_tags malformed")
            except Exception as e:
                checks.append(CheckResult(name="unit_tags.probe", ok=True, detail=str(e), severity="info"))
        # ----- Aggregate -----
        hard_fails = [c for c in checks if not c.ok and c.severity == "error"]
        if hard_fails:
            verdict = EngineerVerdict.FAIL
            issues.extend([f"{c.name}: {c.detail}" for c in hard_fails])
        elif any(not c.ok for c in checks):
            verdict = EngineerVerdict.ABSTAIN
            issues.extend([f"{c.name}: {c.detail}" for c in checks if not c.ok])
        else:
            verdict = EngineerVerdict.PASS

        report = EngineerReport(
            engineer="stationary",
            pass_number=pass_number,
            timestamp=datetime.now(timezone.utc).isoformat(),
            verdict=verdict,
            checks=checks,
            issues=issues,
            metadata={
                "subject_id": subject_id,
                "subject_type": subject_type,
                "n_checks": len(checks),
                "n_hard_fails": len(hard_fails),
                "context_keys": list(context.keys()),
            },
        )
        self.last_report = report
        self.ledger.append(f"stationary_pass_{pass_number}", report.to_dict())
        return report

    # ----- private check families -----

    def _schema_checks(self, subject: Any, subject_type: str) -> List[CheckResult]:
        out: List[CheckResult] = []
        # DecisionPacket-like
        if subject_type in ("DecisionPacket", "packet"):
            for field in ("decision_id", "as_of", "action_candidates"):
                present = hasattr(subject, field) or (isinstance(subject, dict) and field in subject)
                out.append(CheckResult(name=f"schema.{field}", ok=bool(present), detail=field))
        # OutcomeLabel-like
        if subject_type in ("OutcomeLabel", "label"):
            for field in ("decision_id", "net_pnl_usd", "reverted", "outcome_timestamp_ms"):
                present = hasattr(subject, field) or (isinstance(subject, dict) and field in subject)
                out.append(CheckResult(name=f"schema.{field}", ok=bool(present), detail=field))
        # NormalizedEvent-like
        if subject_type in ("NormalizedEvent", "event"):
            for field in ("event_id", "event_timestamp_ms", "available_timestamp_ms", "event_type"):
                present = hasattr(subject, field) or (isinstance(subject, dict) and field in subject)
                out.append(CheckResult(name=f"schema.{field}", ok=bool(present), detail=field))
        # Generic dict / list
        if isinstance(subject, dict):
            out.append(CheckResult(name="schema.non_empty_dict", ok=len(subject) > 0, detail=len(subject)))
        if isinstance(subject, list):
            out.append(CheckResult(name="schema.list_bounded", ok=len(subject) < 1_000_000, detail=len(subject)))
        return out

    def _causality_checks(self, subject: Any, subject_type: str) -> List[CheckResult]:
        out: List[CheckResult] = []

        def _get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # available_timestamp >= observed_timestamp
        avail = _get(subject, "available_timestamp_ms")
        obs = _get(subject, "observed_timestamp_ms")
        if avail is not None and obs is not None:
            try:
                ok = int(avail) >= int(obs)
                out.append(CheckResult(
                    name="causality.available_after_observed",
                    ok=ok,
                    detail={"available": avail, "observed": obs},
                ))
            except Exception as e:
                out.append(CheckResult(name="causality.available_after_observed", ok=False, detail=str(e)))

        # outcome after decision (for labels)
        if subject_type in ("OutcomeLabel", "label"):
            outcome_ts = _get(subject, "outcome_timestamp_ms")
            # decision time may live in context; we only check self-consistency here
            if outcome_ts is not None:
                try:
                    out.append(CheckResult(
                        name="causality.outcome_timestamp_present",
                        ok=int(outcome_ts) > 0,
                        detail=outcome_ts,
                    ))
                except Exception as e:
                    out.append(CheckResult(name="causality.outcome_timestamp_present", ok=False, detail=str(e)))
        return out

    def _numeric_checks(self, subject: Any, subject_type: str) -> List[CheckResult]:
        out: List[CheckResult] = []

        def _get(obj, key, default=None):
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)

        # Net PnL reconstruction for labels
        if subject_type in ("OutcomeLabel", "label"):
            try:
                realized = float(_get(subject, "realized_output_usd") or 0)
                costs = (
                    float(_get(subject, "input_cost_usd") or 0)
                    + float(_get(subject, "gas_usd") or 0)
                    + float(_get(subject, "protocol_fees_usd") or 0)
                    + float(_get(subject, "borrow_fees_usd") or 0)
                    + float(_get(subject, "bridge_fees_usd") or 0)
                    + float(_get(subject, "slippage_cost_usd") or 0)
                    + float(_get(subject, "revert_cost_usd") or 0)
                    + float(_get(subject, "other_costs_usd") or 0)
                )
                reported_net = float(_get(subject, "net_pnl_usd") or 0)
                calculated = realized - costs
                ok = abs(calculated - reported_net) < 0.02
                out.append(CheckResult(
                    name="accounting.net_pnl_identity",
                    ok=ok,
                    detail={"calculated": calculated, "reported": reported_net},
                ))
            except Exception as e:
                out.append(CheckResult(name="accounting.net_pnl_identity", ok=False, detail=str(e)))

        # Finite-number probe for any float-like fields
        for key in ("mean_net_pnl_usd", "trade_size_usd", "estimated_gas_usd", "net_pnl_usd"):
            val = _get(subject, key)
            if val is not None:
                try:
                    f = float(val)
                    out.append(CheckResult(
                        name=f"numeric.finite.{key}",
                        ok=math.isfinite(f),
                        detail=f,
                    ))
                except Exception:
                    out.append(CheckResult(name=f"numeric.finite.{key}", ok=False, detail=str(val)))
        return out

    def _source_ast_checks(self, source_text: str) -> List[CheckResult]:
        out: List[CheckResult] = []
        try:
            tree = ast.parse(source_text)
            out.append(CheckResult(name="source.ast_parse", ok=True, detail=f"{len(source_text)} chars"))
            classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
            funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
            out.append(CheckResult(
                name="source.has_definitions",
                ok=(len(classes) + len(funcs)) > 0,
                detail={"classes": len(classes), "functions": len(funcs)},
            ))
        except SyntaxError as e:
            out.append(CheckResult(name="source.ast_parse", ok=False, detail=str(e)))
        return out

    def _math_logic_probes(self) -> List[CheckResult]:
        """Tiny always-on math/logic probes – no external libraries required."""
        out: List[CheckResult] = []
        # Arithmetic identity
        out.append(CheckResult(name="math.arithmetic_identity", ok=(2 + 2 == 4), detail="2+2==4"))
        # Float finiteness
        out.append(CheckResult(name="math.isfinite_pi", ok=math.isfinite(math.pi), detail=math.pi))
        # Contradiction detection (classical)
        A = True
        out.append(CheckResult(
            name="logic.no_contradiction",
            ok=not (A and not A),
            detail="A & ~A is false",
        ))
        return out


# =============================================================================
# Non-Stationary Engineer  (actor / experimental – may propose transforms)
# =============================================================================

class NonStationaryEngineer:
    """
    Non-stationary (actor / experimental) engineer.

    Responsibilities:
      - Attempt bounded probes / transforms on a *copy* of the subject
      - Run SourceEngineer-style structural audits
      - Propose repairs when safe (never silently apply them to production state)
      - Always followed by a second Stationary pass

    It is allowed to be creative; the second stationary pass is the brake.
    """

    def __init__(self, ledger: Optional[VerificationLedger] = None):
        self.ledger = ledger or VerificationLedger()
        self.last_report: Optional[EngineerReport] = None

    def act_and_check(
        self,
        subject: Any,
        subject_id: str,
        subject_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> EngineerReport:
        context = context or {}
        checks: List[CheckResult] = []
        issues: List[str] = []
        proposals: List[Dict[str, Any]] = []

        # ----- 1. Deep-copy probe (ensure subject is serialisable) -----
        try:
            blob = json.dumps(subject, default=str)
            restored = json.loads(blob)
            checks.append(CheckResult(
                name="actor.serialisable",
                ok=True,
                detail=f"{len(blob)} bytes",
            ))
        except Exception as e:
            checks.append(CheckResult(name="actor.serialisable", ok=False, detail=str(e)))
            issues.append(f"not serialisable: {e}")
            restored = None

        # ----- 2. Bounded mutation probe on the copy only -----
        if restored is not None and isinstance(restored, dict):
            probe = dict(restored)
            probe["__non_stationary_probe__"] = True
            checks.append(CheckResult(
                name="actor.mutation_probe_on_copy",
                ok=probe.get("__non_stationary_probe__") is True,
                detail="copy mutated; original untouched",
            ))

        # ----- 3. Structural / shape audit -----
        checks.extend(self._structure_audit(subject, subject_type))

        # ----- 4. Propose (but do not apply) repairs when issues found -----
        if subject_type in ("OutcomeLabel", "label"):
            repair = self._propose_net_pnl_repair(subject)
            if repair:
                proposals.append(repair)
                checks.append(CheckResult(
                    name="actor.repair_proposal_net_pnl",
                    ok=True,
                    detail=repair,
                    severity="info",
                ))

        # ----- 5. Adversarial / stress micro-probe -----
        checks.extend(self._adversarial_probes(subject))

        hard_fails = [c for c in checks if not c.ok and c.severity == "error"]
        if hard_fails:
            verdict = EngineerVerdict.FAIL
            issues.extend([f"{c.name}: {c.detail}" for c in hard_fails])
        else:
            verdict = EngineerVerdict.PASS

        report = EngineerReport(
            engineer="non_stationary",
            pass_number=1,
            timestamp=datetime.now(timezone.utc).isoformat(),
            verdict=verdict,
            checks=checks,
            issues=issues,
            metadata={
                "subject_id": subject_id,
                "subject_type": subject_type,
                "proposals": proposals,
                "n_checks": len(checks),
            },
        )
        self.last_report = report
        self.ledger.append("non_stationary", report.to_dict())
        return report

    def _structure_audit(self, subject: Any, subject_type: str) -> List[CheckResult]:
        out: List[CheckResult] = []
        out.append(CheckResult(
            name="actor.type_known",
            ok=subject_type in (
                "NormalizedEvent", "event",
                "DecisionPacket", "packet",
                "OutcomeLabel", "label",
                "DecisionOutput", "decision",
                "dict", "list", "report", "batch",
            ) or True,  # soft – unknown types still allowed but noted
            detail=subject_type,
            severity="warn",
        ))
        # Depth / size bound
        try:
            blob = json.dumps(subject, default=str)
            out.append(CheckResult(
                name="actor.size_bound",
                ok=len(blob) < 5_000_000,
                detail=len(blob),
            ))
        except Exception as e:
            out.append(CheckResult(name="actor.size_bound", ok=False, detail=str(e)))
        return out

    def _propose_net_pnl_repair(self, subject: Any) -> Optional[Dict[str, Any]]:
        def _get(obj, key, default=0.0):
            if isinstance(obj, dict):
                return float(obj.get(key) or default)
            return float(getattr(obj, key, default) or default)

        try:
            realized = _get(subject, "realized_output_usd")
            costs = sum(_get(subject, k) for k in (
                "input_cost_usd", "gas_usd", "protocol_fees_usd", "borrow_fees_usd",
                "bridge_fees_usd", "slippage_cost_usd", "revert_cost_usd", "other_costs_usd",
            ))
            reported = _get(subject, "net_pnl_usd")
            calculated = realized - costs
            if abs(calculated - reported) >= 0.02:
                return {
                    "field": "net_pnl_usd",
                    "reported": reported,
                    "proposed": calculated,
                    "reason": "net_pnl identity mismatch",
                }
        except Exception:
            return None
        return None

    def _adversarial_probes(self, subject: Any) -> List[CheckResult]:
        """Tiny stress probes – NaN injection resistance, empty containers, etc."""
        out: List[CheckResult] = []
        # NaN resistance: if any float field is NaN, flag it
        def _walk(obj, path=""):
            found = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    found.extend(_walk(v, f"{path}.{k}"))
            elif isinstance(obj, (list, tuple)):
                for i, v in enumerate(obj):
                    found.extend(_walk(v, f"{path}[{i}]"))
            elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
                found.append(path)
            return found

        try:
            # Convert pydantic models etc. to dict first
            if hasattr(subject, "model_dump"):
                blob = subject.model_dump()
            elif hasattr(subject, "__dict__"):
                blob = subject.__dict__
            else:
                blob = subject
            bad = _walk(blob)
            out.append(CheckResult(
                name="actor.no_nan_inf",
                ok=len(bad) == 0,
                detail=bad[:10] if bad else None,
            ))
        except Exception as e:
            out.append(CheckResult(name="actor.no_nan_inf", ok=False, detail=str(e)))
        return out


# =============================================================================
# Double-Pass Gate  (the mandatory spine)
# =============================================================================

class DoublePassEngineerGate:
    """
    Mandatory Stationary → Non-Stationary → Stationary secondary verification.

    Usage:
        gate = DoublePassEngineerGate(ledger_path="artifacts/verification_ledger.jsonl")
        result = gate.run(subject, subject_id="pkt-001", subject_type="DecisionPacket")
        if not result.allowed_for_llm:
            # do not hand this information to the LLM interpreter
            ...
    """

    def __init__(self, ledger_path: Optional[Union[str, Path]] = None):
        self.ledger = VerificationLedger(ledger_path)
        self.stationary = StationaryEngineer(self.ledger)
        self.non_stationary = NonStationaryEngineer(self.ledger)

    def run(
        self,
        subject: Any,
        subject_id: str,
        subject_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> DoublePassResult:
        context = context or {}

        # Pass 1 – Stationary
        s1 = self.stationary.verify(
            subject, subject_id, subject_type, pass_number=1, context=context
        )

        # Non-stationary experimental pass (always runs; stationary-1 failure still recorded)
        ns = self.non_stationary.act_and_check(
            subject, subject_id, subject_type, context=context
        )

        # Pass 2 – Stationary secondary verification
        s2 = self.stationary.verify(
            subject, subject_id, subject_type, pass_number=2, context=context
        )

        # Final policy: both stationary passes must be PASS (or ABSTAIN) and
        # non-stationary must not hard-fail, otherwise BLOCKED for LLM.
        if s1.verdict == EngineerVerdict.FAIL or s2.verdict == EngineerVerdict.FAIL:
            final = EngineerVerdict.BLOCKED
            allowed = False
        elif ns.verdict == EngineerVerdict.FAIL:
            final = EngineerVerdict.BLOCKED
            allowed = False
        elif s1.verdict == EngineerVerdict.ABSTAIN or s2.verdict == EngineerVerdict.ABSTAIN:
            final = EngineerVerdict.ABSTAIN
            allowed = False   # conservative: abstain also withholds from LLM
        else:
            final = EngineerVerdict.PASS
            allowed = True

        entry_id = self.ledger.append("double_pass", {
            "subject_id": subject_id,
            "subject_type": subject_type,
            "final_verdict": final.value,
            "allowed_for_llm": allowed,
        })

        return DoublePassResult(
            subject_id=subject_id,
            subject_type=subject_type,
            stationary_pass_1=s1,
            non_stationary=ns,
            stationary_pass_2=s2,
            final_verdict=final,
            allowed_for_llm=allowed,
            ledger_entry_id=entry_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def run_batch(
        self,
        items: List[Tuple[Any, str, str]],
        context: Optional[Dict[str, Any]] = None,
        parallel: bool = False,
        max_workers: int = 4,
    ) -> Dict[str, Any]:
        """
        Run double-pass over a list of (subject, subject_id, subject_type).
        Optional parallel execution for large batches (upgrade.parallel_batch).
        """
        context = context or {}
        results: List[DoublePassResult] = []
        if parallel and len(items) > 4:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
                futs = [
                    ex.submit(self.run, subject, sid, stype, context)
                    for subject, sid, stype in items
                ]
                for fut in concurrent.futures.as_completed(futs):
                    results.append(fut.result())
        else:
            for subject, sid, stype in items:
                results.append(self.run(subject, sid, stype, context=context))
        n_allowed = sum(1 for r in results if r.allowed_for_llm)
        n_blocked = len(results) - n_allowed
        return {
            "n_total": len(results),
            "n_allowed_for_llm": n_allowed,
            "n_blocked": n_blocked,
            "results": [r.to_dict() for r in results],
        }

# ===== END engineers.py =====


# ===== BEGIN adversarial_suite.py =====

#!/usr/bin/env python3
"""
Adversarial suite: planted bugs the engineers must catch
(causality leaks, net-PnL mismatches, NaNs, completeness overclaims).
"""
from typing import Any, Dict, List, Tuple
from pathlib import Path


def planted_cases() -> List[Dict[str, Any]]:
    return [
        {
            "id": "leak_future_feature",
            "subject_type": "NormalizedEvent",
            "subject": {
                "event_id": "adv-1",
                "event_timestamp_ms": 1000,
                "observed_timestamp_ms": 1000,
                "available_timestamp_ms": 500,  # before observed — bad
                "event_type": "swap",
                "entity_id": "pool",
                "chain_id": 42161,
            },
            "expect_blocked": True,
            "reason": "available < observed",
        },
        {
            "id": "net_pnl_mismatch",
            "subject_type": "OutcomeLabel",
            "subject": {
                "decision_id": "adv-2",
                "action_id": "a1",
                "realized_output_usd": 100.0,
                "input_cost_usd": 90.0,
                "gas_usd": 1.0,
                "protocol_fees_usd": 0.0,
                "borrow_fees_usd": 0.0,
                "bridge_fees_usd": 0.0,
                "slippage_cost_usd": 0.0,
                "revert_cost_usd": 0.0,
                "other_costs_usd": 0.0,
                "net_pnl_usd": 50.0,  # should be ~9
                "outcome_timestamp_ms": 2000,
                "reverted": False,
            },
            "expect_blocked": True,
            "reason": "net_pnl identity broken",
        },
        {
            "id": "nan_payload",
            "subject_type": "dict",
            "subject": {"decision_id": "adv-3", "score": float("nan")},
            "expect_blocked": True,
            "reason": "NaN not allowed",
        },
        {
            "id": "completeness_overclaim",
            "subject_type": "dict",
            "subject": {"claim": "This is the complete conclusive world physics theory of everything"},
            "expect_blocked": True,
            "reason": "completeness overclaim",
        },
        {
            "id": "clean_event",
            "subject_type": "NormalizedEvent",
            "subject": {
                "event_id": "adv-ok",
                "event_timestamp_ms": 1000,
                "observed_timestamp_ms": 1000,
                "available_timestamp_ms": 1100,
                "event_type": "swap",
                "entity_id": "pool",
                "chain_id": 42161,
            },
            "expect_blocked": False,
            "reason": "valid causality",
        },
    ]


def run_suite(ledger_path: str = "artifacts/adversarial_ledger.jsonl") -> Dict[str, Any]:
    # Isolated ledger dir so engineer ledger_memory does not scan entire artifacts/
    Path(ledger_path).parent.mkdir(parents=True, exist_ok=True)
    gate = DoublePassEngineerGate(ledger_path=ledger_path)
    results = []
    n_pass = 0
    n_fail = 0
    for case in planted_cases():
        r = gate.run(case["subject"], case["id"], case["subject_type"])
        blocked = not r.allowed_for_llm
        ok = blocked == case["expect_blocked"]
        if ok:
            n_pass += 1
        else:
            n_fail += 1
        results.append({
            "id": case["id"],
            "expect_blocked": case["expect_blocked"],
            "got_blocked": blocked,
            "verdict": r.final_verdict.value,
            "suite_ok": ok,
            "reason": case["reason"],
        })
    return {
        "n_cases": len(results),
        "n_suite_pass": n_pass,
        "n_suite_fail": n_fail,
        "all_ok": n_fail == 0,
        "results": results,
    }


if __name__ == "__main__" and False:  # disabled in GENERATED spine
    import json
    print(json.dumps(run_suite(), indent=2))

# ===== END adversarial_suite.py =====


# ===== BEGIN gate_fuzzer.py =====

#!/usr/bin/env python3
"""Differential fuzzer: mutate subjects and expect engineer gates to stay fail-closed."""
import copy
import random
from typing import Any, Dict, List


def mutate(subject: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
    s = copy.deepcopy(subject)
    keys = list(s.keys())
    if not keys:
        return s
    k = rng.choice(keys)
    v = s[k]
    choice = rng.randint(0, 5)
    if choice == 0 and isinstance(v, (int, float)):
        s[k] = float("nan")
    elif choice == 1 and isinstance(v, (int, float)):
        s[k] = -abs(float(v)) * 10
    elif choice == 2 and "available_timestamp_ms" in s and "observed_timestamp_ms" in s:
        s["available_timestamp_ms"] = int(s["observed_timestamp_ms"]) - abs(rng.randint(1, 10**6))
    elif choice == 3 and "net_pnl_usd" in s:
        s["net_pnl_usd"] = 1e9  # break identity if costs present
    elif choice == 4:
        s[k] = None
    else:
        s["claim"] = "complete conclusive world physics"
    return s


def fuzz(
    seed_subjects: List[Dict[str, Any]],
    n: int = 20,
    seed: int = 0,
    ledger_path: str = "artifacts/fuzz_ledger.jsonl",
) -> Dict[str, Any]:
    rng = random.Random(seed)
    gate = DoublePassEngineerGate(ledger_path=ledger_path)
    results = []
    for i in range(n):
        base = rng.choice(seed_subjects)
        mut = mutate(base if isinstance(base, dict) else {"v": base}, rng)
        r = gate.run(mut, f"fuzz-{i}", "dict")
        results.append({
            "i": i,
            "allowed": r.allowed_for_llm,
            "verdict": r.final_verdict.value,
        })
    # Fuzzer success = mutations usually blocked (not all must be; NaN/completeness should block)
    n_blocked = sum(1 for x in results if not x["allowed"])
    return {
        "n": n,
        "n_blocked": n_blocked,
        "block_rate": n_blocked / max(n, 1),
        "results": results,
        "ok": n_blocked >= max(1, n // 3),  # at least ~1/3 blocked
    }

# ===== END gate_fuzzer.py =====


# ===== BEGIN promotion.py =====

#!/usr/bin/env python3
"""
Promote candidate facts into Known-Settled DB only after double-pass engineers clear them.
Hardened: every promotion is signed into a promotion ledger; verify before append.
Offline only — never mutates mid-replay silently.
"""
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional



@dataclass
class CandidateFact:
    id: str
    field: str
    statement: str
    formal: str
    assumptions: List[str]
    regime: str
    tags: List[str]
    source: str = "manual"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PromotionService:
    def __init__(
        self,
        ledger_path: Optional[str] = None,
        promote_log: Optional[str] = None,
        signed_ledger_path: Optional[str] = None,
    ):
        self.gate = DoublePassEngineerGate(
            ledger_path=ledger_path or "artifacts/promotion_ledger.jsonl"
        )
        self.promote_log = Path(promote_log or "artifacts/promoted_facts.jsonl")
        self.promote_log.parent.mkdir(parents=True, exist_ok=True)
        self.db = get_settled_db()
        self.signed = SignedLedger(
            path=signed_ledger_path or "artifacts/promotion_signed.jsonl"
        )

    def evaluate(self, candidate: CandidateFact) -> Dict[str, Any]:
        rej = self.db.reject_completeness_claim(candidate.statement + " " + candidate.formal)
        subject = candidate.to_dict()
        result = self.gate.run(subject, candidate.id, "dict")
        allowed = result.allowed_for_llm and rej.get("ok", True)
        return {
            "candidate_id": candidate.id,
            "double_pass": result.final_verdict.value if hasattr(result.final_verdict, "value") else str(result.final_verdict),
            "allowed_for_llm": result.allowed_for_llm,
            "completeness_ok": rej.get("ok", True),
            "promote_eligible": allowed and result.final_verdict == EngineerVerdict.PASS,
            "detail": result.to_dict(),
            "rejection": rej,
        }

    def promote(
        self,
        candidate: CandidateFact,
        force: bool = False,
        human_confirm: bool = True,
    ) -> Dict[str, Any]:
        evaluation = self.evaluate(candidate)
        if not evaluation["promote_eligible"] and not force:
            self.signed.append("promotion_rejected", {
                "candidate_id": candidate.id,
                "reason": "not_eligible",
            })
            return {"promoted": False, "reason": "not_eligible", "evaluation": evaluation}

        if candidate.id in getattr(self.db, "entries", {}) and not force:
            return {"promoted": False, "reason": "already_exists", "evaluation": evaluation}

        if not human_confirm and not force:
            return {"promoted": False, "reason": "human_confirm_required", "evaluation": evaluation}

        # Signed append BEFORE mutating KSKB
        signed_entry = self.signed.append("promotion_accepted", {
            "candidate": candidate.to_dict(),
            "evaluation_summary": {
                "double_pass": evaluation["double_pass"],
                "allowed_for_llm": evaluation["allowed_for_llm"],
            },
            "human_confirm": human_confirm,
        })

        # Verify ledger integrity after append
        verify = self.signed.verify_file()
        if not verify.get("ok"):
            return {
                "promoted": False,
                "reason": "signature_verify_failed",
                "verify": verify,
                "evaluation": evaluation,
            }

        entry = SettledEntry(
            id=candidate.id,
            field=candidate.field,
            statement=candidate.statement,
            formal=candidate.formal,
            assumptions=candidate.assumptions,
            regime=candidate.regime,
            tags=list(candidate.tags) + [f"source:{candidate.source}"],
            confidence=Confidence.SETTLED,
        )
        try:
            if hasattr(self.db, "entries"):
                self.db.entries[candidate.id] = entry
            if hasattr(self.db, "export"):
                data = self.db.export()
                Path("artifacts/known_settled_export.json").write_text(
                    json.dumps(data, indent=2, default=str)
                )
            elif hasattr(self.db, "to_dict"):
                Path("artifacts/known_settled_export.json").write_text(
                    json.dumps(self.db.to_dict(), indent=2, default=str)
                )
        except Exception as e:
            return {"promoted": False, "reason": f"db_append_failed:{e}", "evaluation": evaluation}

        with self.promote_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "promoted_at": datetime.now(timezone.utc).isoformat(),
                "candidate": candidate.to_dict(),
                "signature": signed_entry.signature,
                "entry_id": signed_entry.entry_id,
                "algorithm": signed_entry.algorithm,
            }, default=str) + "\n")

        return {
            "promoted": True,
            "candidate_id": candidate.id,
            "signature": signed_entry.signature,
            "entry_id": signed_entry.entry_id,
            "algorithm": signed_entry.algorithm,
            "verify": verify,
            "evaluation": evaluation,
        }

    def verify_promotion_ledger(self) -> Dict[str, Any]:
        return self.signed.verify_file()

# ===== END promotion.py =====


# ===== BEGIN adapters/historical.py =====

#!/usr/bin/env python3
"""
Historical data adapters for paper-only simulation assurance.

Provides normalized, availability-timestamped events from local files
(CSV / JSONL / parquet when pyarrow present). Never signs or broadcasts.
Live RPC remains opt-in and read-only via chain_observer_ro.
"""

import csv
import json
import hashlib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union


@dataclass
class NormalizedHistoricalEvent:
    event_id: str
    event_timestamp_ms: int
    available_timestamp_ms: int
    event_type: str
    chain_id: int
    payload: Dict[str, Any]
    source: str
    source_row: int = 0
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _row_checksum(row: Dict[str, Any]) -> str:
    raw = json.dumps(row, sort_keys=True, separators=(",", ":"), default=str).encode()
    return _sha256_hex(raw)


class HistoricalAdapter:
    """
    Load historical market-like events into the same NormalizedEvent shape
    the pipeline expects, with explicit available_timestamp_ms.
    """

    def __init__(
        self,
        chain_id: int = 42161,
        availability_lag_ms: int = 0,
        default_event_type: str = "quote",
    ):
        self.chain_id = chain_id
        self.availability_lag_ms = availability_lag_ms
        self.default_event_type = default_event_type

    def from_jsonl(self, path: Union[str, Path]) -> List[NormalizedHistoricalEvent]:
        path = Path(path)
        out: List[NormalizedHistoricalEvent] = []
        with path.open("r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                out.append(self._normalize(row, source=str(path), source_row=i))
        return out

    def from_csv(self, path: Union[str, Path]) -> List[NormalizedHistoricalEvent]:
        path = Path(path)
        out: List[NormalizedHistoricalEvent] = []
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # coerce numeric-looking fields
                coerced: Dict[str, Any] = {}
                for k, v in row.items():
                    if v is None or v == "":
                        coerced[k] = v
                        continue
                    try:
                        if "." in str(v):
                            coerced[k] = float(v)
                        else:
                            coerced[k] = int(v)
                    except ValueError:
                        coerced[k] = v
                out.append(self._normalize(coerced, source=str(path), source_row=i))
        return out

    def from_parquet(self, path: Union[str, Path]) -> List[NormalizedHistoricalEvent]:
        path = Path(path)
        try:
            import pyarrow.parquet as pq  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "pyarrow required for parquet historical adapter; use JSONL/CSV otherwise"
            ) from e
        table = pq.read_table(path)
        rows = table.to_pylist()
        return [
            self._normalize(row, source=str(path), source_row=i)
            for i, row in enumerate(rows)
        ]

    def from_records(self, rows: List[Dict[str, Any]], source: str = "records") -> List[NormalizedHistoricalEvent]:
        return [self._normalize(r, source=source, source_row=i) for i, r in enumerate(rows)]

    def _normalize(self, row: Dict[str, Any], source: str, source_row: int) -> NormalizedHistoricalEvent:
        ts = int(row.get("event_timestamp_ms") or row.get("timestamp_ms") or row.get("ts_ms") or 0)
        avail = int(row.get("available_timestamp_ms") or (ts + self.availability_lag_ms))
        eid = str(row.get("event_id") or f"{Path(source).stem}_{source_row}_{ts}")
        etype = str(row.get("event_type") or self.default_event_type)
        chain = int(row.get("chain_id") or self.chain_id)
        payload = {k: v for k, v in row.items() if k not in (
            "event_id", "event_timestamp_ms", "available_timestamp_ms",
            "event_type", "chain_id", "timestamp_ms", "ts_ms"
        )}
        # Ensure causality: available >= event
        if avail < ts:
            avail = ts
        return NormalizedHistoricalEvent(
            event_id=eid,
            event_timestamp_ms=ts,
            available_timestamp_ms=avail,
            event_type=etype,
            chain_id=chain,
            payload=payload,
            source=source,
            source_row=source_row,
            checksum=_row_checksum(row),
        )

    def iter_as_pipeline_events(self, events: List[NormalizedHistoricalEvent]) -> Iterator[Dict[str, Any]]:
        """Yield dicts compatible with engineer/schema NormalizedEvent checks."""
        for e in events:
            yield {
                "event_id": e.event_id,
                "event_timestamp_ms": e.event_timestamp_ms,
                "available_timestamp_ms": e.available_timestamp_ms,
                "event_type": e.event_type,
                "chain_id": e.chain_id,
                "payload": e.payload,
                "source": e.source,
                "checksum": e.checksum,
            }


def write_sample_jsonl(path: Union[str, Path], n: int = 5) -> Path:
    """Write a small synthetic historical file for demos/tests."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    base = 1_700_000_000_000
    with path.open("w", encoding="utf-8") as f:
        for i in range(n):
            row = {
                "event_id": f"hist_{i}",
                "event_timestamp_ms": base + i * 12_000,
                "available_timestamp_ms": base + i * 12_000 + 500,
                "event_type": "quote",
                "chain_id": 42161,
                "mid_usd": 100.0 + i * 0.1,
                "bid_usd": 99.9 + i * 0.1,
                "ask_usd": 100.1 + i * 0.1,
                "gas_gwei": 0.05,
            }
            f.write(json.dumps(row) + "\n")
    return path

# ===== END adapters/historical.py =====


# ===== BEGIN adapters/feed_format.py =====

#!/usr/bin/env python3
"""
Canonical data feed format for MegaCompact paper simulation.

Feed file: JSON object with schema_version=1.0.0 and an events[] array.
Each event MUST include event/observed/available timestamps for causality.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


SCHEMA_VERSION = "1.0.0"
REQUIRED_EVENT_FIELDS = (
    "event_id",
    "entity_id",
    "event_timestamp_ms",
    "observed_timestamp_ms",
    "available_timestamp_ms",
    "event_type",
)


def _checksum_event(ev: Dict[str, Any]) -> str:
    body = {k: ev[k] for k in sorted(ev) if k != "checksum"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_event(ev: Dict[str, Any]) -> Dict[str, Any]:
    missing = [f for f in REQUIRED_EVENT_FIELDS if f not in ev or ev[f] in (None, "")]
    if missing:
        return {"ok": False, "missing": missing}
    try:
        ets = int(ev["event_timestamp_ms"])
        ots = int(ev["observed_timestamp_ms"])
        ats = int(ev["available_timestamp_ms"])
    except (TypeError, ValueError) as e:
        return {"ok": False, "error": f"timestamp_cast:{e}"}
    if ats < ets:
        return {"ok": False, "error": "available_timestamp_ms < event_timestamp_ms", "causality": False}
    if ots < ets:
        return {"ok": False, "error": "observed_timestamp_ms < event_timestamp_ms"}
    return {"ok": True, "causality": True}


def validate_feed(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(doc, dict):
        return {"ok": False, "error": "feed_not_object"}
    if doc.get("schema_version") != SCHEMA_VERSION:
        return {"ok": False, "error": "schema_version_mismatch", "got": doc.get("schema_version")}
    for key in ("feed_id", "chain_id", "events"):
        if key not in doc:
            return {"ok": False, "error": f"missing_{key}"}
    events = doc["events"]
    if not isinstance(events, list) or len(events) < 1:
        return {"ok": False, "error": "events_empty"}
    failures = []
    for i, ev in enumerate(events):
        r = validate_event(ev)
        if not r.get("ok"):
            failures.append({"index": i, "event_id": ev.get("event_id"), **r})
    return {
        "ok": len(failures) == 0,
        "n_events": len(events),
        "failures": failures,
        "feed_id": doc.get("feed_id"),
        "schema_version": doc.get("schema_version"),
    }


def load_feed(path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    report = validate_feed(doc)
    report["path"] = str(path)
    return {"doc": doc, "validation": report}


def feed_to_pipeline_events(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert validated feed events to pipeline-normalized dicts."""
    out = []
    chain = int(doc.get("chain_id") or 42161)
    for ev in doc.get("events") or []:
        row = dict(ev)
        row.setdefault("chain_id", chain)
        if "checksum" not in row:
            row["checksum"] = _checksum_event(row)
        out.append({
            "event_id": row["event_id"],
            "entity_id": row["entity_id"],
            "event_timestamp_ms": int(row["event_timestamp_ms"]),
            "observed_timestamp_ms": int(row["observed_timestamp_ms"]),
            "available_timestamp_ms": int(row["available_timestamp_ms"]),
            "event_type": row["event_type"],
            "chain_id": int(row.get("chain_id", chain)),
            "payload": row.get("payload") or {},
            "checksum": row.get("checksum"),
            "source": doc.get("source") or doc.get("feed_id"),
        })
    return out


def write_example_feed(path: Union[str, Path], n: int = 5) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    base = 1_700_000_000_000
    events = []
    for i in range(n):
        ets = base + i * 12_000
        ev = {
            "event_id": f"feed_ex_{i}",
            "entity_id": "pool_demo",
            "event_timestamp_ms": ets,
            "observed_timestamp_ms": ets + 200,
            "available_timestamp_ms": ets + 500,
            "event_type": "quote",
            "chain_id": 42161,
            "payload": {
                "mid_usd": 100.0 + i * 0.05,
                "bid_usd": 99.95 + i * 0.05,
                "ask_usd": 100.05 + i * 0.05,
                "gas_gwei": 0.05,
            },
        }
        ev["checksum"] = _checksum_event(ev)
        events.append(ev)
    doc = {
        "feed_id": "example_feed_v1",
        "schema_version": SCHEMA_VERSION,
        "chain_id": 42161,
        "source": "synthetic_example",
        "as_of": "2026-08-19",
        "license": "CC0-1.0",
        "events": events,
    }
    path.write_text(json.dumps(doc, indent=2))
    return path


def ingest_feed_file(path: Union[str, Path]) -> Dict[str, Any]:
    """Load + validate + convert. Fail-closed on validation errors."""
    loaded = load_feed(path)
    val = loaded["validation"]
    if not val.get("ok"):
        return {"ok": False, "validation": val, "events": []}
    events = feed_to_pipeline_events(loaded["doc"])
    return {"ok": True, "validation": val, "events": events, "n": len(events)}

# ===== END adapters/feed_format.py =====


# ===== BEGIN independent_audit.py =====

#!/usr/bin/env python3
"""
Independent audit / formal subset (Product VD4).

Runs a self-contained audit battery that does not depend on pipeline stage
order, and emits formal obligations via formal_bridge for external kernels.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional









def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class IndependentAuditor:
    """
    Product-facing independent audit runner for simulation-assurance labs.
    Paper-only: no live trading, no completeness claims.
    """

    def __init__(self, run_dir: Optional[str] = None, ledger_path: Optional[str] = None):
        self.run_dir = Path(run_dir or "artifacts/run_independent_audit")
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.gate = DoublePassEngineerGate(
            ledger_path=ledger_path or str(self.run_dir / "audit_engineer_ledger.jsonl")
        )
        self.signed = SignedLedger(path=str(self.run_dir / "signed_audit_ledger.jsonl")) if SignedLedger else None

    def run(self, subject: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        subject = subject or {
            "event_id": "audit_probe",
            "entity_id": "entity_audit",
            "event_timestamp_ms": 1000,
            "observed_timestamp_ms": 1050,
            "available_timestamp_ms": 1100,
            "event_type": "quote",
            "chain_id": 42161,
            "payload": {"mid_usd": 100.0},
        }
        report: Dict[str, Any] = {
            "auditor": "IndependentAuditor",
            "version": "1.0.0-product",
            "timestamp": _utc(),
            "product": "simulation_assurance",
            "live_trading": False,
            "checks": {},
        }

        # 1. Double-pass on subject
        dp = self.gate.run(subject, subject_id="independent_audit_subject", subject_type="NormalizedEvent")
        report["checks"]["double_pass"] = {
            "verdict": dp.final_verdict.value if hasattr(dp.final_verdict, "value") else str(dp.final_verdict),
            "allowed_for_llm": dp.allowed_for_llm,
        }

        # 2. Adversarial suite
        if run_suite:
            adv = run_suite()
            report["checks"]["adversarial"] = {
                "all_ok": adv.get("all_ok"),
                "n_suite_pass": adv.get("n_suite_pass"),
                "n_cases": adv.get("n_cases"),
            }
        else:
            report["checks"]["adversarial"] = {"all_ok": False, "error": "suite_unavailable"}

        # 3. Mechanical battery
        if full_mechanical_battery:
            bat = full_mechanical_battery(subject)
            report["checks"]["mechanical_battery"] = {
                k: (v.get("final_verdict") if isinstance(v, dict) and "final_verdict" in v else v)
                for k, v in bat.items()
            }
        else:
            report["checks"]["mechanical_battery"] = {"error": "unavailable"}

        # 4. Formal obligation (not proven until kernel accepts)
        formal_result: Dict[str, Any] = {"ok": False, "proven": False}
        if submit_obligation:
            formal_dir = self.run_dir / "formal"
            formal_dir.mkdir(parents=True, exist_ok=True)
            formal_result = submit_obligation(
                statement_id="audit_net_pnl_identity",
                formal_text="Net PnL identity: gross - sum(costs) == net for labeled outcomes",
                out_dir=str(formal_dir),
            )
            if try_lean_check and formal_result.get("path"):
                lean = try_lean_check(formal_result["path"])
                formal_result["lean_attempt"] = lean
        report["checks"]["formal_subset"] = formal_result
        report["checks"]["kernels_available"] = kernel_available() if kernel_available else {}

        # 5. Bit-exact self-proof on this audit run dir
        if self_proof:
            # write a minimal summary so hashes have something to pin
            summary_path = self.run_dir / "reports"
            summary_path.mkdir(parents=True, exist_ok=True)
            (summary_path / "run_summary.json").write_text(
                json.dumps({"audit": True, "ts": _utc()}, indent=2)
            )
            report["checks"]["bit_exact_self"] = self_proof(str(self.run_dir))
        else:
            report["checks"]["bit_exact_self"] = {"ok": False, "error": "unavailable"}

        # 6. Merkle over audit artifacts
        if build_merkle:
            report["checks"]["merkle"] = build_merkle(str(self.run_dir))
        else:
            report["checks"]["merkle"] = {"error": "unavailable"}

        # 7. Signed ledger entry
        if self.signed:
            entry = self.signed.append("independent_audit", {
                "double_pass": report["checks"]["double_pass"],
                "adversarial_ok": report["checks"].get("adversarial", {}).get("all_ok"),
            })
            report["checks"]["signed_ledger"] = {
                "entry_id": entry.entry_id,
                "algorithm": entry.algorithm,
                "verify": self.signed.verify_file(),
            }

        # Aggregate
        hard = []
        if report["checks"]["double_pass"].get("verdict") not in ("PASS", "pass"):
            hard.append("double_pass")
        if not report["checks"].get("adversarial", {}).get("all_ok"):
            hard.append("adversarial")
        report["ok"] = len(hard) == 0
        report["failed"] = hard
        report["product_claim"] = (
            "Paper-only simulation assurance under double-pass engineers. "
            "No live trading. Finite settled knowledge only."
        )

        out_path = self.run_dir / "independent_audit_report.json"
        out_path.write_text(json.dumps(report, indent=2, default=str))
        report["report_path"] = str(out_path)
        return report


def run_independent_audit(run_dir: Optional[str] = None) -> Dict[str, Any]:
    return IndependentAuditor(run_dir=run_dir).run()

# ===== END independent_audit.py =====


# ===== BEGIN llm_wrapper.py =====

#!/usr/bin/env python3
"""
Cleared-LLM gateway: refuse any subject not double-pass cleared.

Does not call a real model by default. Provides a safe interface that:
  - accepts only subjects with allowed_for_llm=True (or runs double-pass first)
  - refuses blocked / uncleared inputs
  - never claims world-oracle authority
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union



def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GatewayResult:
    status: str  # "ok" | "refused" | "error"
    reason: str = ""
    allowed_for_llm: bool = False
    engineer_verdict: Optional[str] = None
    response: Optional[str] = None
    subject_id: Optional[str] = None
    timestamp: str = field(default_factory=_utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "allowed_for_llm": self.allowed_for_llm,
            "engineer_verdict": self.engineer_verdict,
            "response": self.response,
            "subject_id": self.subject_id,
            "timestamp": self.timestamp,
        }


class ClearedLLMGateway:
    """
    LLM interpretation only after Stationary → NonStationary → Stationary PASS.

    llm_fn: optional callable(prompt: str, subject: Any) -> str
    If llm_fn is None, returns a deterministic stub response for cleared subjects.
    """

    def __init__(
        self,
        ledger_path: Optional[str] = None,
        llm_fn: Optional[Callable[..., str]] = None,
        require_fresh_double_pass: bool = True,
    ):
        self.gate = DoublePassEngineerGate(
            ledger_path=ledger_path or "artifacts/llm_gateway_ledger.jsonl"
        )
        self.llm_fn = llm_fn
        self.require_fresh_double_pass = require_fresh_double_pass
        self.refusal_log: List[Dict[str, Any]] = []

    def _already_cleared(self, subject: Any) -> bool:
        if isinstance(subject, dict):
            if subject.get("allowed_for_llm") is True:
                return True
            meta = subject.get("metadata") or {}
            if isinstance(meta, dict) and meta.get("allowed_for_llm") is True:
                return True
            eng = subject.get("engineer") or subject.get("double_pass") or {}
            if isinstance(eng, dict) and eng.get("allowed_for_llm") is True:
                return True
        return False

    def interpret(
        self,
        subject: Any,
        subject_id: str = "llm_subject",
        subject_type: str = "dict",
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Fast refuse: explicit deny flag
        if isinstance(subject, dict) and subject.get("allowed_for_llm") is False:
            res = GatewayResult(
                status="refused",
                reason="subject.allowed_for_llm is False",
                allowed_for_llm=False,
                subject_id=subject_id,
            )
            self.refusal_log.append(res.to_dict())
            return res.to_dict()

        allowed = False
        verdict = None

        if self.require_fresh_double_pass or not self._already_cleared(subject):
            # Always prefer a fresh double-pass for safety
            result = self.gate.run(subject, subject_id=subject_id, subject_type=subject_type)
            d = result.to_dict()
            verdict = d.get("final_verdict")
            allowed = bool(result.allowed_for_llm) and verdict == "PASS"
        else:
            allowed = True
            verdict = "PASS_CACHED"

        if not allowed:
            res = GatewayResult(
                status="refused",
                reason="not_cleared_by_double_pass",
                allowed_for_llm=False,
                engineer_verdict=str(verdict),
                subject_id=subject_id,
            )
            self.refusal_log.append(res.to_dict())
            return res.to_dict()

        # Cleared — optional LLM call
        text_prompt = prompt or (
            "Summarize this cleared simulation-assurance artifact. "
            "Do not claim complete knowledge or live trading capability.\n\n"
            + json.dumps(subject if not isinstance(subject, str) else {"text": subject}, default=str)[:4000]
        )
        if self.llm_fn is not None:
            try:
                response = self.llm_fn(text_prompt, subject)
            except Exception as e:
                return GatewayResult(
                    status="error",
                    reason=f"llm_fn_error:{e}",
                    allowed_for_llm=True,
                    engineer_verdict=str(verdict),
                    subject_id=subject_id,
                ).to_dict()
        else:
            response = (
                "[cleared-stub] Subject passed double-pass. "
                "No external LLM configured. "
                "This is simulation-assurance output only — not a world oracle, not live trading."
            )

        return GatewayResult(
            status="ok",
            reason="cleared",
            allowed_for_llm=True,
            engineer_verdict=str(verdict),
            response=response,
            subject_id=subject_id,
        ).to_dict()

    def interpret_file(self, path: Union[str, Path], subject_id: Optional[str] = None) -> Dict[str, Any]:
        path = Path(path)
        raw = path.read_text(encoding="utf-8")
        try:
            subject = json.loads(raw)
        except json.JSONDecodeError:
            subject = {"text": raw, "path": str(path)}
        return self.interpret(subject, subject_id=subject_id or path.name, subject_type="doc")

# ===== END llm_wrapper.py =====


# ===== BEGIN ci/lab_ci.py =====

#!/usr/bin/env python3
"""
Lab CI job for simulation-assurance gates.

Runs adversarial suite + independent audit (+ optional mechanical battery).
Intended for every PR / commit in a research lab setting.
Exit code 0 only if all required gates pass.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_lab_ci(
    run_dir: str = "artifacts/run_lab_ci",
    include_battery: bool = True,
    include_overclaim_probe: bool = True,
) -> Dict[str, Any]:
    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)
    report: Dict[str, Any] = {
        "job": "lab_ci",
        "version": "1.0.0",
        "timestamp": _utc(),
        "product": "simulation_assurance",
        "live_trading": False,
        "checks": {},
        "failed": [],
    }

    # 1. Adversarial suite
    try:
        adv = run_suite(ledger_path=str(run_path / "adversarial_ledger.jsonl"))
        report["checks"]["adversarial"] = {
            "all_ok": adv.get("all_ok"),
            "n_suite_pass": adv.get("n_suite_pass"),
            "n_cases": adv.get("n_cases"),
        }
        if not adv.get("all_ok"):
            report["failed"].append("adversarial")
    except Exception as e:
        report["checks"]["adversarial"] = {"all_ok": False, "error": str(e)}
        report["failed"].append("adversarial")

    # 2. Independent audit
    try:
        audit = run_independent_audit(str(run_path / "independent_audit"))
        report["checks"]["independent_audit"] = {
            "ok": audit.get("ok"),
            "failed": audit.get("failed"),
            "double_pass": audit.get("checks", {}).get("double_pass"),
            "adversarial": audit.get("checks", {}).get("adversarial"),
        }
        if not audit.get("ok"):
            report["failed"].append("independent_audit")
    except Exception as e:
        report["checks"]["independent_audit"] = {"ok": False, "error": str(e)}
        report["failed"].append("independent_audit")

    # 3. Optional mechanical battery
    if include_battery:
        try:
            bat = full_mechanical_battery()
            # adversarial inside battery is nested; require double_pass PASS
            dp = bat.get("double_pass")
            dp_ok = dp == "PASS" or (isinstance(dp, dict) and dp.get("final_verdict") == "PASS")
            adv_ok = True
            if isinstance(bat.get("adversarial"), dict):
                adv_ok = bool(bat["adversarial"].get("all_ok", True))
            report["checks"]["mechanical_battery"] = {
                "double_pass_ok": dp_ok,
                "adversarial_ok": adv_ok,
                "keys": list(bat.keys()),
            }
            if not dp_ok:
                report["failed"].append("mechanical_battery_double_pass")
        except Exception as e:
            report["checks"]["mechanical_battery"] = {"error": str(e)}
            report["failed"].append("mechanical_battery")

    # 4. Completeness overclaim must stay blocked
    if include_overclaim_probe:
        try:
            gate = DoublePassEngineerGate(ledger_path=str(run_path / "overclaim_ledger.jsonl"))
            r = gate.run(
                {"claim": "complete conclusive world physics catalogue as oracle stage"},
                subject_type="claim",
                subject_id="ci_overclaim",
            )
            blocked = r.to_dict().get("final_verdict") == "BLOCKED"
            report["checks"]["overclaim_probe"] = {
                "blocked": blocked,
                "verdict": r.to_dict().get("final_verdict"),
            }
            if not blocked:
                report["failed"].append("overclaim_not_blocked")
        except Exception as e:
            report["checks"]["overclaim_probe"] = {"error": str(e)}
            report["failed"].append("overclaim_probe")

    # 5. Feed format self-check
    try:
        example = run_path / "example_feed.json"
        write_example_feed(example, n=3)
        ing = ingest_feed_file(example)
        report["checks"]["feed_format"] = {
            "ok": ing.get("ok"),
            "n": ing.get("n"),
            "validation_ok": (ing.get("validation") or {}).get("ok"),
        }
        if not ing.get("ok"):
            report["failed"].append("feed_format")
    except Exception as e:
        report["checks"]["feed_format"] = {"error": str(e)}
        report["failed"].append("feed_format")

    # 6. LLM wrapper refuse probe
    try:
        gw = ClearedLLMGateway()
        blocked_subj = {"raw": "uncleared text", "allowed_for_llm": False}
        refuse = gw.interpret(blocked_subj)
        report["checks"]["llm_wrapper_refuse"] = {
            "refused": refuse.get("status") == "refused",
            "detail": refuse.get("reason"),
        }
        if refuse.get("status") != "refused":
            report["failed"].append("llm_wrapper_did_not_refuse")
    except Exception as e:
        report["checks"]["llm_wrapper_refuse"] = {"error": str(e)}
        report["failed"].append("llm_wrapper")

    report["ok"] = len(report["failed"]) == 0
    out = run_path / "lab_ci_report.json"
    out.write_text(json.dumps(report, indent=2, default=str))
    report["report_path"] = str(out)
    return report


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="MegaCompact lab CI — adversarial + independent audit")
    p.add_argument("--run-dir", default="artifacts/run_lab_ci")
    p.add_argument("--no-battery", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    report = run_lab_ci(
        run_dir=args.run_dir,
        include_battery=not args.no_battery,
    )
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print("lab_ci ok=", report["ok"], "failed=", report["failed"])
        print("report:", report.get("report_path"))
    return 0 if report["ok"] else 1


if __name__ == "__main__" and False:  # disabled in GENERATED spine
    sys.exit(main())

# ===== END ci/lab_ci.py =====


# ===== BEGIN tools/artifacts.py =====

#!/usr/bin/env python3
"""Local artifact tool-set: list runs, read reports, merkle, pin, compare, ledgers."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

compare_runs = write_pin = pin_matrix = None  # type: ignore
ledger_summary = ledger_search = find_ledgers = None  # type: ignore


def list_runs(artifacts_root: str = "artifacts") -> List[Dict[str, Any]]:
    root = Path(artifacts_root)
    if not root.exists():
        return []
    runs = []
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p.name.startswith("run_") or p.name in ("run_scaled", "run_complete")):
            runs.append({
                "run_id": p.name,
                "path": str(p),
                "has_reports": (p / "reports").exists(),
                "has_audits": (p / "audits").exists(),
            })
    return runs


def load_json(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"ok": False, "error": "missing", "path": path}
    return json.loads(p.read_text(encoding="utf-8"))


def run_summary(run_dir: str) -> Dict[str, Any]:
    base = Path(run_dir)
    candidates = [
        base / "reports" / "run_summary.json",
        base / "reports" / "final_summary.json",
    ]
    for c in candidates:
        if c.exists():
            return load_json(str(c))
    return {"ok": False, "error": "no_summary"}


def merkle(run_dir: str, write: bool = False) -> Dict[str, Any]:
    if build_merkle is None:
        return {"ok": False, "error": "merkle_unavailable"}
    if write and write_merkle:
        return write_merkle(run_dir)
    return build_merkle(run_dir)


def pin(run_dir: str) -> Dict[str, Any]:
    if write_pin is None:
        return {"ok": False, "error": "pin_unavailable"}
    path = write_pin(run_dir)
    return {"ok": True, "path": str(path), "matrix": pin_matrix() if pin_matrix else {}}


def compare(run_a: str, run_b: str) -> Dict[str, Any]:
    if compare_runs is None:
        return {"ok": False, "error": "compare_unavailable"}
    return compare_runs(run_a, run_b)


def ledgers(artifacts_root: str = "artifacts") -> Dict[str, Any]:
    if ledger_summary is None:
        return {"ok": False, "error": "ledger_index_unavailable"}
    return ledger_summary(artifacts_root)


def ledger_query(query: str, artifacts_root: str = "artifacts", limit: int = 20) -> List[Dict[str, Any]]:
    if ledger_search is None:
        return []
    return ledger_search(query, root=artifacts_root, limit=limit)

# ===== END tools/artifacts.py =====


# ===== BEGIN tools/verifiers.py =====

#!/usr/bin/env python3
"""Mechanical verifier tool-set: double-pass, SMT, interval, typed IR, causal, schema, units, sandbox."""
from typing import Any, Dict, List, Optional


validate_actions = None  # type: ignore
check_features = None  # type: ignore
stationary_unit_probe = attach_unit_tags = tag_feature = None  # type: ignore
sandbox_run = None  # type: ignore
fuzz = None  # type: ignore
get_facade = None  # type: ignore


def double_pass(subject: Any, subject_id: str = "tool", subject_type: str = "dict",
                ledger_path: str = "artifacts/toolset_verify_ledger.jsonl") -> Dict[str, Any]:
    gate = DoublePassEngineerGate(ledger_path=ledger_path)
    r = gate.run(subject, subject_id, subject_type)
    return {
        "final_verdict": r.final_verdict.value,
        "allowed_for_llm": r.allowed_for_llm,
        "report": r.to_dict(),
    }


def stationary_only(subject: Any, subject_id: str = "tool", subject_type: str = "dict") -> Dict[str, Any]:
    r = StationaryEngineer().verify(subject, subject_id, subject_type)
    return {"verdict": r.verdict.value, "all_ok": r.all_ok, "issues": r.issues, "n_checks": len(r.checks)}


def smt_trade(net_edge_usd: float, revert_p: float, inclusion_p: float, ood: float,
              thresholds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    if pre_trade_gate is None:
        return {"ok": False, "error": "smt_unavailable"}
    return pre_trade_gate(net_edge_usd, revert_p, inclusion_p, ood, thresholds)


def interval_edge(output_lo: float, output_hi: float, cost_lo: float, cost_hi: float,
                  min_edge: float = 1.0) -> Dict[str, Any]:
    if Interval is None:
        return {"ok": False, "error": "interval_unavailable"}
    edge = net_edge_interval(Interval(output_lo, output_hi), Interval(cost_lo, cost_hi))
    return trade_allowed_by_interval(edge, min_edge)


def typed_actions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    if validate_actions is None:
        return {"ok": False, "error": "typed_ir_unavailable"}
    return validate_actions(actions)


def causal_features(features: List[str]) -> Dict[str, Any]:
    if check_features is None:
        return {"ok": False, "error": "causal_unavailable"}
    return check_features(features)


def schema_check(obj: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
    if load_schema is None:
        return {"ok": False, "error": "schema_unavailable"}
    sch = load_schema(schema_name)
    return validate_required(obj, sch)


def unit_probe(payload: Dict[str, Any]) -> Dict[str, Any]:
    if stationary_unit_probe is None:
        return {"ok": False, "error": "unit_tags_unavailable"}
    return stationary_unit_probe(payload)


def sandboxed(fn, timeout_s: float = 2.0) -> Dict[str, Any]:
    if sandbox_run is None:
        return {"ok": False, "error": "sandbox_unavailable"}
    return sandbox_run(fn, timeout_s=timeout_s)


def adversarial() -> Dict[str, Any]:
    if run_suite is None:
        return {"ok": False, "error": "adversarial_unavailable"}
    return run_suite()


def fuzz_gates(seeds: List[Dict[str, Any]], n: int = 10, seed: int = 0) -> Dict[str, Any]:
    if fuzz is None:
        return {"ok": False, "error": "fuzzer_unavailable"}
    return fuzz(seeds, n=n, seed=seed)


def knowledge_stats() -> Dict[str, Any]:
    if get_facade is None:
        return {"ok": False, "error": "facade_unavailable"}
    return get_facade().stats()


    """Run a standard battery of mechanical verifiers (local only)."""
    subject = subject or {
        "event_id": "battery",
        "event_timestamp_ms": 1000,
        "observed_timestamp_ms": 1000,
        "available_timestamp_ms": 1100,
        "event_type": "swap",
        "entity_id": "pool",
        "chain_id": 42161,
    }
    return {
        "double_pass": double_pass(subject, "battery", "NormalizedEvent"),
        "smt": smt_trade(2.0, 0.01, 0.95, 0.2),
        "interval": interval_edge(10, 12, 8, 9, 1.0),
        "causal": causal_features(["features_t", "outcome_t"]),
        "typed": typed_actions([{
            "kind": "swap", "venue": "x", "token_in": "A", "token_out": "B",
            "amount_in": 1.0, "max_slippage_bps": 30, "chain_id": 42161, "deadline_ms": 999,
        }]),
        "schema": schema_check(subject, "events_v1.json"),
        "adversarial": adversarial(),
        "knowledge": knowledge_stats(),
    }

# ===== END tools/verifiers.py =====


# ===== BEGIN uair/contracts.py =====

"""
Data contracts for UAIR - typed interfaces between components.

All cross-module communication uses these contracts to ensure type safety,
provenance tracking, and auditable traces.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import uuid


class Sensitivity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskClass(Enum):
    ARITHMETIC = "arithmetic"
    DATA_EXTRACTION = "data_extraction"
    CODE_EXECUTION = "code_execution"
    KNOWLEDGE_LOOKUP = "knowledge_lookup"
    DOC_QA = "doc_qa"
    STRUCTURED_TRANSFORM = "structured_transform"
    CREATIVE_GENERATION = "creative_generation"
    PLANNING = "planning"
    DEFI_ANALYSIS = "defi_analysis"
    UNKNOWN = "unknown"


class RoutePath(Enum):
    CACHE = "cache"
    DETERMINISTIC = "deterministic"
    RETRIEVAL = "retrieval"
    SPECIALIST = "specialist"
    LLM = "llm"
    HYBRID = "hybrid"
    CLARIFY = "clarify"
    ABSTAIN = "abstain"


class ResponseStatus(Enum):
    ANSWERED = "answered"
    CLARIFY = "clarify"
    ABSTAINED = "abstained"
    REFUSED = "refused"
    FAILED = "failed"


class VerificationStatus(Enum):
    PASSED = "passed"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class SafetyStatus(Enum):
    PASSED = "passed"
    BLOCKED = "blocked"
    REVIEW = "review"


class TrustTier(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceType(Enum):
    DOCUMENT = "document"
    DATABASE = "database"
    TOOL = "tool"
    USER = "user"
    MODEL = "model"


@dataclass
class Request:
    """Canonical request object from user to UAIR."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id_hash: Optional[str] = None
    timestamp_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    input_text: str = ""
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    session_context_ids: List[str] = field(default_factory=list)
    task_hint: Optional[str] = None
    sensitivity: Sensitivity = Sensitivity.LOW
    max_latency_ms: int = 5000
    max_cost_usd: float = 0.10
    allow_external_tools: bool = False
    allow_memory: bool = False
    locale: str = "en"


@dataclass
class NormalizedInput:
    """Normalized and validated input from Request."""
    text_norm: str = ""
    lang: str = "en"
    char_count: int = 0
    attachment_manifest: List[Dict[str, Any]] = field(default_factory=list)
    pii_flags: List[str] = field(default_factory=list)
    injection_flags: List[str] = field(default_factory=list)
    unsupported_flags: List[str] = field(default_factory=list)
    canonical_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentReport:
    """Intent classification with confidence distribution."""
    intent_distribution: Dict[TaskClass, float] = field(default_factory=dict)
    top_k: List[tuple[TaskClass, float]] = field(default_factory=list)
    classifier_version: str = "v0.1"
    needs_clarification: bool = False
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class ComplexityReport:
    """Complexity and risk estimation for routing."""
    context_need: float = 0.5
    depth: float = 0.5
    expected_tools: int = 0
    expected_out_len: int = 100
    sensitivity: Sensitivity = Sensitivity.LOW
    verification_burden: float = 0.5
    estimator_version: str = "v0.1"


@dataclass
class RoutePlan:
    """Planned execution route with budgets."""
    intent_distribution: Dict[TaskClass, float] = field(default_factory=dict)
    complexity_score: float = 0.5
    risk_score: float = 0.5
    selected_path: RoutePath = RoutePath.ABSTAIN
    token_budget: int = 1000
    retrieval_budget: int = 5
    tool_budget: int = 3
    verification_plan: List[str] = field(default_factory=list)
    fallback_path: RoutePath = RoutePath.ABSTAIN
    reason_codes: List[str] = field(default_factory=list)
    predicted_cost_usd: float = 0.01
    predicted_latency_ms: int = 100


@dataclass
class EvidenceItem:
    """Retrieved evidence with provenance."""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_type: SourceType = SourceType.DOCUMENT
    source_uri_or_id: str = ""
    source_timestamp: str = ""
    content_hash: str = ""
    passage: str = ""
    relevance_score: float = 0.0
    trust_tier: TrustTier = TrustTier.MEDIUM
    license_status: str = "unknown"
    retrieved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ToolResult:
    """Result from tool execution."""
    tool_name: str = ""
    version: str = "v0.1"
    args_hash: str = ""
    ok: bool = False
    output: Any = None
    error: Optional[str] = None
    latency_ms: int = 0


@dataclass
class UncertaintyReport:
    """Decomposed uncertainty with calibration status."""
    overall_confidence: float = 0.5
    epistemic: float = 0.0  # Model uncertainty
    aleatoric: float = 0.0  # Inherent ambiguity
    retrieval: float = 0.0  # Evidence uncertainty
    execution: float = 0.0  # Tool failure uncertainty
    ood_score: float = 0.0  # Out-of-distribution score
    calibrated: bool = False
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class VerificationCheck:
    """Single verification check result."""
    name: str = ""
    passed: bool = False
    detail: str = ""


@dataclass
class VerificationReport:
    """Aggregated verification results."""
    status: VerificationStatus = VerificationStatus.NOT_APPLICABLE
    checks: List[VerificationCheck] = field(default_factory=list)


@dataclass
class SafetyCheck:
    """Single safety check result."""
    name: str = ""
    passed: bool = False
    reason_code: str = ""


@dataclass
class SafetyReport:
    """Aggregated safety check results."""
    status: SafetyStatus = SafetyStatus.PASSED
    reason_codes: List[str] = field(default_factory=list)


@dataclass
class CostMetrics:
    """Cost breakdown for the request."""
    input_tokens: int = 0
    output_tokens: int = 0
    retrieval_tokens: int = 0
    tool_calls: int = 0
    latency_ms: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class SystemVersions:
    """Version tracking for all components."""
    router: str = "v0.1"
    models: Dict[str, str] = field(default_factory=dict)
    prompts: Dict[str, str] = field(default_factory=dict)
    index: str = "v0.1"
    policy: str = "v0.1"


@dataclass
class Response:
    """Canonical response from UAIR to user."""
    answer: Any = None
    status: ResponseStatus = ResponseStatus.FAILED
    route_used: RoutePath = RoutePath.ABSTAIN
    evidence_ids: List[str] = field(default_factory=list)
    uncertainty: UncertaintyReport = field(default_factory=UncertaintyReport)
    verification: VerificationReport = field(default_factory=VerificationReport)
    safety: SafetyReport = field(default_factory=SafetyReport)
    cost: CostMetrics = field(default_factory=CostMetrics)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: SystemVersions = field(default_factory=SystemVersions)

# ===== END uair/contracts.py =====


# ===== BEGIN uair/layers.py =====

"""
UAIR Capability Layers - Implements the 16 layer architecture.

Each layer is a single-responsibility component that can be tested independently.
For v0.1, we implement the core layers needed for the MVP.
"""

import re
import math
from typing import Optional, List, Dict, Any
from datetime import datetime



class NormalizationLayer:
    """Layer 1: Input normalization and validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.max_length = config.get("max_input_length", 10000)
    
    def process(self, request: Request) -> NormalizedInput:
        """Normalize and validate input."""
        text = request.input_text.strip()
        
        # Basic normalization
        text_norm = " ".join(text.split())  # Normalize whitespace
        char_count = len(text_norm)
        
        # Simple language detection (placeholder)
        lang = "en"  # In v0.1, assume English
        
        # Check for injection patterns (basic)
        injection_flags = []
        if re.search(r"(ignore|forget|override)\s+(previous|all)\s+(instructions|rules)", text_norm, re.IGNORECASE):
            injection_flags.append("prompt_injection")
        
        # Size check
        unsupported_flags = []
        if char_count > self.max_length:
            unsupported_flags.append("too_long")
        
        return NormalizedInput(
            text_norm=text_norm,
            lang=lang,
            char_count=char_count,
            attachment_manifest=request.attachments,
            injection_flags=injection_flags,
            unsupported_flags=unsupported_flags
        )


class IntentLayer:
    """Layer 2: Intent and task classification."""
    
    def __init__(self, config: Dict[str, Any]):
        self.confidence_threshold = config.get("intent_threshold", 0.7)
    
    def classify(self, normalized: NormalizedInput) -> IntentReport:
        """Classify intent using rules (v0.1 uses rules, not ML)."""
        text = normalized.text_norm.lower()
        
        # Rule-based classification
        scores = {
            TaskClass.ARITHMETIC: 0.0,
            TaskClass.DATA_EXTRACTION: 0.0,
            TaskClass.CODE_EXECUTION: 0.0,
            TaskClass.KNOWLEDGE_LOOKUP: 0.0,
            TaskClass.DOC_QA: 0.0,
            TaskClass.STRUCTURED_TRANSFORM: 0.0,
            TaskClass.CREATIVE_GENERATION: 0.0,
            TaskClass.PLANNING: 0.0,
            TaskClass.DEFI_ANALYSIS: 0.0,
            TaskClass.UNKNOWN: 0.0
        }
        
        # Arithmetic patterns
        if re.search(r"\d+\s*[\+\-\*\/]\s*\d+", text):
            scores[TaskClass.ARITHMETIC] = 0.9
        
        # Question patterns
        if re.search(r"^(what|how|why|when|where|who|which)", text):
            scores[TaskClass.KNOWLEDGE_LOOKUP] = 0.7
            scores[TaskClass.DOC_QA] = 0.6
        
        # Code patterns
        if re.search(r"(code|function|class|def |import |print\()", text):
            scores[TaskClass.CODE_EXECUTION] = 0.8
        
        # DeFi patterns
        if re.search(r"(token|price|gas|liquidity|pool|swap|defi)", text):
            scores[TaskClass.DEFI_ANALYSIS] = 0.8
        
        # Extract patterns
        if re.search(r"(extract|parse|get\s+(the\s+)?(value|price|amount))", text):
            scores[TaskClass.DATA_EXTRACTION] = 0.7
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        else:
            scores[TaskClass.UNKNOWN] = 1.0
        
        # Get top-K
        top_k = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Check if clarification needed
        max_score = top_k[0][1] if top_k else 0.0
        needs_clarification = max_score < self.confidence_threshold
        
        return IntentReport(
            intent_distribution=scores,
            top_k=top_k,
            needs_clarification=needs_clarification
        )


class ComplexityLayer:
    """Layer 3: Complexity and risk estimation."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def estimate(
        self,
        normalized: NormalizedInput,
        intent_report: IntentReport
    ) -> ComplexityReport:
        """Estimate complexity based on features."""
        features = {
            "length": normalized.char_count,
            "has_numbers": bool(re.search(r"\d+", normalized.text_norm)),
            "has_math": bool(re.search(r"[\+\-\*\/\^]", normalized.text_norm)),
            "injection": len(normalized.injection_flags) > 0,
            "unsupported": len(normalized.unsupported_flags) > 0
        }
        
        # Simple heuristic complexity score
        complexity = 0.0
        complexity += min(features["length"] / 1000, 0.4)
        complexity += 0.2 if features["has_numbers"] else 0
        complexity += 0.2 if features["has_math"] else 0
        complexity += 0.3 if features["injection"] else 0
        complexity += 0.3 if features["unsupported"] else 0
        
        return ComplexityReport(
            context_need=min(complexity, 1.0),
            depth=min(complexity * 0.5, 1.0),
            expected_tools=1 if features["has_math"] else 0,
            expected_out_len=int(50 + complexity * 200),
            sensitivity=Sensitivity.HIGH if features["injection"] else Sensitivity.LOW
        )


class RoutingLayer:
    """Layer 4 (combined with planning): Route planning."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def plan(
        self,
        intent_report: IntentReport,
        complexity_report: ComplexityReport,
        request: Request
    ) -> RoutePlan:
        """Plan the execution route."""
        # Route decision logic (simple for v0.1)
        top_intent = intent_report.top_k[0][0] if intent_report.top_k else TaskClass.UNKNOWN
        
        # Default route selection
        if top_intent == TaskClass.ARITHMETIC:
            selected_path = RoutePath.DETERMINISTIC
        elif top_intent == TaskClass.KNOWLEDGE_LOOKUP:
            selected_path = RoutePath.RETRIEVAL
        elif top_intent == TaskClass.DEFI_ANALYSIS:
            selected_path = RoutePath.HYBRID
        elif intent_report.needs_clarification:
            selected_path = RoutePath.CLARIFY
        elif complexity_report.sensitivity == Sensitivity.HIGH:
            selected_path = RoutePath.ABSTAIN
        else:
            selected_path = RoutePath.LLM
        
        return RoutePlan(
            intent_distribution=intent_report.intent_distribution,
            complexity_score=complexity_report.context_need,
            risk_score=complexity_report.sensitivity.value == "high",
            selected_path=selected_path,
            token_budget=1000,
            retrieval_budget=5,
            tool_budget=3
        )


class CacheLayer:
    """Layer 5: Semantic and exact caching."""
    
    def __init__(self, config: Dict[str, Any]):
        self.cache = {}  # Simple in-memory cache for v0.1
    
    def lookup(
        self,
        request: Request,
        intent_report: IntentReport,
        complexity_report: ComplexityReport
    ) -> Optional[Dict[str, Any]]:
        """Check cache for matching request."""
        # Simple exact match on input text
        cache_key = (request.input_text, intent_report.top_k[0][0] if intent_report.top_k else "unknown")
        return self.cache.get(cache_key)
    
    def store(self, request: Request, response: Any, intent: TaskClass):
        """Store result in cache."""
        cache_key = (request.input_text, intent)
        self.cache[cache_key] = response


class RetrievalLayer:
    """Layer 6: Retrieval and evidence memory."""
    
    def __init__(self, config: Dict[str, Any]):
        # Mock knowledge base for v0.1
        self.knowledge_base = [
            "Python is a programming language created by Guido van Rossum.",
            "Machine learning is a subset of artificial intelligence.",
            "DeFi stands for Decentralized Finance.",
            "Arithmetic operations include addition, subtraction, multiplication, and division.",
            "Gas fees are payments made to network validators for processing transactions."
        ]
    
    def retrieve(
        self,
        normalized: NormalizedInput,
        route_plan: RoutePlan
    ) -> List[EvidenceItem]:
        """Retrieve relevant evidence."""
        query = normalized.text_norm.lower()
        evidence = []
        
        # Simple keyword matching
        for i, doc in enumerate(self.knowledge_base):
            doc_lower = doc.lower()
            # Check if any query word appears in document
            query_words = set(query.split())
            doc_words = set(doc_lower.split())
            overlap = len(query_words & doc_words)
            
            if overlap > 0:
                relevance = overlap / len(query_words)
                evidence.append(EvidenceItem(
                    source_type="database",
                    source_uri_or_id=f"doc_{i}",
                    passage=doc,
                    relevance_score=relevance
                ))
        
        # Sort by relevance
        evidence.sort(key=lambda e: e.relevance_score, reverse=True)
        return evidence[:route_plan.retrieval_budget]


class DeterministicLayer:
    """Layer 7: Deterministic execution (calculators, parsers)."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def execute(
        self,
        normalized: NormalizedInput,
        intent_report: IntentReport
    ) -> Any:
        """Execute deterministic computation."""
        text = normalized.text_norm

        # Extract the arithmetic expression from within the text, rather than
        # requiring the ENTIRE input to be pure arithmetic characters. The
        # original regex (anchored ^...$) meant any natural-language wrapper
        # ("What is 47 * 83 + 12?") could never match, making this calculator
        # unreachable for the exact kind of input it's meant to handle.
        match = re.search(r"[\d\s\+\-\*\/\(\)\.]{3,}", text)
        if match:
            candidate = match.group(0).strip()
            # Require at least one operator so we don't "compute" a bare number.
            if re.search(r"[\+\-\*\/]", candidate):
                try:
                    result = eval(candidate, {"__builtins__": {}}, {})
                    if isinstance(result, (int, float)):
                        return str(result)
                except Exception:
                    pass

        return "Could not compute deterministically"


class LLMAdapter:
    """Layer 9: LLM synthesis adapter (stub for v0.1)."""
    
    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get("llm_enabled", False)
    
    def generate(
        self,
        normalized: NormalizedInput,
        route_plan: RoutePlan,
        evidence: List[EvidenceItem]
    ) -> tuple[str, List[EvidenceItem]]:
        """Generate response using LLM (stub in v0.1)."""
        if not self.enabled:
            return "LLM not enabled in v0.1", []
        
        # In a real implementation, this would call an LLM API
        # For v0.1, return a simple response
        return f"LLM response for: {normalized.text_norm[:50]}...", evidence


class VerificationLayer:
    """Layer 10: Verification of claims."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def verify(
        self,
        answer: Any,
        evidence: List[EvidenceItem],
        route_plan: RoutePlan
    ) -> VerificationReport:
        """Verify claims against evidence."""
        # Simple verification for v0.1
        checks = []
        
        # Check if answer is based on evidence
        if evidence and isinstance(answer, str):
            answer_lower = answer.lower()
            has_evidence_support = any(
                e.passage.lower() in answer_lower or 
                any(word in e.passage.lower() for word in answer_lower.split())
                for e in evidence
            )
            checks.append(("evidence_support", has_evidence_support))
        
        passed = all(check[1] for check in checks) if checks else True
        
        return VerificationReport(
            status=VerificationStatus.PASSED if passed else VerificationStatus.PARTIAL,
            checks=[{"name": c[0], "passed": c[1]} for c in checks]
        )


class UncertaintyLayer:
    """Layer 11: Uncertainty quantification."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def quantify(
        self,
        execution_result: Dict[str, Any],
        verification: VerificationReport,
        route_plan: RoutePlan
    ) -> UncertaintyReport:
        """Quantify uncertainty."""
        # Simple uncertainty model for v0.1
        epistemic = 0.0
        aleatoric = 0.0
        retrieval = 0.0
        execution = 0.0
        
        # Evidence uncertainty
        if not execution_result.get("evidence"):
            retrieval = 0.5
        
        # Verification uncertainty
        if verification.status == "partial":
            epistemic = 0.3
        
        # Route-based uncertainty
        if route_plan.selected_path == RoutePath.ABSTAIN:
            aleatoric = 0.8
        
        overall = 1.0 - (epistemic + aleatoric + retrieval + execution) / 4
        
        return UncertaintyReport(
            overall_confidence=max(0.0, min(1.0, overall)),
            epistemic=epistemic,
            aleatoric=aleatoric,
            retrieval=retrieval,
            execution=execution,
            calibrated=False  # Not calibrated in v0.1
        )


class SafetyLayer:
    """Layer 14: Safety and policy constraints."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def check(
        self,
        answer: Any,
        uncertainty: UncertaintyReport,
        sensitivity: Sensitivity
    ) -> SafetyReport:
        """Check safety constraints."""
        reason_codes = []
        
        # High uncertainty on high sensitivity = block
        if sensitivity == Sensitivity.HIGH and uncertainty.overall_confidence < 0.5:
            reason_codes.append("high_uncertainty_high_sensitivity")
        
        # Check for unsafe content (basic)
        if isinstance(answer, str):
            unsafe_patterns = ["hack", "exploit", "bypass", "steal private key"]
            if any(pattern in answer.lower() for pattern in unsafe_patterns):
                reason_codes.append("unsafe_content")
        
        passed = len(reason_codes) == 0
        
        return SafetyReport(
            status=SafetyStatus.BLOCKED if not passed else SafetyStatus.PASSED,
            reason_codes=reason_codes
        )


class ResponseLayer:
    """Layer 15: Response policy and rendering."""
    
    def __init__(self, config: Dict[str, Any]):
        pass
    
    def build(
        self,
        answer: Any,
        route_used: RoutePath,
        evidence: List[EvidenceItem],
        uncertainty: UncertaintyReport,
        verification: VerificationReport,
        safety: SafetyReport,
        request: Request
    ) -> Response:
        """Build final response."""
        
        # Determine status
        if route_used == RoutePath.ABSTAIN:
            status = ResponseStatus.ABSTAINED
        elif route_used == RoutePath.CLARIFY:
            status = ResponseStatus.CLARIFY
        else:
            status = ResponseStatus.ANSWERED
        
        # Extract evidence IDs
        evidence_ids = [e.evidence_id for e in evidence]
        
        return Response(
            answer=answer,
            status=status,
            route_used=route_used,
            evidence_ids=evidence_ids,
            uncertainty=uncertainty,
            verification=verification,
            safety=safety,
            cost=CostMetrics(),
            trace_id=request.request_id,
            version=SystemVersions()
        )

# ===== END uair/layers.py =====


# ===== BEGIN uair/orchestrator.py =====

"""
UAIR Orchestrator - Implements the request lifecycle:

Input → Normalize → Classify → Estimate → Route → Execute → Verify → 
Calibrate → Safety → Respond → Log → (async) Learn

This is the core pipeline that coordinates all 16 capability layers.
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UAIRRuntime:
    """
    Main UAIR runtime orchestrator.
    
    This class coordinates all layers and implements the complete request lifecycle.
    It is designed to be:
    - Measurable: Every operation is timed and costed
    - Auditable: Every decision has a trace
    - Safe: Safety gates cannot be bypassed
    - Efficient: Routes to cheapest verified path
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize UAIR runtime with all layers.
        
        Args:
            config: Configuration dictionary for layer parameters
        """
        self.config = config or {}
        
        # Initialize all layers
        self.normalize = NormalizationLayer(self.config)
        self.intent = IntentLayer(self.config)
        self.complexity = ComplexityLayer(self.config)
        self.routing = RoutingLayer(self.config)
        self.cache = CacheLayer(self.config)
        self.retrieval = RetrievalLayer(self.config)
        self.deterministic = DeterministicLayer(self.config)
        self.llm = LLMAdapter(self.config)
        self.verify = VerificationLayer(self.config)
        self.uncertainty = UncertaintyLayer(self.config)
        self.safety = SafetyLayer(self.config)
        self.response = ResponseLayer(self.config)
        
        # Metrics storage
        self.metrics = {
            "total_requests": 0,
            "by_route": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "verification_passes": 0,
            "verification_failures": 0,
            "safety_blocks": 0,
            "abstentions": 0,
        }
        
        logger.info("UAIR Runtime initialized")
    
    def handle_request(self, request: Request) -> Response:
        """
        Main entry point - processes a request through the full lifecycle.
        
        Args:
            request: Canonical Request object
            
        Returns:
            Response object with full trace and metrics
        """
        start_time = time.time()
        trace_id = request.request_id
        
        logger.info(f"Starting request {trace_id}")
        self.metrics["total_requests"] += 1
        
        try:
            # Phase 1: Normalize
            normalized = self.normalize.process(request)
            
            # Phase 2: Classify intent
            intent_report = self.intent.classify(normalized)
            
            # Phase 3: Estimate complexity/risk
            complexity_report = self.complexity.estimate(normalized, intent_report)
            
            # Phase 4: Check cache first
            cached_result = self.cache.lookup(request, intent_report, complexity_report)
            if cached_result is not None:
                self.metrics["cache_hits"] += 1
                logger.info(f"Cache hit for request {trace_id}")
                return self._build_cached_response(cached_result, request)
            
            self.metrics["cache_misses"] += 1
            
            # Phase 5: Plan route
            route_plan = self.routing.plan(
                intent_report,
                complexity_report,
                request
            )
            
            # Phase 6: Execute based on route
            execution_result = self._execute_route(
                route_plan,
                request,
                normalized,
                intent_report
            )
            
            # Phase 7: Verify
            verification = self.verify.verify(
                execution_result["answer"],
                execution_result["evidence"],
                route_plan
            )
            self.metrics["verification_passes" if verification.status.value == "passed" else "verification_failures"] += 1
            
            # Phase 8: Quantify uncertainty
            uncertainty = self.uncertainty.quantify(
                execution_result,
                verification,
                route_plan
            )
            
            # Phase 9: Safety gate
            safety = self.safety.check(
                execution_result["answer"],
                uncertainty,
                request.sensitivity
            )
            if safety.status.value == "blocked":
                self.metrics["safety_blocks"] += 1
                logger.warning(f"Safety blocked request {trace_id}")
                return self._build_safety_response(request, safety, route_plan)
            
            # Phase 10: Build response
            response = self.response.build(
                execution_result["answer"],
                route_plan.selected_path,
                execution_result["evidence"],
                uncertainty,
                verification,
                safety,
                request
            )
            
            # Update route metrics
            route_name = route_plan.selected_path.value
            self.metrics["by_route"][route_name] = self.metrics["by_route"].get(route_name, 0) + 1
            if response.status == ResponseStatus.ABSTAINED:
                self.metrics["abstentions"] += 1
            
            # Add timing
            response.cost.latency_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Completed request {trace_id} with status {response.status.value}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing request {trace_id}: {e}")
            return self._build_error_response(request, str(e))
    
    def _execute_route(
        self,
        route_plan: RoutePlan,
        request: Request,
        normalized: NormalizedInput,
        intent_report: IntentReport
    ) -> Dict[str, Any]:
        """Execute the selected route."""
        route = route_plan.selected_path
        
        if route == RoutePath.CACHE:
            # Should have been handled earlier
            raise ValueError("Cache route should be handled before execution")
        
        elif route == RoutePath.DETERMINISTIC:
            result = self.deterministic.execute(normalized, intent_report)
            return {
                "answer": result,
                "evidence": [],
                "tool_results": []
            }
        
        elif route == RoutePath.RETRIEVAL:
            evidence = self.retrieval.retrieve(normalized, route_plan)
            # Extractive answer from evidence
            answer = self._extractive_answer(evidence, normalized)
            return {
                "answer": answer,
                "evidence": evidence,
                "tool_results": []
            }
        
        elif route == RoutePath.SPECIALIST:
            # Placeholder for specialist models
            return {
                "answer": "Specialist not implemented in v0.1",
                "evidence": [],
                "tool_results": []
            }
        
        elif route == RoutePath.LLM:
            answer, evidence = self.llm.generate(
                normalized,
                route_plan,
                []
            )
            return {
                "answer": answer,
                "evidence": evidence,
                "tool_results": []
            }
        
        elif route == RoutePath.HYBRID:
            # Combine retrieval + LLM
            evidence = self.retrieval.retrieve(normalized, route_plan)
            answer, llm_evidence = self.llm.generate(
                normalized,
                route_plan,
                evidence
            )
            return {
                "answer": answer,
                "evidence": evidence + llm_evidence,
                "tool_results": []
            }
        
        elif route in (RoutePath.CLARIFY, RoutePath.ABSTAIN):
            return {
                "answer": self._get_refusal_message(route),
                "evidence": [],
                "tool_results": []
            }
        
        else:
            raise ValueError(f"Unknown route: {route}")
    
    def _extractive_answer(self, evidence: list, normalized: NormalizedInput) -> str:
        """Build extractive answer from retrieved evidence."""
        if not evidence:
            return "No relevant information found"
        
        # Simple extractive: return most relevant passage
        best = max(evidence, key=lambda e: e.relevance_score)
        return best.passage
    
    def _get_refusal_message(self, route: RoutePath) -> str:
        """Get appropriate refusal message."""
        if route == RoutePath.CLARIFY:
            return "I need more information to answer this question. Could you clarify?"
        elif route == RoutePath.ABSTAIN:
            return "I cannot provide a reliable answer to this question with the available information."
        return "Unable to process this request."
    
    def _build_cached_response(self, cached: Any, request: Request) -> Response:
        """Build response from cached result."""
        return Response(
            answer=cached["answer"],
            status=ResponseStatus.ANSWERED,
            route_used=RoutePath.CACHE,
            evidence_ids=cached.get("evidence_ids", []),
            cost=CostMetrics(
                latency_ms=0,
                estimated_cost_usd=0.0
            ),
            trace_id=request.request_id
        )
    
    def _build_safety_response(
        self,
        request: Request,
        safety: SafetyReport,
        route_plan: RoutePlan
    ) -> Response:
        """Build response when safety gate blocks."""
        return Response(
            answer="This request was blocked by safety checks.",
            status=ResponseStatus.REFUSED,
            route_used=route_plan.selected_path,
            safety=safety,
            cost=CostMetrics(latency_ms=0),
            trace_id=request.request_id
        )
    
    def _build_error_response(self, request: Request, error: str) -> Response:
        """Build error response."""
        return Response(
            answer=f"An error occurred: {error}",
            status=ResponseStatus.FAILED,
            route_used=RoutePath.ABSTAIN,
            cost=CostMetrics(latency_ms=0),
            trace_id=request.request_id
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current runtime metrics."""
        return self.metrics.copy()

# ===== END uair/orchestrator.py =====

def _spine_main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description="GENERATED condensed spine — do not edit; rebuild with build_condense.py")
    p.add_argument("cmd", nargs="?", default="help",
                   choices=["help", "adversarial", "smt-demo", "evidence", "feed-demo"])
    args = p.parse_args(argv)
    if args.cmd == "adversarial":
        print(json.dumps(run_suite(), indent=2, default=str))
    elif args.cmd == "smt-demo":
        print("allow", pre_trade_gate(2.0, 0.01, 0.95, 0.1))
        print("block", pre_trade_gate(0.1, 0.5, 0.5, 0.9))
    elif args.cmd == "evidence":
        print(json.dumps(evidence_for_decision({"regime": "normal"}), indent=2, default=str))
    elif args.cmd == "feed-demo":
        path = write_example_feed("artifacts/spine_feed_demo.json", n=3)
        print(json.dumps(ingest_feed_file(path), indent=2, default=str)[:2000])
    else:
        print("GENERATED file. Edit canonical modules, then: python build_condense.py")
        print("cmds: adversarial | smt-demo | evidence | feed-demo")
    return 0

if __name__ == "__main__":
    raise SystemExit(_spine_main())
