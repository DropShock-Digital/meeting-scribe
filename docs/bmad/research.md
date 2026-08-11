# Discovery and research

## Evidence reviewed
- The former `hermes-voice-scribe` package: a Hermes source patch that handled voice-state events, durable transcript lines, disclosure, long-call checkpoints, catch-up summaries, and graceful finalization.
- The old design is useful evidence, but it is not a release-ready product architecture: it patches a general agent gateway and couples recording availability to Hermes runtime behavior.
- Discord voice recording is privacy-sensitive. Discord bot authorization, server permissions, user disclosure, retention, and local law remain the operator's responsibility.

## Product decision
Build a new standalone app rather than reviving the patch. It will own meeting state, local storage, consent records, transcript exports, and a localhost-first operator console. Discord is an optional adapter. AI extraction is intentionally optional and cannot directly create tasks, send messages, or mutate external systems.

## Comparable capability retained
- explicit operator start/stop
- visible disclosure and per-participant acknowledgement ledger
- append-only transcript event log
- durable meeting package and exports
- checkpoint summaries and finalization
- reconnect/error state, not silent loss

## Rejected paths
- A Hermes patch: makes a recorder depend on an agent gateway and complicates upgrades.
- n8n in the capture path: adds latency and exposes sensitive raw media/transcripts to workflow execution data.
- automatic task creation: meeting language is ambiguous; outputs must be review candidates.
- public control plane: outside scope. The app is localhost-first and Dockerized.

## Voice-receive compatibility finding

The tested Pycord 2.8.1 API includes a recording method, but its own source emits a runtime warning that voice reception is currently broken under Discord's DAVE end-to-end-encryption protocol. Its repository is active and MIT-licensed, but that does **not** satisfy Meeting Scribe's capture reliability gate. The public project therefore ships a Discord command adapter and an explicit unavailable-capture capability instead of a misleading partial recorder. See [`../DISCORD_AUDIO_COMPATIBILITY.md`](../DISCORD_AUDIO_COMPATIBILITY.md).
