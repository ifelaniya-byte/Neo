# Claw OS v2 – Obsidian Edition

**One-click media → AI caption → X/Twitter**

## What is included

- **claw_os.py** – Full GUI with glossy Obsidian dark mode + multi-image albums
- **claw_os_headless.py** – Pure CLI / server version
- **docker/** – Dockerfile + docker-compose
- **systemd/** – Background service unit
- **docs/MANUAL.md** – Complete user manual
- **docs/AI_HELP_GUIDE.md** – Help guide written for AI assistants
- **docs/RECURSIVE_AI_HELP.md** – Layered recursive help for when AIs get stuck
- **.env.example** – Credential template
- **requirements.txt**

## Quick Start (GUI)

```bash
cd claw_os
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# → edit .env with your real keys
python claw_os.py
```

1. Click **Browse…** and choose any folder  
2. Click **▶ Start Pipeline**  
3. Drop images or videos → automatic caption + post to X  
4. Successfully posted files move into `processed/`

## Headless

```bash
python claw_os_headless.py --folder /path/to/inbox --watch
python claw_os_headless.py --folder /path/to/inbox --once
```

## Docker

```bash
cd docker
# edit docker-compose.yml to point to your media folder
docker compose up -d
```

## Systemd (Linux)

See `systemd/claw-os.service` and the full manual.

## Features

- Obsidian Luxury dark theme (deep black, muted gold accents, high-end look)
- Multi-image grouping (drop several images within ~8 s → one album tweet, max 4)
- OpenAI or local Ollama captions
- Chunked media upload
- Automatic archive to `processed/`
- Retries + solid logging
- Full documentation + AI-oriented help guides

## Important Notes

- X free tier is almost never enough for media posting. A paid plan is required.
- Keep the GUI open while the pipeline runs.
- Never commit your real `.env` file.

## Documentation

- `docs/MANUAL.md` – full user manual
- `docs/AI_HELP_GUIDE.md` – for AI assistants
- `docs/RECURSIVE_AI_HELP.md` – recursive recovery guide

Enjoy.
