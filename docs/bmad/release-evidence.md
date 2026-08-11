# Release evidence

This file is updated only with commands actually run and results actually observed. It intentionally distinguishes local-core verification from a real Discord voice test.

## 0.1.0 pre-release evidence

| Check | Observed result |
|---|---|
| Dependency resolution | `uv lock` and `uv sync --extra dev --extra discord` completed. |
| Syntax | `python -m compileall -q src tests scripts` completed. |
| Automated behavior | `pytest -q --basetemp .pytest-control-room-commit` passed: **12 tests**, including atomic lifecycle protection, Discord CLI wiring, sanitized control-room state, and non-capturing offline-review records. |
| Lint | `ruff check .` passed. |
| Type check | `mypy src` passed for 10 source files. |
| Public-source guard | `python scripts/repo_safety_check.py` passed. |
| Compose validation | `docker compose config` and `docker compose --profile discord config` passed. |
| Python packaging | `uv build` produced both an sdist and wheel. |
| Docker build and runtime | The control-room image built successfully. A fresh non-root container reached healthy state, returned `/api/health`, and returned a sanitized `/api/console` payload. The build used temporary host networking only because this environment's Docker bridge DNS could not resolve package hosts. |
| Control-room user path | A clean instance created an offline review record, kept it out of `recording`, exposed Markdown/JSON exports, and finalized it successfully. |
| Visual review | Desktop and 390px mobile renders were reviewed in no-gateway, no-capture, and offline-review states. A misleading offline-review headline was found and corrected before release. |
| Private deployment | The Dockerized control room was rebuilt and verified through its Tailscale-bound address. Docker reports a single binding to the host's Tailscale IPv4 address; no public tunnel or Funnel was configured. |
| Remote CI | GitHub Actions run `31484082709` passed for the control-room release. |

## Deliberately not claimed

- No real Discord voice meeting was joined, recorded, or transcribed.
- No third-party account, public host, production Discord credential, raw recording, or external workflow was used.


## Release decision

**Eligible for public alpha source publication as a local-core release.** The public repository and its GitHub CI passed after the initial release; the independent review findings are addressed in the follow-up change-control record. It is **not** eligible to claim live Discord audio recording support.
