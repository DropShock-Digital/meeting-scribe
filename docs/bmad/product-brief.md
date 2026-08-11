# Product brief — Meeting Scribe

**Status:** final fast-path brief
**Audience:** Discord community operators who want self-hosted, consent-aware meeting records.

## The problem
A good Discord meeting recorder should be dependable during a long call, respectful about consent, and useful after the call. Most tooling either makes recording opaque, sends the meeting to a SaaS by default, or treats the recorder as a minor feature inside a larger bot.

## The product
Meeting Scribe is a standalone, Docker-first application. Its optional Discord command adapter can create an explicitly disclosed meeting record in a specifically authorized voice channel; it does not claim to join or capture audio until a DAVE-compatible receive transport has passed the documented capability gate. The core records provenance and consent acknowledgements, stores a durable local meeting package, and provides a local web console for transcript review and export.

## First release promise
A self-hosting operator can run a local demo without Discord, create and close a consented meeting through the console/API, ingest a transcript event, inspect the immutable event timeline, export clean Markdown/JSON, and run the optional Discord adapter with its own bot token.

## Non-goals
- legal consent determination or legal advice
- automatic recording or monitoring of channels
- unreviewed external messaging, task creation, CRM writes, or calendar changes
- hosted multi-tenant service
- audio intelligence that silently invents speakers, commitments, or outcomes

## Success
The first release is successful when an operator can understand its safety model in one README, run it locally with Docker, verify the core lifecycle with tests, and adapt the optional Discord integration without modifying the core product.
