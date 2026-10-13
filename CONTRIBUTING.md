# Contributing to ai-movie-trailer-generator

Thanks for wanting to help build the trailer engine. This is a Windows-first
desktop tool that turns a script + media pool into a scored, cut, captioned
movie trailer using local and remote AI models.

## Ground rules

- Python 3.11+ only. We use `match`, `tomllib`, and `asyncio.TaskGroup`.
- Windows is the primary target. Linux/macOS should still import cleanly.
- Every PR that touches `src/core/` must include or update a test under `tests/`.
- Keep the pipeline stages pure where possible. Side effects live in `services/`.

## Dev setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python -m src.app --config config/default.toml --dry-run
```

FFmpeg must be on `PATH` (we shell out for muxing and loudness normalization).

## What we want help with

- New beat-detection heuristics in `src/handlers/beat_sync.py`
- Better voiceover prosody scoring in `src/services/tts_service.py`
- Additional trailer templates under `src/core/templates/`
- GPU backend coverage (CUDA, DirectML, ROCm) in `src/services/render_service.py`

## Style

- `ruff` + `black`, line length 100.
- Type hints on public functions. `from __future__ import annotations` at top.
- No bare `except`. Log with the module logger.

## Pull request checklist

- [ ] `pytest -q` passes
- [ ] `ruff check src tests` clean
- [ ] New config keys documented in `config/default.toml` comments
- [ ] No model weights committed