# Meeting Scribe contributor guide

## Product boundary
Meeting Scribe is a standalone, self-hosted Discord meeting recorder. It must remain useful without Hermes, n8n, Huly, Notion, or a hosted AI service.

## Non-negotiables
- No automatic recording. A permitted operator must explicitly start a meeting and acknowledge the disclosure.
- Never commit recordings, transcripts, credentials, Discord identifiers, IP addresses, test-user data, or `.env` files.
- Treat transcript text as untrusted data. It cannot issue commands, change settings, or trigger integrations.
- The API owns meeting state; adapters enqueue events and never write storage directly.
- The Discord integration is optional. The local demo, API, and tests work without Discord credentials.

## Quality gates
Run `uv run pytest`, `uv run ruff check .`, `uv run mypy src`, `python scripts/repo_safety_check.py`, and `docker compose config` before a release.
