import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks
import traceback, sys

from reo.memory.cache import cache

from reo.src.checks.variables import fetch_variables

from reo.style import color

from reo.engine.Bot import AutoShardedBot

import json




class on_member_join(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def join_log(self,member:discord.Member):
        try:
            guilds_log_cache = cache.guilds_log.get(str(member.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {member.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('member_join_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for member join log in {member.guild.name}")
            
            embed = discord.Embed(
                title=f'{member.display_name} has joined the server',
                description=f'**__User__** {member.mention}\n**__Username:__** {member.name}\n**__User ID:__** {member.id}\n\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                color=color.green
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f'User ID: {member.id}')
            await self.bot.log.send(guild=member.guild,embed=embed,type=f"member_join_channel_id")
        except Exception as e:
            logger.error(f"Error in on_member_join.join_log: {e}")

    add_bot_timeouts = {}
    async def anti_bot_add_module(self,bot:discord.Member):
        if not bot.bot:
            return logger.warning(f"User {bot} is not a bot")
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(bot.guild.id))
            if not anti_nuke_cache:
                return 
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {bot.guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_bot_add'):
                return logger.warning(f"Guild {bot.guild.name} has anti bot add disabled")
            
            async def check_entry():
                async for entry in bot.guild.audit_logs(limit=1,action=discord.AuditLogAction.bot_add,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == bot.id:
                        return entry
            entry = await check_entry()
            if entry:
                adder = entry.user
                if adder == self.bot.user:
                    return logger.warning(f"Bot {bot} was added by the bot")
            else:
                return logger.warning(f"Bot {bot} was not added by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(bot.guild.id),{}).get(str(adder.id),{})
            if anti_nuke_bypass_cache.get('anti_bot_add'):
                return logger.warning(f"User {adder} is bypassed from anti bot add")
            
            if adder.id == bot.guild.owner.id or await checks.check_is_owner_raw(adder,bot.guild):
                return logger.warning(f"Bot {bot} was added by the owner")
            if adder.top_role.position >= bot.guild.me.top_role.position:
                return logger.warning(f"Bot {bot} was added by a user with a higher role than the bot")
            
            # ==================================
            if str(bot.guild.id) not in self.add_bot_timeouts:
                self.add_bot_timeouts[str(bot.guild.id)] = {}
            if str(adder.id) not in self.add_bot_timeouts.get(str(bot.guild.id)):
                self.add_bot_timeouts[str(bot.guild.id)][str(adder.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.add_bot_timeouts[str(bot.guild.id)][str(adder.id)]['count'] += 1
            self.add_bot_timeouts[str(bot.guild.id)][str(adder.id)]['created_at'] = datetime.datetime.now()

            if str(bot.guild.id) in self.add_bot_timeouts:
                if self.add_bot_timeouts.get(str(bot.guild.id)):
                    if self.add_bot_timeouts.get(str(bot.guild.id),{}).get(str(adder.id)):
                        if (self.add_bot_timeouts.get(str(bot.guild.id),{}).get(str(adder.id),{}).get('count') >= anti_nuke_cache.get('anti_bot_add_limit',1)
                            and
                            self.add_bot_timeouts.get(str(bot.guild.id),{}).get(str(adder.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_bot_add_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {bot.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{bot.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Bot Add\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=bot.guild.icon.url if bot.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(adder,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {adder.mention}\n**__ID__**: `{adder.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Bot Add\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=adder.display_avatar.url)
                                    await bot.guild.ban(adder,reason="Banned by Antinuke System: Anti Bot Add")
                                    await self.bot.antinuke_log.send(guild=bot.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_bot_add_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{bot.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Bot Add\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=bot.guild.icon.url if bot.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(adder,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {adder.mention}\n**__ID__**: `{adder.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Bot Add\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=adder.display_avatar.url)
                                    await bot.guild.kick(adder,reason="Kicked by Antinuke System: Anti Bot Add")
                                    await self.bot.antinuke_log.send(guild=bot.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_bot_add_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{bot.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Bot Add\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=bot.guild.icon.url if bot.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(adder,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {adder.mention}\n**__ID__**: `{adder.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Bot Add\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=adder.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=bot.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_bot_add_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{bot.guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Bot Add\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=bot.guild.icon.url if bot.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(adder,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {adder.mention}\n**__ID__**: `{adder.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Bot Add\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=adder.display_avatar.url)
                                    try:
                                        await adder.edit(roles=[],reason="Muted by Antinuke System: Anti Bot Add")
                                    except:
                                        pass
                                    await adder.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Bot Add")
                                    await self.bot.antinuke_log.send(guild=bot.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_member_remove.anti_bot_add_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {bot.guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(bot.guild.id) in self.add_bot_timeouts:
                                    if str(adder.id) in self.add_bot_timeouts.get(str(bot.guild.id)):
                                        self.add_bot_timeouts[str(bot.guild.id)][str(adder.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        
        except Exception as e:
            logger.error(f"Error in on_member_remove.anti_bot_add_module: {e}")

    async def guild_welcome_module(self,member:discord.Member):
        guild = member.guild
        try:
            welcomer_cache = self.bot.cache.welcomer_settings.get(str(guild.id),{})
            if not welcomer_cache:
                return
            if not welcomer_cache.get('welcome'):
                return logger.warning(f"Guild {guild.name} has welcome disabled")
            if not welcomer_cache.get('welcome_message') and not welcomer_cache.get('welcome_embed'):
                return logger.warning(f"Guild {guild.name} has welcome message and embed disabled")
            channel_id = welcomer_cache.get('welcome_channel')
            if not channel_id:
                return logger.warning(f"Channel ID not found for welcome in {guild.name}")
            channel = guild.get_channel(int(channel_id))
            if not channel:
                return logger.warning(f"Channel not found for welcome in {guild.name}")

            if welcomer_cache.get('welcome_message'):
                message_content = fetch_variables(text=welcomer_cache.get('welcome_message_content'),member=member,guild=guild)
            else:
                message_content = None

            embed_color = discord.Color.blurple()
            if welcomer_cache.get('welcome_embed_color'):
                if str(welcomer_cache.get('welcome_embed_color')).lower() == 'red':
                    embed_color = color.red
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'green':
                    embed_color = color.green
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'blue':
                    embed_color = color.blue
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'yellow':
                    embed_color = color.yellow
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'purple':
                    embed_color = color.purple
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'orange':
                    embed_color = color.orange
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'pink':
                    embed_color = color.pink
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'cyan':
                    embed_color = color.black
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'white':
                    embed_color = color.white
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'black':
                    embed_color = color.black
                elif str(welcomer_cache.get('welcome_embed_color')).lower() == 'gray':
                    embed_color = color.gray
                else:
                    embed_color = discord.Color.blurple()


            
            if welcomer_cache.get('welcome_embed'):
                embed = discord.Embed(
                    title=fetch_variables(text=welcomer_cache.get('welcome_embed_title'),member=member,guild=guild),
                    description=fetch_variables(text=welcomer_cache.get('welcome_embed_description'),member=member,guild=guild),
                    color=embed_color
                )
                if welcomer_cache.get('welcome_embed_thumbnail'):
                    embed.set_thumbnail(url=fetch_variables(text=welcomer_cache.get('welcome_embed_thumbnail'),member=member,guild=guild))
                if welcomer_cache.get('welcome_embed_image'):
                    embed.set_image(url=fetch_variables(text=welcomer_cache.get('welcome_embed_image'),member=member,guild=guild))
                if welcomer_cache.get('welcome_embed_footer'):
                    embed.set_footer(text=fetch_variables(text=welcomer_cache.get('welcome_embed_footer'),member=member,guild=guild),icon_url=fetch_variables(text=welcomer_cache.get('welcome_embed_footer_icon'),member=member,guild=guild))
                if welcomer_cache.get('welcome_embed_author'):
                    embed.set_author(name=fetch_variables(text=welcomer_cache.get('welcome_embed_author'),member=member,guild=guild),icon_url=fetch_variables(text=welcomer_cache.get('welcome_embed_author_icon'),member=member,guild=guild),url=fetch_variables(text=welcomer_cache.get('welcome_embed_author_url'),member=member,guild=guild))
            else:
                embed = None
            await channel.send(content=message_content,embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    async def guild_autorole_module(self,member:discord.Member):
        guild = member.guild
        try:
            welcomer_cache = self.bot.cache.welcomer_settings.get(str(guild.id),{})
            if not welcomer_cache:
                return
            if not welcomer_cache.get('autorole'):
                return logger.warning(f"Guild {guild.name} has autorole disabled")
            
            autoroles = welcomer_cache.get('autoroles', [])
            if not autoroles:
                return logger.warning(f"Guild {guild.name} has no autoroles")
            
            roles_to_add = []
            for role in autoroles:
                role = guild.get_role(int(role))
                if role:
                    if role.permissions.administrator:
                        logger.warning(f"Role {role.name} in {guild.name} is an admin role")
                        continue
                    roles_to_add.append(role)
            if not roles_to_add:
                return logger.warning(f"Guild {guild.name} has no valid autoroles")
            
            await member.add_roles(*roles_to_add,reason="Autoroles by Welcomer System")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    async def guild_autonick_module(self,member:discord.Member):
        guild = member.guild
        try:
            welcomer_cache = self.bot.cache.welcomer_settings.get(str(guild.id),{})
            if not welcomer_cache:
                return
            if not welcomer_cache.get('autonick'):
                return logger.warning(f"Guild {guild.name} has autonick disabled")
            
            autonick_format = welcomer_cache.get('autonick_format')
            if not autonick_format:
                return logger.warning(f"Guild {guild.name} has no autonick format")
            
            autonick_format = fetch_variables(text=autonick_format,member=member,guild=guild)
            await member.edit(nick=autonick_format,reason="Autonick by Welcomer System")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    async def guild_greet_module(self,member:discord.Member):
        guild = member.guild
        try:
            welcomer_cache = self.bot.cache.welcomer_settings.get(str(guild.id),{})
            if not welcomer_cache:
                return
            if not welcomer_cache.get('greet'):
                return logger.error(f"Guild {member.guild.name} has greeting disabled")
            channel_ids = welcomer_cache.get('greet_channels', [])
            if not channel_ids:
                return logger.error(f"Channel ID not found for greeting in {member.guild.name}")
            for channel_id in channel_ids:
                try:
                    channel = guild.get_channel(int(channel_id))
                    if not channel:
                        return logger.error(f"Channel not found for greeting in {member.guild.name}")
                    message_content = fetch_variables(text=welcomer_cache.get('greet_message'),member=member,guild=guild)
                    if message_content:
                        await channel.send(content=message_content,delete_after=welcomer_cache.get('greet_delete_after',5))
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error in on_member_join.guild_greet_module: {e}")
        except Exception as e:
            logger.error(f"Error in on_member_join.guild_greet_module: {e}")


    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            asyncio.create_task(self.anti_bot_add_module(member))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.join_log(member))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.guild_welcome_module(member))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.guild_autorole_module(member))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.guild_autonick_module(member))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.guild_greet_module(member))
        except Exception as e:
            pass

