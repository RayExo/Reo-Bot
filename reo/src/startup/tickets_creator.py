from reo.memory.cache import cache
from reo.console.logging import logger
from discord.ext import commands

import asyncio
from storage import ticket_settings as ticket_settings_db
from storage import tickets as tickets_db

from reo.src.modules import ticket_panel

import traceback

resumed = False

async def resume_ticket_creator(bot: commands.Bot):
    global resumed
    if resumed:
        return logger.info("Ticket Creator already resumed")
    
    resumed = True
    
    # Wait for the bot to be ready
    while not bot.is_ready():
        # logger.info("Waiting for bot to be ready in Ticket Creator Resume")
        await asyncio.sleep(1)
    
    async def create_ticket_message(data,bot):
        try:
            await ticket_panel.send_ticket_panel_message(data,bot)
            logger.info(f"Resumed Ticket Creator for {data.get('guild_id')} - Module {data.get('ticket_module_id')}")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")    

    async def create_ticket_message_guild(guild_id, ticket_modules):
        try:
            logger.info(f"Resuming Ticket Creator for guild {guild_id}")
            guild = bot.get_guild(int(guild_id))
            
            if not guild:
                logger.error(f"Guild {guild_id} not found for Ticket Creator")
                return
            
            logger.info(f"Total Ticket Modules in Cache for {guild.name}: {len(ticket_modules)}")
            for ticket_module_id, data in ticket_modules.items():
                asyncio.create_task(create_ticket_message(data,bot))
        except Exception as e:
            logger.error(f"Error while resuming ticket modules for guild {guild_id}: {e}")

    logger.info(f"Total Ticket Modules in Cache Guilds: {len(cache.ticket_settings)}")

    for guild_id, ticket_modules in cache.ticket_settings.items():
        try:
            asyncio.create_task(create_ticket_message_guild(guild_id, ticket_modules))
        except Exception as e:
            logger.error(f"Failed to create task for guild {guild_id}: {e}")

    logger.info("Resumed Ticket Creator for all guilds")


ticket_closed_resumed = False
async def resume_ticket_closer(bot: commands.Bot):
    global ticket_closed_resumed
    if ticket_closed_resumed:
        return logger.info("Ticket Closer already resumed")
    
    ticket_closed_resumed = True
    
    # Wait for the bot to be ready
    while not bot.is_ready():
        # logger.info("Waiting for bot to be ready in Ticket Closer Resume")
        await asyncio.sleep(1)
    
    async def close_ticket(data,bot):
        try:
            await ticket_panel.send_close_ticket_module(data,bot)
            logger.info(f"Resumed Ticket Closer for {data.get('guild_id')} - Module {data.get('ticket_module_id')}")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")    


    for ticket in await tickets_db.gets(closed=False):
        try:
            asyncio.create_task(close_ticket(ticket,bot))
        except Exception as e:
            logger.error(f"Failed to create task for ticket module {ticket.get('id')}: {e}")

    logger.info("Resumed Ticket Closer for all guilds")
