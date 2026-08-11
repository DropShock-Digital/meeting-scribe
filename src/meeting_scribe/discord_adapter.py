"""Optional Pycord command adapter. It is intentionally not imported by the core."""
from __future__ import annotations

from typing import Any

from .capture import CaptureUnavailableError, require_discord_capture
from .config import Settings
from .service import MeetingService, PolicyError, StateError


class DiscordAdapterUnavailable(RuntimeError):
    pass


def build_bot(settings: Settings, service: MeetingService) -> Any:
    """Build the command bot without silently activating audio capture.

    The adapter has no listener, auto-join behavior, or voice connection. A future
    capture adapter may call the core only after it has proved a successful capture
    start. See ``capture.py`` for the current explicit DAVE compatibility block.
    """
    if not settings.discord_enabled:
        raise DiscordAdapterUnavailable(
            "Discord adapter is disabled. Set MEETING_SCRIBE_DISCORD_ENABLED=true."
        )
    if not settings.discord_token or not settings.discord_guild_id:
        raise DiscordAdapterUnavailable(
            "Discord adapter requires token and guild ID configuration."
        )
    try:
        import discord
    except ImportError as error:
        raise DiscordAdapterUnavailable(
            "Install the optional Discord dependency: uv sync --extra discord"
        ) from error

    intents = discord.Intents.none()
    intents.guilds = True
    intents.voice_states = True
    bot = discord.Bot(intents=intents)

    def permitted(ctx: Any) -> bool:
        return str(ctx.author.id) in settings.operator_allowlist

    @bot.slash_command(
        name="meeting_disclose",
        description="Create an explicitly disclosed meeting record; never starts audio.",
    )
    async def meeting_disclose(ctx: Any, title: str) -> None:
        if not permitted(ctx):
            await ctx.respond("You are not authorized to create a meeting record.", ephemeral=True)
            return
        voice = getattr(ctx.author, "voice", None)
        channel = getattr(voice, "channel", None)
        if channel is None or str(channel.id) not in settings.channel_allowlist:
            await ctx.respond("Join an allowlisted voice channel first.", ephemeral=True)
            return
        try:
            meeting = service.create(
                title=title,
                channel_id=str(channel.id),
                operator_id=str(ctx.author.id),
                disclosure=(
                    "This meeting is being recorded and summarized. Please leave now if you do not consent."
                ),
                confirmed=True,
            )
            await ctx.respond(
                f"Disclosure record created for **{meeting.title}**. "
                "No audio capture has started. A verified capture adapter must explicitly "
                "start it after the disclosure is delivered."
            )
        except (PolicyError, StateError) as error:
            await ctx.respond(str(error), ephemeral=True)

    @bot.slash_command(
        name="meeting_capture_status",
        description="Show whether this deployment can honestly start Discord audio capture.",
    )
    async def meeting_capture_status(ctx: Any) -> None:
        try:
            require_discord_capture()
        except CaptureUnavailableError as error:
            await ctx.respond(f"Capture unavailable: {error}", ephemeral=True)

    @bot.slash_command(name="meeting_stop", description="Finalize a meeting record by ID")
    async def meeting_stop(ctx: Any, meeting_id: str) -> None:
        if not permitted(ctx):
            await ctx.respond("You are not authorized to finalize meeting records.", ephemeral=True)
            return
        try:
            meeting = service.finalize(meeting_id, "discord-operator-stopped")
            await ctx.respond(
                f"Meeting **{meeting.title}** finalized. Export it from the local console."
            )
        except (PolicyError, StateError) as error:
            await ctx.respond(str(error), ephemeral=True)

    return bot


def run_discord_adapter(settings: Settings, service: MeetingService) -> None:
    bot = build_bot(settings, service)
    bot.run(settings.discord_token)
