"""Stage 1: scan the media pool, build proxies, classify items."""
from __future__ import annotations

import logging
from pathlib import Path

from src.core.project import MediaItem, TrailerProject
from src.services.ffmpeg_service import make_proxy, probe_duration
from src.utils.config import AppConfig

log = logging.getLogger(__name__)

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".flac"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}


def _classify(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in VIDEO_EXT:
        return "video"
    if ext in AUDIO_EXT:
        return "audio"
    if ext in IMAGE_EXT:
        return "image"
    return "unknown"


def run(cfg: AppConfig, project: TrailerProject, state: dict) -> dict:
    base = project.source_dir or project.root
    items: list[MediaItem] = []

    for path in base.rglob("*"):
        if not path.is_file():
            continue
        kind = _classify(path)
        if kind == "unknown":
            continue
        duration = probe_duration(path) if kind != "image" else 0.0
        items.append(MediaItem(path=path, kind=kind, duration_s=duration))

    log.info("ingested %d media items from %s", len(items), base)
    state["media"] = items

    if cfg.pipeline.ingest.proxy_height and any(i.kind == "video" for i in items):
        proxy_dir = Path(cfg.app.cache_dir) / "proxies"
        proxy_dir.mkdir(parents=True, exist_ok=True)
        for item in items:
            if item.kind == "video":
                item.tags.append(str(make_proxy(item.path, proxy_dir, cfg.pipeline.ingest.proxy_height)))

    return state