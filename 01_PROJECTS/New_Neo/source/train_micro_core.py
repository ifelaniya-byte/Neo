"""
PROJECT APEX: MICRO-LLM (135M-500M) DISTILLATION TRAINER
Trains a ultra-compact local model (SmolLM2-135M / Qwen2.5-0.5B) on trajectories farmed via Gemini Cloud.

This script implements the second Karpathy Loop where the micro-LLM evolves its own
training and architecture code while staying under the 500M parameter ceiling.
"""

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)

# STRICT GUARDRAIL: Parameter ceiling enforced at 500M
MAX_PARAM_LIMIT = 500_000_000
MODEL_ID = "HuggingFaceTB/SmolLM2-135M-Instruct"
DATASET_PATH = "verified_trajectories.jsonl"
OUTPUT_DIR = "./apex_nano_checkpoint"

def verify_parameter_count(model):
    """Enforces parameter constraint guardrail."""
    total_params = sum(p.numel() for p in model.parameters())
    print(f"[PARAM CHECK] Total Model Parameters: {total_params:,}")
    if total_params > MAX_PARAM_LIMIT:
        raise ValueError(f"CRITICAL: Model exceeds parameter cap! ({total_params} > {MAX_PARAM_LIMIT})")
    return total_params

def format_prompt(example):
    """Formats trajectory data into training prompt for instruction tuning."""
    prompt = (
        f"<|im_start|>system\nYou are Apex-Nano, a specialized micro-LLM code optimizer.<|im_end|>\n"
        f"<|im_start|>user\nOptimize worker_core.py for max speed and min loss.\n"
        f"Instruction: {example['instruction']}<|im_end|>\n"
        f"<|im_start|>assistant\n{example['hypothesis']}\n```python\n{example['verified_code_patch']}\n```<|im_end|>"
    )
    return {"text": prompt}

def train():
    """Main training function for micro-LLM distillation."""
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] {DATASET_PATH} not found. Run agent_runner.py first to collect trajectories.")
        return

    print(f"[MICRO-LLM TRAINER] Loading base model: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token

    dataset = load_dataset("json", data_files=DATASET_PATH)
    formatted_dataset = dataset["train"].map(format_prompt)

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=2048)

    tokenized_dataset = formatted_dataset.map(
        tokenize_function, batched=True, remove_columns=formatted_dataset.column_names
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )

    # Verify model is under 500M parameters
    verify_parameter_count(model)

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=5,
        logging_steps=5,
        save_strategy="epoch",
        fp16=not torch.cuda.is_available(),
        bf16=torch.cuda.is_available(),
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    )

    print("[MICRO-LLM TRAINER] Starting Distillation Fine-Tuning...")
    trainer.train()
    model.save_pretrained("./apex_nano_final")
    tokenizer.save_pretrained("./apex_nano_final")
    print("[SUCCESS] Apex-Nano Micro-LLM model exported to ./apex_nano_final")

if __name__ == "__main__":
    train()
