# Change control — disclosure must not claim capture

## Trigger

An independent review of the pre-control-room alpha found that `POST /disclosure-delivered` transitioned a meeting from `disclosing` to `recording` despite the project’s declared unavailable Discord capture capability. The old browser UI exposed this as a generic “Confirm disclosure” action.

## Risk

A durable record could say `recording` even though no verified Discord transport had started. This violates the project’s fail-closed boundary and could mislead an operator or downstream integration.

## Remediation

- The new control room contains no disclosure-confirmation control.
- Disclosure delivery now appends durable evidence while keeping the meeting `disclosing`.
- Transcript ingestion remains rejected until a future verified capture adapter owns a separate capture-start transition.
- Tests assert that disclosure evidence is stored but no recording claim or transcript ingestion is allowed.
- Public API documentation now describes the endpoint accurately.

## Current decision

**Accepted:** no current browser/API path can mark a meeting as recording merely because a disclosure was acknowledged. Real Discord capture remains unavailable pending DAVE-compatible, explicitly opted-in verification.
