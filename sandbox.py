#!/usr/bin/env python3
"""Resource-limited runner for non-stationary probes (best-effort pure Python)."""
from __future__ import annotations
import signal
from typing import Any, Callable, Dict, Optional


class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutError("sandbox time limit exceeded")


def run(
    fn: Callable[[], Any],
    timeout_s: float = 2.0,
    max_result_bytes: int = 2_000_000,
) -> Dict[str, Any]:
    """
    Run fn with a SIGALRM time limit (Unix). Memory limits require OS cgroups;
    we only bound wall time and result size serialization estimate.
    """
    try:
        old = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, timeout_s)
        try:
            result = fn()
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old)
        # size bound
        import json
        try:
            size = len(json.dumps(result, default=str))
        except Exception:
            size = -1
        if size > max_result_bytes:
            return {"ok": False, "error": "result_too_large", "size": size}
        return {"ok": True, "result": result, "size": size}
    except TimeoutError as e:
        return {"ok": False, "error": str(e)}
    except Exception as e:
        return {"ok": False, "error": type(e).__name__ + ": " + str(e)}
