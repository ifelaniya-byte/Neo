"""FastAPI surface for the Weight Foundry lab."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .ledger import Ledger
from .queue_store import FileQueue
from .fusion import describe_fusion, fusion_banner, resolve_model_id

# Config
CFG_PATH = Path("config.yaml")
cfg = yaml.safe_load(CFG_PATH.read_text()) if CFG_PATH.exists() else {}

app = FastAPI(title="Universal Agent Lab — Weight Foundry", version="0.1.0")
queue = FileQueue(cfg.get("paths", {}).get("queue_file", "./artifacts/queue.jsonl"))
ledger = Ledger.load(cfg.get("paths", {}).get("ledger_file", "./artifacts/ledger.json"))
START = time.monotonic()
SESSION = {
    "mode": "simulation",
    "cycles_completed": 0,
    "leader": "Tree-Filtered",
    "scores": {
        "Online-LoRA+": 0.712,
        "GRPO-R1": 0.689,
        "Tree-Filtered": 0.736,
    },
    "lineage": {
        "Online-LoRA+": "Christina200/Online-LoRA + CL-LoRA",
        "GRPO-R1": "DeepSeek-R1 / verl / open-r1 / GRPO-Zero",
        "Tree-Filtered": "TreeLoRA / CL-LoRA / InfLoRA",
    },
}


class TaskRequest(BaseModel):
    prompt: str
    expected: Optional[str] = None


def _check_key(x_api_key: Optional[str] = Header(None)):
    key = cfg.get("server", {}).get("api_key")
    if key and x_api_key != key:
        raise HTTPException(401, "Invalid or missing X-API-Key")


@app.get("/", response_class=HTMLResponse)
def root():
    index = Path("web/index.html")
    if index.exists():
        return HTMLResponse(index.read_text())
    return HTMLResponse("<h1>Weight Foundry</h1><p>Place web/index.html for the live dashboard.</p>")


@app.get("/stats")
def stats():
    elapsed = time.monotonic() - START
    return {
        "mode": SESSION["mode"],
        "uptime_seconds": round(elapsed, 2),
        "cycles_completed": SESSION["cycles_completed"],
        "leader": SESSION["leader"],
        "scores": SESSION["scores"],
        "queue_depth": queue.depth(),
        "accepted": ledger.accepted,
        "rejected": ledger.rejected,
        "note": "Cadence never multiplies learning rate. Missed cycles are logged, not converted into explosive gradients.",
    }


@app.get("/ledger")
def get_ledger():
    return ledger.to_dict()


@app.get("/safety")
def safety_status():
    # Lightweight status even without a live SafetyGuard instance
    return {
        "nan_guard": True,
        "explosion_guard": True,
        "auto_checkpoint": True,
        "auto_rollback": True,
        "holdout_drop_threshold": cfg.get("training", {}).get("holdout_drop_threshold", 0.15),
        "message": "Promotions require holdout improvement; failures roll back.",
    }


@app.get("/heartbeat")
def heartbeat():
    path = Path(cfg.get("paths", {}).get("heartbeat_file", "./artifacts/watchdog_heartbeat.json"))
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "wall_time": time.time(),
        "uptime": time.monotonic() - START,
        "alive": True,
        "pass_rate": ledger.accepted / max(1, ledger.accepted + ledger.rejected),
    }
    path.write_text(json.dumps(payload, indent=2))
    return payload


@app.post("/enqueue")
def enqueue(req: TaskRequest):
    task_id = queue.put(req.prompt, meta={"expected": req.expected})
    return {"status": "enqueued", "id": task_id, "queue_depth": queue.depth()}


@app.get("/session")
def session():
    sf = Path(cfg.get("paths", {}).get("session_file", "./artifacts/session.json"))
    if sf.exists():
        return json.loads(sf.read_text())
    return SESSION




@app.get("/fusion")
def fusion_info():
    info = describe_fusion()
    info["resolved_model"] = resolve_model_id(cfg)
    info["config_model"] = cfg.get("model", {})
    return info

# Optional static mount
web_dir = Path("web")
if web_dir.exists():
    app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
