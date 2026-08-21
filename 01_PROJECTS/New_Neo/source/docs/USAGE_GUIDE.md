# PROJECT APEX: Complete Usage Guide

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Git installed and configured
- Internet connection (for Gemini API or initial model download)

### Installation (2 Commands)

```bash
# 1. Bootstrap the environment
python setup_env.py

# 2. Start the autonomous optimization loop
python agent_runner.py
```

That's it! The system will begin optimizing `worker_core.py` automatically.

---

## Detailed Setup Instructions

### Step 1: Environment Bootstrap

The `setup_env.py` script handles:
- Git repository initialization
- Git user configuration for autonomous commits
- Required package installation (psutil)
- Experiment log seeding with baseline metrics

**Expected Output:**
```
==================================================
      PROJECT APEX: SYSTEM BOOTSTRAPPER          
==================================================
[SETUP] Initializing local Git repository...
[SETUP] Dependency 'psutil' verified.
[SETUP] Seeding experiment_log.tsv...

[SUCCESS] Environment bootstrapped!
To start autonomous Gemini execution loop, run:
  python agent_runner.py
==================================================
```

### Step 2: API Configuration

#### Option A: Use Pre-configured Gemini Key
The system comes with a pre-configured Gemini API key in `agent_runner.py`. No additional setup required.

#### Option B: Use Your Own API Key
Set the `GEMINI_API_KEY` environment variable:
```bash
# Windows
set GEMINI_API_KEY=your_actual_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_actual_api_key_here
```

#### Option C: Local LLM (Ollama, LM Studio, etc.)
```bash
# Set local endpoint URL
set LOCAL_LLM_URL=http://localhost:11434/v1/chat/completions

# The system will automatically use local LLM if GEMINI_API_KEY is not set
```

#### Option D: OpenAI API
```bash
set OPENAI_API_KEY=your_openai_api_key
```

### Step 3: Start Optimization Loop

```bash
python agent_runner.py
```

**What happens next:**
1. The system reads the current `worker_core.py` implementation
2. It sends an optimization request to the configured LLM
3. The LLM proposes a code modification with a hypothesis
4. The system applies the change and runs `eval_harness.py`
5. Based on the score, it either keeps (Git commit) or reverts the change
6. Winning trajectories are exported to `verified_trajectories.jsonl`
7. The loop continues until interrupted (Ctrl+C)

---

## Understanding the Output

### Console Output Example

```
==========================================
--- STARTING EVOLUTION ITERATION #0001 ---
Current Best Score (S_eval_best): 0.500000
[HARNESS] Dispatching prompt to Gemini API...
[HYPOTHESIS]: Vectorized mathematical operations using NumPy
[HARNESS] Executing eval_harness.py...
[SERE-X GATE] Executing benchmark evaluation...
--- BENCHMARK METRICS ---
Exec Time : 8.234567s
Final Loss: 0.456789
Unit Tests: PASSED
S_EVAL    : 0.523456
[RATCHET RESULT] SUCCESS! New score 0.523456 > Best 0.500000. Keeping commit.
[DATASET BUILDER] Successfully exported winning trajectory 0001 to verified_trajectories.jsonl
```

### Key Metrics Explained

- **S_eval:** Composite score (higher is better)
- **Exec Time:** How long the benchmark took to run
- **Final Loss:** Mathematical error in computation
- **Unit Tests:** Whether correctness checks passed
- **Git Status:** KEEP (improvement) or DISCARD (regression)

---

## Monitoring Progress

### Real-Time Monitoring
Watch the console for:
- Score improvements over iterations
- Types of optimizations being attempted
- Success/failure patterns

### Experiment Log Analysis

```bash
# View complete optimization history
type experiment_log.tsv

# Count successful optimizations
findstr /C:"KEEP" experiment_log.tsv | find /C /V ""

# View recent performance
powershell "Get-Content experiment_log.tsv | Select-Object -Last 10"
```

### Trajectory Data Inspection

```bash
# View training data being collected
type verified_trajectories.jsonl

# Count collected trajectories
powershell "(Get-Content verified_trajectories.jsonl).Count"
```

### Git History Analysis

```bash
# View commit history
git log --oneline

# See code changes in latest commit
git show HEAD

# Compare with baseline
git diff base000 HEAD
```

---

## Phase 2: Building Your Local Micro-LLM

### When to Start Phase 2
Begin Phase 2 when you have:
- At least 20-50 winning trajectories in `verified_trajectories.jsonl`
- A consistent pattern of successful optimizations
- A desire to run optimization offline

### Installation of ML Dependencies

```bash
pip install torch transformers datasets accelerate
```

**Expected installation time:** 5-15 minutes depending on internet speed

### Running Micro-LLM Training

```bash
python train_micro_core.py
```

**Training Process:**
1. Loads SmolLM2-135M base model from HuggingFace
2. Processes `verified_trajectories.jsonl` into training format
3. Fine-tunes model on optimization patterns
4. Saves compressed model to `./apex_nano_final`

**Expected outputs:**
```
[MICRO-LLM TRAINER] Loading base model: HuggingFaceTB/SmolLM2-135M-Instruct
[PARAM CHECK] Total Model Parameters: 135,000,000
[MICRO-LLM TRAINER] Starting Distillation Fine-Tuning...
[SUCCESS] Apex-Nano Micro-LLM model exported to ./apex_nano_final
```

### Switching to Local Model

After training completes, modify `agent_runner.py` to use the local model:

```python
# Change MODEL_NAME to point to local model
MODEL_NAME = "./apex_nano_final"
```

Or set environment variable:
```bash
set LOCAL_LLM_URL=./apex_nano_final
```

---

## Advanced Configuration

### Customizing the Workload

To optimize your own computational task:

1. **Edit `worker_core.py`:**
```python
def run_unit_tests():
    """Your validation logic"""
    # Return True if computation is correct
    pass

def execute_benchmark_batch():
    """Your computational workload"""
    # Your code to optimize
    pass
```

2. **Update evaluation metrics in `eval_harness.py`:**
```python
# Adjust weight constants based on your priorities
W_LOSS = 0.4    # Accuracy importance
W_SPEED = 0.3   # Speed importance  
W_RAM = 0.2     # Memory efficiency
W_TESTS = 0.1   # Test reliability
```

### Adjusting Optimization Parameters

#### Loop Speed
Modify `agent_runner.py`:
```python
# Reduce sleep time for faster iteration
time.sleep(1)  # Default is 2 seconds
```

#### Training Configuration
Modify `train_micro_core.py`:
```python
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=4,  # Increase if GPU available
    gradient_accumulation_steps=2,  # Decrease for faster training
    learning_rate=2e-4,
    num_train_epochs=10,  # Increase for better quality
    # ... other parameters
)
```

### Model Selection

#### Larger Base Model
Modify `train_micro_core.py`:
```python
# Use Qwen2.5-0.5B for more capacity
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
```

#### Smaller Base Model
```python
# Use even smaller model for faster training
MODEL_ID = "HuggingFaceTB/SmolLM2-135M"
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "Git commit failed"
**Solution:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### Issue: "psutil not found"
**Solution:**
```bash
pip install psutil
```

#### Issue: "Gemini API rate limit exceeded"
**Solution:**
- Switch to local LLM: `set LOCAL_LLM_URL=http://localhost:11434/v1/chat/completions`
- Add delay between iterations: increase `time.sleep()` in `agent_runner.py`

#### Issue: "Out of memory during training"
**Solution:**
- Reduce batch size in `train_micro_core.py`
- Use gradient checkpointing
- Use smaller base model

#### Issue: "Score not improving"
**Solution:**
- Check if optimizations are actually being applied
- Review experiment log for pattern analysis
- Try different LLM or adjust temperature parameter
- Consider if current implementation is near-optimal

#### Issue: "Module import errors"
**Solution:**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Or install individually
pip install torch transformers datasets accelerate psutil
```

### Debug Mode

Enable detailed logging by modifying `agent_runner.py`:
```python
# Add at the top of the file
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Performance Optimization Tips

### For Faster Iteration
1. Use local LLM instead of cloud API
2. Reduce benchmark iteration count in `worker_core.py`
3. Optimize `eval_harness.py` for quicker execution
4. Use GPU for model training

### For Better Quality
1. Collect more trajectories before training
2. Use larger base model (within 500M limit)
3. Increase training epochs
4. Implement DPO for preference learning

### For Resource Efficiency
1. Use quantization (INT8) during training
2. Reduce batch size
3. Enable gradient accumulation
4. Use CPU-only training if GPU unavailable

---

## Integration Examples

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run APEX Optimization
  run: |
    python setup_env.py
    python agent_runner.py &
    sleep 300  # Run for 5 minutes
    pkill -f agent_runner.py
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /apex
COPY . .

RUN pip install torch transformers datasets accelerate psutil

RUN python setup_env.py

CMD ["python", "agent_runner.py"]
```

### Monitoring Integration

```python
# Add to agent_runner.py for external monitoring
def send_metrics_to_monitoring(score, hypothesis):
    # Send to Prometheus, Grafana, etc.
    pass
```

---

## Best Practices

### 1. Start Simple
- Begin with the provided `worker_core.py` baseline
- Understand the optimization patterns before customization
- Monitor initial iterations to establish baseline behavior

### 2. Monitor Progress
- Regularly check `experiment_log.tsv` for trends
- Inspect trajectory quality in `verified_trajectories.jsonl`
- Review Git commits to understand optimization strategies

### 3. Ensure Safety
- Keep Git repository clean
- Backup important versions before major changes
- Monitor system resources during execution

### 4. Optimize Iteratively
- Let the system run for sufficient iterations (20-50+)
- Analyze patterns in successful optimizations
- Adjust evaluation weights based on priorities

### 5. Plan for Phase 2
- Collect diverse optimization strategies
- Ensure trajectory quality before training
- Test local model thoroughly before full deployment

---

## FAQs

**Q: How long should I let the system run?**
A: For initial data collection, 20-50 iterations (1-2 hours). For continuous optimization, let it run until score convergence.

**Q: Can I use this for optimizing my own code?**
A: Yes! Modify `worker_core.py` with your computational task while maintaining the required function signatures.

**Q: What if the system makes my code worse?**
A: The Git Ratchet automatically reverts any changes that don't improve the score. Your code is always protected.

**Q: Can I run multiple optimization instances?**
A: Yes, but use separate directories to avoid Git conflicts and trajectory mixing.

**Q: How do I know when to stop?**
A: Stop when the score plateaus for 10+ consecutive iterations or reaches your target performance.

**Q: Can I use this for other programming languages?**
A: The current system is Python-specific. For other languages, you'd need to modify the evaluation harness and code generation.

---

## Support and Contributing

### Getting Help
- Check this documentation first
- Review experiment logs for patterns
- Inspect Git history for successful strategies

### Contributing
- Share successful optimization strategies
- Report bugs with detailed logs
- Suggest improvements to evaluation metrics

### Community Resources
- Join the Project APEX community
- Share your trajectory datasets
- Contribute evaluation benchmarks

---

## Conclusion

Project APEX provides a complete, turnkey system for autonomous code optimization. By following this guide, you can:

1. **Quickly start** optimizing code with minimal setup
2. **Monitor progress** through comprehensive logging
3. **Build local models** for offline operation
4. **Customize the system** for your specific needs
5. **Troubleshoot issues** with detailed guidance

The system represents a new paradigm in autonomous software improvement, combining cutting-edge AI techniques with practical software engineering principles.