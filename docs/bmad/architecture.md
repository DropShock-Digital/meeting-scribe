# Architecture spine

## Paradigm
**Local-first hexagonal application.** The core lifecycle is synchronous and deterministic. Discord, audio/STT, AI enrichment, and workflow tools are adapters around it.

## Invariants
- **AD-01 Core owns state.** Only the core service writes meetings, events, and exports. Adapters call the core API/service layer.
- **AD-02 Consent before capture.** A meeting begins as `disclosing`; transcript events are accepted only while `recording`.
- **AD-02a Capture must prove its start.** A Discord command/disclosure alone cannot transition a meeting into actual capture. Unsupported transports fail closed with an explicit capability reason.
- **AD-03 Event evidence is append-only.** State transitions add immutable event rows in the same transaction.
- **AD-04 Default isolation.** The reference deployment binds to loopback, has no telemetry, and accepts no browser-entered secrets.
- **AD-05 Providers are replaceable.** Discord, audio receive, speech-to-text, and enrichment implement narrow interfaces and cannot change core policy.
- **AD-06 Review before consequence.** Commitments are local review candidates; no external action adapter ships enabled.

## Seed architecture
Browser → FastAPI routes/static console → service layer → SQLite + local export directory.

Optional: Discord gateway → policy/command adapter → service layer. A verified audio/STT worker → validated transcript-event adapter → service layer. The current Discord audio adapter is deliberately unavailable because Pycord's tested receive path warns of a DAVE compatibility break.

## Deferred
Multi-user web authentication, distributed queues, encrypted-at-rest key management, automatic retention deletion, and external workflow adapters are intentionally deferred until an operator-auth and deployment threat model exists.
