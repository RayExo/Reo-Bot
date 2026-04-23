import discord


from discord.ext import commands


import datetime


import traceback, sys


from reo.src.checks import checks


from reo.memory.cache import cache


import storage.antinuke_bypass


import storage.antinuke_settings


from reo.console.logging import logger


from reo.style import color


from reo.utils import pings


import asyncio


from reo.config.config import BotConfigClass


BotConfig = BotConfigClass()


import json


from reo.engine.Bot import AutoShardedBot


import storage


class Security(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Security"

            category = "Main"

            description = "Security commands"

            hidden = False

            emoji = self.bot.emoji.SECURITY

        self.cog_info = cog_info

    @commands.hybrid_group(
        name="antinuke",
        with_app_command=True,
        help="Enable/Disable Anti-Nuke system",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def antinuke_command(self, ctx: commands.Context, option: str = None):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "manage_guild"):

                return

            embed = discord.Embed(
                title="AntiNuke Commands",
                description="These are the Antinuke commands",
                color=color.green,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"\n\n{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name} - {command.help}"

            embed.set_footer(
                text=f"REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antinuke_command.command(
        name="enable", help="Enable Anti-Nuke system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def antinuke_command_enable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            cache_antinuke_settings = cache.antinuke_settings.get(str(ctx.guild.id), {})

            if not cache_antinuke_settings:

                await storage.antinuke_settings.insert(guild_id=ctx.guild.id)

                cache_antinuke_settings = cache.antinuke_settings.get(
                    str(ctx.guild.id), {}
                )

            if cache_antinuke_settings.get("enabled"):

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.WARNING} : Anti-Nuke system is already enabled",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            await storage.antinuke_settings.update(
                cache_antinuke_settings.get("id"), enabled=True
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.SUCCESS} : Anti-Nuke system has been enabled",
                    color=color.green,
                ),
                delete_after=30,
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antinuke_command.command(
        name="disable", help="Disable Anti-Nuke system", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def antinuke_command_disable(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            cache_antinuke_settings = cache.antinuke_settings.get(str(ctx.guild.id), {})

            if not cache_antinuke_settings:

                await storage.antinuke_settings.insert(guild_id=ctx.guild.id)

                cache_antinuke_settings = cache.antinuke_settings.get(
                    str(ctx.guild.id), {}
                )

            if not cache_antinuke_settings.get("enabled"):

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.WARNING} : Anti-Nuke system is already disabled",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            await storage.antinuke_settings.update(
                cache_antinuke_settings.get("id"), enabled=False
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.SUCCESS} : Anti-Nuke system has been disabled",
                    color=color.green,
                ),
                delete_after=30,
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @antinuke_command.command(
        name="settings", help="Edit Anti-Nuke settings", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def antinuke_command_settings(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            setup_cog = self.bot.get_command("setup").cog

            await setup_cog.AntiNuke_Module(ctx)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.ERROR} : An error occurred while trying to setup Anti-Nuke settings",
                    color=color.red,
                ),
                delete_after=10,
            )

    @commands.hybrid_group(
        name="whitelist",
        with_app_command=True,
        help="Whitelist a user from Anti-Nuke system",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def whitelist_command(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Anti-Nuke Whitelist Commands",
                description="Whitelist a user from Anti-Nuke system\n\n",
                color=color.purple,
            )

            if hasattr(ctx.command, "commands") and len(ctx.command.commands) > 0:

                for command in ctx.command.commands:

                    embed.description += f"`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}\n"

            embed.set_footer(
                text=f"REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @whitelist_command.command(
        name="add", help="Add a user to whitelist", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=6, per=60, type=commands.BucketType.guild)
    async def whitelist_command_add(
        self, ctx: commands.Context, member: discord.Member
    ):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            if not member:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"Please provide a member to whitelist",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            cache_antinuke_whitelist = cache.antinuke_bypass.get(str(ctx.guild.id), {})

            if len(cache_antinuke_whitelist) >= 50:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.ERROR} : You can only whitelist 10 users",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            if str(member.id) in cache_antinuke_whitelist:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.WARNING} : User is already whitelisted",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            await storage.antinuke_bypass.insert(
                guild_id=ctx.guild.id, user_id=member.id
            )

            await self.whitelist_command_edit(ctx, member)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @whitelist_command.command(
        name="delete", help="Delete a user from whitelist", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def whitelist_command_delete(
        self, ctx: commands.Context, member: discord.Member
    ):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            if not member:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"Please provide a member to whitelist",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            cache_antinuke_whitelist = cache.antinuke_bypass.get(str(ctx.guild.id), {})

            if str(member.id) not in cache_antinuke_whitelist:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.WARNING} : User is not whitelisted",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            await storage.antinuke_bypass.delete(
                guild_id=ctx.guild.id, user_id=member.id
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.SUCCESS} : User has been removed from whitelist",
                    color=color.green,
                ),
                delete_after=30,
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @whitelist_command.command(
        name="edit", help="Edit whitelist settings of a user", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def whitelist_command_edit(
        self, ctx: commands.Context, member: discord.Member
    ):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            if not member:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"Please provide a member to whitelist",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            cache_antinuke_whitelist = cache.antinuke_bypass.get(
                str(ctx.guild.id), {}
            ).get(str(member.id), None)

            if not cache_antinuke_whitelist:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ANTINUKE} : {self.bot.emoji.WARNING} : User is not whitelisted",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            whitelist_variabled = [
                "anti_channel_create",
                "anti_channel_delete",
                "anti_channel_update",
                "anti_role_create",
                "anti_role_delete",
                "anti_role_update",
                "anti_member_ban",
                "anti_member_unban",
                "anti_member_kick",
                "anti_member_update",
                "anti_bot_add",
                "anti_invite_delete",
                "anti_webhook_create",
                "anti_webhook_update",
                "anti_server_update",
                "anti_emote_create",
                "anti_emote_delete",
                "anti_emote_update",
                "anti_prune_member",
                "anti_everyone_mention",
            ]

            async def get_embed():

                cache_antinuke_whitelist = cache.antinuke_bypass.get(
                    str(ctx.guild.id), {}
                ).get(str(member.id), {})

                embed = discord.Embed(
                    title=f"{self.bot.emoji.ANTINUKE} Anti-Nuke Whitelist Settings",
                    description=f"Whitelist Settings for {member.mention}\n\n",
                    color=color.purple,
                )

                embed.set_thumbnail(url=member.display_avatar.url)

                embed.set_footer(text="Be sure while giving whitelist settings to user")

                for variable in whitelist_variabled:

                    embed.description += f"{self.bot.emoji.ENABLED_BUNDLE if cache_antinuke_whitelist.get(variable) else self.bot.emoji.DISABLED_BUNDLE} : {variable.replace('_',' ').title()}\n"

                return embed

            timeout_time = 300

            cancled = False

            def reset_timeout(timeout=300):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disable=False):

                cache_antinuke_whitelist = cache.antinuke_bypass.get(
                    str(ctx.guild.id), {}
                ).get(str(member.id), {})

                view = discord.ui.View(timeout=300)

                reset_timeout()

                click_to_enable_all_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Enable All",
                    emoji=self.bot.emoji.SUCCESS,
                    custom_id="enable_all",
                    disabled=(
                        True
                        if all(
                            cache_antinuke_whitelist.get(variable)
                            for variable in whitelist_variabled
                        )
                        else False
                    ),
                )

                click_to_enable_all_button.callback = (
                    lambda i: click_to_enable_all_button_callback(i)
                )

                click_to_disable_all_button = discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    label="Disable All",
                    emoji=self.bot.emoji.FAILED,
                    custom_id="disable_all",
                    disabled=(
                        True
                        if all(
                            not cache_antinuke_whitelist.get(variable)
                            for variable in whitelist_variabled
                        )
                        else False
                    ),
                )

                click_to_disable_all_button.callback = (
                    lambda i: click_to_disable_all_button_callback(i)
                )

                edit_select = discord.ui.Select(
                    placeholder="Select A Setting To Edit",
                    min_values=1,
                    max_values=1,
                    options=(
                        [
                            discord.SelectOption(
                                label=variable.replace("_", " ").title(),
                                value=variable,
                                emoji=(
                                    self.bot.emoji.SUCCESS
                                    if cache_antinuke_whitelist.get(variable)
                                    else self.bot.emoji.FAILED
                                ),
                                description=(
                                    f"Click to Disable This Permission"
                                    if cache_antinuke_whitelist.get(variable)
                                    else f"Click to Enable This Permission"
                                ),
                            )
                            for variable in whitelist_variabled
                        ]
                        if len(whitelist_variabled) > 0
                        else [
                            discord.SelectOption(
                                label="No Setting Found", value="no_setting_found"
                            )
                        ]
                    ),
                    disabled=True if len(cache_antinuke_whitelist) == 0 else False,
                )

                edit_select.callback = lambda i: edit_select_callback(i)

                cancle_button = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Cancel",
                    emoji=self.bot.emoji.CANCLED,
                    custom_id="cancle",
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(click_to_enable_all_button)

                view.add_item(click_to_disable_all_button)

                view.add_item(edit_select)

                view.add_item(cancle_button)

                if disable:

                    for item in view.children:

                        item.disabled = True

                return view

            async def click_to_enable_all_button_callback(
                interaction: discord.Interaction,
            ):

                try:

                    if interaction.user.id != ctx.author.id:

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                        return

                    await interaction.response.defer()

                    cache_antinuke_whitelist = cache.antinuke_bypass.get(
                        str(ctx.guild.id), {}
                    ).get(str(member.id), {})

                    await storage.antinuke_bypass.update(
                        id=cache_antinuke_whitelist.get("id"),
                        guild_id=ctx.guild.id,
                        user_id=member.id,
                        **{variable: True for variable in whitelist_variabled},
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.ERROR} : An error occurred while trying to enable all whitelist settings",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

            async def click_to_disable_all_button_callback(
                interaction: discord.Interaction,
            ):

                try:

                    if interaction.user.id != ctx.author.id:

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                        return

                    await interaction.response.defer()

                    cache_antinuke_whitelist = cache.antinuke_bypass.get(
                        str(ctx.guild.id), {}
                    ).get(str(member.id), {})

                    await storage.antinuke_bypass.update(
                        id=cache_antinuke_whitelist.get("id"),
                        guild_id=ctx.guild.id,
                        user_id=member.id,
                        **{variable: False for variable in whitelist_variabled},
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.ERROR} : An error occurred while trying to disable all whitelist settings",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

            async def edit_select_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                        return

                    await interaction.response.defer()

                    variable = interaction.data["values"][0]

                    cache_antinuke_whitelist = cache.antinuke_bypass.get(
                        str(ctx.guild.id), {}
                    ).get(str(member.id), {})

                    if variable not in whitelist_variabled:

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : Invalid Setting",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                        return

                    await storage.antinuke_bypass.update(
                        id=cache_antinuke_whitelist.get("id"),
                        guild_id=ctx.guild.id,
                        user_id=member.id,
                        **{variable: not cache_antinuke_whitelist.get(variable)},
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.ERROR} : An error occurred while trying to edit whitelist settings",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

            async def cancle_button_callback(interaction: discord.Interaction):

                nonlocal cancled

                if interaction.user.id != ctx.author.id:

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

                    return

                await interaction.response.defer()

                cancled = True

                await interaction.message.edit(
                    embed=await get_embed(), view=await get_view(disable=True)
                )

            embed = await get_embed()

            view = await get_view()

            message = await ctx.send(embed=embed, view=view)

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(view=await get_view(disable=True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @whitelist_command.command(
        name="list", help="List all whitelisted users", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.guild)
    async def whitelist_command_list(self, ctx: commands.Context):

        if not await checks.check_is_owner(ctx, notify=True):

            return

        async def home_embed():

            cache_antinuke_whitelist = cache.antinuke_bypass.get(str(ctx.guild.id), {})

            embed = discord.Embed(
                title=f"{self.bot.emoji.ANTINUKE} Anti-Nuke Whitelist",
                color=color.purple,
            )

            embed.set_footer(text="Be sure to whitelist only trusted users")

            if len(cache_antinuke_whitelist) == 0:

                embed.description = "No user is whitelisted"

                return embed

            else:

                description = ""

                for user_id in cache_antinuke_whitelist:

                    user = ctx.guild.get_member(int(user_id))

                    description += (
                        f"{self.bot.emoji.USER} : "
                        + (user.mention if user else f"Unknown User ({user_id})")
                        + "\n"
                    )

                embed.description = description

                return embed

        timeout_time = 300

        cancled = False

        def reset_timeout(timeout=300):

            nonlocal timeout_time

            timeout_time = timeout

        async def home_view(disable=False):

            cache_antinuke_whitelist = cache.antinuke_bypass.get(str(ctx.guild.id), {})

            reset_timeout()

            view = discord.ui.View(timeout=300)

            add_user_button = discord.ui.Button(
                style=discord.ButtonStyle.primary,
                label="Add User",
                emoji=self.bot.emoji.CREATE,
                custom_id="add_user",
            )

            delete_user_button = discord.ui.Button(
                style=discord.ButtonStyle.danger,
                label="Delete User",
                emoji=self.bot.emoji.DELETE,
                custom_id="delete_user",
            )

            options = [
                discord.SelectOption(
                    label=f"{user.display_name if (user := ctx.guild.get_member(int(user_id))) else f'Unknown User ({user_id})'}",
                    value=str(user_id),
                    emoji=self.bot.emoji.USER,
                    description=f"Select this user to edit whitelist settings",
                )
                for user_id in cache_antinuke_whitelist.keys()
            ]

            edit_user_settings_button = discord.ui.Select(
                placeholder="Select A Whitelisted User To Edit",
                min_values=1,
                max_values=1,
                options=(
                    options
                    if len(options) > 0
                    else [
                        discord.SelectOption(
                            label="No User Found", value="no_user_found"
                        )
                    ]
                ),
                disabled=True if len(cache_antinuke_whitelist) == 0 else False,
            )

            add_user_button.callback = lambda i: add_user_button_callback(i)

            delete_user_button.callback = lambda i: delete_user_button_callback(i)

            edit_user_settings_button.callback = (
                lambda i: edit_user_settings_button_callback(i)
            )

            cancle_button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Cancel",
                emoji=self.bot.emoji.CANCLED,
                custom_id="cancle",
            )

            cancle_button.callback = lambda i: cancle_button_callback(i)

            view.add_item(add_user_button)

            view.add_item(delete_user_button)

            view.add_item(edit_user_settings_button)

            view.add_item(cancle_button)

            if disable:

                for item in view.children:

                    item.disabled = True

            return view

        async def edit_user_settings_button_callback(interaction: discord.Interaction):

            try:

                if interaction.user.id != ctx.author.id:

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

                    return

                await interaction.response.defer()

                user_id = int(interaction.data["values"][0])

                nonlocal cancled

                cancled = True

                await interaction.message.delete()

                member = await ctx.guild.fetch_member(int(user_id))

                if not member:

                    await ctx.send(
                        embed=discord.Embed(
                            description=f"User not found", color=color.red
                        ),
                        delete_after=10,
                    )

                    return

                await self.whitelist_command(ctx, "edit", member)

            except Exception as e:

                logger.error(
                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                )

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} : An error occurred while trying to edit user whitelist settings",
                        color=color.red,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

        async def cancle_button_callback(interaction: discord.Interaction):

            nonlocal cancled

            if interaction.user.id != ctx.author.id:

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                        color=color.red,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

                return

            await interaction.response.defer()

            cancled = True

            await interaction.message.edit(
                embed=await home_embed(), view=await home_view(disable=True)
            )

        async def delete_user_button_callback(interaction: discord.Interaction):

            cache_antinuke_whitelist = cache.antinuke_bypass.get(str(ctx.guild.id), {})

            if interaction.user.id != ctx.author.id:

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                        color=color.red,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

                return

            await interaction.response.defer()

            try:

                view = discord.ui.View(timeout=300)

                reset_timeout()

                select_user_select = discord.ui.Select(
                    placeholder=(
                        "Select A User To Delete"
                        if len(cache_antinuke_whitelist) > 0
                        else "No User To Delete"
                    ),
                    min_values=1,
                    max_values=1,
                    options=(
                        [
                            discord.SelectOption(
                                label=f"{user.display_name if (user := ctx.guild.get_member(int(user_id))) else f'Unknown User ({user_id})'}",
                                value=str(user_id),
                                emoji=self.bot.emoji.USER,
                                description=f"Select this user to delete from whitelist",
                            )
                            for user_id in cache_antinuke_whitelist.keys()
                        ]
                        if len(cache_antinuke_whitelist) > 0
                        else [
                            discord.SelectOption(
                                label="No User Found", value="no_user_found"
                            )
                        ]
                    ),
                    row=0,
                    disabled=True if len(cache_antinuke_whitelist) == 0 else False,
                )

                async def delete_user_select_callback(interaction: discord.Interaction):

                    try:

                        user_id = int(interaction.data["values"][0])

                        if str(user_id) not in cache_antinuke_whitelist:

                            await interaction.response.send_message(
                                embed=discord.Embed(
                                    description=f"{self.bot.emoji.ERROR} : User is not whitelisted",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                            return

                        await interaction.response.defer()

                        await storage.antinuke_bypass.delete(
                            guild_id=ctx.guild.id, user_id=user_id
                        )

                        await interaction.message.edit(
                            embed=await home_embed(), view=await home_view()
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : An error occurred while trying to delete user from whitelist",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                select_user_select.callback = lambda i: delete_user_select_callback(i)

                async def back_button_callback(interaction: discord.Interaction):

                    try:

                        if interaction.user.id != ctx.author.id:

                            await interaction.response.send_message(
                                embed=discord.Embed(
                                    description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                            return

                        await interaction.response.edit_message(
                            embed=await home_embed(), view=await home_view()
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                        )

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : An error occurred while trying to go back",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                back_button = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Back",
                    emoji=self.bot.emoji.BACK,
                    custom_id="back",
                    row=1,
                )

                back_button.callback = lambda i: back_button_callback(i)

                view.add_item(select_user_select)

                view.add_item(back_button)

                await interaction.message.edit(view=view)

            except Exception as e:

                logger.error(
                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                )

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} : An error occurred while trying to delete user from whitelist",
                        color=color.red,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

        async def add_user_button_callback(interaction: discord.Interaction):

            try:

                if interaction.user.id != ctx.author.id:

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

                    return

                await interaction.response.defer()

                view = discord.ui.View(timeout=300)

                reset_timeout()

                async def user_select_callback(interaction: discord.Interaction):

                    cache_antinuke_whitelist = cache.antinuke_bypass.get(
                        str(ctx.guild.id), {}
                    )

                    try:

                        user_id = int(interaction.data["values"][0])

                        if str(user_id) in cache_antinuke_whitelist:

                            await interaction.response.send_message(
                                embed=discord.Embed(
                                    description=f"{self.bot.emoji.ERROR} : User is already whitelisted",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                            return

                        await interaction.response.defer()

                        await storage.antinuke_bypass.insert(
                            guild_id=ctx.guild.id, user_id=int(user_id)
                        )

                        await interaction.message.edit(
                            embed=await home_embed(), view=await home_view()
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : An error occurred while trying to add user to whitelist",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                users_select = discord.ui.UserSelect(
                    placeholder="Select A User To Whitelist",
                    min_values=1,
                    max_values=1,
                    row=0,
                )

                users_select.callback = lambda i: user_select_callback(i)

                view.add_item(users_select)

                async def back_button_callback(interaction: discord.Interaction):

                    try:

                        if interaction.user.id != ctx.author.id:

                            await interaction.response.send_message(
                                embed=discord.Embed(
                                    description=f"{self.bot.emoji.ERROR} : You are not allowed to use this button",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                            return

                        await interaction.response.edit_message(
                            embed=await home_embed(), view=await home_view()
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description=f"{self.bot.emoji.ERROR} : An error occurred while trying to go back",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                back_button = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Back",
                    emoji=self.bot.emoji.BACK,
                    custom_id="back",
                    row=1,
                )

                back_button.callback = lambda i: back_button_callback(i)

                view.add_item(back_button)

                await interaction.message.edit(view=view)

            except Exception as e:

                logger.error(
                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                )

                await interaction.response.send_message(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} : An error occurred while trying to add user to whitelist",
                        color=color.red,
                    ),
                    ephemeral=True,
                    delete_after=10,
                )

        embed = await home_embed()

        view = await home_view()

        message = await ctx.send(embed=embed, view=view)

        while not cancled:

            timeout_time -= 1

            if timeout_time <= 0:

                await message.edit(view=None)

                break

            await asyncio.sleep(1)

    @commands.hybrid_group(
        name="extraowner",
        help="Manage extra owners in the server",
        invoke_without_command=True,
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.guild)
    async def extra_owner_command(self, ctx: commands.Context):

        try:

            if ctx.author != ctx.guild.owner and not checks.check_is_owner_predicate(
                ctx
            ):

                return await ctx.send(
                    embed=discord.Embed(
                        description="You need to be the owner of the server to manage extra owners",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            embed = discord.Embed(
                title="Extra Owner Commands",
                description="Here are the commands to manage extra owners",
                color=color.random_color(),
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}"

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in extra owner command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @extra_owner_command.command(
        name="add", help="Add an extra owner", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def extra_owner_add_command(
        self, ctx: commands.Context, member: discord.Member
    ):

        try:

            if ctx.author != ctx.guild.owner and not checks.check_is_owner_predicate(
                ctx
            ):

                return await ctx.send(
                    embed=discord.Embed(
                        description="You need to be the owner of the server to manage extra owners",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            if member == ctx.guild.owner:

                await ctx.send(
                    embed=discord.Embed(
                        description="You can't add the owner of the server as an extra owner",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            if member.bot:

                await ctx.send(
                    embed=discord.Embed(
                        description="You can't add a bot as an extra owner",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            guilds_cache = cache.guilds.get(str(ctx.guild.id), {})

            if not guilds_cache:

                try:

                    await storage.guilds.insert(guild_id=ctx.guild.id)

                except:

                    pass

                guilds_cache = cache.guilds.get(str(ctx.guild.id), {})

            if not guilds_cache:

                await ctx.send(
                    embed=discord.Embed(
                        description="An error occurred while processing the command.",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            extra_owner_ids = json.loads(guilds_cache.get("extra_owner_ids", "[]"))

            guilds_subscription = guilds_cache.get("subscription", "free")

            if guilds_subscription == "free":

                extra_owner_limit = 1

            elif guilds_subscription == "silver_guild_preminum":

                extra_owner_limit = 5

            elif guilds_subscription == "golden_guild_premium":

                extra_owner_limit = 10

            elif guilds_subscription == "diamond_guild_premium":

                extra_owner_limit = 20

            else:

                extra_owner_limit = 1

            if len(extra_owner_ids) >= extra_owner_limit:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"Extra owners limit reached. You can only have {extra_owner_limit} extra owners",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            if str(member.id) in extra_owner_ids:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{member.mention} is already an extra owner",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            extra_owner_ids.append(str(member.id))

            await storage.guilds.update(
                id=guilds_cache.get("id"), extra_owner_ids=json.dumps(extra_owner_ids)
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{member.mention} has been added as an extra owner",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in extra owner add command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @extra_owner_command.command(
        name="remove", help="Remove an extra owner", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    async def extra_owner_remove_command(
        self, ctx: commands.Context, member: discord.Member
    ):

        try:

            if ctx.author != ctx.guild.owner and not checks.check_is_owner_predicate(
                ctx
            ):

                return await ctx.send(
                    embed=discord.Embed(
                        description="You need to be the owner of the server to manage extra owners",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            guilds_cache = cache.guilds.get(str(ctx.guild.id), {})

            extra_owner_ids = json.loads(guilds_cache.get("extra_owner_ids", "[]"))

            if str(member.id) not in extra_owner_ids:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"{member.mention} is not an extra owner",
                        color=color.red,
                    ),
                    delete_after=10,
                )

                return

            extra_owner_ids.remove(str(member.id))

            await storage.guilds.update(
                id=guilds_cache.get("id"), extra_owner_ids=json.dumps(extra_owner_ids)
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{member.mention} has been removed as an extra owner",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in extra owner remove command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @extra_owner_command.command(
        name="list", help="List extra owners", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.guild)
    async def extra_owner_list_command(self, ctx: commands.Context):

        try:

            if ctx.author != ctx.guild.owner and not checks.check_is_owner_predicate(
                ctx
            ):

                return await ctx.send(
                    embed=discord.Embed(
                        description="You need to be the owner of the server to manage extra owners",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            guilds_cache = cache.guilds.get(str(ctx.guild.id), {})

            extra_owner_ids = json.loads(guilds_cache.get("extra_owner_ids", "[]"))

            if not extra_owner_ids:

                await ctx.send(
                    embed=discord.Embed(
                        description="No extra owners are added", color=color.red
                    ),
                    delete_after=10,
                )

                return

            embed = discord.Embed(
                description="Here are the extra owners of the server\n",
                color=color.random_color(),
            )

            embed.set_author(
                name=ctx.guild.name,
                icon_url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                ),
            )

            embed.set_thumbnail(
                url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                )
            )

            for index, extra_owner_id in enumerate(extra_owner_ids):

                member = ctx.guild.get_member(int(extra_owner_id))

                if member:

                    embed.description += f"\n{index+1}. {member.mention}"

            embed.set_footer(text=f"Total extra owners: {len(extra_owner_ids)}")

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in extra owner list command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )
