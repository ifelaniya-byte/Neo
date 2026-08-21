# IMPLEMENTATION GUIDE

## Building the Complete System

This guide walks you through building the complete Project APEX system step by step.

## Phase 1: Core Model

### Step 1: Define the Model Architecture

```python
import torch
import torch.nn as nn

class MicroLLM(nn.Module):
    def __init__(self, vocab_size=50000, d_model=512, nhead=8, num_layers=6, d_ff=2048):
        super().__init__()
        
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model)
        
        self.layers = nn.ModuleList([
            TransformerLayer(d_model, nhead, d_ff)
            for _ in range(num_layers)
        ])
        
        self.output = nn.Linear(d_model, vocab_size)
    
    def forward(self, x):
        x = self.embedding(x)
        x = self.pos_encoding(x)
        
        for layer in self.layers:
            x = layer(x)
        
        return self.output(x)
```

### Step 2: Initialize with Proper Weights

```python
def initialize_model(model):
    for name, param in model.named_parameters():
        if 'weight' in name and param.dim() >= 2:
            nn.init.xavier_uniform_(param)
        elif 'bias' in name:
            nn.init.zeros_(param)
    
    return model
```

## Phase 2: Karpathy Loop Integration

### Step 3: Implement Self-Evaluation

```python
def self_evaluate(model, validation_loader):
    model.eval()
    total_loss = 0.0
    total_accuracy = 0.0
    
    with torch.no_grad():
        for batch in validation_loader:
            outputs = model(batch['input_ids'])
            loss = nn.functional.cross_entropy(
                outputs, batch['target_ids']
            )
            
            predictions = outputs.argmax(dim=-1)
            correct = (predictions == batch['target_ids']).sum().item()
            total = batch['target_ids'].numel()
            
            total_loss += loss.item()
            total_accuracy += (correct / total) * 100
    
    return {
        'loss': total_loss / len(validation_loader),
        'accuracy': total_accuracy / len(validation_loader)
    }
```

### Step 4: Implement Hypothesis Generation

```python
def generate_hypothesis(model, current_metrics):
    param_count = sum(p.numel() for p in model.parameters())
    
    hypotheses = []
    
    # Parameter constraint check
    if param_count > 450_000_000:
        hypotheses.append({
            'type': 'compression',
            'description': 'Prune 10% of weights',
            'priority': 1.0
        })
    
    # Accuracy check
    if current_metrics['accuracy'] < 0.8:
        hypotheses.append({
            'type': 'capacity',
            'description': 'Increase d_ff in layers 4-6',
            'priority': 0.8
        })
    
    # Always consider weight evolution
    hypotheses.append({
        'type': 'weight_evolution',
        'description': 'Apply Gaussian mutation',
        'priority': 0.6
    })
    
    return max(hypotheses, key=lambda h: h['priority'])
```

### Step 5: Implement Modification Application

```python
def apply_compression(model):
    original_count = sum(p.numel() for p in model.parameters())
    
    with torch.no_grad():
        for name, param in model.named_parameters():
            if param.dim() > 1:
                importance = torch.abs(param)
                threshold = torch.quantile(importance, 0.1)
                mask = importance > threshold
                param.data *= mask.float()
    
    new_count = sum(p.numel() for p in model.parameters())
    compression_ratio = original_count / new_count
    
    return compression_ratio > 1.0

def apply_weight_mutation(model):
    with torch.no_grad():
        for name, param in model.named_parameters():
            if param.dim() > 1:
                noise = torch.randn_like(param) * 0.01
                param.data += noise
    
    return True
```

### Step 6: Implement Validation

```python
def validate_modification(model, training_loader, validation_loader):
    old_metrics = self_evaluate(model, validation_loader)
    
    # Train for one step
    model.train()
    for batch in training_loader:
        optimizer.zero_grad()
        outputs = model(batch['input_ids'])
        loss = nn.functional.cross_entropy(outputs, batch['target_ids'])
        loss.backward()
        optimizer.step()
        break
    
    new_metrics = self_evaluate(model, validation_loader)
    
    improvement = new_metrics['accuracy'] > old_metrics['accuracy']
    
    return {
        'improvement': improvement,
        'old_metrics': old_metrics,
        'new_metrics': new_metrics
    }
```

## Phase 3: Integration

### Step 7: Create Main Loop

```python
def run_internal_loop(model, training_loader, validation_loader, iterations=100):
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    for iteration in range(iterations):
        # 1. Self-evaluate
        current_metrics = self_evaluate(model, validation_loader)
        
        # 2. Generate hypothesis
        hypothesis = generate_hypothesis(model, current_metrics)
        
        # 3. Apply modification
        old_state = copy.deepcopy(model.state_dict())
        
        modification_success = False
        if hypothesis['type'] == 'compression':
            modification_success = apply_compression(model)
        elif hypothesis['type'] == 'weight_evolution':
            modification_success = apply_weight_mutation(model)
        
        if modification_success:
            # 4. Validate
            validation_result = validate_modification(
                model, training_loader, validation_loader
            )
            
            if validation_result['improvement']:
                # 5. Commit
                print(f"Iteration {iteration}: IMPROVEMENT")
                print(f"  Old Accuracy: {validation_result['old_metrics']['accuracy']:.2f}")
                print(f"  New Accuracy: {validation_result['new_metrics']['accuracy']:.2f}")
            else:
                # 6. Revert
                model.load_state_dict(old_state)
                print(f"Iteration {iteration}: REVERT")
        else:
            print(f"Iteration {iteration}: MODIFICATION FAILED")
    
    return model
```

## Phase 4: Testing

### Step 8: Test the Implementation

```python
# Create test data
test_model = MicroLLM()
test_model = initialize_model(test_model)

# Test evaluation
print("Testing self-evaluation...")
# Add your test data loader here

# Test hypothesis generation
print("Testing hypothesis generation...")
metrics = {'accuracy': 0.75, 'parameter_count': 500_000_000}
hypothesis = generate_hypothesis(test_model, metrics)
print(f"Generated hypothesis: {hypothesis}")

# Test modification
print("Testing modification application...")
success = apply_weight_mutation(test_model)
print(f"Modification success: {success}")

print("Implementation test complete.")
```

## Common Errors

### Error 1: Parameter Count Exceeded
**Symptom:** Error about too many parameters
**Solution:** Apply compression before capacity increase

### Error 2: Loss NaN
**Symptom:** Loss becomes NaN during training
**Solution:** Reduce learning rate, check gradient clipping

### Error 3: No Improvement
**Symptom:** Accuracy stays constant
**Solution:** Try different hypothesis, check learning rate

## Verification Checklist

Before proceeding to testing, verify:
- [ ] Model compiles without errors
- [ ] Self-evaluation returns valid metrics
- [ ] Hypothesis generation works
- [ ] Modifications apply correctly
- [ ] Validation detects improvements
- [ ] Revert restores previous state
- [ ] Overall loop runs without errors

## Next Step

Take the DOCUMENT_TEST.md to verify your understanding of this implementation guide.
