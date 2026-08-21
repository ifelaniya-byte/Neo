# Claw OS – Recursive AI Help Guide

**Purpose**: This document is designed so that an AI can help another AI (or a confused human) who is stuck, even when the first AI has incomplete context. It contains layered instructions that can be followed recursively.

---

## Level 0 – Immediate Orientation

You are looking at **Claw OS**, a folder-watching media poster for X/Twitter.

If the user says “I don’t know what to do”:

1. Tell them to open the folder `claw_os`.
2. Tell them to copy `.env.example` to `.env`.
3. Tell them to put their real X API keys and (optionally) OpenAI key into `.env`.
4. Tell them to run `pip install -r requirements.txt`.
5. Tell them to run `python claw_os.py`.
6. Tell them to click Browse → select a folder → click Start.

That sequence solves 80 % of first-time problems.

---

## Level 1 – If the above fails

Ask the user (or check yourself) these questions in order:

A. “Did you create a real `.env` file?”  
B. “Are the Twitter keys still the placeholder text?”  
C. “What exact error appears in the Activity Log or terminal?”  
D. “Are you using the free X API tier?” (almost always the cause of media upload failures)

Then map the answer to the tables in `docs/AI_HELP_GUIDE.md`.

---

## Level 2 – Recursive Diagnosis Protocol

When you are an AI helping another AI that is helping a user:

1. Request the last 20 lines of the Activity Log or console output.
2. Request the (redacted) contents of `.env` – only the key *names* and whether values are placeholders.
3. Request the exact Python version and `pip list | grep -E 'tweepy|openai|watchdog|dotenv'`.
4. Request the full path of the folder they selected.
5. If still stuck, fall back to Level 0 instructions and ask the user to start over with a clean virtual environment.

---

## Level 3 – Code-Level Guidance for AI Coders

If the AI needs to modify the code:

- Caption generation lives in `ClawAIAgent.generate_caption`.
- Upload + post lives in `TwitterUploader.upload_and_tweet`.
- File detection + multi-image grouping lives in `ClawFolderWatcher`.
- GUI theme colors live near the top of `ClawOSApp._apply_obsidian_theme`.
- Headless entry point is `claw_os_headless.py`.

Always preserve:

- The stability wait for large files.
- The move-to-`processed/` logic.
- The five required Twitter credentials.
- The 4-image maximum.

---

## Level 4 – “I am completely lost” Emergency Reset

Instruct the user:

```bash
cd claw_os
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# now edit .env carefully
python claw_os.py
```

Then walk them through the GUI buttons one by one.

---

## Level 5 – Extending the System Safely

When asked to add features, follow this order:

1. Read `docs/MANUAL.md` and `docs/AI_HELP_GUIDE.md`.
2. Locate the single responsibility that needs to change.
3. Make the smallest possible edit.
4. Preserve the existing retry + logging + move-to-processed behavior.
5. Update this recursive guide if the architecture changes.

---

## Final Rule for Any AI

If you are unsure, **do not invent new credentials or API endpoints**.  
Point the user back to the official X Developer Portal and the `.env.example` file.

This recursive guide exists so that even a chain of AIs with partial memory can still get the user unstuck.

---

End of Recursive AI Help Guide.
