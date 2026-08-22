# Model Weight Rotation Lab

## Overview

This notebook implements a **dynamic weight rotation system** that automatically switches between different model configurations based on the domain of the input prompt. This addresses the concept of "dialing in weights" without storing 56 static weight files.

## How It Works

### 1. Domain Classification
The system classifies input prompts into domains:
- **Math**: Calculation, equations, percentages
- **Structured**: JSON output, formatting, data parsing
- **Instruction**: Step-by-step procedures, commands
- **Fact**: Informational questions, definitions
- **General**: Fallback for uncategorized prompts

### 2. Weight Variants
Each domain has a specialized weight variant with optimized parameters:
- **base_q4**: General purpose (temp=0.7, top_p=0.9)
- **math_specialist**: Low temperature for precision (temp=0.3)
- **structured_specialist**: Very low temperature for exact formatting (temp=0.2)
- **instruction_specialist**: Balanced for following directions (temp=0.6)

### 3. Dynamic Rotation
Instead of storing 56 separate weight files, the system:
- Uses a single GGUF model
- Dynamically adjusts inference parameters (temperature, top_p, top_k)
- Swaps system prompts based on domain
- Tracks rotation history and statistics

## Key Concepts

### This is NOT MoE
This rotation system is different from Mixture of Experts:
- **MoE**: 128 expert weights, router activates specific experts per token
- **Rotation**: Single model, dynamic parameter switching per request

### The "56" Concept
The "56" from our discussion referred to:
- Frontier MoE models have 128+ experts (Qwen3-235B, gpt-oss)
- Your vision of 56 diverse "opinions" (expert weights)
- This rotation system is a lightweight approximation

### Tesla Math Connections
The rotation mechanism uses:
1. **Classification routing** (linear algebra: similarity scoring)
2. **Parameter interpolation** (calculus: gradient-based adjustment)
3. **Temperature scheduling** (optimization: annealing patterns)

## Usage on Kaggle

1. Upload `30_rotation_lab.ipynb` to Kaggle
2. Enable GPU accelerator
3. Run cells sequentially:
   - Cell 1-4: Setup and configuration
   - Cell 5-7: Download model and build llama.cpp
   - Cell 8: Create multiple GGUF quantizations (Q4, Q5, Q6)
   - Cell 9-10: Run rotation benchmark
   - Cell 11: Generate rotation manifest

## Expected Output

The system will:
1. Classify test prompts into domains
2. Select appropriate weight variant
3. Generate responses with domain-optimized parameters
4. Report rotation accuracy (how often it selected the correct variant)
5. Output a rotation manifest with all configurations

## Advantages

- **Storage efficient**: 1 model × 3 quantizations = 3 files (not 56)
- **Fast switching**: Parameter changes are instant
- **Tracked**: Full rotation history and statistics
- **Extensible**: Easy to add new domains or variants

## Limitations

- Same base model weights (not true expert specialization)
- Parameter changes have limited effect compared to weight changes
- Requires good domain classification for best results
- Not as powerful as true MoE with learned routing

## Next Steps

To move closer to your vision:
1. **Fine-tune variants**: Train separate adapters for each domain
2. **Learned routing**: Train a neural router instead of keyword matching
3. **MoE conversion**: Convert the model to MoE architecture
4. **Expert weights**: Train actual expert weights for each domain
