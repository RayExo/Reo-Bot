from reo.memory.cache import cache
from reo.console.logging import logger
from discord.ext import commands

import asyncio
from storage import giveaways as giveaway_db

resumed = False

async def resume_active_giveaway(bot: commands.Bot):
    global resumed
    if resumed:
        return logger.info("Giveaway Controller already resumed")
    
    resumed = True
    
    # Wait for the bot to be ready
    while not bot.is_ready():
        logger.info("Waiting for bot to be ready in Giveaway Controller Resume")
        await asyncio.sleep(1)
    
    async def create_giveaway_message(guild, data):
        try:
            channel = guild.get_channel(int(data.get("channel_id")))
            if not channel:
                await giveaway_db.delete(id=data.get("id"))
                return
            
            giveaway_cog = bot.get_cog("Giveaway")
            if giveaway_cog:
                await giveaway_cog.create_giveaway_message(data, channel=channel)
                logger.info(f"Resumed Giveaway Controller for {channel.name}")
            else:
                logger.error("Giveaway cog not found")
        except Exception as e:
            logger.error(f"Error while creating giveaway message: {e}")

    async def create_giveaway_message_guild(guild_id, giveaways):
        try:
            logger.info(f"Resuming Giveaway Controller for guild {guild_id}")
            guild = bot.get_guild(int(guild_id))
            
            if not guild:
                logger.error(f"Guild {guild_id} not found for Giveaway Controller")
                return
            
            logger.info(f"Total Giveaways in Cache for {guild.name}: {len(giveaways)}")
            for giveaway_id, data in giveaways.items():
                asyncio.create_task(create_giveaway_message(guild, data))
        except Exception as e:
            logger.error(f"Error while resuming giveaways for guild {guild_id}: {e}")

    logger.info(f"Total Giveaways in Cache Guilds: {len(cache.giveaways)}")
    
    for guild_id, giveaways in cache.giveaways.items():
        try:
            asyncio.create_task(create_giveaway_message_guild(guild_id, giveaways))
        except Exception as e:
            logger.error(f"Failed to create task for guild {guild_id}: {e}")
