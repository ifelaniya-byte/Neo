"""
GlimmerFoundry trainer — Muse Glimmer (or fallback) + continual LoRA path.

Base stays frozen. Only adapters train. Holdout governs promote/rollback.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from .fusion import GLIMMER_ID, LFM_ID, FALLBACK_ID, resolve_model_id, FusionStatus
from .verifier import E2BSandboxVerifier, verify_with_safety_fallback
from .groq_teacher import GroqAugmentedTrainer


class OnlineTrainerDaemon:
    """
    Backend priority:
      1. peft + transformers on Muse Glimmer (4-bit)  — primary fusion path
      2. peft on fallback small model                 — CPU / low VRAM
      3. verl / trl GRPO when installed               — scale-up
      4. simulation                                   — always
    """

    def __init__(self, config: dict):
        self.config = config
        self.mode = config.get("training", {}).get("mode", "all")
        self.model = None
        self.tokenizer = None
        self.optimizer = None
        self.adapters: dict[str, Any] = {}
        self.backend = "simulation"
        self.base_id = resolve_model_id(config)
        self.load_in_4bit = bool(config.get("model", {}).get("load_in_4bit", True))

        # Initialize E2B sandbox verifier
        safety_config = config.get("safety", {})
        self.e2b_verifier = None
        if safety_config.get("e2b_enabled", False):
            e2b_api_key = config.get("external_services", {}).get("e2b_api_key")
            self.e2b_verifier = E2BSandboxVerifier(e2b_api_key)

        # Initialize Groq teacher distillation
        self.groq_trainer = GroqAugmentedTrainer(config)

        self.backend = self._detect_and_init()

    def status(self) -> FusionStatus:
        external = self.config.get("external_services", {})
        safety = self.config.get("safety", {})
        
        return FusionStatus(
            base_model=self.base_id,
            backend=self.backend,
            load_in_4bit=self.load_in_4bit,
            local_only=bool(self.config.get("agent", {}).get("local_only", True)),
            continual_modes=["Online-LoRA+", "GRPO-R1", "Tree-Filtered"],
            e2b_enabled=safety.get("e2b_enabled", False) and self.e2b_verifier and self.e2b_verifier.is_available(),
            groq_enabled=external.get("groq_enabled", False) and self.groq_trainer.is_available(),
            model_variants=[
                self.config.get("model", {}).get("id", GLIMMER_ID),
                self.config.get("model", {}).get("alternative_id", LFM_ID),
                self.config.get("model", {}).get("fallback_id", FALLBACK_ID)
            ],
            message=(
                "GlimmerFoundry ready"
                if self.backend != "simulation"
                else "Simulation mode — install torch/peft/transformers for real Glimmer adapters"
            ),
        )

    def _detect_and_init(self) -> str:
        try:
            import verl  # noqa: F401
            # Prefer peft load first; verl is for GRPO scale jobs
        except ImportError:
            pass

        try:
            import torch
            from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        except ImportError:
            return "simulation"

        mid = self.base_id
        device_map = "auto"
        quant = None
        if self.load_in_4bit:
            try:
                quant = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.bfloat16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
            except Exception:
                quant = None

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                mid, trust_remote_code=self.config.get("model", {}).get("trust_remote_code", True)
            )
            kwargs = {
                "trust_remote_code": True,
                "device_map": device_map,
            }
            if quant is not None:
                kwargs["quantization_config"] = quant
            else:
                kwargs["torch_dtype"] = torch.bfloat16

            base = AutoModelForCausalLM.from_pretrained(mid, **kwargs)
            if quant is not None:
                base = prepare_model_for_kbit_training(base)

            lora_cfg = self.config.get("lora", {})
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=lora_cfg.get("r", 16),
                lora_alpha=lora_cfg.get("alpha", 32),
                target_modules=lora_cfg.get(
                    "target_modules", ["q_proj", "v_proj", "k_proj", "o_proj"]
                ),
                lora_dropout=lora_cfg.get("dropout", 0.05),
            )
            self.model = get_peft_model(base, peft_config)
            self.optimizer = torch.optim.AdamW(
                self.model.parameters(),
                lr=self.config.get("training", {}).get("learning_rate", 2e-4),
            )
            self.adapters["primary"] = self.model
            return "peft-glimmer" if "Glimmer" in mid or "glimmer" in mid.lower() else "peft"
        except Exception as e:
            # Fallback to small model
            if mid != FALLBACK_ID:
                self.base_id = self.config.get("model", {}).get("fallback_id", FALLBACK_ID)
                try:
                    return self._load_fallback()
                except Exception:
                    pass
            self._last_error = str(e)
            return "simulation"

    def _load_fallback(self) -> str:
        import torch
        from peft import LoraConfig, get_peft_model, TaskType
        from transformers import AutoModelForCausalLM, AutoTokenizer

        mid = self.base_id
        self.tokenizer = AutoTokenizer.from_pretrained(mid)
        base = AutoModelForCausalLM.from_pretrained(mid, torch_dtype=torch.float32, device_map="cpu")
        peft_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=8,
            lora_alpha=16,
            target_modules=["q_proj", "v_proj"],
        )
        self.model = get_peft_model(base, peft_config)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=2e-4)
        self.adapters["primary"] = self.model
        return "peft-fallback"

    def process_task(self, prompt: str, expected: Optional[str] = None, use_code_execution: bool = False) -> dict[str, Any]:
        if self.backend == "simulation" or self.model is None:
            return {
                "status": "SIMULATION",
                "backend": self.backend,
                "base_model": self.base_id,
                "message": "Install torch+peft+transformers (+ bitsandbytes for 4-bit Glimmer)",
                "fusion": "GlimmerFoundry",
            }

        from .compressor import compress_prompt
        from .verifier import verify_output_text
        import torch

        # Get teacher signal from Groq if available
        teacher_output = None
        if self.groq_trainer.is_available():
            teacher_output = self.groq_trainer.get_teacher_signal(prompt)

        compressed = compress_prompt(prompt)
        inputs = self.tokenizer(compressed, return_tensors="pt")
        try:
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        except Exception:
            pass

        self.model.eval()
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.config.get("model", {}).get("max_new_tokens", 256),
                do_sample=True,
                temperature=0.7,
            )
        text = self.tokenizer.decode(out[0], skip_special_tokens=True)

        # Enhanced verification with E2B sandbox for code execution tasks
        verification_passed = False
        verification_method = "text_only"
        
        if use_code_execution and self.e2b_verifier and self.e2b_verifier.is_available():
            # Try E2B sandbox verification for code execution
            e2b_result = self.e2b_verifier.verify_code_patch(text)
            verification_passed = e2b_result["passed"]
            verification_method = e2b_result["method"]
            
            if not verification_passed and self.config.get("safety", {}).get("e2b_fallback_to_text", True):
                # Fall back to text verification
                verification_passed = verify_output_text(text, expected)
                verification_method = "text_fallback"
        else:
            # Standard text verification
            verification_passed = verify_output_text(text, expected)

        if not verification_passed:
            return {
                "status": "REJECTED", 
                "text": text, 
                "backend": self.backend, 
                "base_model": self.base_id,
                "verification_method": verification_method,
                "teacher_used": teacher_output is not None
            }

        self.model.train()
        self.optimizer.zero_grad()
        loss = self.model(**inputs, labels=inputs["input_ids"]).loss
        if torch.isnan(loss) or torch.isinf(loss):
            return {"status": "NAN_BLOCKED", "backend": self.backend}
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            self.model.parameters(),
            self.config.get("training", {}).get("max_grad_norm", 1.0),
        )
        self.optimizer.step()
        return {
            "status": "UPDATED",
            "loss": float(loss.item()),
            "text": text,
            "backend": self.backend,
            "base_model": self.base_id,
            "fusion": "GlimmerFoundry",
            "verification_method": verification_method,
            "teacher_used": teacher_output is not None,
        }

    def save_adapter(self, path: str | Path) -> None:
        if self.model is None:
            return
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(path)

    def augmented_training_step(
        self, 
        training_examples: list[tuple[str, str]], 
        use_teacher_augmentation: bool = True,
        use_sandbox_verification: bool = True
    ) -> dict[str, Any]:
        """
        Enhanced training step with Groq teacher augmentation and E2B sandbox verification.
        
        Args:
            training_examples: List of (prompt, expected) tuples
            use_teacher_augmentation: Whether to use Groq teacher for data augmentation
            use_sandbox_verification: Whether to use E2B sandbox for code verification
            
        Returns:
            dict with training results and metrics
        """
        results = {
            "total_examples": len(training_examples),
            "successful_updates": 0,
            "rejected": 0,
            "nan_blocked": 0,
            "verification_methods": [],
            "teacher_augmented": 0,
            "average_loss": 0.0
        }
        
        # Augment training data with Groq teacher if available
        augmented_examples = training_examples
        if use_teacher_augmentation and self.groq_trainer.is_available():
            augmented_examples = self.groq_trainer.augment_training_data(
                training_examples, 
                augmentation_factor=2
            )
            results["teacher_augmented"] = len(augmented_examples) - len(training_examples)
            results["total_examples"] = len(augmented_examples)
        
        losses = []
        
        for prompt, expected in augmented_examples:
            # Determine if this is a code execution task
            is_code_task = any(keyword in prompt.lower() for keyword in ['code', 'function', 'script', 'implement'])
            
            result = self.process_task(
                prompt, 
                expected, 
                use_code_execution=is_code_task and use_sandbox_verification
            )
            
            results["verification_methods"].append(result.get("verification_method", "text_only"))
            
            if result["status"] == "UPDATED":
                results["successful_updates"] += 1
                if "loss" in result:
                    losses.append(result["loss"])
            elif result["status"] == "REJECTED":
                results["rejected"] += 1
            elif result["status"] == "NAN_BLOCKED":
                results["nan_blocked"] += 1
        
        if losses:
            results["average_loss"] = sum(losses) / len(losses)
        
        return results

    def get_external_services_status(self) -> dict[str, Any]:
        """Get status of external services (E2B, Groq, etc.)"""
        return {
            "e2b_available": self.e2b_verifier is not None and self.e2b_verifier.is_available(),
            "groq_available": self.groq_trainer.is_available(),
            "backend": self.backend,
            "base_model": self.base_id,
            "selection_strategy": self.config.get("model", {}).get("selection_strategy", "auto")
        }
