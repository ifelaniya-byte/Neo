# WEIGHT CHARTS

## Understanding Parameter Efficiency

Weight charts show how different parameter counts correlate with performance across model architectures.

## Flagship Model Parameters

| Model | Parameters | Performance (MMLU) | Efficiency Score |
|-------|-----------|-------------------|-----------------|
| Claude 3.5 Sonnet | 175B | 88.7 | 0.507 |
| GPT-4 Turbo | 1.7T | 86.4 | 0.051 |
| Gemini 1.5 Pro | 1.5T | 85.2 | 0.057 |
| GLM-4 | 1.8T | 82.5 | 0.046 |
| DeepSeek V2 | 236B/21B | 81.0 | 3.858 |
| Llama 3.1 405B | 405B | 88.3 | 0.218 |
| Mixtral 8x22B | 141B/39B | 81.2 | 2.083 |
| Qwen2.5 72B | 72B | 86.5 | 1.201 |

## Efficiency Formula

```
Efficiency Score = Performance Score / (Parameters in Billions)
```

**Example Calculation:**
- Claude 3.5 Sonnet: 88.7 / 175 = 0.507
- DeepSeek V2: 81.0 / 21 (active) = 3.858

## Key Insights

### 1. Parameter Count vs Performance
- More parameters ≠ always better performance
- Architecture matters significantly
- Mixture of Experts (MoE) provides efficiency advantage

### 2. Your Constraint: 500M Parameters
- You have 0.5B parameters
- Target efficiency: 2.0+ (above DeepSeek V2)
- To achieve 0.507 efficiency (Claude): need 25.35 MMLU score
- To achieve 3.858 efficiency (DeepSeek): need 192.9 MMLU score

### 3. Optimization Strategies
- **Layer Pruning:** Remove 10-20% of weights
- **Quantization:** FP16 → INT8 reduces size 2-4x
- **Knowledge Distillation:** Learn from larger models
- **Architecture Search:** Find optimal patterns

## Weight Distribution

### Typical Transformer Distribution

For a 500M parameter model:

- **Embeddings:** 10% (50M)
- **Attention:** 40% (200M)
- **Feed-Forward:** 40% (200M)
- **Output:** 10% (50M)

### Layer-wise Distribution

```
Layer 1:   5M parameters
Layer 2:   10M parameters
Layer 3:   20M parameters
Layer 4:   40M parameters
Layer 5:   80M parameters
Layer 6:   160M parameters
Layer 7:   85M parameters
Layer 8:   0M parameters (removed by pruning)
```

## Compression Impact

### Before Compression
- Total Parameters: 500M
- Accuracy: 85%
- Size: 1GB (FP16)

### After Compression (50% pruning + INT8 quantization)
- Total Parameters: 250M
- Accuracy: 83% (minimal loss)
- Size: 250MB (INT8)
- **Efficiency Gain:** 2x

## Scaling Laws

### Chinchilla Scaling

```
Performance ∝ Parameters^0.076
```

**Example:**
- 175B → 88.7 MMLU
- 0.5B → expected: 88.7 × (0.5/175)^0.076 = 88.7 × 0.50 = 44.35 MMLU

**Your Target:** Beat 44.35 expected through architectural optimization

### Neural Scaling Laws

- **Kaplan et al.:** Performance ∝ N^(0.076)
- **Hestness et al.:** Performance ∝ N^(0.074)
- **Henighan et al.:** Performance ∝ N^(0.08)

Your goal: Beat scaling law predictions through clever architecture.

## Weight Initialization

### Best Practices

1. **Xavier/Glorot Initialization**
   - Scales based on layer input/output dimensions
   - Prevents vanishing/exploding gradients

2. **Pre-trained Initialization**
   - Start from larger model weights
   - Fine-tune for your task
   - Better than random initialization

3. **Layer-wise Learning Rate Decay**
   - Lower learning rates for earlier layers
   - Higher learning rates for later layers
   - Improves fine-tuning

## Weight Evolution

### Mutation Strategies

1. **Gaussian Mutation**
   - Add Gaussian noise to weights
   - Small standard deviation (0.01-0.1)
   - Preserves learned patterns

2. **Layer-wise Mutation**
   - Mutate specific layers
   - Target underperforming components
   - Preserve working components

3. **Structural Mutation**
   - Add/remove layers
   - Change layer sizes
   - Modify connections

## Testing Your Understanding

**Question 1:** What is the efficiency score of DeepSeek V2?
**Answer:** 3.858 (81.0 / 21 active parameters)

**Question 2:** What is your parameter constraint?
**Answer:** 500,000,000 parameters maximum

**Question 3:** What is the Chinchilla scaling exponent?
**Answer:** 0.076

**Question 4:** Why is MoE architecture efficient?
**Answer:** Only uses active parameters during inference (21B active vs 236B total)

## Next Step

Read PERFORMANCE_METRICS.md to understand how to measure your optimization success.
