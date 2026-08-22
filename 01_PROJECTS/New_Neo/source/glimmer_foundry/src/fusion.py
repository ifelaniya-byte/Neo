"""
GlimmerFoundry fusion layer.

Fills both gaps:
  1. Meta Muse Glimmer — open Apache 2.0 weights, on-device agent, single GPU
  2. Weight Foundry   — Online-LoRA+ / GRPO-R1 / Tree-Filtered continual updates
                        with holdout promote/rollback

Result: people download a real local model AND keep improving it safely on their machine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


GLIMMER_ID = "meta-models/Muse-Glimmer-30B"
LFM_ID = "LFM/LFM-2.5-8B-A1B"
FALLBACK_ID = "Qwen/Qwen2.5-0.5B-Instruct"


@dataclass
class FusionStatus:
    base_model: str
    backend: str
    load_in_4bit: bool
    local_only: bool
    continual_modes: list[str]
    message: str
    e2b_enabled: bool = False
    groq_enabled: bool = False
    model_variants: list[str] = None

    def __post_init__(self):
        if self.model_variants is None:
            self.model_variants = []

    def to_dict(self) -> dict:
        return {
            "base_model": self.base_model,
            "backend": self.backend,
            "load_in_4bit": self.load_in_4bit,
            "local_only": self.local_only,
            "continual_modes": self.continual_modes,
            "message": self.message,
            "fusion": "GlimmerFoundry",
            "thesis": "Open weights in your hands + continual adaptation you control",
            "e2b_enabled": self.e2b_enabled,
            "groq_enabled": self.groq_enabled,
            "model_variants": self.model_variants,
        }


def resolve_model_id(cfg: dict, force_fallback: bool = False) -> str:
    if force_fallback:
        return cfg.get("model", {}).get("fallback_id", FALLBACK_ID)
    
    strategy = cfg.get("model", {}).get("selection_strategy", "auto")
    
    if strategy == "alternative":
        return cfg.get("model", {}).get("alternative_id", LFM_ID)
    elif strategy == "auto":
        # Auto-select based on available resources
        # Try alternative first (LFM 8B), fall back to primary if needed
        alternative_id = cfg.get("model", {}).get("alternative_id", LFM_ID)
        primary_id = cfg.get("model", {}).get("id", GLIMMER_ID)
        
        # For now, prefer the alternative model (LFM 8B) for better resource efficiency
        return alternative_id
    else:
        return cfg.get("model", {}).get("id", GLIMMER_ID)


def fusion_banner(cfg: dict) -> str:
    mid = resolve_model_id(cfg)
    external = cfg.get("external_services", {})
    e2b_status = "✓ E2B Sandbox" if external.get("e2b_enabled") else "✗ E2B Sandbox"
    groq_status = "✓ Groq Teacher" if external.get("groq_enabled") else "✗ Groq Teacher"
    
    return (
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║  GLIMMER FOUNDRY  —  open local model × continual harness    ║\n"
        "╠══════════════════════════════════════════════════════════════╣\n"
        f"║  Base:  {mid[:48]:<48} ║\n"
        f"║  Safety: {e2b_status:<20} │ Teacher: {groq_status:<19} ║\n"
        "║  Modes: Online-LoRA+ · GRPO-R1 · Tree-Filtered               ║\n"
        "║  Contract: holdout promote/rollback · fixed LR · local-first ║\n"
        "╚══════════════════════════════════════════════════════════════╝"
    )


def describe_fusion() -> dict[str, Any]:
    return {
        "name": "GlimmerFoundry",
        "fills": {
            "meta_gap": "Downloadable open weights + on-device agent (Muse Glimmer)",
            "foundry_gap": "Continual weight updates under verifier + holdout safety",
            "lfm_gap": "High-performance compact model (LFM 2.5 8B A1B)",
            "safety_gap": "E2B sandbox execution for safe code verification",
            "teacher_gap": "Groq high-speed teacher distillation",
        },
        "base": {
            "primary_id": GLIMMER_ID,
            "alternative_id": LFM_ID,
            "fallback_id": FALLBACK_ID,
            "license": "Apache 2.0",
            "params": "30B (Glimmer) / 8B (LFM) / 0.5B (fallback)",
            "role": "Frozen foundation for local agents",
        },
        "harness": {
            "Online-LoRA+": "shift detect + importance reg + adapter updates",
            "GRPO-R1": "group relative policy opt on verified rewards",
            "Tree-Filtered": "isolated adapter banks + hard filter",
        },
        "safety": [
            "base weights stay frozen",
            "only LoRA / banks train",
            "deterministic verifier for promote",
            "E2B sandbox for safe code execution",
            "holdout never in training signal",
            "rollback on holdout regression",
            "LR never scaled by wall-clock time",
        ],
        "external_services": {
            "E2B": "Isolated cloud micro-VMs for code execution",
            "Groq": "High-speed teacher traces and distillation",
            "HuggingFace": "Optional checkpoint synchronization",
        },
        "run": {
            "simulation": "python -m src.lab --mode simulation --cycles 40",
            "local_server": "uvicorn src.server:app --host 0.0.0.0 --port 8000",
            "glimmer_infer": "see docs/FUSION.md — Ollama / vLLM / transformers 4-bit",
            "unified": "python main.py --full-pipeline",
        },
    }
