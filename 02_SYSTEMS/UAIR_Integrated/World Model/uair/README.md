# UniCompact Adaptive Intelligence Runtime (UAIR)

**Version 0.1.0** - Minimum Viable Implementation

## What UAIR Is

UAIR is a **measurable adaptive intelligence runtime** that routes requests to the cheapest verified execution path capable of meeting quality and safety contracts.

**What UAIR does:**
- Routes arithmetic to calculators (not LLMs)
- Routes factual queries to retrieval (not hallucination)
- Routes synthesis to LLMs (only when necessary)
- Measures cost per verified success
- Enforces uncertainty quantification
- Implements safety gates and abstention

**What UAIR is NOT:**
- An LLM replacement
- General intelligence
- A zero-dependency system
- A single-file universe
- Guaranteed 20-100× cheaper (measured empirically, not claimed)

## Architecture

UAIR implements 16 capability layers as interfaces (not 16 separate models):

1. **Input normalization** - Canonical request object
2. **Intent classification** - Task distribution + confidence
3. **Complexity estimation** - Budget planning
4. **Context selection** - Extractive ranking with provenance
5. **Semantic cache** - Exact → normalized → semantic
6. **Retrieval memory** - Hybrid search with citations
7. **Deterministic execution** - Calculators, parsers, validators
8. **Specialized predictors** - Compact models (post-v0.1)
9. **LLM synthesis** - Optional, budgeted, schema-constrained
10. **Verification** - Numerical, citation, schema checks
11. **Uncertainty** - Epistemic/aleatoric/retrieval/execution
12. **Calibration** - Per-task, held-out (post-v0.1)
13. **OOD detection** - Novelty detection (post-v0.1)
14. **Safety** - Pre/in/post execution checks
15. **Response policy** - Minimal sufficient answer
16. **Learning & governance** - Offline/shadow/canary (post-v0.1)

## v0.1 Scope

**MVP includes:**
- Typed data contracts
- Rule-based routing
- Exact + normalized caching
- Deterministic calculator
- Retrieval with provenance
- LLM adapter (stub)
- Basic uncertainty states
- Safety gates
- Structured traces
- Cost metrics

**Post-v0.1 (requires measurement):**
- Learned routing
- Semantic cache
- Compact specialist models
- Full calibration
- OOD detection
- Multi-model verification

## Installation

```bash
cd uair
pip install -r requirements.txt
```

## Usage

```python
from uair import UAIRRuntime, Request, Sensitivity

# Initialize runtime
runtime = UAIRRuntime()

# Create request
request = Request(
    input_text="What is 2 + 2?",
    sensitivity=Sensitivity.LOW
)

# Handle request
response = runtime.handle_request(request)

print(f"Answer: {response.answer}")
print(f"Route: {response.route_used}")
print(f"Confidence: {response.uncertainty.overall_confidence}")
print(f"Cost: ${response.cost.estimated_cost_usd:.4f}")
```

## Success Metrics

v0.1 success criteria:
- Completes bounded benchmark suite
- Reduces LLM tokens or total cost vs all-LLM baseline
- Preserves or improves verified task success
- Demonstrates safe abstention on unsupported inputs
- Produces auditable traces for every request

## Key Principle

**Route every request to the least expensive verified execution path that meets the quality and safety contract.**

## Relationship to MegaCompact16

- **MegaCompact16**: Decision framework for DeFi trading
- **UAIR**: General adaptive intelligence runtime
- **Shared patterns**: Uncertainty quantification, safety gates, verification, abstention, cost accounting

## License

MIT License - See LICENSE file for details

## Acknowledgments

This system incorporates patterns from:
- MegaCompact16 (decision-making, uncertainty, safety)
- Production LLM orchestration systems (routing, verification, cost accounting)
- Academic research on conformal prediction and uncertainty quantification
