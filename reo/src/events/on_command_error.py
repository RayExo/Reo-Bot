import datetime
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks
import traceback

class on_command_error(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self,ctx:commands.Context,error):
        if isinstance(error, (commands.CommandNotFound, commands.MissingRequiredArgument, commands.BadArgument, commands.CommandOnCooldown, commands.CheckFailure)):
            # Handling these below but don't log them as "Errors" in console
            pass
        else:
            logger.error(f"Error in file {__file__}: {repr(error)}")
            logger.error(f"Error in {ctx.command}, Command: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {error}")

        if isinstance(error, commands.CommandOnCooldown):
            # if the colldown type is user, then the error.retry_after will be the time left for the user to use the command again
            if error.type == commands.BucketType.user:
                await ctx.reply(f"**{self.bot.emojis.WARNING} - Command On Cooldown. Retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>**",delete_after=int(error.retry_after))
            elif (error.type == commands.BucketType.guild):
                await ctx.reply(f"**{self.bot.emojis.WARNING} - Command On Guild Cooldown. Retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>**",delete_after=int(error.retry_after))
            elif (error.type == commands.BucketType.channel):
                await ctx.reply(f"**{self.bot.emojis.WARNING} - Command On Channel Cooldown. Retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>**",delete_after=int(error.retry_after))
            elif (error.type == commands.BucketType.category):
                await ctx.reply(f"**{self.bot.emojis.WARNING} - Command On Member Cooldown. Retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>**",delete_after=int(error.retry_after))
            elif (error.type == commands.BucketType.member):
                await ctx.reply(f"**{self.bot.emojis.WARNING} - Command On Member Cooldown. Retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>**",delete_after=int(error.retry_after))
            elif (error.type == commands.BucketType.role):
                await ctx.reply(f"**{self.bot.emojis.WARNING} - Command On Role Cooldown. Retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>**",delete_after=int(error.retry_after))
            else:
                await ctx.reply(f"**{self.bot.emojis.WARNING} - Command On Cooldown. Retry <t:{int(datetime.datetime.now().timestamp() + error.retry_after)}:R>**",delete_after=int(error.retry_after))
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"**{self.bot.emojis.WARNING} - Missing Required Argument.\nUsage: `{ctx.prefix}{ctx.command} {ctx.command.signature}`**",delete_after=5)
        if isinstance(error, commands.BadArgument):
            await ctx.reply(f"**{self.bot.emojis.WARNING} - Bad Argument.\nUsage: `{ctx.prefix}{ctx.command} {ctx.command.signature}`**",delete_after=5)
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"**{self.bot.emojis.WARNING} - Missing Permissions.\nYou need to have {error.missing_perms} permissions to run this command.**",delete_after=5)
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(f"**{self.bot.emojis.WARNING} - Bot Missing Permissions.\nI need to have {error.missing_perms} permissions to run this command.**",delete_after=5)
        if isinstance(error, commands.NotOwner):
            await ctx.reply(f"**{self.bot.emojis.WARNING} - Not Owner.\nYou need to be the owner of the bot to run this command.**",delete_after=5)
        if isinstance(error, commands.CheckFailure):
            if checks.check_ignore_predicate in ctx.command.checks:
                if not checks.check_ignore_predicate(ctx):
                    return
                
            if checks.check_blacklist_predicate in ctx.command.checks:
                if not checks.check_blacklist_predicate(ctx):
                    return
                
            if checks.check_is_admin_predicate in ctx.command.checks:
                if not checks.check_is_admin_predicate(ctx.author):
                    await ctx.reply(f"**{self.bot.emojis.WARNING} - Admin Only. You need to be an admin to run this command.**",delete_after=5)
            
            if checks.check_is_owner_predicate in ctx.command.checks:
                if not checks.check_is_owner_predicate(ctx):
                    await ctx.reply(f"**{self.bot.emojis.WARNING} - Owner Only. You need to be the owner of the bot to run this command.**",delete_after=5)
