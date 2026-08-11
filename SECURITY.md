# Security policy

## Supported versions
Only the latest `0.x` release line receives fixes.

## Reporting a vulnerability
Do not open a public issue for a vulnerability involving recordings, transcripts, authentication, or Discord tokens. Use GitHub private vulnerability reporting for this repository when available, or contact the maintainers through the organization profile with a minimal reproduction and no secrets.

## Security model
Meeting Scribe is localhost-first. A publicly exposed deployment is unsupported until the operator adds an authenticated reverse proxy, TLS, network restrictions, backups, and a separate deployment threat review. Discord tokens belong in a protected runtime secret store or local `.env`, never Git.
