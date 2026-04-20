import asyncio
import importlib

from reo.bridge import lavalink
from reo.console.logging import logger
from reo.engine.Bot import AutoShardedBot
from reo.src.startup import tickets_creator
from reo.workflows.startup import (
    check_guilds_subscription,
    check_users_subscription,
    resume_afk_functions,
)

from .commands.automod import Automod
from .commands.fun import Fun
from .commands.giveaway import Giveaway
from .commands.help import Help
from .commands.mention import MentionReply
from .commands.moderation import Moderation
from .commands.more import More
from .commands.music import Music
from .commands.root import Root
from .commands.security import Security
from .commands.ticket import Ticket
from .commands.utils import Utils
from .commands.voice import Voice
from .commands.welcomer import Welcomer
from .events.message import message
from .events.on_command import on_command
from .events.on_command_error import on_command_error
from .events.on_guild_channel_create import on_guild_channel_create
from .events.on_guild_channel_delete import on_guild_channel_delete
from .events.on_guild_channel_update import on_guild_channel_update
from .events.on_guild_emojis_update import on_guild_emojis_update
from .events.on_guild_join import on_guild_join
from .events.on_guild_remove import on_guild_remove
from .events.on_guild_role_create import on_guild_role_create
from .events.on_guild_role_delete import on_guild_role_delete
from .events.on_guild_role_update import on_guild_role_update
from .events.on_guild_update import on_guild_update
from .events.on_invite_create import on_invite_create
from .events.on_invite_delete import on_invite_delete
from .events.on_member_join import on_member_join
from .events.on_member_remove import on_member_remove
from .events.on_member_unban import on_member_unban
from .events.on_member_update import on_member_update
from .events.on_message_delete import on_message_delete
from .events.on_message_edit import on_message_edit
from .events.on_voice_state_update import on_voice_state_update
from .events.on_webhooks_update import on_webhooks_update
from .events.ready import ready
from .events.wavelink import Wavelink


async def setup(bot: AutoShardedBot):
    units_to_mount = [
        Utils(bot=bot),
        Security(bot=bot),
        Automod(bot=bot),
        Moderation(bot=bot),
        Ticket(bot=bot),
        Welcomer(bot=bot),
        Music(bot=bot),
        Giveaway(bot=bot),
        Help(bot=bot),
        Fun(bot=bot),
        Voice(bot=bot),
        More(bot=bot),
        Root(bot=bot),
        on_command(bot=bot),
        Wavelink(bot=bot),
        message(bot=bot),
        on_guild_join(bot=bot),
        on_guild_remove(bot=bot),
        on_member_join(bot=bot),
        on_member_remove(bot=bot),
        ready(bot=bot),
        on_command_error(bot=bot),
        on_member_unban(bot=bot),
        on_member_update(bot=bot),
        on_message_delete(bot=bot),
        on_message_edit(bot=bot),
        on_guild_channel_create(bot=bot),
        on_guild_channel_delete(bot=bot),
        on_guild_channel_update(bot=bot),
        on_guild_role_create(bot=bot),
        on_guild_role_delete(bot=bot),
        on_guild_role_update(bot=bot),
        on_guild_emojis_update(bot=bot),
        on_voice_state_update(bot=bot),
        on_webhooks_update(bot=bot),
        on_invite_create(bot=bot),
        on_invite_delete(bot=bot),
        on_guild_update(bot=bot),
        MentionReply(bot=bot),
    ]

    await asyncio.gather(*[bot.add_cog(unit) for unit in units_to_mount])
    logger.cog(f"Mounted {len(units_to_mount)} src units")

    try:
        importlib.reload(lavalink)
        asyncio.create_task(lavalink.on_node(bot))
    except Exception:
        pass

    try:
        asyncio.create_task(check_guilds_subscription(bot))
    except Exception:
        pass

    try:
        asyncio.create_task(check_users_subscription(bot))
    except Exception:
        pass

    try:
        asyncio.create_task(resume_afk_functions(bot))
    except Exception:
        pass

    try:
        asyncio.create_task(tickets_creator.resume_ticket_creator(bot))
    except Exception:
        pass
    logger.cog("Ticket creator restored")

    try:
        asyncio.create_task(tickets_creator.resume_ticket_closer(bot))
    except Exception:
        pass
    logger.cog("Ticket closer restored")
    logger.success("REO runtime is online")
