# GPU Lane — how the King gets free hours into this sandbox

This sandbox has **no GPU**. You sign up elsewhere. Then you paste a secret.

KP-14: treat Kaggle as a **batch lab** on one identity. 70B is not a T4 job.

## Do this first (10 minutes)

1. Create a Hugging Face account: https://huggingface.co/join
2. Make a **Read** token: https://huggingface.co/settings/tokens
3. Put it in this environment as `HF_TOKEN`.
4. Re-run the council. We already proved the router lists Kimi K3, GLM 5.2,
   DeepSeek V4 Pro, Qwen 3.8 Max, Apertus 70B Instruct — we got **401** without a token.

## Free GPU hours (if you want a real card, not just hosted inference)

### Hugging Face token (do this first)
- URL: https://huggingface.co/settings/tokens
- Cost: free, no card
- Hours: rate-limited serverless / Inference Providers, not a reserved GPU
- What: Create a READ token. This sandbox already reached the router (131 models, 401 without auth).
- Env var we read: `HF_TOKEN`

### Kaggle Notebooks GPU
- URL: https://www.kaggle.com/code
- Cost: free, no card
- Hours: ~30 h/week T4 16GB
- What: Guaranteed ~30 GPU hours/week on T4/P100, 9-hour sessions. More reliable than Colab.
- Env var we read: `GPU_ENDPOINT (after you run gpu_worker.py with Gradio share)`

### Google Colab free GPU
- URL: https://colab.research.google.com
- Cost: free, no card
- Hours: ~15–30 h/week T4 16GB
- What: 15–30 h/week T4, 12-hour sessions. Throttles at peak. Complement to Kaggle.
- Env var we read: `GPU_ENDPOINT`

### Lightning AI Studio
- URL: https://lightning.ai
- Cost: free tier, phone verify
- Hours: ~80 h/month (verify current quota in-app)
- What: Persistent VS Code cloud. Reported ~80 GPU hours/month on the free plan.
- Env var we read: `GPU_ENDPOINT`

### Hugging Face ZeroGPU Space
- URL: https://huggingface.co/new-space
- Cost: free daily seconds; Pro $9 unlocks more / easier hosting
- Hours: seconds/day on free; minutes/day on Pro
- What: Time-sliced A100/H200. Host gpu_worker as a Gradio Space, then we call the public URL.
- Env var we read: `GPU_ENDPOINT`

### RunPod signup credit
- URL: https://www.runpod.io
- Cost: ~$10 one-time credit (card often required)
- Hours: ~3–30 h depending on GPU
- What: A few hours of a real H100/4090 if you need one 70B Q4 smoke test.
- Env var we read: `GPU_ENDPOINT`

## What fits where (honesty)

- **Free T4 16GB (Colab/Kaggle):** smollm3-3b, phi-4, falcon-h1r-7b, granite-4.1, gpt-oss-20b, liquid-lfm2.5, mellum-2, laguna-xs-2.1, gemma-4-31b
- **Need hosted inference or a rented 70B+ box:** kimi-k3, qwen-3.8-max, apertus-70b, glm-5.2, glm-5.5, deepseek-v4-pro, llama-5, inkling, qwen3.5-397b
- A rumored 1T GLM-5.5 will **not** load on a free T4. Day-1 for 5.5 is hosted inference or a paid H100.

## Worker

Upload `gpu_worker.py` to Colab or Kaggle, run it, copy the public Gradio URL,
set `GPU_ENDPOINT` to that URL. The council will POST prompts to `/run`.

## This session

- HF_TOKEN present: **False**
- GPU_ENDPOINT: `none`
- Ready: **False**
- Next: Paste HF_TOKEN into the environment (huggingface.co/settings/tokens). That is the shortest path. For actual GPU hours, sign up at Kaggle + Colab, run gpu_worker.py, and set GPU_ENDPOINT to the public Gradio URL.

### Chat attempt

```
{
  "ok": false,
  "status": null,
  "note": "no HF_TOKEN in environment"
}
```

