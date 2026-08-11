# Control-room rework readiness

**Outcome:** READY FOR IMPLEMENTATION

## Evidence

- User rejected the form-led flow and explicitly requested a high-end interface while preserving the historic automatic operating model.
- Current source confirms the UI requires title, channel ID, operator ID, editable disclosure, and a per-session confirmation before creating a record.
- Historic source configuration and command surface show the intended recorder behavior is configuration-driven, automatic around approved voice rooms, disclosure-aware, checkpointed, and able to catch up/finalize.
- Current capture capability is explicitly unavailable and must remain fail-closed.

## Implementation guardrails

- Build a control room, not a second product or generic admin panel.
- Preserve server-side allowlists and atomic lifecycle constraints.
- Hide configuration internals from normal operation rather than deleting enforcement.
- Do not change Discord/Hermes runtime or re-enable capture in this UI rework.
- Verify with automated, visual, responsive, Docker, Tailnet, and independent-review gates.
