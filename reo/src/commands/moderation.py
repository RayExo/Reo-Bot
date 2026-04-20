import discord
from discord.ext import commands
import datetime
import re
from reo.src.checks import checks
from reo.memory.cache import cache

import storage.guilds
import storage.ignore_data
import storage.media_channels
from reo.console.logging import logger

from reo.style import color
from reo.utils import pings

from reo.config.config import BotConfigClass
BotConfig = BotConfigClass()

import traceback, sys

import storage
import asyncio
import json


from reo.engine.Bot import AutoShardedBot

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Moderation"
            category = "Main"
            description =  "Moderation commands"
            hidden =  False
            emoji =  self.bot.emoji.MODERATION 
        self.cog_info = cog_info

    @commands.group(
        name="purge",
        help="Purge messages in a channel",
        invoke_without_command=True,
        aliases=['clear','clean','c'],
        usage="purge <amount:int>, purge user <user:discord.Member> <amount:int>, purge images <amount:int>, purge links <amount:int>, purge bots <amount:int>"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_command(self,ctx:commands.Context,amount:int):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                await ctx.send(embed=discord.Embed(description="You can only delete 1000 messages at a time",color=color.red),delete_after=10)
                return
            try:
                await ctx.channel.purge(limit=amount+1,reason=f"Purged by {ctx.author}")
                await ctx.send(embed=discord.Embed(description=f"Deleted {amount} messages",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while purging messages",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @purge_command.command(
        name="user",
        help="Purge messages of a user in a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_user_command(self,ctx:commands.Context,user:discord.Member,amount:int=10):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                await ctx.send(embed=discord.Embed(description="You can only delete 100 messages at a time",color=color.red),delete_after=10)
                return
            try:
                def check(message:discord.Message):
                    return message.author.id == user.id
                await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await ctx.send(embed=discord.Embed(description=f"Deleted {amount} messages of {user.mention}",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while purging messages",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @purge_command.command(
        name="images",
        help="Purge messages containing images in a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_images_command(self,ctx:commands.Context,amount:int=10):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                await ctx.send(embed=discord.Embed(description="You can only delete 100 messages at a time",color=color.red),delete_after=10)
                return
            try:
                def check_images(message:discord.Message):
                    return len(message.attachments) > 0
                def check(message:discord.Message):
                    return check_images(message) or message.embeds
                await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await ctx.send(embed=discord.Embed(description=f"Deleted {amount} messages containing images",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while purging messages",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @purge_command.command(
        name="links",
        help="Purge messages containing links in a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_links_command(self,ctx:commands.Context,amount:int=10):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                await ctx.send(embed=discord.Embed(description="You can only delete 100 messages at a time",color=color.red),delete_after=10)
                return
            try:
                def check_links(text):
                    pattern = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
                    return True if pattern.match(text) else False
                def check(message:discord.Message):
                    return check_links(message.content)
                await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await ctx.send(embed=discord.Embed(description=f"Deleted {amount} messages containing links",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while purging messages",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @purge_command.command(
        name="bots",
        help="Purge messages of a bot in a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2,per=60,type=commands.BucketType.channel)
    async def purge_bots_command(self,ctx:commands.Context,amount:int=10):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            if amount > 1000:
                await ctx.send(embed=discord.Embed(description="You can only delete 100 messages at a time",color=color.red),delete_after=10)
                return
            try:
                def check(message:discord.Message):
                    return message.author.bot
                await ctx.channel.purge(limit=amount+1,check=check)
                try:
                    await ctx.message.delete()
                except:
                    pass
                await ctx.send(embed=discord.Embed(description=f"Deleted {amount} messages of bots",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while purging messages",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @commands.hybrid_command(
        name="ban",
        with_app_command=True,
        help="Ban a user from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=30,type=commands.BucketType.user)
    async def ban_command(self,ctx:commands.Context,user:discord.Member,*,reason:str=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'ban_members'):
                return
            if not await checks.check_if_user_can_be_banned_or_kicked(ctx,user):
                return
            try:
                ban_embed = discord.Embed(
                    title=f"You have been banned from {ctx.guild.name}",
                    description=f"Reason: {reason if reason else 'No Reason Provided'}\n\nBy: {ctx.author.mention}\nTime: <t:{int(datetime.datetime.now().timestamp())}:F>",
                    color=color.red
                )
                ban_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
                ban_embed.set_footer(text=f"Server ID: {ctx.guild.id}",icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                await user.send(embed=ban_embed)
            except:
                logger.warning(f"Couldn't send a DM to the user {user.id} in guild {ctx.guild.id} while banning the user")
            pre_reason = reason if reason else 'No Reason Provided'
            reason = f"Banned by {ctx.author} with reason: {reason if reason else 'No Reason Provided'}"
            await user.ban(reason=reason)
            embed = discord.Embed(
                description=f"{self.bot.emoji.BAN} | Successfully Banned {user.mention} !\nReason: `{pre_reason}`",
                color=color.green
            )
            embed.set_footer(text=f"Action by {ctx.author}",icon_url=ctx.author.display_avatar.url)
            embed.set_author(
                name=f"User Banned",
                icon_url=user.display_avatar.url
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error while banning user {user.id} in guild {ctx.guild.id} with error {e}")
            await ctx.send(embed=discord.Embed(description="An Error occurred while banning the user",color=color.red),delete_after=10)

    @commands.hybrid_command(
        name="kick",
        with_app_command=True,
        help="Kick a user from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=30,type=commands.BucketType.user)
    async def kick_command(self,ctx:commands.Context,user:discord.Member,*,reason:str=None):
        if not await checks.check_is_moderator_permissions(ctx, 'kick_members'):
            return
        if not await checks.check_if_user_can_be_banned_or_kicked(ctx,user):
            return
        try:
            try:
                kick_embed = discord.Embed(
                    title=f"You have been kicked from {ctx.guild.name}",
                    description=f"Reason: {reason if reason else 'No Reason Provided'}\n\nBy: {ctx.author.mention}\nTime: <t:{int(datetime.datetime.now().timestamp())}:F>",
                    color=color.red
                )
                kick_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
                kick_embed.set_footer(text=f"Server ID: {ctx.guild.id}",icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                await user.send(embed=kick_embed)
            except:
                logger.warning(f"Couldn't send a DM to the user {user.id} in guild {ctx.guild.id} while kicking the user")
            pre_reason = reason if reason else 'No Reason Provided'
            reason = f"Kicked by {ctx.author} with reason: {reason if reason else 'No Reason Provided'}"
            await user.kick(reason=reason)
            embed = discord.Embed(
                description=f"{self.bot.emoji.KICK} | Successfully Kicked {user.mention} !\nReason: `{pre_reason}`",
                color=color.green
            )
            embed.set_footer(text=f"Action by {ctx.author}",icon_url=ctx.author.display_avatar.url)
            embed.set_author(
                name=f"User Kicked",
                icon_url=user.display_avatar.url
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error while kicking user {user.id} in guild {ctx.guild.id} with error {e}")
            await ctx.send(embed=discord.Embed(description="An Error occurred while kicking the user",color=color.red),delete_after=10)
        

    @commands.hybrid_command(
        name="unban",
        with_app_command=True,
        help="Unban a user from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def unban_command(self,ctx:commands.Context,user:discord.User,*,reason:str=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'ban_members'):
                return
            user_to_unban = None
            async for entry in ctx.guild.bans(limit=None):
                if entry.user.id == user.id:
                    user_to_unban = entry.user
                    break
                
            if not user_to_unban:
                await ctx.send(embed=discord.Embed(description="The user is not banned",color=color.red),delete_after=10)
                return
            try:
                await ctx.guild.unban(user,reason=reason if reason else "No Reason Provided")
                await ctx.send(embed=discord.Embed(description=f"{user.mention} has been unbanned. Reason: {reason if reason else 'No Reason Provided'}",color=color.green),delete_after=10)
                try:
                    unban_embed = discord.Embed(
                        title=f"You have been unbanned from {ctx.guild.name}",
                        description=f"Reason: {reason if reason else 'No Reason Provided'}\n\nBy: {ctx.author.mention}\nTime: <t:{int(datetime.datetime.now().timestamp())}:F>",
                        color=color.green
                    )
                    unban_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
                    unban_embed.set_footer(text=f"Server ID: {ctx.guild.id}",icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                    await user.send(embed=unban_embed)
                except:
                    logger.warning(f"Couldn't send a DM to the user {user.id} in guild {ctx.guild.id} while unbanning the user")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while unbanning the user",color=color.red),delete_after=10)
                return
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @commands.command(
        name="unbanall",
        help="Unban all users from the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=60,type=commands.BucketType.guild)
    async def unbanall_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'ban_members'):
                return
            try:
                banned_users = []
                message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Unbanning all users",color=color.yellow))
                async for ban in ctx.guild.bans(limit=None):
                    banned_users.append(ban.user)

                for banned_user in banned_users:
                    try:
                        await ctx.guild.unban(banned_user)
                    except:
                        pass
                await message.edit(embed=discord.Embed(description=f"{len(banned_users)} users have been unbanned",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while unbanning all users",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    
    @commands.command(
        name='snipe',
        help='Snipe the last deleted message in the channel',
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.channel)
    async def snipe_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            snipe_data = cache.snipe_data.get('delete',{}).get(str(ctx.channel.id))
            if not snipe_data:
                await ctx.send(embed=discord.Embed(description="No message to snipe",color=color.red),delete_after=10)
                return
            message_id = snipe_data.get('message_id')
            content = snipe_data.get('before_content')
            author_id = snipe_data.get('author_id')
            created_at = snipe_data.get('created_at').replace(tzinfo=None)
            embed = discord.Embed(
                title=f"Sniped Message",
                description=f"**__Author:__** <@{author_id}>\n**__Deleted At:__** <t:{int(created_at.timestamp())}:F>",
                color=color.green
            )
            embed.add_field(name="Content",value=content,inline=False)
            embed.set_footer(text=f"Message ID: {message_id}")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @commands.command(
        name='editsnipe',
        help='Snipe the last edited message in the channel',
        aliases=['esnipe','es']
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.channel)
    async def editsnipe_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_messages'):
                return
            snipe_data = cache.snipe_data.get('edit',{}).get(str(ctx.channel.id))
            if not snipe_data:
                await ctx.send(embed=discord.Embed(description="No message to snipe",color=color.red),delete_after=10)
                return
            message_id = snipe_data.get('message_id')
            before_content = snipe_data.get('before_content')
            after_content = snipe_data.get('after_content')
            author_id = snipe_data.get('author_id')
            created_at = snipe_data.get('created_at').replace(tzinfo=None)
            embed = discord.Embed(
                title=f"Sniped Message",
                description=f"**__Author:__** <@{author_id}>\n**__Edited At:__** <t:{int(created_at.timestamp())}:F>",
                color=color.green
            )
            embed.add_field(name="Before Edit",value=before_content,inline=True)
            embed.add_field(name="After Edit",value=after_content,inline=True)
            embed.set_footer(text=f"Message ID: {message_id}")
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    
    # want to make a group name ignore with subcommands user, channel and in the user,channel subcommand want to add a subcommand add and remove and list

    @commands.group(
        name="ignore",
        help="Ignore users or channels",
        invoke_without_command=True,
        usage="ignore user <user:discord.Member>, ignore channel <channel:discord.TextChannel>"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            
            embed = discord.Embed(
                title="Ignore Commands",
                description="Ignore users or channels",
                color=color.random_color()
            )

            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}"
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_command.group(
        name="user",
        help="Ignore a user",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            
            embed = discord.Embed(
                title="Ignore User Commands",
                description="Here are the commands to ignore a user",
                color=color.random_color()
            )
            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.parent.name} {ctx.command.name} {command.name}` : {command.help}"
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_user_command.command(
        name="add",
        help="Ignore a user"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_add_command(self,ctx:commands.Context,member:discord.Member):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if cache.ignore_data.get('users',{}).get(str(ctx.guild.id),{}).get(str(member.id)):
                    await ctx.send(embed=discord.Embed(description=f"{member.mention} is already ignored",color=color.red),delete_after=10)
                    return
                await storage.ignore_data.insert(guild_id=ctx.guild.id,user_id=member.id)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been ignored",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while ignoring the member",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @ignore_user_command.command(
        name="remove",
        help="Unignore a user"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_remove_command(self,ctx:commands.Context,member:discord.Member):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if not cache.ignore_data.get('users',{}).get(str(ctx.guild.id),{}).get(str(member.id)):
                    await ctx.send(embed=discord.Embed(description=f"{member.mention} is not ignored",color=color.red),delete_after=10)
                    return
                await storage.ignore_data.delete(guild_id=ctx.guild.id,user_id=member.id)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been unignored",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while unignoring the member",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_user_command.command(
        name="list",
        help="List ignored users"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_user_list_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                ignored_users = cache.ignore_data.get('users',{}).get(str(ctx.guild.id),{})
                
                if not ignored_users:
                    await ctx.send(embed=discord.Embed(description="No users are ignored",color=color.red),delete_after=10)
                    return
                ignored_users = list(ignored_users.keys())
                # make ignored_users 5 by 5 list
                ignored_users = [ignored_users[i:i + 5] for i in range(0, len(ignored_users), 5)]
                
                current_page_index = 0
                view_timeout = 60
                cancled = False
                def reset_view_timeout():
                    nonlocal view_timeout
                    view_timeout = 60
                
                async def get_embed():
                    nonlocal ignored_users,current_page_index
                    embed = discord.Embed(
                        title="Ignored Users",
                        color=color.random_color()
                    )
                    embed.description = ', '.join([f"<@{user_id}>" for user_id in ignored_users[current_page_index]])
                    embed.set_footer(text=f"Page {current_page_index+1}/{len(ignored_users)}")
                    return embed
                
                async def get_view(disabled=False):
                    nonlocal view_timeout
                    reset_view_timeout()
                    view = discord.ui.View()
                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.PREVIOUS,
                        row=0,
                        disabled=current_page_index <= 0
                    )
                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.danger,
                        emoji=self.bot.emoji.STOP,
                        row=0,
                        disabled=len(ignored_users) == 1
                    )
                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.NEXT,
                        row=0,
                        disabled=current_page_index >= len(ignored_users)-1
                    )
                    previous_button.callback = lambda i: previous_button_callback(i)
                    stop_button.callback = lambda i: stop_button_callback(i)
                    next_button.callback = lambda i: next_button_callback(i)
                    view.add_item(previous_button)
                    view.add_item(stop_button)
                    view.add_item(next_button)
                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                
                async def previous_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index -= 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                async def stop_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal cancled
                        cancled = True
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view(disabled=True))
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                async def next_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index += 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                message = await ctx.send(embed=await get_embed(),view=await get_view())

                while not cancled:
                    view_timeout -= 1
                    if view_timeout <= 0:
                        await message.edit(embed=await get_embed(),view=await get_view(disabled=True))
                        break
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while listing ignored users",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_command.group(
        name="channel",
        help="Ignore a channel",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            
            embed = discord.Embed(
                title="Ignore Channel Commands",
                description="Here are the commands to ignore a channel",
                color=color.random_color()
            )
            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.parent.name} {ctx.command.name} {command.name}` : {command.help}"
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_channel_command.command(
        name="add",
        help="Ignore a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_add_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if cache.ignore_data.get('channels',{}).get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is already ignored",color=color.red),delete_after=10)
                    return
                await storage.ignore_data.insert(guild_id=ctx.guild.id,channel_id=channel.id,type='channel')
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been ignored",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while ignoring the channel",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @ignore_channel_command.command(
        name="remove",
        help="Unignore a channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_remove_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                if not cache.ignore_data.get('channels',{}).get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is not ignored",color=color.red),delete_after=10)
                    return
                await storage.ignore_data.delete(guild_id=ctx.guild.id,channel_id=channel.id)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been unignored",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while unignoring the channel",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @ignore_channel_command.command(
        name="list",
        help="List ignored channels"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=10,type=commands.BucketType.user)
    async def ignore_channel_list_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            try:
                ignored_channels = cache.ignore_data.get('channels',{}).get(str(ctx.guild.id),{})
                
                if not ignored_channels:
                    await ctx.send(embed=discord.Embed(description="No channels are ignored",color=color.red),delete_after=10)
                    return
                ignored_channels = list(ignored_channels.keys())
                # make ignored_channels 5 by 5 list
                ignored_channels = [ignored_channels[i:i + 5] for i in range(0, len(ignored_channels), 5)]
                
                current_page_index = 0
                view_timeout = 60
                cancled = False
                def reset_view_timeout():
                    nonlocal view_timeout
                    view_timeout = 60
                
                async def get_embed():
                    nonlocal ignored_channels,current_page_index
                    embed = discord.Embed(
                        title="Ignored Channels",
                        color=color.random_color()
                    )
                    embed.description = ', '.join([f"<#{channel_id}>" for channel_id in ignored_channels[current_page_index]])
                    embed.set_footer(text=f"Page {current_page_index+1}/{len(ignored_channels)}")
                    return embed
                
                async def get_view(disabled=False):
                    nonlocal view_timeout
                    reset_view_timeout()
                    view = discord.ui.View()
                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.PREVIOUS,
                        row=0,
                        disabled=current_page_index <= 0
                    )
                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.danger,
                        emoji=self.bot.emoji.STOP,
                        row=0,
                        disabled=len(ignored_channels) == 1
                    )
                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.primary,
                        emoji=self.bot.emoji.NEXT,
                        row=0,
                        disabled=current_page_index >= len(ignored_channels)-1
                    )
                    previous_button.callback = lambda i: previous_button_callback(i)
                    stop_button.callback = lambda i: stop_button_callback(i)
                    next_button.callback = lambda i: next_button_callback(i)
                    view.add_item(previous_button)
                    view.add_item(stop_button)
                    view.add_item(next_button)
                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                
                async def previous_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index -= 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

                async def stop_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal cancled
                        cancled = True
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view(disabled=True))
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                async def next_button_callback(interaction:discord.Interaction):
                    try:
                        nonlocal current_page_index
                        current_page_index += 1
                        await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
                message = await ctx.send(embed=await get_embed(),view=await get_view())

                while not cancled:
                    view_timeout -= 1
                    if view_timeout <= 0:
                        await message.edit(embed=await get_embed(),view=await get_view(disabled=True))
                        break
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                await ctx.send(embed=discord.Embed(description="An Error occurred while listing ignored channels",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @commands.hybrid_command(
        name='lock',
        help='Lock a channel',
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def lock_command(self,ctx:commands.Context,channel:discord.abc.GuildChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'):
                return
            if not channel:
                channel = ctx.channel
            if isinstance(channel, discord.TextChannel):
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            elif isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(ctx.guild.default_role, connect=False,send_messages=False)
            else:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been locked",color=color.green))
        except Exception as e:
            logger.error(f"Error in lock command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @commands.hybrid_command(
        name='unlock',
        help='Unlock a channel',
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def unlock_command(self,ctx:commands.Context,channel:discord.abc.GuildChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_channels'):
                return
            if not channel:
                channel = ctx.channel
            if isinstance(channel, discord.TextChannel):
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            elif isinstance(channel, discord.VoiceChannel):
                await channel.set_permissions(ctx.guild.default_role, connect=True,send_messages=True)
            else:
                await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been unlocked",color=color.green))
        except Exception as e:
            logger.error(f"Error in unlock command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)


    running_lockall = {}
    @commands.hybrid_command(
        name="lockall",
        help="Lock all channels in the server",
        aliases=["lockchannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def lockall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_lockall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another lockall command is already running",color=color.red),delete_after=10)
                return
            async def lock_channel(channel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(ctx.guild.default_role, connect=False,send_messages=False)
                    else:
                        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                except Exception as e:
                    logger.error(f"Error in lockall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Locking all channels",color=color.yellow))
            self.running_lockall[ctx.guild.id] = True
            for channel in ctx.guild.text_channels:
                try:
                    await lock_channel(channel)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_lockall:
                del self.running_lockall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description="All channels have been locked",color=color.green))
        except Exception as e:
            if ctx.guild.id in self.running_lockall:
                del self.running_lockall[ctx.guild.id]
            logger.error(f"Error in lockall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    


    running_unhideall = {}
    @commands.hybrid_command(
        name="unlockall",
        help="Unlock all channels in the server",
        aliases=["unlockchannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def unlockall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_unhideall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another unlockall command is already running",color=color.red),delete_after=10)
                return
            async def unlock_channel(channel:discord.abc.GuildChannel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(ctx.guild.default_role, connect=True,send_messages=True)
                    else:
                        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
                except Exception as e:
                    logger.error(f"Error in unlockall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Unlocking all channels",color=color.yellow))
            self.running_unhideall[ctx.guild.id] = True
            for channel in ctx.guild.channels:
                try:
                    await unlock_channel(channel)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description="All channels have been unlocked",color=color.green))
        except Exception as e:
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            logger.error(f"Error in unlockall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    @commands.hybrid_command(
        name="hide",
        help="Hide a channel",
        aliases=["hidechannel"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def hide(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels'):
                return
            if not channel:
                channel = ctx.channel
            await channel.set_permissions(ctx.guild.default_role, view_channel=False)
            await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been hidden",color=color.green))
        except Exception as e:
            logger.error(f"Error in hide command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    running_hideall = {}
    @commands.hybrid_command(
        name="hideall",
        help="Hide all channels in the server",
        aliases=["hidechannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()  
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def hideall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_hideall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another hideall command is already running",color=color.red),delete_after=10)
                return
            async def hide_channel(channel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == False:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == False and channel.permissions_for(ctx.guild.default_role).connect == False:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=False, connect=False)
                    else:
                        if channel.permissions_for(ctx.guild.default_role).view_channel == False:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                except Exception as e:
                    logger.error(f"Error in hideall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Hiding all channels",color=color.yellow))
            self.running_hideall[ctx.guild.id] = True
            for channel in ctx.guild.channels:
                try:
                    await hide_channel(channel)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_hideall:
                del self.running_hideall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description="All channels have been hidden",color=color.green))
        except Exception as e:
            if ctx.guild.id in self.running_hideall:
                del self.running_hideall[ctx.guild.id]
            logger.error(f"Error in hideall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @commands.hybrid_command(
        name="unhide",
        help="Unhide a channel",
        aliases=["unhidechannel"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=60,type=commands.BucketType.guild)
    async def unhide(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels'):
                return
            if not channel:
                channel = ctx.channel
            await channel.set_permissions(ctx.guild.default_role, view_channel=True)
            await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been unhidden",color=color.green))
        except Exception as e:
            logger.error(f"Error in unhide command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    running_unhideall = {}
    @commands.hybrid_command(
        name="unhideall",
        help="Unhide all channels in the server",
        aliases=["unhidechannels"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def unhideall(self, ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels',role_position_check=True):
                return
            if self.running_unhideall.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another unhideall command is already running",color=color.red),delete_after=10)
                return
            async def unhide_channel(channel):
                try:
                    if isinstance(channel, discord.TextChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == True:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
                    elif isinstance(channel, discord.VoiceChannel):
                        if channel.permissions_for(ctx.guild.default_role).view_channel == True and channel.permissions_for(ctx.guild.default_role).connect == True:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=True, connect=True)
                    else:
                        if channel.permissions_for(ctx.guild.default_role).view_channel == True:
                            return
                        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
                except Exception as e:
                    logger.error(f"Error in unhideall command: {e}")
            processing_message = await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.LOADING} Unhiding all channels",color=color.yellow))
            self.running_unhideall[ctx.guild.id] = True
            for channel in ctx.guild.channels:
                try:
                    await unhide_channel(channel)
                    await asyncio.sleep(1.5)
                except Exception as e:
                    pass
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            await processing_message.edit(embed=discord.Embed(description="All channels have been unhidden",color=color.green))
        except Exception as e:
            if ctx.guild.id in self.running_unhideall:
                del self.running_unhideall[ctx.guild.id]
            logger.error(f"Error in unhideall command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)


    # main primary command will also will be in slash command
    # role is not in the slashcommand fix it
    @commands.hybrid_group(
        name="role",
        help="Manage roles of the users",
        with_app_command=True,
        invoke_without_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=60,type=commands.BucketType.user)
    # role @member @role
    @discord.app_commands.describe(member="The member to assign or remove the role", role="The role to assign or remove")
    async def role_command(self,ctx:commands.Context,member:discord.Member=None,*,role:discord.Role=None):
        try:
            if not member:
                # show all the commands this group has
                embed = discord.Embed(
                    title="Role Commands",
                    description="Manage roles of the users",
                    color=color.random_color()
                )
                embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} <member> <role>` : give or remove a role to a member"
                if hasattr(ctx.command,'commands'):
                    for command in ctx.command.commands:
                        embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}"
                await ctx.send(embed=embed)
            elif not role:
                return await ctx.send(embed=discord.Embed(description=f"Invalid Syntax\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} <member> <role>`",color=color.red))


            else:
                try:
                    if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'):
                        return
                    if not await checks.check_if_user_can_manage_this_role(ctx,role):
                        return
                    
                    if role in member.roles:
                        await member.remove_roles(role)
                        await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.DELETE} Removed {role.mention} from {member.mention}",color=color.green))
                    else:
                        await member.add_roles(role)
                        await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.CREATE} Added {role.mention} to {member.mention}",color=color.green))          
                except Exception as e:
                    logger.error(f"Error in role command: {e}")
                    await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in role command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)


    running_humans_command = {} # running_humans_command[guild_id] = True/False

    # role humans @role
    @role_command.command(
        name="humans",
        help="Manage roles of the humans in the server",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def role_humans_command(self,ctx:commands.Context,role:discord.Role):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'):
                return
            if not await checks.check_if_user_can_manage_this_role(ctx,role):
                return
            
            if self.running_humans_command.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another humans command is already running",color=color.red),delete_after=10)
                return

            def calculate_role_delay(user_count: int) -> float:
                # Maximum allowed rate per second
                max_rate_per_second = 16.67
                
                # Calculate delay per role change (in seconds)
                delay_per_user = 1 / max_rate_per_second
                
                # Adding a safety buffer
                safe_delay = delay_per_user + 2 # 0.04 seconds is added as a safety buffer
                
                # Calculate total time required for the given number of users
                total_time = user_count * safe_delay
                
                return safe_delay, total_time
            
            # Get all the humans in the server
            humans = [member for member in ctx.guild.members if not member.bot and role not in member.roles]
            total_humans = len(humans)
            delay_per_user, total_time = calculate_role_delay(total_humans)

            # Send a message aproximating the time required to complete the task
            message = await ctx.send(embed=discord.Embed(description=f"Estimated time to complete the task: <t:{int(datetime.datetime.now().timestamp() + datetime.timedelta(seconds=total_time).total_seconds()+20)}:R>",color=color.random_color()))
            self.running_humans_command[ctx.guild.id] = True

            # Add the role to all the humans
            added_users = 0
            for human in humans:
                try:
                    if role in human.roles:
                        continue
                    await human.add_roles(role)
                    await asyncio.sleep(delay_per_user)
                    added_users += 1
                except Exception as e:
                    pass
            await message.edit(embed=discord.Embed(description=f"Added {role.mention} to {added_users} users",color=color.green))
        except Exception as e:
            logger.error(f"Error in role humans command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
        self.running_humans_command[ctx.guild.id] = False


    running_bots_command = {} # running_bots_command[guild_id] = True/False

    # role bots @role
    @role_command.command(
        name="bots",
        help="Manage roles of the bots in the server",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=300,type=commands.BucketType.guild)
    async def role_bots_command(self,ctx:commands.Context,role:discord.Role):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_roles'):
                return
            if not await checks.check_if_user_can_manage_this_role(ctx,role):
                return
            
            if self.running_bots_command.get(ctx.guild.id,False):
                await ctx.send(embed=discord.Embed(description="Another bots command is already running",color=color.red),delete_after=10)
                return

            def calculate_role_delay(user_count: int) -> float:
                # Maximum allowed rate per second
                max_rate_per_second = 16.67
                
                # Calculate delay per role change (in seconds)
                delay_per_user = 1 / max_rate_per_second
                
                # Adding a safety buffer
                safe_delay = delay_per_user + 2 # 0.04 seconds is added as a safety buffer
                
                # Calculate total time required for the given number of users
                total_time = user_count * safe_delay
                
                return safe_delay, total_time
            
            # Get all the bots in the server
            bots = [member for member in ctx.guild.members if member.bot and role not in member.roles]
            total_bots = len(bots)
            delay_per_user, total_time = calculate_role_delay(total_bots)

            # Send a message aproximating the time required to complete the task
            message = await ctx.send(embed=discord.Embed(description=f"Estimated time to complete the task: <t:{int(datetime.datetime.now().timestamp() + datetime.timedelta(seconds=total_time).total_seconds()+20)}:R>",color=color.random_color()))

            self.running_bots_command[ctx.guild.id] = True

            # Add the role to all the bots
            added_users = 0
            for bot in bots:
                try:
                    if role in bot.roles:
                        continue
                    await bot.add_roles(role)
                    await asyncio.sleep(delay_per_user)
                    added_users += 1
                except Exception as e:
                    pass
            await message.edit(embed=discord.Embed(description=f"Added {role.mention} to {added_users} bots",color=color.green))
        except Exception as e:
            logger.error(f"Error in role bots command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
        self.running_bots_command[ctx.guild.id] = False

    @commands.command(
        name="mute",
        help="Mute a member in the server",
        aliases=["timeout"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5,per=60,type=commands.BucketType.user)
    # mute @member 2h[optional] reason[optional]
    async def mute_command(self,ctx:commands.Context,member:discord.Member,time:str,*,reason:str='No reason provided'):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'moderate_members'):
                return
            
            # check if the bot has the required permissions
            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send(embed=discord.Embed(description="I don't have the required permissions to mute members",color=color.red),delete_after=10)
                return

            if member.guild_permissions.administrator:
                await ctx.send(embed=discord.Embed(description=f"{member.mention} is an administrator",color=color.red),delete_after=10)
                return
            
            if member == ctx.author:
                await ctx.send(embed=discord.Embed(description=f"Dropping a piano on your head...",color=color.red),delete_after=10)
                return
            
            if member == ctx.guild.me:
                await ctx.send(embed=discord.Embed(description=f"What have I done to you?",color=color.red),delete_after=10)
                return
            
            if member.top_role >= ctx.author.top_role:
                await ctx.send(embed=discord.Embed(description=f"You can't mute {member.mention} cause their role is higher than you",color=color.red),delete_after=10)
                return

            if member.top_role >= ctx.guild.me.top_role:
                await ctx.send(embed=discord.Embed(description=f"I can't mute {member.mention} cause their role is higher than me",color=color.red),delete_after=10)
                return

            if await checks.check_is_owner_raw(member,ctx.guild):
                await ctx.send(embed=discord.Embed(description=f"You can't mute the owner of the server",color=color.red),delete_after=10)
                return
            
            if member.is_timed_out():
                await ctx.send(embed=discord.Embed(description=f"{member.mention} is already muted",color=color.red),delete_after=10)
                return
            
            # convert time from 1s, 1m, 1h, 1d to seconds
            
            try:
                time = time.lower()
                if time:
                    time = time.replace('s','').replace('m','*60').replace('h','*60*60').replace('d','*60*60*24')
                    time = eval(time)
            except Exception as e:
                time = None
                
            try:
                await member.timeout(datetime.timedelta(seconds=time),reason=reason)
                await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.SUCCESS} {member.mention} has been muted",color=color.green))
            except Exception as e:
                logger.error(f"Error in mute command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in mute command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @commands.group(
        name="unmute",
        help="Unmute a member in the server",
        invoke_without_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=5,per=60,type=commands.BucketType.user)
    # unmute @member reason[optional]
    async def unmute_command(self,ctx:commands.Context,member:discord.Member,*,reason:str='No reason provided'):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'moderate_members'):
                return
            
            # check if the bot has the required permissions
            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send(embed=discord.Embed(description="I don't have the required permissions to unmute members",color=color.red),delete_after=10)
                return

            if member.is_timed_out():
                await member.timeout(None,reason=reason)
                await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.SUCCESS} {member.mention} has been unmuted",color=color.green))
            else:
                await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} {member.mention} is not muted",color=color.red),delete_after=10)
        except Exception as e:
            logger.error(f"Error in unmute command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @unmute_command.command(
        name="all",
        help="Unmute all members in the server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=120,type=commands.BucketType.guild)
    async def unmute_all_command(self,ctx:commands.Context,*,reason:str='No reason provided'):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'moderate_members'):
                return
            
            # check if the bot has the required permissions
            if not ctx.guild.me.guild_permissions.moderate_members:
                await ctx.send(embed=discord.Embed(description="I don't have the required permissions to unmute members",color=color.red),delete_after=10)
                return

            muted_members = [member for member in ctx.guild.members if member.is_timed_out()]
            count = 0
            for member in muted_members:
                try:
                    await member.timeout(None,reason=reason)
                    count += 1
                except Exception as e:
                    pass
            await ctx.send(embed=discord.Embed(description=f"Unmuted {len(count)} members out of {len(muted_members)} muted members",color=color.green))
        except Exception as e:
            logger.error(f"Error in unmute all command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @commands.hybrid_group(
        name="mediachannel",
        help="Manage media channels in the server",
        invoke_without_command=True,
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            
            embed = discord.Embed(
                title="Media Channel Commands",
                description="Here are the commands to manage media channels",
                color=color.random_color()
            )
            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}"
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in media channel command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @media_channel_command.command(
        name="add",
        help="Add a media channel",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_add_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                if cache.media_channels.get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is already a media channel",color=color.red),delete_after=10)
                    return
                
                guilds_subscription = cache.guilds.get(str(ctx.guild.id),{}).get('subscription','free')

                if guilds_subscription == 'free':
                    media_channels_limit = 1
                elif guilds_subscription == 'silver_guild_preminum':
                    media_channels_limit = 3
                elif guilds_subscription == 'golden_guild_premium':
                    media_channels_limit = 5
                elif guilds_subscription == 'diamond_guild_premium':
                    media_channels_limit = 10
                else:
                    media_channels_limit = 1
                
                if len(cache.media_channels.get(str(ctx.guild.id),{})) >= media_channels_limit:
                    await ctx.send(embed=discord.Embed(description=f"Media channels limit reached. You can only have {media_channels_limit} media channels",color=color.red),delete_after=10)
                    return

                await storage.media_channels.insert(guild_id=ctx.guild.id,channel_id=channel.id)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been added as a media channel",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in media channel add command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel add command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @media_channel_command.command(
        name="remove",
        help="Remove a media channel",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_remove_command(self,ctx:commands.Context,channel:discord.TextChannel):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                if not cache.media_channels.get(str(ctx.guild.id),{}).get(str(channel.id)):
                    await ctx.send(embed=discord.Embed(description=f"{channel.mention} is not a media channel",color=color.red),delete_after=10)
                    return
                await storage.media_channels.delete(guild_id=ctx.guild.id,channel_id=channel.id)
                await ctx.send(embed=discord.Embed(description=f"{channel.mention} has been removed as a media channel",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in media channel remove command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel remove command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @media_channel_command.command(
        name="list",
        help="List media channels",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=30,type=commands.BucketType.guild)
    async def media_channel_list_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                media_channels = cache.media_channels.get(str(ctx.guild.id),{})
                
                if not media_channels:
                    await ctx.send(embed=discord.Embed(description="No media channels are added",color=color.red),delete_after=10)
                    return
                embed = discord.Embed(
                    title="Media Channels",
                    color=color.random_color()
                )
                embed.description = ' | '.join([f"<#{channel_id}>" for channel_id in media_channels.keys()])
                embed.set_footer(text=f"Total media channels: {len(media_channels)}")
                await ctx.send(embed=embed)
            except Exception as e:
                logger.error(f"Error in media channel list command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel list command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)

    @media_channel_command.command(
        name='reset',
        help="Reset all media channels",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1,per=120,type=commands.BucketType.guild)
    async def media_channel_reset_command(self,ctx:commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'administrator'):
                return
            try:
                await storage.media_channels.delete(guild_id=ctx.guild.id)
                await ctx.send(embed=discord.Embed(description="All media channels have been reset",color=color.green),delete_after=10)
            except Exception as e:
                logger.error(f"Error in media channel reset command: {e}")
                await ctx.send("An error occurred while processing the command.",delete_after=5)
        except Exception as e:
            logger.error(f"Error in media channel reset command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
    
    @commands.command(
        name="nickname",
        help="Change the nickname of a member",
        aliases=["nick"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3,per=30,type=commands.BucketType.user)
    async def nickname_command(self,ctx:commands.Context,member:discord.Member,*,nickname:str=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx, 'manage_nicknames'):
                return

            if not await checks.check_if_user_can_manage_this_member(ctx,member):
                return
            print (nickname)
            await member.edit(nick=nickname)
            await ctx.send(embed=discord.Embed(description=f"{member.mention}'s nickname has been changed to {nickname}",color=color.green))
        except Exception as e:
            logger.error(f"Error in nickname command: {e}")
            await ctx.send("An error occurred while processing the command.",delete_after=5)
        

