# Control-room rework brief

**Decision:** Replace the form-led alpha console with a private, operator-native Discord meeting control room.

## Why

An operator should not type a meeting title, Discord channel ID, operator ID, disclosure text, or a per-session legal checkbox to run a recurring meeting. Those are configuration and automation concerns, not the core operating experience.

## Product outcome

At a glance, Steven can tell:

- whether the Discord gateway, disclosure automation, audio receiver, transcript stream, and summary loop are healthy;
- which configured room is active and who is present;
- whether the current meeting is collecting usable text;
- what the recorder has produced so far; and
- what safe recovery action is available.

## Preserved operating model

The historic model is automatic: an approved room becomes active when people arrive; the system posts its disclosure; recording/transcription starts only after that delivery succeeds; it periodically summarizes, catches up late joiners, and finalizes after the room empties. The operator console observes and assists that loop rather than becoming a data-entry gate.

## Current capability boundary

Discord audio receive remains unavailable in this release because the project has not verified a DAVE-compatible capture transport. The UI must say this plainly and must not simulate a live recording, speaker list, transcript, or summary.

## Release scope

- Replace form-first UI with responsive control room.
- Move normal meeting identity, room selection, operator identity, and disclosure copy behind deployment/gateway configuration.
- Add a no-input local review-session endpoint for UI walkthroughs; it creates an explicitly non-capturing record.
- Add console status API exposing configuration counts and verified capture capability.
- Keep raw identifiers out of ordinary UI; show human labels only when a future authenticated Discord gateway supplies them.
- Preserve existing API lifecycle and exports for integrations.

## Non-goals

- re-enable live Discord capture;
- browser-based token/configuration entry;
- fake live transcript data or wired-looking disabled controls;
- alter deployed Discord/Hermes configuration; or
- claim legal consent determination.
