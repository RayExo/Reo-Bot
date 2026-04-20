import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot

class on_guild_emojis_update(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    create_emoji_timeouts = {}
    async def anti_emote_create_module(self, guild: discord.Guild, emoji: discord.Emoji, entry: discord.AuditLogEntry=None):

    
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(guild.id))
            if not anti_nuke_cache:
                return 
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_emote_create'):
                return logger.warning(f"Guild {guild.name} has anti emote create disabled")
            
            async def check_entry():
                async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.emoji_create,after=datetime.datetime.now() - datetime.timedelta(seconds=5)):
                    if entry.target.id == emoji.id:
                        return entry
            if not entry:
                entry = await check_entry()
            if entry:
                creator = entry.user
                if creator == self.bot.user:
                    return logger.warning(f"Emoji {emoji.name} was created by the bot")
            else:
                return logger.warning(f"Emoji {emoji.name} was created by an unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(guild.id),{}).get(str(creator.id),{})
            if anti_nuke_bypass_cache.get('anti_emote_create'):
                return logger.warning(f"Emoji {emoji.name} was created by a user that has bypass permissions")
            

            if creator.id == guild.owner.id or await checks.check_is_owner_raw(creator,guild):
                return logger.warning(f"Emoji {emoji.name} was created by the owner of the server")
            if creator.top_role.position >= guild.me.top_role.position:
                return logger.warning(f"Emoji {emoji.name} was created by a user with a higher role than the bot")
            

            # =================================================

            if str(guild.id) not in self.create_emoji_timeouts:
                self.create_emoji_timeouts[str(guild.id)] = {}
            if str(creator.id) not in self.create_emoji_timeouts.get(str(guild.id)):
                self.create_emoji_timeouts[str(guild.id)][str(creator.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.create_emoji_timeouts[str(guild.id)][str(creator.id)]['count'] += 1
            self.create_emoji_timeouts[str(guild.id)][str(creator.id)]['created_at'] = datetime.datetime.now()
            
            if str(guild.id) in self.create_emoji_timeouts:
                if self.create_emoji_timeouts.get(str(guild.id)):
                    if self.create_emoji_timeouts.get(str(guild.id),{}).get(str(creator.id)):
                        if (self.create_emoji_timeouts.get(str(guild.id),{}).get(str(creator.id),{}).get('count') >= anti_nuke_cache.get('anti_emote_create_limit',1)
                            and
                            self.create_emoji_timeouts.get(str(guild.id),{}).get(str(creator.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_emote_create_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Emoji Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Emoji Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await guild.ban(creator,reason="Banned by Antinuke System: Anti Emoji Create")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_create_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Emoji Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Emoji Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await guild.kick(creator,reason="Kicked by Antinuke System: Anti Emoji Create")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_create_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been warned for Anti Emoji Create\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Emoji Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_create_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been muted for Anti Emoji Create\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Emoji Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    try:
                                        await creator.edit(roles=[],reason="Muted by Antinuke System: Anti Emoji Create")
                                    except:
                                        pass
                                    await creator.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Emoji Create")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_create_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {guild.name}")

                            if action != 'warn':
                            # reset the timeout
                                if str(guild.id) in self.create_emoji_timeouts:
                                    if str(creator.id) in self.create_emoji_timeouts.get(str(guild.id)):
                                        self.create_emoji_timeouts[str(guild.id)][str(creator.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return

        except Exception as e:
            logger.error(f"Error in on_guild_emojis_update.anti_emote_create_module: {e}")
    
    delete_emoji_timeouts = {}
    async def anti_emote_delete_module(self, guild: discord.Guild, emoji: discord.Emoji, entry: discord.AuditLogEntry=None):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(guild.id))
            if not anti_nuke_cache:
                return 
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_emote_delete'):
                return logger.warning(f"Guild {guild.name} has anti emote delete disabled")
            
            async def check_entry():
                async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.emoji_delete,after=datetime.datetime.now() - datetime.timedelta(seconds=5)):
                    if entry.target.id == emoji.id:
                        return entry
            if not entry:
                entry = await check_entry()
            if entry:
                deleter = entry.user
                if deleter == self.bot.user:
                    return logger.warning(f"Emoji {emoji.name} was deleted by the bot")
            else:
                return logger.warning(f"Emoji {emoji.name} was deleted by an unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(guild.id),{}).get(str(deleter.id),{})
            if anti_nuke_bypass_cache.get('anti_emote_delete'):
                return logger.warning(f"Emoji {emoji.name} was deleted by a user that has bypass permissions")
            

            if deleter.id == guild.owner.id or await checks.check_is_owner_raw(deleter,guild):
                return logger.warning(f"Emoji {emoji.name} was deleted by the owner of the server")
            if deleter.top_role.position >= guild.me.top_role.position:
                return logger.warning(f"Emoji {emoji.name} was deleted by a user with a higher role than the bot")
            

            # =================================================
            if str(guild.id) not in self.delete_emoji_timeouts:
                self.delete_emoji_timeouts[str(guild.id)] = {}
            if str(deleter.id) not in self.delete_emoji_timeouts.get(str(guild.id)):
                self.delete_emoji_timeouts[str(guild.id)][str(deleter.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.delete_emoji_timeouts[str(guild.id)][str(deleter.id)]['count'] += 1
            self.delete_emoji_timeouts[str(guild.id)][str(deleter.id)]['created_at'] = datetime.datetime.now()

            if str(guild.id) in self.delete_emoji_timeouts:
                if self.delete_emoji_timeouts.get(str(guild.id)):
                    if self.delete_emoji_timeouts.get(str(guild.id),{}).get(str(deleter.id)):
                        if (self.delete_emoji_timeouts.get(str(guild.id),{}).get(str(deleter.id),{}).get('count') >= anti_nuke_cache.get('anti_emote_delete_limit',1)
                            and
                            self.delete_emoji_timeouts.get(str(guild.id),{}).get(str(deleter.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_emote_delete_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Emoji Delete\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Emoji Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await guild.ban(deleter,reason="Banned by Antinuke System: Anti Emoji Delete")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_delete_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Emoji Delete\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Emoji Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await guild.kick(deleter,reason="Kicked by Antinuke System: Anti Emoji Delete")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_delete_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been warned for Anti Emoji Delete\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Emoji Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_delete_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been muted for Anti Emoji Delete\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Emoji Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    try:
                                        await deleter.edit(roles=[],reason="Muted by Antinuke System: Anti Emoji Delete")
                                    except:
                                        pass
                                    await deleter.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Emoji Delete")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_delete_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(guild.id) in self.delete_emoji_timeouts:
                                    if str(deleter.id) in self.delete_emoji_timeouts.get(str(guild.id)):
                                        self.delete_emoji_timeouts[str(guild.id)][str(deleter.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        


        except Exception as e:
            logger.error(f"Error in on_guild_emojis_update.anti_emote_delete_module: {e}")


    update_emoji_timeouts = {}
    async def anti_emote_update_module(self, guild: discord.Guild, emoji: discord.Emoji, entry: discord.AuditLogEntry=None):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(guild.id))
            if not anti_nuke_cache:
                return 
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_emote_update'):
                return logger.warning(f"Guild {guild.name} has anti emote update disabled")
            
            async def check_entry():
                async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.emoji_update,after=datetime.datetime.now() - datetime.timedelta(seconds=5)):
                    if entry.target.id == emoji.id:
                        return entry
            if not entry:
                entry = await check_entry()
            if entry:
                updater = entry.user
                if updater == self.bot.user:
                    return logger.warning(f"Emoji {emoji.name} was updated by the bot")
            else:
                return logger.warning(f"Emoji {emoji.name} was updated by an unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(guild.id),{}).get(str(updater.id),{})
            if anti_nuke_bypass_cache.get('anti_emote_update'):
                return logger.warning(f"Emoji {emoji.name} was updated by a user that has bypass permissions")
            

            if updater.id == guild.owner.id or await checks.check_is_owner_raw(updater,guild):
                return logger.warning(f"Emoji {emoji.name} was updated by the owner of the server")
            if updater.top_role.position >= guild.me.top_role.position:
                return logger.warning(f"Emoji {emoji.name} was updated by a user with a higher role than the bot")
            

            # =================================================
            if str(guild.id) not in self.update_emoji_timeouts:
                self.update_emoji_timeouts[str(guild.id)] = {}
            if str(updater.id) not in self.update_emoji_timeouts.get(str(guild.id)):
                self.update_emoji_timeouts[str(guild.id)][str(updater.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.update_emoji_timeouts[str(guild.id)][str(updater.id)]['count'] += 1
            self.update_emoji_timeouts[str(guild.id)][str(updater.id)]['created_at'] = datetime.datetime.now()


            if str(guild.id) in self.update_emoji_timeouts:
                if self.update_emoji_timeouts.get(str(guild.id)):
                    if self.update_emoji_timeouts.get(str(guild.id),{}).get(str(updater.id)):
                        if (self.update_emoji_timeouts.get(str(guild.id),{}).get(str(updater.id),{}).get('count') >= anti_nuke_cache.get('anti_emote_update_limit',1)
                            and
                            self.update_emoji_timeouts.get(str(guild.id),{}).get(str(updater.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_emote_update_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Emoji Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Emoji Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await guild.ban(updater,reason="Banned by Antinuke System: Anti Emoji Update")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_update_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Emoji Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Emoji Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await guild.kick(updater,reason="Kicked by Antinuke System: Anti Emoji Update")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_update_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been warned for Anti Emoji Update\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Emoji Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_update_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been muted for Anti Emoji Update\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Emoji Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    try:
                                        await updater.edit(roles=[],reason="Muted by Antinuke System: Anti Emoji Update")
                                    except:
                                        pass
                                    await updater.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Emoji Update")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_emojis_update.anti_emote_update_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(guild.id) in self.update_emoji_timeouts:
                                    if str(updater.id) in self.update_emoji_timeouts.get(str(guild.id)):
                                        self.update_emoji_timeouts[str(guild.id)][str(updater.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        


        except Exception as e:
            logger.error(f"Error in on_guild_emojis_update.anti_emote_update_module: {e}")
            


    async def emojis_add_or_remove_or_update_log(self, guild: discord.Guild, before: list[discord.Emoji], after: list[discord.Emoji]):
        try:
            guilds_log_cache = cache.guilds_log.get(str(guild.id))
            if not guilds_log_cache:
                return 
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {guild.name} has logging disabled")
        
            removed = []
            added = []
            updated = []
            before_emojis = {emoji.id: emoji for emoji in before}
            after_emojis = {emoji.id: emoji for emoji in after}


            for emoji_id, emoji in before_emojis.items():
                if emoji_id not in after_emojis:
                    removed.append(emoji)
                elif emoji.name != after_emojis[emoji_id].name:
                    updated.append(after_emojis[emoji_id])

            # Check for added emojis
            for emoji_id, emoji in after_emojis.items():
                if emoji_id not in before_emojis:
                    added.append(after_emojis[emoji_id])


            if added:
                for emoji in added:
                    try:
                        asyncio.create_task(self.anti_emote_create_module(guild,emoji))
                    except Exception as e:
                        pass
            if removed:
                for emoji in removed:
                    try:
                        asyncio.create_task(self.anti_emote_delete_module(guild,emoji))
                    except Exception as e:
                        pass
            if updated:
                for emoji in updated:
                    try:
                        asyncio.create_task(self.anti_emote_update_module(guild,emoji))
                    except Exception as e:
                        pass

            if not removed and not added and not updated:
                return
            
            if added:
                async def check_entry():
                    async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.emoji_create,after=datetime.datetime.now() - datetime.timedelta(seconds=5)):
                        if entry.target.id in [emoji.id for emoji in removed]:
                            return entry
                channel_id = guilds_log_cache.get('emoji_create_channel_id')
                if not channel_id:
                    return logger.error(f"Channel ID not found for emojis add log in {guild.name}")
                
                entry = await check_entry()
                if entry:
                    user = entry.user.mention
                    user_id = entry.user.id
                else:
                    user = "Unknown"
                    user_id = "Unknown"



                embed = discord.Embed(
                    title=f'Emoji{"s" if len(added) > 1 else ""} added to the server',
                    description=f"{'-'*50}\n",
                    color=color.green
                )
                for emoji in added:
                    embed.description += f"**__Emoji:__** {emoji}\n**__Emoji Name:__** {emoji.name}\n**__Emoji ID:__** `{emoji.id}`\n**__Animated:__** {emoji.animated}\n**__Emoji Created At:__** <t:{int(emoji.created_at.timestamp())}>\n{'-'*50}\n"
                
                embed.description += f"\n\n**__Added By:__** {user}\n**__Added By ID:__** `{user_id}`\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>"

                embed.set_footer(text=f"Total emojis added: {len(added)}")
                embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                await self.bot.log.send(guild=guild,embed=embed,type=f"emoji_create")

            if removed:
                async def check_entry():
                    async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.emoji_delete,after=datetime.datetime.now() - datetime.timedelta(seconds=5)):
                        if entry.target.id in [emoji.id for emoji in removed]:
                            return entry
                        
                channel_id = guilds_log_cache.get('emoji_delete_channel_id')
                if not channel_id:
                    return logger.error(f"Channel ID not found for emojis remove log in {guild.name}")
                
                entry = await check_entry()
                if entry:
                    user = entry.user.mention
                    user_id = entry.user.id
                else:
                    user = "Unknown"
                    user_id = "Unknown"


                embed = discord.Embed(
                    title=f'Emoji{"s" if len(removed) > 1 else ""} removed from the server',
                    description=f"{'-'*50}\n",
                    color=color.red
                )
                for emoji in removed:
                    embed.description += f"**__Emoji:__** {emoji}\n**__Emoji Name:__** {emoji.name}\n**__Emoji ID:__** `{emoji.id}`\n**__Animated:__** {emoji.animated}\n**__Emoji Created At:__** <t:{int(emoji.created_at.timestamp())}>\n{'-'*50}\n"
                
                embed.description += f"\n\n**__Removed By:__** {user}\n**__Removed By ID:__** `{user_id}`\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>"


                embed.set_footer(text=f"Total emojis removed: {len(removed)}")
                embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                await self.bot.log.send(guild=guild,embed=embed,type=f"emoji_delete")

            if updated:
                async def check_entry():
                    async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.emoji_update,after=datetime.datetime.now() - datetime.timedelta(seconds=5)):
                        if entry.target.id in [emoji.id for emoji in removed]:
                            return entry
                channel_id = guilds_log_cache.get('emoji_update_channel_id')
                if not channel_id:
                    return logger.error(f"Channel ID not found for emojis update log in {guild.name}")
                
                entry = await check_entry()
                if entry:
                    user = entry.user.mention
                    user_id = entry.user.id
                else:
                    user = "Unknown"
                    user_id = "Unknown"

                embed = discord.Embed(
                    title=f'Emoji{"s" if len(updated) > 1 else ""} updated in the server',
                    description=f"{'-'*50}\n",
                    color=color.blue
                )
                for emoji in updated:
                    # show the before and after name
                    embed.description += f"**__Emoji:__** {emoji}\n**__Emoji Name:__** {emoji.name}\n**__Emoji ID:__** `{emoji.id}`\n**__Animated:__** {emoji.animated}\n\n**Name changed from** `{before_emojis[emoji.id].name}` --> `{emoji.name}`\n{'-'*50}\n**__Emoji Created At:__** <t:{int(emoji.created_at.timestamp())}>\n**__Emoji Updated At:__** <t:{int(datetime.datetime.now().timestamp())}>\n"
                
                embed.description += f"\n\n**__Updated By:__** {user}\n**__Updated By ID:__** `{user_id}`\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>"


                embed.set_footer(text=f"Total emojis updated: {len(updated)}")
                embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                await self.bot.log.send(guild=guild,embed=embed,type=f"emoji_update")
        except Exception as e:
            logger.error(f"Error in emojis_add_or_remove_or_update_log: {e}")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: discord.Guild, before: list[discord.Emoji], after: list[discord.Emoji]):
        try:
            asyncio.create_task(self.emojis_add_or_remove_or_update_log(guild, before, after))
        except Exception as e:
            pass
        