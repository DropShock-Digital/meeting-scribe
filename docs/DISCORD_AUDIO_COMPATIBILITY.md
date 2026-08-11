# Discord audio compatibility

## Current product posture

Meeting Scribe ships a **Discord command adapter**, not a claimed live-audio recorder. It does not auto-join a voice channel, start a voice connection, or move a meeting into capture state merely because a Discord command ran.

This is not a missing disclaimer. It is a safety property: a meeting record must never say recording started when the bot cannot prove it received audio.

## Evidence behind the block

The currently available Pycord `VoiceClient.start_recording` implementation in the project's tested dependency line emits an upstream warning that voice reception is currently broken under Discord's DAVE end-to-end-encryption protocol. We therefore reject it as a production capture transport for this release.

The project includes the dependency only for command-adapter development; it is not an endorsement of its recording path.

## Gate for an audio-receive adapter

A future adapter can change this position only after all of the following are recorded in a release PR:

1. **Source review:** maintained source, explicit license, bounded permissions, current DAVE compatibility evidence, and no undisclosed hosted audio routing.
2. **Unit/integration tests:** failed join, missing permission, reconnect, stop, exception, duplicate-start, and file/write failure all create honest events without marking audio captured.
3. **Isolated test-guild proof:** opt-in human test participants verify join/disclosure, speech from multiple people, silence, reconnect, stop, and stored audio format.
4. **Failure proof:** disable the transport mid-session and prove the meeting becomes degraded rather than silently complete.
5. **Privacy/release review:** precise bot intents/scopes, retention, storage encryption/access, user-facing disclosure, and rollback documented.

Until then, use Meeting Scribe's local lifecycle/transcript-import flow for meeting records, or contribute a verified adapter behind the same explicit capability gate.
