import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

from reo.memory.cache import cache


from reo.style import color

from reo.engine.Bot import AutoShardedBot

class on_webhooks_update(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot

    async def webhooks_update_log(self,channel:discord.TextChannel):
        try:
            guilds_log_cache = cache.guilds_log.get(str(channel.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {channel.guild.name} has logging disabled")
            
            created = []
            removed = []
            updated = []

            webhooks = {webhook.id:webhook for webhook in await channel.webhooks()}

            user = "Unknown"
            user_id = "Unknown"

            async def check_entry():
                nonlocal user,user_id
                async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.webhook_create,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id in webhooks:
                        created.append(webhooks[entry.target.id])
                        user = entry.user.mention
                        user_id = entry.user.id
                async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.webhook_update,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id in webhooks:
                        updated.append(webhooks[entry.target.id])
                        user = entry.user.mention
                        user_id = entry.user.id
                async for entry in channel.guild.audit_logs(limit=1,action=discord.AuditLogAction.webhook_delete,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id in webhooks:
                        removed.append(webhooks[entry.target.id])
                        user = entry.user.mention
                        user_id = entry.user.id

            await check_entry()

            if created:
                for webhook in created:
                    try:
                        asyncio.create_task(self.anti_webhook_create_module(webhook))
                    except Exception as e:
                        pass
            if removed:
                for webhook in removed:
                    try:
                        asyncio.create_task(self.anti_webhook_delete_module(webhook))
                    except Exception as e:
                        pass
            if updated:
                for webhook in updated:
                    try:
                        asyncio.create_task(self.anti_webhook_update_module(webhook))
                    except Exception as e:
                        pass


            if created:
                channel_id = guilds_log_cache.get('webhook_create_channel_id')
                if not channel_id:
                    return logger.error(f"Channel ID not found for webhook create log in {channel.guild.name}")
                
                embed = discord.Embed(
                    title=f'{len(created)} Webhook(s) has been created',
                    description="",
                    color=color.green
                )
                for webhook in created:
                    embed.description += f"**__Webhook Name:__** {webhook.name}\n**__Webhook ID:__** `{webhook.id}`\n**__Webhook Channel:__** {webhook.channel.mention}\n\n**__Created By:__** {user}\n**__Created By ID:__** `{user_id}`\n\n**__Webhook Created At:__** <t:{int(webhook.created_at.timestamp())}>\n\n"

                embed.set_footer(text=f'Channel ID: {channel.id}')
                embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                await self.bot.log.send(guild=channel.guild,embed=embed,type=f"webhook_create")
            if removed:
                channel_id = guilds_log_cache.get('webhook_delete_channel_id')
                if not channel_id:
                    return logger.error(f"Channel ID not found for webhook delete log in {channel.guild.name}")
                
                embed = discord.Embed(
                    title=f'{len(removed)} Webhook(s) has been removed',
                    description="",
                    color=color.red
                )
                for webhook in removed:
                    embed.description += f"**__Webhook Name:__** {webhook.name}\n**__Webhook ID:__** `{webhook.id}`\n**__Webhook Channel:__** {webhook.channel.mention}\n\n**__Removed By:__** {user}\n**__Removed By ID:__** `{user_id}`\n\n**__Webhook Created At:__** <t:{int(webhook.created_at.timestamp())}>\n**__Webhook Removed At:__** <t:{int(datetime.datetime.now().timestamp())}>\n\n"

                embed.set_footer(text=f'Channel ID: {channel.id}')
                embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                await self.bot.log.send(guild=channel.guild,embed=embed,type=f"webhook_delete")
            if updated:
                channel_id = guilds_log_cache.get('webhook_update_channel_id')
                if not channel_id:
                    return logger.error(f"Channel ID not found for webhook update log in {channel.guild.name}")
                
                embed = discord.Embed(
                    title=f'{len(updated)} Webhook(s) has been updated',
                    description="",
                    color=color.green
                )
                for webhook in updated:
                    embed.description += f"**__Webhook Name:__** {webhook.name}\n**__Webhook ID:__** `{webhook.id}`\n**__Webhook Channel:__** {webhook.channel.mention}\n\n**__Updated By:__** {user}\n**__Updated By ID:__** `{user_id}`\n\n**__Webhook Created At:__** <t:{int(webhook.created_at.timestamp())}>\n**__Webhook Updated At:__** <t:{int(datetime.datetime.now().timestamp())}>\n\n"
                
                embed.set_footer(text=f'Channel ID: {channel.id}')
                embed.set_thumbnail(url=channel.guild.icon.url if channel.guild.icon else None)
                await self.bot.log.send(guild=channel.guild,embed=embed,type=f"webhook_update")
        except Exception as e:
            logger.error(f"Error in on_webhooks_update.webhooks_update_log: {e}")

    create_webhook_timeouts = {}
    async def anti_webhook_create_module(self,webhook:discord.Webhook):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(webhook.guild.id))
            if not anti_nuke_cache:
                return
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {webhook.guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_webhook_create'):
                return logger.warning(f"Guild {webhook.guild.name} has anti webhook create disabled")
            
            async def check_entry():
                async for entry in webhook.guild.audit_logs(limit=1,action=discord.AuditLogAction.webhook_create,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == webhook.id:
                        return entry
            entry = await check_entry()
            if entry:
                creator = entry.user
                if creator == self.bot.user:
                    return logger.warning(f"Webhook {webhook} was created by the bot")
            else:
                return logger.warning(f"Webhook {webhook} was not created by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(webhook.guild.id),{}).get(str(creator.id),{})
            if anti_nuke_bypass_cache.get('anti_webhook_create'):
                return logger.warning(f"User {creator} is bypassed from anti webhook create")
            
            if creator.id == webhook.guild.owner.id or await checks.check_is_owner_raw(creator,webhook.guild):
                return logger.warning(f"Webhook {webhook} was created by the owner")
            if creator.top_role.position >= webhook.guild.me.top_role.position:
                return logger.warning(f"Webhook {webhook} was created by a user with a higher role than the bot")
            
            # ==================================
            if str(webhook.guild.id) not in self.create_webhook_timeouts:
                self.create_webhook_timeouts[str(webhook.guild.id)] = {}
            if str(creator.id) not in self.create_webhook_timeouts.get(str(webhook.guild.id)):
                self.create_webhook_timeouts[str(webhook.guild.id)][str(creator.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.create_webhook_timeouts[str(webhook.guild.id)][str(creator.id)]['count'] += 1
            self.create_webhook_timeouts[str(webhook.guild.id)][str(creator.id)]['created_at'] = datetime.datetime.now()
            
            if str(webhook.guild.id) in self.create_webhook_timeouts:
                if self.create_webhook_timeouts.get(str(webhook.guild.id)):
                    if self.create_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(creator.id)):
                        if (self.create_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(creator.id),{}).get('count') >= anti_nuke_cache.get('anti_webhook_create_limit',1)
                            and
                            self.create_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(creator.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_webhook_create_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {webhook.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Webhook Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Webhook Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await webhook.guild.ban(creator,reason="Banned by Antinuke System: Anti Webhook Create")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_create_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Webhook Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Webhook Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await webhook.guild.kick(creator,reason="Kicked by Antinuke System: Anti Webhook Create")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_create_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Webhook Create\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Webhook Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_create_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**Details:** ```\nYou have been muted for Anti Webhook Create\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(creator,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Webhook Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=creator.display_avatar.url)
                                    try:
                                        await creator.edit(roles=[],reason="Muted by Antinuke System: Anti Webhook Create")
                                    except:
                                        pass
                                    await creator.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Webhook Create")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_create_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {webhook.guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(webhook.guild.id) in self.create_webhook_timeouts:
                                    if str(creator.id) in self.create_webhook_timeouts.get(str(webhook.guild.id)):
                                        self.create_webhook_timeouts[str(webhook.guild.id)][str(creator.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        

        except Exception as e:
            logger.error(f"Error in on_webhooks_update.anti_webhook_create_module: {e}")

    
    delete_webhook_timeouts = {}
    async def anti_webhook_delete_module(self,webhook:discord.Webhook):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(webhook.guild.id))
            if not anti_nuke_cache:
                return
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {webhook.guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_webhook_delete'):
                return logger.warning(f"Guild {webhook.guild.name} has anti webhook delete disabled")
            
            async def check_entry():
                async for entry in webhook.guild.audit_logs(limit=1,action=discord.AuditLogAction.webhook_delete,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == webhook.id:
                        return entry
            entry = await check_entry()
            if entry:
                deleter = entry.user
                if deleter == self.bot.user:
                    return logger.warning(f"Webhook {webhook} was deleted by the bot")
            else:
                return logger.warning(f"Webhook {webhook} was not deleted by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(webhook.guild.id),{}).get(str(deleter.id),{})
            if anti_nuke_bypass_cache.get('anti_webhook_delete'):
                return logger.warning(f"User {deleter} is bypassed from anti webhook delete")
            
            if deleter.id == webhook.guild.owner.id or await checks.check_is_owner_raw(deleter,webhook.guild):
                return logger.warning(f"Webhook {webhook} was deleted by the owner")
            if deleter.top_role.position >= webhook.guild.me.top_role.position:
                return logger.warning(f"Webhook {webhook} was deleted by a user with a higher role than the bot")
            
            # ==================================
            if str(webhook.guild.id) not in self.delete_webhook_timeouts:
                self.delete_webhook_timeouts[str(webhook.guild.id)] = {}
            if str(deleter.id) not in self.delete_webhook_timeouts.get(str(webhook.guild.id)):
                self.delete_webhook_timeouts[str(webhook.guild.id)][str(deleter.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.delete_webhook_timeouts[str(webhook.guild.id)][str(deleter.id)]['count'] += 1
            self.delete_webhook_timeouts[str(webhook.guild.id)][str(deleter.id)]['created_at'] = datetime.datetime.now()
        
            if str(webhook.guild.id) in self.delete_webhook_timeouts:
                if self.delete_webhook_timeouts.get(str(webhook.guild.id)):
                    if self.delete_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(deleter.id)):
                        if (self.delete_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(deleter.id),{}).get('count') >= anti_nuke_cache.get('anti_webhook_delete_limit',1)
                            and
                            self.delete_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(deleter.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user
                            action = anti_nuke_cache.get('anti_webhook_delete_punishment')
                            
                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {webhook.guild.name}")
                                
                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Webhook Delete\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Webhook Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await webhook.guild.ban(deleter,reason="Banned by Antinuke System: Anti Webhook Delete")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_delete_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Webhook Delete\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Webhook Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await webhook.guild.kick(deleter,reason="Kicked by Antinuke System: Anti Webhook Delete")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_delete_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Webhook Delete\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Webhook Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_delete_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**Details:** ```\nYou have been muted for Anti Webhook Delete\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(deleter,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {deleter.mention}\n**__ID__**: `{deleter.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Webhook Delete\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=deleter.display_avatar.url)
                                    try:
                                        await deleter.edit(roles=[],reason="Muted by Antinuke System: Anti Webhook Delete")
                                    except:
                                        pass
                                    await deleter.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Webhook Delete")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_delete_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {webhook.guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(webhook.guild.id) in self.delete_webhook_timeouts:
                                    if str(deleter.id) in self.delete_webhook_timeouts.get(str(webhook.guild.id)):
                                        self.delete_webhook_timeouts[str(webhook.guild.id)][str(deleter.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        

        except Exception as e:
            logger.error(f"Error in on_webhooks_update.anti_webhook_delete_module: {e}")

    update_webhook_timeouts = {}
    async def anti_webhook_update_module(self,webhook:discord.Webhook):
        try:
            anti_nuke_cache = self.bot.cache.antinuke_settings.get(str(webhook.guild.id))
            if not anti_nuke_cache:
                return
            if not anti_nuke_cache.get('enabled'):
                return logger.warning(f"Guild {webhook.guild.name} has antinuke disabled")
            if not anti_nuke_cache.get('anti_webhook_update'):
                return logger.warning(f"Guild {webhook.guild.name} has anti webhook update disabled")
            
            async def check_entry():
                async for entry in webhook.guild.audit_logs(limit=1,action=discord.AuditLogAction.webhook_update,after=datetime.datetime.now()-datetime.timedelta(seconds=5)):
                    if entry.target.id == webhook.id:
                        return entry
            entry = await check_entry()
            if entry:
                updater = entry.user
                if updater == self.bot.user:
                    return logger.warning(f"Webhook {webhook} was updated by the bot")
            else:
                return logger.warning(f"Webhook {webhook} was not updated by a user or maybe unknown user")
            
            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(str(webhook.guild.id),{}).get(str(updater.id),{})
            if anti_nuke_bypass_cache.get('anti_webhook_update'):
                return logger.warning(f"User {updater} is bypassed from anti webhook update")
            
            if updater.id == webhook.guild.owner.id or await checks.check_is_owner_raw(updater,webhook.guild):
                return logger.warning(f"Webhook {webhook} was updated by the owner")
            if updater.top_role.position >= webhook.guild.me.top_role.position:
                return logger.warning(f"Webhook {webhook} was updated by a user with a higher role than the bot")
            
            # ==================================

            if str(webhook.guild.id) not in self.update_webhook_timeouts:
                self.update_webhook_timeouts[str(webhook.guild.id)] = {}
            if str(updater.id) not in self.update_webhook_timeouts.get(str(webhook.guild.id)):
                self.update_webhook_timeouts[str(webhook.guild.id)][str(updater.id)] = {
                    'count': 0,
                    'created_at': datetime.datetime.now()
                }
            self.update_webhook_timeouts[str(webhook.guild.id)][str(updater.id)]['count'] += 1
            self.update_webhook_timeouts[str(webhook.guild.id)][str(updater.id)]['created_at'] = datetime.datetime.now()
        
            if str(webhook.guild.id) in self.update_webhook_timeouts:
                if self.update_webhook_timeouts.get(str(webhook.guild.id)):
                    if self.update_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(updater.id)):
                        if (self.update_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(updater.id),{}).get('count') >= anti_nuke_cache.get('anti_webhook_update_limit',1)
                            and
                            self.update_webhook_timeouts.get(str(webhook.guild.id),{}).get(str(updater.id),{}).get('created_at') >= (datetime.datetime.now() - datetime.timedelta(seconds=60))
                            ):
                            # getting action for the user

                            action = anti_nuke_cache.get('anti_webhook_update_punishment')

                            async def send_notify_to_user(user:discord.Member,embed:discord.Embed):
                                try:
                                    await user.send(embed=embed)
                                except:
                                    logger.warning(f"Could not send message to {user} in {webhook.guild.name}")

                            if action == 'ban':
                                try:
                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Webhook Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Webhook Update\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await webhook.guild.ban(updater,reason="Banned by Antinuke System: Anti Webhook Update")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_update_module: {e}")
                            elif action == 'kick':
                                try:
                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Webhook Update\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Kick`\n**__Reason:__** Anti Webhook Update\n**__Time:__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await webhook.guild.kick(updater,reason="Kicked by Antinuke System: Anti Webhook Update")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_update_module: {e}")
                            elif action == 'warn':
                                try:
                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Webhook Update\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Warn`\n**__Reason:__** Anti Webhook Update\n**__Time:__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_update_module: {e}")
                            elif action == 'mute':
                                try:
                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{webhook.guild.name}`**\n**Details:** ```\nYou have been muted for Anti Webhook Update\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=webhook.guild.icon.url if webhook.guild.icon else None)
                                    asyncio.create_task(send_notify_to_user(updater,embed))
                                except:
                                    pass
                                try:
                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {updater.mention}\n**__ID__**: `{updater.id}`\n**__Action__**: `Mute`\n**__Reason:__** Anti Webhook Update\n**__Time:__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red
                                    )
                                    embed.set_footer(text=f"Antinuke System",icon_url=self.bot.user.display_avatar.url)
                                    embed.set_thumbnail(url=updater.display_avatar.url)
                                    try:
                                        await updater.edit(roles=[],reason="Muted by Antinuke System: Anti Webhook Update")
                                    except:
                                        pass
                                    await updater.timeout(datetime.timedelta(days=1),reason="Muted by Antinuke System: Anti Webhook Update")
                                    await self.bot.antinuke_log.send(guild=webhook.guild,embed=embed,type="antinuke")
                                except Exception as e:
                                    logger.error(f"Error in on_webhooks_update.anti_webhook_update_module: {e}")
                            else:
                                return logger.warning(f"Invalid action {action} in {webhook.guild.name}")
                            
                            if action != 'warn':
                            # reset the timeout
                                if str(webhook.guild.id) in self.update_webhook_timeouts:
                                    if str(updater.id) in self.update_webhook_timeouts.get(str(webhook.guild.id)):
                                        self.update_webhook_timeouts[str(webhook.guild.id)][str(updater.id)] = {
                                            'count': 0,
                                            'created_at': datetime.datetime.now()
                                        }
                            return
                        

        except Exception as e:
            logger.error(f"Error in on_webhooks_update.anti_webhook_update_module: {e}")


    
    @commands.Cog.listener()
    async def on_webhooks_update(self, channel: discord.TextChannel):
        try:
            asyncio.create_task(self.webhooks_update_log(channel))
        except Exception as e:
            pass