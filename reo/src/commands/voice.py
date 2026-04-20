import discord
from discord.ext import commands
import psutil
import asyncio
import io
import platform
import datetime
import time

from reo.src.checks import checks
from reo.memory.cache import cache
import traceback,sys
import re

import storage.afk
import storage.guilds
import storage.shop
import storage.users
from reo.console.logging import logger

from reo.style import color
from reo.workflows import ui
from reo.utils import pings


from reo.config.config import BotConfigClass
BotConfig = BotConfigClass()

import storage
from reo.workflows.afk_delay import afk_delay


from reo.engine.Bot import AutoShardedBot

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Voice"
            category = "Extra"
            description =  "Voice related commands"
            hidden =  False
            emoji = self.bot.emoji.MICROPHONE or "🎤"
        self.cog_info = cog_info

    @commands.command(
        name="vcmute",
        help="Mute a user in a voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcmute(self, ctx: commands.Context, member: discord.Member):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'mute_members'):
                return

            if not member.voice:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not in a voice channel",color=color.red))
            
            if member.voice.mute:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is already muted",color=color.red))
            
            try:
                await member.edit(mute=True)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been muted",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcunmute",
        help="Unmute a user in a voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcunmute(self, ctx: commands.Context, member: discord.Member):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'mute_members'):
                return

            if not member.voice:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not in a voice channel",color=color.red))
            
            if not member.voice.mute:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not muted",color=color.red))
            
            try:
                await member.edit(mute=False)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been unmuted",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcdeafen",
        help="Deafen a user in a voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdeafen(self, ctx: commands.Context, member: discord.Member):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'deafen_members'):
                return

            if not member.voice:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not in a voice channel",color=color.red))
            
            if member.voice.deaf:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is already deafened",color=color.red))
            
            try:
                await member.edit(deafen=True)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been deafened",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcundeafen",
        help="Undeafen a user in a voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcundeafen(self, ctx: commands.Context, member: discord.Member):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'deafen_members'):
                return

            if not member.voice:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not in a voice channel",color=color.red))
            
            if not member.voice.deaf:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not deafened",color=color.red))
            
            try:
                await member.edit(deafen=False)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been undeafened",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(
        name="vcmove",
        help="Move a user to a voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcmove(self, ctx: commands.Context, member: discord.Member, channel: discord.VoiceChannel):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'move_members'):
                return

            if not member.voice:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not in a voice channel",color=color.red))
            
            try:
                await member.move_to(channel)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been moved to {channel.mention}",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(
        name="vcmoveall",
        help="Move all users in a voice channel to another voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def vcmoveall(self, ctx: commands.Context, channel: discord.VoiceChannel, new_channel: discord.VoiceChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'manage_channels'):
                return
            if not await checks.check_is_moderator_permissions(ctx,'move_members'):
                return

            if not new_channel:
                if not ctx.author.voice:
                    return await ctx.send(embed=discord.Embed(description=f"You are not in a voice channel",color=color.red))
                new_channel = channel
                channel = ctx.author.voice.channel                
            
            if len(channel.members) == 0:
                return await ctx.send(embed=discord.Embed(description=f"{channel.mention} has no users",color=color.red))
            
            try:
                for member in channel.members:
                    try:
                        await member.move_to(new_channel)
                    except Exception as e:
                        pass
                await ctx.send(embed=discord.Embed(description=f"All users in {channel.mention} have been moved to {new_channel.mention}",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


    @commands.command(
        name="vcdisconnect",
        help="Disconnect a user from a voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdisconnect(self, ctx: commands.Context, member: discord.Member):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'move_members'):
                return

            if not member.voice:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not in a voice channel",color=color.red))
            
            try:
                await member.move_to(None)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been disconnected",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcpull",
        help="Pull a user to your voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcpull(self, ctx: commands.Context, member: discord.Member):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'move_members'):
                return

            if not ctx.author.voice:
                return await ctx.send(embed=discord.Embed(description=f"You are not in a voice channel",color=color.red))

            if not member.voice:
                return await ctx.send(embed=discord.Embed(description=f"{member.mention} is not in a voice channel",color=color.red))
            
            try:
                await member.move_to(ctx.author.voice.channel)
                await ctx.send(embed=discord.Embed(description=f"{member.mention} has been pulled to your voice channel",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    # vcmuteall
    # vcunmuteall
    # vcdeafenall
    # vcundeafenall

    @commands.command(
        name="vcmuteall",
        help="Mute all users in a voice channel"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcmuteall(self, ctx: commands.Context, channel: discord.VoiceChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'mute_members'):
                return

            if not channel:
                if not ctx.author.voice:
                    return await ctx.send(embed=discord.Embed(description=f"You are not in a voice channel",color=color.red))
                channel = ctx.author.voice.channel

            if len(channel.members) == 0:
                return await ctx.send(embed=discord.Embed(description=f"{channel.mention} has no users",color=color.red))
            
            try:
                for member in channel.members:
                    try:
                        await member.edit(mute=True)
                    except Exception as e:
                        pass
                await ctx.send(embed=discord.Embed(description=f"All users in {channel.mention} have been muted",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcunmuteall",
        help="Unmute all users in a voice channel",
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcunmuteall(self, ctx: commands.Context, channel: discord.VoiceChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'mute_members'):
                return

            if not channel:
                if not ctx.author.voice:
                    return await ctx.send(embed=discord.Embed(description=f"You are not in a voice channel",color=color.red))
                channel = ctx.author.voice.channel

            if len(channel.members) == 0:
                return await ctx.send(embed=discord.Embed(description=f"{channel.mention} has no users",color=color.red))
            
            try:
                for member in channel.members:
                    try:
                        await member.edit(mute=False)
                    except Exception as e:
                        pass
                await ctx.send(embed=discord.Embed(description=f"All users in {channel.mention} have been unmuted",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcdeafenall",
        help="Deafen all users in a voice channel",
        aliases=["vcdefall"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdeafenall(self, ctx: commands.Context, channel: discord.VoiceChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'deafen_members'):
                return

            if not channel:
                if not ctx.author.voice:
                    return await ctx.send(embed=discord.Embed(description=f"You are not in a voice channel",color=color.red))
                channel = ctx.author.voice.channel

            if len(channel.members) == 0:
                return await ctx.send(embed=discord.Embed(description=f"{channel.mention} has no users",color=color.red))
            
            try:
                for member in channel.members:
                    try:
                        await member.edit(deafen=True)
                    except Exception as e:
                        pass
                await ctx.send(embed=discord.Embed(description=f"All users in {channel.mention} have been deafened",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcundeafenall",
        help="Undeafen all users in a voice channel",
        aliases=["vcundefall"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcundeafenall(self, ctx: commands.Context, channel: discord.VoiceChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'deafen_members'):
                return

            if not channel:
                if not ctx.author.voice:
                    return await ctx.send(embed=discord.Embed(description=f"You are not in a voice channel",color=color.red))
                channel = ctx.author.voice.channel

            if len(channel.members) == 0:
                return await ctx.send(embed=discord.Embed(description=f"{channel.mention} has no users",color=color.red))
            
            try:
                for member in channel.members:
                    try:
                        await member.edit(deafen=False)
                    except Exception as e:
                        pass
                await ctx.send(embed=discord.Embed(description=f"All users in {channel.mention} have been undeafened",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(
        name="vcdisconnectall",
        help="Disconnect all users in a voice channel",
        aliases=["vckickall"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.user)
    async def vcdisconnectall(self, ctx: commands.Context, channel: discord.VoiceChannel=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'move_members'):
                return

            if not channel:
                if not ctx.author.voice:
                    return await ctx.send(embed=discord.Embed(description=f"You are not in a voice channel",color=color.red))
                channel = ctx.author.voice.channel

            if len(channel.members) == 0:
                return await ctx.send(embed=discord.Embed(description=f"{channel.mention} has no users",color=color.red))
            
            try:
                for member in channel.members:
                    try:
                        await member.move_to(None)
                    except Exception as e:
                        pass
                await ctx.send(embed=discord.Embed(description=f"All users in {channel.mention} have been disconnected",color=color.green))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"An error occured: {e}",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
    
