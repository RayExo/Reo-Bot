import discord


from discord.ext import commands


import asyncio


import os, sys


from io import BytesIO


import traceback, sys


import wavelink


import datetime


import discord.http


from reo.src.checks import checks


import storage.ban_data


import storage.redeem_codes


import storage.users


from reo.console.logging import logger


from reo.style import color


from reo.utils import pings


from reo.workflows.cache import load_cache


from reo.console.generator import generate_redeem_code


from reo.utils.generate import generate_directory_tree_string_split_text


import storage


import traceback, sys


from io import StringIO


import textwrap


from contextlib import redirect_stdout


from reo.engine.Bot import AutoShardedBot


from reo.config.config import Types


from reo.style import emoji


redeem_code_types = Types.redeem_code_types


from reo.workflows.actions import change_user_subscription


def get_formatted_balance(balance: int) -> str:

    # Format balance with suffixes like 1m, 1k, 1b with max 1 decimal if needed

    if balance >= 1_000_000_000:

        formatted = balance / 1_000_000_000

        suffix = "b"

    elif balance >= 1_000_000:

        formatted = balance / 1_000_000

        suffix = "m"

    elif balance >= 1_000:

        formatted = balance / 1_000

        suffix = "k"

    else:

        return str(balance)

    # Check if the decimal part is zero

    if formatted.is_integer():

        return f"{int(formatted)}{suffix}"

    else:

        return f"{formatted:.1f}{suffix}"


class Root(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Root"

            category = "Extra"

            description = "Root Commands"

            hidden = True

            emoji = bot.emoji.ROOT

        self.cog_info = cog_info

    @commands.group(
        name="root", help="Root Commands", hidden=True, invoke_without_command=True
    )
    @checks.is_owner()
    async def root(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                title="Root Commands",
                description="Here are the list of root commands\n",
                color=color.blue,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}\n"

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @root.command(name="reload", help="Reloads all src units", hidden=True)
    async def reload(self, ctx: commands.Context, name: str = None):

        if not name:

            reloading_embed = discord.Embed(title="Reloading", color=color.orange)

            reloading_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            reloading_embed.set_footer(
                text="REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            message = await ctx.send(embed=reloading_embed)

            commands_cogs = [
                cog
                for cog in self.bot.cogs.values()
                if hasattr(cog, "get_commands") and cog.get_commands()
            ]

            events_cogs = [
                cog
                for cog in self.bot.cogs.values()
                if hasattr(cog, "get_listeners") and cog.get_listeners()
            ]

            await self.bot.reload()

            await self.bot.reload_extension("reo.src")

            commands_cogs_text = "\n".join(
                [str(cog.__class__.__name__).capitalize() for cog in commands_cogs]
            )

            events_cogs_text = "\n".join(
                [str(cog.__class__.__name__).capitalize() for cog in events_cogs]
            )

            reloading_embed.add_field(
                name="__Command Units:__",
                value=f"```prolog\n{commands_cogs_text}```",
                inline=True,
            )

            reloading_embed.add_field(
                name="__Event Units:__",
                value=f"```prolog\n{events_cogs_text}```",
                inline=True,
            )

            reloading_embed.title = "Successfully Reloaded REO Src"

            reloading_embed.description = (
                f"\n\n**__Bot Ping:__** `{pings.bot(self.bot)}ms`"
            )

            reloading_embed.description += (
                f"\n**__Storage Ping:__** `{await pings.database()}ms`"
            )

            reloading_embed.description += f"\n**__Cache Ping:__** `{pings.cache()}ms`"

            reloading_embed.description += (
                f"\n\n**{self.bot.emoji.LOADING} Reloading Tree**"
            )

            reloading_embed.set_footer(
                text="REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            await message.edit(embed=reloading_embed)

            await self.bot.tree.sync()

            reloading_embed.description = reloading_embed.description.replace(
                f"\n\n**{self.bot.emoji.LOADING} Reloading Tree**",
                f"\n\n**{self.bot.emoji.SUCCESS} Tree Synced**",
            )

            await message.edit(embed=reloading_embed)

        else:

            valid_types = ["cache"]

            if name.lower() not in valid_types:

                return await ctx.send(
                    f"Invalid Type: `{name}`. Valid Types: `{'/'.join(valid_types)}`.",
                    delete_after=10,
                )

            reloading_embed = discord.Embed(
                title="Reloading",
                description=f"Reloading {name} data",
                color=color.yellow,
            )

            reloading_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            reloading_embed.set_footer(
                text=f"Reloading requested by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )

            message = await ctx.send(embed=reloading_embed)

            if name.lower() == "cache":

                await load_cache()

                reloading_embed.title = "Successfully Reloaded Cache"

                reloading_embed.description = f"Succesfully reloaded cache data.\n\n**Bot Ping:** `{pings.bot(self.bot)}ms`"

                await message.edit(embed=reloading_embed)

            else:

                await message.edit(embed=reloading_embed)

    @root.command(name="restart", help="Restarts the bot", hidden=True)
    @checks.is_owner()
    async def restart(self, ctx: commands.Context):

        confirmation_embed = discord.Embed(
            title=f"Need Confirmation",
            description=f"Do you want to restart the bot?",
            color=color.yellow,
        )

        confirmation_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        confirmation_embed.set_footer(
            text=f"Restart requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url,
        )

        view_timeout = 60

        cancled = False

        def get_view(disabled=False):

            view = discord.ui.View(timeout=60)

            yes_button = discord.ui.Button(
                label="Yes",
                style=discord.ButtonStyle.green,
                disabled=disabled,
                emoji="☑",
            )

            no_button = discord.ui.Button(
                label="No",
                style=discord.ButtonStyle.gray,
                disabled=disabled,
                emoji=self.bot.emoji.NO,
            )

            yes_button.callback = lambda i: yes_button_callback(i)

            no_button.callback = lambda i: no_button_callback(i)

            view.add_item(yes_button)

            view.add_item(no_button)

            return view

        async def yes_button_callback(interaction: discord.Interaction):

            if interaction.user.id != ctx.author.id:

                return await interaction.response.send_message(
                    "You are not allowed to use this Interaction.", ephemeral=True
                )

            nonlocal cancled

            cancled = True

            embed = discord.Embed(
                title="Restarted", description="Restarted the bot.", color=color.green
            )

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            embed.set_footer(
                text=f"Restarted by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )

            await interaction.response.edit_message(embed=embed, view=None)

            def restart_bot():

                # Restart the bot

                os.execl(sys.executable, sys.executable, *sys.argv)

            restart_bot()

        async def no_button_callback(interaction: discord.Interaction):

            if interaction.user.id != ctx.author.id:

                return await interaction.response.send_message(
                    "You are not allowed to use this Interaction.", ephemeral=True
                )

            nonlocal cancled

            cancled = True

            embed = discord.Embed(
                title="Canceled", description="Canceled the restart.", color=color.red
            )

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            embed.set_footer(
                text=f"Restart canceled by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )

            await interaction.response.edit_message(embed=embed, view=None)

        message = await ctx.send(embed=confirmation_embed, view=get_view())

        while True:

            if cancled:

                break

            if view_timeout <= 0:

                await message.edit(view=get_view(True))

                break

            view_timeout -= 1

            await asyncio.sleep(1)

    @root.command(
        name="shutdown",
        help="Shuts down the bot",
        hidden=True,
        aliases=["shut", "stop"],
    )
    @checks.is_owner()
    async def shutdown(self, ctx: commands.Context):

        shutted_down_embed = discord.Embed(
            title="Shutting Down", description="Shutting down the bot.", color=color.red
        )

        shutted_down_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        shutted_down_embed.set_footer(
            text=f"Shutdown requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=shutted_down_embed)

        def shutdown_bot():

            sys.exit()

        shutdown_bot()

    @root.command(name="logs", help="Shows the last 50 list of logs", hidden=True)
    @checks.is_owner()
    async def logs(self, ctx: commands.Context):

        log_folder = os.path.join(os.getcwd(), "logs")

        logs = [str(log) for log in os.listdir(log_folder)]

        logs = logs[-50:]

        logs_text = "\n".join(logs)

        logs_embed = discord.Embed(
            title="Last 50 Logs List",
            description=f"```prolog\n{logs_text}```",
            color=color.blue,
        )

        logs_embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        logs_embed.set_footer(
            text=f"Logs requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=logs_embed)

    @root.command(name="log", help="Shows the content of a log file", hidden=True)
    @checks.is_owner()
    async def log(self, ctx: commands.Context, *, filename: str = None):

        try:

            if filename:

                file_path = f"logs/{filename}"

            else:

                file_path = logger.logging_file

                filename = os.path.basename(logger.logging_file)

            if not os.path.exists(file_path):

                return await ctx.reply(f"Log file `{filename}` doesn't exist.")

            # Check file size

            file_size = os.path.getsize(file_path)

            max_size = 25 * 1024 * 1024  # 8 MB

            if file_size > max_size:

                return await ctx.reply(
                    f"File `{filename}` is too large to upload. Maximum size is 25 MB. Please download the file and view from the host."
                )

            # Read the file content into a BytesIO object

            with open(file_path, "rb") as file_data:

                file_bytes = BytesIO(file_data.read())

            # Reset the BytesIO cursor to the beginning of the stream

            file_bytes.seek(0)

            # Create a discord.File object using the BytesIO stream

            file = discord.File(fp=file_bytes, filename=filename)

            # Send the file in the response

            await ctx.send(file=file)

        except Exception as e:

            await ctx.send(f"Error: {e}")

    @root.command(name="ping", help="Shows all kinds of pings", hidden=True)
    @checks.is_owner()
    async def root_ping(self, ctx: commands.Context):

        try:

            # send ping snapshots for the bot runtime and surface endpoint

            message = await ctx.send(
                embed=discord.Embed(
                    title="Pinging", description="Pinging...", color=color.orange
                )
            )

            for i in range(10):

                try:

                    def get_shard_guilds_count(shard_id):

                        try:

                            return len(
                                [
                                    guild
                                    for guild in self.bot.guilds
                                    if guild.shard_id == int(shard_id)
                                ]
                            )

                        except:

                            return 0

                    shards_text = "\n**__Shards Ping:__**\n"

                    shards_text += "\n".join(
                        [
                            f"**Shard {shard} Ping:** `{ping}ms` ({get_shard_guilds_count(shard)})"
                            for shard, ping in pings.shards(self.bot).items()
                        ]
                    )

                    embed = discord.Embed(
                        title="Pings",
                        description=f"**Bot Ping:** `{pings.bot(self.bot)}ms`\n"
                        f"**Storage Ping:** `{await pings.storage()}ms`\n"
                        f"**Cache Ping:** `{pings.cache()}ms`\n"
                        f"**Surface Ping:** `{pings.surface()}ms`\n"
                        f"{shards_text}",
                        color=color.blue,
                    )

                    embed.set_footer(
                        text=f"Updated {i+1}/10" if i < 9 else "Finished",
                    )

                    await message.edit(embed=embed)

                    await asyncio.sleep(3)

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

        except Exception as e:

            await ctx.send(
                embed=discord.Embed(
                    description=f"An Error occurred while pinging: {e}", color=color.red
                ),
                delete_after=10,
            )

    @commands.command(
        name="generate",
        help="Generates different types of redeemable codes",
        hidden=True,
    )
    @checks.is_owner()
    async def generate(self, ctx: commands.Context):

        try:

            selected_code_type = None

            code_validity = None

            code_expires_at = datetime.datetime.now() + datetime.timedelta(days=30)

            async def get_embed():

                embed = discord.Embed(
                    title="Generate Redeem Code", description="", color=color.blue
                )

                embed.description += f"**Selected Code Type:** `{redeem_code_types[selected_code_type] if selected_code_type else 'Undefined'}`\n"

                # make code validity like 300 days

                # it will make it formated like 1 year 2 months 3 days

                if code_validity == 0:

                    code_validity_text = "Unlimited"

                elif code_validity:

                    code_validity_text = f"{code_validity} Days"

                else:

                    code_validity_text = "Not Set"

                embed.description += f"**Code Validity:** `{code_validity_text}`\n"

                embed.description += (
                    f"**Code Expires:** <t:{int(code_expires_at.timestamp())}:R>\n"
                )

                embed.set_thumbnail(url=self.bot.user.display_avatar.url)

                embed.set_footer(
                    text=f"Generate Redeem Code requested by {ctx.author}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            timeout_time = 120

            def reset_timeout(timeout: int = 120):

                nonlocal timeout_time

                timeout_time = timeout

            cancled = False

            async def get_view(disabled=False):

                reset_timeout()

                view = discord.ui.View(timeout=120)

                select_code_type = discord.ui.Select(
                    placeholder="Select Redeem Code Type",
                    options=[
                        discord.SelectOption(
                            label=value,
                            value=key,
                            emoji=self.bot.emoji.PREMIUM,
                            description=f"Generate {value} Redeem Code",
                            default=True if key == selected_code_type else False,
                        )
                        for key, value in redeem_code_types.items()
                    ],
                    row=0,
                )

                select_code_type.callback = lambda i: select_code_type_callback(i)

                view.add_item(select_code_type)

                valid_for_days_button = discord.ui.Button(
                    label="Set Code Validity",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.TIME,
                    row=1,
                )

                valid_for_days_button.callback = (
                    lambda i: valid_for_days_button_callback(i)
                )

                view.add_item(valid_for_days_button)

                generate_button = discord.ui.Button(
                    label="Generate",
                    style=discord.ButtonStyle.green,
                    emoji=self.bot.emoji.CREATE,
                    row=1,
                )

                generate_button.callback = lambda i: generate_button_callback(i)

                if code_validity == None or not selected_code_type:

                    generate_button.disabled = True

                view.add_item(generate_button)

                cancle_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.CANCLED,
                    row=2,
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(cancle_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def select_code_type_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal selected_code_type

                    selected_code_type = interaction.data["values"][0]

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def valid_for_days_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    class code_validity_modal(
                        discord.ui.Modal, title="Set Code Validity"
                    ):

                        new_code_validity = discord.ui.TextInput(
                            label="Enter Code Validity in Days",
                            placeholder="Enter Code Validity in Days",
                            min_length=1,
                            required=True,
                            default=(
                                str(code_validity)
                                if (code_validity or code_validity == 0)
                                else "30"
                            ),
                        )

                        async def on_submit(self, interaction: discord.Interaction):

                            if interaction.user.id != ctx.author.id:

                                return await interaction.response.send_message(
                                    embed=discord.Embed(
                                        description="You are not allowed to use this Interaction.",
                                        color=color.red,
                                    ),
                                    ephemeral=True,
                                    delete_after=10,
                                )

                            nonlocal code_validity

                            if (
                                not self.new_code_validity.value == ""
                                and not self.new_code_validity.value.isdigit()
                            ):

                                return await interaction.response.send_message(
                                    embed=discord.Embed(
                                        description="Invalid Input. Please enter a valid number.",
                                        color=color.red,
                                    ),
                                    ephemeral=True,
                                    delete_after=10,
                                )

                            code_validity = int(
                                self.new_code_validity.value
                                if self.new_code_validity.value != ""
                                else 0
                            )

                            await interaction.response.edit_message(
                                embed=await get_embed(), view=await get_view()
                            )

                    await interaction.response.send_modal(code_validity_modal())

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def generate_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You are not allowed to use this Interaction.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.defer()

                    code = generate_redeem_code()

                    try:

                        await storage.redeem_codes.insert(
                            code=code,
                            code_type="subscription",
                            code_value=selected_code_type,
                            valid_for_days=(
                                None if code_validity == 0 else code_validity
                            ),
                            expires_at=code_expires_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
                            claimed=False,
                            claimed_by=None,
                            claimed_at=None,
                        )

                        await interaction.followup.send(
                            embed=discord.Embed(
                                title="Generated Redeem Code",
                                description=f"**||```prolog\n{code}```||**",
                                color=color.green,
                            ),
                            ephemeral=True,
                        )

                        await interaction.message.delete()

                        try:

                            await interaction.user.send(
                                content=f"Redeem Code For **`{redeem_code_types[selected_code_type]}`**",
                                embed=discord.Embed(
                                    title="Generated Redeem Code",
                                    description=f"**||```prolog\n{code}```||**",
                                    color=color.green,
                                ),
                            )

                        except:

                            pass

                    except Exception as e:

                        await interaction.followup.send(
                            embed=discord.Embed(
                                description=f"Failed to generate redeem code: {e}",
                                color=color.red,
                            ),
                            ephemeral=True,
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
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view(True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                if timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                timeout_time -= 1

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.group(
        name="blacklist",
        help="Blacklist Users/Guilds",
        hidden=True,
        invoke_without_command=True,
    )
    @checks.is_owner()
    async def blacklist(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                title="Blacklist Commands",
                description="Here are the list of blacklist commands\n",
                color=color.blue,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` - {command.help}\n"

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @blacklist.group(
        name="user", help="Blacklist Users", hidden=True, invoke_without_command=True
    )
    @checks.is_owner()
    async def blacklist_user(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                title="Blacklist User Commands",
                description="Here are the list of blacklist user commands\n",
                color=color.blue,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"`{self.bot.BotConfig.PREFIX}{ctx.command.parent.name} {ctx.command.name} {command.name}` - {command.help}\n"

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @blacklist_user.command(name="add", help="Blacklist a User", hidden=True)
    @checks.is_owner()
    async def blacklist_user_add(self, ctx: commands.Context, user: discord.User):

        try:

            if str(user.id) in self.bot.cache.ban_data.get("users", {}):

                return await ctx.send(f"User is already blacklisted.")

            await storage.ban_data.insert(
                user_id=user.id,
            )

            await ctx.send(f"User is blacklisted.")

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @blacklist_user.command(name="remove", help="Unblacklist a User", hidden=True)
    @checks.is_owner()
    async def blacklist_user_remove(self, ctx: commands.Context, user: discord.User):

        try:

            if str(user.id) not in self.bot.cache.ban_data.get("users", {}):

                return await ctx.send(f"User is not blacklisted.")

            await storage.ban_data.delete(
                user_id=user.id,
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"User is unblacklisted.", color=color.green
                )
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @blacklist_user.command(name="list", help="List Blacklisted Users", hidden=True)
    @checks.is_owner()
    async def blacklist_user_list(self, ctx: commands.Context):

        try:

            blacklisted_users = self.bot.cache.ban_data.get("users", {})

            if not blacklisted_users:

                return await ctx.send(
                    embed=discord.Embed(
                        description="No users are blacklisted", color=color.red
                    ),
                    delete_after=10,
                )

            blacklisted_users = list(blacklisted_users.keys())

            # make blacklisted_users 5 by 5 list

            blacklisted_users = [
                blacklisted_users[i : i + 5]
                for i in range(0, len(blacklisted_users), 5)
            ]

            current_page_index = 0

            view_timeout = 60

            cancled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 60

            async def get_embed():

                nonlocal blacklisted_users, current_page_index

                embed = discord.Embed(
                    title="Blacklisted Users", color=color.random_color()
                )

                embed.description = ", ".join(
                    [
                        f"<@{user_id}>"
                        for user_id in blacklisted_users[current_page_index]
                    ]
                )

                embed.set_footer(
                    text=f"Page {current_page_index+1}/{len(blacklisted_users)}"
                )

                return embed

            async def get_view(disabled=False):

                nonlocal view_timeout

                reset_view_timeout()

                view = discord.ui.View()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    emoji=self.bot.emoji.STOP,
                    row=0,
                    disabled=len(blacklisted_users) == 1,
                )

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(blacklisted_users) - 1,
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

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout -= 1

                if view_timeout <= 0:

                    await message.edit(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                embed=discord.Embed(
                    description="An Error occurred while listing blacklisted users",
                    color=color.red,
                ),
                delete_after=10,
            )

    @blacklist.group(
        name="guild", help="Blacklist Guilds", hidden=True, invoke_without_command=True
    )
    @checks.is_owner()
    async def blacklist_guild(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                title="Blacklist Guild Commands",
                description="Here are the list of blacklist guild commands\n",
                color=color.blue,
            )

            if hasattr(ctx.command, "commands"):

                for command in ctx.command.commands:

                    embed.description += f"`{self.bot.BotConfig.PREFIX}{ctx.command.parent.name} {ctx.command.name} {command.name}` - {command.help}\n"

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @blacklist_guild.command(name="add", help="Blacklist a Guild", hidden=True)
    @checks.is_owner()
    async def blacklist_guild_add(self, ctx: commands.Context, guild: discord.Guild):

        try:

            if str(guild.id) in self.bot.cache.ban_data.get("guilds", {}):

                return await ctx.send(f"Guild is already blacklisted.")

            await storage.ban_data.insert(
                guild_id=guild.id,
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"Guild is blacklisted.", color=color.green
                )
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @blacklist_guild.command(name="remove", help="Unblacklist a Guild", hidden=True)
    @checks.is_owner()
    async def blacklist_guild_remove(self, ctx: commands.Context, guild: discord.Guild):

        try:

            if str(guild.id) not in self.bot.cache.ban_data.get("guilds", {}):

                return await ctx.send(f"Guild is not blacklisted.")

            await storage.ban_data.delete(
                guild_id=guild.id,
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"Guild is unblacklisted.", color=color.green
                )
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @blacklist_guild.command(name="list", help="List Blacklisted Guilds", hidden=True)
    @checks.is_owner()
    async def blacklist_guild_list(self, ctx: commands.Context):

        try:

            blacklisted_guilds = self.bot.cache.ban_data.get("guilds", {})

            if not blacklisted_guilds:

                return await ctx.send(
                    embed=discord.Embed(
                        description="No guilds are blacklisted", color=color.red
                    ),
                    delete_after=10,
                )

            blacklisted_guilds = list(blacklisted_guilds.keys())

            # make blacklisted_guilds 5 by 5 list

            blacklisted_guilds = [
                blacklisted_guilds[i : i + 5]
                for i in range(0, len(blacklisted_guilds), 5)
            ]

            current_page_index = 0

            view_timeout = 60

            cancled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 60

            async def get_embed():

                nonlocal blacklisted_guilds, current_page_index

                embed = discord.Embed(
                    title="Blacklisted Guilds", color=color.random_color()
                )

                embed.description = ", ".join(
                    [
                        f"<@{guild_id}>"
                        for guild_id in blacklisted_guilds[current_page_index]
                    ]
                )

                embed.set_footer(
                    text=f"Page {current_page_index+1}/{len(blacklisted_guilds)}"
                )

                return embed

            async def get_view(disabled=False):

                nonlocal view_timeout

                reset_view_timeout()

                view = discord.ui.View()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    emoji=self.bot.emoji.STOP,
                    row=0,
                    disabled=len(blacklisted_guilds) == 1,
                )

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(blacklisted_guilds) - 1,
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

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout -= 1

                if view_timeout <= 0:

                    await message.edit(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                embed=discord.Embed(
                    description="An Error occurred while listing blacklisted guilds",
                    color=color.red,
                ),
                delete_after=10,
            )

    @blacklist.command(name="list", help="List Blacklisted Users/Guilds", hidden=True)
    @checks.is_owner()
    async def blacklist_list(self, ctx: commands.Context):

        try:

            blacklisted_users = self.bot.cache.ban_data.get("users", {})

            blacklisted_guilds = self.bot.cache.ban_data.get("guilds", {})

            if not blacklisted_users and not blacklisted_guilds:

                return await ctx.send(
                    embed=discord.Embed(
                        description="No users/guilds are blacklisted", color=color.red
                    ),
                    delete_after=10,
                )

            blacklisted_users = list(blacklisted_users.keys())

            blacklisted_guilds = list(blacklisted_guilds.keys())

            # make blacklisted_users 5 by 5 list

            blacklisted_users = [
                blacklisted_users[i : i + 5]
                for i in range(0, len(blacklisted_users), 5)
            ]

            blacklisted_guilds = [
                blacklisted_guilds[i : i + 5]
                for i in range(0, len(blacklisted_guilds), 5)
            ]

            current_page_index = 0

            view_timeout = 60

            cancled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 60

            async def get_embed():

                nonlocal blacklisted_users, blacklisted_guilds, current_page_index

                embed = discord.Embed(
                    title="Blacklisted Users/Guilds", color=color.random_color()
                )

                embed.description = f"**Users:**\n"

                embed.description += ", ".join(
                    [
                        f"<@{user_id}>"
                        for user_id in blacklisted_users[current_page_index]
                    ]
                )

                embed.description += f"\n\n**Guilds:**\n"

                embed.description += ", ".join(
                    [
                        f"<@{guild_id}>"
                        for guild_id in blacklisted_guilds[current_page_index]
                    ]
                )

                embed.set_footer(
                    text=f"Page {current_page_index+1}/{len(blacklisted_users)}"
                )

                return embed

            async def get_view(disabled=False):

                nonlocal view_timeout

                reset_view_timeout()

                view = discord.ui.View()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    emoji=self.bot.emoji.STOP,
                    row=0,
                    disabled=len(blacklisted_users) == 1,
                )

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(blacklisted_users) - 1,
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

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout -= 1

                if view_timeout <= 0:

                    await message.edit(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                embed=discord.Embed(
                    description="An Error occurred while listing blacklisted users/guilds",
                    color=color.red,
                ),
                delete_after=10,
            )

    @root.command(name="tree", help="Shows the tree of code", hidden=True)
    @checks.is_owner()
    async def tree(self, ctx: commands.Context):

        try:

            tree_string_chunks = generate_directory_tree_string_split_text(1950)

            for message in tree_string_chunks:

                await ctx.send(f"```prolog\n{message}```")

        except Exception as e:

            await ctx.send(f"Error: {e}")

    @root.command(name="server", help="Shows the server info", hidden=True)
    @checks.is_owner()
    async def server(self, ctx: commands.Context, guild: discord.Guild):

        try:

            if not guild:

                return await ctx.send(
                    embed=discord.Embed(description="Guild not found", color=color.red),
                    delete_after=10,
                )

            total_member_in_vc = 0

            for channel in guild.voice_channels:

                total_member_in_vc += len(
                    [member for member in channel.members if not member.bot]
                )

            embed = discord.Embed(title=f"Server Info", color=color.random_color())

            invite_text = (
                f"\n> Invite: [Click Here]({guild.vanity_url})"
                if guild.vanity_url
                else ""
            )

            members_in_vc_text = (
                f"\n> Members in VC: `{total_member_in_vc}`"
                if total_member_in_vc
                else ""
            )

            guild_subscription = str(
                self.bot.cache.guilds.get(str(guild.id), {}).get("subscription", "Free")
            ).capitalize()

            embed.add_field(
                name=f"{guild.name}",
                value=(
                    f"> Members: {len(guild.members)}\n"
                    f"> ID: {guild.id}\n"
                    f"> Has Admin: `{guild.me.guild_permissions.administrator}`\n"
                    f"> Subscription: `{guild_subscription}`"
                    f"{invite_text}"
                    f"{members_in_vc_text}"
                ),
                inline=True,
            )

            embed.set_thumbnail(
                url=guild.icon.url if guild.icon else guild.me.display_avatar.url
            )

            await ctx.send(embed=embed)

        except Exception as e:

            await ctx.send(f"Error: {e}")

    @root.command(
        name="servers", help="Shows the list of servers the bot is in", hidden=True
    )
    @checks.is_owner()
    async def servers(self, ctx: commands.Context):

        try:

            # make guilds 5 by 5 list

            high_to_low = lambda x: len(x.members)

            guilds = sorted(self.bot.guilds, key=high_to_low, reverse=True)

            all_guilds = [guilds[i : i + 20] for i in range(0, len(guilds), 20)]

            current_page_index = 0

            view_timeout = 120

            cancled = False

            def reset_view_timeout():

                nonlocal view_timeout

                view_timeout = 120

            async def get_embed():

                embed = discord.Embed(
                    title=f"Total Servers ({len(guilds)})", color=color.random_color()
                )

                guilds_data = all_guilds[current_page_index]

                for guild in guilds_data:

                    total_member_in_vc = 0

                    for channel in guild.voice_channels:

                        total_member_in_vc += len(
                            [member for member in channel.members if not member.bot]
                        )

                    invite_text = (
                        f"\n> Invite: [Click Here]({guild.vanity_url})"
                        if guild.vanity_url
                        else ""
                    )

                    members_in_vc_text = (
                        f"\n> Members in VC: `{total_member_in_vc}`"
                        if total_member_in_vc
                        else ""
                    )

                    guild_subscription = str(
                        self.bot.cache.guilds.get(str(guild.id), {}).get(
                            "subscription", "Free"
                        )
                    ).capitalize()

                    embed.add_field(
                        name=f"{guild.name}",
                        value=(
                            f"> Members: {len(guild.members)}\n"
                            f"> ID: {guild.id}\n"
                            f"> Has Admin: `{guild.me.guild_permissions.administrator}`\n"
                            f"> Subscription: `{guild_subscription}`"
                            f"{invite_text}"
                            f"{members_in_vc_text}"
                        ),
                        inline=True,
                    )

                embed.set_footer(text=f"Page {current_page_index+1}/{len(all_guilds)}")

                return embed

            async def get_view(disabled=False):

                nonlocal view_timeout

                reset_view_timeout()

                view = discord.ui.View()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.danger,
                    emoji=self.bot.emoji.STOP,
                    row=0,
                    disabled=len(all_guilds) == 1,
                )

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(all_guilds) - 1,
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

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def stop_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout -= 1

                if view_timeout <= 0:

                    await message.edit(
                        embed=await get_embed(), view=await get_view(disabled=True)
                    )

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @root.command(
        name="leaveserver", help="Leaves a server", hidden=True, aliases=["leaveguild"]
    )
    @checks.is_owner()
    async def leaveserver(self, ctx: commands.Context, guild_id: int):

        try:

            guild = await self.bot.fetch_guild(guild_id)

            if not guild:

                return await ctx.send(
                    embed=discord.Embed(description="Guild not found", color=color.red),
                    delete_after=10,
                )

            await guild.leave()

            await ctx.send(
                embed=discord.Embed(
                    description=f"Left the server **{guild.name}**", color=color.green
                )
            )

        except Exception as e:

            await ctx.send(f"Error: {e}")

    @root.command(
        name="serverinvite",
        help="Generates a server invite",
        hidden=True,
        aliases=["serverinv", "serverlink"],
    )
    @checks.is_owner()
    async def serverinvite(self, ctx: commands.Context, guild_id: int):

        try:

            guild = await self.bot.fetch_guild(guild_id)

            if not guild:

                return await ctx.send(
                    embed=discord.Embed(description="Guild not found", color=color.red),
                    delete_after=10,
                )

            if not guild.vanity_url:

                channels = await guild.fetch_channels()

                channels = [
                    channel
                    for channel in channels
                    if isinstance(channel, discord.TextChannel)
                ]

                invite = await channels[0].create_invite()

                invite = invite.url

            else:

                invite = guild.vanity_url

            await ctx.send(
                embed=discord.Embed(
                    description=f"**{guild.name}** Invite: {invite}", color=color.green
                )
            )

        except Exception as e:

            await ctx.send(f"Error: {e}")

    @root.command(
        name="python", help="Executes a python code", hidden=True, aliases=["py"]
    )
    @checks.is_owner()
    async def python(self, ctx: commands.Context, *, code: str):

        try:

            # Remove code block formatting

            code = code.replace("```", "").replace("py", "").strip()

            # Prepare the environment

            env = {
                "ctx": ctx,
                "bot": self.bot,
                "discord": discord,
                "commands": commands,
                "__import__": __import__,
            }

            # Capture the output

            stdout = StringIO()

            # Define the code execution

            exec_code = f'async def _exec(ctx):\n{textwrap.indent(code, "    ")}'

            # Compile and execute the code

            exec(exec_code, env)

            async def run_code():

                with redirect_stdout(stdout):

                    await env["_exec"](ctx)

            # Run the code with a timeout (max 5 seconds)

            await asyncio.wait_for(run_code(), timeout=5)

            # Output the result

            result = stdout.getvalue()

            if result:

                await ctx.send(f"```\n{result}\n```")

            else:

                await ctx.send("`No output.`")

        except asyncio.TimeoutError:

            await ctx.send("Error: Code execution took too long (max 5s).")

        except Exception as e:

            await ctx.send(f"Error: {e}")

    @root.command(
        name="emojis", help="Shows the list of emojis the bot has", hidden=True
    )
    @checks.is_owner()
    async def emojis(self, ctx: commands.Context):

        try:

            from reo.style import emoji

            # get all the variables from emoji.py

            emoji_vars = [var for var in dir(emoji) if not var.startswith("__")]

            # sort them by alphabetical order

            emoji_vars = sorted(emoji_vars)

            # make emoji_vars 5 by 5 list

            emoji_vars = [emoji_vars[i : i + 1] for i in range(0, len(emoji_vars), 1)]

            # make 20 by 20 emoji_vars

            sorted_emoji_vars = [
                emoji_vars[i : i + 20] for i in range(0, len(emoji_vars), 20)
            ]

            for emoji_vars in sorted_emoji_vars:

                # name it like emoji - emoji1 | emoji - emoji2 | emoji - emoji3

                emoji_vars = [
                    f" | ".join([f"{var} : {getattr(emoji,var)}" for var in emoji_var])
                    for emoji_var in emoji_vars
                ]

                await ctx.send(
                    embed=discord.Embed(
                        description="\n".join(emoji_vars), color=color.random_color()
                    )
                )

        except Exception as e:

            await ctx.send(f"Error: {e}")

    @root.command(
        name="givebalance",
        help="Gives balance to a user",
        aliases=["givebal", "givecoins", "givecoin"],
        hidden=True,
    )
    @checks.is_owner()
    async def givebalance(self, ctx: commands.Context, user: discord.User, amount: int):

        try:

            message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Giving balance...",
                    color=color.orange,
                )
            )

            if amount < 0:

                return await message.edit(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | Amount cannot be negative",
                        color=color.red,
                    )
                )

            user_data = self.bot.cache.users.get(str(user.id), {})

            if not user_data:

                user_data = await storage.users.get(id=user.id)

            user_data = self.bot.cache.users.get(str(user.id), {})

            await storage.users.update(
                id=self.bot.cache.users.get(str(user.id), {}).get("id"),
                balance=self.bot.cache.users.get(str(user.id), {}).get("balance", 0)
                + amount,
            )

            await message.edit(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.SUCCESS} | {user.display_name} | Current Balance: `{get_formatted_balance(self.bot.cache.users.get(str(user.id),{}).get('balance',0))}`{self.bot.emoji.COIN}",
                    color=color.green,
                )
            )

        except Exception as e:

            await message.edit(
                embed=discord.Embed(description=f"Error: {e}", color=color.red)
            )

    @root.command(
        name="removebalance",
        help="Removes balance from a user",
        aliases=["removebal", "removecoins", "removecoin"],
        hidden=True,
    )
    @checks.is_owner()
    async def removebalance(
        self, ctx: commands.Context, user: discord.User, amount: int
    ):

        try:

            message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Removing balance...",
                    color=color.orange,
                )
            )

            if amount < 0:

                return await message.edit(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | Amount cannot be negative",
                        color=color.red,
                    )
                )

            user_data = self.bot.cache.users.get(str(user.id), {})

            if not user_data:

                user_data = await storage.users.get(id=user.id)

            user_data = self.bot.cache.users.get(str(user.id), {})

            await storage.users.update(
                id=self.bot.cache.users.get(str(user.id), {}).get("id"),
                balance=(
                    self.bot.cache.users.get(str(user.id), {}).get("balance", 0)
                    - amount
                    if self.bot.cache.users.get(str(user.id), {}).get("balance", 0)
                    - amount
                    >= 0
                    else 0
                ),
            )

            await message.edit(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.SUCCESS} | {user.display_name} | Current Balance: `{get_formatted_balance(self.bot.cache.users.get(str(user.id),{}).get('balance',0))}`{self.bot.emoji.COIN}",
                    color=color.green,
                )
            )

        except Exception as e:

            await message.edit(
                embed=discord.Embed(description=f"Error: {e}", color=color.red)
            )

    @root.command(
        name="setbalance",
        help="Sets balance of a user",
        aliases=["setbal", "setcoins", "setcoin"],
        hidden=True,
    )
    @checks.is_owner()
    async def setbalance(self, ctx: commands.Context, user: discord.User, amount: int):

        try:

            message = await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Setting balance...",
                    color=color.orange,
                )
            )

            user_data = self.bot.cache.users.get(str(user.id), {})

            if not user_data:

                user_data = await storage.users.get(id=user.id)

            user_data = self.bot.cache.users.get(str(user.id), {})

            await storage.users.update(
                id=self.bot.cache.users.get(str(user.id), {}).get("id"),
                balance=amount if amount >= 0 else 0,
            )

            await message.edit(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.SUCCESS} | {user.display_name} | Current Balance: `{get_formatted_balance(self.bot.cache.users.get(str(user.id),{}).get('balance',0))}`{self.bot.emoji.COIN}",
                    color=color.green,
                )
            )

        except Exception as e:

            await message.edit(
                embed=discord.Embed(description=f"Error: {e}", color=color.red)
            )

    # @root.command(

    #     name="shop",

    #     help="Shows the shop to edit items",

    #     hidden=True

    # )

    # @checks.is_owner()

    # async def root_shop(self, ctx:commands.Context):

    #     try:

    #         async def get_embed():

    #             shop_data = self.bot.cache.shop

    #             embed = discord.Embed(

    #                 title="Root Shop",

    #                 description="",

    #                 color=color.orange

    #             )

    #             embed.set_author(

    #                 name=self.bot.user.display_name,

    #                 icon_url=self.bot.user.display_avatar.url

    #             )

    #             embed.set_footer(

    #                 text=f"Requested by {ctx.author.display_name}",

    #                 icon_url=ctx.author.display_avatar.url

    #             )

    #             for item, data in shop_data.items():

    #                 embed.description += f"> **{item}** - {data['name']} - `{data['price']}`{self.bot.emoji.COIN}\n\n"

    #             return embed

    #         timeout_time = 600

    #         cancled = False

    #         def refresh_timeout_time():

    #             nonlocal timeout_time

    #             timeout_time = 600

    #         async def get_view(disabled=False):

    #             shop_data = self.bot.cache.shop

    #             view = discord.ui.View(timeout=600)

    #             refresh_timeout_time()

    #             add_item = discord.ui.Button(

    #                 style=discord.ButtonStyle.green,

    #                 label="Add Item",

    #                 emoji=self.bot.emoji.CREATE,

    #                 row=0

    #             )

    #             add_item.callback = lambda i: add_item_callback(i)

    #             view.add_item(add_item)

    #             remove_item = discord.ui.Button(

    #                 style=discord.ButtonStyle.red,

    #                 label="Remove Item",

    #                 emoji=self.bot.emoji.DELETE,

    #                 row=0,

    #                 disabled=not shop_data

    #             )

    #             remove_item.callback = lambda i: remove_item_callback(i)

    #             view.add_item(remove_item)

    #             cancel = discord.ui.Button(

    #                 style=discord.ButtonStyle.gray,

    #                 label="Cancel",

    #                 emoji=self.bot.emoji.CANCLED,

    #                 row=0,

    #             )

    #             cancel.callback = lambda i: cancel_callback(i)

    #             view.add_item(cancel)

    #             select_to_edit = discord.ui.Select(

    #                 placeholder="Select an item to edit",

    #                 options=[discord.SelectOption(label=str(data.get('name',"Undefined")).capitalize(),value=item) for item,data in shop_data.items()] if shop_data else [],

    #                 min_values=1,

    #                 max_values=1,

    #                 row=1

    #             )

    #             select_to_edit.callback = lambda i: select_to_edit_callback(i)

    #             if shop_data:

    #                 view.add_item(select_to_edit)

    #             if disabled:

    #                 for item in view.children:

    #                     item.disabled = True

    #             return view

    #         async def cancel_callback(interaction:discord.Interaction):

    #             try:

    #                 if interaction.user.id != ctx.author.id:

    #                     return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this message",color=color.red),ephemeral=True,delete_after=5)

    #                 nonlocal cancled

    #                 cancled = True

    #                 await interaction.response.edit_message(embed=await get_embed(),view=await get_view(disabled=True))

    #             except Exception as e:

    #                 logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #         async def add_item_callback(interaction:discord.Interaction):

    #             try:

    #                 if interaction.user.id != ctx.author.id:

    #                     return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this message",color=color.red),ephemeral=True,delete_after=5)

    #                 class add_item_modal(discord.ui.Modal,title="Add New Item"):

    #                     new_item_name_field = discord.ui.TextInput(

    #                         placeholder="Enter the item name",

    #                         label="Item Name",

    #                         style=discord.TextStyle.short,

    #                         row=0

    #                     )

    #                     new_item_description_field = discord.ui.TextInput(

    #                         placeholder="Enter the item description",

    #                         label="Item Description",

    #                         style=discord.TextStyle.long,

    #                         row=1

    #                     )

    #                     new_item_price_field = discord.ui.TextInput(

    #                         placeholder="Enter the item price",

    #                         label="Item Price",

    #                         style=discord.TextStyle.short,

    #                         row=2

    #                     )

    #                     new_item_image_url_field = discord.ui.TextInput(

    #                         placeholder="Enter the item image url",

    #                         label="Item Image URL",

    #                         style=discord.TextStyle.short,

    #                         required=False,

    #                         row=3

    #                     )

    #                     bot = self.bot

    #                     async def on_submit(self, interaction:discord.Interaction):

    #                         try:

    #                             new_item_name = self.new_item_name_field.value

    #                             new_item_description = self.new_item_description_field.value

    #                             new_item_price = self.new_item_price_field.value

    #                             new_item_image_url = self.new_item_image_url_field.value

    #                             shop_data = self.bot.cache.shop

    #                             def check_existing_item(name:str):

    #                                 for item in shop_data:

    #                                     if shop_data[item].get('name') == name:

    #                                         return True

    #                                 return False

    #                             if check_existing_item(new_item_name.lower()):

    #                                 return await interaction.response.send_message(embed=discord.Embed(description="An item with that name already exists",color=color.red),ephemeral=True,delete_after=5)

    #                             try:

    #                                 new_item_price = float(new_item_price)

    #                             except:

    #                                 return await interaction.response.send_message(embed=discord.Embed(description="Invalid price",color=color.red),ephemeral=True,delete_after=5)

    #                             await interaction.response.defer()

    #                             await storage.shop.insert(

    #                                 name=new_item_name.lower(),

    #                                 description=new_item_description,

    #                                 price=new_item_price,

    #                                 image_url=new_item_image_url

    #                             )

    #                             await interaction.message.edit(embed=await get_embed(),view=await get_view())

    #                             temp_message = await interaction.followup.send(embed=discord.Embed(description=f"Item {new_item_name} has been added",color=color.green),ephemeral=True)

    #                             await asyncio.sleep(5)

    #                             try:

    #                                 await temp_message.delete()

    #                             except:

    #                                 pass

    #                         except Exception as e:

    #                             logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #                             await interaction.response.send_message(embed=discord.Embed(description="An error occured",color=color.red),ephemeral=True,delete_after=5)

    #                 await interaction.response.send_modal(add_item_modal())

    #             except Exception as e:

    #                 logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #                 await interaction.response.send_message(embed=discord.Embed(description="An error occured",color=color.red),ephemeral=True,delete_after=5)

    #         async def remove_item_callback(interaction:discord.Interaction):

    #             try:

    #                 if interaction.user.id != ctx.author.id:

    #                     return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this message",color=color.red),ephemeral=True,delete_after=5)

    #                 class remove_item_modal(discord.ui.Modal,title="Remove Item"):

    #                     item_id_field = discord.ui.TextInput(

    #                         placeholder="Enter the item id",

    #                         label="Item ID",

    #                         style=discord.TextStyle.short,

    #                         row=0

    #                     )

    #                     bot = self.bot

    #                     async def on_submit(self, interaction:discord.Interaction):

    #                         try:

    #                             item_id = self.item_id_field.value

    #                             shop_data = self.bot.cache.shop

    #                             if item_id not in shop_data:

    #                                 return await interaction.response.send_message(embed=discord.Embed(description="Item not found",color=color.red),ephemeral=True,delete_after=5)

    #                             await interaction.response.defer()

    #                             await storage.shop.delete(

    #                                 id=shop_data[item_id].get('id')

    #                             )

    #                             await interaction.message.edit(embed=await get_embed(),view=await get_view())

    #                             temp_message = await interaction.followup.send(embed=discord.Embed(description=f"Item {item_id} has been removed",color=color.green),ephemeral=True)

    #                             await asyncio.sleep(5)

    #                             try:

    #                                 await temp_message.delete()

    #                             except:

    #                                 pass

    #                         except Exception as e:

    #                             logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #                             await interaction.response.send_message(embed=discord.Embed(description="An error occured",color=color.red),ephemeral=True,delete_after=5)

    #                 await interaction.response.send_modal(remove_item_modal())

    #             except Exception as e:

    #                 logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #                 await interaction.response.send_message(embed=discord.Embed(description="An error occured",color=color.red),ephemeral=True,delete_after=5)

    #         async def select_to_edit_callback(interaction:discord.Interaction):

    #             try:

    #                 if interaction.user.id != ctx.author.id:

    #                     return await interaction.response.send_message(embed=discord.Embed(description="You can't interact with this message",color=color.red),ephemeral=True,delete_after=5)

    #                 shop_data = self.bot.cache.shop

    #                 selected_item = interaction.data.get('values')[0]

    #                 selected_data = shop_data.get(selected_item)

    #                 if not selected_data:

    #                     return await interaction.response.send_message(embed=discord.Embed(description="Item not found",color=color.red),ephemeral=True,delete_after=5)

    #                 class edit_item_modal(discord.ui.Modal,title="Edit Item"):

    #                     new_item_name_field = discord.ui.TextInput(

    #                         placeholder="Enter the item name",

    #                         label="Item Name",

    #                         style=discord.TextStyle.short,

    #                         row=0,

    #                         default=selected_data.get('name',"")

    #                     )

    #                     new_item_description_field = discord.ui.TextInput(

    #                         placeholder="Enter the item description",

    #                         label="Item Description",

    #                         style=discord.TextStyle.long,

    #                         row=1,

    #                         default=selected_data.get('description',"")

    #                     )

    #                     new_item_price_field = discord.ui.TextInput(

    #                         placeholder="Enter the item price",

    #                         label="Item Price",

    #                         style=discord.TextStyle.short,

    #                         row=2,

    #                         default=selected_data.get('price',"")

    #                     )

    #                     new_item_image_url_field = discord.ui.TextInput(

    #                         placeholder="Enter the item image url",

    #                         label="Item Image URL",

    #                         style=discord.TextStyle.short,

    #                         required=False,

    #                         row=1,

    #                         default=selected_data.get('image_url',"")

    #                     )

    #                     bot = self.bot

    #                     async def on_submit(self, interaction:discord.Interaction):

    #                         try:

    #                             item_id = self.item_id_field.value

    #                             new_item_name = self.new_item_name_field.value

    #                             new_item_description = self.new_item_description_field.value

    #                             new_item_price = self.new_item_price_field.value

    #                             new_item_image_url = self.new_item_image_url_field.value

    #                             shop_data = self.bot.cache.shop

    #                             if item_id not in shop_data:

    #                                 return await interaction.response.send_message(embed=discord.Embed(description="Item not found",color=color.red),ephemeral=True,delete_after=5)

    #                             try:

    #                                 new_item_price = float(new_item_price)

    #                             except:

    #                                 return await interaction.response.send_message(embed=discord.Embed(description="Invalid price",color=color.red),ephemeral=True,delete_after=5)

    #                             await interaction.response.defer()

    #                             await storage.shop.update(

    #                                 id=shop_data[item_id].get('id'),

    #                                 name=new_item_name.lower(),

    #                                 description=new_item_description,

    #                                 price=new_item_price,

    #                                 image_url=new_item_image_url

    #                             )

    #                             await interaction.message.edit(embed=await get_embed(),view=await get_view())

    #                             temp_message = await interaction.followup.send(embed=discord.Embed(description=f"Item {new_item_name} has been updated",color=color.green),ephemeral=True)

    #                             await asyncio.sleep(5)

    #                             try:

    #                                 await temp_message.delete()

    #                             except:

    #                                 pass

    #                         except Exception as e:

    #                             logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #                             await interaction.response.send_message(embed=discord.Embed(description="An error occured",color=color.red),ephemeral=True,delete_after=5)

    #                 await interaction.response.send_modal(edit_item_modal())

    #             except Exception as e:

    #                 logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #                 await interaction.response.send_message(embed=discord.Embed(description="An error occured",color=color.red),ephemeral=True,delete_after=5)

    #         message = await ctx.send(embed=await get_embed(),view=await get_view())

    #         while not cancled:

    #             try:

    #                 await asyncio.sleep(1)

    #                 if timeout_time <= 0:

    #                     await message.edit(view=await get_view(disabled=True))

    #                     break

    #                 timeout_time -= 1

    #             except Exception as e:

    #                 logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    #                 break

    #     except Exception as e:

    #         logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @root.command(
        name="lavalinks",
        aliases=["nodes"],
        description="Get information about all connected Lavalink nodes.",
    )
    @checks.is_owner()
    async def lavalinks(self, ctx: commands.Context):

        try:

            all_nodes = wavelink.Pool.nodes

            if not all_nodes:

                return await ctx.send("No Lavalink nodes are connected.")

            # make a list of all nodes 5 by 5

            nodes_list = [
                list(all_nodes.values())[i : i + 5] for i in range(0, len(all_nodes), 5)
            ]

            current_page_index = 0

            async def get_embed():

                nodes = nodes_list[current_page_index]

                embed = discord.Embed(
                    title="Lavalink Nodes",
                    description=f"Total Nodes: {len(all_nodes)}",
                    color=color.blue,
                )

                embed.set_footer(
                    text=f"Page {current_page_index + 1}/{len(nodes_list)}"
                )

                embed.description += "\n\n"

                for node in nodes:

                    embed.description += f"**{node.uri}**\n"

                    embed.description += f"Status: {node.status.name}\n"

                    embed.description += f"Players: {len(node.players)}\n\n"

                return embed

            async def get_view():

                view = discord.ui.View(timeout=600)

                previous_button = discord.ui.Button(
                    label="Previous",
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.PREVIOUS,
                    disabled=current_page_index == 0,
                )

                next_button = discord.ui.Button(
                    label="Next",
                    style=discord.ButtonStyle.primary,
                    emoji=self.bot.emoji.NEXT,
                    disabled=current_page_index == len(nodes_list) - 1,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                next_button.callback = lambda i: next_button_callback(i)

                view.add_item(previous_button)

                view.add_item(next_button)

                return view

            async def previous_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't use this button.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You can't use this button.",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=5,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
                    )

            embed = await get_embed()

            view = await get_view()

            message = await ctx.send(embed=embed, view=view)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}"
            )

    @root.command(
        name="noprefixadd",
        aliases=["npadd", "npa", "reo"],
        description="Adds a user to the no prefix list.",
        hidden=True,
    )
    @checks.is_owner()
    async def noprefixadd(
        self, ctx: commands.Context, user: discord.User, days: int = 0
    ):

        try:

            if days < 1:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | Minimum days must be 1.",
                        color=color.red,
                    )
                )

            if not str(user.id) not in self.bot.cache.users:

                try:

                    await storage.users.insert(
                        user_id=user.id,
                    )

                except:

                    pass

            if self.bot.cache.users.get(str(user.id), {}).get(
                "no_prefix_subscription", False
            ):

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | {user.display_name} is already has no prefix subscription.",
                        color=color.red,
                    )
                )

            await change_user_subscription(
                bot=self.bot,
                user_id=user.id,
                subscription="user_no_prefix",
                valid_for_days=days,
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.SUCCESS} | {user.display_name}'s received no prefix subscription for {days} days."
                )
            )

        except Exception as e:

            await ctx.send(
                embed=discord.Embed(description=f"Error: {e}", color=color.red)
            )

    @root.command(
        name="noprefixremove",
        aliases=["npremove", "nprem", "nprm"],
        description="Removes a user from the no prefix list.",
        hidden=True,
    )
    @checks.is_owner()
    async def noprefixremove(self, ctx: commands.Context, user: discord.User):

        try:

            if not str(user.id) not in self.bot.cache.users:

                try:

                    await storage.users.insert(
                        user_id=user.id,
                    )

                except:

                    pass

            if not self.bot.cache.users.get(str(user.id), {}).get(
                "no_prefix_subscription", False
            ):

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"{self.bot.emoji.ERROR} | {user.display_name} does not have no prefix subscription.",
                        color=color.red,
                    )
                )

            await change_user_subscription(
                bot=self.bot, user_id=user.id, subscription=None
            )

            await ctx.send(
                embed=discord.Embed(
                    description=f"{self.bot.emoji.SUCCESS} | {user.display_name}'s subscription has been changed to free."
                )
            )

        except Exception as e:

            await ctx.send(
                embed=discord.Embed(description=f"Error: {e}", color=color.red)
            )
