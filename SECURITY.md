# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | security fixes only |
| < 0.3   | no        |

## Reporting a vulnerability

Open a private security advisory on GitHub, or email
`security@ai-movie-trailer-generator.dev`. Please include:

- Affected version (`python -m src.app --version`)
- Steps to reproduce
- Whether the issue requires a malicious `.trailerproj` file, a crafted
  media file, or a compromised remote model endpoint.

## Threat model notes

- Trailer project files (`.trailerproj`) are treated as untrusted input.
  They are parsed with `tomllib` and never `eval`'d.
- Remote model endpoints are user-configured. We do not ship API keys.
  Keys live in `config/secrets.toml` (gitignored) or environment vars.
- FFmpeg is invoked with argument lists, never `shell=True`.
- Rendered output paths are sanitized against traversal in
  `src/utils/paths.py`.