# Live Hugging Face router completions

The HF token is **not** stored in this file. Account: `love90`.
This is **hosted Inference Providers**, not a reserved GPU in the sandbox.

## Wave 1 — token worked (HTTP 200)

Prompt: `Name the largest ocean on Earth in one short sentence.`

| Seat | HF id | HTTP | Live text |
|---|---|---|---|
| Phi-4 | `microsoft/phi-4` | 200 | The largest ocean on Earth is the Pacific Ocean. |
| gpt-oss-20b | `openai/gpt-oss-20b` | 200 | *(empty `content`; 38 reasoning tokens — thinking model)* |
| Qwen 3.6 27B | `Qwen/Qwen3.6-27B` | 200 | *(empty `content`; 40 completion tokens, likely think-mode)* |
| **Apertus 70B** | `swiss-ai/Apertus-70B-Instruct-2509` | 200 | The largest ocean on Earth is the Pacific Ocean. |
| **GLM 5.2** | `zai-org/GLM-5.2` | 200 | The largest ocean on Earth is the Pacific Ocean. |
| **Kimi K3** | `moonshotai/Kimi-K3` | 200 | The Pacific Ocean is the *(cut at 40 tokens; 29 reasoning tokens)* |

Phi-4 usage on that call: 18 prompt + 11 completion tokens, estimated cost **$0.0000028**.

## Wave 2 — credits gone (HTTP 402)

A second panel of 8 seats (including DeepSeek V4 Pro and Qwen 3.8 Max) all returned:

```
402 Payment Required
You have depleted your monthly included credits.
Purchase pre-paid credits to continue using Inference Providers.
Alternatively, subscribe to PRO to get 20x more included usage.
```

So: the token is real, the first completions were real weights, and the **free monthly included credit is now empty**.

## What this means

- This sandbox still has **no GPU**.
- The King now has a working HF token path. It burned the free included credits on the first live panel.
- Next spend options: HF Inference Providers prepaid credits, HF PRO (~20× included), or free T4 hours on Kaggle/Colab via `gpu_worker.py` (those do not use this quota).
- **Rotate this token** if the chat log is shared — it was pasted in the clear.

GLM 5.5 is still unreleased. It was not called. It keeps its lab only while its day-1 eval pack stays useful (KP-13).
