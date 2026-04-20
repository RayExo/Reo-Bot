import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache

import traceback,sys

from reo.style import color

from reo.engine.Bot import AutoShardedBot


class on_guild_channel_create(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def channel_create_log(self,channel:discord.abc.GuildChannel):
        try:
            guilds_log_cache = cache.guilds_log.get(str(channel.guild.id))
            if not guilds_log_cache:
                return 
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {channel.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('channel_create_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for channel create log in {channel.guild.name}")
            
            async def check_entry():
                async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_create):
                    if entry.target.id == channel.id:
                        return entry
            entry = await check_entry()
            if entry:
                user = entry.user.mention
                user_id = entry.user.id
                reason = entry.reason
            else:
                user = "Unknown"
                user_id = "Unknown"
                reason = "Unknown"
            
            category_details = ""
            if channel.category:
                category_details = (
                    f"\n**__Channel Category:__** {channel.category.mention}"
                    f"\n**__Channel Category ID:__** `{channel.category.id}`"
                )
            embed = discord.Embed(
                title=f'#{channel.name} has been created',
                description=(
                    f"**__Channel:__** {channel.mention}\n"
                    f"**__Channel Name:__** {channel.mention}\n"
                    f"**__Channel ID:__** `{channel.id}`\n"
                    f"**__Channel Type:__** {channel.type}"
                    f"{category_details}\n\n"
                    f"**__Created By:__** {user}\n"
                    f"**__Created By ID:__** {user_id}\n"
                    f"**__Reason:__** `{reason}`\n\n"
                    f"**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>"
                ),
                color=color.green
            )
            embed.set_footer(text=f'Channel ID: {channel.id}')
            embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
            await self.bot.log.send(guild=channel.guild,embed=embed,type=f"channel_create")
        except Exception as e:
            logger.error(f"Error in on_guild_channel_create.channel_create_log: {e}")

    create_channel_timeouts = {}
    
    
    async def anti_channel_create_module(self,channel:discord.abc.GuildChannel):
        
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(channel.guild.id))
            if not anti_nuke_cache:
                return 
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {channel.guild.name} has antinuke disabled")
            
            if not anti_nuke_cache.get('anti_channel_create'):
                return logger.warning(f"Anti Channel Create is disabled in {channel.guild.name}")
            
            async def check_entry():
                async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.channel_create):
                    if entry.target.id == channel.id:
                        return entry
            entry = await check_entry()

            if entry:
                creator = entry.user
                if creator == self.bot.user:
                    return logger.warning(f"Channel {channel.name} was created by the bot in {channel.guild.name}")
            else:
                return logger.warning(f"Channel {channel.name} was created by the bot in {channel.guild.name}")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(channel.guild.id),{}).get(str(creator.id),{})
            if anti_nuke_bypass_cache:
                if anti_nuke_bypass_cache.get('anti_channel_create'):
                    return logger.warning(f"User {creator} is bypassed from anti channel create in {channel.guild.name}")

            if creator.top_role.position >= channel.guild.me.top_role.position:
                return logger.warning(f"User {creator} has higher or equal role than the bot in {channel.guild.name}")
            if creator == channel.guild.owner or await checks.check_is_owner_raw(creator,channel.guild):
                return logger.warning(f"User {creator} is the owner of the guild in {channel.guild.name} so bypassed from anti channel create")

            if str(channel.guild.id) not in self.create_channel_timeouts:
                self.create_channel_timeouts[str(channel.guild.id)] = {}
            if str(creator.id) not in self.create_channel_timeouts.get(str(channel.guild.id)):
                self.create_channel_timeouts[str(channel.guild.id)][str(creator.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.create_channel_timeouts[str(channel.guild.id)][str(creator.id)]['count'] += 1
            self.create_channel_timeouts[str(channel.guild.id)][str(creator.id)]['created_at'] = datetime.datetime.now()
            
            if str(channel.guild.id) in self.create_channel_timeouts:
                if self.create_channel_timeouts.get(str(channel.guild.id)):
                    if self.create_channel_timeouts.get(str(channel.guild.id),{}).get(str(creator.id)):
                        if (self.create_channel_timeouts.get(str(channel.guild.id),{}).get(str(creator.id),{}).get('count') >= anti_nuke_cache.get('anti_channel_create_limit',1)
                            and
                            self.create_channel_timeouts.get(str(channel.guild.id),{}).get(str(creator.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_channel_create_punishment')

                            async def delete_channel(channel):
                                try:
                                    await channel.delete(reason="Deleted by Antinuke System: Anti Channel Create")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_create.anti_channel_create_module: {e}")

                            try:
                                asyncio.create_task(delete_channel(channel))
                            except:
                                pass

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {channel.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Channel Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await channel.guild.ban(creator,reason="Banned by Antinuke System: Anti Channel Create")
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_create.anti_channel_create_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Channel Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await channel.guild.kick(creator,reason="Kicked by Antinuke System: Anti Channel Create")
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_create.anti_channel_create_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Channel Create\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_channel_create.anti_channel_create_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Channel Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    try:
                                        # remove all roles from the user
                                        await creator.edit(roles=[],reason="Muted by Antinuke System: Anti Channel Create")
                                    except Exception as e:
                                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                                    await creator.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Channel Create")
                                    await self.bot.antinuke_log.send(guild=channel.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                                    
                            else:
                                return logger.warning(f"Invalid action {action} in {channel.guild.name}")

                            if action != 'warn':
                            # reset the timeout
                                if str(channel.guild.id) in self.create_channel_timeouts:
                                    if str(creator.id) in self.create_channel_timeouts.get(str(channel.guild.id)):
                                        self.create_channel_timeouts[str(channel.guild.id)][str(creator.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return


        except Exception as e:
            logger.error(f"Error in on_guild_channel_create.anti_channel_create_module: {e}")
                        




        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        try:
            asyncio.create_task(self.anti_channel_create_module(channel))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.channel_create_log(channel))
        except Exception as e:
            pass
