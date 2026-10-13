"""Stage 7: assemble the final trailer with FFmpeg and write the output."""
from __future__ import annotations

import logging
from pathlib import Path

from src.core.project import TrailerProject
from src.services.render_service import render_trailer
from src.utils.config import AppConfig

log = logging.getLogger(__name__)


def run(cfg: AppConfig, project: TrailerProject, state: dict) -> dict:
    edl_path = state.get("edl_path")
    score_path = state.get("score_path")
    vo_path = state.get("vo_path")
    srt_path = state.get("srt_path")

    if not edl_path or not score_path:
        raise RuntimeError("missing EDL or score; cannot render")

    out_dir = Path(cfg.app.render_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in project.title)
    output_path = out_dir / f"{safe_title}_trailer.{cfg.pipeline.mux.container}"

    render_trailer(
        edl_path=edl_path,
        score_path=score_path,
        vo_path=vo_path,
        srt_path=srt_path,
        output_path=output_path,
        cfg=cfg,
    )
    log.info("trailer rendered -> %s", output_path)
    state["output_path"] = output_path
    return state