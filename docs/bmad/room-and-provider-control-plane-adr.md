# ADR — provider configuration stays out of the meeting UI

**Status:** accepted for the current local-core release.

## Context

Meeting Scribe does not currently perform AI summarization or verified Discord audio capture. The private control room is Tailnet-reachable but is not a secret-management surface or a provider-selection screen.

## Decision

1. **Rooms** are defined by a server-owned catalog of `label + allowlisted ID` pairs. The console receives labels only and saves a chosen room locally in the browser.
2. **Providers** may be declared by protected deployment configuration, but provider names, details, status, endpoints, OAuth state, and key references are omitted from the console and browser-facing configuration API.
3. The interface shows a plainly unavailable meeting-helper state until a verified, user-authorized summarization workflow exists.
4. Provider secrets stay outside the browser:
   - **Codex OAuth:** requires a dedicated, verified provider relay/connection. Meeting Scribe must never read a Hermes profile's OAuth cache or auth file.
   - **OpenRouter:** a protected secret-file/env mechanism may supply a key to a future runtime adapter; it is not exposed to the browser.
   - **LM Studio / compatible:** a future deployment may define an approved endpoint; the browser cannot submit a URL or initiate a fetch.
5. Neither room selection nor provider configuration can create a meeting, join Discord, disclose, record, transcribe, summarize, spend money, or change access.

## Consequences

- The screen represents only what a meeting host can do today.
- A future AI implementation must add a verified provider relay and explicit product workflow before its provider choices can appear in the UI.
- Operators who need to add a provider use protected deployment/vault procedures, not the browser.
