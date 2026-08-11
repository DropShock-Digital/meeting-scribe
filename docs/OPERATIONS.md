# Operations

## Local run
```bash
cp .env.example .env
uv sync --extra dev
uv run meeting-scribe serve
```
Open `http://127.0.0.1:8080`.

## Docker run
```bash
docker compose up --build
```
Open `http://127.0.0.1:8088`. The Compose file binds only to loopback by default.

## Backup
Stop the service for a consistent cold backup, then archive the configured data directory or Docker volume. The SQLite database and generated exports are the durable product data. Test restore into an isolated empty data directory before relying on a backup.

## Discord adapter
The adapter is optional and disabled by default. Use a dedicated bot with only the guild/channel/user permissions required for the chosen setup. Set a token only in a protected runtime secret path. Start with a non-sensitive test guild. A real Discord voice receive/capture test is required before relying on it for a live meeting.

## Recovery
If a meeting is degraded, do not claim complete capture. Preserve the event timeline, finalize it with an honest reason, and export it for review. Do not delete the underlying database to hide a failure.
