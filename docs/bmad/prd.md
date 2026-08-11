# Product requirements document — Meeting Scribe 0.1

## Scope
A standalone self-hosted meeting-record product with a local operator console, durable SQLite state/event storage, local package exports, and an optional Discord command/voice adapter.

## Functional requirements
- **FR-01** The API shall create a meeting only when the requested channel is allowlisted and the operator explicitly confirms the disclosure.
- **FR-02** The API shall record an append-only event for creation, disclosure, acknowledgement, transcript segment, warning, stop, and export.
- **FR-03** The operator console shall show recent meetings, current status, consent/disclosure state, and transcript tail without exposing secrets.
- **FR-04** The API shall accept validated transcript segments with an explicit source, timestamp, and optional speaker label.
- **FR-05** The API shall render deterministic Markdown and JSON exports from stored meeting state/events.
- **FR-06** The API shall reject transcript ingestion after finalization.
- **FR-07** The Discord adapter shall remain disabled unless its token and explicit channel allowlist are configured.
- **FR-08** Discord start/stop commands shall require an approved operator identity and use the same core lifecycle as HTTP requests.
- **FR-09** The app shall persist data under a configurable local volume and never place meeting bodies in application logs.
- **FR-10** The app shall expose health/readiness endpoints that reveal no transcript or secret material.

## Non-functional requirements
- **NFR-01 Privacy:** no telemetry, no default cloud calls, no recording by default.
- **NFR-02 Recoverability:** each mutation is committed with its event record; exports are reproducible from SQLite state.
- **NFR-03 Security:** configuration is environment-based; tokens are never returned by APIs, logs, demo fixtures, docs, or tests.
- **NFR-04 Accessibility:** console supports keyboard navigation, semantic landmarks, high contrast, reduced motion, and readable error states.
- **NFR-05 Operations:** `docker compose up --build` supports a local demo; the service exposes health checks and documented backup/restore.
- **NFR-06 Honesty:** any unavailable audio/STT capability must surface as a warning—not a claim that recording/transcription occurred.

## Acceptance criteria
The automated suite must cover permitted/denied meeting creation, explicit confirmation, transcript lifecycle, finalized-state denial, export content, path traversal resistance, secret-free health, and console asset availability. Docker configuration must parse and the default demo must serve its health endpoint.
