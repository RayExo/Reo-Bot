import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot

class on_invite_create(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def invite_create_log(self,invite:discord.Invite):
        try:
            guilds_log_cache = cache.guilds_log.get(str(invite.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {invite.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('invite_create_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for invite create log in {invite.guild.name}")
            
            created_by = invite.inviter
            if not created_by:
                user = "Vanity URL"
                user_id = "Vanity URL"
                user_avatar = invite.guild.icon.url if invite.guild.icon else None
            else:
                user = created_by.mention
                user_id = created_by.id
                user_avatar = created_by.display_avatar.url
            
            embed = discord.Embed(
                title=f'Invite {invite.code} has been created',
                description=f'**__Invite:__** [Link Here](https://discord.gg/{invite.code})\n**__Invite Code:__** `{invite.code}`\n\n**__Created By:__** {user}\n**__Created By ID:__** `{user_id}`\n\n**__Invite Created At:__** <t:{int(invite.created_at.timestamp())}>',
                color=color.green
            )

            embed.set_footer(text=f'Invite Code: https://discord.gg/{invite.code}')
            embed.set_thumbnail(url=user_avatar)
            await self.bot.log.send(guild=invite.guild,embed=embed,type=f"invite_create")
        except Exception as e:
            logger.error(f"Error in on_invite_create.invite_create_log: {e}")

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        try:
            asyncio.create_task(self.invite_create_log(invite))
        except Exception as e:
            pass