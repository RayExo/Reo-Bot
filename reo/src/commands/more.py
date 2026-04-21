import discord


from discord.ext import commands


import asyncio


import traceback, sys


import storage.antinuke_settings


import storage.auto_responder


import storage.automod


import storage.custom_roles


import storage.custom_roles_permissions


import storage.guilds_log


import storage.music


from reo.console.logging import logger


from reo.memory.cache import cache


from reo.src.checks import checks


import datetime


from reo.style import color


from reo.engine.Bot import AutoShardedBot


import storage


from reo.src.modules import j2c_controller


from storage import (
    guilds as guilds_db,
    j2c_settings as j2c_settings_db,
    guilds_log as guilds_log_db,
    antinuke_settings as antinuke_settings_db,
    welcomer_settings as welcomer_settings_db,
)


from storage import custom_roles as custom_roles_db


from reo.config.config import Types


redeem_code_types = Types.redeem_code_types


from reo.workflows.actions import change_guild_subscription, change_user_subscription


all_modules = ["JoinToCreateVC", "AutoMod", "AntiNuke", "Logging", "Welcome"]


joined_by_comma_all_modules = ", ".join(all_modules)


joined_by_newline_all_modules = "\n".join(all_modules)


punishments = ["Ban", "Kick", "Mute"]


def format_logging_channel(settings: dict, key: str) -> str:

    channel_id = settings.get(key)

    channel_text = f"<#{channel_id}>" if channel_id else "Not Set"

    return f"__Current:__ {channel_text}\n__ID:__ `{channel_id}`"


class More(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "More"

            category = "Extra"

            description = "Extra commands that don't fit in any other category"

            hidden = False

            emoji = self.bot.emoji.EXTRA

        self.cog_info = cog_info

    @commands.group(
        name="customrole",
        help="Setup the Custom Role Commands",
        aliases=["customroles", "cr"],
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=30, type=commands.BucketType.guild)
    async def customrole(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="Set Role Commands",
                description=f"Here are the list of commands\n\n",
                color=color.green,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}**\n"

            else:

                embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name}` - {ctx.command.help}**\n"

            embed.set_footer(
                text=f"REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @customrole.command(
        name="add", help="Add a Custom Role Command", aliases=["create", "new"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=6, per=60, type=commands.BucketType.guild)
    async def customrole_add(
        self, ctx: commands.Context, name: str, role: discord.Role
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if role.permissions.administrator:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"Role {role.mention} has administrator permissions and cannot be added as a custom role",
                        color=color.red,
                    )
                )

            name = name.lower()

            # check if the bot has any command with the same name

            if self.bot.get_command(name):

                return await ctx.send(f"Command with the name {name} already exists")

            customrole_cache = cache.custom_roles.get(str(ctx.guild.id), {})

            guilds_subscription = cache.guilds.get(str(ctx.guild.id), {}).get(
                "subscription", "free"
            )

            if guilds_subscription == "free":

                customrole_limit = 5

            elif guilds_subscription == "silver_guild_preminum":

                customrole_limit = 10

            elif guilds_subscription == "golden_guild_premium":

                customrole_limit = 15

            elif guilds_subscription == "diamond_guild_premium":

                customrole_limit = 20

            else:

                customrole_limit = 5

            if len(customrole_cache) >= customrole_limit:

                return await ctx.send(
                    f"Your guild has reached the limit of {customrole_limit} custom roles"
                )

            # check if the custom role already exists

            if customrole_cache.get(name):

                return await ctx.send(
                    f"Custom Role with the name {name} already exists"
                )

            await storage.custom_roles.insert(
                guild_id=ctx.guild.id, name=name, role_id=role.id
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"**Role {role.mention} has been added as a custom role with the name `{name}`**",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @customrole.command(
        name="remove", help="Remove a Custom Role Command", aliases=["delete", "del"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=6, per=60, type=commands.BucketType.guild)
    async def customrole_remove(self, ctx: commands.Context, name: str):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            name = name.lower()

            customrole_cache = cache.custom_roles.get(str(ctx.guild.id), {})

            if not customrole_cache.get(name):

                return await ctx.send(
                    f"Custom Role with the name {name} does not exist"
                )

            await storage.custom_roles.delete(guild_id=ctx.guild.id, name=name)

            await ctx.send(
                embed=discord.Embed(
                    description=f"**Custom Role with the name `{name}` has been removed**",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @customrole.command(
        name="update", help="Update a Custom Role Command", aliases=["edit"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=6, per=60, type=commands.BucketType.guild)
    async def customrole_update(
        self, ctx: commands.Context, name: str, role: discord.Role
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            name = name.lower()

            customrole_cache = cache.custom_roles.get(str(ctx.guild.id), {})

            if not customrole_cache.get(name):

                return await ctx.send(
                    f"Custom Role with the name {name} does not exist"
                )

            await storage.custom_roles.update(
                id=customrole_cache[name].get("id"),
                guild_id=ctx.guild.id,
                name=name,
                role_id=role.id,
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"**Role {role.mention} has been updated as a custom role with the name `{name}`**",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @customrole.command(
        name="list", help="List all Custom Role Commands", aliases=["all"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=6, per=60, type=commands.BucketType.guild)
    async def customrole_list(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            customrole_cache = cache.custom_roles.get(str(ctx.guild.id), {})

            if not customrole_cache:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"No Custom Roles have been setup", color=color.red
                    )
                )

            embed = discord.Embed(
                title="Custom Roles",
                description=f"Here are the list of custom roles\n\n",
                color=color.green,
            )

            for name, value in customrole_cache.items():

                role = ctx.guild.get_role(value.get("role_id"))

                if not role:

                    await storage.custom_roles.delete(guild_id=ctx.guild.id, name=name)

                    continue

                embed.description += f"**`{name}` - {role.mention}**\n"

            embed.set_footer(
                text=f"REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @customrole.command(
        name="setreqrole",
        help="Set a Required Role for Custom Role Commands",
        aliases=["setrequiredrole"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=80, type=commands.BucketType.guild)
    async def customrole_setreqrole(self, ctx: commands.Context, role: discord.Role):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            customrole_cache_permissions = cache.custom_roles_permissions.get(
                str(ctx.guild.id), {}
            )

            if customrole_cache_permissions:

                await storage.custom_roles_permissions.update(
                    id=customrole_cache_permissions.get("id"),
                    guild_id=ctx.guild.id,
                    required_role_id=role.id,
                )

            else:

                await storage.custom_roles_permissions.insert(
                    guild_id=ctx.guild.id, required_role_id=role.id
                )

            await ctx.send(
                embed=discord.Embed(
                    description=f"**Required Role for Custom Role Commands has been set to {role.mention}**",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @customrole.command(
        name="reqrole",
        help="Show the Required Role for Custom Role Commands",
        aliases=["requiredrole"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def customrole_reqrole(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            customrole_cache_permissions = cache.custom_roles_permissions.get(
                str(ctx.guild.id), {}
            )

            if not customrole_cache_permissions:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"No Required Role has been setup", color=color.red
                    )
                )

            role = ctx.guild.get_role(
                customrole_cache_permissions.get("required_role_id")
            )

            if not role:

                await storage.custom_roles_permissions.delete(guild_id=ctx.guild.id)

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"Required Role has been deleted as it no longer exists",
                        color=color.red,
                    )
                )

            await ctx.send(
                embed=discord.Embed(
                    description=f"**Required Role for Custom Role Commands is {role.mention}**",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_group(
        name="autoresponder",
        help="Setup the Auto Responder Commands",
        aliases=["autoresponders", "ar"],
        with_app_command=True,
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def autoresponder(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="Set Auto Responder Commands",
                description=f"Here are the list of commands\n\n",
                color=color.green,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}**\n"

            else:

                embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command.name}` - {ctx.command.help}**\n"

            embed.set_footer(
                text=f"REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @autoresponder.command(
        name="create",
        help="Add an Auto Responder Command",
        aliases=["add", "new"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def autoresponder_add(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            auto_responder_cache = cache.auto_responder.get(str(ctx.guild.id), {})

            guilds_subscription = cache.guilds.get(str(ctx.guild.id), {}).get(
                "subscription", "free"
            )

            if guilds_subscription == "free":

                auto_responder_limit = 5

            elif guilds_subscription == "silver_guild_preminum":

                auto_responder_limit = 10

            elif guilds_subscription == "golden_guild_premium":

                auto_responder_limit = 15

            elif guilds_subscription == "diamond_guild_premium":

                auto_responder_limit = 20

            else:

                auto_responder_limit = 5

            if len(auto_responder_cache) >= auto_responder_limit:

                return await ctx.send(
                    f"Your guild has reached the limit of {auto_responder_limit} auto responders"
                )

            embed = discord.Embed(
                title="Create Auto Responder",
                description="Please enter the **Create** Button to create an Auto Responder",
                color=color.green,
            )

            closed = False

            view = discord.ui.View(timeout=120)

            create_button = discord.ui.Button(
                label="Create",
                style=discord.ButtonStyle.green,
                emoji=self.bot.emoji.CREATE,
            )

            create_button.callback = lambda i: create_button_callback(i)

            view.add_item(create_button)

            async def create_button_callback(interaction: discord.Interaction):

                if interaction.user.id != ctx.author.id:

                    return await interaction.response.send_message(
                        embed=discord.Embed(
                            description="You cannot interact with this button",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

                class create_auto_responder(
                    discord.ui.Modal, title="Create Auto Responder"
                ):

                    keyword_field = discord.ui.TextInput(
                        label="Keyword",
                        placeholder="Enter the Keyword",
                        required=True,
                        style=discord.TextStyle.short,
                    )

                    response_field = discord.ui.TextInput(
                        label="Response",
                        placeholder="Enter the Response",
                        required=True,
                        style=discord.TextStyle.long,
                    )

                    bot = self.bot

                    async def on_submit(self, interaction: discord.Interaction):

                        try:

                            keyword = self.keyword_field.value

                            response = self.response_field.value

                            await interaction.response.edit_message(
                                embed=discord.Embed(
                                    description=f"{self.bot.emoji.LOADING} Creating Auto Responder...",
                                    color=color.orange,
                                ),
                                view=None,
                            )

                            auto_responder_cache = cache.auto_responder.get(
                                str(ctx.guild.id), {}
                            )

                            guilds_subscription = cache.guilds.get(
                                str(ctx.guild.id), {}
                            ).get("subscription", "free")

                            if guilds_subscription == "free":

                                auto_responder_limit = 5

                            elif guilds_subscription == "silver_guild_preminum":

                                auto_responder_limit = 10

                            elif guilds_subscription == "golden_guild_premium":

                                auto_responder_limit = 15

                            elif guilds_subscription == "diamond_guild_premium":

                                auto_responder_limit = 20

                            else:

                                auto_responder_limit = 5

                            if len(auto_responder_cache) >= auto_responder_limit:

                                return await interaction.edit_original_response(
                                    embed=discord.Embed(
                                        description=f"Your guild has reached the limit of {auto_responder_limit} auto responders",
                                        color=color.red,
                                    ),
                                    view=None,
                                )

                            if keyword.lower() in auto_responder_cache:

                                return await interaction.edit_original_response(
                                    embed=discord.Embed(
                                        description=f"Auto Responder with the keyword {keyword} already exists",
                                        color=color.red,
                                    ),
                                    view=None,
                                )

                            await storage.auto_responder.insert(
                                guild_id=ctx.guild.id,
                                keyword=keyword.lower(),
                                response=response,
                            )

                            nonlocal closed

                            closed = True

                            await interaction.edit_original_response(
                                embed=discord.Embed(
                                    description=f"Auto Responder with the keyword {keyword} has been created",
                                    color=color.green,
                                ),
                                view=None,
                            )

                        except Exception as e:

                            logger.error(
                                f"Error in file {__file__}: {traceback.format_exc()}"
                            )

                await interaction.response.send_modal(create_auto_responder())

            message = await ctx.send(embed=embed, view=view)

            await asyncio.sleep(120)

            if not closed:

                for item in view.children:

                    item.disabled = True

                await message.edit(embed=embed, view=view)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @autoresponder.command(
        name="remove",
        help="Remove an Auto Responder Command",
        aliases=["delete", "del"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def autoresponder_remove(self, ctx: commands.Context, *, keyword: str):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            keyword = keyword.lower()

            auto_responder_cache = cache.auto_responder.get(str(ctx.guild.id), {})

            if not auto_responder_cache.get(keyword):

                return await ctx.send(
                    f"Auto Responder with the keyword {keyword} does not exist"
                )

            await storage.auto_responder.delete(guild_id=ctx.guild.id, keyword=keyword)

            await ctx.send(
                embed=discord.Embed(
                    description=f"**Auto Responder with the keyword `{keyword}` has been removed**",
                    color=color.green,
                )
            )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @autoresponder.command(
        name="update",
        help="Update an Auto Responder Command",
        aliases=["edit"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def autoresponder_update(self, ctx: commands.Context, *, keyword: str):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            keyword = keyword.lower()

            auto_responder_cache = cache.auto_responder.get(str(ctx.guild.id), {})

            if not auto_responder_cache.get(keyword):

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"Auto Responder with the keyword {keyword} does not exist",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            closed = False

            view = discord.ui.View(timeout=120)

            embed = discord.Embed(
                title="Update Auto Responder", description="", color=color.green
            )

            embed.set_thumbnail(
                url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                )
            )

            embed.set_footer(
                text=f"REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            embed.description += (
                f"**__Keyword:__**\n{auto_responder_cache[keyword].get('keyword')}\n\n"
            )

            embed.description += f"**__Response:__**\n{auto_responder_cache[keyword].get('response')}\n\n"

            update_button = discord.ui.Button(
                label="Update",
                style=discord.ButtonStyle.green,
                emoji=self.bot.emoji.UPDATE,
            )

            update_button.callback = lambda i: update_button_callback(i)

            view.add_item(update_button)

            async def update_button_callback(interaction: discord.Interaction):

                if interaction.user.id != ctx.author.id:

                    return await interaction.response.send_message(
                        embed=discord.Embed(
                            description="You cannot interact with this button",
                            color=color.red,
                        ),
                        ephemeral=True,
                        delete_after=10,
                    )

                auto_responder_cache = cache.auto_responder.get(str(ctx.guild.id), {})

                class update_auto_responder(
                    discord.ui.Modal, title="Update Auto Responder"
                ):

                    response_field = discord.ui.TextInput(
                        label="Response",
                        placeholder="Enter the Response",
                        required=True,
                        style=discord.TextStyle.long,
                        default=auto_responder_cache[keyword].get("response") or "",
                    )

                    bot = self.bot

                    async def on_submit(self, interaction: discord.Interaction):

                        try:

                            response = self.response_field.value

                            await interaction.response.edit_message(
                                embed=discord.Embed(
                                    description=f"{self.bot.emoji.LOADING} Updating Auto Responder...",
                                    color=color.orange,
                                ),
                                view=None,
                            )

                            auto_responder_cache = cache.auto_responder.get(
                                str(ctx.guild.id), {}
                            )

                            guilds_subscription = cache.guilds.get(
                                str(ctx.guild.id), {}
                            ).get("subscription", "free")

                            if guilds_subscription == "free":

                                auto_responder_limit = 5

                            elif guilds_subscription == "silver_guild_preminum":

                                auto_responder_limit = 10

                            elif guilds_subscription == "golden_guild_premium":

                                auto_responder_limit = 15

                            elif guilds_subscription == "diamond_guild_premium":

                                auto_responder_limit = 20

                            else:

                                auto_responder_limit = 5

                            if len(auto_responder_cache) >= auto_responder_limit:

                                return await interaction.edit_original_response(
                                    embed=discord.Embed(
                                        description=f"Your guild has reached the limit of {auto_responder_limit} auto responders",
                                        color=color.red,
                                    ),
                                    view=None,
                                )

                            if (
                                keyword.lower() in auto_responder_cache
                                and keyword.lower()
                                != auto_responder_cache[keyword].get("keyword")
                            ):

                                return await interaction.edit_original_response(
                                    embed=discord.Embed(
                                        description=f"Auto Responder with the keyword {keyword} already exists",
                                        color=color.red,
                                    ),
                                    view=None,
                                )

                            await storage.auto_responder.update(
                                id=auto_responder_cache[keyword].get("id"),
                                guild_id=ctx.guild.id,
                                response=response,
                            )

                            nonlocal closed

                            closed = True

                            await interaction.edit_original_response(
                                embed=discord.Embed(
                                    description=f"Auto Responder with the keyword {keyword} has been updated",
                                    color=color.green,
                                ),
                                view=None,
                            )

                        except Exception as e:

                            logger.error(
                                f"Error in file {__file__}: {traceback.format_exc()}"
                            )

                await interaction.response.send_modal(update_auto_responder())

            message = await ctx.send(embed=embed, view=view)

            await asyncio.sleep(120)

            if not closed:

                for item in view.children:

                    item.disabled = True

                await message.edit(embed=embed, view=view)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @autoresponder.command(
        name="list",
        help="List all Auto Responder Commands",
        aliases=["all"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def autoresponder_list(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            auto_responder_cache = cache.auto_responder.get(str(ctx.guild.id), {})

            if not auto_responder_cache:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"No Auto Responders have been setup",
                        color=color.red,
                    )
                )

            view_timeout = 120

            canceled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 120

            # 1 keyword per page

            current_page_index = 0

            async def get_page_embed():

                nonlocal current_page_index

                auto_responder_cache = cache.auto_responder.get(str(ctx.guild.id), {})

                if not auto_responder_cache:

                    return discord.Embed(
                        description=f"No Auto Responders have been setup",
                        color=color.red,
                    )

                if current_page_index >= len(auto_responder_cache):

                    current_page_index = 0

                auto_responder = list(auto_responder_cache.keys())[current_page_index]

                auto_responder_data = auto_responder_cache[auto_responder]

                embed = discord.Embed(title=f"Auto Responders List", color=color.green)

                embed.set_thumbnail(
                    url=(
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    )
                )

                embed.description = (
                    f"**__Keyword:__**\n{auto_responder_data.get('keyword')}\n\n"
                )

                embed.description += (
                    f"**__Response:__**\n{auto_responder_data.get('response')}\n\n"
                )

                embed.description += f"**__Created At:__**\n<t:{int(auto_responder_data.get('created_at').timestamp())}:F>"

                embed.set_footer(
                    text=f"Page {current_page_index+1}/{len(auto_responder_cache)}",
                    icon_url=self.bot.user.display_avatar.url,
                )

                return embed

            async def get_view(disabled: bool = False):

                view = discord.ui.View(timeout=120)

                reset_view_timeout()

                options = []

                auto_responder_cache = cache.auto_responder.get(str(ctx.guild.id), {})

                i = 0

                for auto_responder in auto_responder_cache:

                    options.append(
                        discord.SelectOption(
                            label=auto_responder_cache[auto_responder]
                            .get("keyword")
                            .capitalize(),
                            value=i,
                            default=i == current_page_index,
                        )
                    )

                    i += 1

                if options:

                    page_selector = discord.ui.Select(
                        placeholder="Select a Page",
                        options=options,
                        min_values=1,
                        max_values=1,
                    )

                    page_selector.callback = lambda i: page_selector_callback(i)

                    view.add_item(page_selector)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def page_selector_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You cannot interact with this button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index = int(interaction.data.get("values")[0])

                    await interaction.response.edit_message(
                        embed=await get_page_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            message = await ctx.send(
                embed=await get_page_embed(), view=await get_view()
            )

            while not canceled:

                try:

                    view_timeout -= 1

                    if view_timeout <= 0:

                        await message.edit(
                            embed=await get_page_embed(), view=await get_view(True)
                        )

                        break

                    await asyncio.sleep(1)

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(name="redeem", help="Claim Redeem Code")
    @checks.ignore_check()
    @checks.blacklist_check()
    async def redeem(self, ctx: commands.Context):

        try:

            if ctx.interaction:

                await ctx.defer()

            embed = discord.Embed(title="Please Enter Redeem Code", color=color.gray)

            embed.set_footer(text="You can get redeem code from our support server")

            timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal timeout_time

                timeout_time = timeout

            view = discord.ui.View(timeout=70)

            enter_code = discord.ui.Button(
                label="Enter Redeem Code",
                style=discord.ButtonStyle.primary,
                emoji=self.bot.emoji.REDEEM,
            )

            enter_code.callback = lambda i: enter_code_callback(i)

            view.add_item(enter_code)

            async def enter_code_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't use this button", color=color.red
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                        return

                    reset_timeout_time()

                    self_bot = self.bot

                    class enter_code_modal(discord.ui.Modal, title="Enter Redeem Code"):

                        redeem_code = discord.ui.TextInput(
                            label="Redeem Code",
                            placeholder="Enter Your Redeem Code",
                            min_length=10,
                            max_length=30,
                            required=True,
                            style=discord.TextStyle.short,
                        )

                        async def on_submit(self, interaction: discord.Interaction):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You can't use this button",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                    return

                                reset_timeout_time()

                                redeem_code = self.redeem_code.value

                                if not cache.redeem_codes.get(redeem_code, {}):

                                    await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="Invalid Redeem Code",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                    return

                                if (
                                    cache.redeem_codes.get(redeem_code, {}).get(
                                        "claimed"
                                    )
                                    == True
                                ):

                                    await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="Redeem Code Already Claimed",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                    return

                                if cache.redeem_codes.get(redeem_code, {}).get(
                                    "expires_at"
                                ):

                                    localized = (
                                        cache.redeem_codes.get(redeem_code, {})
                                        .get("expires_at")
                                        .replace(tzinfo=None)
                                    )

                                    if datetime.datetime.now() > localized:

                                        await interaction.response.send_message(
                                            embed=discord.Embed(
                                                description=f"Redeem Code Expired at <t:{int(cache.redeem_codes.get(redeem_code,{}).get('expires_at').timestamp())}:F>",
                                                color=color.red,
                                            ),
                                            ephemeral=True,
                                            delete_after=30,
                                        )

                                await interaction.response.defer()

                                async def get_embed():

                                    redeem_code_data = cache.redeem_codes.get(
                                        redeem_code, {}
                                    )

                                    redeem_code_data_code_type = redeem_code_data.get(
                                        "code_type"
                                    )

                                    redeem_code_data_code_value = redeem_code_data.get(
                                        "code_value"
                                    )

                                    redeem_code_data_valid_for_days = (
                                        redeem_code_data.get("valid_for_days")
                                    )

                                    redeem_code_data_expires_at = redeem_code_data.get(
                                        "expires_at"
                                    )

                                    redeem_code_data_claimed = redeem_code_data.get(
                                        "claimed"
                                    )

                                    redeem_code_data_claimed_by = redeem_code_data.get(
                                        "claimed_by"
                                    )

                                    redeem_code_data_claimed_at = redeem_code_data.get(
                                        "claimed_at"
                                    )

                                    redeem_code_data_created_at = redeem_code_data.get(
                                        "created_at"
                                    )

                                    embed = discord.Embed(
                                        title="Redeem Code Details",
                                        color=(
                                            color.green
                                            if not redeem_code_data_claimed
                                            else color.red
                                        ),
                                    )

                                    embed.description = (
                                        f"Redeem Code: ||`{redeem_code}`||"
                                    )

                                    embed.description += (
                                        f"\nCode Type: `{redeem_code_data_code_type.capitalize()}`"
                                        if redeem_code_data_code_type
                                        else "\nCode Type: `None`"
                                    )

                                    embed.description += f"\nCode Value: `{redeem_code_types.get(redeem_code_data_code_value,'None')}`"

                                    embed.description += f"\nCode Valid For: `{redeem_code_data_valid_for_days} Days`"

                                    embed.description += (
                                        f"\nCode Expires At: <t:{int(redeem_code_data_expires_at.timestamp())}:F>"
                                        if redeem_code_data_expires_at
                                        else "\nCode Expires At: `Never`"
                                    )

                                    embed.description += (
                                        f"\nCode Claimed: `{redeem_code_data_claimed}`"
                                    )

                                    embed.description += (
                                        f"\nCode Claimed By: <@{redeem_code_data_claimed_by}>"
                                        if redeem_code_data_claimed_by
                                        else "\nCode Claimed By: `None`"
                                    )

                                    embed.description += (
                                        f"\nCode Claimed At: <t:{int(redeem_code_data_claimed_at.timestamp())}:F>"
                                        if redeem_code_data_claimed_at
                                        else "\nCode Claimed At: `None`"
                                    )

                                    embed.description += f"\nCode Created At: <t:{int(redeem_code_data_created_at.timestamp())}:F>"

                                    embed.set_footer(
                                        text="Do you want to claim this code?"
                                    )

                                    embed.set_thumbnail(
                                        url=self_bot.user.display_avatar.url
                                    )

                                    return embed

                                async def get_view(disabled: bool = False):

                                    view = discord.ui.View()

                                    claim_button = discord.ui.Button(
                                        label="Claim",
                                        style=discord.ButtonStyle.success,
                                        emoji=self_bot.emoji.SUCCESS,
                                        disabled=disabled,
                                    )

                                    claim_button.callback = (
                                        lambda i: claim_button_callback(i)
                                    )

                                    view.add_item(claim_button)

                                    cancel_button = discord.ui.Button(
                                        label="Cancel",
                                        emoji=self_bot.emoji.CANCLED,
                                        style=discord.ButtonStyle.gray,
                                    )

                                    cancel_button.callback = (
                                        lambda i: cancel_button_callback(i)
                                    )

                                    view.add_item(cancel_button)

                                    if disabled:

                                        for item in view.children:

                                            item.disabled = True

                                    return view

                                async def cancel_button_callback(
                                    interaction: discord.Interaction,
                                ):

                                    try:

                                        if interaction.user.id != ctx.author.id:

                                            await interaction.response.send_message(
                                                embed=discord.Embed(
                                                    description="You can't use this button",
                                                    color=color.red,
                                                ),
                                                ephemeral=True,
                                                delete_after=5,
                                            )

                                            return

                                        nonlocal cancled

                                        cancled = True

                                        await interaction.response.edit_message(
                                            view=await get_view(disabled=True)
                                        )

                                    except Exception as e:

                                        logger.error(
                                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                        )

                                async def claim_button_callback(
                                    interaction: discord.Interaction,
                                ):

                                    try:

                                        if interaction.user.id != ctx.author.id:

                                            await interaction.response.send_message(
                                                embed=discord.Embed(
                                                    description="You can't use this button",
                                                    color=color.red,
                                                ),
                                                ephemeral=True,
                                                delete_after=5,
                                            )

                                            return

                                        await interaction.response.edit_message(
                                            view=None,
                                            embed=discord.Embed(
                                                description=f"{self_bot.emoji.LOADING} Claiming Redeem Code...",
                                                color=color.gray,
                                            ),
                                        )

                                        nonlocal cancled

                                        cancled = True

                                        redeem_code_data = cache.redeem_codes.get(
                                            redeem_code, {}
                                        )

                                        if "guild" in redeem_code_data.get(
                                            "code_value"
                                        ):

                                            await change_guild_subscription(
                                                bot=self_bot,
                                                guild_id=ctx.guild.id,
                                                subscription=redeem_code_data.get(
                                                    "code_value"
                                                ),
                                                valid_for_days=redeem_code_data.get(
                                                    "valid_for_days", None
                                                ),
                                            )

                                        elif "user" in redeem_code_data.get(
                                            "code_value"
                                        ):

                                            await change_user_subscription(
                                                bot=self_bot,
                                                user_id=ctx.author.id,
                                                subscription=redeem_code_data.get(
                                                    "code_value"
                                                ),
                                                valid_for_days=redeem_code_data.get(
                                                    "valid_for_days", None
                                                ),
                                            )

                                        else:

                                            await interaction.edit_original_response(
                                                embed=discord.Embed(
                                                    description="Invalid Redeem Code Value",
                                                    color=color.red,
                                                )
                                            )

                                            return

                                        await storage.redeem_codes.update(
                                            id=redeem_code_data.get("id"),
                                            claimed=True,
                                            claimed_by=ctx.author.id,
                                            claimed_at=datetime.datetime.now(),
                                        )

                                        await interaction.edit_original_response(
                                            embed=discord.Embed(
                                                description=f"{self_bot.emoji.SUCCESS} Redeem Code Claimed Successfully",
                                                color=color.green,
                                            )
                                        )

                                    except Exception as e:

                                        logger.error(
                                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                        )

                                embed = await get_embed()

                                view = await get_view()

                                message = await interaction.followup.send(
                                    embed=embed, view=view, ephemeral=True
                                )

                                await interaction.message.delete()

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                )

                    await interaction.response.send_modal(enter_code_modal())

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=embed, view=view)

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(
                        view=None, content="You took too long to respond"
                    )

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def JoinToCreateVC_Module(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            waiting_embed = discord.Embed(
                title=f"{self.bot.emoji.J2C} - Join To Create VC Module",
                description="Please wait while we fetch the settings...",
                color=color.black,
            )

            waiting_embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            waiting_embed.set_thumbnail(
                url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                )
            )

            message = await ctx.send(embed=waiting_embed)

            guild_id = ctx.guild.id

            cache_data = cache.guilds.get(str(guild_id))

            if not cache_data:

                waiting_embed.description = f"Guild not found in storage.\nPlease wait while we add the guild to storage {self.bot.emoji.LOADING}"

                try:

                    await guilds_db.insert(guild_id=guild_id)

                    cache_data = cache.guilds.get(str(guild_id))

                    try:

                        await message.edit(embed=waiting_embed)

                    except:

                        pass

                except Exception as e:

                    logger.error(f"Error while adding guild to storage.\nError: {e}")

                    waiting_embed.description = f"An error occured while adding the guild to storage. Please contact our support team."

                    view = discord.ui.View()

                    view.add_item(
                        discord.ui.Button(
                            label="Support Server",
                            url=self.bot.urls.SUPPORT_SERVER,
                            style=discord.ButtonStyle.link,
                        )
                    )

                    await message.edit(embed=waiting_embed, view=view)

                    return

                await asyncio.sleep(1)

            cache_j2c_settings = cache.j2c_settings.get(str(guild_id))

            if not cache_j2c_settings:

                waiting_embed.description = f"Settings not found in storage.\nPlease wait while we fetch the settings {self.bot.emoji.LOADING}"

                try:

                    await j2c_settings_db.insert(guild_id=guild_id)

                    cache_j2c_settings = cache.j2c_settings.get(str(guild_id))

                    try:

                        await message.edit(embed=waiting_embed)

                    except:

                        pass

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

                    waiting_embed.description = f"An error occured while adding the settings to storage. Please contact our support team."

                    view = discord.ui.View()

                    view.add_item(
                        discord.ui.Button(
                            label="Support Server",
                            url=self.bot.urls.SUPPORT_SERVER,
                            style=discord.ButtonStyle.link,
                        )
                    )

                    await message.edit(embed=waiting_embed, view=view)

                    return

                await asyncio.sleep(1)

            async def get_embed():

                cache_j2c_settings = cache.j2c_settings.get(str(guild_id))

                embed = waiting_embed

                embed.description = None

                embed.color = (
                    color.green if cache_j2c_settings.get("enabled") else color.red
                )

                # remove old fields

                embed.clear_fields()

                embed.add_field(
                    name="Guild ID",
                    value=f"`{cache_j2c_settings.get('guild_id')}`",
                    inline=True,
                )

                embed.add_field(
                    name="Enabled",
                    value=(
                        self.bot.emoji.ENABLED
                        if cache_j2c_settings.get("enabled")
                        else self.bot.emoji.DISABLED
                    ),
                    inline=True,
                )

                embed.add_field(name="", value="", inline=False)

                vc_channel_id = cache_j2c_settings.get("create_vc_channel_id")

                vc_category_id = cache_j2c_settings.get("create_vc_category_id")

                vc_channel_text = f"<#{vc_channel_id}>" if vc_channel_id else "Not Set"

                vc_category_text = (
                    f"<#{vc_category_id}>" if vc_category_id else "Not Set"
                )

                embed.add_field(
                    name=f"VC Channel {self.bot.emoji.MICROPHONE}",
                    value=f"**__Channel:__** {vc_channel_text}\n**__ID:__** `{vc_channel_id}`",
                    inline=True,
                )

                embed.add_field(
                    name=f"Category {self.bot.emoji.CATEGORY}",
                    value=f"**__Category:__** {vc_category_text}\n**__ID:__** `{vc_category_id}`",
                    inline=True,
                )

                embed.add_field(name="", value="", inline=False)

                embed.set_footer(
                    text=f"Setting of Join To Create VC",
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

                return embed

            timeout_time = 120

            cancled = False

            def reset_timeout_time(timeout: int = 120):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled: bool = False):

                cache_j2c_settings = cache.j2c_settings.get(str(guild_id))

                reset_timeout_time()

                view = discord.ui.View(timeout=130)

                enabled_toggle_button = discord.ui.Button(
                    label=(
                        "Click to Enable"
                        if not cache_j2c_settings.get("enabled")
                        else "Click to Disable"
                    ),
                    style=(
                        discord.ButtonStyle.success
                        if not cache_j2c_settings.get("enabled")
                        else discord.ButtonStyle.gray
                    ),
                    emoji=(
                        self.bot.emoji.ENABLED
                        if not cache_j2c_settings.get("enabled")
                        else self.bot.emoji.DISABLED
                    ),
                    row=1,
                )

                enabled_toggle_button.callback = (
                    lambda i: enabled_toggle_button_callback(i)
                )

                view.add_item(enabled_toggle_button)

                cancle_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.CANCLED,
                    row=1,
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(cancle_button)

                default_j2c_vc_channel = []

                if cache_j2c_settings.get("create_vc_channel_id"):

                    channel = self.bot.get_channel(
                        cache_j2c_settings.get("create_vc_channel_id")
                    )

                    if channel:

                        if isinstance(channel, discord.VoiceChannel):

                            default_j2c_vc_channel.append(channel)

                j2c_vc_channel_select = discord.ui.ChannelSelect(
                    placeholder="Select a VC Channel",
                    min_values=0,
                    max_values=1,
                    row=2,
                    disabled=not cache_j2c_settings.get("enabled"),
                    channel_types=[discord.ChannelType.voice],
                    default_values=default_j2c_vc_channel,
                )

                j2c_vc_channel_select.callback = (
                    lambda i: j2c_vc_channel_select_callback(i)
                )

                view.add_item(j2c_vc_channel_select)

                default_j2c_category = []

                if cache_j2c_settings.get("create_vc_category_id"):

                    category = self.bot.get_channel(
                        cache_j2c_settings.get("create_vc_category_id")
                    )

                    if category:

                        if isinstance(category, discord.CategoryChannel):

                            default_j2c_category.append(category)

                j2c_category_select = discord.ui.ChannelSelect(
                    placeholder="Select a Category",
                    min_values=0,
                    max_values=1,
                    row=3,
                    disabled=not cache_j2c_settings.get("enabled"),
                    channel_types=[discord.ChannelType.category],
                    default_values=default_j2c_category,
                )

                j2c_category_select.callback = lambda i: j2c_category_select_callback(i)

                view.add_item(j2c_category_select)

                if disabled:

                    # Disable all the buttons

                    for item in view.children:

                        item.disabled = True

                return view

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    nonlocal cancled

                    cancled = True

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view(True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def j2c_vc_channel_select_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    cache_j2c_settings = cache.j2c_settings.get(str(guild_id))

                    await j2c_settings_db.update(
                        id=cache_j2c_settings.get("id"),
                        create_vc_channel_id=(
                            interaction.data.get("values")[0]
                            if interaction.data.get("values")
                            else ""
                        ),
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def j2c_category_select_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    cache_j2c_settings = cache.j2c_settings.get(str(guild_id))

                    await j2c_settings_db.update(
                        id=cache_j2c_settings.get("id"),
                        create_vc_category_id=(
                            interaction.data.get("values")[0]
                            if interaction.data.get("values")
                            else ""
                        ),
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def enabled_toggle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    cache_j2c_settings = cache.j2c_settings.get(str(guild_id))

                    await j2c_settings_db.update(
                        id=cache_j2c_settings.get("id"),
                        enabled=not cache_j2c_settings.get("enabled", False),
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            embed = await get_embed()

            view = await get_view()

            await message.edit(embed=embed, view=view)

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(embed=embed, view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def AutoMod_Module(self, ctx: commands.Context):

        try:

            command = self.bot.get_command("automod")

            embed = discord.Embed(
                title="AutoMod",
                description=f"Please use `{self.bot.BotConfig.PREFIX}{command.name}`",
                color=color.black,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def Ticket_Module(self, ctx: commands.Context):

        try:

            ticket_cog = self.bot.get_command("ticket").cog

            await ticket_cog.ticket_setup(ctx)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def AntiNuke_Module(self, ctx: commands.Context):

        if not await checks.check_is_owner(ctx, notify=True):

            return

        antinuke_options = {
            "anti_channel_settings": {
                "name": "AntiNuke Channel",
                "emoji": self.bot.emoji.CHANNEL,
                "description": "Block the channel create, delete, update event",
                "options": {
                    "anti_channel_create": {
                        "name": "Anti Channel Create",
                        "emoji": self.bot.emoji.CREATE,
                        "description": "Block the channel create event",
                    },
                    "anti_channel_delete": {
                        "name": "Anti Channel Delete",
                        "emoji": self.bot.emoji.DELETE,
                        "description": "Block the channel delete event",
                    },
                    "anti_channel_update": {
                        "name": "Anti Channel Update",
                        "emoji": self.bot.emoji.UPDATE,
                        "description": "Block the channel update event",
                    },
                },
            },
            "anti_role_settings": {
                "name": "AntiNuke Role",
                "emoji": self.bot.emoji.ROLE,
                "description": "Block the role create, delete, update event",
                "options": {
                    "anti_role_create": {
                        "name": "Anti Role Create",
                        "emoji": self.bot.emoji.CREATE,
                        "description": "Block the role create event",
                    },
                    "anti_role_delete": {
                        "name": "Anti Role Delete",
                        "emoji": self.bot.emoji.DELETE,
                        "description": "Block the role delete event",
                    },
                    "anti_role_update": {
                        "name": "Anti Role Update",
                        "emoji": self.bot.emoji.UPDATE,
                        "description": "Block the role update event",
                    },
                },
            },
            "anti_member_settings": {
                "name": "AntiNuke Member",
                "emoji": self.bot.emoji.MEMBER,
                "description": "Block the member ban, unban, kick, update event",
                "options": {
                    "anti_member_ban": {
                        "name": "Anti Member Ban",
                        "emoji": self.bot.emoji.BAN,
                        "description": "Block the member ban event",
                    },
                    "anti_member_unban": {
                        "name": "Anti Member Unban",
                        "emoji": self.bot.emoji.UNBAN,
                        "description": "Block the member unban event",
                    },
                    "anti_member_kick": {
                        "name": "Anti Member Kick",
                        "emoji": self.bot.emoji.KICK,
                        "description": "Block the member kick event",
                    },
                    "anti_member_update": {
                        "name": "Anti Member Update",
                        "emoji": self.bot.emoji.UPDATE,
                        "description": "Block the member update event",
                    },
                },
            },
            "anti_bot_settings": {
                "name": "AntiNuke Bot",
                "emoji": self.bot.emoji.ROBOT,
                "description": "Block the bot add event",
                "options": {
                    "anti_bot_add": {
                        "name": "Anti Bot Add",
                        "emoji": self.bot.emoji.ROBOT,
                        "description": "Block the bot add event",
                    }
                },
            },
            "anti_invite_settings": {
                "name": "AntiNuke Invite",
                "emoji": self.bot.emoji.INVITE,
                "description": "Block the invite delete event",
                "options": {
                    "anti_invite_delete": {
                        "name": "Anti Invite Delete",
                        "emoji": self.bot.emoji.DELETE,
                        "description": "Block the invite delete event",
                    }
                },
            },
            "anti_webhook_settings": {
                "name": "AntiNuke Webhook",
                "emoji": self.bot.emoji.WEBHOOK,
                "description": "Block the webhook create, update event",
                "options": {
                    "anti_webhook_create": {
                        "name": "Anti Webhook Create",
                        "emoji": self.bot.emoji.CREATE,
                        "description": "Block the webhook create event",
                    },
                    "anti_webhook_update": {
                        "name": "Anti Webhook Update",
                        "emoji": self.bot.emoji.UPDATE,
                        "description": "Block the webhook update event",
                    },
                },
            },
            "anti_server_settings": {
                "name": "AntiNuke Server",
                "emoji": self.bot.emoji.SERVER,
                "description": "Block the server update event",
                "options": {
                    "anti_server_update": {
                        "name": "Anti Server Update",
                        "emoji": self.bot.emoji.UPDATE,
                        "description": "Block the server update event",
                    }
                },
            },
            "anti_emote_settings": {
                "name": "AntiNuke Emoji",
                "emoji": self.bot.emoji.EMOJI,
                "description": "Block the emoji create, delete, update event",
                "options": {
                    "anti_emote_create": {
                        "name": "Anti Emoji Create",
                        "emoji": self.bot.emoji.CREATE,
                        "description": "Block the emoji create event",
                    },
                    "anti_emote_delete": {
                        "name": "Anti Emoji Delete",
                        "emoji": self.bot.emoji.DELETE,
                        "description": "Block the emoji delete event",
                    },
                    "anti_emote_update": {
                        "name": "Anti Emoji Update",
                        "emoji": self.bot.emoji.UPDATE,
                        "description": "Block the emoji update event",
                    },
                },
            },
            "anti_prune_settings": {
                "name": "AntiNuke Prune",
                "emoji": self.bot.emoji.PRUNE,
                "description": "Block the prune member event",
                "options": {
                    "anti_prune_member": {
                        "name": "Anti Prune Member",
                        "emoji": self.bot.emoji.PRUNE,
                        "description": "Block the prune member event",
                    }
                },
            },
            "anti_message_settings": {
                "name": "AntiNuke Message",
                "emoji": self.bot.emoji.MESSAGE,
                "description": "Block the message delete, update, other event",
                "options": {
                    "anti_everyone_mention": {
                        "name": "Anti Everyone Mention",
                        "emoji": self.bot.emoji.EVERYONE,
                        "description": "Block the everyone mention message",
                    },
                },
            },
        }

        try:

            guild_id = ctx.guild.id

            waiting_embed = discord.Embed(
                title=f"{self.bot.emoji.ANTINUKE} - Anti Nuke",
                description="Please wait while we fetch the settings...",
                color=color.black,
            )

            waiting_embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            waiting_embed.set_thumbnail(
                url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                )
            )

            message = await ctx.send(embed=waiting_embed)

            cache_data = cache.guilds.get(str(guild_id))

            if not cache_data:

                waiting_embed.description = f"Guild not found in storage.\nPlease wait while we add the guild to storage {self.bot.emoji.LOADING}"

                try:

                    await guilds_db.insert(guild_id=guild_id)

                    cache_data = cache.guilds.get(str(guild_id))

                    try:

                        await message.edit(embed=waiting_embed)

                    except:

                        pass

                except Exception as e:

                    logger.error(f"Error while adding guild to storage.\nError: {e}")

                    waiting_embed.description = f"An error occured while adding the guild to storage. Please contact our support team."

                    view = discord.ui.View()

                    view.add_item(
                        discord.ui.Button(
                            label="Support Server",
                            url=self.bot.urls.SUPPORT_SERVER,
                            style=discord.ButtonStyle.link,
                        )
                    )

                    await message.edit(embed=waiting_embed, view=view)

                    return

                await asyncio.sleep(1)

            cache_antinuke_settings = cache.antinuke_settings.get(str(guild_id))

            if not cache_antinuke_settings:

                waiting_embed.description = f"Settings not found in storage.\nPlease wait while we fetch the settings {self.bot.emoji.LOADING}"

                try:

                    await antinuke_settings_db.insert(guild_id=guild_id)

                    cache_antinuke_settings = cache.antinuke_settings.get(str(guild_id))

                    try:

                        await message.edit(embed=waiting_embed)

                    except:

                        pass

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

                    waiting_embed.description = f"An error occured while adding the settings to storage. Please contact our support team."

                    view = discord.ui.View()

                    view.add_item(
                        discord.ui.Button(
                            label="Support Server",
                            url=self.bot.urls.SUPPORT_SERVER,
                            style=discord.ButtonStyle.link,
                        )
                    )

                    await message.edit(embed=waiting_embed, view=view)

                    return

                await asyncio.sleep(1)

            async def get_embed():

                try:

                    cache_antinuke_settings = cache.antinuke_settings.get(str(guild_id))

                    embed = waiting_embed

                    embed.description = None

                    embed.color = (
                        color.green
                        if cache_antinuke_settings.get("enabled")
                        else color.red
                    )

                    embed.clear_fields()

                    modules_category_text = ""

                    for key, value in antinuke_options.items():

                        modules_category_text += f"**{self.bot.emoji.ENABLED_BUNDLE if all(cache_antinuke_settings.get(sub_key) for sub_key in value.get('options').keys()) else self.bot.emoji.DISABLED_BUNDLE} {value.get('name')}**\n"

                    embed.description = f"""**__Guild ID:__** `{cache_antinuke_settings.get('guild_id')}`





**__Enabled:__** {self.bot.emoji.ENABLED_BUNDLE if cache_antinuke_settings.get('enabled') else self.bot.emoji.DISABLED_BUNDLE}





**__Settings type:__** `{cache_antinuke_settings.get('type')}`











{modules_category_text}"""

                    embed.set_footer(
                        text=f"Setting of Anti Nuke",
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

                    return embed

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            timeout_time = 120

            cancled = False

            def reset_timeout_time(timeout: int = 120):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled: bool = False):

                try:

                    cache_antinuke_settings = cache.antinuke_settings.get(str(guild_id))

                    reset_timeout_time()

                    view = discord.ui.View(timeout=130)

                    enabled_toggle_button = discord.ui.Button(
                        label=(
                            "Click to Enable"
                            if not cache_antinuke_settings.get("enabled")
                            else "Click to Disable"
                        ),
                        style=(
                            discord.ButtonStyle.success
                            if not cache_antinuke_settings.get("enabled")
                            else discord.ButtonStyle.gray
                        ),
                        emoji=(
                            self.bot.emoji.ENABLED
                            if not cache_antinuke_settings.get("enabled")
                            else self.bot.emoji.DISABLED
                        ),
                        row=0,
                    )

                    enabled_toggle_button.callback = (
                        lambda i: enabled_toggle_button_callback(i)
                    )

                    view.add_item(enabled_toggle_button)

                    enabled_modules_button = discord.ui.Button(
                        label=(
                            "Enable All Modules"
                            if not (
                                cache_antinuke_settings.get("anti_channel_create")
                                and cache_antinuke_settings.get("anti_channel_delete")
                                and cache_antinuke_settings.get("anti_channel_update")
                                and cache_antinuke_settings.get("anti_role_create")
                                and cache_antinuke_settings.get("anti_role_delete")
                                and cache_antinuke_settings.get("anti_role_update")
                                and cache_antinuke_settings.get("anti_member_ban")
                                and cache_antinuke_settings.get("anti_member_unban")
                                and cache_antinuke_settings.get("anti_member_kick")
                                and cache_antinuke_settings.get("anti_member_update")
                                and cache_antinuke_settings.get("anti_bot_add")
                                and cache_antinuke_settings.get("anti_invite_delete")
                                and cache_antinuke_settings.get("anti_webhook_create")
                                and cache_antinuke_settings.get("anti_webhook_update")
                                and cache_antinuke_settings.get("anti_server_update")
                                and cache_antinuke_settings.get("anti_emote_create")
                                and cache_antinuke_settings.get("anti_emote_delete")
                                and cache_antinuke_settings.get("anti_emote_update")
                                and cache_antinuke_settings.get("anti_prune_member")
                                and cache_antinuke_settings.get("anti_everyone_mention")
                            )
                            else "Disable All Modules"
                        ),
                        style=(
                            discord.ButtonStyle.success
                            if not (
                                cache_antinuke_settings.get("anti_channel_create")
                                and cache_antinuke_settings.get("anti_channel_delete")
                                and cache_antinuke_settings.get("anti_channel_update")
                                and cache_antinuke_settings.get("anti_role_create")
                                and cache_antinuke_settings.get("anti_role_delete")
                                and cache_antinuke_settings.get("anti_role_update")
                                and cache_antinuke_settings.get("anti_member_ban")
                                and cache_antinuke_settings.get("anti_member_unban")
                                and cache_antinuke_settings.get("anti_member_kick")
                                and cache_antinuke_settings.get("anti_member_update")
                                and cache_antinuke_settings.get("anti_bot_add")
                                and cache_antinuke_settings.get("anti_invite_delete")
                                and cache_antinuke_settings.get("anti_webhook_create")
                                and cache_antinuke_settings.get("anti_webhook_update")
                                and cache_antinuke_settings.get("anti_server_update")
                                and cache_antinuke_settings.get("anti_emote_create")
                                and cache_antinuke_settings.get("anti_emote_delete")
                                and cache_antinuke_settings.get("anti_emote_update")
                                and cache_antinuke_settings.get("anti_prune_member")
                                and cache_antinuke_settings.get("anti_everyone_mention")
                            )
                            else discord.ButtonStyle.gray
                        ),
                        emoji=(
                            self.bot.emoji.ENABLED
                            if not (
                                cache_antinuke_settings.get("anti_channel_create")
                                and cache_antinuke_settings.get("anti_channel_delete")
                                and cache_antinuke_settings.get("anti_channel_update")
                                and cache_antinuke_settings.get("anti_role_create")
                                and cache_antinuke_settings.get("anti_role_delete")
                                and cache_antinuke_settings.get("anti_role_update")
                                and cache_antinuke_settings.get("anti_member_ban")
                                and cache_antinuke_settings.get("anti_member_unban")
                                and cache_antinuke_settings.get("anti_member_kick")
                                and cache_antinuke_settings.get("anti_member_update")
                                and cache_antinuke_settings.get("anti_bot_add")
                                and cache_antinuke_settings.get("anti_invite_delete")
                                and cache_antinuke_settings.get("anti_webhook_create")
                                and cache_antinuke_settings.get("anti_webhook_update")
                                and cache_antinuke_settings.get("anti_server_update")
                                and cache_antinuke_settings.get("anti_emote_create")
                                and cache_antinuke_settings.get("anti_emote_delete")
                                and cache_antinuke_settings.get("anti_emote_update")
                                and cache_antinuke_settings.get("anti_prune_member")
                                and cache_antinuke_settings.get("anti_everyone_mention")
                            )
                            else self.bot.emoji.DISABLED
                        ),
                        row=0,
                    )

                    enabled_modules_button.callback = (
                        lambda i: enabled_modules_button_callback(i)
                    )

                    view.add_item(enabled_modules_button)

                    select_antinuke_type = discord.ui.Select(
                        placeholder="Select a type",
                        min_values=1,
                        max_values=1,
                        options=[
                            discord.SelectOption(
                                label="Normal",
                                value="normal",
                                description="Default settings",
                                emoji=(
                                    self.bot.emoji.ENABLED
                                    if cache_antinuke_settings.get("type") == "normal"
                                    else self.bot.emoji.DISABLED
                                ),
                                default=cache_antinuke_settings.get("type") == "normal",
                            ),
                            discord.SelectOption(
                                label="Extream",
                                value="extream",
                                description="Extream settings",
                                emoji=(
                                    self.bot.emoji.ENABLED
                                    if cache_antinuke_settings.get("type") == "extream"
                                    else self.bot.emoji.DISABLED
                                ),
                                default=cache_antinuke_settings.get("type")
                                == "extream",
                            ),
                            discord.SelectOption(
                                label="Custom",
                                value="custom",
                                description="Custom settings (Premium Only)",
                                emoji=(
                                    self.bot.emoji.ENABLED
                                    if cache_antinuke_settings.get("type") == "custom"
                                    else self.bot.emoji.DISABLED
                                ),
                                default=cache_antinuke_settings.get("type") == "custom",
                            ),
                        ],
                        row=1,
                        disabled=not cache_antinuke_settings.get("enabled"),
                    )

                    select_antinuke_type.callback = (
                        lambda i: select_antinuke_type_callback(i)
                    )

                    view.add_item(select_antinuke_type)

                    select_module_to_edit = discord.ui.Select(
                        placeholder="Select a module to edit",
                        min_values=1,
                        max_values=1,
                        options=[
                            discord.SelectOption(
                                label=antinuke_options.get(key, {}).get("name"),
                                value=key,
                                description=antinuke_options.get(key, {}).get(
                                    "description"
                                ),
                                emoji=antinuke_options.get(key, {}).get("emoji"),
                                default=cache_antinuke_settings.get(key),
                            )
                            for key in antinuke_options.keys()
                        ],
                        row=2,
                        disabled=not cache_antinuke_settings.get("enabled"),
                    )

                    cache_guilds_data = cache.guilds.get(str(guild_id), {})

                    if cache_guilds_data.get("subscription") == "free":

                        select_module_to_edit.placeholder = (
                            "Upgrade to premium to edit this module"
                        )

                    select_module_to_edit.callback = (
                        lambda i: select_module_to_edit_callback(i)
                    )

                    view.add_item(select_module_to_edit)

                    cancle_button = discord.ui.Button(
                        label="Cancel",
                        style=discord.ButtonStyle.gray,
                        emoji=self.bot.emoji.CANCLED,
                        row=3,
                    )

                    cancle_button.callback = lambda i: cancle_button_callback(i)

                    view.add_item(cancle_button)

                    if disabled:

                        # Disable all the buttons

                        for item in view.children:

                            item.disabled = True

                    return view

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def select_antinuke_type_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    cache_antinuke_settings = cache.antinuke_settings.get(str(guild_id))

                    await antinuke_settings_db.update(
                        id=cache_antinuke_settings.get("id"),
                        type=interaction.data.get("values")[0],
                    )

                    await antinuke_settings_db.change_antinuke_settings_type(
                        cache_antinuke_settings, interaction.data.get("values")[0]
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def enabled_modules_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    cache_antinuke_settings = cache.antinuke_settings.get(str(guild_id))

                    # if any 1 of them is disable enable all

                    enable = not (
                        cache_antinuke_settings.get("anti_channel_create")
                        and cache_antinuke_settings.get("anti_channel_delete")
                        and cache_antinuke_settings.get("anti_channel_update")
                        and cache_antinuke_settings.get("anti_role_create")
                        and cache_antinuke_settings.get("anti_role_delete")
                        and cache_antinuke_settings.get("anti_role_update")
                        and cache_antinuke_settings.get("anti_member_ban")
                        and cache_antinuke_settings.get("anti_member_unban")
                        and cache_antinuke_settings.get("anti_member_kick")
                        and cache_antinuke_settings.get("anti_member_update")
                        and cache_antinuke_settings.get("anti_bot_add")
                        and cache_antinuke_settings.get("anti_invite_delete")
                        and cache_antinuke_settings.get("anti_webhook_create")
                        and cache_antinuke_settings.get("anti_webhook_update")
                        and cache_antinuke_settings.get("anti_server_update")
                        and cache_antinuke_settings.get("anti_emote_create")
                        and cache_antinuke_settings.get("anti_emote_delete")
                        and cache_antinuke_settings.get("anti_emote_update")
                        and cache_antinuke_settings.get("anti_prune_member")
                        and cache_antinuke_settings.get("anti_everyone_mention")
                    )

                    await antinuke_settings_db.update(
                        id=cache_antinuke_settings.get("id"),
                        anti_channel_create=enable,
                        anti_channel_delete=enable,
                        anti_channel_update=enable,
                        anti_role_create=enable,
                        anti_role_delete=enable,
                        anti_role_update=enable,
                        anti_member_ban=enable,
                        anti_member_unban=enable,
                        anti_member_kick=enable,
                        anti_member_update=enable,
                        anti_bot_add=enable,
                        anti_invite_delete=enable,
                        anti_webhook_create=enable,
                        anti_webhook_update=enable,
                        anti_server_update=enable,
                        anti_emote_create=enable,
                        anti_emote_delete=enable,
                        anti_emote_update=enable,
                        anti_prune_member=enable,
                        anti_everyone_mention=enable,
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    nonlocal cancled

                    cancled = True

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view(True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def enabled_toggle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    cache_antinuke_settings = cache.antinuke_settings.get(str(guild_id))

                    await antinuke_settings_db.update(
                        id=cache_antinuke_settings.get("id"),
                        enabled=not cache_antinuke_settings.get("enabled", False),
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def select_module_to_edit_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    selected_category = interaction.data.get("values")[0]

                    async def get_selected_category_embed():

                        try:

                            cache_antinuke_settings = cache.antinuke_settings.get(
                                str(guild_id)
                            )

                            embed = discord.Embed(
                                title=f"{antinuke_options.get(selected_category,{}).get('emoji')} - {antinuke_options.get(selected_category,{}).get('name')}",
                                color=(
                                    color.green
                                    if (
                                        cache_antinuke_settings.get(sub_key)
                                        for sub_key in antinuke_options.get(
                                            selected_category, {}
                                        )
                                        .get("options")
                                        .keys()
                                    )
                                    else color.red
                                ),
                            )

                            embed.color = (
                                color.green
                                if cache_antinuke_settings.get("enabled")
                                else color.red
                            )

                            embed.clear_fields()

                            embed.description = f"""**__Guild ID:__** `{cache_antinuke_settings.get('guild_id')}`





**__Enabled:__** {self.bot.emoji.ENABLED_BUNDLE if cache_antinuke_settings.get('enabled') else self.bot.emoji.DISABLED_BUNDLE}





**__Settings type:__** `{cache_antinuke_settings.get('type')}`





\n"""

                            for key, value in (
                                antinuke_options.get(selected_category, {})
                                .get("options")
                                .items()
                            ):

                                embed.description += f"**{self.bot.emoji.ENABLED_BUNDLE if (cache_antinuke_settings.get(key)) else self.bot.emoji.DISABLED_BUNDLE} {value.get('name')}**\n"

                            embed.set_footer(
                                text=f"Setting of Anti Nuke",
                                icon_url=(
                                    ctx.guild.icon.url
                                    if ctx.guild.icon
                                    else self.bot.user.display_avatar.url
                                ),
                            )

                            # embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)

                            return embed

                        except Exception as e:

                            logger.error(
                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                            )

                            return None

                    async def get_selected_category_view(disabled: bool = False):

                        cache_antinuke_settings = cache.antinuke_settings.get(
                            str(guild_id)
                        )

                        reset_timeout_time()

                        view = discord.ui.View(timeout=130)

                        async def select_a_module_to_edit_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                selected_module = interaction.data.get("values")[0]

                                cache_antinuke_settings = cache.antinuke_settings.get(
                                    str(guild_id)
                                )

                                async def get_selected_module_embed():

                                    cache_antinuke_settings = (
                                        cache.antinuke_settings.get(str(guild_id))
                                    )

                                    selected_mpdule_data = (
                                        antinuke_options.get(selected_category, {})
                                        .get("options")
                                        .get(selected_module, {})
                                    )

                                    embed = discord.Embed(
                                        title=f"{selected_mpdule_data.get('emoji')} - {selected_mpdule_data.get('name')}",
                                        color=(
                                            color.green
                                            if cache_antinuke_settings.get(
                                                selected_module
                                            )
                                            else color.red
                                        ),
                                    )

                                    embed.color = (
                                        color.green
                                        if cache_antinuke_settings.get(selected_module)
                                        else color.red
                                    )

                                    embed.clear_fields()

                                    embed.description = f"""**__Guild ID:__** `{cache_antinuke_settings.get('guild_id')}`





**__Enabled:__** {self.bot.emoji.ENABLED_BUNDLE if cache_antinuke_settings.get('enabled') else self.bot.emoji.DISABLED_BUNDLE}





**__Settings type:__** `{cache_antinuke_settings.get('type')}`





\n"""

                                    selected_limit = cache_antinuke_settings.get(
                                        f"{selected_module}_limit"
                                    )

                                    selected_punishment = cache_antinuke_settings.get(
                                        f"{selected_module}_punishment"
                                    )

                                    embed.description += f"**{selected_mpdule_data.get('name')} Enabled: {self.bot.emoji.ENABLED_BUNDLE if cache_antinuke_settings.get(selected_module) else self.bot.emoji.DISABLED_BUNDLE}**\n"

                                    embed.description += f"**{selected_mpdule_data.get('name')} Limit: `{selected_limit}`**\n"

                                    embed.description += f"**{selected_mpdule_data.get('name')} Punishment: `{selected_punishment}`**\n"

                                    embed.set_footer(
                                        text=f"Setting of {selected_mpdule_data.get('name')}",
                                        icon_url=(
                                            ctx.guild.icon.url
                                            if ctx.guild.icon
                                            else self.bot.user.display_avatar.url
                                        ),
                                    )

                                    # embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)

                                    return embed

                                async def get_selected_module_view(
                                    disabled: bool = False,
                                ):

                                    cache_antinuke_settings = (
                                        cache.antinuke_settings.get(str(guild_id))
                                    )

                                    cache_guilds_data = cache.guilds.get(
                                        str(guild_id), {}
                                    )

                                    reset_timeout_time()

                                    view = discord.ui.View(timeout=130)

                                    async def enabled_toggle_button_callback(
                                        interaction: discord.Interaction,
                                    ):

                                        try:

                                            if interaction.user.id != ctx.author.id:

                                                return await interaction.response.send_message(
                                                    embed=discord.Embed(
                                                        description="You are not allowed to use this Interaction.",
                                                        color=color.red,
                                                    ),
                                                    ephemeral=True,
                                                    delete_after=5,
                                                )

                                            await interaction.response.defer()

                                            cache_antinuke_settings = (
                                                cache.antinuke_settings.get(
                                                    str(guild_id)
                                                )
                                            )

                                            await antinuke_settings_db.update(
                                                **{
                                                    selected_module: not cache_antinuke_settings.get(
                                                        selected_module
                                                    ),
                                                    "id": cache_antinuke_settings.get(
                                                        "id"
                                                    ),
                                                }
                                            )

                                            await interaction.message.edit(
                                                embed=await get_selected_module_embed(),
                                                view=await get_selected_module_view(),
                                            )

                                        except Exception as e:

                                            logger.error(
                                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                            )

                                    enabled_toggle_button = discord.ui.Button(
                                        label=(
                                            f"Click to Enable"
                                            if not cache_antinuke_settings.get(
                                                selected_module
                                            )
                                            else "Click to Disable"
                                        ),
                                        style=(
                                            discord.ButtonStyle.success
                                            if not cache_antinuke_settings.get(
                                                selected_module
                                            )
                                            else discord.ButtonStyle.gray
                                        ),
                                        emoji=(
                                            self.bot.emoji.ENABLED
                                            if not cache_antinuke_settings.get(
                                                selected_module
                                            )
                                            else self.bot.emoji.DISABLED
                                        ),
                                        row=0,
                                    )

                                    enabled_toggle_button.callback = (
                                        lambda i: enabled_toggle_button_callback(i)
                                    )

                                    # 1 - 10

                                    async def limit_selector_callback(
                                        interaction: discord.Interaction,
                                    ):

                                        try:

                                            if interaction.user.id != ctx.author.id:

                                                return await interaction.response.send_message(
                                                    embed=discord.Embed(
                                                        description="You are not allowed to use this Interaction.",
                                                        color=color.red,
                                                    ),
                                                    ephemeral=True,
                                                    delete_after=5,
                                                )

                                            await interaction.response.defer()

                                            cache_antinuke_settings = (
                                                cache.antinuke_settings.get(
                                                    str(guild_id)
                                                )
                                            )

                                            await antinuke_settings_db.update(
                                                **{
                                                    f"{selected_module}_limit": interaction.data.get(
                                                        "values"
                                                    )[
                                                        0
                                                    ],
                                                    "id": cache_antinuke_settings.get(
                                                        "id"
                                                    ),
                                                }
                                            )

                                            await interaction.message.edit(
                                                embed=await get_selected_module_embed(),
                                                view=await get_selected_module_view(),
                                            )

                                        except Exception as e:

                                            logger.error(
                                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                            )

                                    limit_selector = discord.ui.Select(
                                        placeholder="Select a limit",
                                        min_values=1,
                                        max_values=1,
                                        options=[
                                            discord.SelectOption(
                                                label=str(i),
                                                value=str(i),
                                                description=f"Select the limit for {selected_module}",
                                                default=cache_antinuke_settings.get(
                                                    f"{selected_module}_limit"
                                                )
                                                == i,
                                            )
                                            for i in range(1, 11)
                                        ],
                                        row=1,
                                        disabled=not cache_antinuke_settings.get(
                                            selected_module
                                        ),
                                    )

                                    limit_selector.callback = (
                                        lambda i: limit_selector_callback(i)
                                    )

                                    async def select_punishment_callback(
                                        interaction: discord.Interaction,
                                    ):

                                        try:

                                            if interaction.user.id != ctx.author.id:

                                                return await interaction.response.send_message(
                                                    embed=discord.Embed(
                                                        description="You are not allowed to use this Interaction.",
                                                        color=color.red,
                                                    ),
                                                    ephemeral=True,
                                                    delete_after=5,
                                                )

                                            await interaction.response.defer()

                                            cache_antinuke_settings = (
                                                cache.antinuke_settings.get(
                                                    str(guild_id)
                                                )
                                            )

                                            await antinuke_settings_db.update(
                                                **{
                                                    f"{selected_module}_punishment": interaction.data.get(
                                                        "values"
                                                    )[
                                                        0
                                                    ],
                                                    "id": cache_antinuke_settings.get(
                                                        "id"
                                                    ),
                                                }
                                            )

                                            await interaction.message.edit(
                                                embed=await get_selected_module_embed(),
                                                view=await get_selected_module_view(),
                                            )

                                        except Exception as e:

                                            logger.error(
                                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                            )

                                    select_punishment = discord.ui.Select(
                                        placeholder="Select a punishment",
                                        min_values=1,
                                        max_values=1,
                                        options=[
                                            discord.SelectOption(
                                                label=punishment,
                                                value=punishment.lower(),
                                                default=str(
                                                    cache_antinuke_settings.get(
                                                        f"{selected_module}_punishment"
                                                    )
                                                ).lower()
                                                == punishment.lower(),
                                            )
                                            for punishment in punishments
                                        ],
                                        row=2,
                                        disabled=not cache_antinuke_settings.get(
                                            selected_module
                                        ),
                                    )

                                    select_punishment.callback = (
                                        lambda i: select_punishment_callback(i)
                                    )

                                    async def cancle_button_callback(
                                        interaction: discord.Interaction,
                                    ):

                                        try:

                                            if interaction.user.id != ctx.author.id:

                                                return await interaction.response.send_message(
                                                    embed=discord.Embed(
                                                        description="You are not allowed to use this Interaction.",
                                                        color=color.red,
                                                    ),
                                                    ephemeral=True,
                                                    delete_after=5,
                                                )

                                            await interaction.response.defer()

                                            nonlocal cancled

                                            cancled = True

                                            await interaction.message.edit(
                                                embed=await get_selected_module_embed(),
                                                view=await get_selected_module_view(
                                                    True
                                                ),
                                            )

                                        except Exception as e:

                                            logger.error(
                                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                            )

                                    if cache_guilds_data.get("subscription") != "free":

                                        if (
                                            cache_antinuke_settings.get("type")
                                            == "custom"
                                        ):

                                            view.add_item(enabled_toggle_button)

                                            view.add_item(limit_selector)

                                            view.add_item(select_punishment)

                                    else:

                                        upgrade_to_premium_button = discord.ui.Button(
                                            label="Upgrade to Premium to edit this module",
                                            style=discord.ButtonStyle.link,
                                            url=self.bot.urls.SUPPORT_SERVER,
                                            row=0,
                                            emoji=self.bot.emoji.PREMIUM,
                                        )

                                        view.add_item(upgrade_to_premium_button)

                                    cancle_button = discord.ui.Button(
                                        label="Cancel",
                                        style=discord.ButtonStyle.gray,
                                        emoji=self.bot.emoji.CANCLED,
                                        row=3,
                                    )

                                    cancle_button.callback = (
                                        lambda i: cancle_button_callback(i)
                                    )

                                    view.add_item(cancle_button)

                                    async def back_button_callback(
                                        interaction: discord.Interaction,
                                    ):

                                        try:

                                            if interaction.user.id != ctx.author.id:

                                                return await interaction.response.send_message(
                                                    embed=discord.Embed(
                                                        description="You are not allowed to use this Interaction.",
                                                        color=color.red,
                                                    ),
                                                    ephemeral=True,
                                                    delete_after=5,
                                                )

                                            await interaction.response.defer()

                                            await interaction.message.edit(
                                                embed=await get_selected_category_embed(),
                                                view=await get_selected_category_view(),
                                            )

                                        except Exception as e:

                                            logger.error(
                                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                            )

                                    back_button = discord.ui.Button(
                                        label="Back",
                                        style=discord.ButtonStyle.gray,
                                        emoji=self.bot.emoji.BACK,
                                        row=3,
                                    )

                                    back_button.callback = (
                                        lambda i: back_button_callback(i)
                                    )

                                    view.add_item(back_button)

                                    if disabled:

                                        # Disable all the buttons

                                        for item in view.children:

                                            item.disabled = True

                                    return view

                                embed = await get_selected_module_embed()

                                view = await get_selected_module_view()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                )

                        select_a_module_to_edit = discord.ui.Select(
                            placeholder="Select a module to edit",
                            min_values=1,
                            max_values=1,
                            options=[
                                discord.SelectOption(
                                    label=sub_value.get("name"),
                                    value=sub_key,
                                    description=sub_value.get("description"),
                                    emoji=sub_value.get("emoji"),
                                )
                                for sub_key, sub_value in antinuke_options.get(
                                    selected_category, {}
                                )
                                .get("options")
                                .items()
                            ],
                            row=0,
                            disabled=not cache_antinuke_settings.get("enabled"),
                        )

                        select_a_module_to_edit.callback = (
                            lambda i: select_a_module_to_edit_callback(i)
                        )

                        view.add_item(select_a_module_to_edit)

                        async def cancle_button_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                nonlocal cancled

                                cancled = True

                                await interaction.message.edit(
                                    embed=await get_selected_category_embed(),
                                    view=await get_selected_category_view(True),
                                )

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                )

                        cancle_button = discord.ui.Button(
                            label="Cancel",
                            style=discord.ButtonStyle.gray,
                            emoji=self.bot.emoji.CANCLED,
                            row=1,
                        )

                        cancle_button.callback = lambda i: cancle_button_callback(i)

                        view.add_item(cancle_button)

                        async def back_button_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                await interaction.message.edit(
                                    embed=await get_embed(), view=await get_view()
                                )

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                )

                        back_button = discord.ui.Button(
                            label="Back",
                            style=discord.ButtonStyle.gray,
                            emoji=self.bot.emoji.BACK,
                            row=1,
                        )

                        back_button.callback = lambda i: back_button_callback(i)

                        view.add_item(back_button)

                        if disabled:

                            # Disable all the buttons

                            for item in view.children:

                                item.disabled = True

                        return view

                    embed = await get_selected_category_embed()

                    view = await get_selected_category_view()

                    await interaction.message.edit(embed=embed, view=view)

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            embed = await get_embed()

            view = await get_view()

            await message.edit(embed=embed, view=view)

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(
                        view=None, content="⌛Timeout Time Reached. Try again."
                    )

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def Logging_Module(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            guild_id = ctx.guild.id

            waiting_embed = discord.Embed(
                title=f"{self.bot.emoji.LOG} - Logging",
                description="Please wait while we fetch the settings...",
                color=color.black,
            )

            waiting_embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            waiting_embed.set_thumbnail(
                url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                )
            )

            message = await ctx.send(embed=waiting_embed)

            cache_data = cache.guilds.get(str(ctx.guild.id))

            if not cache_data:

                waiting_embed.description = f"Guild not found in storage.\nPlease wait while we add the guild to storage {self.bot.emoji.LOADING}"

                try:

                    await guilds_db.insert(guild_id=guild_id)

                    cache_data = cache.guilds.get(str(guild_id))

                    try:

                        await message.edit(embed=waiting_embed)

                    except:

                        pass

                except Exception as e:

                    logger.error(f"Error while adding guild to storage.\nError: {e}")

                    waiting_embed.description = f"An error occured while adding the guild to storage. Please contact our support team."

                    view = discord.ui.View()

                    view.add_item(
                        discord.ui.Button(
                            label="Support Server",
                            url=self.bot.urls.SUPPORT_SERVER,
                            style=discord.ButtonStyle.link,
                        )
                    )

                    await message.edit(embed=waiting_embed, view=view)

                    return

                await asyncio.sleep(1)

            cache_logging_settings = cache.guilds_log.get(str(guild_id), {})

            if not cache_logging_settings:

                waiting_embed.description = f"Settings not found in storage.\nPlease wait while we fetch the settings {self.bot.emoji.LOADING}"

                try:

                    await guilds_log_db.insert(guild_id=guild_id)

                    cache_logging_settings = cache.guilds_log.get(str(guild_id), {})

                    try:

                        await message.edit(embed=waiting_embed)

                    except:

                        pass

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

                    waiting_embed.description = f"An error occured while adding the settings to storage. Please contact our support team."

                    view = discord.ui.View()

                    view.add_item(
                        discord.ui.Button(
                            label="Support Server",
                            url=self.bot.urls.SUPPORT_SERVER,
                            style=discord.ButtonStyle.link,
                        )
                    )

                    await message.edit(embed=waiting_embed, view=view)

                    return

                await asyncio.sleep(1)

            async def get_embed():

                cache_logging_settings = cache.guilds_log.get(str(guild_id), {})

                embed = waiting_embed

                embed.description = None

                embed.color = (
                    color.green if cache_logging_settings.get("enabled") else color.red
                )

                embed.clear_fields()

                embed.description = f"\n**__Logging Status:__** {self.bot.emoji.ENABLED if cache_logging_settings.get('enabled') else self.bot.emoji.DISABLED}"

                embed.description += f"\n{'-'*50}"

                embed.description += f"\n**{self.bot.emoji.MEMBER} : Member Logs**"

                embed.description += f"\n**{self.bot.emoji.MESSAGE} : Message Logs**"

                embed.description += f"\n**{self.bot.emoji.CHANNEL} : Channel Logs**"

                embed.description += f"\n**{self.bot.emoji.CATEGORY} : Role Logs**"

                embed.description += f"\n**{self.bot.emoji.EMOJI} : Emoji Logs**"

                embed.description += f"\n**{self.bot.emoji.WEBHOOK} : Webhook Logs**"

                embed.description += f"\n**{self.bot.emoji.INVITE} : Invite Logs**"

                embed.description += f"\n**{self.bot.emoji.GUILD} : Guild Logs**"

                embed.description += f"\n**{self.bot.emoji.MICROPHONE} : Voice Logs**"

                embed.description += f"\n**{self.bot.emoji.ANTINUKE} : Anti Nuke Logs**"

                embed.description += f"\n{'-'*50}"

                embed.description += (
                    f"\n*You can click on the buttons below to edit the settings.*"
                )

                embed.set_footer(
                    text=f"Setting of Logging",
                    icon_url=(
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    ),
                )

                embed.set_footer(
                    text=f"Setting of Logging",
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

                return embed

            timeout_time = 120

            cancled = False

            def reset_timeout_time(timeout: int = 120):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled: bool = False):

                cache_logging_settings = cache.guilds_log.get(str(guild_id), {})

                reset_timeout_time()

                view = discord.ui.View(timeout=130)

                enabled_toggle_button = discord.ui.Button(
                    label=(
                        "Click to Enable"
                        if not cache_logging_settings.get("enabled")
                        else "Click to Disable"
                    ),
                    style=(
                        discord.ButtonStyle.success
                        if not cache_logging_settings.get("enabled")
                        else discord.ButtonStyle.gray
                    ),
                    emoji=(
                        self.bot.emoji.ENABLED
                        if not cache_logging_settings.get("enabled")
                        else self.bot.emoji.DISABLED
                    ),
                    row=0,
                )

                enabled_toggle_button.callback = (
                    lambda i: enabled_toggle_button_callback(i)
                )

                view.add_item(enabled_toggle_button)

                auto_setup_button = discord.ui.Button(
                    label="Auto Setup",
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.AUTO_SETUP,
                    row=0,
                )

                auto_setup_button.disabled = (
                    cache_logging_settings.get("member_join_channel_id")
                    or cache_logging_settings.get("member_leave_channel_id")
                    or cache_logging_settings.get("member_kick_channel_id")
                    or cache_logging_settings.get("member_ban_channel_id")
                    or cache_logging_settings.get("member_unban_channel_id")
                    or cache_logging_settings.get("member_update_channel_id")
                    or cache_logging_settings.get("message_delete_channel_id")
                    or cache_logging_settings.get("message_edit_channel_id")
                    or cache_logging_settings.get("channel_create_channel_id")
                    or cache_logging_settings.get("channel_delete_channel_id")
                    or cache_logging_settings.get("channel_update_channel_id")
                    or cache_logging_settings.get("role_create_channel_id")
                    or cache_logging_settings.get("role_delete_channel_id")
                    or cache_logging_settings.get("role_update_channel_id")
                    or cache_logging_settings.get("emoji_create_channel_id")
                    or cache_logging_settings.get("emoji_delete_channel_id")
                    or cache_logging_settings.get("emoji_update_channel_id")
                    or cache_logging_settings.get("webhook_create_channel_id")
                    or cache_logging_settings.get("webhook_delete_channel_id")
                    or cache_logging_settings.get("webhook_update_channel_id")
                    or cache_logging_settings.get("invite_create_channel_id")
                    or cache_logging_settings.get("invite_delete_channel_id")
                    or cache_logging_settings.get("guild_update_channel_id")
                    or cache_logging_settings.get("antinuke_channel_id")
                    or cache_logging_settings.get("voice_state_update_channel_id")
                )

                auto_setup_button.callback = lambda i: auto_setup_button_callback(i)

                view.add_item(auto_setup_button)

                edit_module_select = discord.ui.Select(
                    placeholder="Select a module to edit",
                    min_values=1,
                    max_values=1,
                    options=[
                        discord.SelectOption(
                            label="Member Logs",
                            value="member_logs",
                            description="Join, Leave, Kick, Ban, Unban, Update",
                            emoji=self.bot.emoji.MEMBER,
                        ),
                        discord.SelectOption(
                            label="Message Logs",
                            value="message_logs",
                            description="Delete, Edit",
                            emoji=self.bot.emoji.MESSAGE,
                        ),
                        discord.SelectOption(
                            label="Channel Logs",
                            value="channel_logs",
                            description="Create, Delete, Update",
                            emoji=self.bot.emoji.CHANNEL,
                        ),
                        discord.SelectOption(
                            label="Role Logs",
                            value="role_logs",
                            description="Create, Delete, Update",
                            emoji=self.bot.emoji.CATEGORY,
                        ),
                        discord.SelectOption(
                            label="Emoji Logs",
                            value="emoji_logs",
                            description="Create, Delete, Update",
                            emoji=self.bot.emoji.EMOJI,
                        ),
                        discord.SelectOption(
                            label="Webhook Logs",
                            value="webhook_logs",
                            description="Create, Delete, Update",
                            emoji=self.bot.emoji.WEBHOOK,
                        ),
                        discord.SelectOption(
                            label="Invite Logs",
                            value="invite_logs",
                            description="Create, Delete",
                            emoji=self.bot.emoji.INVITE,
                        ),
                        discord.SelectOption(
                            label="Guild Logs",
                            value="guild_logs",
                            description="Update",
                            emoji=self.bot.emoji.GUILD,
                        ),
                        discord.SelectOption(
                            label="Voice Logs",
                            value="voice_logs",
                            description="Join/Leave/Move",
                            emoji=self.bot.emoji.MICROPHONE,
                        ),
                        discord.SelectOption(
                            label="Anti Nuke Logs",
                            value="antinue_logs",
                            description="Anti Nuke",
                            emoji=self.bot.emoji.ANTINUKE,
                        ),
                    ],
                    row=1,
                    disabled=not cache_logging_settings.get("enabled"),
                )

                edit_module_select.callback = lambda i: edit_module_select_callback(i)

                view.add_item(edit_module_select)

                cancled_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.CANCLED,
                    row=0,
                )

                cancled_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(cancled_button)

                if disabled:

                    # Disable all the buttons

                    for item in view.children:

                        item.disabled = True

                return view

            async def auto_setup_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    reset_timeout_time(timeout=500)

                    loading_description = []

                    embed = discord.Embed(
                        title="Auto Setup Initializing...",
                        description="\n".join(loading_description),
                        color=color.purple,
                    )

                    embed.set_footer(
                        text=f"Setting of Logging",
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

                    async def update_embed():

                        try:

                            embed.description = "\n".join(loading_description)

                            await message.edit(embed=embed, view=None)

                        except Exception as e:

                            logger.warning(
                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                            )

                    overwrites = {
                        ctx.guild.default_role: discord.PermissionOverwrite(
                            read_messages=False
                        ),
                        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                    }

                    await guilds_log_db.update(
                        id=cache_logging_settings.get("id"), enabled=True
                    )

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Initializing Category**"
                    )

                    await update_embed()

                    try:

                        logging_category = await ctx.guild.create_category(
                            name="Logging", overwrites=overwrites
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Category**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Category**"
                        )

                        logging_category = None

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Member Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        member_join_channel = await ctx.guild.create_text_channel(
                            name="Members Logs",
                            category=logging_category,
                            overwrites=overwrites,
                            reason="Creating by Auto Setup for Logging",
                        )

                        action_logs_channel = await ctx.guild.create_text_channel(
                            name="Action Logs",
                            category=logging_category,
                            overwrites=overwrites,
                            reason="Creating by Auto Setup for Logging",
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            member_join_channel_id=member_join_channel.id,
                            member_leave_channel_id=member_join_channel.id,
                            member_update_channel_id=member_join_channel.id,
                            member_ban_channel_id=action_logs_channel.id,
                            member_kick_channel_id=action_logs_channel.id,
                            member_unban_channel_id=action_logs_channel.id,
                        )

                        # remove the last item

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Member Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Failed to create Member Join Channel in guild {ctx.guild.id}\nError: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Member Logs**"
                        )

                        await update_embed()

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Message Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        message_delete_channel = await ctx.guild.create_text_channel(
                            name="Message logs",
                            category=logging_category,
                            overwrites=overwrites,
                            reason="Creating by Auto Setup for Logging",
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            message_delete_channel_id=message_delete_channel.id,
                            message_edit_channel_id=message_delete_channel.id,
                        )

                        # remove the last item

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Message Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Failed to create Message Delete Channel in guild {ctx.guild.id}\nError: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Message Logs**"
                        )

                        await update_embed()

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Channel Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        channel_create_channel = await ctx.guild.create_text_channel(
                            name="Channel logs",
                            category=logging_category,
                            overwrites=overwrites,
                            reason="Creating by Auto Setup for Logging",
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            channel_create_channel_id=channel_create_channel.id,
                            channel_delete_channel_id=channel_create_channel.id,
                            channel_update_channel_id=channel_create_channel.id,
                        )

                        # remove the last 3

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Channel Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Channel Logs**"
                        )

                        await update_embed()

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Role Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        role_create_channel = await ctx.guild.create_text_channel(
                            name="Role logs",
                            category=logging_category,
                            overwrites=overwrites,
                            reason="Creating by Auto Setup for Logging",
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            role_create_channel_id=role_create_channel.id,
                            role_delete_channel_id=role_create_channel.id,
                            role_update_channel_id=role_create_channel.id,
                        )

                        # remove the last 3

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Role Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Role Logs**"
                        )

                        await update_embed()

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Guild Logs**"
                    )

                    await update_embed()

                    # Emoji Logs & Webhook Logs & Invite Logs & Guild Logs in the same channel

                    try:

                        await update_embed()

                        guilds_log_channel = await ctx.guild.create_text_channel(
                            name="Guild logs",
                            category=logging_category,
                            overwrites=overwrites,
                            reason="Creating by Auto Setup for Logging",
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            emoji_create_channel_id=guilds_log_channel.id,
                            emoji_delete_channel_id=guilds_log_channel.id,
                            emoji_update_channel_id=guilds_log_channel.id,
                        )

                        # remove the last 3

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Emoji Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Emoji Logs**"
                        )

                        await update_embed()

                        guilds_log_channel = None

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Webhook Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        # if not guilds_log_channel

                        guilds_log_channel = (
                            guilds_log_channel
                            or await ctx.guild.create_text_channel(
                                name="Guild logs",
                                category=logging_category,
                                overwrites=overwrites,
                                reason="Creating by Auto Setup for Logging",
                            )
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            webhook_create_channel_id=guilds_log_channel.id,
                            webhook_delete_channel_id=guilds_log_channel.id,
                            webhook_update_channel_id=guilds_log_channel.id,
                        )

                        # remove the last 3

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Webhook Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Webhook Logs**"
                        )

                        await update_embed()

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Invite Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        # if not guilds_log_channel

                        guilds_log_channel = (
                            guilds_log_channel
                            or await ctx.guild.create_text_channel(
                                name="Guild logs",
                                category=logging_category,
                                overwrites=overwrites,
                                reason="Creating by Auto Setup for Logging",
                            )
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            invite_create_channel_id=guilds_log_channel.id,
                            invite_delete_channel_id=guilds_log_channel.id,
                        )

                        # remove the last 2

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Invite Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Invite Logs**"
                        )

                        await update_embed()

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Guild Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        guilds_log_channel = (
                            guilds_log_channel
                            or await ctx.guild.create_text_channel(
                                name="Guild logs",
                                category=logging_category,
                                overwrites=overwrites,
                                reason="Creating by Auto Setup for Logging",
                            )
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            guild_update_channel_id=guilds_log_channel.id,
                        )

                        # remove the last item

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Guild Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Failed to create Guild Update Channel in guild {ctx.guild.id}\nError: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Guild Logs**"
                        )

                        await update_embed()

                    loading_description.append(
                        f"**{self.bot.emoji.LOADING} : Voice Logs**"
                    )

                    await update_embed()

                    try:

                        await update_embed()

                        voice_state_update_channel = (
                            await ctx.guild.create_text_channel(
                                name="Voice State Logs",
                                category=logging_category,
                                overwrites=overwrites,
                                reason="Creating by Auto Setup for Logging",
                            )
                        )

                        await guilds_log_db.update(
                            id=cache_logging_settings.get("id"),
                            voice_state_update_channel_id=voice_state_update_channel.id,
                        )

                        # remove the last item

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.SUCCESS} : Voice Logs**"
                        )

                        await update_embed()

                    except Exception as e:

                        logger.error(
                            f"Failed to create Voice State Update Channel in guild {ctx.guild.id}\nError: {e}"
                        )

                        loading_description.pop()

                        loading_description.append(
                            f"**{self.bot.emoji.FAILED} : Voice Logs**"
                        )

                        await update_embed()

                    # after successfull setup

                    embed.title = f"Auto Setup Completed"

                    embed.set_footer(
                        text=f"Logging Auto Setup Completed",
                        icon_url=(
                            ctx.guild.icon.url
                            if ctx.guild.icon
                            else self.bot.user.display_avatar.url
                        ),
                    )

                    await update_embed()

                    view = discord.ui.View(timeout=130)

                    async def back_to_home_button_callback(
                        interaction: discord.Interaction,
                    ):

                        try:

                            if interaction.user.id != ctx.author.id:

                                return await interaction.response.send_message(
                                    embed=discord.Embed(
                                        description="You are not allowed to use this Interaction.",
                                        color=color.red,
                                    ),
                                    ephemeral=True,
                                    delete_after=5,
                                )

                            await interaction.response.defer()

                            await message.edit(
                                embed=await get_embed(), view=await get_view()
                            )

                        except Exception as e:

                            logger.error(
                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                            )

                    back_to_home_button = discord.ui.Button(
                        label="Back to Home",
                        style=discord.ButtonStyle.blurple,
                        emoji=self.bot.emoji.BACK,
                        row=0,
                    )

                    back_to_home_button.callback = (
                        lambda i: back_to_home_button_callback(i)
                    )

                    view.add_item(back_to_home_button)

                    await message.edit(view=view)

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

                    await message.edit(
                        embed=discord.Embed(
                            description=f"An error occured while setting up the logging.\nError: {e}",
                            color=color.red,
                        ),
                        view=None,
                    )

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    nonlocal cancled

                    cancled = True

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view(True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def back_to_home_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    await message.edit(embed=await get_embed(), view=await get_view())

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def edit_module_select_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    # delete the interaction response

                    await interaction.response.defer()

                    value = interaction.data.get("values")[0]

                    if value == "member_logs":

                        async def get_embed_and_view_member_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.MEMBER} - Member Logs",
                                description="Select the channel for the logs of the member logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.JOIN} - Join Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "member_join_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.LEAVE} - Leave Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "member_leave_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(name="", value="", inline=False)

                            embed.add_field(
                                name=f"{self.bot.emoji.KICK} - Kick Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "member_kick_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.BAN} - Ban Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "member_ban_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(name="", value="", inline=False)

                            embed.add_field(
                                name=f"{self.bot.emoji.UNBAN} - Unban Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "member_unban_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.UPDATE} - Update Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "member_update_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Member Logs",
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

                            default_join_logs = []

                            if cache_logging_settings.get("member_join_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get("member_join_channel_id")
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_join_logs.append(channel)

                            join_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Join Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_join_logs,
                            )

                            join_log_select.callback = (
                                lambda i: join_log_select_callback(i)
                            )

                            view.add_item(join_log_select)

                            default_leave_logs = []

                            if cache_logging_settings.get("member_leave_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "member_leave_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_leave_logs.append(channel)

                            leave_log_select = discord.ui.ChannelSelect(
                                row=1,
                                placeholder="Select a channel for Leave Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_leave_logs,
                            )

                            leave_log_select.callback = (
                                lambda i: leave_log_select_callback(i)
                            )

                            view.add_item(leave_log_select)

                            default_kick_ban_and_unban_logs = []

                            if cache_logging_settings.get("member_kick_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get("member_kick_channel_id")
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_kick_ban_and_unban_logs.append(channel)

                            kick_ban_and_unban_log_select = discord.ui.ChannelSelect(
                                row=2,
                                placeholder="Select a channel for Kick/Ban/Unban Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_kick_ban_and_unban_logs,
                            )

                            kick_ban_and_unban_log_select.callback = (
                                lambda i: kick_ban_and_unban_log_select_callback(i)
                            )

                            view.add_item(kick_ban_and_unban_log_select)

                            default_update_logs = []

                            if cache_logging_settings.get("member_update_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "member_update_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_update_logs.append(channel)

                            update_log_select = discord.ui.ChannelSelect(
                                row=3,
                                placeholder="Select a channel for Update Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_update_logs,
                            )

                            update_log_select.callback = (
                                lambda i: update_log_select_callback(i)
                            )

                            view.add_item(update_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=4,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def join_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    member_join_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_member_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                )

                        async def leave_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    member_leave_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_member_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                )

                        async def kick_ban_and_unban_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    member_kick_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                    member_ban_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                    member_unban_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_member_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                )

                        async def update_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    member_update_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_member_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                                )

                        embed, view = await get_embed_and_view_member_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "message_logs":

                        async def get_embed_and_view_message_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.MESSAGE} - Message Logs",
                                description="Select the channel for the logs of the message logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.DELETE} - Delete Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "message_delete_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.EDIT} - Edit Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "message_edit_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Message Logs",
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

                            default_delete_logs = []

                            if cache_logging_settings.get("message_delete_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "message_delete_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_delete_logs.append(channel)

                            message_delete_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Delete Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_delete_logs,
                            )

                            message_delete_log_select.callback = (
                                lambda i: message_delete_log_select_callback(i)
                            )

                            view.add_item(message_delete_log_select)

                            default_edit_logs = []

                            if cache_logging_settings.get("message_edit_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "message_edit_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_edit_logs.append(channel)

                            message_edit_log_select = discord.ui.ChannelSelect(
                                row=1,
                                placeholder="Select a channel for Edit Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_edit_logs,
                            )

                            message_edit_log_select.callback = (
                                lambda i: message_edit_log_select_callback(i)
                            )

                            view.add_item(message_edit_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=2,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def message_delete_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    message_delete_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_message_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def message_edit_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    message_edit_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_message_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_message_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "channel_logs":

                        async def get_embed_and_view_channel_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.CHANNEL} - Channel Logs",
                                description="Select the channel for the logs of the channel logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.CREATE} - Create Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "channel_create_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.DELETE} - Delete Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "channel_delete_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(name="", value="", inline=False)

                            embed.add_field(
                                name=f"{self.bot.emoji.UPDATE} - Update Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "channel_update_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Channel Logs",
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

                            default_create_logs = []

                            if cache_logging_settings.get("channel_create_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "channel_create_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_create_logs.append(channel)

                            channel_create_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Create Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_create_logs,
                            )

                            channel_create_log_select.callback = (
                                lambda i: channel_create_log_select_callback(i)
                            )

                            view.add_item(channel_create_log_select)

                            default_delete_logs = []

                            if cache_logging_settings.get("channel_delete_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "channel_delete_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_delete_logs.append(channel)

                            channel_delete_log_select = discord.ui.ChannelSelect(
                                row=1,
                                placeholder="Select a channel for Delete Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_delete_logs,
                            )

                            channel_delete_log_select.callback = (
                                lambda i: channel_delete_log_select_callback(i)
                            )

                            view.add_item(channel_delete_log_select)

                            default_update_logs = []

                            if cache_logging_settings.get("channel_update_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "channel_update_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_update_logs.append(channel)

                            channel_update_log_select = discord.ui.ChannelSelect(
                                row=2,
                                placeholder="Select a channel for Update Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_update_logs,
                            )

                            channel_update_log_select.callback = (
                                lambda i: channel_update_log_select_callback(i)
                            )

                            view.add_item(channel_update_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=3,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def channel_create_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    channel_create_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_channel_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def channel_delete_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    channel_delete_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_channel_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def channel_update_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    channel_update_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_channel_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_channel_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "role_logs":

                        async def get_embed_and_view_role_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.CATEGORY} - Role Logs",
                                description="Select the channel for the logs of the role logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.CREATE} - Create Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "role_create_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.DELETE} - Delete Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "role_delete_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(name="", value="", inline=False)

                            embed.add_field(
                                name=f"{self.bot.emoji.UPDATE} - Update Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "role_update_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Role Logs",
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

                            default_create_logs = []

                            if cache_logging_settings.get("role_create_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get("role_create_channel_id")
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_create_logs.append(channel)

                            role_create_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Create Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_create_logs,
                            )

                            role_create_log_select.callback = (
                                lambda i: role_create_log_select_callback(i)
                            )

                            view.add_item(role_create_log_select)

                            default_delete_logs = []

                            if cache_logging_settings.get("role_delete_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get("role_delete_channel_id")
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_delete_logs.append(channel)

                            role_delete_log_select = discord.ui.ChannelSelect(
                                row=1,
                                placeholder="Select a channel for Delete Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_delete_logs,
                            )

                            role_delete_log_select.callback = (
                                lambda i: role_delete_log_select_callback(i)
                            )

                            view.add_item(role_delete_log_select)

                            default_update_logs = []

                            if cache_logging_settings.get("role_update_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get("role_update_channel_id")
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_update_logs.append(channel)

                            role_update_log_select = discord.ui.ChannelSelect(
                                row=2,
                                placeholder="Select a channel for Update Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_update_logs,
                            )

                            role_update_log_select.callback = (
                                lambda i: role_update_log_select_callback(i)
                            )

                            view.add_item(role_update_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=3,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def role_create_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    role_create_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_role_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def role_delete_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    role_delete_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_role_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def role_update_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    role_update_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_role_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_role_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "emoji_logs":

                        async def get_embed_and_view_emoji_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.EMOJI} - Emoji Logs",
                                description="Select the channel for the logs of the emoji logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.CREATE} - Create Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "emoji_create_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.DELETE} - Delete Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "emoji_delete_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(name="", value="", inline=False)

                            embed.add_field(
                                name=f"{self.bot.emoji.UPDATE} - Update Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "emoji_update_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Emoji Logs",
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

                            default_create_logs = []

                            if cache_logging_settings.get("emoji_create_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "emoji_create_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_create_logs.append(channel)

                            emoji_create_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Create Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_create_logs,
                            )

                            emoji_create_log_select.callback = (
                                lambda i: emoji_create_log_select_callback(i)
                            )

                            view.add_item(emoji_create_log_select)

                            default_delete_logs = []

                            if cache_logging_settings.get("emoji_delete_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "emoji_delete_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_delete_logs.append(channel)

                            emoji_delete_log_select = discord.ui.ChannelSelect(
                                row=1,
                                placeholder="Select a channel for Delete Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_delete_logs,
                            )

                            emoji_delete_log_select.callback = (
                                lambda i: emoji_delete_log_select_callback(i)
                            )

                            view.add_item(emoji_delete_log_select)

                            default_update_logs = []

                            if cache_logging_settings.get("emoji_update_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "emoji_update_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_update_logs.append(channel)

                            emoji_update_log_select = discord.ui.ChannelSelect(
                                row=2,
                                placeholder="Select a channel for Update Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_update_logs,
                            )

                            emoji_update_log_select.callback = (
                                lambda i: emoji_update_log_select_callback(i)
                            )

                            view.add_item(emoji_update_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=3,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def emoji_create_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    emoji_create_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_emoji_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def emoji_delete_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    emoji_delete_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_emoji_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def emoji_update_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    emoji_update_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_emoji_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_emoji_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "webhook_logs":

                        async def get_embed_and_view_webhook_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.WEBHOOK} - Webhook Logs",
                                description="Select the channel for the logs of the webhook logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.CREATE} - Create Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "webhook_create_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.DELETE} - Delete Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "webhook_delete_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(name="", value="", inline=False)

                            embed.add_field(
                                name=f"{self.bot.emoji.UPDATE} - Update Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "webhook_update_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Webhook Logs",
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

                            default_create_logs = []

                            if cache_logging_settings.get("webhook_create_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "webhook_create_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_create_logs.append(channel)

                            webhook_create_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Create Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_create_logs,
                            )

                            webhook_create_log_select.callback = (
                                lambda i: webhook_create_log_select_callback(i)
                            )

                            view.add_item(webhook_create_log_select)

                            default_delete_logs = []

                            if cache_logging_settings.get("webhook_delete_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "webhook_delete_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_delete_logs.append(channel)

                            webhook_delete_log_select = discord.ui.ChannelSelect(
                                row=1,
                                placeholder="Select a channel for Delete Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_delete_logs,
                            )

                            webhook_delete_log_select.callback = (
                                lambda i: webhook_delete_log_select_callback(i)
                            )

                            view.add_item(webhook_delete_log_select)

                            default_update_logs = []

                            if cache_logging_settings.get("webhook_update_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "webhook_update_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_update_logs.append(channel)

                            webhook_update_log_select = discord.ui.ChannelSelect(
                                row=2,
                                placeholder="Select a channel for Update Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_update_logs,
                            )

                            webhook_update_log_select.callback = (
                                lambda i: webhook_update_log_select_callback(i)
                            )

                            view.add_item(webhook_update_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=3,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def webhook_create_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    webhook_create_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_webhook_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def webhook_delete_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    webhook_delete_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_webhook_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def webhook_update_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    webhook_update_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_webhook_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_webhook_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "invite_logs":

                        async def get_embed_and_view_invite_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.INVITE} - Invite Logs",
                                description="Select the channel for the logs of the invite logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.CREATE} - Create Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "invite_create_channel_id"
                                ),
                                inline=True,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.DELETE} - Delete Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "invite_delete_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Invite Logs",
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

                            default_create_logs = []

                            if cache_logging_settings.get("invite_create_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "invite_create_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_create_logs.append(channel)

                            invite_create_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Create Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_create_logs,
                            )

                            invite_create_log_select.callback = (
                                lambda i: invite_create_log_select_callback(i)
                            )

                            view.add_item(invite_create_log_select)

                            default_delete_logs = []

                            if cache_logging_settings.get("invite_delete_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "invite_delete_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_delete_logs.append(channel)

                            invite_delete_log_select = discord.ui.ChannelSelect(
                                row=1,
                                placeholder="Select a channel for Delete Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_delete_logs,
                            )

                            invite_delete_log_select.callback = (
                                lambda i: invite_delete_log_select_callback(i)
                            )

                            view.add_item(invite_delete_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=2,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def invite_create_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    invite_create_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_invite_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        async def invite_delete_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    invite_delete_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_invite_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_invite_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "guild_logs":

                        async def get_embed_and_view_guild_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.GUILD} - Guild Logs",
                                description="Select the channel for the logs of the guild logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.UPDATE} - Update Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "guild_update_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Guild Logs",
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

                            default_update_logs = []

                            if cache_logging_settings.get("guild_update_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "guild_update_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_update_logs.append(channel)

                            guild_update_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Update Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_update_logs,
                            )

                            guild_update_log_select.callback = (
                                lambda i: guild_update_log_select_callback(i)
                            )

                            view.add_item(guild_update_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=1,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def guild_update_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    guild_update_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_guild_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_guild_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "voice_logs":

                        async def get_embed_and_view_voice_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.MICROPHONE} - Voice Logs",
                                description="Select the channel for the logs of the voice logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.JOIN} - Join/Leave/Move Log",
                                value=format_logging_channel(
                                    cache_logging_settings,
                                    "voice_state_update_channel_id",
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of Voice Logs",
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

                            default_voice_logs = []

                            if cache_logging_settings.get(
                                "voice_state_update_channel_id"
                            ):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get(
                                        "voice_state_update_channel_id"
                                    )
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_voice_logs.append(channel)

                            voice_state_update_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for Join/Leave/Move Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_voice_logs,
                            )

                            voice_state_update_log_select.callback = (
                                lambda i: voice_state_update_log_select_callback(i)
                            )

                            view.add_item(voice_state_update_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=1,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def voice_state_update_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    voice_state_update_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_voice_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_voice_logs()

                        await interaction.message.edit(embed=embed, view=view)

                    elif value == "antinue_logs":

                        async def get_embed_and_view_antinue_logs():

                            reset_timeout_time()

                            view = discord.ui.View(timeout=130)

                            cache_logging_settings = cache.guilds_log.get(
                                str(guild_id), {}
                            )

                            embed = discord.Embed(
                                title=f"{self.bot.emoji.ANTINUKE} - AntiNuke Logs",
                                description="Select the channel for the logs of the antinue logs.",
                                color=color.green,
                            )

                            embed.add_field(
                                name=f"{self.bot.emoji.ANTINUKE} - AntiNuke Log",
                                value=format_logging_channel(
                                    cache_logging_settings, "antinuke_channel_id"
                                ),
                                inline=True,
                            )

                            embed.set_footer(
                                text=f"Setting of AntiNuke Logs",
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

                            default_antinue_logs = []

                            if cache_logging_settings.get("antinuke_channel_id"):

                                channel = ctx.guild.get_channel(
                                    cache_logging_settings.get("antinuke_channel_id")
                                )

                                if channel:

                                    if isinstance(channel, discord.TextChannel):

                                        default_antinue_logs.append(channel)

                            antinue_log_select = discord.ui.ChannelSelect(
                                row=0,
                                placeholder="Select a channel for AntiNuke Log",
                                min_values=0,
                                max_values=1,
                                channel_types=[discord.ChannelType.text],
                                default_values=default_antinue_logs,
                            )

                            antinue_log_select.callback = (
                                lambda i: antinue_log_select_callback(i)
                            )

                            view.add_item(antinue_log_select)

                            back_to_home_button = discord.ui.Button(
                                label="Back to Home",
                                style=discord.ButtonStyle.primary,
                                emoji=self.bot.emoji.HOME,
                                row=1,
                            )

                            back_to_home_button.callback = (
                                lambda i: back_to_home_button_callback(i)
                            )

                            view.add_item(back_to_home_button)

                            return embed, view

                        async def antinue_log_select_callback(
                            interaction: discord.Interaction,
                        ):

                            try:

                                if interaction.user.id != ctx.author.id:

                                    return await interaction.response.send_message(
                                        embed=discord.Embed(
                                            description="You are not allowed to use this Interaction.",
                                            color=color.red,
                                        ),
                                        ephemeral=True,
                                        delete_after=5,
                                    )

                                await interaction.response.defer()

                                cache_logging_settings = cache.guilds_log.get(
                                    str(guild_id), {}
                                )

                                await guilds_log_db.update(
                                    id=cache_logging_settings.get("id"),
                                    antinuke_channel_id=(
                                        interaction.data.get("values")[0]
                                        if interaction.data.get("values")
                                        else ""
                                    ),
                                )

                                embed, view = await get_embed_and_view_antinue_logs()

                                await interaction.message.edit(embed=embed, view=view)

                            except Exception as e:

                                logger.error(
                                    f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                                )

                        embed, view = await get_embed_and_view_antinue_logs()

                        await interaction.message.edit(embed=embed, view=view)

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def enabled_toggle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    cache_logging_settings = cache.guilds_log.get(str(guild_id), {})

                    await guilds_log_db.update(
                        id=cache_logging_settings.get("id"),
                        enabled=not cache_logging_settings.get("enabled", False),
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            embed = await get_embed()

            view = await get_view()

            await message.edit(embed=embed, view=view)

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(
                        view=None, content="⌛Timeout Time Reached. Try again."
                    )

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def Welcome_Module(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            cache_welcome_settings = cache.welcomer_settings.get(str(ctx.guild.id), {})

            if not cache_welcome_settings:

                await welcomer_settings_db.insert(
                    guild_id=ctx.guild.id,
                    welcome=True,
                    welcome_channel=(
                        ctx.guild.system_channel.id
                        if ctx.guild.system_channel
                        else None
                    ),
                    welcome_message=True,
                    welcome_message_content="Welcome {user} to {server}. Enjoy your stay!",
                )

            async def get_home_embed():

                embed = discord.Embed(
                    title="Welcome Module List",
                    description=f"These are the welcome module available in the bot.",
                    color=color.green,
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author.name}",
                    icon_url=ctx.author.display_avatar.url,
                )

                embed.set_thumbnail(
                    url=(
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    )
                )

                cache_welcome_settings = cache.welcomer_settings.get(
                    str(ctx.guild.id), {}
                )

                embed.description += f"\n\n{self.bot.emoji.ENABLED if cache_welcome_settings.get('welcome') else self.bot.emoji.DISABLED} - Welcome Module"

                embed.description += f"\n{self.bot.emoji.ENABLED if cache_welcome_settings.get('autorole') else self.bot.emoji.DISABLED} - AutoRole Module"

                embed.description += f"\n{self.bot.emoji.ENABLED if cache_welcome_settings.get('autonick') else self.bot.emoji.DISABLED} - AutoNick Module"

                return embed

            timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_home_view(disabled=False):

                view = discord.ui.View(timeout=200)

                reset_timeout_time(200)

                guilds_cache = cache.guilds.get(str(ctx.guild.id), {})

                cache_welcome_settings = cache.welcomer_settings.get(
                    str(ctx.guild.id), {}
                )

                Select_module_to_edit = discord.ui.Select(
                    placeholder="Select a module to edit",
                    min_values=1,
                    max_values=1,
                    options=[
                        discord.SelectOption(
                            label="Welcome",
                            value="welcome",
                            description="Welcome the user when they join the server",
                            emoji=self.bot.emoji.WELCOME,
                        ),
                        discord.SelectOption(
                            label="AutoRole",
                            value="autorole",
                            description="Give roles to the user when they join the server",
                            emoji=self.bot.emoji.AUTOROLE,
                        ),
                        discord.SelectOption(
                            label="AutoNick",
                            value="autonick",
                            description="Change the nickname of the user when they join the server",
                            emoji=self.bot.emoji.AUTONICK,
                        ),
                    ],
                    row=0,
                )

                Select_module_to_edit.callback = (
                    lambda i: Select_module_to_edit_callback(i)
                )

                cancle_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.CANCLED,
                    row=1,
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(Select_module_to_edit)

                view.add_item(cancle_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def Select_module_to_edit_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.defer()

                    await interaction.message.delete()

                    if interaction.data.get("values")[0] == "welcome":

                        await self.bot.get_command("welcome").cog.welcome_settings(ctx)

                    elif interaction.data.get("values")[0] == "autorole":

                        await self.bot.get_command("autorole").cog.autorole_settings(
                            ctx
                        )

                    elif interaction.data.get("values")[0] == "autonick":

                        await self.bot.get_command("autonick").cog.autonick_settings(
                            ctx
                        )

                    else:

                        await ctx.send(
                            embed=discord.Embed(
                                description="Invalid Module Selected", color=color.red
                            )
                        )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.defer()

                    await interaction.message.edit(
                        embed=await get_home_embed(),
                        view=await get_home_view(disabled=True),
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            embed = await get_home_embed()

            view = await get_home_view()

            message = await ctx.send(embed=embed, view=view)

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(view=await get_home_view(disabled=True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def all_modules(self, ctx: commands.Context):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                title="All Modules List", description="", color=color.green
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            embed.set_thumbnail(
                url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                )
            )

            cache_j2c_settings = cache.j2c_settings.get(str(ctx.guild.id), {})

            cache_logging_settings = cache.guilds_log.get(str(ctx.guild.id), {})

            cache_anti_nuke_settings = cache.antinuke_settings.get(
                str(ctx.guild.id), {}
            )

            cache_welcomer_settings = cache.welcomer_settings.get(str(ctx.guild.id), {})

            cache_automod_settings = cache.automod.get(str(ctx.guild.id), {})

            tickets_settings = cache.ticket_settings.get(str(ctx.guild.id), {})

            music_data = cache.music.get(str(ctx.guild.id), {})

            # embed.description += f"\n\n**{self.bot.emoji.J2C} __Join To Create VC__ {(self.bot.emoji.ENABLED if cache_j2c_settings.get('enabled') else self.bot.emoji.DISABLED) if cache_j2c_settings else self.bot.emoji.DISABLED}**"

            # embed.description += f"\n**__AntiNuke__ {self.bot.emoji.ENABLED if cache_anti_nuke_settings.get('enabled') else self.bot.emoji.DISABLED}**"

            # embed.description += f"\n**__AutoMod__ {self.bot.emoji.ENABLED if (cache_automod_settings.get('antilink_enabled') or  cache_automod_settings.get('antibadwords_enabled') or cache_automod_settings.get('antispam_enabled')) else self.bot.emoji.DISABLED}**"

            # embed.description += f"\n**__Logging__ {(self.bot.emoji.ENABLED if cache_logging_settings.get('enabled') else self.bot.emoji.DISABLED) if cache_logging_settings else self.bot.emoji.DISABLED}**"

            # embed.description += f"\n**__Welcomer__ {self.bot.emoji.ENABLED if any([cache_welcomer_settings.get('welcome'),cache_welcomer_settings.get('autorole'),cache_welcomer_settings.get('autonick')]) else self.bot.emoji.DISABLED}**"

            def check_ticket_enabled(tickets_settings):

                try:

                    enabled = False

                    for (
                        ticket_module_id,
                        ticket_settings_data,
                    ) in tickets_settings.items():

                        if ticket_settings_data.get("enabled"):

                            enabled = True

                            break

                    return enabled

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

                    return False

            embed.description += f"**{self.bot.emoji.ENABLED if cache_j2c_settings.get('enabled') else self.bot.emoji.DISABLED} : {self.bot.emoji.J2C} - Join To Create VC"

            embed.description += f"\n{self.bot.emoji.ENABLED if any([cache_automod_settings.get('antilink_enabled'),cache_automod_settings.get('antibadwords_enabled'),cache_automod_settings.get('antispam_enabled')]) else self.bot.emoji.DISABLED} : {self.bot.emoji.AUTOMOD} - AutoMod"

            embed.description += f"\n{self.bot.emoji.ENABLED if cache_anti_nuke_settings.get('enabled') else self.bot.emoji.DISABLED} : {self.bot.emoji.ANTINUKE} - AntiNuke"

            embed.description += f"\n{self.bot.emoji.ENABLED if cache_logging_settings.get('enabled') else self.bot.emoji.DISABLED} : {self.bot.emoji.LOG} - Logging"

            embed.description += f"\n{self.bot.emoji.ENABLED if any([cache_welcomer_settings.get('welcome'),cache_welcomer_settings.get('autorole'),cache_welcomer_settings.get('autonick')]) else self.bot.emoji.DISABLED} : {self.bot.emoji.WELCOME} - Welcomer"

            embed.description += f"\n{self.bot.emoji.ENABLED if check_ticket_enabled(tickets_settings) else self.bot.emoji.DISABLED} : {self.bot.emoji.TICKET} - Ticket System**"

            embed.description += f"\n{self.bot.emoji.ENABLED if music_data else self.bot.emoji.DISABLED} : {self.bot.emoji.MUSIC} - Music System**"

            # embed.add_field(

            #     name=f"{self.bot.emoji.J2C} - Join To Create VC",

            #     value=f"{self.bot.emoji.ENABLED if cache_j2c_settings.get('enabled') else self.bot.emoji.DISABLED}",

            #     inline=False

            # )

            # embed.add_field(

            #     name=f"{self.bot.emoji.AUTOMOD} - AutoMod",

            #     value=f"{self.bot.emoji.ENABLED if any([cache_automod_settings.get('antilink_enabled'),cache_automod_settings.get('antibadwords_enabled'),cache_automod_settings.get('antispam_enabled')]) else self.bot.emoji.DISABLED}",

            #     inline=False

            # )

            # embed.add_field(

            #     name=f"{self.bot.emoji.ANTINUKE} - AntiNuke",

            #     value=f"{self.bot.emoji.ENABLED if cache_anti_nuke_settings.get('enabled') else self.bot.emoji.DISABLED}",

            #     inline=False

            # )

            # embed.add_field(

            #     name=f"{self.bot.emoji.LOG} - Logging",

            #     value=f"{self.bot.emoji.ENABLED if cache_logging_settings.get('enabled') else self.bot.emoji.DISABLED}",

            #     inline=False

            # )

            # embed.add_field(

            #     name=f"{self.bot.emoji.WELCOME} - Welcomer",

            #     value=f"{self.bot.emoji.ENABLED if any([cache_welcomer_settings.get('welcome'),cache_welcomer_settings.get('autorole'),cache_welcomer_settings.get('autonick')]) else self.bot.emoji.DISABLED}",

            #     inline=False

            # )

            view = discord.ui.View(timeout=150)

            view_timeout_time = 60

            cancled = False

            # auto_setup_button = discord.ui.Button(

            #     label="Auto Setup All Modules (Recommended for new users)",

            #     style=discord.ButtonStyle.success,

            #     emoji=self.bot.emoji.ROBOT,

            #     row=1

            # )

            # auto_setup_button.callback = lambda i: auto_setup_button_callback(i)

            # if not cache_j2c_settings.get('enabled') and not cache_logging_settings.get('enabled'):

            #     view.add_item(auto_setup_button)

            select_module = discord.ui.Select(
                placeholder="Select a module to setup",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(
                        label="Join To Create VC",
                        value="j2c",
                        description="Create a VC when a user joins the VC Channel",
                        emoji=self.bot.emoji.J2C,
                    ),
                    discord.SelectOption(
                        label="AutoMod",
                        value="automod",
                        description="Automatically moderate the server",
                        emoji=self.bot.emoji.AUTOMOD,
                    ),
                    discord.SelectOption(
                        label="AntiNuke",
                        value="antinuke",
                        description="Protect your server from nukers",
                        emoji=self.bot.emoji.ANTINUKE,
                    ),
                    discord.SelectOption(
                        label="Logging",
                        value="logging",
                        description="Log all the actions in the server",
                        emoji=self.bot.emoji.LOG,
                    ),
                    discord.SelectOption(
                        label="Welcomer",
                        value="welcomer",
                        description="Activitys when a user joins the server",
                        emoji=self.bot.emoji.WELCOME,
                    ),
                    discord.SelectOption(
                        label="Ticket",
                        value="ticket",
                        description="Create a ticket system in the server",
                        emoji=self.bot.emoji.TICKET,
                    ),
                    discord.SelectOption(
                        label="Music",
                        value="music",
                        description="Setup the music system in the server",
                        emoji=self.bot.emoji.MUSIC,
                    ),
                ],
                row=2,
            )

            select_module.callback = lambda i: select_module_callback(i)

            view.add_item(select_module)

            async def auto_setup_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    await interaction.response.defer()

                    pass  # Auto Setup all the modules

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def select_module_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    # delete the interaction response

                    await interaction.response.defer()

                    await interaction.message.delete()

                    if interaction.data.get("values")[0] == "j2c":

                        await self.JoinToCreateVC_Module(ctx)

                    elif interaction.data.get("values")[0] == "automod":

                        await self.AutoMod_Module(ctx)

                    elif interaction.data.get("values")[0] == "antinuke":

                        await self.AntiNuke_Module(ctx)

                    elif interaction.data.get("values")[0] == "logging":

                        await self.Logging_Module(ctx)

                    elif interaction.data.get("values")[0] == "welcomer":

                        await self.Welcome_Module(ctx)

                    elif interaction.data.get("values")[0] == "ticket":

                        await self.Ticket_Module(ctx)

                    elif interaction.data.get("values")[0] == "music":

                        await self.setup_music(ctx)

                    else:

                        await ctx.send(
                            embed=discord.Embed(
                                description="Invalid Module Selected", color=color.red
                            )
                        )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=embed, view=view)

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    for item in view.children:

                        item.disabled = True

                    await message.edit(view=view)

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_group(
        name="setup",
        help="Help In Setup diff. things",
        with_app_command=True,
        aliases=["settings"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup(self, ctx: commands.Context, module: str = None):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            if ctx.interaction and not ctx.interaction.response:

                await ctx.defer()

            if not module:

                await self.all_modules(ctx)

                return

            module = module.lower()

            if module not in [
                "j2c",
                "automod",
                "antinuke",
                "logging",
                "welcomer",
                "all",
                "music",
            ]:

                return await ctx.send(
                    embed=discord.Embed(
                        description="Invalid Module Selected to setup\nAvailable Modules: `j2c`,`automod`,`antinuke`,`logging`,`welcomer`",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            if module == "all":

                await self.all_modules(ctx)

            elif module == "j2c":

                await self.JoinToCreateVC_Module(ctx)

            elif module == "automod":

                await self.AutoMod_Module(ctx)

            elif module == "antinuke":

                await self.AntiNuke_Module(ctx)

            elif module == "logging":

                await self.Logging_Module(ctx)

            elif module == "welcomer":

                await self.Welcome_Module(ctx)

            elif module == "music":

                await self.setup_music(ctx)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @setup.command(name="all", help="Setup all the modules", with_app_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup_all(self, ctx: commands.Context):

        await self.all_modules(ctx)

    @setup.command(
        name="j2c", help="Setup the Join To Create VC Module", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup_j2c(self, ctx: commands.Context):

        await self.JoinToCreateVC_Module(ctx)

    @setup.command(
        name="automod", help="Setup the AutoMod Module", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup_automod(self, ctx: commands.Context):

        await self.AutoMod_Module(ctx)

    @setup.command(
        name="antinuke", help="Setup the AntiNuke Module", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup_antinuke(self, ctx: commands.Context):

        await self.AntiNuke_Module(ctx)

    @setup.command(
        name="logging", help="Setup the Logging Module", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup_logging(self, ctx: commands.Context):

        await self.Logging_Module(ctx)

    @setup.command(
        name="ticket", help="Setup the Ticket System Module", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup_ticket(self, ctx: commands.Context):

        await self.Ticket_Module(ctx)

    @setup.command(
        name="welcomer", help="Setup the Welcomer Module", with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def setup_welcomer(self, ctx: commands.Context):

        await self.Welcome_Module(ctx)

    @setup.command(name="music", help="Setup the Music Module", with_app_command=True)
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=60, type=commands.BucketType.guild)
    async def setup_music(self, ctx: commands.Context):

        try:

            music_cog = self.bot.get_cog("Music")

            if not music_cog:

                return await ctx.send(
                    embed=discord.Embed(
                        description="Music Module is not loaded in the bot.",
                        color=color.red,
                    )
                )

            await music_cog.music_settings(ctx)

        except:

            logger.error(f"Traceback: {traceback.format_exc()}")

    @commands.group(
        name="reset",
        help="Reset the settings of the modules",
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset Modules",
                description="Here are the list of modules that you can reset.",
                color=color.green,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}"

            embed.set_footer(
                text=f"REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(
        name="all", help="Reset all the settings of the modules", aliases=["everything"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_all(self, ctx: commands.Context):

        try:

            # first ask for confirmation in a embed

            # the if he click yes or no you know what to do

            # this confirmation must be under 60 second else disable the buttons

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset All Modules",
                description="Are you sure you want to reset all the settings of the modules?",
                color=color.green,
            )

            embed.description += "\n\nThis will reset all the settings of the modules like Join To Create VC, AutoMod, AntiNuke, Logging, Welcomer."

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting all the modules settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.automod.delete(guild_id=ctx.guild.id)

                    await storage.antinuke_settings.delete(guild_id=ctx.guild.id)

                    await storage.guilds_log.delete(guild_id=ctx.guild.id)

                    await storage.j2c_settings.delete(guild_id=ctx.guild.id)

                    await storage.welcomer_settings.delete(guild_id=ctx.guild.id)

                    await storage.music.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="All the modules settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(
        name="j2c",
        help="Reset the settings of the Join To Create VC Module",
        aliases=["join_to_create_vc"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_j2c(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset Join To Create VC",
                description="Are you sure you want to reset the settings of the Join To Create VC Module?",
                color=color.green,
            )

            embed.description += (
                "\n\nThis will reset all the settings of the Join To Create VC Module."
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting the Join To Create VC Module settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.j2c_settings.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="Join To Create VC Module settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(
        name="automod",
        help="Reset the settings of the AutoMod Module",
        aliases=["auto_mod"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_automod(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset AutoMod",
                description="Are you sure you want to reset the settings of the AutoMod Module?",
                color=color.green,
            )

            embed.description += (
                "\n\nThis will reset all the settings of the AutoMod Module."
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting the AutoMod Module settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.automod.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="AutoMod Module settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(
        name="antinuke",
        help="Reset the settings of the AntiNuke Module",
        aliases=["anti_nuke"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_antinuke(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset AntiNuke",
                description="Are you sure you want to reset the settings of the AntiNuke Module?",
                color=color.green,
            )

            embed.description += (
                "\n\nThis will reset all the settings of the AntiNuke Module."
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting the AntiNuke Module settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.antinuke_settings.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="AntiNuke Module settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(
        name="logging", help="Reset the settings of the Logging Module", aliases=["log"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_logging(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset Logging",
                description="Are you sure you want to reset the settings of the Logging Module?",
                color=color.green,
            )

            embed.description += (
                "\n\nThis will reset all the settings of the Logging Module."
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting the Logging Module settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.guilds_log.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="Logging Module settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(
        name="welcomer",
        help="Reset the settings of the Welcomer Module",
        aliases=["welcome"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_welcomer(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset Welcomer",
                description="Are you sure you want to reset the settings of the Welcomer Module?",
                color=color.green,
            )

            embed.description += (
                "\n\nThis will reset all the settings of the Welcomer Module."
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting the Welcomer Module settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.welcomer_settings.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="Welcomer Module settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(name="ticket", help="Reset the settings of the Ticket System Module")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_ticket(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset Ticket System",
                description="Are you sure you want to reset the settings of the Ticket System Module?",
                color=color.green,
            )

            embed.description += (
                "\n\nThis will reset all the settings of the Ticket System Module."
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting the Ticket System Module settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.ticket.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="Ticket System Module settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @reset.command(name="music", help="Reset the settings of the Music Module")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=120, type=commands.BucketType.guild)
    async def reset_music(self, ctx: commands.Context):

        try:

            if not await checks.check_is_owner(ctx, notify=True):

                return

            embed = discord.Embed(
                title="Reset Music",
                description="Are you sure you want to reset the settings of the Music Module?",
                color=color.green,
            )

            embed.description += (
                "\n\nThis will reset all the settings of the Music Module."
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Resetting the Music Module settings...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await storage.music.delete(guild_id=ctx.guild.id)

                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            description="Music Module settings has been reseted successfully.",
                            color=color.green,
                        )
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Reset Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_group(
        name="premium",
        help="Check if a user has premium",
        aliases=["haspremium"],
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def premium(self, ctx: commands.Context):

        try:

            user_data = self.bot.cache.users.get(str(ctx.author.id))

            if not user_data:

                await storage.users.insert(user_id=ctx.author.id)

                user_data = self.bot.cache.users.get(str(ctx.author.id))

            if not user_data:

                return await ctx.send(
                    embed=discord.Embed(description="An error occured", color=color.red)
                )

            user_data_id = user_data.get("id")

            user_data_user_id = user_data.get("user_id")

            user_data_balance = user_data.get("balance")

            user_data_level = user_data.get("level")

            user_data_type = user_data.get("type")

            user_data_no_prefix = user_data.get("no_prefix")

            user_data_no_prefix_subscription = user_data.get("no_prefix_subscription")

            user_data_no_prefix_end = user_data.get("no_prefix_end")

            user_data_banned = user_data.get("banned")

            user_data_banned_reason = user_data.get("banned_reason")

            user_data_banned_at = user_data.get("banned_at")

            user_data_updated_at = user_data.get("updated_at")

            user_data_created_at = user_data.get("created_at")

            embed = discord.Embed(title="Premium Info", color=color.green)

            embed.description = f"""{self.bot.emoji.NAME} Name: {ctx.author.name}





{self.bot.emoji.ID} ID: {ctx.author.id}











{self.bot.emoji.PREMIUM} Premium: {self.bot.emoji.YES if user_data_no_prefix_subscription else self.bot.emoji.NO}





{self.bot.emoji.EXPIRES} Expires: {f'<t:{int(user_data_no_prefix_end.timestamp())}:R>' if user_data_no_prefix_end else '`Never`'}"""

            embed.set_footer(
                text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url
            )

            embed.set_thumbnail(url=ctx.author.display_avatar.url)

            view = discord.ui.View()

            buy_button = discord.ui.Button(
                label="Buy Premium",
                emoji=self.bot.emoji.BUY,
                style=discord.ButtonStyle.link,
                url=self.bot.urls.SUPPORT_SERVER,
            )

            view.add_item(buy_button)

            await ctx.send(embed=embed, view=view)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @premium.command(
        name="server", help="Check if The Server has premium", aliases=["guild"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def premium_server(self, ctx: commands.Context):

        try:

            guild_data = self.bot.cache.guilds.get(str(ctx.guild.id), {})

            if not guild_data:

                await storage.guilds.insert(guild_id=ctx.guild.id)

                guild_data = self.bot.cache.guilds.get(str(ctx.guild.id), {})

            subscription = guild_data.get("subscription", "free")

            subscription_end = guild_data.get("subscription_end")

            embed = discord.Embed(title="Server Premium Info", color=color.green)

            embed.description = f"""{self.bot.emoji.NAME} Name: {ctx.guild.name}





{self.bot.emoji.ID} ID: {ctx.guild.id}











{self.bot.emoji.PREMIUM} Premium: `{subscription.capitalize().replace('_',' ') if subscription else 'Free'}`





{self.bot.emoji.EXPIRES} Expires: {f'<t:{int(subscription_end.timestamp())}:R>' if subscription_end else '`Never`'}"""

            embed.set_footer(
                text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url
            )

            embed.set_thumbnail(
                url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                )
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.command(name="nuke", help="Nuke a Text Channel")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=300, type=commands.BucketType.guild)
    async def nuke(self, ctx: commands.Context, channel: discord.TextChannel = None):

        try:

            if not channel:

                channel = ctx.channel

            if not await checks.check_is_moderator_permissions(ctx, "administrator"):

                return

            embed = discord.Embed(
                description=f"Are you sure you want to nuke {channel.mention}?",
                color=color.red,
            )

            view = discord.ui.View(timeout=60)

            confirmed = False

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.success,
                emoji=self.bot.emoji.YES,
                row=0,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                emoji=self.bot.emoji.NO,
                row=0,
            )

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            message = await ctx.send(embed=embed, view=view)

            async def yes_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description=f"Nuking {channel.mention}...",
                            color=color.green,
                        ),
                        view=None,
                    )

                    await channel.delete()

                    new_channel = await ctx.guild.create_text_channel(
                        name=channel.name,
                        category=channel.category,
                        position=channel.position,
                        overwrites=channel.overwrites,
                        topic=channel.topic,
                        nsfw=channel.is_nsfw(),
                        slowmode_delay=channel.slowmode_delay,
                        reason=f"Nuked by {ctx.author}",
                    )

                    await new_channel.send(f"{ctx.author.mention} Nuked The Channel.")

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            async def no_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal confirmed

                    confirmed = True

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Nuke Cancled", color=color.red
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[0][1])}: {e}"
                    )

            await asyncio.sleep(60)

            if not confirmed:

                for item in view.children:

                    item.disabled = True

                await message.edit(view=view)

                return

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_command(
        name="vccontrol", help="Control remote for a J2C VC", aliases=["vccontrolpanel"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def vccontrol(self, ctx: commands.Context):

        try:

            if not cache.j2c.get(str(ctx.channel.id), {}):

                return await ctx.send(
                    embed=discord.Embed(
                        description="This is not a J2C VC", color=color.red
                    )
                )

            if not ctx.author.voice:

                return await ctx.send(
                    embed=discord.Embed(
                        description="You are not in a voice channel", color=color.red
                    )
                )

            if ctx.author.voice.channel.id != ctx.channel.id:

                return await ctx.send(
                    embed=discord.Embed(
                        description="You are not in the J2C VC", color=color.red
                    )
                )

            if cache.j2c.get(str(ctx.channel.id), {}).get("owner_id") != ctx.author.id:

                return await ctx.send(
                    embed=discord.Embed(
                        description="You are not the owner of this J2C VC",
                        color=color.red,
                    )
                )

            j2c_data = cache.j2c.get(str(ctx.channel.id), {})

            if ctx.interaction:

                await ctx.interaction.response.defer()

            try:

                controller_message = (
                    await ctx.channel.fetch_message(
                        j2c_data.get("controller_message_id")
                    )
                    if j2c_data.get("controller_message_id")
                    else None
                )

            except:

                controller_message = None

            if controller_message:

                await controller_message.delete()

            await j2c_controller.controller_module(
                self.bot, data=j2c_data, channel=ctx.channel
            )

            if ctx.interaction:

                await ctx.interaction.delete_original_response()

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
