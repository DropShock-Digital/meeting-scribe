# Room and AI-provider control plane

## Decision

Meeting Scribe lets an operator choose a **human-readable, approved voice room** from the private control room. AI-provider configuration remains deployment-side and is not rendered as an operator preference until a verified, user-authorized summary workflow exists.

## Why

The original recorder was room-oriented. A normal operator should choose a named meeting destination, not paste a channel ID. Provider configuration must stay out of the meeting UI until it can lead to a real, reviewed action rather than a cosmetic preference.

## Scope now

- Render an eligible room chooser from a server-owned room catalog.
- Render a plain unavailable helper state; keep Codex OAuth, OpenRouter, LM Studio, and compatible-provider configuration out of the browser UI.
- Persist the operator's local browser room preference only; do not store it as shared server state.
- State plainly that the current version cannot join calls, record sound, or send content to AI.
- Keep Discord capture, live join, transcription, and summarization disabled unless their individual capability gates are met.

## Non-goals

- No browser collection, display, or storage of API keys, OAuth tokens, Discord tokens, channel IDs, model URLs, or credentials.
- No mounting or reading Hermes/Codex OAuth stores from Meeting Scribe.
- No arbitrary provider URL fields or browser-originated server-side fetches.
- No claim that a selected provider is connected, called, billed, or used while no verified summary path exists.

## Acceptance criteria

1. The primary UI has a named room selector and never shows a raw room/channel ID.
2. Choices come only from deployment configuration; browser selection cannot widen the allowlist.
3. The UI states that no meeting helper is available; it does not render Codex OAuth, OpenRouter, LM Studio, or compatible-provider choices.
4. Keys/tokens/endpoints/IDs never appear in the console API, DOM, exports, logs, tests, screenshots, or public docs.
5. Provider configuration has no effect on capture status and cannot enable Discord audio.
6. The server/API tests prove sanitization; browser QA proves desktop/mobile clarity and exact unavailable-state language; Docker/Tailnet verification proves the private deployment still works.
