# ADR-001: Keep Meeting Scribe standalone

**Status:** accepted

## Decision
Meeting Scribe owns its lifecycle, local storage, exports, and operator console. Hermes, n8n, Huly, and external AI systems are optional downstream adapters.

## Consequences
The recorder can run without an AI-agent gateway and does not send raw meeting artifacts into automation logs. Integration work is smaller, separately testable, and approval-gated.
