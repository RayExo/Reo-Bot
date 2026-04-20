import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot


class on_member_unban(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def unban_log(self, guild: discord.Guild, user: discord.User):
        try:
            logger.info(f"Fetching unban log for {user.name} in {guild.name}")
            guilds_log_cache = cache.guilds_log.get(str(guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('member_unban_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for member unban log in {guild.name}")
            
            async def check_for_entry():
                async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.unban,after=datetime.datetime.now()-datetime.timedelta(minutes=1)):
                    if entry.target.id == user.id:
                        return entry
                return None
            
            entry = await check_for_entry()
            if entry:
                action = 'unban'
                action_by = entry.user
                reason = entry.reason
                if action_by == self.bot.user:
                    return logger.info(f"Bot unbanned {user.name} in {guild.name}")
            else:
                action = 'unban'
                action_by = "Unknown"
                reason = "No Reason Provided"

            embed = discord.Embed(
                title=f'{user.display_name} has been unbanned',
                description=f'**__User:__** {user.mention}\n**__Username:__** {user.name}\n**__User ID:__** {user.id}\n\n**__Action:__** {action}\n**__Reason:__** {reason}\n**__Action By:__** {action_by.mention}\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                color=color.green
            )
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f'User ID: {user.id}')
            await self.bot.log.send(guild=guild,embed=embed,type=f"member_{action}")
        except Exception as e:
            logger.error(f"Error in on_member_unban.unban_log: {e}")

    unban_user_timeouts = {}
    async def anti_unban_module(self,unban:discord.User,guild:discord.Guild):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(guild.id))
            if not anti_nuke_cache:
                return
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_member_unban'):
                return logger.warning(f"Guild {guild.name} has anti member unban disabled")
            
            async def check_entry():
                async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.unban,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == unban.id:
                        return entry
            entry = await check_entry()
            if entry:
                unbanner = entry.user
                if unbanner == self.bot.user:
                    return logger.warning(f"User {unban} was unbanned by the bot")
            else:
                return logger.warning(f"User {unban} was not unbanned by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(guild.id),{}).get(str(unbanner.id),{})
            if anti_nuke_bypass_cache.get('anti_member_unban'):
                return logger.warning(f"User {unbanner} is bypassed from anti member unban")
            
            if unbanner.id == guild.owner.id or await checks.check_is_owner_raw(unbanner,guild):
                return logger.warning(f"User {unban} was unbanned by the owner")
            if unbanner.top_role.position >= guild.me.top_role.position:
                return logger.warning(f"User {unban} was unbanned by a user with a higher role than the bot")
            
            # ==================================
            if str(guild.id) not in self.unban_user_timeouts:
                self.unban_user_timeouts[str(guild.id)] = {}
            if str(unbanner.id) not in self.unban_user_timeouts.get(str(guild.id)):
                self.unban_user_timeouts[str(guild.id)][str(unbanner.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.unban_user_timeouts[str(guild.id)][str(unbanner.id)]['count'] += 1
            self.unban_user_timeouts[str(guild.id)][str(unbanner.id)]['created_at'] = datetime.datetime.now()
            
            if str(guild.id) in self.unban_user_timeouts:
                if self.unban_user_timeouts.get(str(guild.id)):
                    if self.unban_user_timeouts.get(str(guild.id),{}).get(str(unbanner.id)):
                        if (self.unban_user_timeouts.get(str(guild.id),{}).get(str(unbanner.id),{}).get('count') >= anti_nuke_cache.get('anti_member_unban_limit',1)
                            and
                            self.unban_user_timeouts.get(str(guild.id),{}).get(str(unbanner.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_member_unban_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Member Unban\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(unbanner,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {unbanner.mention}\n**__ID__**: `{unbanner.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Member Unban\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=unbanner.display_avatar.url)
                                    await guild.ban(unbanner,reason="Banned by Antinuke System: Anti Member Unban")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_unban_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Member Unban\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(unbanner,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {unbanner.mention}\n**__ID__**: `{unbanner.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Member Unban\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=unbanner.display_avatar.url)
                                    await guild.kick(unbanner,reason="Kicked by Antinuke System: Anti Member Unban")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_unban_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been warned for Anti Member Unban\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(unbanner,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {unbanner.mention}\n**__ID__**: `{unbanner.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Member Unban\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=unbanner.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_unban_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Member Unban\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(unbanner,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {unbanner.mention}\n**__ID__**: `{unbanner.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Member Unban\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=unbanner.display_avatar.url)
                                    try:
                                        await unbanner.edit(roles=[],reason="Muted by Antinuke System: Anti Member Unban")
                                    except:
                                        pass
                                    await unbanner.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Member Unban")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_unban_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(guild.id) in self.unban_user_timeouts:
                                    if str(unbanner.id) in self.unban_user_timeouts.get(str(guild.id)):
                                        self.unban_user_timeouts[str(guild.id)][str(unbanner.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        

        except Exception as e:
            logger.error(f"Error in on_member_remove.anti_unban_module: {e}")



    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        try:
            asyncio.create_task(self.anti_unban_module(user,guild))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.unban_log(guild, user))
        except Exception as e:
            logger.error(f"Error in on_member_unban: {e}")