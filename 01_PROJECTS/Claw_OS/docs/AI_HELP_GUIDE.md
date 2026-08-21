# Claw OS – AI Help Guide

This guide is written specifically so that **any AI assistant** (or human) can quickly understand, diagnose, and extend Claw OS without prior context.

---

## What Claw OS Is

A Python application that:

1. Watches a user-chosen folder for new media files (images + videos).
2. Uses an LLM (OpenAI or Ollama) to generate a short, engaging X/Twitter caption.
3. Uploads the media via Twitter v1.1 chunked API.
4. Posts a tweet via Twitter v2 API with the media attached.
5. Moves successfully posted files into a `processed/` subfolder.

It has two entry points:

- `claw_os.py` → full GUI (Obsidian dark theme)
- `claw_os_headless.py` → pure CLI / server mode

---

## Quick Diagnosis Checklist for AI

When a user says “it doesn’t work”, ask / check in this order:

1. Is Python ≥ 3.10?
2. Has `pip install -r requirements.txt` been run?
3. Does a real `.env` exist (not just `.env.example`)?
4. Are all five Twitter keys filled and not placeholders?
5. Is `LLM_PROVIDER` set correctly and the chosen LLM reachable?
6. Is the selected folder writable?
7. Does the file extension match the allowed list?
8. Is the X API plan high enough for media posting?

---

## Key Classes & Responsibilities

| Class / File              | Responsibility |
|---------------------------|----------------|
| `ClawAIAgent`             | Generates captions (OpenAI or Ollama) |
| `TwitterUploader`         | Chunked media upload + create_tweet |
| `ClawFolderWatcher`       | watchdog event handler + multi-image grouping |
| `ClawOSApp`               | GUI + orchestration |
| `claw_os_headless.py`     | CLI entry point |

---

## Common Failure Modes & Exact Fixes

### “Missing or placeholder Twitter credentials”
→ Open `.env` and replace every `your_…` value with real keys from developer.x.com.

### “Cannot reach Ollama”
→ User must run `ollama serve` and `ollama pull <model>`.

### Rate-limit or 403 on media upload
→ Free X API tier is insufficient. User needs Basic or higher.

### File appears but nothing happens
→ Check extension. Wait for the file to finish copying (stability check). Look at the Activity Log.

### GUI is blank or crashes on start
→ Usually missing `python-dotenv` or tkinter not installed (rare on modern systems).

---

## How to Extend (for AI coding assistants)

- Caption style → edit the `system_prompt` string inside `ClawAIAgent.generate_caption`.
- Add new media type → add extension to `ALLOWED_EXTS` / `IMAGE_EXTS` / `VIDEO_EXTS`.
- Change multi-image window → look for `GROUP_WINDOW_SECONDS` constant.
- Add thread posting → after `create_tweet`, store the tweet ID and reply to it.
- New LLM provider → add a new branch in `ClawAIAgent.__init__` and `generate_caption`.

---

## Safe Places to Edit

- Prompts and temperature
- Allowed file extensions
- Processed folder name
- Logging level
- Retry counts in the `@retry` decorator

Avoid editing the OAuth flow or the core upload sequence unless you fully understand the current X API requirements.

---

## Version & Compatibility Notes

- Built against tweepy ≥ 4.14 and the 2025/2026 X API.
- Media category is set automatically (`tweet_image` vs `tweet_video`).
- Maximum 4 images per tweet (X limit).

---

End of AI Help Guide.
