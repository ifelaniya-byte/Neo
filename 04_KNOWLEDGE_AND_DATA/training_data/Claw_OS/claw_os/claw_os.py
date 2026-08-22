#!/usr/bin/env python3
"""
Claw OS v2 – One-Click Media → X Pipeline
=========================================
• Obsidian Luxury Dark Mode GUI
• Multi-image album support
• Real AI captions (OpenAI / Ollama)
• Chunked upload + automatic archive
"""

import os
import sys
import time
import shutil
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from collections import defaultdict

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    import tweepy
except ImportError:
    tweepy = None
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    import requests
except ImportError:
    requests = None

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("ClawOS")

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.see(tk.END)
            self.text_widget.configure(state="disabled")
        try:
            self.text_widget.after(0, append)
        except Exception:
            pass

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_EXTS = IMAGE_EXTS | VIDEO_EXTS
GROUP_WINDOW_SECONDS = 8

OBSIDIAN = {
    "bg": "#0a0a0c",
    "bg2": "#121216",
    "bg3": "#1a1a20",
    "fg": "#e8e6e3",
    "fg_dim": "#9a9690",
    "accent": "#c9a227",
    "accent_hover": "#e0b83a",
    "border": "#2a2a32",
    "success": "#4ade80",
    "error": "#f87171",
    "log_bg": "#08080a",
    "button_bg": "#1e1e26",
    "button_fg": "#e8e6e3",
}

class ClawAIAgent:
    def __init__(self, provider: str = "openai"):
        self.provider = provider.lower()
        if self.provider == "openai":
            if OpenAI is None:
                raise RuntimeError("openai package not installed")
            key = os.getenv("OPENAI_API_KEY")
            if not key or key.startswith("sk-your"):
                raise RuntimeError("OPENAI_API_KEY not set or still placeholder")
            self.client = OpenAI(api_key=key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            logger.info(f"AI Agent → OpenAI ({self.model})")
        elif self.provider == "ollama":
            if requests is None:
                raise RuntimeError("requests required for Ollama")
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
            r = requests.get(f"{self.base_url}/api/tags", timeout=4)
            r.raise_for_status()
            logger.info(f"AI Agent → Ollama ({self.model})")
        else:
            raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

    def generate_caption(self, file_paths: List[str]) -> str:
        names = [Path(p).name for p in file_paths]
        is_multi = len(file_paths) > 1
        media_type = "album" if is_multi else (
            "video" if Path(file_paths[0]).suffix.lower() in VIDEO_EXTS else "image"
        )
        size_mb = sum(Path(p).stat().st_size for p in file_paths) / (1024 * 1024)
        system = (
            "You are Claw, a sharp social-media AI agent. "
            "Write a short, engaging X/Twitter caption. "
            "Keep under 220 characters. Be energetic and natural. "
            "Include 2-4 relevant hashtags. Do not wrap the whole caption in quotes."
        )
        user = (
            f"Files: {', '.join(names)}\n"
            f"Type: {media_type}\n"
            f"Total size: {size_mb:.1f} MB\n\n"
            "Generate one optimized caption."
        )
        try:
            if self.provider == "openai":
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}],
                    max_tokens=120, temperature=0.8,
                )
                caption = resp.choices[0].message.content.strip()
            else:
                payload = {
                    "model": self.model,
                    "messages": [{"role": "system", "content": system},
                                 {"role": "user", "content": user}],
                    "stream": False, "options": {"temperature": 0.8},
                }
                r = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=60)
                r.raise_for_status()
                caption = r.json()["message"]["content"].strip()
            if len(caption) > 270:
                caption = caption[:267] + "..."
            logger.info(f"Caption: {caption[:70]}...")
            return caption
        except Exception as e:
            logger.warning(f"LLM failed ({e}) – using fallback")
            return (
                f"🚀 Fresh {media_type} via Claw OS\n"
                f"{', '.join(names[:3])}\n#ClawOS #AI #Automation"
            )

class TwitterUploader:
    def __init__(self):
        if tweepy is None:
            raise RuntimeError("tweepy not installed")
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        bearer = os.getenv("TWITTER_BEARER_TOKEN")
        missing = [k for k, v in {
            "TWITTER_API_KEY": api_key, "TWITTER_API_SECRET": api_secret,
            "TWITTER_ACCESS_TOKEN": access_token, "TWITTER_ACCESS_SECRET": access_secret,
            "TWITTER_BEARER_TOKEN": bearer,
        }.items() if not v or str(v).startswith("your_")]
        if missing:
            raise RuntimeError(f"Missing/placeholder Twitter credentials: {', '.join(missing)}")
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
        self.client_v2 = tweepy.Client(
            bearer_token=bearer, consumer_key=api_key, consumer_secret=api_secret,
            access_token=access_token, access_token_secret=access_secret,
            wait_on_rate_limit=True,
        )
        logger.info("X / Twitter API ready")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30),
           retry=retry_if_exception_type(Exception), reraise=True)
    def upload_and_tweet(self, file_paths: List[str], caption: str) -> Optional[str]:
        media_ids = []
        for fp in file_paths[:4]:
            cat = "tweet_video" if Path(fp).suffix.lower() in VIDEO_EXTS else "tweet_image"
            logger.info(f"Uploading {Path(fp).name}")
            media = self.api_v1.media_upload(filename=fp, chunked=True, media_category=cat)
            media_ids.append(media.media_id_string)
        response = self.client_v2.create_tweet(text=caption, media_ids=media_ids)
        tweet_id = response.data["id"]
        logger.info(f"✅ Tweet live → https://x.com/i/status/{tweet_id}")
        return tweet_id

class ClawFolderWatcher(FileSystemEventHandler):
    def __init__(self, agent, uploader, processed_dir: Path, gui_callback=None):
        self.agent = agent
        self.uploader = uploader
        self.processed_dir = processed_dir
        self.gui_callback = gui_callback
        self.pending: Dict[int, List[str]] = defaultdict(list)
        self._processing = set()

    def on_created(self, event):
        if not event.is_directory:
            self._queue(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._queue(event.dest_path)

    def _queue(self, file_path: str):
        path = Path(file_path)
        if path.suffix.lower() not in ALLOWED_EXTS:
            return
        if path.name.startswith(".") or path.name.endswith((".tmp", ".part", ".crdownload")):
            return
        if str(path) in self._processing:
            return
        self._processing.add(str(path))
        bucket = int(time.time() // GROUP_WINDOW_SECONDS)
        self.pending[bucket].append(str(path))
        threading.Timer(GROUP_WINDOW_SECONDS + 0.8, self._flush, args=(bucket,)).start()

    def _flush(self, bucket: int):
        files = self.pending.pop(bucket, [])
        if not files:
            return
        stable = []
        for f in files:
            if self._wait_stable(Path(f)):
                stable.append(f)
        if not stable:
            for f in files:
                self._processing.discard(f)
            return
        videos = [f for f in stable if Path(f).suffix.lower() in VIDEO_EXTS]
        images = [f for f in stable if Path(f).suffix.lower() in IMAGE_EXTS]
        groups = [[v] for v in videos]
        if images:
            groups.append(images[:4])
        for group in groups:
            try:
                logger.info(f"Processing group: {[Path(g).name for g in group]}")
                caption = self.agent.generate_caption(group)
                tid = self.uploader.upload_and_tweet(group, caption)
                if tid:
                    for f in group:
                        self._archive(f)
                    if self.gui_callback:
                        self.gui_callback(f"✅ Posted album/file(s)")
            except Exception as e:
                logger.exception(e)
                if self.gui_callback:
                    self.gui_callback(f"❌ Error: {e}")
            finally:
                for f in group:
                    self._processing.discard(f)

    def _wait_stable(self, path: Path, timeout=30.0, interval=0.5) -> bool:
        start = time.time()
        last = -1
        while time.time() - start < timeout:
            try:
                size = path.stat().st_size
                if size == last and size > 0:
                    return True
                last = size
            except FileNotFoundError:
                return False
            time.sleep(interval)
        return path.exists()

    def _archive(self, file_path: str):
        path = Path(file_path)
        dest = self.processed_dir / path.name
        if dest.exists():
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = self.processed_dir / f"{path.stem}_{stamp}{path.suffix}"
        shutil.move(str(path), str(dest))
        logger.info(f"Archived → {dest.name}")

class ClawOSApp:
    def __init__(self):
        load_dotenv()
        self.root = tk.Tk()
        self.root.title("Claw OS  •  Obsidian")
        self.root.geometry("780x620")
        self.root.minsize(680, 520)
        self.root.configure(bg=OBSIDIAN["bg"])
        self.watch_folder: Optional[Path] = None
        self.observer: Optional[Observer] = None
        self.agent = None
        self.uploader = None
        self.is_running = False
        self._apply_obsidian_theme()
        self._build_ui()
        self._setup_logging()

    def _apply_obsidian_theme(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", background=OBSIDIAN["bg"], foreground=OBSIDIAN["fg"],
                        fieldbackground=OBSIDIAN["bg2"], bordercolor=OBSIDIAN["border"],
                        troughcolor=OBSIDIAN["bg2"])
        style.configure("TFrame", background=OBSIDIAN["bg"])
        style.configure("TLabel", background=OBSIDIAN["bg"], foreground=OBSIDIAN["fg"])
        style.configure("TLabelframe", background=OBSIDIAN["bg"], foreground=OBSIDIAN["accent"])
        style.configure("TLabelframe.Label", background=OBSIDIAN["bg"],
                        foreground=OBSIDIAN["accent"], font=("Segoe UI", 10, "bold"))
        style.configure("TButton", background=OBSIDIAN["button_bg"], foreground=OBSIDIAN["button_fg"],
                        bordercolor=OBSIDIAN["border"], focusthickness=0, padding=8)
        style.map("TButton",
                  background=[("active", OBSIDIAN["accent"]), ("pressed", OBSIDIAN["accent_hover"])],
                  foreground=[("active", "#0a0a0c"), ("pressed", "#0a0a0c")])
        style.configure("Accent.TButton", background=OBSIDIAN["accent"], foreground="#0a0a0c",
                        font=("Segoe UI", 10, "bold"), padding=10)
        style.map("Accent.TButton",
                  background=[("active", OBSIDIAN["accent_hover"]), ("pressed", "#f0d060")])
        style.configure("Stop.TButton", background="#3a1a1a", foreground=OBSIDIAN["error"])
        style.map("Stop.TButton", background=[("active", "#5a2a2a")])

    def _build_ui(self):
        header = tk.Frame(self.root, bg=OBSIDIAN["bg"], pady=14)
        header.pack(fill=tk.X, padx=16)
        title = tk.Label(header, text="CLAW OS", font=("Segoe UI", 22, "bold"),
                         bg=OBSIDIAN["bg"], fg=OBSIDIAN["accent"])
        title.pack(side=tk.LEFT)
        subtitle = tk.Label(header, text="  Obsidian Edition  •  Media → X",
                            font=("Segoe UI", 10), bg=OBSIDIAN["bg"], fg=OBSIDIAN["fg_dim"])
        subtitle.pack(side=tk.LEFT, pady=6)

        folder_card = tk.Frame(self.root, bg=OBSIDIAN["bg2"], highlightbackground=OBSIDIAN["border"],
                               highlightthickness=1, padx=12, pady=10)
        folder_card.pack(fill=tk.X, padx=16, pady=8)
        tk.Label(folder_card, text="SELECT FOLDER", font=("Segoe UI", 8, "bold"),
                 bg=OBSIDIAN["bg2"], fg=OBSIDIAN["accent"]).pack(anchor=tk.W)
        row = tk.Frame(folder_card, bg=OBSIDIAN["bg2"])
        row.pack(fill=tk.X, pady=4)
        self.folder_var = tk.StringVar(value="No folder selected")
        tk.Label(row, textvariable=self.folder_var, font=("Segoe UI", 10),
                 bg=OBSIDIAN["bg2"], fg=OBSIDIAN["fg"], wraplength=520, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Browse…", command=self.select_folder).pack(side=tk.RIGHT)

        ctrl = tk.Frame(self.root, bg=OBSIDIAN["bg"], pady=6)
        ctrl.pack(fill=tk.X, padx=16)
        self.start_btn = ttk.Button(ctrl, text="▶  Start Pipeline", style="Accent.TButton",
                                    command=self.start_pipeline)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.stop_btn = ttk.Button(ctrl, text="⏹  Stop", style="Stop.TButton",
                                   command=self.stop_pipeline, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl, text="Process existing files", command=self.process_existing).pack(side=tk.LEFT, padx=12)

        self.status_var = tk.StringVar(value="Ready — select a folder and press Start")
        tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 9),
                 bg=OBSIDIAN["bg"], fg=OBSIDIAN["fg_dim"]).pack(anchor=tk.W, padx=18, pady=4)

        log_frame = tk.Frame(self.root, bg=OBSIDIAN["bg2"], highlightbackground=OBSIDIAN["border"],
                             highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        tk.Label(log_frame, text="ACTIVITY LOG", font=("Segoe UI", 8, "bold"),
                 bg=OBSIDIAN["bg2"], fg=OBSIDIAN["accent"]).pack(anchor=tk.W, padx=8, pady=(6, 2))
        self.log_text = scrolledtext.ScrolledText(
            log_frame, state="disabled", height=16,
            font=("Consolas", 9), wrap=tk.WORD,
            bg=OBSIDIAN["log_bg"], fg=OBSIDIAN["fg"],
            insertbackground=OBSIDIAN["accent"],
            relief=tk.FLAT, borderwidth=0, highlightthickness=0,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        foot = tk.Frame(self.root, bg=OBSIDIAN["bg"], pady=6)
        foot.pack(fill=tk.X, padx=16)
        tk.Label(foot, text="JPG  PNG  GIF  WEBP   •   MP4  MOV  AVI  MKV  WEBM",
                 font=("Segoe UI", 8), bg=OBSIDIAN["bg"], fg=OBSIDIAN["fg_dim"]).pack(side=tk.LEFT)
        tk.Label(foot, text="Processed →  <folder>/processed/",
                 font=("Segoe UI", 8), bg=OBSIDIAN["bg"], fg=OBSIDIAN["fg_dim"]).pack(side=tk.RIGHT)

    def _setup_logging(self):
        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    def select_folder(self):
        path = filedialog.askdirectory(title="Select folder for Claw OS")
        if path:
            self.watch_folder = Path(path)
            self.folder_var.set(str(self.watch_folder))
            self.status_var.set(f"Folder ready: {self.watch_folder.name}")
            logger.info(f"Watch folder → {self.watch_folder}")

    def _init_services(self):
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.agent = ClawAIAgent(provider)
        self.uploader = TwitterUploader()

    def start_pipeline(self):
        if not self.watch_folder or not self.watch_folder.exists():
            messagebox.showwarning("No folder", "Please select a folder first.")
            return
        if self.is_running:
            return
        try:
            self._init_services()
        except Exception as e:
            messagebox.showerror("Configuration Error", str(e))
            logger.error(str(e))
            return
        processed = self.watch_folder / "processed"
        processed.mkdir(exist_ok=True)
        handler = ClawFolderWatcher(self.agent, self.uploader, processed,
                                    gui_callback=lambda m: self.status_var.set(m))
        self.observer = Observer()
        self.observer.schedule(handler, str(self.watch_folder), recursive=False)
        self.observer.start()
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set(f"🟢 Watching  {self.watch_folder.name}")
        logger.info("=== Claw OS pipeline STARTED ===")

    def stop_pipeline(self):
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Stopped")
        logger.info("=== Claw OS pipeline STOPPED ===")

    def process_existing(self):
        if not self.watch_folder or not self.watch_folder.exists():
            messagebox.showwarning("No folder", "Select a folder first.")
            return
        try:
            if not self.agent or not self.uploader:
                self._init_services()
        except Exception as e:
            messagebox.showerror("Configuration Error", str(e))
            return
        processed = self.watch_folder / "processed"
        processed.mkdir(exist_ok=True)
        files = [p for p in self.watch_folder.iterdir()
                 if p.is_file() and p.suffix.lower() in ALLOWED_EXTS and not p.name.startswith(".")]
        if not files:
            messagebox.showinfo("Empty", "No supported media files found.")
            return
        def worker():
            images = [str(p) for p in files if p.suffix.lower() in IMAGE_EXTS][:4]
            videos = [str(p) for p in files if p.suffix.lower() in VIDEO_EXTS]
            groups = ([images] if images else []) + [[v] for v in videos]
            logger.info(f"Processing {len(files)} existing file(s) in {len(groups)} group(s)")
            for group in groups:
                try:
                    caption = self.agent.generate_caption(group)
                    tid = self.uploader.upload_and_tweet(group, caption)
                    if tid:
                        for f in group:
                            src = Path(f)
                            dest = processed / src.name
                            if dest.exists():
                                stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                dest = processed / f"{src.stem}_{stamp}{src.suffix}"
                            shutil.move(str(src), str(dest))
                            logger.info(f"Archived {src.name}")
                except Exception as e:
                    logger.exception(e)
            logger.info("Finished existing files")
            self.status_var.set("Finished processing existing files")
        threading.Thread(target=worker, daemon=True).start()
        self.status_var.set(f"Processing {len(files)} file(s)…")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.is_running:
            self.stop_pipeline()
        self.root.destroy()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    app = ClawOSApp()
    app.run()
