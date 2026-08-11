# Change control — independent review remediation

**Trigger:** independent public-alpha review after the initial implementation.

## Findings fixed

1. **Atomic lifecycle transitions.** SQLite now applies a compare-and-swap status condition in the same transaction as its evidence event. Consent acknowledgements and transcript events are also status-gated in their insert statements. Concurrent transition tests prove a duplicate disclosure cannot commit and finalization cannot be overwritten by a stale disclosure.
2. **Runnable command adapter.** `meeting-scribe discord` now initializes the same protected data store as the console and runs the optional command-only adapter. Docker Compose exposes it only behind the explicit `discord` profile.
3. **Package-output safety scan.** Build output is intentionally ignored by the source safety scanner; the scanner still evaluates the committed source tree and public documentation.

## Retest gate

The remediation must pass the full test, lint, type, source-safety, Compose, locked Docker-image, runtime-health, committed-tree, and CI checks before publication of this follow-up commit.
