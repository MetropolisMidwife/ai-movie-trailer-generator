"""Pipeline orchestrator — runs ingest → analyze → score → cut → voiceover → caption → mux."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from src.core.project import TrailerProject
from src.handlers import (
    beat_sync,
    caption_burn,
    cut_assembly,
    ingest_scan,
    mux_export,
    score_compose,
    shot_analyze,
    voiceover_synth,
)
from src.utils.config import AppConfig

log = logging.getLogger(__name__)

StageFn = Callable[[AppConfig, TrailerProject, dict], dict]


@dataclass
class PipelineResult:
    ok: bool
    output_path: Path | None = None
    failed_stage: str | None = None
    error: str | None = None
    timings: dict[str, float] = field(default_factory=dict)


STAGE_TABLE: dict[str, StageFn] = {
    "ingest": ingest_scan.run,
    "analyze": shot_analyze.run,
    "score": score_compose.run,
    "cut": cut_assembly.run,
    "voiceover": voiceover_synth.run,
    "caption": caption_burn.run,
    "mux": mux_export.run,
}


class TrailerPipeline:
    """Sequential, resumable trailer build. State flows through a shared dict."""

    def __init__(self, cfg: AppConfig, project: TrailerProject) -> None:
        self.cfg = cfg
        self.project = project
        self.state: dict = {"cfg": cfg, "project": project}

    def run(self, dry_run: bool = False) -> PipelineResult:
        result = PipelineResult(ok=True)
        for stage_name in self.cfg.pipeline.stages:
            stage_cfg = getattr(self.cfg.pipeline, stage_name, None)
            if stage_cfg is not None and not getattr(stage_cfg, "enabled", True):
                log.info("stage %s disabled, skipping", stage_name)
                continue

            fn = STAGE_TABLE.get(stage_name)
            if fn is None:
                log.warning("unknown stage %r, skipping", stage_name)
                continue

            if dry_run:
                log.info("[dry-run] would run stage %s", stage_name)
                continue

            t0 = time.perf_counter()
            try:
                self.state = fn(self.cfg, self.project, self.state)
            except Exception as exc:  # noqa: BLE001 — pipeline boundary
                log.exception("stage %s failed", stage_name)
                result.ok = False
                result.failed_stage = stage_name
                result.error = str(exc)
                return result
            result.timings[stage_name] = time.perf_counter() - t0
            log.info("stage %s done in %.2fs", stage_name, result.timings[stage_name])

        if not dry_run:
            result.output_path = self.state.get("output_path")
        return result


# beat_sync is imported for its side-effect registration in some builds
_ = beat_sync