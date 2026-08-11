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
| Remote CI | GitHub Actions run `31485138123` passed after the capture-claim remediation. |
| Capture-claim remediation | An independent review identified a false `recording` transition after disclosure acknowledgement. The endpoint now stores disclosure evidence while retaining `disclosing`; the fresh Docker runtime returned `409` for transcript ingestion, confirming fail-closed behavior without verified capture. |

## Deliberately not claimed

- No real Discord voice meeting was joined, recorded, or transcribed.
- No third-party account, public host, production Discord credential, raw recording, or external workflow was used.


## Release decision

**Eligible for public alpha source publication as a local-core release.** The public repository and its GitHub CI passed after the initial release; the independent review findings are addressed in the follow-up change-control record. It is **not** eligible to claim live Discord audio recording support.

## Room and provider control-plane change

| Check | Observed result |
|---|---|
| Independent review | Found raw-label/endpoint leakage, false provider-readiness language, unstable room preferences, and catalog-validation gaps. All were remediated before release. |
| Automated behavior | `pytest -q --basetemp .pytest-room-provider-release` passed: **21 tests**. |
| Source gates | `node --check`, `uv lock --check`, `compileall`, Ruff, mypy, repository safety scan, Compose profiles, and whitespace checks passed. |
| Container runtime | A fresh non-root Docker runtime returned a sanitized named room catalog, no configured provider by default, and the same fail-closed capture capability. |
| Visual review | Isolated desktop and full-height 390px renders showed the named room selector, configured-but-unverified provider preference, no raw IDs/secrets, no overflow, and explicit no-join/no-capture/no-AI-request messaging. |

The OpenRouter/Codex/LM Studio choices are **configuration preferences only** in this release. They are not authentication health, provider connectivity, model execution, or a transcript/summarization feature.

### Final publication and deployment proof

- **Remote CI:** GitHub Actions run `31489221289` passed after adding the optional private catalog overlay.
- **Private review deployment:** The existing Tailnet-only container was rebuilt, restored to its Tailnet bind, and returned the two named approved rooms through a sanitized console payload. Capture and all AI providers remain unavailable/unconfigured.

## Human-language interface revision

| Check | Observed result |
|---|---|
| Copy and interaction scope | The room, helper, disclosure, meeting-state, empty-state, export, and review-completion language was rewritten for plain human use; technical labels, raw identifiers, secrets, and implementation detail remain out of the rendered experience. |
| Automated behavior | `pytest -q --basetemp .pytest-copy-release` passed: **21 tests**. The focused post-review check also passed. |
| Source gates | JavaScript syntax, lockfile validation, bytecode compilation, Ruff, mypy, repository safety scan, Compose profiles, and whitespace checks passed. |
| Runtime and visual review | Isolated and deployed desktop plus 390px mobile views were reviewed. A clipped empty-helper label and the user-visible `Offline review` title were found and corrected. Final renders show no clipping, raw IDs, secrets, recording claim, or AI-content claim. |
| Private deployment | The Tailnet-only review container rebuilt healthy and returned the revised page and fail-closed capture state through its intended private path. |
| Remote CI | GitHub Actions run `31491072507` passed for the final overflow fix. |

### Capability-truthfulness follow-up

An independent copy/accessibility review found remaining setup/checking language that could suggest recording or a meeting helper may become usable in this build. It was corrected before this release:

- The page leads with **“Private reviews, not recordings.”** and states that this version cannot join calls or record sound.
- Recording is shown as unavailable; no `ready`, `checking`, `set up`, or `available` path can present it as an action.
- The helper is an unavailable state only. Provider names, configuration state, and protected-provider details are omitted from the control-room and browser-facing configuration responses.
- The helper placeholder is now **“No helper available.”** and was visually checked at desktop and 390px mobile widths.
- **Observed verification:** `21 passed`; JavaScript syntax, lockfile validation, compilation, Ruff, mypy, repository safety scan, normal and Discord-profile Compose validation, a configured-key fixture, rebuilt Tailnet-only container, API boundary check, and deployed desktop review all passed. The fixture and deployment UI exposed no provider name, status, secret, endpoint, raw room ID, or misleading capability claim.
