# ADR — provider choice is configuration-backed, not a credential form

**Status:** accepted for the control-plane slice.

## Context

Meeting Scribe is a standalone Docker-first application. It does not currently perform AI summarization or verified Discord audio capture. The private control room is Tailnet-reachable but is not a secret-management surface.

## Decision

1. **Rooms** are defined by a server-owned catalog of `label + allowlisted ID` pairs. The console receives labels only.
2. **Providers** are declared by deployment configuration and exposed as sanitized `{id, label, kind, availability, detail}` records.
3. The browser saves a selected room/provider in its local storage. A later verified gateway/summarizer must revalidate against server configuration before use.
4. Provider secrets stay outside the browser:
   - **Codex OAuth:** requires a dedicated, verified provider relay/connection. Meeting Scribe must never read a Hermes profile's OAuth cache or auth file.
   - **OpenRouter:** key is supplied to the runtime by a protected secret-file/env mechanism and represented only as `configured`/`not configured`.
   - **LM Studio / compatible:** the deployment defines an approved endpoint. The browser cannot submit a URL; no arbitrary server-side fetch is created by this slice.
5. A provider preference cannot create a meeting, join Discord, disclose, record, transcribe, summarize, spend money, or change access.

## Consequences

- The immediate UI is useful and truth-preserving without pretending a summarization feature already exists.
- A future AI implementation has one explicit provider registry and can add authenticated provider-relay and model-health gates without redesigning the control room.
- Operators who need to add a provider use protected deployment/vault procedures, not the browser.
