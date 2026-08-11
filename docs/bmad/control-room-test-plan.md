# Control-room rework test plan

## Behavioral acceptance

1. The root page contains no visible title, channel ID, operator ID, disclosure text input, or disclosure-confirmation checkbox.
2. `GET /api/console` reports the real capture capability and does not expose a token, raw allowlist entry, or local path.
3. `POST /api/meetings/offline-review` accepts no operator-supplied identity, generates a readable title, records a non-capturing origin event, and stays `disclosing`.
4. Existing explicit lifecycle endpoints continue to enforce allowlists and disclosure-before-transcript policy.
5. A browser can create an offline review record, see it in the archive, open both exports, and finalize it.
6. The page has semantic main/heading/status structure, keyboard focus, reduced-motion behavior, and no horizontal overflow at 390px, 768px, and 1440px.
7. Every visible action reaches a working endpoint or is absent.
8. Docker runtime, source scan, lint, type check, tests, Compose config, and private Tailnet endpoint pass.

## Negative acceptance

- No endpoint marks an offline review record as `recording`.
- No UI text claims that audio, speakers, transcript, summary, or Discord connection are live when capability is unavailable.
- No browser response includes Discord tokens, raw configured IDs, or filesystem paths.
