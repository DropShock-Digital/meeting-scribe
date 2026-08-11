from __future__ import annotations

import argparse

import uvicorn

from .config import Settings
from .main import create_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="meeting-scribe")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("serve", help="Run the local operator console and API.")
    subparsers.add_parser("print-config", help="Print a non-secret configuration summary.")
    args = parser.parse_args()
    settings = Settings.from_env()
    if args.command == "print-config":
        print(f"bind={settings.bind_host}:{settings.port}")
        print(f"data_dir={settings.data_dir}")
        print(f"discord_enabled={settings.discord_enabled}")
        print(f"allowlisted_channels={len(settings.channel_allowlist)}")
        return
    uvicorn.run(create_app(), host=settings.bind_host, port=settings.port)


if __name__ == "__main__":
    main()
