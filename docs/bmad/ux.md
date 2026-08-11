# UX and accessibility specification

## Product character
Quiet, clear, operator-first. The interface is not a surveillance dashboard. It should make the next safe action obvious and make uncertainty visible.

## Information architecture
- **Meetings:** current and recent meeting cards.
- **Meeting detail:** status, disclosure/acknowledgement evidence, transcript tail, system warnings, exports.
- **Start meeting:** one compact form with channel, title, disclosure text, and a required acknowledgement checkbox.
- **Settings:** local-only configuration guidance; no token display or in-browser secret editing.

## Key flow
1. An operator chooses an allowlisted channel and a descriptive meeting title.
2. They read the disclosure and confirm that it will be delivered before capture.
3. The app creates a `disclosing` meeting—not a hidden recording.
4. The adapter or operator records disclosure/acknowledgement events. Transcript ingestion becomes available only in `recording` state.
5. The operator ends the meeting, reviews the timeline, and exports a local package.

## State patterns
- **Idle:** start is available; no live meeting claim.
- **Disclosing:** clear amber notice; audio/transcript collection is not claimed.
- **Recording:** red status with elapsed time and a Stop button.
- **Degraded:** amber warning with exact failed component; raw events remain visible.
- **Finalized:** read-only package with export controls.

## Accessibility floor
Use native buttons/inputs/labels, a skip link, visible focus, `aria-live` for status changes, 4.5:1 text contrast, and `prefers-reduced-motion` support. No important control relies solely on color.
