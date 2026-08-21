"""URGENT safety layer — NaN/explosion guards + holdout rollback."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional


@dataclass
class SafetyState:
    best_holdout: float = 0.0
    last_holdout: float = 0.0
    checkpoints_saved: int = 0
    rollbacks: int = 0
    nan_blocks: int = 0
    explosion_blocks: int = 0
    history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class SafetyGuard:
    """
    Wrap every optimizer step.
    - Reject NaN / Inf gradients before step.
    - Reject exploding gradient norms.
    - Evaluate holdout (never trained on).
    - Checkpoint on improvement; rollback on drop > threshold.
    """

    def __init__(
        self,
        checkpoint_dir: str,
        drop_threshold: float = 0.15,
        max_grad_norm: float = 1.0,
        eval_fn: Optional[Callable[[], float]] = None,
    ):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.drop_threshold = drop_threshold
        self.max_grad_norm = max_grad_norm
        self.eval_fn = eval_fn
        self.state = SafetyState()
        self._best_dir = self.checkpoint_dir / "best"
        self._current_dir = self.checkpoint_dir / "current"

    def check_gradients(self, parameters) -> bool:
        """Return True if safe to step. parameters is iterable of tensors or None (sim)."""
        if parameters is None:
            return True  # simulation path has no real grads

        import torch
        total_norm = 0.0
        for p in parameters:
            if p.grad is None:
                continue
            if torch.isnan(p.grad).any() or torch.isinf(p.grad).any():
                self.state.nan_blocks += 1
                return False
            param_norm = p.grad.data.norm(2)
            total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5
        if total_norm > self.max_grad_norm * 10:  # hard explosion
            self.state.explosion_blocks += 1
            return False
        return True

    def after_update(self, model_save_fn: Callable[[Path], None]) -> dict:
        """
        Call after a successful optimizer step.
        model_save_fn(path) should write the current adapter weights.
        """
        report: dict[str, Any] = {"action": "none"}
        if self.eval_fn is None:
            # still checkpoint
            model_save_fn(self._current_dir)
            self.state.checkpoints_saved += 1
            report["action"] = "checkpoint"
            return report

        score = float(self.eval_fn())
        self.state.last_holdout = score
        entry = {"score": score, "best": self.state.best_holdout}
        self.state.history.append(entry)

        if score > self.state.best_holdout:
            self.state.best_holdout = score
            model_save_fn(self._best_dir)
            model_save_fn(self._current_dir)
            self.state.checkpoints_saved += 1
            report["action"] = "promote"
            report["score"] = score
        elif self.state.best_holdout > 0 and (self.state.best_holdout - score) / max(self.state.best_holdout, 1e-8) > self.drop_threshold:
            # regression → rollback (always record action; restore files if present)
            self.state.rollbacks += 1
            report["action"] = "rollback"
            report["score"] = score
            report["best"] = self.state.best_holdout
            if self._best_dir.exists():
                if self._current_dir.exists():
                    shutil.rmtree(self._current_dir)
                shutil.copytree(self._best_dir, self._current_dir)
            else:
                report["warning"] = "best checkpoint missing; rollback recorded without file restore"
        else:
            model_save_fn(self._current_dir)
            report["action"] = "hold"
            report["score"] = score

        return report

    def snapshot(self) -> dict:
        return self.state.to_dict()
