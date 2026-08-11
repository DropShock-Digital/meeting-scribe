# Control-room experience

## Information hierarchy

1. **Now** — one clear state: `Waiting for a configured room`, `Disclosure sending`, `Recording`, `Needs attention`, or `Closed`.
2. **Signal strip** — Discord gateway, disclosure automation, voice capture, transcript, and summary status. Each has a direct, truthful label.
3. **Active meeting** — room label, elapsed time, people, transcript freshness, and current summary when live integration exists.
4. **Control surface** — only actions that are real. The first safe set is refresh, create an offline review record, open an export, and finalize an offline record.
5. **Archive** — completed/local records with exports. Raw IDs stay absent from the interface.

## Normal flow

- Deployment config establishes approved rooms, operator authority, disclosure wording, and retention.
- Discord detects people in an approved room.
- Gateway creates the meeting identity from Discord context, posts the configured disclosure, and records delivery evidence.
- Only a verified capture worker may report audio/transcript start.
- Console updates automatically. It exposes recovery actions only when their durable action bridge exists.
- When people leave, gateway closes and exports the meeting package.

## No-live-capture flow

The headline must say `Voice capture is safely paused`. The support text says why in one sentence and links to the capability detail. The operator can create an **offline review record** to inspect the UI and exports. It must never transition to `recording` automatically.

## Visual direction

A dark, editorial “control room,” not a generic admin dashboard:

- near-black canvas, fogged indigo horizon, warm white type, one electric-cyan signal color;
- giant restrained type for the present state; small monospace metadata for machine signals;
- asymmetric grid: large live-state canvas beside compact system-health rail;
- a thin animated signal line only when reduced motion is allowed; it is decorative, never status evidence;
- no gradient-card grid, stock icons, fake activity charts, decorative number rows, or pill-heavy navigation;
- 44px minimum touch targets, keyboard-visible focus, semantic status text, reduced-motion fallback, and no color-only status.

## Exact UI language

- `Waiting for a configured room`
- `Everything is ready except voice capture.`
- `Voice capture is safely paused`
- `Discord's current encrypted voice receive path has not passed this app's verification gate.`
- `Create offline review record`
- `No active meeting yet`
- `Local records`
- `Open Markdown` / `Open JSON`

Avoid `channel ID`, `operator ID`, `I confirm`, `demo`, `manual-import`, `fake`, and claims such as `recording` unless the backend has recorded that state.
