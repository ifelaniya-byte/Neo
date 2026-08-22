# Claw OS – Complete User Manual

**Version 2.0 – Full Package**  
One-click media → AI caption → X/Twitter pipeline with glossy Obsidian dark mode, multi-image support, headless mode, Docker & systemd.

---

## Table of Contents

1. Introduction  
2. System Requirements  
3. Installation  
4. Configuration (.env)  
5. GUI Mode (recommended for most users)  
6. Headless Mode  
7. Multi-Image / Album Posting  
8. Dark Mode (Obsidian Luxury Theme)  
9. Docker Deployment  
10. Systemd Service (Linux background)  
11. Folder Structure & Workflow  
12. Troubleshooting  
13. Advanced Tips  
14. Security Notes  
15. Changelog & Roadmap  

---

## 1. Introduction

Claw OS watches a folder of your choice. When you drop images or videos into it, the AI agent inspects the file(s), writes an optimized caption, uploads the media to X (Twitter) using chunked upload, posts the tweet, and moves the file(s) into a `processed/` subfolder.

You can run it with a beautiful one-click GUI or completely headless from the command line / Docker / systemd.

---

## 2. System Requirements

- Python 3.10 or newer  
- Internet connection (for X API + optional OpenAI)  
- For local AI: Ollama installed and running  
- X/Twitter Developer account with elevated access (paid plan recommended for media)  
- Optional: Docker for containerized runs  

---

## 3. Installation

```bash
cd claw_os
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your real keys
```

---

## 4. Configuration (.env)

Copy `.env.example` → `.env` and fill every value that starts with `your_`.

Key settings:

```
LLM_PROVIDER=openai          # or "ollama"
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# OR for local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
TWITTER_BEARER_TOKEN=...
```

---

## 5. GUI Mode

```bash
python claw_os.py
```

1. Click **Browse…** and select any folder.  
2. Click **▶ Start Pipeline**.  
3. Drop media files → automatic caption + post.  
4. Optional: **Process existing files now**.  

The interface uses the **Obsidian Luxury Dark Theme** (glossy, deep black, subtle metallic highlights, expensive look).

---

## 6. Headless Mode

```bash
python claw_os_headless.py /path/to/your/folder
# or
python claw_os_headless.py --folder /path/to/folder --once   # process existing then exit
python claw_os_headless.py --folder /path/to/folder --watch  # continuous
```

Perfect for servers, cron, or scripts.

---

## 7. Multi-Image / Album Support

- Drop several images within a short time window (default 8 seconds) → Claw groups them into a single tweet with up to 4 images.  
- Videos are always posted individually.  
- Configurable in code or future GUI settings.

---

## 8. Dark Mode (Obsidian Luxury)

The GUI ships with a custom high-end dark theme:

- Deep obsidian background (#0a0a0c)  
- Soft metallic silver accents  
- Subtle gradient buttons with hover glow  
- High-contrast log panel  
- Expensive, quiet, professional aesthetic  

(Further visual polish can be added via the assets/ folder.)

---

## 9. Docker Deployment

```bash
cd docker
docker compose up -d
```

See `docker/Dockerfile` and `docker/docker-compose.yml` for details. Mount your media folder and `.env`.

---

## 10. Systemd Service (Linux)

```bash
sudo cp systemd/claw-os.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now claw-os
```

Runs headless in the background and restarts on failure.

---

## 11. Folder Structure & Workflow

```
SelectedFolder/
├── new_photo.jpg
├── clip.mp4
└── processed/
    ├── new_photo.jpg
    └── clip.mp4
```

Workflow:

```
[You drop file(s)] → Watcher → AI Agent (caption) → X Upload + Tweet → Move to processed/
```

---

## 12. Troubleshooting

| Symptom | Solution |
|---------|----------|
| Missing credentials | Check `.env` – no placeholders |
| Ollama connection refused | Run `ollama serve` and pull the model |
| Rate limit / 403 | Upgrade X API plan |
| File ignored | Check extension and wait for copy to finish |
| GUI looks wrong | Ensure you are on Python 3.10+ with ttk |

---

## 13. Advanced Tips

- Use a dedicated “Claw Inbox” folder on your Desktop.  
- Combine with cloud sync (Dropbox, etc.) for remote drops.  
- For very large videos, increase the stability wait time in the code.  
- Caption style can be customized by editing the system prompt in `ClawAIAgent`.

---

## 14. Security Notes

- Never commit `.env`.  
- Restrict the X app permissions to the minimum required.  
- Run the service under a low-privilege user when using systemd.

---

## 15. Changelog & Roadmap

**v2.0**
- Obsidian dark GUI
- Multi-image grouping
- Headless mode
- Docker + systemd
- Full manuals + AI help guides

**Future**
- Thread posting
- Custom caption templates per folder
- Web dashboard
- Native macOS / Windows installers

---

End of Manual.
