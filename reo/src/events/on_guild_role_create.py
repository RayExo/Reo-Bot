import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot

class on_guild_role_create(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def role_create_log(self,role:discord.Role):
        try:
            guilds_log_cache = cache.guilds_log.get(str(role.guild.id))
            if not guilds_log_cache:
                return 
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {role.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('role_create_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for role create log in {role.guild.name}")
            
            async def check_entry():
                async for entry in role.guild.audit_logs(limit=1,action=discord.AuditLogAction.role_create):
                    if entry.target.id == role.id:
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
            
            embed = discord.Embed(
                title=f'Role {role.name} has been created',
                description=f'**__Role:__** {role.mention}\n**__Role Name:__** {role.name}\n**__Role ID:__** `{role.id}`\n**__Role Created At:__** <t:{int(role.created_at.timestamp())}>\n\n**__Created By:__** {user}\n**__Created By ID:__** `{user_id}`\n**__Reason:__** `{reason}`\n\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                color=color.green
            )
            embed.set_footer(text=f'Role ID: {role.id}')
            embed.set_thumbnail(url=role.guild.icon.url if role.guild.icon else None)
            await self.bot.log.send(guild=role.guild,embed=embed,type=f"role_create")
        except Exception as e:
            logger.error(f"Error in on_guild_role_create.role_create_log: {e}")

    create_role_timeouts = {}

    async def anti_role_create_module(self,role:discord.Role):
        try:
        
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(role.guild.id))
            if not anti_nuke_cache:
                return 
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {role.guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_role_create'):
                return logger.warning(f"Guild {role.guild.name} has anti role create disabled")
            
            async def check_entry():
                async for entry in role.guild.audit_logs(limit=1,action=discord.AuditLogAction.role_create,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == role.id:
                        return entry
            entry = await check_entry()
            if entry:
                creator = entry.user
                if creator == self.bot.user:
                    return logger.warning(f"Role {role.name} was created by the bot")
            else:
                return logger.warning(f"Role {role.name} was not created by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(role.guild.id),{}).get(str(creator.id),{})
            if anti_nuke_bypass_cache.get('anti_role_create'):
                return logger.warning(f"User {creator} is bypassed from anti role create")
            
            if creator.id == role.guild.owner.id or await checks.check_is_owner_raw(creator,role.guild):
                return logger.warning(f"Role {role.name} was created by the owner")
            if creator.top_role.position >= role.guild.me.top_role.position:
                return logger.warning(f"Role {role.name} was created by a user with a higher role than the bot")
            
            # ==================================
            if str(role.guild.id) not in self.create_role_timeouts:
                self.create_role_timeouts[str(role.guild.id)] = {}
            if str(creator.id) not in self.create_role_timeouts.get(str(role.guild.id)):
                self.create_role_timeouts[str(role.guild.id)][str(creator.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.create_role_timeouts[str(role.guild.id)][str(creator.id)]['count'] += 1
            self.create_role_timeouts[str(role.guild.id)][str(creator.id)]['created_at'] = datetime.datetime.now()


            if str(role.guild.id) in self.create_role_timeouts:
                if self.create_role_timeouts.get(str(role.guild.id)):
                    if self.create_role_timeouts.get(str(role.guild.id),{}).get(str(creator.id)):
                        if (self.create_role_timeouts.get(str(role.guild.id),{}).get(str(creator.id),{}).get('count') >= anti_nuke_cache.get('anti_role_create_limit',1)
                            and
                            self.create_role_timeouts.get(str(role.guild.id),{}).get(str(creator.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_role_create_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {role.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{role.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Role Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=role.guild.icon.url if role.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Role Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await role.guild.ban(creator,reason="Banned by Antinuke System: Anti Role Create")
                                    await self.bot.antinuke_log.send(guild=role.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_role_create.anti_role_create_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{role.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Role Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=role.guild.icon.url if role.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Role Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await role.guild.kick(creator,reason="Kicked by Antinuke System: Anti Role Create")
                                    await self.bot.antinuke_log.send(guild=role.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_role_create.anti_role_create_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{role.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Role Create\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=role.guild.icon.url if role.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Role Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=role.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_role_create.anti_role_create_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{role.guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Role Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=role.guild.icon.url if role.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Role Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    try:
                                        await creator.edit(roles=[],reason="Muted by Antinuke System: Anti Role Delete")
                                    except:
                                        pass
                                    await creator.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Role Create")
                                    await self.bot.antinuke_log.send(guild=role.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_guild_role_create.anti_role_create_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {role.guild.name}")

                            if action != 'warn':
                            # reset the timeout
                                if str(role.guild.id) in self.create_role_timeouts:
                                    if str(creator.id) in self.create_role_timeouts.get(str(role.guild.id)):
                                        self.create_role_timeouts[str(role.guild.id)][str(creator.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return


        except Exception as e:
            logger.error(f"Error in on_guild_role_create.anti_role_create_module: {e}")

    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        try:
            asyncio.create_task(self.anti_role_create_module(role))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.role_create_log(role))
        except Exception as e:
            pass