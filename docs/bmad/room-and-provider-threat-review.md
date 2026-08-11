# Threat review — room and provider control plane

| Boundary | Risk | Required control |
|---|---|---|
| Browser → console API | Raw Discord IDs or provider metadata leak | Return labels and status only; validate display labels so they cannot be Discord-like identifiers or URLs/endpoints. |
| Browser preference | A selection widens room/provider authority | Store locally only; a later backend action must revalidate against server configuration. |
| OpenRouter credential | API key exposed in page, logs, export, or SQLite | Deployment-only protected secret source; console receives a configuration signal only—not health, authentication, or provider readiness. |
| Codex OAuth | Standalone app borrows Hermes/host OAuth | Prohibited. Use a future dedicated relay/connection with explicit authorization and its own scope. |
| LM Studio / compatible URL | Browser-controlled SSRF | No URL entry or dynamic server fetch. Approved endpoint is deployment configuration. |
| Provider selection | Implied capture/summarization/billing | UI calls it a preference and declares no AI run occurs in the current capability state. |
| Discord room selection | Arbitrary bot join | Catalog is a subset of the allowlist; selection alone performs no Discord request. |

## Release gate

Do not add in-browser key fields, OAuth callbacks, arbitrary endpoints, direct provider invocations, or room-join commands in this slice. Those require explicit authentication, vault/secret delivery, network policy, a verified gateway/provider integration, and separate end-to-end tests.
