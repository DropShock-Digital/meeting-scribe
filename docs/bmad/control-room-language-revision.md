# Control-room language revision

**Decision:** simplify every rendered control-room label, action, empty state, and status into clear human language while preserving the existing safety boundary.

## Product brief

- **Audience:** a meeting host, not a developer or deployment operator.
- **Job:** see what is happening, choose a room and optional writing helper for a later supported workflow, and safely open or finish a private review record.
- **Tone:** calm, plain, private, and direct. No technical product theatre.
- **Truth boundary:** the current build cannot join Discord, record sound, or send meeting content to an AI provider. The interface must say that once in clear language, not repeat implementation details.

## Research and copy principles

1. Prefer a person’s task over the system component: `Room to use next`, not `Next voice room`; `Meeting helper`, not `AI provider`.
2. Prefer a concrete state over an operational claim: `Recording is off`, not `safe hold` or `gateway ready`.
3. Use verbs that match the real action: `Open a private review`, `Check again`, `Finish review`, `Open notes`, and `Download record`.
4. Keep the reason for an unavailable feature short and non-technical: `Recording is off until the connection has been fully checked.`
5. Never use a warm phrase to conceal a material limitation or make a non-action look active.

## Requirements and acceptance criteria

- All visible buttons, selectors, status names, headings, empty states, exports, and dialog text use everyday language.
- No user-visible string says `control plane`, `gateway`, `capture`, `Markdown`, `JSON`, `offline record`, `ready`, `safe hold`, or exposes implementation configuration.
- The current no-action boundary remains explicit: choosing a room/helper does not join a call, record sound, or share meeting content.
- A private review remains explicitly non-recording and cannot be mistaken for a meeting.
- Tests lock the human labels and the no-action boundary; source/API safety tests remain intact.
- Desktop and narrow-mobile review confirm readability, no overflow, clear state hierarchy, and usable actions.

## Architecture / security / rollout

- **Architecture:** N/A. This is a presentation-language revision, including the user-visible private-review title; no API schema, state transition, credential, storage, network, or deployment design changes are allowed.
- **Threat review:** rendering must continue to escape server values; the revision must not introduce identifiers, secret values, OAuth flows, endpoint fields, or provider calls.
- **Rollback:** one Git commit; the previous static UI remains recoverable.

## Implementation readiness

**Ready.** The scope is limited to the static HTML/JavaScript copy layer and its regression tests. Capture and provider execution remain unavailable. Required evidence: source tests, JavaScript syntax, lint/type/safety gates, local desktop/mobile visual review, container/private-review health, and remote CI.
