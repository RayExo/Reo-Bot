import discord


from discord.ext import commands


import storage.afk


from reo.console.logging import logger


from reo.memory.cache import cache


from reo.style import color


from reo.utils import pings


from collections import defaultdict


import time


import re


import json


from reo.src.checks import checks


from reo.config.config import BotConfigClass


BotConfig = BotConfigClass()


import traceback, sys


import asyncio


import storage


import datetime


from reo.engine.Bot import AutoShardedBot


check_for_owner_first_time_message_in_guild_cache = (
    {}
)  # guild_id: [owner_id1,owner_id2]


class message(commands.Cog):

    def __init__(self, bot):

        self.bot: AutoShardedBot = bot

        self.user_messages = defaultdict(lambda: defaultdict(int))

        self.user_last_message_time = defaultdict(lambda: time.time())

        self.user_message_counts = defaultdict(int)

        self.user_message_timestamps = defaultdict(float)

        self.MusicCog = self.bot.get_cog("Music")

    async def check_for_afk(self, message: discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        try:

            if message.author.bot:

                return

            if not message.guild:

                return

            global_afk = cache.afk.get("global", {}).get(str(message.author.id), {})

            if global_afk:

                await storage.afk.delete(user_id=message.author.id)

                created_at: datetime.datetime = global_afk.get("created_at")

                embed = discord.Embed(
                    description=f"**You are no longer Globally AFK**", color=color.green
                )

                was_afk_for_seconds = (
                    datetime.datetime.now(tz=datetime.timezone.utc) - created_at
                ).total_seconds()

                def fetch_seconds(seconds):

                    hours, remainder = divmod(seconds, 3600)

                    minutes, seconds = divmod(remainder, 60)

                    return int(hours), int(minutes), int(seconds)

                hours, minutes, seconds = fetch_seconds(was_afk_for_seconds)

                was_afk_for = ""

                if hours:

                    was_afk_for += f"{hours} hours "

                if minutes:

                    was_afk_for += f"{minutes} minutes "

                if seconds:

                    was_afk_for += f"{seconds} seconds "

                embed.set_footer(
                    text=f"Was afk for: {was_afk_for}",
                )

                await message.reply(embed=embed)

            guild_afk = (
                cache.afk.get("guilds", {})
                .get(str(message.guild.id), {})
                .get(str(message.author.id), {})
            )

            if guild_afk:

                await storage.afk.delete(
                    guild_id=message.guild.id, user_id=message.author.id
                )

                created_at: datetime.datetime = guild_afk.get("created_at").astimezone()

                embed = discord.Embed(
                    description=f"**You are no longer AFK in this server**",
                    color=color.green,
                )

                was_afk_for_seconds = (
                    datetime.datetime.now().astimezone() - created_at
                ).total_seconds()

                def fetch_seconds(seconds):

                    hours, remainder = divmod(seconds, 3600)

                    minutes, seconds = divmod(remainder, 60)

                    return int(hours), int(minutes), int(seconds)

                hours, minutes, seconds = fetch_seconds(was_afk_for_seconds)

                was_afk_for = ""

                if hours:

                    was_afk_for += f"{hours} hours "

                if minutes:

                    was_afk_for += f"{minutes} minutes "

                if seconds:

                    was_afk_for += f"{seconds} seconds "

                embed.set_footer(
                    text=f"Was afk for: {was_afk_for}",
                )

                await message.reply(embed=embed)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def check_afk_user_mention(self, message: discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        try:

            if not message.mentions:

                return

            for user in message.mentions:

                if user.bot:

                    return

                global_afk = cache.afk.get("global", {}).get(str(user.id), {})

                if global_afk:

                    await storage.afk.update(
                        id=global_afk.get("id"),
                        user_id=user.id,
                        mentioned=global_afk.get("mentioned", 0) + 1,
                    )

                    created_at: datetime.datetime = global_afk.get("created_at")

                    text = f"**{user.display_name}** is Globally AFK: {global_afk.get('reason','`Without reason`')} - <t:{int(created_at.timestamp())}:R>"

                    await message.reply(content=text)

                guild_afk = (
                    cache.afk.get("guilds", {})
                    .get(str(message.guild.id), {})
                    .get(str(user.id), {})
                )

                if guild_afk:

                    await storage.afk.update(
                        id=guild_afk.get("id"),
                        guild_id=message.guild.id,
                        user_id=user.id,
                        mentioned=guild_afk.get("mentioned", 0) + 1,
                    )

                    created_at: datetime.datetime = guild_afk.get("created_at")

                    text = f"**{user.display_name}** is AFK in this server: {guild_afk.get('reason','`Without reason`')} - <t:{int(created_at.timestamp())}:R>"

                    await message.reply(content=text)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

        # async def check_for_bot_mention(self,message:discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        if message.content == self.bot.user.mention:

            DEFAULT_PREFIX = BotConfig.PREFIX

            guild_cache = cache.guilds.get(str(message.guild.id), {})

            guild_prefix = guild_cache.get("prefix", DEFAULT_PREFIX)

            embed = discord.Embed(
                title=f"✨ Hey {message.author.display_name}!",
                color=color.aqua,
                description=(
                    f"> Use `{guild_prefix}help` to get the command list\n"
                    f"> Use the REO support hub if you need setup help or troubleshooting\n\n"
                    f"-# Powered by REO"
                ),
            )

            embed.set_footer(
                text="REO • CodeX Development",
                icon_url=self.bot.user.display_avatar.url,
            )

            view = discord.ui.View()

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.url,
                    label="Invite Me",
                    url=self.bot.urls.INVITE,
                    row=0,
                )
            )

            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.url,
                    label="Support Server",
                    url=self.bot.urls.SUPPORT_SERVER,
                    row=0,
                )
            )

            await message.reply(embed=embed, view=view)

    async def antispam_punishment(
        self, message: discord.Message, data: dict, delete_limit: int = 5
    ):

        try:

            PUNISHMENT = data.get("antispam_punishment", "warn")

            PUNISHMENT_DURATION = data.get("antispam_punishment_duration", 0)

            try:

                asyncio.create_task(
                    message.channel.purge(
                        limit=delete_limit, check=lambda m: m.author == message.author
                    )
                )

            except:

                pass

            if PUNISHMENT == "warn":

                await message.reply(
                    embed=discord.Embed(
                        description=f"**{message.author} has been warned for spamming**",
                        color=color.red,
                    )
                )

            elif PUNISHMENT == "mute":

                await message.channel.send(
                    embed=discord.Embed(
                        description=f"**{message.author} has been muted for spamming**",
                        color=color.red,
                    )
                )

                # timed_out_until must be an aware datetime. Consider using discord.utils.utcnow() or datetime.datetime.now().astimezone() for local time.

                await message.author.edit(
                    timed_out_until=datetime.datetime.now().astimezone()
                    + datetime.timedelta(seconds=PUNISHMENT_DURATION)
                )

            elif PUNISHMENT == "kick":

                await message.channel.send(
                    embed=discord.Embed(
                        description=f"**{message.author} has been kicked for spamming**",
                        color=color.red,
                    )
                )

                await message.author.kick(reason="Spamming")

            elif PUNISHMENT == "ban":

                await message.channel.send(
                    embed=discord.Embed(
                        description=f"**{message.author} has been banned for spamming**",
                        color=color.red,
                    )
                )

                await message.author.ban(reason="Spamming")

            elif PUNISHMENT == "tempban":

                await message.channel.send(
                    embed=discord.Embed(
                        description=f"**{message.author} has been banned for spamming**",
                        color=color.red,
                    )
                )

                await message.author.ban(
                    reason="Spamming", delete_message_days=PUNISHMENT_DURATION
                )

            return True

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            return False

    async def antiduplicate_module(self, message: discord.Message, data: dict):

        logger.info("Checking for duplicate messages")

        try:

            MESSAGE_THRESHOLD = data.get("antispam_max_messages", 5)

            CLEANUP_INTERVAL = data.get("antispam_max_interval", 10)

            def check_message(user_id, message_content):

                current_time = time.time()

                # Cleanup old messages

                if (
                    current_time - self.user_last_message_time[user_id]
                    > CLEANUP_INTERVAL
                ):

                    self.user_messages[user_id] = defaultdict(int)

                    self.user_last_message_time[user_id] = current_time

                # Update message count

                self.user_messages[user_id][message_content] += 1

                # Check for spam

                if self.user_messages[user_id][message_content] >= MESSAGE_THRESHOLD:

                    return True  # Spam detected

                return False  # No spam

            if check_message(message.author.id, message.content):

                if await self.antispam_punishment(
                    message, data, delete_limit=MESSAGE_THRESHOLD
                ):

                    return True

                return True

            return False

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            return False

    async def antispam_module(self, message: discord.Message, data: dict):

        logger.info("Checking for spam messages")

        try:

            MESSAGE_THRESHOLD = data.get("antispam_max_messages", 5)

            CLEANUP_INTERVAL = data.get("antispam_max_interval", 10)

            user_id = message.author.id

            current_time = time.time()

            # Initialize or reset user message count if the interval has passed

            if current_time - self.user_message_timestamps[user_id] > CLEANUP_INTERVAL:

                self.user_message_counts[user_id] = 0

                self.user_message_timestamps[user_id] = current_time

            # Increment message count for the user

            self.user_message_counts[user_id] += 1

            # Check for spam

            if self.user_message_counts[user_id] >= MESSAGE_THRESHOLD:

                if await self.antispam_punishment(
                    message, data, delete_limit=MESSAGE_THRESHOLD
                ):

                    return True

                return True

            return False

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            return False

    async def anti_mass_mentions(self, message: discord.Message, data: dict):

        logger.info("Checking for mass mentions")

        try:

            MENTION_THRESHOLD = data.get("antispam_max_mentions", 5)

            if len(message.mentions) + len(message.role_mentions) >= MENTION_THRESHOLD:

                if await self.antispam_punishment(message, data, delete_limit=1):

                    return True

                return True

            return False

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            return False

    async def anti_mass_emojis(self, message: discord.Message, data: dict):

        logger.info("Checking for mass emojis")

        try:

            EMOJI_THRESHOLD = data.get("antispam_max_emojis", 5)

            emoji_count = len(re.findall(r"<a?:\w+:\d+>", message.content))

            if emoji_count >= EMOJI_THRESHOLD:

                if await self.antispam_punishment(message, data, delete_limit=1):

                    return True

                return True

            return False

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            return False

    async def anti_mass_caps(self, message: discord.Message, data: dict):

        logger.info("Checking for mass caps")

        try:

            CAPS_THRESHOLD = data.get(
                "antispam_max_caps", 50
            )  # percentage of uppercase letters

            def uppercase_percentage(message: str) -> float:

                total_chars = len(message)

                if total_chars == 0:

                    return 0

                uppercase_chars = sum(1 for c in message if c.isupper())

                return (uppercase_chars / total_chars) * 100

            # check if many CAPITAL letters in same word

            if len(message.content) >= 8:

                if uppercase_percentage(message.content) >= CAPS_THRESHOLD:

                    if await self.antispam_punishment(message, data, delete_limit=1):

                        return True

                    return True

            return False

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

            return False

    async def check_automod(self, message: discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        try:

            if message.author == self.bot.user:

                logger.info("Message author is me, skipping automod")

                return

            guild_cache = cache.automod.get(str(message.guild.id), {})

            if not guild_cache:

                return

            if not guild_cache.get("antispam_enabled", False):

                logger.info("Antispam is disabled for this guild")

                return

            if await checks.check_is_owner_raw(message.author, message.guild):

                logger.info("Message author is guild owner, skipping automod")

                return

            if message.author.guild_permissions.administrator:

                logger.info("Message author has admin permissions, skipping automod")

                return

            if message.author.guild_permissions.manage_messages:

                logger.info(
                    "Message author has manage messages permissions, skipping automod"
                )

                return

            if message.author.guild_permissions.manage_guild:

                logger.info(
                    "Message author has manage guild permissions, skipping automod"
                )

                return

            if message.author.guild_permissions.manage_roles:

                logger.info(
                    "Message author has manage roles permissions, skipping automod"
                )

                return

            if message.author.guild_permissions.manage_channels:

                logger.info(
                    "Message author has manage channels permissions, skipping automod"
                )

                return

            whitelist_roles = guild_cache.get("antispam_whitelist_roles", [])  # ids
            whitelist_channels = guild_cache.get("antispam_whitelist_channels", [])  # ids

            if message.channel.id in whitelist_channels:

                logger.info("Message channel is whitelisted, skipping automod")

                return

            if any(role.id in whitelist_roles for role in message.author.roles):

                logger.info("Message author has a whitelisted role, skipping automod")

                return

            if await self.antiduplicate_module(message, guild_cache):

                return logger.info("Detected spam message, deleted and warned user")

            elif await self.antispam_module(message, guild_cache):

                return logger.info("Detected spam message, deleted and warned user")

            elif await self.anti_mass_mentions(message, guild_cache):

                return logger.info("Detected mass mentions, deleted and warned user")

            elif await self.anti_mass_emojis(message, guild_cache):

                return logger.info("Detected mass emojis, deleted and warned user")

            elif await self.anti_mass_caps(message, guild_cache):

                return logger.info("Detected mass caps, deleted and warned user")

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    role_command_usage = {}

    async def custom_role_command(self, message: discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        try:

            custom_roles_cache = cache.custom_roles.get(str(message.guild.id), {})

            custom_roles_permissions_cache = cache.custom_roles_permissions.get(
                str(message.guild.id), {}
            )

            if not custom_roles_cache:

                return

            # if first word of content in custom_roles_cache

            if not custom_roles_cache.get(message.content.split()[0].lower()):

                return

            # example of custom_roles_command: vip @user or id

            member = (
                await message.guild.fetch_member(
                    int(
                        message.content.split()[1]
                        .replace("<@", "")
                        .replace(">", "")
                        .replace("!", "")
                    )
                )
                if message.mentions
                else (
                    await message.guild.fetch_member(int(message.content.split()[1]))
                    if len(message.content.split()) > 1
                    else None
                )
            )

            if not member:

                return logger.error(f"Member not found for custom role command")

            if not await checks.check_is_owner_raw(member, message.guild):

                if not custom_roles_permissions_cache:

                    return logger.warning(
                        f"Custom roles permissions not found for guild {message.guild.id}"
                    )

                if not any(
                    role.id == custom_roles_permissions_cache.get("required_role_id")
                    for role in message.author.roles
                ):

                    return logger.error(
                        f"User does not have required role to use custom role command"
                    )

            guilds_subscription = cache.guilds.get(str(message.guild.id), {}).get(
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

            if len(custom_roles_cache) > customrole_limit:

                return await message.reply(
                    embed=discord.Embed(
                        description=f"**Your guild has reached the limit of {customrole_limit} custom roles\nYou need to delete {len(custom_roles_cache) - customrole_limit} custom roles to use this command**",
                        color=color.red,
                    ),
                    delete_after=10,
                )

            # Get the user ID

            user_id = message.author.id

            current_time = time.time()

            # Initialize usage data for the user if not present

            if user_id not in self.role_command_usage:

                self.role_command_usage[user_id] = []

            cooldown = 10

            # Filter out timestamps older than 60 seconds

            self.role_command_usage[user_id] = [
                timestamp
                for timestamp in self.role_command_usage[user_id]
                if current_time - timestamp < cooldown
            ]

            # Check if the user has already used the command twice in the last 60 seconds

            if len(self.role_command_usage[user_id]) >= 2:

                # calculate retry time

                retry_after = cooldown - (
                    current_time - self.role_command_usage[user_id][0]
                )

                return await message.reply(
                    embed=discord.Embed(
                        description=f"**You are on cooldown for using the custom role command. Please try again <t:{int(current_time + retry_after)}:R>**",
                        color=color.red,
                    ),
                    delete_after=retry_after,
                )

            # Add the current usage timestamp

            self.role_command_usage[user_id].append(current_time)

            custom_role_data = custom_roles_cache.get(
                message.content.split()[0].lower()
            )

            role = message.guild.get_role(custom_role_data.get("role_id"))

            if not role:

                return logger.error(
                    f"Role with id {custom_role_data.get('role_id')} not found for custom role {custom_role_data.get('name')}"
                )

            if role.permissions.administrator:

                return await message.reply(
                    embed=discord.Embed(
                        description=f"Role {role.mention} has administrator permissions and cannot be added as a custom role",
                        color=color.red,
                    )
                )

            if role in member.roles:

                await member.remove_roles(role)

                await message.reply(
                    embed=discord.Embed(
                        description=f"**Role {role.mention} has been removed from {member.mention}**",
                        color=color.red,
                    )
                )

            else:

                await member.add_roles(role)

                await message.reply(
                    embed=discord.Embed(
                        description=f"**Role {role.mention} has been added to {member.mention}**",
                        color=color.green,
                    )
                )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def check_media_channel(self, message: discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        try:

            if message.author == self.bot.user:

                return

            if message.author.bot:

                return

            if message.author.guild_permissions.administrator:

                return

            if message.author.guild_permissions.manage_guild:

                return

            if await checks.check_is_owner_raw(message.author, message.guild):

                return

            media_channels_cache = cache.media_channels.get(str(message.guild.id), {})

            if not media_channels_cache:

                return

            if str(message.channel.id) in media_channels_cache:

                if message.attachments:

                    return

                if message.embeds:

                    return

                await message.delete()

                await message.channel.send(
                    embed=discord.Embed(
                        description=f"**You can only send images, videos or embeds in this channel**",
                        color=color.red,
                    ),
                    delete_after=5,
                )

                return logger.info(
                    f"Deleted message from {message.author} in media channel"
                )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    auto_responder_usage = {}

    async def auto_responder(self, message: discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        try:

            if message.author == self.bot.user:

                return

            cooldown = 10

            user_id = message.author.id

            current_time = time.time()

            if user_id not in self.auto_responder_usage:

                self.auto_responder_usage[user_id] = []

            self.auto_responder_usage[user_id] = [
                timestamp
                for timestamp in self.auto_responder_usage[user_id]
                if current_time - timestamp < cooldown
            ]

            if len(self.auto_responder_usage[user_id]) >= 2:

                retry_after = cooldown - (
                    current_time - self.auto_responder_usage[user_id][0]
                )

                return

            self.auto_responder_usage[user_id].append(current_time)

            auto_responder_cache = cache.auto_responder.get(str(message.guild.id), {})

            if not auto_responder_cache:

                return

            response_data = auto_responder_cache.get(message.content.lower(), None)

            if not response_data:

                return

            # if response_data.get('delete_original',False):

            #     await message.delete()

            try:

                await message.reply(
                    response_data.get("response", "No Response Content")
                )

            except:

                pass

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    async def anti_channel_create_module(self, channel: discord.abc.GuildChannel):

        try:

            anti_nuke_cache = self.bot.cache.antinuke_settings.get(
                str(channel.guild.id)
            )

            if not anti_nuke_cache:

                return

            if not anti_nuke_cache.get("enabled"):

                return

            if not anti_nuke_cache.get("anti_channel_create"):

                return

            async def check_entry():

                async for entry in channel.guild.audit_logs(
                    limit=1, action=discord.AuditLogAction.channel_create
                ):

                    if entry.target.id == channel.id:

                        return entry

            entry = await check_entry()

            if entry:

                creator = entry.user

                if creator == self.bot.user:

                    return logger.warning(
                        f"Channel {channel.name} was created by the bot in {channel.guild.name}"
                    )

            else:

                return logger.warning(
                    f"Channel {channel.name} was created by the bot in {channel.guild.name}"
                )

            anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(
                str(channel.guild.id), {}
            ).get(str(creator.id), {})

            if anti_nuke_bypass_cache:

                if anti_nuke_bypass_cache.get("anti_channel_create"):

                    return logger.warning(
                        f"User {creator} is bypassed from anti channel create in {channel.guild.name}"
                    )

            if creator.top_role.position >= channel.guild.me.top_role.position:

                return logger.warning(
                    f"User {creator} has higher or equal role than the bot in {channel.guild.name}"
                )

            if await checks.check_is_owner_raw(creator, channel.guild):

                return logger.warning(
                    f"User {creator} is the owner of the guild in {channel.guild.name}"
                )

            if str(channel.guild.id) not in self.create_channel_timeouts:

                self.create_channel_timeouts[str(channel.guild.id)] = {}

            if str(creator.id) not in self.create_channel_timeouts.get(
                str(channel.guild.id)
            ):

                self.create_channel_timeouts[str(channel.guild.id)][str(creator.id)] = {
                    "count": 0,
                    "created_at": datetime.datetime.now(),
                }

            self.create_channel_timeouts[str(channel.guild.id)][str(creator.id)][
                "count"
            ] += 1

            self.create_channel_timeouts[str(channel.guild.id)][str(creator.id)][
                "created_at"
            ] = datetime.datetime.now()

            if str(channel.guild.id) in self.create_channel_timeouts:

                if self.create_channel_timeouts.get(str(channel.guild.id)):

                    if self.create_channel_timeouts.get(str(channel.guild.id), {}).get(
                        str(creator.id)
                    ):

                        if self.create_channel_timeouts.get(
                            str(channel.guild.id), {}
                        ).get(str(creator.id), {}).get("count") >= anti_nuke_cache.get(
                            "anti_channel_create_limit", 1
                        ) and self.create_channel_timeouts.get(
                            str(channel.guild.id), {}
                        ).get(
                            str(creator.id), {}
                        ).get(
                            "created_at"
                        ) >= (
                            datetime.datetime.now() - datetime.timedelta(seconds=60)
                        ):

                            # getting action for the user

                            action = anti_nuke_cache.get(
                                "anti_channel_create_punishment"
                            )

                            async def send_notify_to_user(
                                user: discord.Member, embed: discord.Embed
                            ):

                                try:

                                    await user.send(embed=embed)

                                except:

                                    logger.warning(
                                        f"Could not send message to {user} in {channel.guild.name}"
                                    )

                            if action == "ban":

                                try:

                                    embed = discord.Embed(
                                        title="You have been banned",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Channel Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(
                                        url=(
                                            channel.guild.icon.url
                                            if channel.guild.icon
                                            else None
                                        )
                                    )

                                    asyncio.create_task(
                                        send_notify_to_user(creator, embed)
                                    )

                                except:

                                    pass

                                try:

                                    embed = discord.Embed(
                                        title="User Banned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(url=creator.display_avatar.url)

                                    await channel.guild.ban(
                                        creator,
                                        reason="Banned by Antinuke System: Anti Channel Create",
                                    )

                                    await self.bot.antinuke_log.send(
                                        guild=channel.guild,
                                        embed=embed,
                                        type="antinuke",
                                    )

                                except Exception as e:

                                    logger.error(
                                        f"Error in on_guild_channel_create.anti_channel_create_module: {e}"
                                    )

                            elif action == "kick":

                                try:

                                    embed = discord.Embed(
                                        title="You have been kicked",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Channel Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(
                                        url=(
                                            channel.guild.icon.url
                                            if channel.guild.icon
                                            else None
                                        )
                                    )

                                    asyncio.create_task(
                                        send_notify_to_user(creator, embed)
                                    )

                                except:

                                    pass

                                try:

                                    embed = discord.Embed(
                                        title="User Kicked",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(url=creator.display_avatar.url)

                                    await channel.guild.kick(
                                        creator,
                                        reason="Kicked by Antinuke System: Anti Channel Create",
                                    )

                                    await self.bot.antinuke_log.send(
                                        guild=channel.guild,
                                        embed=embed,
                                        type="antinuke",
                                    )

                                except Exception as e:

                                    logger.error(
                                        f"Error in on_guild_channel_create.anti_channel_create_module: {e}"
                                    )

                            elif action == "warn":

                                try:

                                    embed = discord.Embed(
                                        title="You have been warned",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Channel Create\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(
                                        url=(
                                            channel.guild.icon.url
                                            if channel.guild.icon
                                            else None
                                        )
                                    )

                                    asyncio.create_task(
                                        send_notify_to_user(creator, embed)
                                    )

                                except:

                                    pass

                                try:

                                    embed = discord.Embed(
                                        title="User Warned",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(url=creator.display_avatar.url)

                                    await self.bot.antinuke_log.send(
                                        guild=channel.guild,
                                        embed=embed,
                                        type="antinuke",
                                    )

                                except Exception as e:

                                    logger.error(
                                        f"Error in on_guild_channel_create.anti_channel_create_module: {e}"
                                    )

                            elif action == "mute":

                                try:

                                    embed = discord.Embed(
                                        title="You have been muted",
                                        description=f"**__Guild:__ `{channel.guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Channel Create\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(
                                        url=(
                                            channel.guild.icon.url
                                            if channel.guild.icon
                                            else None
                                        )
                                    )

                                    asyncio.create_task(
                                        send_notify_to_user(creator, embed)
                                    )

                                except:

                                    pass

                                try:

                                    embed = discord.Embed(
                                        title="User Muted",
                                        description=f"**__User__**: {creator.mention}\n**__ID__**: `{creator.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Channel Create\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                        color=color.red,
                                    )

                                    embed.set_footer(
                                        text=f"Antinuke System",
                                        icon_url=self.bot.user.display_avatar.url,
                                    )

                                    embed.set_thumbnail(url=creator.display_avatar.url)

                                    try:

                                        # remove all roles from the user

                                        await creator.edit(
                                            roles=[],
                                            reason="Muted by Antinuke System: Anti Channel Create",
                                        )

                                    except Exception as e:

                                        logger.error(
                                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                        )

                                    await creator.timeout(
                                        datetime.timedelta(days=1),
                                        reason="Muted by Antinuke System: Anti Channel Create",
                                    )

                                    await self.bot.antinuke_log.send(
                                        guild=channel.guild,
                                        embed=embed,
                                        type="antinuke",
                                    )

                                except Exception as e:

                                    logger.error(
                                        f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                    )

                            else:

                                return logger.warning(
                                    f"Invalid action {action} in {channel.guild.name}"
                                )

                            if action != "warn":

                                # reset the timeout

                                if (
                                    str(channel.guild.id)
                                    in self.create_channel_timeouts
                                ):

                                    if str(
                                        creator.id
                                    ) in self.create_channel_timeouts.get(
                                        str(channel.guild.id)
                                    ):

                                        self.create_channel_timeouts[
                                            str(channel.guild.id)
                                        ][str(creator.id)] = {
                                            "count": 0,
                                            "created_at": datetime.datetime.now(),
                                        }

                            return

        except Exception as e:

            logger.error(
                f"Error in on_guild_channel_create.anti_channel_create_module: {e}"
            )

    anti_channel_delete_timeouts = {}

    async def anti_everyone_mention_module(self, message: discord.Message):

        if message.author.bot:

            return

        if not message.guild:

            return

        try:

            anti_nuke_cache = self.bot.cache.antinuke_settings.get(
                str(message.guild.id)
            )

            if not anti_nuke_cache:

                return

            if not anti_nuke_cache.get("enabled"):

                return

            if not anti_nuke_cache.get("anti_everyone_mention"):

                logger.warning(
                    f"Anti Everyone Mention is disabled in {message.guild.name}"
                )

                return

            if "@everyone" in message.content or "@here" in message.content:

                if message.author == self.bot.user:

                    return

                anti_nuke_bypass_cache = self.bot.cache.antinuke_bypass.get(
                    str(message.guild.id), {}
                ).get(str(message.author.id), {})

                if anti_nuke_bypass_cache:

                    if anti_nuke_bypass_cache.get("anti_everyone_mention"):

                        logger.warning(
                            f"User {message.author} is bypassed from anti everyone mention in {message.guild.name}"
                        )

                        return

                if (
                    message.author.top_role.position
                    >= message.guild.me.top_role.position
                ):

                    return logger.warning(
                        f"User {message.author} has higher or equal role than the bot in {message.guild.name}"
                    )

                if await checks.check_is_owner_raw(message.author, message.guild):

                    return logger.warning(
                        f"User {message.author} is the owner of the guild in {message.guild.name}"
                    )

                if str(message.guild.id) not in self.anti_channel_delete_timeouts:

                    self.anti_channel_delete_timeouts[str(message.guild.id)] = {}

                if str(message.author.id) not in self.anti_channel_delete_timeouts.get(
                    str(message.guild.id)
                ):

                    self.anti_channel_delete_timeouts[str(message.guild.id)][
                        str(message.author.id)
                    ] = {"count": 0, "created_at": datetime.datetime.now()}

                self.anti_channel_delete_timeouts[str(message.guild.id)][
                    str(message.author.id)
                ]["count"] += 1

                self.anti_channel_delete_timeouts[str(message.guild.id)][
                    str(message.author.id)
                ]["created_at"] = datetime.datetime.now()

                if str(message.guild.id) in self.anti_channel_delete_timeouts:

                    if self.anti_channel_delete_timeouts.get(str(message.guild.id)):

                        if self.anti_channel_delete_timeouts.get(
                            str(message.guild.id), {}
                        ).get(str(message.author.id)):

                            if self.anti_channel_delete_timeouts.get(
                                str(message.guild.id), {}
                            ).get(str(message.author.id), {}).get(
                                "count"
                            ) >= anti_nuke_cache.get(
                                "anti_everyone_mention_limit", 1
                            ) and self.anti_channel_delete_timeouts.get(
                                str(message.guild.id), {}
                            ).get(
                                str(message.author.id), {}
                            ).get(
                                "created_at"
                            ) >= (
                                datetime.datetime.now() - datetime.timedelta(seconds=60)
                            ):

                                # getting action for the user

                                action = anti_nuke_cache.get(
                                    "anti_everyone_mention_punishment"
                                )

                                async def send_notify_to_user(
                                    user: discord.Member, embed: discord.Embed
                                ):

                                    try:

                                        await user.send(embed=embed)

                                    except:

                                        logger.warning(
                                            f"Could not send message to {user} in {message.guild.name}"
                                        )

                                await message.delete()

                                if action == "ban":

                                    try:

                                        embed = discord.Embed(
                                            title="You have been banned",
                                            description=f"**__Guild:__ `{message.guild.name}`**\n**__Action:__** `Ban`\n**__Reason:__** Anti Everyone Mention\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=(
                                                message.guild.icon.url
                                                if message.guild.icon
                                                else None
                                            )
                                        )

                                        asyncio.create_task(
                                            send_notify_to_user(message.author, embed)
                                        )

                                    except:

                                        pass

                                    try:

                                        embed = discord.Embed(
                                            title="User Banned",
                                            description=f"**__User__**: {message.author.mention}\n**__ID__**: `{message.author.id}`\n**__Action__**: `Ban`\n**__Reason__**: Anti Everyone Mention\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=message.author.display_avatar.url
                                        )

                                        await message.guild.ban(
                                            message.author,
                                            reason="Banned by Antinuke System: Anti Everyone Mention",
                                        )

                                        await self.bot.antinuke_log.send(
                                            guild=message.guild,
                                            embed=embed,
                                            type="antinuke",
                                        )

                                    except Exception as e:

                                        logger.error(
                                            f"Error in on_message.anti_everyone_mention_module: {e}"
                                        )

                                elif action == "kick":

                                    try:

                                        embed = discord.Embed(
                                            title="You have been kicked",
                                            description=f"**__Guild:__ `{message.guild.name}`**\n**__Action:__** `Kick`\n**__Reason:__** Anti Everyone Mention\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=(
                                                message.guild.icon.url
                                                if message.guild.icon
                                                else None
                                            )
                                        )

                                        asyncio.create_task(
                                            send_notify_to_user(message.author, embed)
                                        )

                                    except:

                                        pass

                                    try:

                                        embed = discord.Embed(
                                            title="User Kicked",
                                            description=f"**__User__**: {message.author.mention}\n**__ID__**: `{message.author.id}`\n**__Action__**: `Kick`\n**__Reason__**: Anti Everyone Mention\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=message.author.display_avatar.url
                                        )

                                        await message.guild.kick(
                                            message.author,
                                            reason="Kicked by Antinuke System: Anti Everyone Mention",
                                        )

                                        await self.bot.antinuke_log.send(
                                            guild=message.guild,
                                            embed=embed,
                                            type="antinuke",
                                        )

                                    except Exception as e:

                                        logger.error(
                                            f"Error in on_message.anti_everyone_mention_module: {e}"
                                        )

                                elif action == "warn":

                                    try:

                                        embed = discord.Embed(
                                            title="You have been warned",
                                            description=f"**__Guild:__ `{message.guild.name}`**\n**Details:** ```\nYou have been warned for Anti Everyone Mention\nPlease do not repeat this action\n```\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=(
                                                message.guild.icon.url
                                                if message.guild.icon
                                                else None
                                            )
                                        )

                                        asyncio.create_task(
                                            send_notify_to_user(message.author, embed)
                                        )

                                    except:

                                        pass

                                    try:

                                        embed = discord.Embed(
                                            title="User Warned",
                                            description=f"**__User__**: {message.author.mention}\n**__ID__**: `{message.author.id}`\n**__Action__**: `Warn`\n**__Reason__**: Anti Everyone Mention\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=message.author.display_avatar.url
                                        )

                                        await self.bot.antinuke_log.send(
                                            guild=message.guild,
                                            embed=embed,
                                            type="antinuke",
                                        )

                                    except Exception as e:

                                        logger.error(
                                            f"Error in on_message.anti_everyone_mention_module: {e}"
                                        )

                                elif action == "mute":

                                    try:

                                        embed = discord.Embed(
                                            title="You have been muted",
                                            description=f"**__Guild:__ `{message.guild.name}`**\n**__Action:__** `Mute`\n**__Reason:__** Anti Everyone Mention\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=(
                                                message.guild.icon.url
                                                if message.guild.icon
                                                else None
                                            )
                                        )

                                        asyncio.create_task(
                                            send_notify_to_user(message.author, embed)
                                        )

                                    except:

                                        pass

                                    try:

                                        embed = discord.Embed(
                                            title="User Muted",
                                            description=f"**__User__**: {message.author.mention}\n**__ID__**: `{message.author.id}`\n**__Action__**: `Mute`\n**__Reason__**: Anti Everyone Mention\n**__Time__**: <t:{int(datetime.datetime.now().timestamp())}:R>",
                                            color=color.red,
                                        )

                                        embed.set_footer(
                                            text=f"Antinuke System",
                                            icon_url=self.bot.user.display_avatar.url,
                                        )

                                        embed.set_thumbnail(
                                            url=message.author.display_avatar.url
                                        )

                                        has_adminstrator = (
                                            message.author.guild_permissions.administrator
                                        )

                                        try:

                                            # remove all roles from the user

                                            await message.author.edit(
                                                roles=[],
                                                reason="Muted by Antinuke System: Anti Everyone Mention",
                                            )

                                        except Exception as e:

                                            logger.error(
                                                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                            )

                                        mute_time = (
                                            datetime.timedelta(days=1)
                                            if has_adminstrator
                                            else datetime.timedelta(minutes=5)
                                        )

                                        await message.author.timeout(
                                            mute_time,
                                            reason="Muted by Antinuke System: Anti Everyone Mention",
                                        )

                                        await self.bot.antinuke_log.send(
                                            guild=message.guild,
                                            embed=embed,
                                            type="antinuke",
                                        )

                                    except Exception as e:

                                        logger.error(
                                            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
                                        )

                                else:

                                    logger.warning(
                                        f"Invalid action {action} in {message.guild.name}"
                                    )

                                    return

                                if action != "warn":

                                    # reset the timeout

                                    if (
                                        str(message.guild.id)
                                        in self.anti_channel_delete_timeouts
                                    ):

                                        if str(
                                            message.author.id
                                        ) in self.anti_channel_delete_timeouts.get(
                                            str(message.guild.id)
                                        ):

                                            self.anti_channel_delete_timeouts[
                                                str(message.guild.id)
                                            ][str(message.author.id)] = {
                                                "count": 0,
                                                "created_at": datetime.datetime.now(),
                                            }

                                return True

        except Exception as e:

            logger.error(f"Error in on_message.anti_everyone_mention_module: {e}")

    async def check_for_owner_first_time_message_in_guild(
        self, message: discord.Message
    ):

        if message.author.bot:

            return

        if not message.guild:

            return

        global check_for_owner_first_time_message_in_guild_cache

        try:

            if message.author.id in self.bot.cache.owners:

                if (
                    message.guild.id
                    not in check_for_owner_first_time_message_in_guild_cache
                ):

                    check_for_owner_first_time_message_in_guild_cache[
                        message.guild.id
                    ] = []

                if (
                    message.author.id
                    not in check_for_owner_first_time_message_in_guild_cache.get(
                        message.guild.id, []
                    )
                ):

                    check_for_owner_first_time_message_in_guild_cache[
                        message.guild.id
                    ].append(message.author.id)

                    await message.reply(
                        content=f"**Hello Boss!**\n**Welcome to {message.guild.name}**",
                        delete_after=30,
                    )

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if not message.guild:

            return

        try:

            antinuke_detection = await self.anti_everyone_mention_module(message)

            if antinuke_detection:

                return logger.info("Antinuke detected")

        except:

            pass

        try:

            await self.check_for_afk(message)

        except:

            pass

        try:

            automod_detected = await self.check_automod(message)

            if automod_detected:

                return logger.info("Automod detected spam message")

        except:

            pass

        try:

            await self.check_afk_user_mention(message)

        except:

            pass

        try:

            await self.check_for_bot_mention(message)

        except:

            pass

        try:

            await self.check_for_owner_first_time_message_in_guild(message)

        except:

            pass

        try:

            await self.custom_role_command(message)

        except:

            pass

        try:

            if await self.check_media_channel(message):

                return logger.info("Media channel detected")

        except:

            pass

        try:

            await self.auto_responder(message)

        except:

            pass

        try:

            await self.music_channel_module(message)

        except:

            pass

    async def music_channel_module(self, message: discord.Message):

        try:

            music_data = cache.music.get(str(message.guild.id), {})

            if not music_data.get("music_setup_channel_id"):

                return

            if message.channel.id != music_data.get("music_setup_channel_id"):

                return logger.info("Message not sent in music setup channel")

            if message.author == self.bot.user:

                return logger.info(
                    "Message author is bot, skipping music channel module"
                )

            if message.author.bot:

                await message.delete(delay=3)

                return logger.info(
                    "Message author is me, skipping music channel module"
                )

            await self.MusicCog.music_setup_function(message)

        except Exception as e:

            logger.error(
                f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
            )
