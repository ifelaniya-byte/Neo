#!/usr/bin/env python3
"""
Claw OS – Headless (no GUI) version
Usage:
  python claw_os_headless.py --folder /path/to/inbox --watch
  python claw_os_headless.py --folder /path/to/inbox --once
"""

import argparse
import os
import sys
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from collections import defaultdict

from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    import tweepy
except ImportError:
    print("tweepy required. pip install tweepy")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger("ClawOS-Headless")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
ALLOWED_EXTS = IMAGE_EXTS | VIDEO_EXTS
GROUP_WINDOW_SECONDS = 8  # multi-image grouping window


class ClawAIAgent:
    def __init__(self, provider: str = "openai"):
        self.provider = provider.lower()
        if self.provider == "openai":
            if OpenAI is None:
                raise RuntimeError("openai package missing")
            key = os.getenv("OPENAI_API_KEY")
            if not key or key.startswith("sk-your"):
                raise RuntimeError("OPENAI_API_KEY missing or placeholder")
            self.client = OpenAI(api_key=key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            logger.info(f"AI → OpenAI ({self.model})")
        elif self.provider == "ollama":
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            logger.info(f"AI → Ollama ({self.model})")
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
            "You are Claw, a sharp social-media AI. "
            "Write one short engaging X/Twitter caption. "
            "Under 220 characters. Energetic, natural, 2-4 hashtags. "
            "No surrounding quotes."
        )
        user = f"Files: {', '.join(names)}\nType: {media_type}\nTotal size: {size_mb:.1f} MB\nGenerate caption."

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
            return caption
        except Exception as e:
            logger.warning(f"LLM fallback: {e}")
            return f"🚀 Fresh {media_type} via Claw OS\n{', '.join(names[:3])}\n#ClawOS #AI #Automation"


class TwitterUploader:
    def __init__(self):
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
            raise RuntimeError(f"Missing Twitter credentials: {missing}")

        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
        self.client_v2 = tweepy.Client(
            bearer_token=bearer, consumer_key=api_key, consumer_secret=api_secret,
            access_token=access_token, access_token_secret=access_secret,
            wait_on_rate_limit=True,
        )
        logger.info("X API clients ready")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=4, max=30),
           retry=retry_if_exception_type(Exception), reraise=True)
    def upload_and_tweet(self, file_paths: List[str], caption: str) -> Optional[str]:
        media_ids = []
        for fp in file_paths[:4]:  # X hard limit
            cat = "tweet_video" if Path(fp).suffix.lower() in VIDEO_EXTS else "tweet_image"
            logger.info(f"Uploading {Path(fp).name} ({cat})")
            media = self.api_v1.media_upload(filename=fp, chunked=True, media_category=cat)
            media_ids.append(media.media_id_string)
        response = self.client_v2.create_tweet(text=caption, media_ids=media_ids)
        tweet_id = response.data["id"]
        logger.info(f"✅ Posted https://x.com/i/status/{tweet_id}")
        return tweet_id


class ClawFolderWatcher(FileSystemEventHandler):
    def __init__(self, agent, uploader, processed_dir: Path):
        self.agent = agent
        self.uploader = uploader
        self.processed_dir = processed_dir
        self.pending: Dict[float, List[str]] = defaultdict(list)
        self._lock_files = set()

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
        if str(path) in self._lock_files:
            return
        self._lock_files.add(str(path))
        # simple time-bucket grouping for multi-image
        bucket = time.time() // GROUP_WINDOW_SECONDS
        self.pending[bucket].append(str(path))
        # schedule processing after window
        import threading
        threading.Timer(GROUP_WINDOW_SECONDS + 0.5, self._process_bucket, args=(bucket,)).start()

    def _process_bucket(self, bucket: float):
        files = self.pending.pop(bucket, [])
        if not files:
            return
        # wait for stability
        stable = []
        for f in files:
            p = Path(f)
            if self._wait_stable(p):
                stable.append(f)
        if not stable:
            return
        # videos never group with others
        videos = [f for f in stable if Path(f).suffix.lower() in VIDEO_EXTS]
        images = [f for f in stable if Path(f).suffix.lower() in IMAGE_EXTS]
        groups = [[v] for v in videos]
        if images:
            groups.append(images[:4])
        for group in groups:
            try:
                caption = self.agent.generate_caption(group)
                tid = self.uploader.upload_and_tweet(group, caption)
                if tid:
                    for f in group:
                        self._archive(f)
            except Exception as e:
                logger.exception(f"Failed group {group}: {e}")
            finally:
                for f in group:
                    self._lock_files.discard(f)

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


def process_existing(folder: Path, agent, uploader, processed: Path):
    files = [p for p in folder.iterdir()
             if p.is_file() and p.suffix.lower() in ALLOWED_EXTS and not p.name.startswith(".")]
    if not files:
        logger.info("No media files found.")
        return
    # simple: process images as one group (max 4), videos individually
    images = [str(p) for p in files if p.suffix.lower() in IMAGE_EXTS][:4]
    videos = [str(p) for p in files if p.suffix.lower() in VIDEO_EXTS]
    for group in ([images] if images else []) + [[v] for v in videos]:
        try:
            caption = agent.generate_caption(group)
            tid = uploader.upload_and_tweet(group, caption)
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


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Claw OS Headless")
    parser.add_argument("--folder", "-f", required=True, help="Folder to watch / process")
    parser.add_argument("--once", action="store_true", help="Process existing files then exit")
    parser.add_argument("--watch", action="store_true", help="Watch continuously (default if not --once)")
    args = parser.parse_args()

    folder = Path(args.folder).resolve()
    if not folder.is_dir():
        logger.error(f"Not a directory: {folder}")
        sys.exit(1)

    processed = folder / "processed"
    processed.mkdir(exist_ok=True)

    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    agent = ClawAIAgent(provider)
    uploader = TwitterUploader()

    if args.once or not args.watch:
        logger.info("One-shot mode")
        process_existing(folder, agent, uploader, processed)
        return

    logger.info(f"Watching {folder}")
    handler = ClawFolderWatcher(agent, uploader, processed)
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    logger.info("Stopped")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    main()
