import datetime
from discord.ext import commands
import discord

from reo.console.logging import logger
from reo.src.checks import checks
import traceback

class on_command(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot

    @commands.Cog.listener()
    async def on_command(self,ctx:commands.Context):
        try:
            # await ctx.command.callback(ctx)
            pass
        except discord.HTTPException as e:
            if e.code == 429:
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.warning(f"Rate limit hit for command: {ctx.command}")
            else:
                logger.error(f"Error executing command: {ctx.command}")
                raise e
        except discord.Forbidden as e:
            logger.error(f"Bot does not have permissions to execute command: {ctx.command}")
            raise e
        except discord.NotFound as e:
            logger.error(f"Message not found for command: {ctx.command}")
            raise e