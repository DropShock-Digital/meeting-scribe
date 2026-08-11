# ADR — operator-native control-room defaults

## Context

The alpha console exposed persistence primitives directly: title, channel ID, operator ID, disclosure text, and a disclosure checkbox. This was technically explicit but mismatched the historic automatic Discord workflow.

## Decision

Keep the durable core schema and policy boundary. Add a console-specific read model and a no-input offline-review creation path.

- `GET /api/console` returns non-secret control-room readiness: configured room/operator counts, Discord adapter enabled state, capture capability, disclosure template presence, and active/archive summaries.
- `POST /api/meetings/offline-review` creates a generated local record with an internal configured identity and an event declaring it non-capturing.
- Real gateway adapters remain responsible for supplying Discord room/user labels and for moving a meeting from disclosure to recording only after an actual disclosure delivery and verified capture start.
- The browser never receives token values, raw channel/operator IDs, local paths, or an unverified live-state claim.

## Consequences

The UI becomes simple without weakening server-side allowlists or evidence. A future Discord adapter can supply rich live state without redesigning the console. The offline record offers a truth-preserving review path while live audio remains blocked.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| A local walkthrough is mistaken for capture | Explicit `offline review` origin/event and non-recording state. |
| UI implies a missing control works | Render only implemented actions; label unavailable capability plainly. |
| A future adapter bypasses consent | Core transition remains conditional and capture remains separately gated. |
| Private metadata leaks into OSS UI | Console API returns counts/capability text only; safety scan remains required. |
