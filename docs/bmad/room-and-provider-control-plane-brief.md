# Room and AI-provider control plane

## Decision

Meeting Scribe will let an operator choose a **human-readable, approved voice room** and a **configured AI provider preference** from the private control room. These are operator preferences, not direct Discord/audio/AI commands.

## Why

The original recorder was room-oriented. A normal operator should choose a named meeting destination, not paste a channel ID. They should also be able to select the intended analysis provider without handling credentials in the meeting UI.

## Scope now

- Render an eligible room chooser from a server-owned room catalog.
- Render provider choices for Codex OAuth, OpenRouter, LM Studio, and other explicitly configured OpenAI-compatible providers.
- Persist the operator's local browser preference only; do not store it as shared server state.
- Explain the selected preference truthfully: it will apply only to a future verified summarization workflow.
- Keep Discord capture, live join, transcription, and summarization disabled unless their individual capability gates are met.

## Non-goals

- No browser collection, display, or storage of API keys, OAuth tokens, Discord tokens, channel IDs, model URLs, or credentials.
- No mounting or reading Hermes/Codex OAuth stores from Meeting Scribe.
- No arbitrary provider URL fields or browser-originated server-side fetches.
- No claim that a selected provider is connected, called, billed, or used while no verified summary path exists.

## Acceptance criteria

1. The primary UI has a named room selector and never shows a raw room/channel ID.
2. Choices come only from deployment configuration; browser selection cannot widen the allowlist.
3. The UI has a provider selector with an accurate configuration-and-verification label for Codex OAuth, OpenRouter, LM Studio, and compatible providers.
4. Keys/tokens/endpoints/IDs never appear in the console API, DOM, exports, logs, tests, screenshots, or public docs.
5. Provider selection has no effect on capture status and cannot enable Discord audio.
6. The server/API tests prove sanitization; browser QA proves desktop/mobile clarity; Docker/Tailnet verification proves the private deployment still works.
