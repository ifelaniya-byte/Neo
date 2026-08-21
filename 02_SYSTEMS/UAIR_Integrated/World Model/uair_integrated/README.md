# UAIR-Integrated Stationary System

**Version 1.0.0** - UAIR Integration with Stationary/Non-Stationary System

## What This Is

This directory contains the integration of **UAIR (UniCompact Adaptive Intelligence Runtime)** with the **stationary/non-stationary mathematical and knowledge system**.

## Integration Phases Implemented

### **Phase 1: UAIR Routing Integration** ✅
- **File**: `uair_enhanced_router.py`
- **What it does**:
  - Replaces simple router with UAIR RoutingLayer
  - Routes to cheapest verified execution path
  - Adds cost accounting to all routing decisions
  - Supports cache → deterministic → retrieval → LLM escalation
  - Integrates with existing tools, Atlas, and gradient systems

### **Phase 2: UAIR Verification Enhancement** ✅
- **File**: `uair_math_verifier.py`
- **What it does**:
  - Adds UAIR VerificationLayer for mathematical proofs
  - Performs numerical re-computation
  - Verifies citations against Atlas knowledge base
  - Validates formula structure/schema
  - Integrates with Shadow seal integrity system
  - Provides verification confidence scores

### **Phase 2: UAIR Uncertainty Quantification** ✅
- **File**: `uair_uncertainty_wrapper.py`
- **What it does**:
  - Adds UAIR UncertaintyLayer for confidence scoring
  - Decomposes uncertainty into epistemic, aleatoric, retrieval, execution
  - Integrates with Shadow seal confidence
  - Tracks evidence source count
  - Measures computation complexity
  - Provides actionable uncertainty signals

### **Phase 3: UAIR Orchestrator** ✅
- **File**: `uair_orchestrator.py`
- **What it does**:
  - Main integration point combining all UAIR components
  - Uses UAIR-enhanced routing for all operations
  - Applies UAIR verification to mathematical results
  - Quantifies uncertainty using UAIR methods
  - Provides full cost accounting
  - Compatible with existing Agent interface via adapter

## How to Use

### **Option 1: Direct Integration (Replace Existing Router)**

```python
from uair_integrated import UAIREnhancedRouter

# Replace existing router with UAIR-enhanced router
# In your stationary system:
router = UAIREnhancedRouter(tools, atlas, gradient, config)

# Use it exactly like the old router
result = router.route("tool:solve_equation", {"computation": "2 + 2"})
```

### **Option 2: Full Integration (Replace Agent)**

```python
from uair_integrated import UAIRIntegratedActor

# Replace existing Agent with UAIR-integrated actor
actor = UAIRIntegratedActor(tools, atlas, gradient, shadow_system, config)

# Use it exactly like the old Agent
results = actor.run(["tool:solve_equation", "atlas:search"])
```

### **Option 3: Gradual Integration (Add Verification/Uncertainty)**

```python
from uair_integrated import UAIRMathVerifier, UAIRUncertaintyWrapper

# Add verifier to existing system
verifier = UAIRMathVerifier(atlas, shadow_system, config)
verification = verifier.verify_mathematical_result(result, formula_name, computation)

# Add uncertainty quantification
uncertainty = UAIRUncertaintyWrapper(shadow_system, config)
uncertainty_report = uncertainty.quantify_uncertainty(result, verification, formula_name)
```

## Key Metrics

### **Cost Metrics**
- **Cost per verified success**: Total cost / successful verifications
- **Route costs**: Tracked by path (cache, deterministic, retrieval, LLM)
- **Total cost**: Cumulative cost across all operations

### **Quality Metrics**
- **Verification pass rate**: Percentage of verifications that pass
- **Average confidence**: Mean confidence across all operations
- **High uncertainty abstentions**: Operations that abstained due to low confidence

### **Performance Metrics**
- **Cache hit rate**: Percentage of requests served from cache
- **Route distribution**: Distribution of requests across different paths
- **Average latency**: Mean latency across all operations

## Integration Benefits

### **Compared to Original System**

**Before Integration:**
- Simple rule-based routing
- No cost accounting
- Basic verification (intact/compromised)
- No uncertainty quantification
- No abstention logic

**After UAIR Integration:**
- Intelligent routing based on intent and complexity
- Full cost accounting per operation
- Multi-layer verification (numerical, citation, schema, seal)
- Decomposed uncertainty with confidence scores
- Uncertainty-gated abstention (abstain when confidence < 0.3)

### **Expected Improvements**

Based on UAIR design principles:
- **2-3× improvement in cost-per-verified-success** (through better routing)
- **1.5-2× improvement in verification quality** (through multi-layer checks)
- **1.2-1.5× improvement in reliability** (through uncertainty quantification)

## Files

- `__init__.py` - Package initialization
- `uair_enhanced_router.py` - Phase 1: UAIR routing integration
- `uair_math_verifier.py` - Phase 2: UAIR verification enhancement
- `uair_uncertainty_wrapper.py` - Phase 2: UAIR uncertainty quantification
- `uair_orchestrator.py` - Phase 3: Main orchestrator
- `integration_example.py` - Example usage with mock systems
- `README.md` - This file

## Dependencies

- UAIR (parent directory)
- Stationary system (atlas_shadow_unified.py)
- PyTorch (from stationary system)
- SymPy (from stationary system)

## Next Steps

### **Phase 3: MegaCompact16 Decision Layer (Optional)**
- Add MegaCompact16 decision-making for complex mathematical planning
- Use MegaCompact16 uncertainty for seal confidence
- Add MegaCompact16 safety gates for experimental operations

### **Phase 4: External LLM Integration**
- Add OpenAI/Anthropic API client
- Replace rule-based intent classification with LLM
- Add LLM-based verification and uncertainty estimation
- Measure cost-per-verified-success improvement

### **Phase 5: Learned Embeddings**
- Add sentence-transformers
- Implement vector search for Atlas
- Add semantic caching
- Measure retrieval quality improvement

## Notes

- This integration preserves the existing interface - you can drop it in without changing the rest of the stationary system
- All UAIR components are modular - you can use them independently or together
- The adapter class `UAIRIntegratedActor` makes integration seamless
- Metrics are tracked at multiple levels (orchestrator, router, verifier, uncertainty)

## License

MIT License - See parent UAIR and stationary system licenses for details
