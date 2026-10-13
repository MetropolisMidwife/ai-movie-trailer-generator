"""Stage 3: compose the trailer score from a music model + target loudness."""
from __future__ import annotations

import logging
from pathlib import Path

from src.core.project import TrailerProject
from src.core.templates.three_act_teaser import beats_for_duration
from src.services.music_service import generate_score
from src.services.ffmpeg_service import normalize_loudness
from src.utils.config import AppConfig

log = logging.getLogger(__name__)


def run(cfg: AppConfig, project: TrailerProject, state: dict) -> dict:
    target_s = cfg.pipeline.cut.max_duration_seconds
    beats = beats_for_duration(target_s)

    prompt = f"{project.genre} trailer score, {project.tone}, cinematic, rising tension"
    score_path = generate_score(
        prompt=prompt,
        duration_s=target_s,
        energy_curve=[(b.name, b.energy) for b, _, _ in beats],
        out_dir=Path(cfg.app.cache_dir) / "score",
    )
    normalized = normalize_loudness(score_path, cfg.pipeline.score.target_loudness_lufs)

    log.info("score composed -> %s", normalized)
    state["score_path"] = normalized
    state["beats"] = beats
    return state