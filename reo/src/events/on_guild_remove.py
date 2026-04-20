import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache

import traceback,sys

from reo.style import color

from reo.engine.Bot import AutoShardedBot
import requests

class on_guild_remove(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    @commands.Cog.listener()
    async def on_guild_remove(self, guild:discord.Guild):
        try:
            logger.info(f"Left Guild {guild.name} ({guild.id})")
            webhook_url = self.bot.channels.guild_leave_webhook
            
            embed = discord.Embed(
                title="Guild Left",
                description=f"> {self.bot.emoji.NAME} **Name:** {guild.name}\n> {self.bot.emoji.ID} **ID:** {guild.id}\n> {self.bot.emoji.MEMBER} **Members:** {guild.member_count}\n> {self.bot.emoji.OWNER} **Owner:** {guild.owner.name if guild.owner else 'Unknown'}",
                color=color.red
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.set_footer(text=f"Guild Count: {len(self.bot.guilds)}")

            if webhook_url:
                requests.post(webhook_url,json={"embeds":[embed.to_dict()]})
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")