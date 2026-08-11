#!/usr/bin/env python3
"""Fail closed on common private deployment and credential leakage patterns."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "_bmad",
    ".agents",
    "dist",
    ".mypy_cache",
    ".pytest-local",
    ".pytest_cache",
    ".ruff_cache",
}
RULES = {
    "private_host_path": re.compile(r"/(?:home/ubuntu|srv/olympus|host/srv)(?:/|$)"),
    "tailnet_address": re.compile(r"100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "discord_secret_value": re.compile(
        r"(?i)(?:discord[_ -]?(?:token|secret)|meeting_scribe_discord_token)"
        r"[ \t]*[:=][ \t]*['\"]?[a-z0-9._-]{20,}"
    ),
    "private_dns": re.compile(r"[\w-]+\.(?:ts\.net|lab)"),
}


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(
            part in SKIP_PARTS or part.startswith(".pytest-") for part in path.parts
        ):
            continue
        if path == Path(__file__):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(
                f"{path.relative_to(ROOT)}: binary file is not allowed in initial public source"
            )
            continue
        for name, pattern in RULES.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)}: {name}")
    if findings:
        print("Repository safety check failed:")
        print("\n".join(f"- {finding}" for finding in findings))
        return 1
    print("Repository safety check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
