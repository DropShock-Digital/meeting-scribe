# Epics and stories

## E1 — Safe core lifecycle
- **S1:** Create a consent-confirmed allowlisted meeting. Acceptance: denied requests do not create rows/events.
- **S2:** Enforce lifecycle transitions and append immutable evidence. Acceptance: transcript events fail before recording/after finalization.
- **S3:** Export reproducible Markdown/JSON packages. Acceptance: export excludes environment configuration.

## E2 — Local operator experience
- **S4:** Serve an accessible static console. Acceptance: healthy service returns visible meeting cards and focusable controls.
- **S5:** Present clear degraded/finalized states. Acceptance: warning events are human-readable without logs.

## E3 — Discord adapter
- **S6:** Parse safe configuration and remain disabled by default. Acceptance: startup without token never connects to Discord.
- **S7:** Map approved slash-command operations to the same core lifecycle. Acceptance: unit tests deny non-operators/unapproved channels.
- **S8:** Define audio/STT adapter contracts and failure receipts. Acceptance: no capture/transcription claim is made when an adapter is unavailable.

## E4 — Open-source operations
- **S9:** Docker-first local demo, health check, backups, and recovery docs.
- **S10:** Public-repo safety scanner, CI, security policy, contribution guide, and release checklist.

## Dependencies
E1 precedes E2/E3. E4 runs throughout. Real Discord voice end-to-end verification requires an operator-owned test guild and is not simulated as a production claim.
