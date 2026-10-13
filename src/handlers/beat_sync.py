"""Stage 3 support: align cut points to musical beats."""
from __future__ import annotations

import logging

import librosa
import numpy as np

log = logging.getLogger(__name__)


def detect_beats(audio_path, sr: int = 22050) -> np.ndarray:
    y, sr = librosa.load(str(audio_path), sr=sr, mono=True)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time")
    log.info("tempo=%.1f bpm, %d beats", float(np.atleast_1d(tempo)[0]), len(beats))
    return beats


def snap_to_beats(cut_times: list[float], beats: np.ndarray, tolerance: float = 0.08) -> list[float]:
    if beats.size == 0:
        return cut_times
    snapped: list[float] = []
    for t in cut_times:
        idx = int(np.argmin(np.abs(beats - t)))
        snapped.append(float(beats[idx]) if abs(beats[idx] - t) <= tolerance else t)
    return snapped