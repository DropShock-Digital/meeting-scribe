# PRFAQ — Meeting Scribe 0.1

## Press release
**Introducing Meeting Scribe: a self-hosted Discord meeting recorder that makes consent and durability first-class.**

Meeting Scribe gives communities a clear way to record the meetings they choose to preserve. An authorized operator starts a meeting. The bot announces the recording. The application writes a durable local event ledger, transcript package, and export. Nothing is automatically sent to an agent, CRM, calendar, or hosted AI provider.

The open-source project ships with a local control room, Docker Compose setup, a documented Discord adapter, privacy-first defaults, test fixtures, and clear extension boundaries.

## FAQ
**Does it record every voice channel?** No. Recording begins only after an operator explicitly starts an approved meeting and confirms the disclosure.

**Does it require an AI service?** No. Meeting lifecycle, transcript import, exports, and the operator console run without an LLM. Optional enrichment is a future adapter with a strict review boundary.

**Does it solve consent law?** No. It records disclosure and acknowledgement evidence, but operators must configure lawful notice, access, retention, and deletion practices for their jurisdiction and community.

**Does it send tasks into other tools?** No. It can produce local review candidates only. External write integrations are out of scope for 0.1.

**Can I host it publicly?** The reference setup is localhost-first. If an operator exposes it, they are responsible for adding real authentication, TLS, network restrictions, and a threat review.
