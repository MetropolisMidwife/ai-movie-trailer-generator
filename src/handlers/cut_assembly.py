"""Stage 4: select shots, order them into beats, emit an edit decision list."""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from src.core.project import TrailerProject
from src.handlers.beat_sync import detect_beats, snap_to_beats
from src.utils.config import AppConfig

log = logging.getLogger(__name__)


def _pick_shot(pool: list[dict], target_energy: float, used: set[int]) -> dict | None:
    """Pick the unused shot whose brightness/emotion best matches target energy."""
    best, best_score = None, -1.0
    for i, shot in enumerate(pool):
        if i in used:
            continue
        e = shot.get("emotion", {})
        valence = float(e.get("valence", 0.5))
        arousal = float(e.get("arousal", 0.5))
        fit = 1.0 - abs(arousal - target_energy) - 0.3 * abs(valence - 0.5)
        if fit > best_score:
            best, best_score = (i, shot), fit
    if best is None:
        return None
    used.add(best[0])
    return best[1]


def run(cfg: AppConfig, project: TrailerProject, state: dict) -> dict:
    shots = state.get("shots", [])
    beats = state.get("beats", [])
    score_path = state.get("score_path")

    if not shots:
        raise RuntimeError("no analyzed shots available for cut assembly")

    beats_audio = detect_beats(score_path) if score_path else np.array([])
    edl: list[dict] = []
    used: set[int] = set()
    cursor = 0.0

    for beat, start_s, end_s in beats:
        target = beat.energy
        while cursor < end_s:
            shot = _pick_shot(shots, target, used)
            if shot is None:
                break
            clip_len = min(shot["end"] - shot["start"], end_s - cursor)
            if clip_len <= 0.15:
                cursor += 0.2
                continue
            edl.append(
                {
                    "beat": beat.name,
                    "src": shot["path"],
                    "in": shot["start"],
                    "out": shot["start"] + clip_len,
                    "timeline_in": cursor,
                }
            )
            cursor += clip_len

    cut_times = [e["timeline_in"] for e in edl]
    snapped = snap_to_beats(cut_times, beats_audio) if beats_audio.size else cut_times
    for e, t in zip(edl, snapped):
        e["timeline_in"] = t

    out = Path(cfg.app.cache_dir) / "edl.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    import json

    out.write_text(json.dumps(edl, indent=2), encoding="utf-8")
    log.info("EDL written with %d cuts -> %s", len(edl), out)
    state["edl"] = edl
    state["edl_path"] = out
    return state