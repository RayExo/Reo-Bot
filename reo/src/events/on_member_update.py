import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot


class on_member_update(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def member_update_log(self, member_before: discord.Member, member_after: discord.Member):
        try:
            guilds_log_cache = cache.guilds_log.get(str(member_after.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {member_after.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('member_update_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for member update log in {member_after.guild.name}")

            async def check_for_entry():
                async for entry in member_after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_role_update, after=datetime.datetime.now() - datetime.timedelta(minutes=1)):
                    if entry.target.id == member_after.id:
                        return entry
                async for entry in member_after.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update, after=datetime.datetime.now() - datetime.timedelta(minutes=1)):
                    if entry.target.id == member_after.id:
                        return entry
                
                return None

            entry = await check_for_entry()
            if not entry:
                return logger.info(f"No entry found for {member_after.name} in {member_after.guild.name}")

            action = entry.action
            action_by = entry.user
            reason = entry.reason
            if action_by == self.bot.user:
                return logger.info(f"Bot updated {member_after.name} in {member_after.guild.name}")

            changes = []
            if member_before.display_name != member_after.display_name:
                changes.append(f"**Nickname:** `{member_before.display_name} -> {member_after.display_name}`")
            if member_before.roles != member_after.roles:
                before_roles = set(member_before.roles)
                after_roles = set(member_after.roles)
                added_roles = after_roles - before_roles
                removed_roles = before_roles - after_roles
                if added_roles:
                    added_role_names = "\n".join([role.name for role in added_roles])
                    changes.append(f"**Roles Added:** ```\n{added_role_names}```")
                if removed_roles:
                    removed_role_names = "\n".join([role.name for role in removed_roles])
                    changes.append(f"**Roles Removed:** ```\n{removed_role_names}```")
            if member_before.avatar != member_after.avatar:
                changes.append(f"**Avatar changed**")
            if not changes:
                changes.append("No significant changes")

            embed = discord.Embed(
                title=f'{member_after.display_name} has been updated',
                description=f'**__User:__** {member_after.mention}\n**__Username:__** {member_after.name}\n**__User ID:__** {member_after.id}\n\n**Changes:**\n' + '\n'.join(changes) + f'\n\n**__Action:__** {action.name.capitalize()}\n**__Reason:__** {reason}\n**__Action By:__** {action_by.mention}\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                color=color.green
            )
            embed.set_thumbnail(url=member_after.display_avatar.url)
            embed.set_footer(text=f'User ID: {member_after.id}')
            await self.bot.log.send(guild=member_after.guild, embed=embed, type="member_update")
        except Exception as e:
            logger.error(f"Error in OnMemberUpdate.member_update_log: {e}")

    update_user_timeouts = {}  
    async def anti_update_module(self,member:discord.Member,member_after:discord.Member):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(member.guild.id))
            if not anti_nuke_cache:
                return
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {member.guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_member_update'):
                return logger.warning(f"Guild {member.guild.name} has anti member update disabled")

            if member.roles == member_after.roles:
                return logger.warning(f"User {member} was not updated by role update")

            
            async def check_entry():
                async for entry in member.guild.audit_logs(limit=1,action=discord.AuditLogAction.member_update,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == member.id:
                        return entry
            entry = await check_entry()
            if entry:
                updater = entry.user
                if updater == self.bot.user:
                    return logger.warning(f"User {member} was updated by the bot")
            else:
                return logger.warning(f"User {member} was not updated by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(member.guild.id),{}).get(str(updater.id),{})
            if anti_nuke_bypass_cache.get('anti_member_update'):
                return logger.warning(f"User {updater} is bypassed from anti member update")
            
            if updater.id == member.guild.owner.id or await checks.check_is_owner_raw(updater,member.guild):
                return logger.warning(f"User {member} was updated by the owner")
            if updater.top_role.position >= member.guild.me.top_role.position:
                return logger.warning(f"User {member} was updated by a user with a higher role than the bot")
            
            
            # ==================================
            if str(member.guild.id) not in self.update_user_timeouts:
                self.update_user_timeouts[str(member.guild.id)] = {}
            if str(updater.id) not in self.update_user_timeouts.get(str(member.guild.id)):
                self.update_user_timeouts[str(member.guild.id)][str(updater.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.update_user_timeouts[str(member.guild.id)][str(updater.id)]['count'] += 1
            self.update_user_timeouts[str(member.guild.id)][str(updater.id)]['created_at'] = datetime.datetime.now()

            if str(member.guild.id) in self.update_user_timeouts:
                if self.update_user_timeouts.get(str(member.guild.id)):
                    if self.update_user_timeouts.get(str(member.guild.id),{}).get(str(updater.id)):
                        if (self.update_user_timeouts.get(str(member.guild.id),{}).get(str(updater.id),{}).get('count') >= anti_nuke_cache.get('anti_member_update_limit',1)
                            and
                            self.update_user_timeouts.get(str(member.guild.id),{}).get(str(updater.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user  

                            action = anti_nuke_cache.get('anti_member_update_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {member.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{member.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Member Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Member Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await member.guild.ban(updater,reason="Banned by Antinuke System: Anti Member Update")
                                    await self.bot.antinuke_log.send(guild=member.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_update_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{member.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Member Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Member Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await member.guild.kick(updater,reason="Kicked by Antinuke System: Anti Member Update")
                                    await self.bot.antinuke_log.send(guild=member.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_update_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{member.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Member Update\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Member Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=member.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_update_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{member.guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Member Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Member Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    try:
                                        await updater.edit(roles=[],reason="Muted by Antinuke System: Anti Member Update")
                                    except:
                                        pass
                                    await updater.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Member Update")
                                    await self.bot.antinuke_log.send(guild=member.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_update_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {member.guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(member.guild.id) in self.update_user_timeouts:
                                    if str(updater.id) in self.update_user_timeouts.get(str(member.guild.id)):
                                        self.update_user_timeouts[str(member.guild.id)][str(updater.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        

        except Exception as e:
            logger.error(f"Error in on_member_remove.anti_update_module: {e}")


    @commands.Cog.listener()
    async def on_member_update(self, member_before: discord.Member, member_after: discord.Member):
        try:
            asyncio.create_task(self.anti_update_module(member_before, member_after))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.member_update_log(member_before, member_after))
        except Exception as e:
            logger.error(f"Error in OnMemberUpdate.on_member_update: {e}")
