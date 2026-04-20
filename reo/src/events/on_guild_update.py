import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot




# class discord.Guild
# Attributes
# afk_channel
# afk_timeout
# approximate_member_count
# approximate_presence_count
# banner
# bitrate_limit
# categories
# channels
# chunked
# created_at
# default_notifications
# default_role
# description
# discovery_splash
# dms_paused_until
# emoji_limit
# emojis
# explicit_content_filter
# features
# filesize_limit
# forums
# icon
# id
# invites_paused_until
# large
# max_members
# max_presences
# max_stage_video_users
# max_video_channel_users
# me
# member_count
# members
# mfa_level
# name
# nsfw_level
# owner
# owner_id
# preferred_locale
# premium_progress_bar_enabled
# premium_subscriber_role
# premium_subscribers
# premium_subscription_count
# premium_tier
# public_updates_channel
# roles
# rules_channel
# safety_alerts_channel
# scheduled_events
# self_role
# shard_id
# splash
# stage_channels
# stage_instances
# sticker_limit
# stickers
# system_channel
# system_channel_flags
# text_channels
# threads
# unavailable
# vanity_url
# vanity_url_code
# verification_level
# voice_channels
# voice_client
# widget_channel
# widget_enabled

class on_guild_update(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def guild_update_log(self,before:discord.Guild,after:discord.Guild):
        try:
            guilds_log_cache = cache.guilds_log.get(str(after.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {after.name} has logging disabled")
            channel_id = guilds_log_cache.get('guild_update_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for guild update log in {after.name}")
            
            embed = discord.Embed(
                title=f'Guild {after.name} has been updated',
                description=f'**__Guild Name:__** {after.name}\n**__Guild ID:__** `{after.id}`\n\n**__Guild Updated At:__** <t:{int(datetime.datetime.now().timestamp())}>\n\n',
                color=color.green
            )

            embed.description += "**__Changes:__**\n"

            if before.name != after.name:
                embed.description += f"**__Old Guild Name:__** {before.name}\n**__New Guild Name:__** {after.name}\n"
            if not before.icon and after.icon:
                embed.description += f"**__Guild icon has been added:__** [Link Here]({after.icon.url if after.icon else None})\n"
            if before.icon and not after.icon:
                embed.description += f"**__Guild icon has been removed:__** [Link Here]({before.icon.url if before.icon else None})\n"
            if before.icon and after.icon and before.icon.url != after.icon.url:
                embed.description += f"**__Old Guild icon:__** [Link Here]({before.icon.url})\n**__New Guild icon:__** [Link Here]({after.icon.url})\n"
            if before.banner and not after.banner:
                embed.description += f"**__Guild banner has been removed:__** [Link Here]({before.banner.url})\n"
            if not before.banner and after.banner:
                embed.description += f"**__Guild banner has been added:__** [Link Here]({after.banner.url})\n"
            if before.banner and after.banner and before.banner.url != after.banner.url:
                embed.description += f"**__Old Guild banner:__** [Link Here]({before.banner.url})\n**__New Guild banner:__** [Link Here]({after.banner.url})\n"
            if before.description != after.description:
                embed.description += f"**__Old Guild Description:__** {before.description}\n**__New Guild Description:__** {after.description}\n"
            if before.discovery_splash and not after.discovery_splash:
                embed.description += f"**__Guild discovery splash has been removed:__** [Link Here]({before.discovery_splash.url})\n"
            if not before.discovery_splash and after.discovery_splash:
                embed.description += f"**__Guild discovery splash has been added:__** [Link Here]({after.discovery_splash.url})\n"
            if before.discovery_splash and after.discovery_splash and before.discovery_splash.url != after.discovery_splash.url:
                embed.description += f"**__Old Guild discovery splash:__** [Link Here]({before.discovery_splash.url})\n**__New Guild discovery splash:__** [Link Here]({after.discovery_splash.url})\n"
            if before.icon and after.icon and before.icon.url != after.icon.url:
                embed.description += f"**__Old Guild icon:__** [Link Here]({before.icon.url})\n**__New Guild icon:__** [Link Here]({after.icon.url})\n"
            if before.splash and not after.splash:
                embed.description += f"**__Guild splash has been removed:__** [Link Here]({before.splash.url})\n"
            if not before.splash and after.splash:
                embed.description += f"**__Guild splash has been added:__** [Link Here]({after.splash.url})\n"
            if before.splash and after.splash and before.splash.url != after.splash.url:
                embed.description += f"**__Old Guild splash:__** [Link Here]({before.splash.url})\n**__New Guild splash:__** [Link Here]({after.splash.url})\n"
            if before.vanity_url_code != after.vanity_url_code:
                embed.description += f"**__Old Guild Vanity URL:__** [Link Here](https://discord.gg/{before.vanity_url_code})\n**__New Guild Vanity URL:__** [Link Here](https://discord.gg/{after.vanity_url_code})\n"
            if before.description != after.description:
                embed.description += f"**__Old Guild Description:__** {before.description}\n**__New Guild Description:__** {after.description}\n"
            if before.rules_channel and not after.rules_channel:
                embed.description += f"**__Guild rules channel has been removed:__** {before.rules_channel.mention}\n"
            if not before.rules_channel and after.rules_channel:
                embed.description += f"**__Guild rules channel has been added:__** {after.rules_channel.mention}\n"
            if before.rules_channel and after.rules_channel and before.rules_channel.mention != after.rules_channel.mention:
                embed.description += f"**__Old Guild rules channel:__** {before.rules_channel.mention}\n**__New Guild rules channel:__** {after.rules_channel.mention}\n"
            if before.system_channel and not after.system_channel:
                embed.description += f"**__Guild system channel has been removed:__** {before.system_channel.mention}\n"
            if not before.system_channel and after.system_channel:
                embed.description += f"**__Guild system channel has been added:__** {after.system_channel.mention}\n"
            if before.system_channel and after.system_channel and before.system_channel.mention != after.system_channel.mention:
                embed.description += f"**__Old Guild system channel:__** {before.system_channel.mention}\n**__New Guild system channel:__** {after.system_channel.mention}\n"
            if before.public_updates_channel and not after.public_updates_channel:
                embed.description += f"**__Guild public updates channel has been removed:__** {before.public_updates_channel.mention}\n"
            if not before.public_updates_channel and after.public_updates_channel:
                embed.description += f"**__Guild public updates channel has been added:__** {after.public_updates_channel.mention}\n"
            if before.public_updates_channel and after.public_updates_channel and before.public_updates_channel.mention != after.public_updates_channel.mention:
                embed.description += f"**__Old Guild public updates channel:__** {before.public_updates_channel.mention}\n**__New Guild public updates channel:__** {after.public_updates_channel.mention}\n"
            if before.preferred_locale != after.preferred_locale:
                embed.description += f"**__Old Guild Preferred Locale:__** {before.preferred_locale}\n**__New Guild Preferred Locale:__** {after.preferred_locale}\n"
            if before.verification_level != after.verification_level:
                embed.description += f"**__Old Guild Verification Level:__** {before.verification_level}\n**__New Guild Verification Level:__** {after.verification_level}\n"
            if before.explicit_content_filter != after.explicit_content_filter:
                embed.description += f"**__Old Guild Explicit Content Filter:__** {before.explicit_content_filter}\n**__New Guild Explicit Content Filter:__** {after.explicit_content_filter}\n"
            if before.afk_channel and not after.afk_channel:
                embed.description += f"**__Guild AFK Channel has been removed:__** {before.afk_channel.mention}\n"
            if not before.afk_channel and after.afk_channel:
                embed.description += f"**__Guild AFK Channel has been added:__** {after.afk_channel.mention}\n"
            if before.afk_channel and after.afk_channel and before.afk_channel.mention != after.afk_channel.mention:
                embed.description += f"**__Old Guild AFK Channel:__** {before.afk_channel.mention}\n**__New Guild AFK Channel:__** {after.afk_channel.mention}\n"
            if before.afk_timeout != after.afk_timeout:
                embed.description += f"**__Old Guild AFK Timeout:__** {before.afk_timeout}\n**__New Guild AFK Timeout:__** {after.afk_timeout}\n"
            if before.default_notifications != after.default_notifications:
                embed.description += f"**__Old Guild Default Notifications:__** {before.default_notifications}\n**__New Guild Default Notifications:__** {after.default_notifications}\n"
            if before.system_channel_flags != after.system_channel_flags:
                embed.description += f"**__Old Guild System Channel Flags:__** {before.system_channel_flags.value}\n**__New Guild System Channel Flags:__** {after.system_channel_flags.value}\n"
            if before.widget_enabled != after.widget_enabled:
                embed.description += f"**__Old Guild Widget Enabled:__** {before.widget_enabled}\n**__New Guild Widget Enabled:__** {after.widget_enabled}\n"
            if before.widget_channel and not after.widget_channel:
                embed.description += f"**__Guild widget channel has been removed:__** {before.widget_channel.mention}\n"
            if not before.widget_channel and after.widget_channel:
                embed.description += f"**__Guild widget channel has been added:__** {after.widget_channel.mention}\n"
            if before.widget_channel and after.widget_channel and before.widget_channel.mention != after.widget_channel.mention:
                embed.description += f"**__Old Guild widget channel:__** {before.widget_channel.mention}\n**__New Guild widget channel:__** {after.widget_channel.mention}\n"
            if not before.banner and after.banner:
                embed.description += f"**__Guild banner has been added:__** [Link Here]({after.banner.url})\n"
            if before.banner and not after.banner:
                embed.description += f"**__Guild banner has been removed:__** [Link Here]({before.banner.url})\n"
            if before.banner and after.banner and before.banner.url != after.banner.url:
                embed.description += f"**__Old Guild banner:__** [Link Here]({before.banner.url})\n**__New Guild banner:__** [Link Here]({after.banner.url})\n"
            if not before.vanity_url_code and after.vanity_url_code:
                embed.description += f"**__Guild Vanity Invite has been added:__** [Link Here](https://discord.gg/{after.vanity_url_code})\n"
            if before.vanity_url_code and not after.vanity_url_code:
                embed.description += f"**__Guild Vanity Invite has been removed:__** [Link Here](https://discord.gg/{before.vanity_url_code})\n"
            if before.vanity_url_code and after.vanity_url_code and before.vanity_url_code != after.vanity_url_code:
                embed.description += f"**__Old Guild Vanity Invite:__** [Link Here](https://discord.gg/{before.vanity_url_code})\n**__New Guild Vanity Invite:__** [Link Here](https://discord.gg/{after.vanity_url_code})\n"


            embed.set_footer(text=f'Guild ID: {after.id}')
            embed.set_thumbnail(url=after.icon.url if after.icon else None)
            await self.bot.log.send(guild=after,embed=embed,type=f"guild_update")
        except Exception as e:
            logger.error(f"Error in on_guild_update.guild_update_log: {e}")


    update_server_timeouts = {}
    async def anti_server_update_module(self,guild:discord.Guild):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(guild.id))
            if not anti_nuke_cache:
                return
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_server_update'):
                return logger.warning(f"Guild {guild.name} has anti server update disabled")
            
            async def check_entry():
                async for entry in guild.audit_logs(limit=1,action=discord.AuditLogAction.guild_update,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == guild.id:
                        return entry
            entry = await check_entry()
            if entry:
                creator = entry.user
                if creator == self.bot.user:
                    return logger.warning(f"Server {guild.name} was updated by the bot")
            else:
                return logger.warning(f"Server {guild.name} was not updated by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(guild.id),{}).get(str(creator.id),{})
            if anti_nuke_bypass_cache.get('anti_server_update'):
                return logger.warning(f"User {creator} is bypassed from anti server update")
            
            if creator.id == guild.owner.id or await checks.check_is_owner_raw(creator,guild):
                return logger.warning(f"Server {guild.name} was updated by the owner")
            if creator.top_role.position >= guild.me.top_role.position:
                return logger.warning(f"Server {guild.name} was updated by a user with a higher role than the bot")
            
            # ==================================
            if str(guild.id) not in self.update_server_timeouts:
                self.update_server_timeouts[str(guild.id)] = {}
            if str(creator.id) not in self.update_server_timeouts.get(str(guild.id)):
                self.update_server_timeouts[str(guild.id)][str(creator.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.update_server_timeouts[str(guild.id)][str(creator.id)]['count'] += 1
            self.update_server_timeouts[str(guild.id)][str(creator.id)]['created_at'] = datetime.datetime.now()


            if str(guild.id) in self.update_server_timeouts:
                if self.update_server_timeouts.get(str(guild.id)):
                    if self.update_server_timeouts.get(str(guild.id),{}).get(str(creator.id)):
                        if (self.update_server_timeouts.get(str(guild.id),{}).get(str(creator.id),{}).get('count') >= anti_nuke_cache.get('anti_server_update_limit',1)
                            and
                            self.update_server_timeouts.get(str(guild.id),{}).get(str(creator.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_server_update_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Server Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
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
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Server Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await guild.ban(creator,reason="Banned by Antinuke System: Anti Server Update")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_update.anti_server_update_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Server Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
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
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Server Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await guild.kick(creator,reason="Kicked by Antinuke System: Anti Server Update")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_update.anti_server_update_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{guild.name}`**\n**Details:** ```\nYou have been warned for Anti Server Update\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
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
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Server Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_update.anti_server_update_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Server Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
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
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Server Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    try:
                                        await creator.edit(roles=[],reason="Muted by Antinuke System: Anti Guild Update")
                                    except:
                                        pass
                                    await creator.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Guild Update")
                                    await self.bot.antinuke_log.send(guild=guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_update.anti_server_update_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {guild.name}")

                            if action != 'warn':
                            # reset the timeout
                                if str(guild.id) in self.update_server_timeouts:
                                    if str(creator.id) in self.update_server_timeouts.get(str(guild.id)):
                                        self.update_server_timeouts[str(guild.id)][str(creator.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        

        except Exception as e:
            logger.error(f"Error in on_guild_update.anti_server_update_module: {e}")
    
    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        try:
            asyncio.create_task(self.anti_server_update_module(after))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.guild_update_log(before,after))
        except Exception as e:
            pass
