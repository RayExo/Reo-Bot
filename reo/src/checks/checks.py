from discord.ext import commands
import discord
from reo.style import color
import traceback
import json

from reo.memory.cache import cache

from reo.config import config

def check_ignore_predicate(ctx):
    try:
        if str(ctx.author.id) in cache.ignore_data.get('users',{}).get(str(ctx.guild.id),{}):
            return False
        if str(ctx.channel.id) in cache.ignore_data.get('channels',{}).get(str(ctx.guild.id),{}):
            return False
        return True
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False

def ignore_check():
    return commands.check(check_ignore_predicate)


def check_blacklist_predicate(ctx):
    try:
        if str(ctx.author.id) in cache.ban_data.get('users',{}):
            return False
        if str(ctx.guild.id) in cache.ban_data.get('guilds',{}):
            return False
        return True
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False

def blacklist_check():
    return commands.check(check_blacklist_predicate)





def check_is_admin_predicate(user):
    if user.id in cache.admins or user.id in cache.owners or user.id in config.users.root:
        return True
    return False

def is_admin():
    return commands.check(check_is_admin_predicate)

def check_is_owner_predicate(ctx):
    if ctx.author.id in cache.owners or ctx.author.id in config.users.root:
        return True
    return False

def is_owner():
    return commands.check(check_is_owner_predicate)

async def check_is_moderator_permissions(ctx:commands.Context,permission:str,role_position_check=False,notify=True):
    try:
        if check_is_admin_predicate(ctx.author):
            return True
        if await check_is_owner_raw(ctx.author,ctx.guild):
            return True
        if role_position_check:
            if ctx.author.top_role.position < ctx.guild.me.top_role.position:
                await ctx.send(embed=discord.Embed(description="You can't access this command because your role is lower than me",color=color.red),delete_after=5)
                return False
        
        if ctx.author.guild_permissions.administrator:
            return True
        
        if hasattr(ctx.author.guild_permissions,permission):
            if getattr(ctx.author.guild_permissions,permission):
                return True
        
        if notify:
            await ctx.send(embed=discord.Embed(description="You don't have the required permissions to use this command",color=color.red),delete_after=5)
        return False
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False


async def check_for_giveaway_permissions(ctx:commands.Context,permission:str="manage_guild"):
    try:
        if await check_is_owner(ctx,notify=False):
            return True
        if await check_is_moderator_permissions(ctx,permission,notify=False):
            return True
        cache_giveaways_permissions = cache.giveaways_permissions.get(str(ctx.guild.id),{})
        required_role_id = cache_giveaways_permissions.get('required_role_id',None)
        if required_role_id:
            if any([role.id == required_role_id for role in ctx.author.roles if not role.is_default()]):
                return True
        await ctx.send(embed=discord.Embed(description="You don't have the required permissions to use this command",color=color.red),delete_after=5)
        return False   
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False

async def check_extra_owners(member:discord.Member,guild:discord.Guild):
    try:
        extra_owner_ids = cache.guilds.get(str(guild.id), {}).get("extra_owner_ids", [])
        guilds_cache = cache.guilds.get(str(guild.id),{})
        guilds_subscription = guilds_cache.get('subscription','free')
        if guilds_subscription == 'free':
            extra_owner_limit = 1
        elif guilds_subscription == 'silver_guild_preminum':
            extra_owner_limit = 5
        elif guilds_subscription == 'golden_guild_premium':
            extra_owner_limit = 10
        elif guilds_subscription == 'diamond_guild_premium':
            extra_owner_limit = 20
        else:
            extra_owner_limit = 1
        if len(extra_owner_ids) > extra_owner_limit:
            return False
        if str(member.id) in extra_owner_ids and member.guild_permissions.administrator:
            return True
        return False
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False

async def check_is_owner_raw(user:discord.User,guild:discord.Guild):
    try:
        extra_owner = await check_extra_owners(user,guild)
        if user==guild.owner or extra_owner:
            return True
        return False
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False




async def close_ticket_permissions(user,guild:discord.Guild,creator_id:int,support_role_ids,notify=True):
    try:
        if check_is_admin_predicate(user):
            return True
        if await check_is_owner_raw(user,guild):
            return True
        if user.id == creator_id:
            return True
        if any([role.id in support_role_ids for role in user.roles]):
            return True
        if notify:
            await user.send(embed=discord.Embed(description="You don't have the required permissions to close this ticket",color=color.red))
        return False
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False


async def check_is_owner(ctx,notify=True):
    try:
        if ctx.author==ctx.guild.owner or check_is_owner_predicate(ctx) or await check_is_owner_raw(ctx.author,ctx.guild):
            return True
        if notify:
            await ctx.send(embed=discord.Embed(description="You are not authorized to use this command",color=color.red),delete_after=10)
        return False
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False

async def check_if_user_can_manage_this_role(ctx:commands.Context,role:discord.Role):
    if ctx.guild.me.top_role.position <= role.position:
        await ctx.send(embed=discord.Embed(description="The role is higher than me. I can't manage it",color=color.red),delete_after=5)
        return False
    if ctx.author == ctx.guild.owner:
        return True
    if ctx.author == role.guild.owner:
        return True
    if ctx.author.top_role.position > role.position:
        return True
    await ctx.send(embed=discord.Embed(description="You can't manage a role with a higher or same position as you",color=color.red),delete_after=5)
    return False

async def check_if_user_can_manage_this_member(ctx:commands.Context,member:discord.Member):
    if ctx.guild.me.top_role.position <= member.top_role.position:
        await ctx.send(embed=discord.Embed(description="The member has a higher role than me. I can't manage it",color=color.red),delete_after=5)
        return False
    if ctx.author == ctx.guild.owner:
        return True
    if ctx.guild.owner == member:
        await ctx.send(embed=discord.Embed(description="You can't manage the owner of the server",color=color.red),delete_after=5)
        return False
    if ctx.author == member:
        return True
    if ctx.author.top_role.position > member.top_role.position:
        return True
    await ctx.send(embed=discord.Embed(description="You can't manage a member with a higher or same role as you",color=color.red),delete_after=5)
    return False


async def check_if_user_can_be_banned_or_kicked(ctx:commands.Context,user:discord.Member):
    try:
        if ctx.author == user:
            await ctx.send(embed=discord.Embed(description="Are you kidding me? You can't ban yourself",color=color.red),delete_after=20)
            return False
        if user == ctx.guild.me:
            await ctx.send(embed=discord.Embed(description="What did I ever do to you?",color=color.red),delete_after=20)
            return False
        # if check_is_admin_predicate(user):
        #     await ctx.send(embed=discord.Embed(description="The User can't be Banned. Because the User is an Bot Admin/Owner",color=color.red),delete_after=20)
        #     return False
        if ctx.guild.owner == user:
            await ctx.send(embed=discord.Embed(description="You can't ban the owner of the server",color=color.red),delete_after=20)
            return False
        if ctx.author.top_role.position <= user.top_role.position and ctx.guild.owner != ctx.author:
            await ctx.send(embed=discord.Embed(description="You can't ban a user with a higher than you or same role as you.",color=color.red),delete_after=20)
            return False
        if ctx.guild.me.top_role.position <= user.top_role.position:
            await ctx.send(embed=discord.Embed(description="I can't ban a user with a higher role than me.",color=color.red),delete_after=20)
            return False
        return True
    except Exception as e:
        print(f"Error in file {__file__}: {traceback.format_exc()}")
        return False

