# Release evidence

This file is updated only with commands actually run and results actually observed. It intentionally distinguishes local-core verification from a real Discord voice test.

## 0.1.0 pre-release evidence

| Check | Observed result |
|---|---|
| Dependency resolution | `uv lock` and `uv sync --extra dev --extra discord` completed. |
| Syntax | `python -m compileall -q src tests scripts` completed. |
| Automated behavior | `pytest -q --basetemp .pytest-local` passed: **6 tests**. |
| Lint | `ruff check .` passed. |
| Type check | `mypy src` passed for 10 source files. |
| Public-source guard | `python scripts/repo_safety_check.py` passed. |
| Compose validation | `docker compose config` passed. |
| Python packaging | `uv build` produced both an sdist and wheel. |
| Docker build and runtime | Dockerfile built successfully; a fresh container's internal `/api/health` returned `{"status":"ok"}`. The build used temporary host networking only because this environment's Docker bridge DNS could not resolve package hosts. |
| Local HTTP user path | A clean local instance returned healthy; create → disclosure → acknowledgement → transcript → finalize → Markdown/JSON export completed. |
| Visual review | The architecture diagram and running local operator console were rendered and reviewed. An initial diagram title overflow was corrected and re-rendered. |

## Deliberately not claimed

- No real Discord voice meeting was joined, recorded, or transcribed.
- No third-party account, public host, production Discord credential, raw recording, or external workflow was used.
- No Docker image build/run evidence is recorded until that command is executed successfully.

## Release decision

**Eligible for public alpha source publication as a local-core release**, provided the pre-publication clean-repository review and GitHub CI confirmation pass. It is **not** eligible to claim live Discord audio recording support.
