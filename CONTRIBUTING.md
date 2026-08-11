# Contributing

Thanks for helping make self-hosted meeting records safer and more useful.

## Before opening a pull request
1. Keep changes independent of any private Hermes, n8n, Notion, Huly, or homelab deployment.
2. Do not commit recordings, transcripts, screenshots containing real people/data, Discord identifiers, tokens, or `.env` files.
3. Run `uv run pytest`, `uv run ruff check .`, `uv run mypy src`, and `python scripts/repo_safety_check.py`.
4. Document new security/privacy behavior and add a test for any changed policy boundary.

## Design principles
Prefer small, explicit adapters around a stable consent-and-lifecycle core. Never make capture or external consequences implicit.
