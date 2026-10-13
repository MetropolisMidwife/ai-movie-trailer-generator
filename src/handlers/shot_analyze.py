"""Stage 2: shot detection + scene embedding for cut planning."""
from __future__ import annotations

import logging

import cv2
import numpy as np

from src.core.project import TrailerProject
from src.services.vision_service import embed_frame, score_emotion
from src.utils.config import AppConfig

log = logging.getLogger(__name__)


def _detect_shots(video_path, min_seconds: float, fps_fallback: float = 24.0) -> list[tuple[float, float]]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        log.warning("cannot open %s", video_path)
        return []
    fps = cap.get(cv2.CAP_PROP_FPS) or fps_fallback
    min_frames = max(1, int(min_seconds * fps))

    shots: list[tuple[float, float]] = []
    prev_hist = None
    shot_start = 0
    frame_idx = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        small = cv2.resize(frame, (160, 90))
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
        cv2.normalize(hist, hist)
        if prev_hist is not None:
            dist = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
            if dist > 0.45 and (frame_idx - shot_start) >= min_frames:
                shots.append((shot_start / fps, frame_idx / fps))
                shot_start = frame_idx
        prev_hist = hist
        frame_idx += 1

    if frame_idx > shot_start:
        shots.append((shot_start / fps, frame_idx / fps))
    cap.release()
    return shots


def run(cfg: AppConfig, project: TrailerProject, state: dict) -> dict:
    media = state.get("media", [])
    analyzed: list[dict] = []

    for item in media:
        if item.kind != "video":
            continue
        shots = _detect_shots(item.path, cfg.pipeline.analyze.min_shot_seconds)
        for start, end in shots:
            frame = _sample_frame(item.path, (start + end) / 2.0)
            if frame is None:
                continue
            analyzed.append(
                {
                    "path": str(item.path),
                    "start": start,
                    "end": end,
                    "embedding": embed_frame(frame).tolist(),
                    "emotion": score_emotion(frame),
                    "brightness": float(np.mean(frame) / 255.0),
                }
            )

    log.info("analyzed %d shots", len(analyzed))
    state["shots"] = analyzed
    return state


def _sample_frame(path, t: float):
    cap = cv2.VideoCapture(str(path))
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000.0)
    ok, frame = cap.read()
    cap.release()
    return frame if ok else None