import datetime,asyncio,discord
from discord.ext import commands

import storage.snipe_data
from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache
import traceback,sys

from reo.style import color
import storage
from reo.engine.Bot import AutoShardedBot

class on_message_delete(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def message_delete_log(self, message: discord.Message):
        try:
            if message.author.bot:
                return
            guilds_log_cache = cache.guilds_log.get(str(message.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {message.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('message_delete_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for message delete log in {message.guild.name}")
            
            embed = discord.Embed(
                title=f'{message.author.display_name}\'s message has been deleted',
                description=f'**__Message Author:__** {message.author.mention}\n**__Author Username:__** {message.author.name}\n**__Author ID:__** {message.author.id}\n\n**__Message Content:__** ```\n{message.content if message.content else "No Content"}```\n**__Message Created At:__** <t:{int(message.created_at.timestamp())}> \n\n**__Delete Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                color=color.red
            )

            if message.attachments:
                embed.add_field(name="Attachments",value="\n".join([attachment.url for attachment in message.attachments]))
            
            if message.embeds:
                for embed in message.embeds:
                    embed.add_field(
                        name="Embed ",
                        value=f"**Title:** {embed.title}\n**Description:** {embed.description}\n**URL:** {embed.url}\n**Type:** {embed.type}\n**Timestamp:** <t:{int(embed.timestamp.timestamp())}>",
                        inline=False
                    )

            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.set_footer(text=f'Message ID: {message.id}')
            await self.bot.log.send(guild=message.guild,embed=embed,type=f"message_delete")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def save_message_snipe_data(self, message: discord.Message):
        try:
            if not message.content:
                return
            if message.author == self.bot.user:
                return
            if message.author.bot:
                return
            await storage.snipe_data.insert(
                channel_id=message.channel.id,
                message_id=message.id,
                type="delete",
                before_content=message.content,
                author_id=message.author.id
            )
            logger.info(f"Message snipe data saved for message {message.id}")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        try:
            asyncio.create_task(self.save_message_snipe_data(message))
        except Exception as e:
            pass

        try:
            asyncio.create_task(self.message_delete_log(message))
        except Exception as e:
            pass
    