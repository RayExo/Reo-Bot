import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache

import traceback,sys

from reo.style import color

from reo.engine.Bot import AutoShardedBot

import requests


class on_guild_join(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot
    
    async def send_join_server_notification(self, guild:discord.Guild):
        try:
            logger.info(f"Joined Guild {guild.name} ({guild.id})")
            if self.bot.cache.ban_data.get('guilds').get(str(guild.id)):
                await guild.owner.send(embed=discord.Embed(
                    title=f"Your Guild {guild.name} is banned from using {self.bot.user.name}",
                    description=f"If you think this is a mistake, please join our Support Server and contact the Management Team",
                    color=color.red
                ),
                view=discord.ui.View().add_item(discord.ui.Button(label="Support Server",url=self.bot.urls.SUPPORT_SERVER,style=discord.ButtonStyle.link,emoji=self.bot.emoji.SUPPORT))
                )
                await guild.leave()
                return logger.warning(f"Guild {guild.name} ({guild.id}) is banned from using {self.bot.user.name}")


            await asyncio.sleep(5)
            inviter = None
            async for entry in guild.audit_logs(limit=3,action=discord.AuditLogAction.bot_add):
                if entry.target == self.bot.user:
                    inviter = entry.user
                    break

            webhook_url = self.bot.channels.guild_join_webhook
            
            embed = discord.Embed(
                title="Guild Joined",
                description=f"> {self.bot.emoji.NAME} **Name:** {guild.name}\n> {self.bot.emoji.ID} **ID:** {guild.id}\n> {self.bot.emoji.MEMBER} **Members:** {guild.member_count}\n> {self.bot.emoji.OWNER} **Owner:** {guild.owner.mention} ({guild.owner.id})\n> {self.bot.emoji.INVITE} **Inviter:** {f'{inviter.mention} ({inviter.id})' if inviter else 'Unknown'}",
                color=color.green
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.set_footer(text=f"Guild Count: {len(self.bot.guilds)}")

            if webhook_url:
                requests.post(webhook_url,json={"embeds":[embed.to_dict()]})
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    async def send_notify_to_server_owner(self, guild:discord.Guild):
        try:
            owner = guild.owner
            await owner.send(embed=discord.Embed(
                title="Thank you for adding me to your server",
                description=f"Hello {owner.mention},\n\nThank you for adding me to your server. I am {self.bot.user.name} and I am here to help you manage your server.\n\nTo get started, you can use the command `{self.bot.BotConfig.PREFIX}help` to get a list of commands that I can do.\n\nIf you have any questions or need help, you can join our Support Server by clicking the button below.",
                color=color.green
            ),
            view=discord.ui.View().add_item(discord.ui.Button(label="Support Server",url=self.bot.urls.SUPPORT_SERVER,style=discord.ButtonStyle.link,emoji=self.bot.emoji.SUPPORT))
            )
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild:discord.Guild):
        try:
            asyncio.create_task(self.send_join_server_notification(guild))
        except:
            pass
        try:
            asyncio.create_task(self.send_notify_to_server_owner(guild))
        except:
            pass