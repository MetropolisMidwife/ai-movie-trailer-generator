"""TrailerProject — the on-disk .trailerproj model."""
from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class MediaItem(BaseModel):
    path: Path
    kind: str  # "video" | "audio" | "image"
    duration_s: float = 0.0
    tags: list[str] = Field(default_factory=list)


class TrailerProject(BaseModel):
    title: str
    logline: str = ""
    genre: str = "thriller"
    tone: str = "tense"
    media: list[MediaItem] = Field(default_factory=list)
    source_dir: Path | None = None
    root: Path = Field(default_factory=Path.cwd)

    @field_validator("media", mode="before")
    @classmethod
    def _coerce_media(cls, v):
        if isinstance(v, list):
            return [m if isinstance(m, dict) else {"path": m, "kind": "video"} for m in v]
        return v

    @classmethod
    def load(cls, path: Path) -> "TrailerProject":
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
        proj = cls(**raw)
        proj.root = path.parent
        if proj.source_dir and not proj.source_dir.is_absolute():
            proj.source_dir = (path.parent / proj.source_dir).resolve()
        return proj

    def resolve_media(self) -> list[MediaItem]:
        base = self.source_dir or self.root
        out: list[MediaItem] = []
        for m in self.media:
            p = m.path if m.path.is_absolute() else (base / m.path)
            out.append(m.model_copy(update={"path": p.resolve()}))
        return out