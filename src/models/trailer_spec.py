"""TrailerSpec — the final, renderable description of a trailer."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Cut(BaseModel):
    beat: str
    src: str
    in_s: float = Field(alias="in")
    out_s: float = Field(alias="out")
    timeline_in: float

    model_config = {"populate_by_name": True}


class TrailerSpec(BaseModel):
    title: str
    total_duration_s: float
    cuts: list[Cut]
    score_path: str
    vo_path: str | None = None
    srt_path: str | None = None