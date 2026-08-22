#!/usr/bin/env python3
"""
MCP BRAIN — a minimal, real Model Context Protocol (MCP) server over stdio,
speaking JSON-RPC 2.0 (one JSON document per line).

It exposes our mini-LLM and mini-LFM as callable *tools*, so the Model Council
(client) can invoke the two models through the standard MCP handshake:

    initialize -> notifications/initialized -> tools/list -> tools/call -> exit

Tools exposed:
  ping                       - liveness probe
  sample_continuation        - mini-LLM: sample text continuing a prompt
  score_continuation         - mini-LLM: average character log-probability of text
  recall_fact                - mini-LFM: score all memorized facts for a question
  mutate_text                - evolution ops (extend / reword / trim) powered by mini-LLM

Run:  python3 mcp_brain.py    (talks MCP over stdin/stdout)
"""

import importlib.util
import json
import os
import random
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_llm = _load("minillm", os.path.join(BASE, "mini_llm.py"))
_lfm = _load("minilfm", os.path.join(BASE, "mini_lfm.py"))

# Pre-trained brains (tables are the "weights"; deterministic, no training loop)
LLM_TABLES, LLM_VOCAB = _llm.train(_llm.CORPUS, 3)
LFM_WORD_FACT, LFM_QUESTIONS, LFM_ANSWERS = _lfm.train(_lfm.FACTS)


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------
def _sample_continuation(args):
    rng = random.Random(args.get("seed", 0))
    return _llm.generate(LLM_TABLES, LLM_VOCAB, args.get("n", 60), args.get("temp", 0.8),
                         args.get("text", ""), rng, args.get("max_k", 3))


def _score_continuation(args):
    out = list(args.get("text", ""))
    if not out:
        return {"avg_logprob": 0.0, "chars": 0}
    vals = [_llm.char_log_prob(LLM_TABLES, LLM_VOCAB, out[:i + 1], args.get("max_k", 3))
            for i in range(len(out))]
    return {"avg_logprob": sum(vals) / len(vals), "chars": len(out)}


def _recall_fact(args):
    probs, matched, _hits = _lfm.score(LFM_WORD_FACT, LFM_ANSWERS,
                                       args.get("question", ""), args.get("temp", 0.15))
    order = sorted(range(len(LFM_ANSWERS)), key=lambda i: -probs[i])
    top = order[0]
    return {
        "answer": LFM_ANSWERS[top],
        "confidence": round(probs[top], 4),
        "matched": sorted(matched),
        "ranked": [{"answer": LFM_ANSWERS[i], "p": round(probs[i], 4)}
                   for i in order[:3]],
    }


def _mutate_text(args):
    text, op, seed = args.get("text", ""), args.get("op", "extend"), args.get("seed", 0)
    rng = random.Random(seed)
    n = args.get("n", 120)
    if op == "extend":
        return _llm.generate(LLM_TABLES, LLM_VOCAB, max(len(text) + n, n),
                             0.8, text, rng, 3)
    if op == "reword":
        return _llm.generate(LLM_TABLES, LLM_VOCAB, len(text), 0.4,
                             text[:min(10, len(text))], rng, 3)
    if op == "trim":
        i = text.find(". ")
        return text[:i + 1] if i >= 0 else text[:len(text) // 2]
    return text


def _ping(args):
    return {"pong": True}


TOOLS = {
    "ping":                 {"description": "liveness probe",
                             "handler": _ping},
    "sample_continuation":  {"description": "mini-LLM: sample text continuing a prompt",
                             "handler": _sample_continuation},
    "score_continuation":   {"description": "mini-LLM: avg char log-probability of text",
                             "handler": _score_continuation},
    "recall_fact":          {"description": "mini-LFM: score memorized facts for a question",
                             "handler": _recall_fact},
    "mutate_text":          {"description": "evolution op: extend | reword | trim",
                             "handler": _mutate_text},
}


def _tool_defs():
    return [{"name": name, "description": info["description"],
             "inputSchema": {"type": "object", "properties": {}, "additionalProperties": True}}
            for name, info in TOOLS.items()]


# ---------------------------------------------------------------------------
# JSON-RPC 2.0 loop (MCP over stdio, line-delimited)
# ---------------------------------------------------------------------------
def serve():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method", "")
        params = msg.get("params") or {}
        msg_id = msg.get("id")

        if method == "initialize":
            result = {"protocolVersion": "2025-06-18",
                      "capabilities": {"tools": {}},
                      "serverInfo": {"name": "mcp-brain", "version": "1.0.0"}}
        elif method == "notifications/initialized":
            result = None
        elif method == "notifications/exit":
            sys.exit(0)
        elif method == "tools/list":
            result = {"tools": _tool_defs()}
        elif method == "tools/call":
            name = params.get("name")
            args = params.get("arguments") or {}
            if name not in TOOLS:
                result = {"isError": True,
                          "content": [{"type": "text", "text": "unknown tool"}]}
            else:
                try:
                    out = TOOLS[name]["handler"](args)
                except Exception as exc:            # never crash the loop
                    result = {"isError": True,
                              "content": [{"type": "text",
                                           "text": f"handler error: {exc}"}]}
                else:
                    result = {"content": [{"type": "text",
                                           "text": json.dumps(out) if not isinstance(out, str) else out}]}
        elif method == "ping":
            result = {}
        else:
            result = None

        if msg_id is not None:          # notifications carry no id -> no reply
            resp = {"jsonrpc": "2.0", "id": msg_id, "result": result}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    serve()
