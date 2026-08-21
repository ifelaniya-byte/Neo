#!/usr/bin/env python3
"""
GPU WORKER — run this on Colab / Kaggle / Lightning / a ZeroGPU Space.

It loads a SMALL real open-weight model that fits a free T4 (default:
HuggingFaceTB/SmolLM3-3B) and serves a /run endpoint plus a Gradio UI
with a public share link. Paste that URL back here as GPU_ENDPOINT.

This file is meant to run WHERE THERE IS A GPU. It will not do much
in the council sandbox (no torch).
"""

import os
import json

MODEL_ID = os.environ.get("WORKER_MODEL", "HuggingFaceTB/SmolLM3-3B")


def load_model():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    kw = {"device_map": "auto"}
    if torch.cuda.is_available():
        kw["torch_dtype"] = torch.float16
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **kw)
    return tok, model


def generate(tok, model, prompt, max_new_tokens=64):
    import torch
    inputs = tok(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        inputs = {k: v.cuda() for k, v in inputs.items()}
    out = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    return tok.decode(out[0], skip_special_tokens=True)


def main():
    print(f"[gpu_worker] loading {MODEL_ID}")
    try:
        import torch
        print(f"[gpu_worker] cuda={torch.cuda.is_available()} "
              f"device={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}")
    except Exception as e:
        print("[gpu_worker] torch missing — you are not on a GPU box:", e)
        print("Open this file in https://colab.research.google.com or https://www.kaggle.com/code")
        return

    tok, model = load_model()

    try:
        import gradio as gr

        def infer(prompt, n):
            return generate(tok, model, prompt, int(n or 64))

        demo = gr.Interface(
            fn=infer,
            inputs=[gr.Textbox(label="prompt"), gr.Number(value=64, label="max_new_tokens")],
            outputs="text",
            title=f"Council GPU worker · {MODEL_ID}",
        )
        # share=True gives a public *.gradio.live URL the sandbox can call
        demo.launch(share=True, server_name="0.0.0.0")
    except Exception as e:
        print("[gpu_worker] gradio launch failed, falling back to one local sample:", e)
        print(generate(tok, model, "Name the largest ocean in one sentence.", 32))


if __name__ == "__main__":
    main()
