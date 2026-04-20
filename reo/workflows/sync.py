import asyncio

import storage

from reo.console.logging import logger


async def load_storage():
    tasks = [
        storage.guilds.create_table(),
        storage.guilds_log.create_table(),
        storage.users.create_table(),
        storage.j2c.create_table(),
        storage.j2c_settings.create_table(),
        storage.antinuke_settings.create_table(),
        storage.antinuke_bypass.create_table(),
        storage.welcomer_settings.create_table(),
        storage.guilds_backup.create_table(),
        storage.redeem_codes.create_table(),
        storage.afk.create_table(),
        storage.snipe_data.create_table(),
        storage.ignore_data.create_table(),
        storage.ban_data.create_table(),
        storage.command_access.create_table(),
        storage.automod.create_table(),
        storage.custom_roles.create_table(),
        storage.custom_roles_permissions.create_table(),
        storage.media_channels.create_table(),
        storage.auto_responder.create_table(),
        storage.giveaways.create_table(),
        storage.giveaway_participants.create_table(),
        storage.giveaways_permissions.create_table(),
        storage.ticket_settings.create_table(),
        storage.tickets.create_table(),
        storage.shop.create_table(),
        storage.music.create_table(),
    ]
    await asyncio.gather(*tasks)
    logger.database("Storage collections loaded")


loadDataBase = load_storage
