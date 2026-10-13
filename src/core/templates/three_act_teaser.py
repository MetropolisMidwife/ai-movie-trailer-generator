"""Three-act teaser template: hook (0-15%), build (15-70%), button (70-100%)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Beat:
    name: str
    start_frac: float
    end_frac: float
    energy: float  # 0..1 target intensity for music + cut rate


THREE_ACT_TEASER: tuple[Beat, ...] = (
    Beat("cold_open", 0.00, 0.06, 0.35),
    Beat("logo_sting", 0.06, 0.10, 0.55),
    Beat("world_build", 0.10, 0.35, 0.45),
    Beat("threat_reveal", 0.35, 0.50, 0.70),
    Beat("montage_rise", 0.50, 0.72, 0.85),
    Beat("hard_cut_silence", 0.72, 0.76, 0.10),
    Beat("title_card", 0.76, 0.88, 0.60),
    Beat("button", 0.88, 1.00, 0.95),
)


def beats_for_duration(total_s: float) -> list[tuple[Beat, float, float]]:
    """Return (beat, start_s, end_s) tuples scaled to a total trailer duration."""
    return [(b, b.start_frac * total_s, b.end_frac * total_s) for b in THREE_ACT_TEASER]