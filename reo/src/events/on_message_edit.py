import datetime,asyncio,discord
from discord.ext import commands
import asyncio
import storage.snipe_data
from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache

import traceback,sys
import storage
from reo.style import color

from reo.engine.Bot import AutoShardedBot

class on_message_edit(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot
    
    async def message_edit_log(self, before: discord.Message, after: discord.Message):
        try:
            if before.author.bot:
                return
            guilds_log_cache = cache.guilds_log.get(str(before.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {before.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('message_edit_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for message edit log in {before.guild.name}")
            
            embed = discord.Embed(
                title=f'{before.author.display_name}\'s message has been edited',
                description=f'**__Message Author:__** {before.author.mention}\n**__Author Username:__** {before.author.name}\n**__Author ID:__** {before.author.id}\n\n**__Before Edit:__** ```\n{before.content if before.content else "No Content"}```\n**__After Edit:__** ```\n{after.content if after.content else "No Content"}```\n**__Message Created At:__** <t:{int(before.created_at.timestamp())}> \n\n**__Edit Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                color=color.white
            )
            embed.set_thumbnail(url=before.author.display_avatar.url)
            embed.set_footer(text=f'Message ID: {before.id}')
            
            await self.bot.log.send(guild=before.guild,embed=embed,type=f"message_edit")
        except Exception as e:
            logger.error(f"Error in on_message_edit.message_edit_log: {e}")
    
    async def save_message_edit_data(self, before: discord.Message, after: discord.Message):
        try:
            if not after.content:
                return
            if after.author == self.bot.user:
                return
            if before.content == after.content:
                return
            if before.author.bot:
                return
            await storage.snipe_data.insert(
                channel_id=before.channel.id,
                message_id=before.id,
                type="edit",
                before_content=before.content,
                after_content=after.content,
                author_id=before.author.id
            )
            logger.info(f"Message edit data saved for message {before.id}")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        try:
            asyncio.create_task(self.message_edit_log(before, after))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.save_message_edit_data(before, after))
        except Exception as e:
            pass