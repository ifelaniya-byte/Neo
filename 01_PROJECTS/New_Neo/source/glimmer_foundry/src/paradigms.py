"""
Weight Foundry paradigms — strongest methods + efficiency core.

Efficiency (real, not LR explosion):
  - Vectorized scoring (one matmul, not Python loops)
  - Hard-example importance sampling (train where error is high)
  - Adaptive skip when delta is below noise floor
  - Shared random banks / preallocated buffers
  - Early plateau detection per method
"""

from __future__ import annotations

from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Vectorized verifier — single matmul for a whole batch
# ---------------------------------------------------------------------------

def score_batch(weights: np.ndarray, data: np.ndarray) -> float:
    """weights (D,) or (G,D); data (N,D) → mean positive-tanh score."""
    # prediction: tanh(data @ w)
    if weights.ndim == 1:
        pred = np.tanh(data @ weights)
        return float(np.mean(pred > 0))
    # group: (G,D)
    pred = np.tanh(data @ weights.T)  # (N,G)
    return pred  # caller aggregates


def score_group(weights_group: np.ndarray, data: np.ndarray) -> np.ndarray:
    """Return (G,) scores for G candidate weight vectors."""
    pred = np.tanh(data @ weights_group.T)  # (N, G)
    return np.mean(pred > 0, axis=0)


def hard_mask(weights: np.ndarray, data: np.ndarray, top_frac: float = 0.5) -> np.ndarray:
    """Keep the hardest fraction of examples (closest to decision boundary / wrong)."""
    pred = np.tanh(data @ weights)
    difficulty = -np.abs(pred)  # near-zero = hard
    k = max(1, int(len(data) * top_frac))
    idx = np.argpartition(difficulty, -k)[-k:]
    return data[idx]


class BaseParadigm:
    name: str = "base"
    short: str = "base"

    def __init__(self, input_dim: int = 8, lr: float = 0.05):
        self.input_dim = input_dim
        self.lr = lr
        self.weights = np.random.randn(input_dim).astype(np.float64)
        self.history: list[float] = []
        self.step_count = 0
        self.skipped = 0
        self.plateau = False
        self._ema_score = 0.5
        self._noise_floor = 0.005  # adaptive skip threshold

    def score(self, test_data: np.ndarray) -> float:
        return score_batch(self.weights, test_data)

    def step(self, test_data: np.ndarray) -> dict[str, Any]:
        raise NotImplementedError

    def _record(self, score: float) -> None:
        self.history.append(score)
        self.step_count += 1
        # Plateau: last 5 scores within noise floor
        if len(self.history) >= 5:
            window = self.history[-5:]
            if max(window) - min(window) < self._noise_floor:
                self.plateau = True
            else:
                self.plateau = False
        self._ema_score = 0.9 * self._ema_score + 0.1 * score

    def should_skip(self) -> bool:
        """Adaptive skip — if plateaued, skip 50% of steps (sample efficiency)."""
        if self.plateau and (self.step_count % 2 == 1):
            self.skipped += 1
            return True
        return False


# ---------------------------------------------------------------------------
# 01  Online-LoRA+
# ---------------------------------------------------------------------------
class OnlineLoRAPlus(BaseParadigm):
    name = "Online-LoRA+"
    short = "OnlineLoRA"

    def __init__(self, input_dim: int = 8, lr: float = 0.03, reg_lambda: float = 0.1):
        super().__init__(input_dim, lr)
        self.base = np.random.randn(input_dim).astype(np.float64)
        self.adapter = np.zeros(input_dim, dtype=np.float64)
        self.importance = np.ones(input_dim, dtype=np.float64)
        self.anchor = self.adapter.copy()
        self.reg_lambda = reg_lambda
        self.loss_ema = 0.5
        self.shift_threshold = 0.08
        self.weights = self.base + self.adapter

    def score(self, test_data: np.ndarray) -> float:
        return score_batch(self.base + self.adapter, test_data)

    def step(self, test_data: np.ndarray) -> dict[str, Any]:
        if self.should_skip():
            current = self.score(test_data)
            self._record(current)
            return {
                "method": self.name, "score": current, "accepted": False,
                "skipped": True, "shift_detected": False, "delta": 0.0,
            }

        # Importance-sample hard examples only (2x sample efficiency)
        hard = hard_mask(self.base + self.adapter, test_data, top_frac=0.5)
        noise = np.random.normal(0, 0.06, size=self.input_dim)
        candidate = self.base + self.adapter + noise
        raw_score = score_batch(candidate, hard)
        full_before = self.score(test_data)
        loss = 1.0 - raw_score

        shift = abs(loss - self.loss_ema)
        self.loss_ema = 0.9 * self.loss_ema + 0.1 * loss
        shift_detected = shift > self.shift_threshold

        accepted = False
        reg_penalty = 0.0
        if shift_detected or raw_score > full_before:
            delta = self.lr * noise / (self.importance + 1e-6)
            reg_penalty = float(
                self.reg_lambda * np.sum(self.importance * (self.adapter - self.anchor) ** 2)
            )
            self.adapter = self.adapter + delta
            self.importance = 0.95 * self.importance + 0.05 * (noise ** 2)
            if raw_score > 0.55:
                self.anchor = self.adapter.copy()
            accepted = True

        current = self.score(test_data)
        self.weights = self.base + self.adapter
        self._record(current)
        return {
            "method": self.name,
            "score": current,
            "accepted": accepted,
            "shift_detected": shift_detected,
            "reg_penalty": reg_penalty,
            "skipped": False,
            "delta": current - full_before,
        }


# ---------------------------------------------------------------------------
# 02  GRPO-R1  — vectorized group
# ---------------------------------------------------------------------------
class GRPOR1(BaseParadigm):
    name = "GRPO-R1"
    short = "GRPO"

    def __init__(
        self,
        input_dim: int = 8,
        lr: float = 0.04,
        group_size: int = 8,
        kl_coef: float = 0.01,
    ):
        super().__init__(input_dim, lr)
        self.group_size = group_size
        self.kl_coef = kl_coef
        self.anchor = self.weights.copy()
        # Preallocate noise buffer
        self._noise_buf = np.empty((group_size, input_dim), dtype=np.float64)

    def step(self, test_data: np.ndarray) -> dict[str, Any]:
        if self.should_skip():
            current = self.score(test_data)
            self._record(current)
            return {
                "method": self.name, "score": current, "accepted": False,
                "skipped": True, "group_mean": current, "delta": 0.0,
            }

        # Vectorized group sample + score in one shot
        self._noise_buf[:] = np.random.normal(0, 0.12, size=self._noise_buf.shape)
        group_w = self.weights + self._noise_buf  # (G, D)
        # Score on hard subset for speed + focus
        hard = hard_mask(self.weights, test_data, top_frac=0.5)
        rewards = score_group(group_w, hard)  # (G,)

        mean_r = float(rewards.mean())
        std_r = float(rewards.std()) + 1e-8
        advantages = (rewards - mean_r) / std_r  # (G,)

        # Vectorized policy gradient
        grad = (advantages[:, None] * self._noise_buf).sum(axis=0)
        kl_pull = self.kl_coef * (self.anchor - self.weights)
        self.weights = self.weights + self.lr * grad + kl_pull

        if self.step_count % 5 == 0:
            self.anchor = self.weights.copy()

        current = self.score(test_data)
        self._record(current)
        return {
            "method": self.name,
            "score": current,
            "group_mean": mean_r,
            "group_best": float(rewards.max()),
            "accepted": True,
            "skipped": False,
            "delta": current - mean_r,
        }


# ---------------------------------------------------------------------------
# 03  Tree-Filtered — vectorized bank probe
# ---------------------------------------------------------------------------
class TreeFilteredAdapter(BaseParadigm):
    name = "Tree-Filtered"
    short = "TreeLoRA"

    def __init__(self, input_dim: int = 8, lr: float = 0.025, n_banks: int = 3):
        super().__init__(input_dim, lr)
        self.base = np.random.randn(input_dim).astype(np.float64)
        self.n_banks = n_banks
        self.banks = np.zeros((n_banks, input_dim), dtype=np.float64)
        self.bank_importance = np.ones(n_banks, dtype=np.float64)
        self.weights = self.base.copy()
        self._noise_buf = np.empty((n_banks, input_dim), dtype=np.float64)

    def _effective(self) -> np.ndarray:
        total = self.bank_importance.sum() + 1e-8
        mix = (self.bank_importance[:, None] / total * self.banks).sum(axis=0)
        return self.base + mix

    def score(self, test_data: np.ndarray) -> float:
        return score_batch(self._effective(), test_data)

    def step(self, test_data: np.ndarray) -> dict[str, Any]:
        if self.should_skip():
            current = self.score(test_data)
            self._record(current)
            return {
                "method": self.name, "score": current, "accepted": False,
                "skipped": True, "routed_bank": -1, "delta": 0.0,
            }

        hard = hard_mask(self._effective(), test_data, top_frac=0.5)
        self._noise_buf[:] = np.random.normal(0, 0.05, size=self._noise_buf.shape)

        # Probe all banks in one vectorized pass
        # candidate_i = base + bank_i + noise_i
        candidates = self.base + self.banks + self._noise_buf  # (B, D)
        bank_scores = score_group(candidates, hard)  # (B,)

        best_idx = int(bank_scores.argmax())
        best_sc = float(bank_scores[best_idx])

        accepted = False
        if best_sc > 0.5:
            self.banks[best_idx] += self.lr * self._noise_buf[best_idx]
            self.bank_importance[best_idx] *= 1.05
            self.bank_importance *= 0.99
            self.bank_importance[best_idx] /= 0.99  # undo decay on winner
            accepted = True

        current = self.score(test_data)
        self.weights = self._effective()
        self._record(current)
        return {
            "method": self.name,
            "score": current,
            "accepted": accepted,
            "routed_bank": best_idx,
            "bank_scores": bank_scores.tolist(),
            "skipped": False,
            "delta": best_sc - 0.5 if accepted else 0.0,
        }


def build_paradigms(cfg: dict) -> list[BaseParadigm]:
    dim = cfg.get("simulation", {}).get("input_dim", 8)
    group = cfg.get("training", {}).get("group_size", 8)
    return [
        OnlineLoRAPlus(input_dim=dim, lr=0.03, reg_lambda=0.1),
        GRPOR1(input_dim=dim, lr=0.04, group_size=group, kl_coef=0.01),
        TreeFilteredAdapter(input_dim=dim, lr=0.025, n_banks=3),
    ]
