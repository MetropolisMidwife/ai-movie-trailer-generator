"""Stage 6: generate caption track and burn-in subtitles."""
from __future__ import annotations

import logging
from pathlib import Path

from src.core.project import TrailerProject
from src.services.caption_service import build_srt
from src.utils.config import AppConfig

log = logging.getLogger(__name__)


def run(cfg: AppConfig, project: TrailerProject, state: dict) -> dict:
    vo_path = state.get("vo_path")
    if not vo_path:
        log.info("no voiceover, skipping captions")
        return state

    srt_path = Path(cfg.app.cache_dir) / "captions.srt"
    build_srt(
        audio_path=vo_path,
        out_path=srt_path,
        font=cfg.pipeline.caption.font,
        position=cfg.pipeline.caption.position,
    )
    log.info("captions written -> %s", srt_path)
    state["srt_path"] = srt_path
    return state