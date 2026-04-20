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


import traceback, sys


import re


import storage.afk


import storage.guilds


import storage.users


from reo.console.logging import logger


from reo.style import color


from reo.workflows import ui


from reo.utils import pings


import requests


from reo.config.config import BotConfigClass


BotConfig = BotConfigClass()


import storage


from reo.workflows.afk_delay import afk_delay


from reo.engine.Bot import AutoShardedBot


class Utils(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        class cog_info:

            name = "Utils"

            category = "Extra"

            description = "Utility commands"

            hidden = False

            emoji = self.bot.emoji.UTILS or "⚒️"

        self.cog_info = cog_info

    @commands.hybrid_command(
        name="ping", with_app_command=True, help="Get The Bot's Ping"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def ping_command(self, ctx: commands.Context):

        try:

            bot_ping = pings.bot(self.bot)

            cache_response_time = pings.cache()

            database_response_time = await pings.database()

            logger.info(
                f"Bot Ping: {bot_ping}ms, Database Response Time: {database_response_time}ms, Cache Response Time: {cache_response_time}ms"
            )

            embed = discord.Embed(color=color.green)

            embed.set_author(
                name=self.bot.user.display_name,
                icon_url=self.bot.user.display_avatar.url,
                url=self.bot.urls.WEBSITE,
            )

            embed.set_footer(text=f"Provided By Runxking & Ray & Naaz")

            embed.description = (
                f"{self.bot.emoji.LATENCY} • **Bot Ping:** `{bot_ping}ms`"
            )

            embed.description += f"\n{self.bot.emoji.STORAGE} • **Storage Ping:** `{database_response_time}ms`"

            embed.description += (
                f"\n{self.bot.emoji.CACHE} • **Cache Ping:** `{cache_response_time}ms`"
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Fetching The Ping")

    @commands.hybrid_command(
        name="invite", with_app_command=True, help="Invite The Bot To Your Server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def invite_command(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                title="Invite Me To Your Server",
                description="Heads Up! You Can Invite Me To Your Server By Clicking The Button Below.\nPlease Make Sure You Have The Required Permissions To Add Me To Your Server.\nWe hope you enjoy using our bot.",
                color=color.green,
            )

            embed.set_footer(
                text=f"Provided By Runxking & Ray & Naaz",
                icon_url=self.bot.user.display_avatar.url,
            )

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            view = discord.ui.View()

            view.add_item(
                discord.ui.Button(
                    emoji=self.bot.emoji.INVITE,
                    label="Invite Me",
                    url=self.bot.urls.INVITE,
                )
            )

            # send as ephemeral if its a slash command

            await ctx.send(embed=embed, view=view, mention_author=False)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Sending The Invite Link")

    @commands.hybrid_command(
        name="support", with_app_command=True, help="Join The Support Server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def support_command(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                title="Support",
                description="Heads Up! You Can Join Our Support Server By Clicking The Button Below.\nPlease Make Sure You Follow The Rules Of The Server.\nWe hope you enjoy using our bot.",
                color=color.green,
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=self.bot.user.display_avatar.url,
            )

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            view = discord.ui.View()

            view.add_item(
                discord.ui.Button(label="Support", url=self.bot.urls.SUPPORT_SERVER)
            )

            # send as ephemeral if its a slash command

            await ctx.send(embed=embed, view=view, mention_author=False)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Sending The Support Server Link")

    @commands.hybrid_command(
        name="vote", with_app_command=True, help="Vote For The Bot"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def vote_command(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                title="Vote",
                description="Heads Up! You Can Vote For Me By Clicking The Button Below.\nPlease Make Sure You Follow The Rules Of The Voting Site.\nWe hope you enjoy using our bot.",
                color=color.green,
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=self.bot.user.display_avatar.url,
            )

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            view = discord.ui.View()

            view.add_item(discord.ui.Button(label="Vote", url=self.bot.urls.VOTE))

            # send as ephemeral if its a slash command

            await ctx.send(embed=embed, view=view, mention_author=False)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Sending The Voting Link")

    @commands.hybrid_command(
        name="stats",
        with_app_command=True,
        help="Get The Bot's Stats",
        aliases=["statistics", "status"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def stats_command(self, ctx: commands.Context):

        # show the cpu uses and memory uses in % also the os and the python version

        try:

            cou_usage = psutil.cpu_percent()

            memory_usage = psutil.virtual_memory().percent

            os_name = platform.uname().system

            python_version = platform.python_version()

            embed = discord.Embed(color=color.black, type="rich")

            # embed.set_author(

            #     name=f"{self.bot.user.display_name} Status",

            #     icon_url=self.bot.user.display_avatar.url

            # )

            def format_number(num):

                return num

                # replace it with the below code if you want to format the numbers

                # if num >= 1_000_000_000:

                #     return f"{num / 1_000_000_000:.1f}b"

                # elif num >= 1_000_000:

                #     return f"{num / 1_000_000:.1f}m"

                # elif num >= 1_000:

                #     return f"{num / 1_000:.1f}k"

                # else:

                #     return str(num)

            embed.description = f"{self.bot.emoji.SEARCH} : **[Hey users !\nHere’s all the info you need\nabout {self.bot.user.display_name}. Check it out]({self.bot.urls.SUPPORT_SERVER})**"

            embed.description += f"\n\n{self.bot.emoji.BOT} : **__Basic Status__**\n"

            embed.description += f"> `User's` : **{format_number(sum([guild.member_count for guild in self.bot.guilds if guild.member_count]))}**\n"

            embed.description += (
                f"> `Guilds` : **{format_number(len(self.bot.guilds))}**\n"
            )

            embed.description += f"> `Python` : **{python_version}**\n"

            embed.description += f"> `Dsc-py` : **{discord.__version__}**\n"

            embed.description += f"> `BotCpu` : **{cou_usage}%**\n"

            embed.description += f"> `BotRam` : **{memory_usage}%**\n"

            embed.description += f"> `BotPid` : **{psutil.Process().pid}**\n"

            embed.description += f"> `Shards` : **{self.bot.shard_count}**\n"

            embed.description += f"> `HostOS` : **{os_name}**\n"

            embed.description += f"> [Invite]({self.bot.urls.INVITE}) | [Support]({self.bot.urls.SUPPORT_SERVER})  | [Vote]({self.bot.urls.VOTE})\n"

            embed.description += f"\n> -# **Hosted on shaodwhost.fun**"

            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

            if self.bot.developers:

                embed.set_footer(
                    text=f"REO • CodeX Development",
                    icon_url=self.bot.user.display_avatar.url,
                )

            else:

                embed.set_footer(
                    text=f"Provided By Runxking & Ray & Naaz",
                    icon_url=self.bot.user.display_avatar.url,
                )

            view = discord.ui.View()

            invite_me_button = discord.ui.Button(
                label="Invite",
                emoji=self.bot.emoji.INVITE,
                style=discord.ButtonStyle.green,
                url=self.bot.urls.INVITE,
            )

            support_server_button = discord.ui.Button(
                label="Server",
                emoji=self.bot.emoji.SUPPORT,
                style=discord.ButtonStyle.green,
                url=self.bot.urls.SUPPORT_SERVER,
            )

            view.add_item(support_server_button)

            view.add_item(invite_me_button)

            await ctx.send(embed=embed, view=view)

        except Exception as e:

            logger.error(
                f"Commmand: ping, Message: {ctx.message.content}, Message ID: {ctx.message.id}, Error: {e}"
            )

            await ctx.send("An Error Occured While Fetching The Stats")

    @commands.command(
        name="steal", help="Can Be Used To Steal Emoji/Multiple Emojis From A Server"
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    async def steal_command(self, ctx: commands.Context, *emojis: discord.PartialEmoji):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "manage_emojis"):

                return await ctx.send(
                    embed=discord.Embed(
                        description="You Need The Manage Emojis Permission To Use This Command",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            if not emojis:

                # check if the command is replied to a message

                replied_message = ctx.message.reference

                if not replied_message:

                    return await ctx.send(
                        embed=discord.Embed(
                            description="Please Provide Some Custom Emojis To Steal or Reply To A Message With Custom Stickers",
                            color=color.red,
                        ),
                        delete_after=10,
                    )

                reply_message = await ctx.channel.fetch_message(
                    replied_message.message_id
                )

                if not reply_message:

                    return await ctx.send(
                        embed=discord.Embed(
                            description="Please Provide Some Custom Emojis To Steal or Reply To A Message With Custom Stickers",
                            color=color.red,
                        ),
                        delete_after=10,
                    )

                stickers = reply_message.stickers

                if not stickers:

                    # try to get the emojis from the message

                    raw_emojis = re.findall(r"<a?:\w+:\d+>", reply_message.content)

                    stickers = []

                    for raw_emoji in raw_emojis:

                        try:

                            # also get those emojis which the bot can't see

                            # emoji = self.bot.get_emoji(int(raw_emoji.split(":")[-1].replace(">","")))

                            emoji = await commands.PartialEmojiConverter().convert(
                                ctx, raw_emoji
                            )

                            if emoji:

                                stickers.append(emoji)

                        except Exception as e:

                            logger.error(
                                f"Error in file {__file__}: {traceback.format_exc()}"
                            )

                            logger.warning(
                                f"Failed To Convert Emoji {raw_emoji} Error: {e}"
                            )

                    if not stickers:

                        return await ctx.send(
                            embed=discord.Embed(
                                description="Please Provide Some Custom Emojis To Steal or Reply To A Message With Custom Stickers",
                                color=color.red,
                            ),
                            delete_after=10,
                        )

                # check if the guild have enough space to add the emojis

                # guild_stickers = await ctx.guild.fetch_stickers()

                # sticket_limit = ctx.guild.sticker_limit

                view_timeout_time = 60

                cancled = False

                added = False

                added_title = None

                async def get_embed():

                    sticker = stickers[current_page_index]

                    embed = discord.Embed(
                        title="Add as Emoji or Sticker" if not added else added_title,
                        color=color.green,
                    )

                    embed.set_image(url=sticker.url)

                    embed.set_footer(
                        text=f"{current_page_index+1}/{len(stickers)} Stickers",
                        icon_url=ctx.bot.user.display_avatar.url,
                    )

                    return embed

                current_page_index = 0

                async def get_view(disabled=False):

                    view = discord.ui.View(timeout=60)

                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Previous",
                        row=1,
                        disabled=current_page_index <= 0,
                    )

                    previous_button.callback = lambda i: previous_button_callback(i)

                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=1
                    )

                    stop_button.callback = lambda i: stop_button_callback(i)

                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Next",
                        row=1,
                        disabled=current_page_index >= len(stickers) - 1,
                    )

                    next_button.callback = lambda i: next_button_callback(i)

                    add_as_emoji_button = discord.ui.Button(
                        label="Add as Emoji", style=discord.ButtonStyle.green, row=0
                    )

                    add_as_emoji_button.callback = (
                        lambda i: add_as_emoji_button_callback(i)
                    )

                    add_as_sticker_button = discord.ui.Button(
                        label="Add as Sticker", style=discord.ButtonStyle.green, row=0
                    )

                    add_as_sticker_button.callback = (
                        lambda i: add_as_sticker_button_callback(i)
                    )

                    if not added:

                        view.add_item(add_as_emoji_button)

                        view.add_item(add_as_sticker_button)

                    if len(stickers) > 1:

                        view.add_item(previous_button)

                        # view.add_item(stop_button)

                        view.add_item(next_button)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                async def previous_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def stop_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                async def next_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def add_as_emoji_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Emoji",
                                color=color.green,
                            ),
                            view=None,
                        )

                        added_emojis = []

                        failed_emojis = []

                        for sticker in stickers:

                            try:

                                added_emoji = await ctx.guild.create_custom_emoji(
                                    name=sticker.name.strip("_"),
                                    image=await sticker.read(),
                                    reason=f"Emoji Added By {ctx.author.name}",
                                )

                                added_emojis.append(added_emoji)

                            except Exception as e:

                                failed_emojis.append(sticker)

                                logger.error(
                                    f"Error in file {__file__}: {traceback.format_exc()}"
                                )

                                logger.warning(
                                    f"Falied To Add Emoji {sticker.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Emojis Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                async def add_as_sticker_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Sticker",
                                color=color.green,
                            ),
                            view=None,
                        )

                        added_stickers = []

                        failed_stickers = []

                        for sticker in stickers:

                            try:

                                image_bytes = await sticker.read()

                                # Creating a discord.File from the bytes

                                image_file = discord.File(
                                    io.BytesIO(image_bytes),
                                    filename=f"{sticker.name}.{'png'}",
                                )

                                added_sticker = await ctx.guild.create_sticker(
                                    name=sticker.name,
                                    emoji="🤖",
                                    description=f"Sticker Added By {ctx.author.name}",
                                    reason=f"Sticker Added By {ctx.author.name}",
                                    file=image_file,
                                )

                                added_stickers.append(added_sticker)

                            except Exception as e:

                                failed_stickers.append(sticker)

                                logger.warning(
                                    f"Falied To Add Sticker {sticker.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Stickers Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                message = await ctx.send(embed=await get_embed(), view=await get_view())

                while not cancled:

                    view_timeout_time -= 1

                    if view_timeout_time <= 0:

                        await message.edit(view=await get_view(True))

                        break

                    await asyncio.sleep(1)

            else:

                for emoji in emojis:

                    if not emoji.is_custom_emoji():

                        return await ctx.send(
                            embed=discord.Embed(
                                description="Please Provide Some Custom Emojis To Steal",
                                color=color.red,
                            ),
                            delete_after=10,
                        )

                view_timeout_time = 60

                cancled = False

                added = False

                added_title = None

                async def get_embed():

                    emoji = emojis[current_page_index]

                    embed = discord.Embed(
                        title="Add as Emoji or Sticker" if not added else added_title,
                        color=color.green,
                    )

                    embed.set_image(url=emoji.url)

                    embed.set_footer(
                        text=f"{current_page_index+1}/{len(emojis)} Emojis",
                        icon_url=ctx.bot.user.display_avatar.url,
                    )

                    return embed

                current_page_index = 0

                async def get_view(disabled=False):

                    view = discord.ui.View(timeout=65)

                    previous_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Previous",
                        row=1,
                        disabled=current_page_index <= 0,
                    )

                    previous_button.callback = lambda i: previous_button_callback(i)

                    stop_button = discord.ui.Button(
                        style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=1
                    )

                    stop_button.callback = lambda i: stop_button_callback(i)

                    next_button = discord.ui.Button(
                        style=discord.ButtonStyle.blurple,
                        label="Next",
                        row=1,
                        disabled=current_page_index >= len(emojis) - 1,
                    )

                    next_button.callback = lambda i: next_button_callback(i)

                    add_as_emoji_button = discord.ui.Button(
                        label="Add as Emoji", style=discord.ButtonStyle.green, row=0
                    )

                    add_as_emoji_button.callback = (
                        lambda i: add_as_emoji_button_callback(i)
                    )

                    add_as_sticker_button = discord.ui.Button(
                        label="Add as Sticker", style=discord.ButtonStyle.green, row=0
                    )

                    add_as_sticker_button.callback = (
                        lambda i: add_as_sticker_button_callback(i)
                    )

                    if not added:

                        view.add_item(add_as_emoji_button)

                        view.add_item(add_as_sticker_button)

                    if len(emojis) > 1:

                        view.add_item(previous_button)

                        # view.add_item(stop_button)

                        view.add_item(next_button)

                    if disabled:

                        for item in view.children:

                            item.disabled = True

                    return view

                async def previous_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index -= 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def stop_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                async def next_button_callback(interaction: discord.Interaction):

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index += 1

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                async def add_as_emoji_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Emoji",
                                color=color.green,
                            ),
                            view=None,
                        )

                        added_emojis = []

                        failed_emojis = []

                        for emoji in emojis:

                            try:

                                added_emoji = await ctx.guild.create_custom_emoji(
                                    name=emoji.name,
                                    image=await emoji.read(),
                                    reason=f"Emoji Added By {ctx.author.name}",
                                )

                                added_emojis.append(added_emoji)

                            except Exception as e:

                                failed_emojis.append(emoji)

                                logger.warning(
                                    f"Falied To Add Emoji {emoji.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Emojis Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                async def add_as_sticker_button_callback(
                    interaction: discord.Interaction,
                ):

                    try:

                        if interaction.user.id != ctx.author.id:

                            return await interaction.response.send_message(
                                embed=discord.Embed(
                                    description="You Can't Interact With This Button",
                                    color=color.red,
                                ),
                                ephemeral=True,
                                delete_after=10,
                            )

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title=None,
                                description="Adding as Sticker",
                                color=color.green,
                            ),
                            view=None,
                        )

                        added_stickers = []

                        failed_stickers = []

                        for emoji in emojis:

                            try:

                                image_bytes = await emoji.read()

                                # Creating a discord.File from the bytes

                                image_file = discord.File(
                                    io.BytesIO(image_bytes),
                                    filename=f"{emoji.name}.{'gif' if emoji.animated else 'png'}",
                                )

                                added_sticker = await ctx.guild.create_sticker(
                                    name=emoji.name,
                                    emoji="🤖",
                                    description=f"Sticker Added By {ctx.author.name}",
                                    reason=f"Sticker Added By {ctx.author.name}",
                                    file=image_file,
                                )

                                added_stickers.append(added_sticker)

                            except Exception as e:

                                failed_stickers.append(emoji)

                                logger.warning(
                                    f"Falied To Add Sticker {emoji.name} To The Server {ctx.guild.name} By {ctx.author.name} Error: {e}"
                                )

                        nonlocal added, added_title

                        added = True

                        added_title = f"{self.bot.emoji.SUCCESS} - Stickers Added"

                        await interaction.message.edit(
                            embed=await get_embed(),
                            view=await get_view(),
                            delete_after=60,
                        )

                    except Exception as e:

                        logger.error(
                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                        )

                message = await ctx.send(embed=await get_embed(), view=await get_view())

                while not cancled:

                    view_timeout_time -= 1

                    if view_timeout_time <= 0:

                        await message.edit(view=await get_view(True))

                        break

                    await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_command(
        name="noprefix",
        with_app_command=True,
        help="Enable/Disable The No Prefix Feature",
        aliases=["np"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def noprefix_command(self, ctx: commands.Context):

        try:

            async def get_embed():

                users_cache = cache.users.get(str(ctx.author.id), {})

                embed = discord.Embed(
                    title="No Prefix Feature",
                    color=color.green if users_cache.get("no_prefix") else color.red,
                )

                embed.description = f"**__Status:__** {self.bot.emoji.ENABLED if users_cache.get('no_prefix') else self.bot.emoji.DISABLED}"

                embed.description += f"\n**__Subscription:__** {self.bot.emoji.ENABLED if users_cache.get('no_prefix_subscription') else self.bot.emoji.DISABLED}"

                if users_cache.get("no_prefix_subscription"):

                    subscription_end = users_cache.get("no_prefix_end")

                    subscription_end_text = (
                        f"<t:{int(subscription_end.timestamp())}:R>"
                        if subscription_end
                        else "`Never`"
                    )

                    embed.description += (
                        f"\n**__Subscription Ends:__** {subscription_end_text}"
                    )

                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                return embed

            timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled=False):

                users_cache = cache.users.get(str(ctx.author.id), {})

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                enable_disable_button = discord.ui.Button(
                    label=(
                        "Click To Enable"
                        if not users_cache.get("no_prefix")
                        else "Click To Disable"
                    ),
                    style=(
                        discord.ButtonStyle.green
                        if not users_cache.get("no_prefix")
                        else discord.ButtonStyle.gray
                    ),
                    row=0,
                    emoji=(
                        self.bot.emoji.ENABLED
                        if not users_cache.get("no_prefix")
                        else self.bot.emoji.DISABLED
                    ),
                )

                enable_disable_button.callback = (
                    lambda i: enable_disable_button_callback(i)
                )

                enable_disable_subscription_button = discord.ui.Button(
                    label="Subscription Required",
                    style=discord.ButtonStyle.link,
                    url=self.bot.urls.SUPPORT_SERVER,
                    row=0,
                    emoji=self.bot.emoji.SUPPORT,
                )

                cancle_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    row=0,
                    emoji=self.bot.emoji.CANCLED,
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                if users_cache.get("no_prefix_subscription", False):

                    view.add_item(enable_disable_button)

                    view.add_item(cancle_button)

                else:

                    view.add_item(enable_disable_subscription_button)

                    nonlocal cancled

                    cancled = True

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def enable_disable_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer()

                    users_cache = cache.users.get(str(ctx.author.id), {})

                    await storage.users.update(
                        id=users_cache.get("id"),
                        user_id=ctx.author.id,
                        no_prefix=not users_cache.get("no_prefix"),
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_command(
        name="afk",
        with_app_command=True,
        help="Set Your AFK Status",
        aliases=["away"],
        usage="<1m/1h/1d> <reason(OPTIONAL)>",
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def afk_command(
        self, ctx: commands.Context, time: str = None, *, reason: str = None
    ):

        try:

            if time:

                time = time.lower()

                try:

                    if time.endswith("m"):

                        time = int(time[:-1]) * 60

                    elif time.endswith("h"):

                        time = int(time[:-1]) * 60 * 60

                    elif time.endswith("d"):

                        time = int(time[:-1]) * 60 * 60 * 24

                    elif time.endswith("s"):

                        time = int(time[:-1])

                    else:

                        time = int(time)

                except:

                    reason = f"{time} {reason if reason else ''}"

                    time = None

            else:

                time = None

            if not reason:

                reason = "No Reason Provided"

            # by using re check the reason if it contains any mentions or urls

            if re.search(r"<@!?\d{17,19}>", reason) or re.search(
                r"https?://(?:www\.)?.+", reason
            ):

                return await ctx.send(
                    embed=discord.Embed(
                        description="You Can't Set AFK With Mentions Or Links In The Reason",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            embed = discord.Embed(
                title="Choose Your AFK Type",
                description=f"**__Afk Ends__** : {f'<t:{int(datetime.datetime.now().timestamp()+time)}:F>' if time else '`Never`'}\n**__Reason__** : {reason}",
                color=color.green,
            )

            cancled = False

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                guild_afk = (
                    cache.afk.get("guilds", {})
                    .get(str(ctx.guild.id), {})
                    .get(str(ctx.author.id), {})
                )

                global_afk = cache.afk.get("global", {}).get(str(ctx.author.id), {})

                guild_afk_button = discord.ui.Button(
                    label="Guild AFK",
                    style=discord.ButtonStyle.green,
                    row=0,
                    disabled=guild_afk.get("afk", False),
                )

                guild_afk_button.callback = lambda i: guild_afk_button_callback(i)

                global_afk_button = discord.ui.Button(
                    label="Global AFK",
                    style=discord.ButtonStyle.green,
                    row=0,
                    disabled=global_afk.get("afk", False),
                )

                global_afk_button.callback = lambda i: global_afk_button_callback(i)

                cancle_button = discord.ui.Button(
                    label="Cancel", style=discord.ButtonStyle.gray, row=1
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(guild_afk_button)

                view.add_item(global_afk_button)

                # view.add_item(cancle_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def guild_afk_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Setting Guild AFK", color=color.green
                        ),
                        view=None,
                    )

                    nonlocal cancled

                    cancled = True

                    await storage.afk.delete(user_id=ctx.author.id)

                    data = await storage.afk.insert(
                        user_id=ctx.author.id,
                        guild_id=ctx.guild.id,
                        afk=True,
                        reason=reason,
                        afk_end=(
                            (
                                datetime.datetime.now(tz=datetime.timezone.utc)
                                + datetime.timedelta(seconds=time)
                            ).isoformat()
                            if time
                            else None
                        ),
                        created_at=datetime.datetime.now(
                            tz=datetime.timezone.utc
                        ).isoformat(),
                    )

                    try:

                        asyncio.create_task(afk_delay(self.bot, data))

                    except:

                        pass

                    afk_end_text = (
                        f" and will end at <t:{int(datetime.datetime.now().timestamp()+time)}:F>"
                        if time
                        else "."
                    )

                    await interaction.message.edit(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.SUCCESS} - Guild AFK Set{afk_end_text}",
                            color=color.green,
                        ),
                        view=None,
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def global_afk_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            description="Setting Global AFK", color=color.green
                        ),
                        view=None,
                    )

                    nonlocal cancled

                    cancled = True

                    await storage.afk.delete(user_id=ctx.author.id)

                    data = await storage.afk.insert(
                        user_id=ctx.author.id,
                        guild_id=None,
                        afk=True,
                        reason=reason,
                        afk_end=(
                            (
                                datetime.datetime.now(tz=datetime.timezone.utc)
                                + datetime.timedelta(seconds=time)
                            ).isoformat()
                            if time
                            else None
                        ),
                        created_at=datetime.datetime.now(
                            tz=datetime.timezone.utc
                        ).isoformat(),
                    )

                    try:

                        asyncio.create_task(afk_delay(self.bot, data))

                    except:

                        pass

                    await interaction.message.edit(
                        embed=discord.Embed(
                            description=f"{self.bot.emoji.SUCCESS} - Global AFK Set{f' and Will End At <t:{int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp()+time)}:F>' if time else '.'}",
                            color=color.green,
                        ),
                        view=None,
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
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=embed, view=await get_view())

            await asyncio.sleep(60)

            if not cancled:

                await message.edit(view=await get_view(True))

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_command(
        name="prefix",
        help="Change The Bot's Prefix or Get The Current Prefix",
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def prefix(self, ctx: commands.Context, new_prefix: str = None):

        if (
            not await checks.check_is_moderator_permissions(ctx, "manage_guild")
            and not checks.check_is_admin_predicate(ctx)
            and not await checks.check_is_owner(ctx)
            and new_prefix
        ):

            embed = discord.Embed(
                title="Error",
                description="You don't have the required permissions to change the prefix.\n**__Permission Required:__** `Manage Server`",
                color=color.red,
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed, delete_after=5)

            return

        if new_prefix:

            if len(new_prefix) > 10:

                embed = discord.Embed(
                    title="Error",
                    description="The prefix can't be more than 10 characters.",
                    color=color.red,
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author.name}",
                    icon_url=ctx.author.display_avatar.url,
                )

                await ctx.send(embed=embed, delete_after=5)

                return

            cache_data = cache.guilds.get(str(ctx.guild.id))

            if not cache_data:

                await storage.guilds.insert(guild_id=ctx.guild.id)

                cache_data = cache.guilds.get(str(ctx.guild.id))

            if new_prefix.lower() == cache_data.get("prefix"):

                embed = discord.Embed(
                    description=f"The prefix is already set to `{new_prefix}`. Try a different prefix.",
                    color=color.red,
                )

                await ctx.send(embed=embed, delete_after=5)

                return

            await storage.guilds.update(id=cache_data.get("id"), prefix=new_prefix)

            embed = discord.Embed(
                description=f"**__Prefix changed to__** `{new_prefix}`",
                color=color.green,
            )

            await ctx.send(embed=embed)

        else:

            cache_data = cache.guilds.get(str(ctx.guild.id))

            if not cache_data:

                await storage.guilds.insert(guild_id=ctx.guild.id)

            embed = discord.Embed(
                description=f"**__Current Prefix:__** `{cache_data.get('prefix')}`",
                color=color.green,
            )

            await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="relationship",
        help="Set Your Relationship Status",
        with_app_command=True,
        aliases=["rs"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def relationship(self, ctx: commands.Context):

        try:

            available_relationships = {
                "single": self.bot.emoji.SINGLE,
                "married": self.bot.emoji.MARRIED,
                "engaged": self.bot.emoji.ENGAGED,
                "in_relationship": self.bot.emoji.IN_RELATIONSHIP,
                "complicated": self.bot.emoji.COMPLICATED,
            }

            user_data = cache.users.get(str(ctx.author.id), {})

            if not user_data:

                await storage.users.insert(user_id=ctx.author.id)

            async def get_embed():

                user_data = cache.users.get(str(ctx.author.id), {})

                embed = discord.Embed(
                    title="Relationship Status",
                    description=f"**__Current Relationship:__** `{user_data.get('relationship','single').capitalize()}`",
                    color=color.green,
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author.name}",
                    icon_url=ctx.author.display_avatar.url,
                )

                embed.set_thumbnail(url=ctx.author.display_avatar.url)

                return embed

            timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal timeout_time

                timeout_time = timeout

            async def get_view(disabled=False):

                user_data = cache.users.get(str(ctx.author.id), {})

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                select_relationship = discord.ui.Select(
                    placeholder="Select Your Relationship",
                    options=[
                        discord.SelectOption(
                            label=relationship.capitalize(),
                            value=relationship,
                            description=f"Set Your Relationship To {relationship.capitalize()}",
                            default=relationship
                            == user_data.get("relationship", "single"),
                        )
                        for relationship, emoji in available_relationships.items()
                    ],
                    row=0,
                )

                select_relationship.callback = lambda i: select_relationship_callback(i)

                view.add_item(select_relationship)

                cancle_button = discord.ui.Button(
                    label="Cancel",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.CANCLED,
                    row=1,
                )

                cancle_button.callback = lambda i: cancle_button_callback(i)

                view.add_item(cancle_button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def cancle_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def select_relationship_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer()

                    user_data = cache.users.get(str(ctx.author.id), {})

                    await storage.users.update(
                        id=user_data.get("id"),
                        user_id=ctx.author.id,
                        relationship=interaction.data["values"][0],
                    )

                    await interaction.message.edit(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            message = await ctx.send(embed=await get_embed(), view=await get_view())

            while not cancled:

                timeout_time -= 1

                if timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.hybrid_command(
        name="profile",
        help="Display a user's profile",
        with_app_command=True,
        aliases=["pr"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def profile(self, ctx, user: discord.Member = None):

        try:

            if ctx.interaction and not ctx.interaction.response:

                await ctx.defer()

            if not user:

                user = ctx.author

            # get the user's badges from the user's public flags as name

            # badges = [badge.name for badge in user.public_flags.all()]

            # badges_list = {

            #     "staff": "discordstaff",

            #     "partner": "discordpartner",

            #     "hypesquad": "hypesquadevents",

            #     "bug_hunter": "discordbughunter1",

            #     "mfa_sms": "supportscommands",

            #     "premium_promo_dismissed": "discordnitro",

            #     "hypesquad_bravery": "hypesquadbravery",

            #     "hypesquad_brilliance": "hypesquadbrilliance",

            #     "hypesquad_balance": "hypesquadbalance",

            #     "early_supporter": "discordearlysupporter",

            #     "team_user": "discordstaff",

            #     "system": "discordstaff",

            #     "has_unread_urgent_messages": "discordstaff",

            #     "bug_hunter_level_2": "discordbughunter2",

            #     "verified_bot": "discordbotdev",

            #     "verified_bot_developer": "discordbotdev",

            #     "discord_certified_moderator": "discordmod",

            #     "bot_http_interactions": "discordstaff",

            #     "spammer": "discordstaff",

            #     "active_developer": "activedeveloper"

            # }

            # badges = [badges_list[badge] for badge in badges if badge in badges_list]

            fetched_user = await self.bot.fetch_user(user.id)

            # Debugging: Log URLs and other details

            avatar_url = user.display_avatar.url

            banner_url = fetched_user.banner.url if fetched_user.banner else None

            # profile_image_byte = ui.get_ui_profile(

            #     avatar_url=avatar_url,

            #     banner_url=banner_url,

            #     display_name=user.display_name,

            #     username=user.name,

            #     coin=self.bot.cache.users.get(str(user.id),{}).get('balance',0),

            #     userid=str(user.id),

            #     created_at=user.created_at.astimezone(datetime.timezone.utc),

            #     badges=badges

            # )

            embed = discord.Embed(
                title=f"{user.display_name}'s Profile",
                description=f"""**{self.bot.emoji.RELATIONSHIP} Relationship:** `{self.bot.cache.users.get(str(user.id),{}).get('relationship','single').capitalize()}`






**{self.bot.emoji.CREATED} Created:** <t:{int(user.created_at.timestamp())}:d> <t:{int(user.created_at.timestamp())}:R>






**{self.bot.emoji.JOIN} Joined:** <t:{int(user.joined_at.timestamp())}:d> <t:{int(user.joined_at.timestamp())}:R>






""",
                color=user.accent_color,
            )

            embed.set_thumbnail(url=avatar_url)

            embed.set_image(url=banner_url)

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in profile command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.hybrid_command(
        name="avatar",
        with_app_command=True,
        help="Display a user's avatar",
        aliases=["av"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def avatar(self, ctx, user: discord.User = None):

        try:

            if ctx.interaction and not ctx.interaction.response:

                await ctx.defer()

            if not user:

                user = ctx.author

            avatar_url = user.display_avatar.url

            embed = discord.Embed(
                title=f"{user.display_name}'s Avatar", color=user.accent_color
            )

            embed.set_image(url=avatar_url)

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in avatar command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.hybrid_group(
        name="banner",
        with_app_command=True,
        help="Display a user's banner",
        invoke_without_command=True,
        usage=["<user>", "server"],
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def banner(self, ctx, user: discord.User = None):

        try:

            if ctx.interaction and not ctx.interaction.response:

                await ctx.defer()

            if not user:

                user = ctx.author

            user = await self.bot.fetch_user(user.id)

            if not user.banner:

                embed = discord.Embed(
                    description=f"{user.display_name} doesn't have a banner.",
                    color=color.red,
                )

                await ctx.send(embed=embed)

                return

            banner_url = user.banner.url

            embed = discord.Embed(
                title=f"{user.display_name}'s Banner", color=user.accent_color
            )

            embed.set_image(url=banner_url)

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in banner command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @banner.command(
        name="server",
        help="Display the server's banner",
        aliases=["guild"],
    )
    async def banner_server(self, ctx):

        try:

            if ctx.interaction and not ctx.interaction.response:

                await ctx.defer()

            guild = await self.bot.fetch_guild(ctx.guild.id)

            if not guild.banner:

                embed = discord.Embed(
                    description=f"This Server doesn't have a banner.", color=color.red
                )

                await ctx.send(embed=embed)

                return

            banner_url = guild.banner.url

            embed = discord.Embed(title=f"{guild.name}'s Banner", color=color.green)

            embed.set_image(url=banner_url)

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in banner command: {e}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.group(
        name="list",
        help="different list commands",
        aliases=["ls"],
        invoke_without_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list(self, ctx: commands.Context):

        embed = discord.Embed(
            title="List Commands",
            color=color.green,
            description="List of all the list commands\n\n",
        )

        if hasattr(ctx.command, "commands"):

            for command in ctx.command.commands:

                embed.description += f"**`{self.bot.BotConfig.PREFIX}{ctx.command} {command.name}`** : {command.help}\n"

        await ctx.send(embed=embed)

    @list.command(name="emojis", help="List all the emojis in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_emojis(self, ctx: commands.Context):

        try:

            emojis = ctx.guild.emojis

            if not emojis:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no emojis in this server",
                        color=color.red,
                    )
                )

            # make 5 by 5 grid of emojis

            emojis = [emojis[i : i + 10] for i in range(0, len(emojis), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Emojis",
                    color=color.green,
                    description="",
                )

                for emoji in emojis[current_page_index]:

                    embed.description += f"> - {emoji} - `{emoji.id}`\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(emojis)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(emojis) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="channels", help="List all the channels in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_channels(self, ctx: commands.Context):

        try:

            channels = ctx.guild.channels

            # make 5 by 5 grid of channels

            if not channels:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no channels in this server",
                        color=color.red,
                    )
                )

            channels = [channels[i : i + 10] for i in range(0, len(channels), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Channels",
                    color=color.green,
                    description="",
                )

                for channel in channels[current_page_index]:

                    embed.description += f"> - {channel.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(channels)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(channels) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="bots", help="List all the bots in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_bots(self, ctx: commands.Context):

        try:

            bots = [member for member in ctx.guild.members if member.bot]

            if not bots:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no bots in this server", color=color.red
                    )
                )

            # make 5 by 5 grid of bots

            bots = [bots[i : i + 10] for i in range(0, len(bots), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Bots", color=color.green, description=""
                )

                for bot in bots[current_page_index]:

                    embed.description += f"> - {bot.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(bots)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(bots) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="admins", help="List all the admins in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_admins(self, ctx: commands.Context):

        try:

            admins = [
                member
                for member in ctx.guild.members
                if member.guild_permissions.administrator and not member.bot
            ]

            if not admins:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no admins in this server",
                        color=color.red,
                    )
                )

            # make 5 by 5 grid of admins

            admins = [admins[i : i + 10] for i in range(0, len(admins), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Admins",
                    color=color.green,
                    description="",
                )

                for admin in admins[current_page_index]:

                    embed.description += f"> - {admin.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(admins)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(admins) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="bans", help="List all the bans in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_bans(self, ctx: commands.Context):

        try:

            bans = []

            async for ban in ctx.guild.bans(limit=None):

                bans.append(ban.user)

            if not bans:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no bans in this server", color=color.red
                    )
                )

            # make 5 by 5 grid of bans

            bans = [bans[i : i + 10] for i in range(0, len(bans), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Bans", color=color.green, description=""
                )

                for ban in bans[current_page_index]:

                    embed.description += f"> - {ban.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(bans)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(bans) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="roles", help="List all the roles in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_roles(self, ctx: commands.Context):

        try:

            roles = ctx.guild.roles

            if not roles:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no roles in this server", color=color.red
                    )
                )

            # make 5 by 5 grid of roles

            roles = [roles[i : i + 10] for i in range(0, len(roles), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Roles", color=color.green, description=""
                )

                for role in roles[current_page_index]:

                    embed.description += f"> - {role.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(roles)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(roles) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="boosters", help="List all the boosters in the server")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_boosters(self, ctx: commands.Context):

        try:

            boosters = ctx.guild.premium_subscribers

            if not boosters:

                return await ctx.send(
                    embed=discord.Embed(
                        description="There are no boosters in this server",
                        color=color.red,
                    )
                )

            # make 5 by 5 grid of boosters

            boosters = [boosters[i : i + 10] for i in range(0, len(boosters), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"{ctx.guild.name}'s Boosters",
                    color=color.green,
                    description="",
                )

                for booster in boosters[current_page_index]:

                    embed.description += f"> - {booster.mention}\n"

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(boosters)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(boosters) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @list.command(name="inrole", help="List all the members in a role")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def list_inrole(self, ctx: commands.Context, role: discord.Role):

        try:

            members = role.members

            if not members:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"There are no members in the {role.mention} role",
                        color=color.red,
                    )
                )

            # make 5 by 5 grid of members

            members = [members[i : i + 10] for i in range(0, len(members), 10)]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                embed = discord.Embed(
                    title=f"Members in the {role.name} role",
                    color=color.green,
                    description="",
                )

                i = 1

                for member in members[current_page_index]:

                    embed.description += f"{i} • {member.mention} - `{member.id}`\n"

                    i += 1

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(members)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                if len(members) == 1:

                    nonlocal cancled

                    cancled = True

                    return None

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                previous_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.PREVIOUS,
                    row=0,
                    disabled=current_page_index <= 0,
                )

                previous_button.callback = lambda i: previous_button_callback(i)

                stop_button = discord.ui.Button(
                    style=discord.ButtonStyle.red, emoji=self.bot.emoji.STOP, row=0
                )

                stop_button.callback = lambda i: stop_button_callback(i)

                next_button = discord.ui.Button(
                    style=discord.ButtonStyle.blurple,
                    emoji=self.bot.emoji.NEXT,
                    row=0,
                    disabled=current_page_index >= len(members) - 1,
                )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal cancled

                    cancled = True

                    await interaction.response.edit_message(view=await get_view(True))

                except Exception as e:

                    logger.error(
                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                    )

            async def next_button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

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

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.command(name="uptime", help="Get the uptime of the bot")
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def uptime(self, ctx: commands.Context):

        try:

            uptime = (
                datetime.datetime.now(tz=datetime.timezone.utc) - self.bot.start_time
            ).total_seconds()

            # convert the uptime to days, hours, minutes and seconds

            uptime_text = ""

            if uptime >= 86400:

                uptime_text += f"{int(uptime/86400)}d "

                uptime %= 86400

            if uptime >= 3600:

                uptime_text += f"{int(uptime/3600)}h "

                uptime %= 3600

            if uptime >= 60:

                uptime_text += f"{int(uptime/60)}m "

                uptime %= 60

            uptime_text += f"{int(uptime)}s"

            await ctx.send(
                embed=discord.Embed(
                    title="Uptime",
                    color=color.green,
                    description=f"```\n{uptime_text}```",
                )
            )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.command(name="roleicon", help="Set a role icon", aliases=["roleemoji"])
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def roleicon(
        self, ctx: commands.Context, role: discord.Role, emoji: discord.PartialEmoji
    ):

        try:

            if not await checks.check_is_moderator_permissions(ctx, "manage_roles"):

                return

            if not await checks.check_if_user_can_manage_this_role(ctx, role):

                return

            if ctx.guild.premium_tier < 2:

                return await ctx.send(
                    embed=discord.Embed(
                        description="You need to have server boost level 2 to use this command",
                        color=color.red,
                    )
                )

            try:

                def get_image_byte_by_url(url):

                    return requests.get(url).content

                await role.edit(display_icon=get_image_byte_by_url(emoji.url))

                await ctx.send(
                    embed=discord.Embed(
                        description=f"Role icon for {role.mention} has been Changed",
                        color=color.green,
                    ).set_image(
                        url=role.display_icon.url if role.display_icon else None
                    )
                )

            except discord.HTTPException as e:

                await ctx.send(
                    embed=discord.Embed(
                        description=f"An error occurred while setting the role icon for {role.mention}",
                        color=color.red,
                    )
                )

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.hybrid_command(
        name="serverinfo",
        help="Get information about the server",
        aliases=["guildinfo", "si", "gi"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def serverinfo(self, ctx: commands.Context):

        try:

            guild_cache = self.bot.cache.guilds.get(str(ctx.guild.id), {})

            subscription = guild_cache.get("subscription", "free")

            subscription_end = guild_cache.get("subscription_end", None)

            message = await ctx.send(
                embed=discord.Embed(
                    description="Fetching server information...", color=color.green
                )
            )

            # Server Name : reo test server

            # Server ID : 1267073544928366677

            # Server Region : Us-Central

            # Owner Name : CheckMate

            # Owner ID : 1058254151810830357

            # Owner Mention : @CheckMate

            # Created : July 28, 2024 4:57 PM

            # Members Count : 14 Humans, 22 Bots

            # Bans Count : 5

            # Preferred Locale : English (United States)

            # Upload Limit : 26.2 MB

            # Vanity invite Code : None

            # Invites Disabled : False

            # Invites Background : Not Set

            # Discovery Splash URL : Not Set

            # :MekoUtility: Server Settings

            # Widget Enabled : False

            # Widget Channel : Not Set

            # Verification Level : Low

            # Default Message Notifications : Only Mentions

            # Explicit Media Content Filter : All Members

            # Nsfw Level : Default

            # MFA Requirement : :MekoCross:

            # System Welcome Messages : :MekoCheck:

            # Join Sticker Reply Buttons : :MekoCheck:

            # System Boost Messages : :MekoCheck:

            # Server Setup Tips : :MekoCheck:

            # Inactive Timeout : 5 minutes

            # Inactive Channel :  voice-2

            # Safety Alerts Channel : Not set

            # Discord Updates Channel :  leave_member

            # System Messages Channel :  general

            # Rules channel : testing

            # :MekoSticker: Emojis & Stickers Info

            # Static Emoji : 50/50

            # Animated Emoji : 20/50

            # Total Emoji : 70/100

            # Total Stickers : 2/5

            # :MekoBoost: Boost Status

            # Level : 0

            # Boost Count : 0

            # Booster Role : None

            # Boost Bar : :MekoCross:

            # :MekoCategory: Channels

            # Total : 144

            # Text : 122 (7 Locked)

            # Voice : 5 (0 Locked)

            # Stage: 0 (0 Locked)

            # Categories : 17 (0 Locked)

            # :MekoRoleGreen: Server Roles

            # Total : 41

            # Normal : 18

            # Integrated : 23

            ban_count = 0

            async for ban in ctx.guild.bans(limit=101):

                ban_count += 1

            if ban_count > 100:

                ban_count = "100+"

            paged_data = [
                {
                    "image": ctx.guild.banner.url if ctx.guild.banner else None,
                    "embed": discord.Embed(
                        title=f"{self.bot.emoji.INFO} About Server",
                        description=f"""**Server Name:** {ctx.guild.name}






**Server ID:** `{ctx.guild.id}`






**Owner Name:** {ctx.guild.owner}






**Owner ID:** `{ctx.guild.owner.id}`






**Owner Mention:** {ctx.guild.owner.mention}






**Created:** <t:{int(ctx.guild.created_at.timestamp())}:d> <t:{int(ctx.guild.created_at.timestamp())}:R>






**Members Count:** `{len(ctx.guild.members)} Humans, {len([member for member in ctx.guild.members if member.bot])} Bots`






**Bans Count:** `{ban_count}`






**Preferred Locale:** `{ctx.guild.preferred_locale}`






**Upload Limit:** `{round(ctx.guild.filesize_limit/1024/1024,1)} MB`






**Vanity invite Code:** `{ctx.guild.vanity_url_code if ctx.guild.vanity_url_code else '`Not Set`'}`






**Invites Disabled:** `{ctx.guild.explicit_content_filter}`






**Discovery Splash URL:** {'[Click Here]('+ctx.guild.discovery_splash.url+')' if ctx.guild.discovery_splash else '`Not Set`'}""",
                        color=color.black,
                    ),
                    "thumbnail": (
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    ),
                    "button": {
                        "name": "About",
                        "style": discord.ButtonStyle.blurple,
                        "emoji": self.bot.emoji.INFO,
                    },
                },
                {
                    "embed": discord.Embed(
                        title=f"{self.bot.emoji.SETTINGS} Server Settings",
                        description=f"""**Widget Enabled:** `{ctx.guild.widget_enabled}`






**Widget Channel:** {ctx.guild.widget_channel.mention if ctx.guild.widget_channel else '`Not Set`'}






**Verification Level:** `{ctx.guild.verification_level}`






**Default Message Notifications:** `{ctx.guild.default_notifications.name.capitalize().replace("_"," ")}`






**Explicit Media Content Filter:** `{ctx.guild.explicit_content_filter}`






**Nsfw Level:** `{ctx.guild.nsfw_level.name.capitalize()}`






**MFA Requirement:** {self.bot.emoji.NO if ctx.guild.mfa_level == 0 else self.bot.emoji.YES}






**System Welcome Messages:** {self.bot.emoji.YES if ctx.guild.system_channel_flags.join_notifications else self.bot.emoji.NO}






**Inactive Timeout:** `{ctx.guild.afk_timeout/60} minutes`






**Inactive Channel:** {ctx.guild.afk_channel.mention if ctx.guild.afk_channel else '`Not Set`'}






**Safety Alerts Channel:** {ctx.guild.system_channel.mention if ctx.guild.system_channel else '`Not Set`'}






**Discord Updates Channel:** {ctx.guild.public_updates_channel.mention if ctx.guild.public_updates_channel else '`Not Set`'}






**System Messages Channel:** {ctx.guild.system_channel.mention if ctx.guild.system_channel else '`Not Set`'}






**Rules channel:** {ctx.guild.rules_channel.mention if ctx.guild.rules_channel else '`Not Set`'}""",
                        color=color.black,
                    ),
                    "thumbnail": (
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    ),
                    "button": {
                        "name": "Settings",
                        "style": discord.ButtonStyle.blurple,
                        "emoji": self.bot.emoji.SETTINGS,
                    },
                },
                {
                    "embed": discord.Embed(
                        title=f"{self.bot.emoji.EMOJI} Emojis & Stickers & Boost",
                        description=f"""**Static Emoji:** `{len([emoji for emoji in ctx.guild.emojis if not emoji.animated])}/{ctx.guild.emoji_limit}`






**Animated Emoji:** `{len([emoji for emoji in ctx.guild.emojis if emoji.animated])}/{ctx.guild.emoji_limit}`






**Total Emoji:** `{len(ctx.guild.emojis)}/{ctx.guild.emoji_limit}`






**Total Stickers:** `{len(ctx.guild.stickers)}/{ctx.guild.sticker_limit}`













**Boost Level:** `{ctx.guild.premium_tier}`






**Boost Count:** `{ctx.guild.premium_subscription_count}`






**Booster Role:** {ctx.guild.premium_subscriber_role.mention if ctx.guild.premium_subscriber_role else '`None`'}






**Boost Bar:** {self.bot.emoji.YES if ctx.guild.premium_subscription_count >= 2 else self.bot.emoji.NO}""",
                        color=color.black,
                    ),
                    "thumbnail": (
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    ),
                    "button": {
                        "name": "Features",
                        "style": discord.ButtonStyle.blurple,
                        "emoji": self.bot.emoji.EMOJI,
                    },
                },
                {
                    "embed": discord.Embed(
                        title=f"{self.bot.emoji.CATEGORY} Channels & Roles",
                        description=f"""**Total Channels:** {len(ctx.guild.channels)}






**Text Channels:** {len([channel for channel in ctx.guild.text_channels])} ({len([channel for channel in ctx.guild.text_channels if channel.overwrites_for(ctx.guild.default_role).read_messages])} Locked)






**Voice Channels:** {len([channel for channel in ctx.guild.voice_channels])} ({len([channel for channel in ctx.guild.voice_channels if channel.overwrites_for(ctx.guild.default_role).connect])} Locked)






**Stage Channels:** {len([channel for channel in ctx.guild.stage_channels])} ({len([channel for channel in ctx.guild.stage_channels if channel.overwrites_for(ctx.guild.default_role).connect])} Locked)






**Categories:** {len([channel for channel in ctx.guild.categories])} ({len([channel for channel in ctx.guild.categories if channel.overwrites_for(ctx.guild.default_role).read_messages])} Locked)













**Total Roles:** {len(ctx.guild.roles)}






**Normal Roles:** {len([role for role in ctx.guild.roles if not role.managed])}






**Integrated Roles:** {len([role for role in ctx.guild.roles if role.managed])}""",
                        color=color.black,
                    ),
                    "thumbnail": (
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    ),
                    "button": {
                        "name": "Extras",
                        "style": discord.ButtonStyle.blurple,
                        "emoji": self.bot.emoji.CATEGORY,
                    },
                },
                #                 {
                #                     "embed":discord.Embed(
                #                         title="Subscription Status",
                #                         description=f"""**{self.bot.emoji.PREMIUM} Subscription:** `{subscription.capitalize().replace("_"," ")}`
                # **{self.bot.emoji.TIME} Subscription End:** {f'<t:{int(subscription_end.timestamp())}:R>' if subscription_end else '`Never`'}""",
                #                         color=color.black
                #                     ),
                #                     "thumbnail":ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url,
                #                     "button":{
                #                         "name":"Subscription",
                #                         "style":discord.ButtonStyle.green,
                #                         "emoji":self.bot.emoji.PREMIUM
                #                     }
                #                 }
            ]

            current_page_index = 0

            view_timeout_time = 60

            cancled = False

            def reset_timeout_time(timeout: int = 60):

                nonlocal view_timeout_time

                view_timeout_time = timeout

            async def get_embed():

                nonlocal current_page_index

                if current_page_index >= len(paged_data):

                    current_page_index = 0

                data = paged_data[current_page_index]

                embed = data.get(
                    "embed",
                    discord.Embed(
                        description="An error occurred while processing the command"
                    ),
                )

                embed.set_author(
                    name=ctx.guild.name,
                    icon_url=(
                        ctx.guild.icon.url
                        if ctx.guild.icon
                        else self.bot.user.display_avatar.url
                    ),
                )

                embed.set_thumbnail(url=data.get("thumbnail", None))

                embed.set_image(url=data.get("image", None))

                embed.set_footer(
                    text=f"{current_page_index+1}/{len(paged_data)}",
                    icon_url=ctx.author.display_avatar.url,
                )

                return embed

            async def get_view(disabled=False):

                view = discord.ui.View(timeout=60)

                reset_timeout_time()

                i = 0

                for page in paged_data:

                    button = discord.ui.Button(
                        style=page.get("button", {}).get(
                            "style", discord.ButtonStyle.blurple
                        ),
                        label=page.get("button", {}).get("name", ""),
                        disabled=page == paged_data[current_page_index],
                        custom_id=str(i),
                    )

                    i += 1

                    button.callback = lambda i: button_callback(i)

                    view.add_item(button)

                if disabled:

                    for item in view.children:

                        item.disabled = True

                return view

            async def button_callback(interaction: discord.Interaction):

                try:

                    if interaction.user.id != ctx.author.id:

                        return await interaction.response.send_message(
                            embed=discord.Embed(
                                description="You Can't Interact With This Button",
                                color=color.red,
                            ),
                            ephemeral=True,
                            delete_after=10,
                        )

                    nonlocal current_page_index

                    current_page_index = int(interaction.data["custom_id"])

                    await interaction.response.edit_message(
                        embed=await get_embed(), view=await get_view()
                    )

                except Exception as e:

                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            message = await message.edit(embed=await get_embed(), view=await get_view())

            while not cancled:

                view_timeout_time -= 1

                if view_timeout_time <= 0:

                    await message.edit(view=await get_view(True))

                    break

                await asyncio.sleep(1)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.hybrid_command(
        name="userinfo",
        help="Get information about a user",
        aliases=["ui", "whois"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def userinfo(self, ctx: commands.Context, user: discord.User = None):

        try:

            if not user:

                user = ctx.author

            if not user:

                return await ctx.send(
                    embed=discord.Embed(description="User not found", color=color.red)
                )

            embed = discord.Embed(
                description=f"""**Name:** {user.mention}






**Global Name:** {user.global_name}






**Display Name:** {user.display_name}






**ID:** `{user.id}`






**Bot:** {self.bot.emoji.YES if user.bot else self.bot.emoji.NO}






**Account Created At:** <t:{int(user.created_at.timestamp())}:F>






""",
                color=user.accent_color if user.accent_color else color.black,
            )

            try:

                member = ctx.guild.get_member(user.id)

            except:

                member = None

            if member:

                permission_names = [
                    perm for perm, value in member.guild_permissions if value
                ]

                if member.guild_permissions.administrator:

                    guild_permissions_text = "Administrator"

                elif not permission_names:

                    guild_permissions_text = "No Permissions"

                elif len(permission_names) < 25:

                    guild_permissions_text = " | ".join(permission_names)

                else:

                    guild_permissions_text = (
                        " | ".join(permission_names[:25])
                        + f" and {len(permission_names) - 25} more"
                    )

                embed.description += f"""\n**Guild Joined At:** <t:{int(member.joined_at.timestamp())}:F>






**Status:** `{str(member.status).capitalize()}`













**__Guild Permissions:__** ```\n{guild_permissions_text}```"""

            embed.set_thumbnail(url=user.display_avatar.url)

            embed.set_image(url=user.banner.url if user.banner else None)

            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )

            embed.set_author(name=user.name, icon_url=user.display_avatar.url)

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.command(
        name="roleinfo", help="Get information about a role", aliases=["ri"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):

        try:

            embed = discord.Embed(color=role.color)

            embed.set_author(
                name=role.name,
                icon_url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                ),
            )

            embed.add_field(
                name=f"{self.bot.emoji.GENERAL} __General info__",
                value=f"""> **{self.bot.emoji.NAME} Name:** {role.mention}






> {self.bot.emoji.ID} Id: `{role.id}`






> {self.bot.emoji.POSITION} Position: `{role.position}`






> {self.bot.emoji.MENTIONABLE} Mentionable: {self.bot.emoji.YES if role.mentionable else self.bot.emoji.NO}






> {self.bot.emoji.HOIST} Hoist: {self.bot.emoji.YES if role.hoist else self.bot.emoji.NO}






> {self.bot.emoji.MANAGED} Managed By Bot: {self.bot.emoji.YES if role.managed else self.bot.emoji.NO}






> {self.bot.emoji.COLOR} Color: `{role.color}`






> {self.bot.emoji.MEMBERS} Members: `{len(role.members)}`






> {self.bot.emoji.CREATED} Created At: <t:{int(role.created_at.timestamp())}:F>""",
                inline=False,
            )

            embed.add_field(
                name=f"{self.bot.emoji.PERMISSIONS} __Permissions__",
                value=(
                    "```\n"
                    + (
                        "Administrator"
                        if role.permissions.administrator
                        else (
                            " | ".join(
                                [perm for perm, value in role.permissions if value]
                            )
                            if len([perm for perm, value in role.permissions if value])
                            < 25
                            else " | ".join(
                                [perm for perm, value in role.permissions if value][:25]
                            )
                            + f" and {len([perm for perm, value in role.permissions if value]) - 25} more"
                        )
                    )
                    + "```"
                    if role.permissions
                    else "No Permissions"
                ),
                inline=False,
            )

            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon_url=ctx.author.display_avatar.url,
            )

            await ctx.send(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.hybrid_command(
        name="membercount",
        help="Get the member count of the server",
        aliases=["mc"],
        with_app_command=True,
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def membercount(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                description=f"```prolog\n{ctx.guild.member_count}```", color=color.black
            )

            embed.set_author(
                name=ctx.guild.name,
                icon_url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                ),
            )

            embed.set_footer(
                text=f"Online: {len([member for member in ctx.guild.members if str(member.status).lower() == 'online'])} | Offline: {len([member for member in ctx.guild.members if str(member.status).lower() == 'offline'])} | DND: {len([member for member in ctx.guild.members if str(member.status).lower() == 'dnd'])} | Idle: {len([member for member in ctx.guild.members if str(member.status).lower() == 'idle'])}",
                icon_url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                ),
            )

            await ctx.reply(f"{ctx.guild.member_count}")

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.command(
        name="firstmessage", help="Get the first message of a channel", aliases=["fm"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def firstmessage(
        self, ctx: commands.Context, channel: discord.TextChannel = None
    ):

        try:

            if not channel:

                channel = ctx.channel

            first_message = None

            async for message in channel.history(limit=1, oldest_first=True):

                first_message = message

            if not first_message:

                return await ctx.send(
                    embed=discord.Embed(
                        description=f"No messages found in {channel.mention}",
                        color=color.red,
                    )
                )

            embed = discord.Embed(
                description=f"First message found in {channel.mention}",
                color=color.green,
            )

            view = discord.ui.View()

            message_url_button = discord.ui.Button(
                style=discord.ButtonStyle.url,
                label="Click to View",
                url=first_message.jump_url,
            )

            view.add_item(message_url_button)

            await ctx.send(embed=embed, view=view)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )

    @commands.command(
        name="boostcount", help="Get the boost count of the server", aliases=["bc"]
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=2, per=15, type=commands.BucketType.user)
    async def boostcount(self, ctx: commands.Context):

        try:

            embed = discord.Embed(
                description=f"```prolog\n{ctx.guild.premium_subscription_count}```",
                color=color.black,
            )

            embed.set_author(
                name=ctx.guild.name,
                icon_url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                ),
            )

            embed.set_footer(
                text=f"Boost Level: {ctx.guild.premium_tier}",
                icon_url=(
                    ctx.guild.icon.url
                    if ctx.guild.icon
                    else self.bot.user.display_avatar.url
                ),
            )

            await ctx.reply(embed=embed)

        except Exception as e:

            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

            await ctx.send(
                "An error occurred while processing the command.", delete_after=5
            )
