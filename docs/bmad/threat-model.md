# Threat model

## Assets
Discord bot token, meeting audio, transcript bodies, participant identity labels, consent evidence, export packages, local SQLite database.

## Trust boundaries
- Discord events and transcript content are untrusted input.
- Browser callers are trusted only in the localhost reference deployment; public deployment is unsupported without an auth layer.
- Optional STT/LLM providers are external processors and must be explicitly configured by the operator.
- The filesystem volume is a sensitive local asset.

## Primary controls
- explicit channel/operator allowlists
- required disclosure confirmation before a meeting can become `recording`
- immutable lifecycle events and strict transition validation
- request-size caps and path-safe export generation
- no configuration/secret echo endpoint
- safe log fields; never log transcript bodies or authorization headers
- non-root Docker user, read-only source mount, writable data volume only
- capture capability fails closed; the command bot cannot imply audio capture when the receive transport is unverified

## Residual risks
No application can verify every participant's legal consent, prevent a server administrator from changing bot permissions, or secure a publicly exposed instance without operator authentication/network controls. These are documented operator responsibilities, not silently solved claims.
