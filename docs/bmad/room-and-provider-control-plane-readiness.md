# Room and provider control plane — test design and readiness

## Test design

- A configured room catalog returns human labels, never channel IDs.
- A catalog entry whose ID is not allowlisted is rejected at startup/config parsing.
- Allowlist-only configuration returns no selectable rooms; a named stable catalog is required before a room can be chosen.
- Provider records expose no secret values, URLs, OAuth state, or key references; room/provider display labels that look like Discord identifiers or endpoints are rejected at configuration load.
- A provider is only selectable when its protected configuration source is present; configuration is not provider verification, authentication, or an AI execution path.
- Unsupported browser preference values fall back to a safe configured/default choice.
- The UI has no password/API-key/token/endpoint form fields and copy states that no AI request occurs yet.
- Desktop and 390px render with no horizontal overflow and accessible native selectors/labels.

## Readiness review

**Ready for implementation:** yes.

The change is additive, local-first, and reversible. It requires no Discord mutation, OAuth login, secret entry, provider request, billing change, or public networking. The chosen first slice deliberately avoids fake integration: it exposes an operator-native selector and truthful configuration state, while preserving later provider connection work behind explicit security and capability gates.

## Release outcome

**Ready for this control-plane release:** yes. It is not ready to join Discord, capture audio, authenticate a provider, submit an OAuth flow, call a model, or summarize a meeting.
