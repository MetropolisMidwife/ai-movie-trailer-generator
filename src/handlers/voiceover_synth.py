"""Stage 5: synthesize voiceover from the logline + beat narration."""
from __future__ import annotations

import logging
from pathlib import Path

from src.core.project import TrailerProject
from src.services.tts_service import synthesize_voiceover
from src.utils.config import AppConfig

log = logging.getLogger(__name__)


def run(cfg: AppConfig, project: TrailerProject, state: dict) -> dict:
    beats = state.get("beats", [])
    lines: list[str] = []
    if project.logline:
        lines.append(project.logline)
    for beat, _, _ in beats:
        if beat.name in {"threat_reveal", "title_card"}:
            lines.append(_narrate(project, beat.name))

    vo_path = synthesize_voiceover(
        lines=lines,
        provider=cfg.pipeline.voiceover.provider,
        voice=cfg.pipeline.voiceover.voice,
        pace_wpm=cfg.pipeline.voiceover.pace_wpm,
        out_dir=Path(cfg.app.cache_dir) / "vo",
    )
    log.info("voiceover synthesized -> %s", vo_path)
    state["vo_path"] = vo_path
    return state


def _narrate(project: TrailerProject, beat_name: str) -> str:
    if beat_name == "threat_reveal":
        return f"In a world of {project.genre}, one {project.tone} truth remains."
    return f"{project.title.upper()}"