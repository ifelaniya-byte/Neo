# PERFORMANCE METRICS

## Measuring Model Performance

To optimize effectively, you must understand how to measure performance accurately.

## Core Metrics

### 1. Loss Function
**Definition:** Error between predicted and actual values
**Target:** Minimize loss
**Common Losses:**
- Cross-Entropy Loss (classification)
- Mean Squared Error (regression)
- Binary Cross-Entropy (binary classification)

```python
loss = cross_entropy_loss(predictions, targets)
```

### 2. Accuracy
**Definition:** Percentage of correct predictions
**Target:** Maximize accuracy
**Calculation:**
```python
accuracy = (correct_predictions / total_predictions) * 100
```

### 3. MMLU (Massive Multitask Language Understanding)
**Definition:** Performance across 57 academic subjects
**Target:** Maximize MMLU score
**Range:** 0-100

### 4. HumanEval
**Definition:** Python coding problem solving
**Target:** Maximize HumanEval score
**Range:** 0-100

### 5. Inference Time
**Definition:** Time to generate response
**Target:** Minimize inference time
**Measurement:** Milliseconds per token

### 6. Memory Usage
**Definition:** GPU/CPU memory consumption
**Target:** Minimize memory usage
**Measurement:** GB

## Evaluation Protocol

### Validation Set
- **Purpose:** Measure performance without overfitting
- **Size:** 10-20% of total data
- **Usage:** Evaluate after each iteration

### Test Set
- **Purpose:** Final performance measurement
- **Size:** 10-20% of total data
- **Usage:** Evaluate at end of training

### Train Set
- **Purpose:** Optimize model weights
- **Size:** 60-80% of total data
- **Usage:** Training only

## Metric Calculation

### Loss Calculation
```python
def compute_loss(outputs, targets):
    criterion = nn.CrossEntropyLoss()
    return criterion(outputs, targets)
```

### Accuracy Calculation
```python
def compute_accuracy(outputs, targets):
    predictions = outputs.argmax(dim=-1)
    correct = (predictions == targets).sum().item()
    total = targets.numel()
    return (correct / total) * 100
```

### F1 Score
```python
def compute_f1_score(predictions, targets):
    from sklearn.metrics import f1_score
    return f1_score(targets.cpu(), predictions.cpu(), average='weighted')
```

## Performance Tracking

### Metrics to Track Per Iteration

1. **Training Loss**
2. **Validation Loss**
3. **Validation Accuracy**
4. **Inference Time**
5. **Memory Usage**
6. **Parameter Count**
7. **GPU Utilization**

### Visualization

**Loss Curve:**
```
Loss
│
│  ╱
│  ╲
│   ╲___
│        ╲___
│────────────── Iteration
```

**Accuracy Curve:**
```
Accuracy
│         ___
│       ___╱
│     ___╱
│  ___╱
│__╱
│────────────── Iteration
```

## Thresholds

### Performance Targets

**For 500M Parameter Model:**
- **MMLU:** 60-70 (good), 70-80 (excellent), 80+ (SOTA)
- **HumanEval:** 50-60 (good), 60-70 (excellent), 70+ (SOTA)
- **Inference Time:** <100ms (good), <50ms (excellent), <20ms (SOTA)
- **Memory:** <2GB (good), <1GB (excellent), <500MB (SOTA)

### Failure Thresholds

**When to Intervene:**
- **Loss stops decreasing:** Plateau detection
- **Accuracy starts decreasing:** Overfitting
- **Inference time increases:** Inefficiency
- **Memory exceeds limit:** Compression needed

## Early Stopping

### Stopping Criteria

Stop training when:
1. Validation loss hasn't improved for 10 iterations
2. Validation accuracy decreases for 5 iterations
3. Training time exceeds budget
4. Memory limit exceeded

### Checkpointing

Save checkpoints when:
1. New best validation accuracy achieved
2. Every 10 iterations
3. Before major architectural changes

## Testing Your Understanding

**Question 1:** What is the primary purpose of the validation set?
**Answer:** To measure performance without overfitting

**Question 2:** What is a good HumanEval score for a 500M model?
**Answer:** 50-60 (good), 60-70 (excellent), 70+ (SOTA)

**Question 3:** When should you stop training?
**Answer:** When validation loss hasn't improved for 10 iterations

**Question 4:** What is F1 score?
**Answer:** Harmonic mean of precision and recall, balanced metric

## Next Step

Read IMPLEMENTATION_GUIDE.md to learn how to build the complete system.
