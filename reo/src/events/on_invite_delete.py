import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot


class on_invite_delete(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def invite_delete_log(self,invite:discord.Invite):
        try:
            guilds_log_cache = cache.guilds_log.get(str(invite.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {invite.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('invite_delete_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for invite delete log in {invite.guild.name}")
            
            async def check_entry():
                async for entry in invite.guild.audit_logs(limit=1,action=discord.AuditLogAction.invite_delete):
                    if entry.target.code == invite.code:
                        return entry
                    
            entry = await check_entry()

            if entry:
                user = entry.user.mention
                user_id = entry.user.id
                user_avatar = entry.user.display_avatar.url
            else:
                user = "Unknown"
                user_id = "Unknown"
                user_avatar = invite.guild.icon.url if invite.guild.icon else None

            embed = discord.Embed(
                title=f'Invite {invite.code} has been deleted',
                description=f'**__Invite:__** [Link Here](https://discord.gg/{invite.code})\n**__Invite Code:__** `{invite.code}`\n\n**__Deleted By:__** {user}\n**__Deleted By ID:__** `{user_id}`\n\n**__Invite Deleted At:__** <t:{int(datetime.datetime.now().timestamp())}>',
                color=color.red
            )
            embed.set_footer(text=f'Invite Code: https://discord.gg/{invite.code}')
            embed.set_thumbnail(url=user_avatar)
            await self.bot.log.send(guild=invite.guild,embed=embed,type=f"invite_delete")
        except Exception as e:
            logger.error(f"Error in on_invite_delete.invite_delete_log: {e}")

    delete_invite_timeouts = {}
    async def anti_invite_delete_module(self,invite:discord.Invite):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(invite.guild.id))
            if not anti_nuke_cache:
                return
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {invite.guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_invite_delete'):
                return logger.warning(f"Guild {invite.guild.name} has anti invite delete disabled")
            
            async def check_entry():
                async for entry in invite.guild.audit_logs(limit=1,action=discord.AuditLogAction.invite_delete,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.code == invite.code:
                        return entry
            entry = await check_entry()
            if entry:
                deleter = entry.user
                if deleter == self.bot.user:
                    return logger.warning(f"Invite {invite.code} was deleted by the bot")
            else:
                return logger.warning(f"Invite {invite.code} was not deleted by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(invite.guild.id),{}).get(str(deleter.id),{})
            if anti_nuke_bypass_cache.get('anti_invite_delete'):
                return logger.warning(f"User {deleter} is bypassed from anti invite delete")
            
            if deleter.id == invite.guild.owner.id or await checks.check_is_owner_raw(deleter,invite.guild):
                return logger.warning(f"Invite {invite.code} was deleted by the owner")
            if deleter.top_role.position >= invite.guild.me.top_role.position:
                return logger.warning(f"Invite {invite.code} was deleted by a user with a higher role than the bot")
            
            # ==================================
            if str(invite.guild.id) not in self.delete_invite_timeouts:
                self.delete_invite_timeouts[str(invite.guild.id)] = {}
            if str(deleter.id) not in self.delete_invite_timeouts.get(str(invite.guild.id)):
                self.delete_invite_timeouts[str(invite.guild.id)][str(deleter.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.delete_invite_timeouts[str(invite.guild.id)][str(deleter.id)]['count'] += 1
            self.delete_invite_timeouts[str(invite.guild.id)][str(deleter.id)]['created_at'] = datetime.datetime.now()


            if str(invite.guild.id) in self.delete_invite_timeouts:
                if self.delete_invite_timeouts.get(str(invite.guild.id)):
                    if self.delete_invite_timeouts.get(str(invite.guild.id),{}).get(str(deleter.id)):
                        if (self.delete_invite_timeouts.get(str(invite.guild.id),{}).get(str(deleter.id),{}).get('count') >= anti_nuke_cache.get('anti_invite_delete_limit',1)
                            and
                            self.delete_invite_timeouts.get(str(invite.guild.id),{}).get(str(deleter.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_invite_delete_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {invite.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{invite.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Invite Delete\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=invite.guild.icon.url if invite.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Invite Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await invite.guild.ban(deleter,reason="Banned by Antinuke System: Anti Invite Delete")
                                    await self.bot.antinuke_log.send(guild=invite.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_invite_delete.anti_invite_delete_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{invite.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Invite Delete\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=invite.guild.icon.url if invite.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Invite Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await invite.guild.kick(deleter,reason="Kicked by Antinuke System: Anti Invite Delete")
                                    await self.bot.antinuke_log.send(guild=invite.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_invite_delete.anti_invite_delete_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{invite.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Invite Delete\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=invite.guild.icon.url if invite.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Invite Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=invite.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_invite_delete.anti_invite_delete_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{invite.guild.name}`**\n**Details:** ```\nYou have been muted for Anti Invite Delete\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=invite.guild.icon.url if invite.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Invite Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    try:
                                        await deleter.edit(roles=[],reason="Muted by Antinuke System: Anti Invite Delete")
                                    except:
                                        pass
                                    await deleter.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Invite Delete")
                                    await self.bot.antinuke_log.send(guild=invite.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_invite_delete.anti_invite_delete_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {invite.guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(invite.guild.id) in self.delete_invite_timeouts:
                                    if str(deleter.id) in self.delete_invite_timeouts.get(str(invite.guild.id)):
                                        self.delete_invite_timeouts[str(invite.guild.id)][str(deleter.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        

        except Exception as e:
            logger.error(f"Error in on_invite_delete.anti_invite_delete_module: {e}")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        try:
            asyncio.create_task(self.anti_invite_delete_module(invite))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.invite_delete_log(invite))
        except Exception as e:
            pass