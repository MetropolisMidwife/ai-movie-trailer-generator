"""FFmpeg wrapper — probing, proxy generation, loudness normalization."""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)


def _run(args: list[str]) -> subprocess.CompletedProcess:
    log.debug("ffmpeg: %s", " ".join(args))
    return subprocess.run(args, capture_output=True, text=True, check=False)


def probe_duration(path: Path) -> float:
    proc = _run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)]
    )
    if proc.returncode != 0:
        log.warning("ffprobe failed for %s: %s", path, proc.stderr.strip())
        return 0.0
    try:
        return float(json.loads(proc.stdout)["format"]["duration"])
    except (KeyError, ValueError):
        return 0.0


def make_proxy(src: Path, out_dir: Path, height: int = 540) -> Path:
    out = out_dir / f"{src.stem}_proxy.mp4"
    if out.exists():
        return out
    proc = _run(
        ["ffmpeg", "-y", "-i", str(src), "-vf", f"scale=-2:{height}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
         "-an", str(out)]
    )
    if proc.returncode != 0:
        log.warning("proxy failed for %s: %s", src, proc.stderr.strip())
    return out


def normalize_loudness(src: Path, target_lufs: float = -14.0) -> Path:
    out = src.with_name(f"{src.stem}_norm{src.suffix}")
    proc = _run(
        ["ffmpeg", "-y", "-i", str(src),
         "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
         str(out)]
    )
    if proc.returncode != 0:
        log.warning("loudnorm failed for %s", src)
        return src
    return out