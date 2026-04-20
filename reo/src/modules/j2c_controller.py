import discord


import asyncio


from reo.engine.Bot import AutoShardedBot


from reo.console.logging import logger


from storage import j2c as j2c_db


from reo.style import color


from reo.memory.cache import cache


from reo.src.events import on_voice_state_update


import traceback, sys


async def controller_module(bot: AutoShardedBot, data, channel=None):

    if not channel:

        channel = await bot.fetch_channel(data.get("channel_id"))

    if not channel:

        return logger.error(f"Channel not found in controller_module")

    if not isinstance(channel, discord.VoiceChannel):

        return logger.error(f"Channel is not a voice channel in controller_module")

    try:

        async def get_embed():

            embed = discord.Embed(
                title=f"Voice Channel Controller",
                color=color.white,
            )

            embed.add_field(name="Channel:", value=channel.mention, inline=True)

            embed.add_field(
                name="Users Limit:",
                value=f"`{channel.user_limit if channel.user_limit != 0 else 'Unlimited'}`",
                inline=True,
            )

            embed.add_field(name="", value="", inline=False)

            embed.add_field(
                name="Bitrate:", value=f"`{channel.bitrate/1000}kbps`", inline=True
            )

            embed.add_field(
                name="Slowmode:", value=f"`{channel.slowmode_delay}s`", inline=True
            )

            embed.add_field(name="NSFW:", value=f"`{channel.is_nsfw()}`", inline=True)

            embed.add_field(name="", value="", inline=False)

            embed.add_field(
                name="Video Quality Mode:",
                value=f"`{channel.video_quality_mode.name}`",
                inline=True,
            )

            embed.add_field(
                name="Region:",
                value=f"`{channel.rtc_region if channel.rtc_region else 'Automatic'}`",
                inline=True,
            )

            embed.add_field(
                name="Created At:",
                value=f"<t:{int(channel.created_at.timestamp())}:F>",
                inline=True,
            )

            embed.set_footer(text=f"Channel ID: {channel.id}")

            embed.set_thumbnail(url=bot.user.display_avatar.url)

            return embed

        embed = await get_embed()

        async def get_view():

            view = discord.ui.View(timeout=None)

            name_changer_button = discord.ui.Button(
                label="Change Name",
                style=discord.ButtonStyle.primary,
                emoji="📌",
                row=1,
            )

            name_changer_button.callback = lambda i: name_changer_button_callback(i)

            change_bitrate_button = discord.ui.Button(
                label="Change Bitrate",
                style=discord.ButtonStyle.primary,
                emoji="📶",
                row=1,
            )

            change_bitrate_button.callback = lambda i: change_bitrate_button_callback(i)

            change_user_limit_button = discord.ui.Button(
                label="User Limit", style=discord.ButtonStyle.primary, emoji="👥", row=2
            )

            change_user_limit_button.callback = (
                lambda i: change_user_limit_button_callback(i)
            )

            transfer_ownership_button = discord.ui.Button(
                label="Transfer Ownership",
                style=discord.ButtonStyle.primary,
                row=2,
            )

            transfer_ownership_button.callback = (
                lambda i: transfer_ownership_button_callback(i)
            )

            switch_region_select = discord.ui.Select(
                placeholder="Select a region",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(
                        label="Automatic",
                        value="Automatic",
                        emoji="🌐",
                        default=True if channel.rtc_region == None else False,
                    ),
                    discord.SelectOption(
                        label="US East",
                        value="us-east",
                        emoji="🌐",
                        default=True if channel.rtc_region == "us-east" else False,
                    ),
                    discord.SelectOption(
                        label="US West",
                        value="us-west",
                        emoji="🇺🇸",
                        default=True if channel.rtc_region == "us-west" else False,
                    ),
                    discord.SelectOption(
                        label="US South",
                        value="us-south",
                        emoji="🇺🇸",
                        default=True if channel.rtc_region == "us-south" else False,
                    ),
                    discord.SelectOption(
                        label="US Central",
                        value="us-central",
                        emoji="🇺🇸",
                        default=True if channel.rtc_region == "us-central" else False,
                    ),
                    discord.SelectOption(
                        label="Singapore",
                        value="singapore",
                        emoji="🇸🇬",
                        default=True if channel.rtc_region == "singapore" else False,
                    ),
                    discord.SelectOption(
                        label="South Africa",
                        value="south-africa",
                        emoji="🇿🇦",
                        default=True if channel.rtc_region == "south-africa" else False,
                    ),
                    discord.SelectOption(
                        label="South Korea",
                        value="south-korea",
                        emoji="🇰🇷",
                        default=True if channel.rtc_region == "south-korea" else False,
                    ),
                    discord.SelectOption(
                        label="Sydney",
                        value="sydney",
                        emoji="🇦🇺",
                        default=True if channel.rtc_region == "sydney" else False,
                    ),
                    discord.SelectOption(
                        label="Brazil",
                        value="brazil",
                        emoji="🇧🇷",
                        default=True if channel.rtc_region == "brazil" else False,
                    ),
                    discord.SelectOption(
                        label="Hong Kong",
                        value="hong-kong",
                        emoji="🇭🇰",
                        default=True if channel.rtc_region == "hong-kong" else False,
                    ),
                    discord.SelectOption(
                        label="Russia",
                        value="russia",
                        emoji="🇷🇺",
                        default=True if channel.rtc_region == "russia" else False,
                    ),
                    discord.SelectOption(
                        label="Europe",
                        value="europe",
                        emoji="🇪🇺",
                        default=True if channel.rtc_region == "europe" else False,
                    ),
                    discord.SelectOption(
                        label="India",
                        value="india",
                        emoji="🇮🇳",
                        default=True if channel.rtc_region == "india" else False,
                    ),
                    discord.SelectOption(
                        label="Japan",
                        value="japan",
                        emoji="🇯🇵",
                        default=True if channel.rtc_region == "japan" else False,
                    ),
                ],
                row=3,
            )

            switch_region_select.callback = lambda i: switch_region_select_callback(i)

            lock_or_unlock_button = discord.ui.Button(
                label=(
                    "Click To Unlock"
                    if str(channel.permissions_for(channel.guild.default_role).connect)
                    == "False"
                    else "Click To Lock"
                ),
                style=(
                    discord.ButtonStyle.green
                    if str(channel.permissions_for(channel.guild.default_role).connect)
                    == "False"
                    else discord.ButtonStyle.red
                ),
                emoji=(
                    "🔒"
                    if str(channel.permissions_for(channel.guild.default_role).connect)
                    == "False"
                    else "🔓"
                ),
                row=4,
            )

            lock_or_unlock_button.callback = lambda i: lock_or_unlock_button_callback(i)

            hide_or_unhide_button = discord.ui.Button(
                label=(
                    "Click To Unhide"
                    if str(
                        channel.overwrites_for(channel.guild.default_role).view_channel
                    )
                    == "False"
                    else "Click To Hide"
                ),
                style=(
                    discord.ButtonStyle.green
                    if str(
                        channel.overwrites_for(channel.guild.default_role).view_channel
                    )
                    == "False"
                    else discord.ButtonStyle.red
                ),
                emoji=(
                    "🙈"
                    if str(
                        channel.overwrites_for(channel.guild.default_role).view_channel
                    )
                    == "False"
                    else "👀"
                ),
                row=4,
            )

            hide_or_unhide_button.callback = lambda i: hide_or_unhide_button_callback(i)

            view.add_item(name_changer_button)

            view.add_item(change_bitrate_button)

            view.add_item(change_user_limit_button)

            view.add_item(transfer_ownership_button)

            view.add_item(switch_region_select)

            view.add_item(lock_or_unlock_button)

            view.add_item(hide_or_unhide_button)

            return view

        async def lock_or_unlock_button_callback(interaction: discord.Interaction):

            try:

                channel_Data = cache.j2c.get(str(interaction.channel.id))

                if not channel_Data:

                    return await interaction.response.send_message(
                        "⛔ This channel is not a J2C channel.",
                        ephemeral=True,
                        delete_after=10,
                    )

                if channel_Data.get("owner_id") != interaction.user.id:

                    return await interaction.response.send_message(
                        "⛔ You are not the owner of this channel.",
                        ephemeral=True,
                        delete_after=10,
                    )

                if str(channel.permissions_for(channel.guild.default_role).connect) in [
                    "True",
                    "None",
                ]:

                    await channel.set_permissions(
                        channel.guild.default_role, connect=False
                    )

                    await interaction.response.send_message(
                        "✅ Channel has been locked.", ephemeral=True, delete_after=10
                    )

                else:

                    await channel.set_permissions(
                        channel.guild.default_role, connect=True
                    )

                    await interaction.response.send_message(
                        "✅ Channel has been unlocked.", ephemeral=True, delete_after=10
                    )

            except Exception as e:

                logger.error(
                    f"Error in controller_module.lock_or_unlock_button_callback: {e}"
                )

                await interaction.response.send_message(
                    f"⚠️ An error occurred while locking/unlocking the channel: {e}",
                    ephemeral=True,
                    delete_after=10,
                )

            try:

                asyncio.create_task(update_channel())

            except:

                pass

        async def hide_or_unhide_button_callback(interaction: discord.Interaction):

            try:

                channel_Data = cache.j2c.get(str(interaction.channel.id))

                if not channel_Data:

                    return await interaction.response.send_message(
                        "⛔ This channel is not a J2C channel.",
                        ephemeral=True,
                        delete_after=10,
                    )

                if channel_Data.get("owner_id") != interaction.user.id:

                    return await interaction.response.send_message(
                        "⛔ You are not the owner of this channel.",
                        ephemeral=True,
                        delete_after=10,
                    )

                if str(
                    channel.overwrites_for(channel.guild.default_role).view_channel
                ) in ["True", "None"]:

                    await channel.set_permissions(
                        channel.guild.default_role, view_channel=False
                    )

                    await interaction.response.send_message(
                        "✅ Channel has been hidden.", ephemeral=True, delete_after=10
                    )

                else:

                    await channel.set_permissions(
                        channel.guild.default_role, view_channel=True
                    )

                    await interaction.response.send_message(
                        "✅ Channel has been unhidden.", ephemeral=True, delete_after=10
                    )

            except Exception as e:

                logger.error(
                    f"Error in controller_module.hide_or_unhide_button_callback: {e}"
                )

                await interaction.response.send_message(
                    f"⚠️ An error occurred while hiding/unhiding the channel: {e}",
                    ephemeral=True,
                    delete_after=10,
                )

            try:

                asyncio.create_task(update_channel())

            except:

                pass

        async def switch_region_select_callback(interaction: discord.Interaction):

            channel_Data = cache.j2c.get(str(interaction.channel.id))

            if not channel_Data:

                return await interaction.response.send_message(
                    "⛔ This channel is not a J2C channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            if channel_Data.get("owner_id") != interaction.user.id:

                return await interaction.response.send_message(
                    "⛔ You are not the owner of this channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            new_region = interaction.data.get("values")[0]

            if new_region == "Automatic":

                new_region = None

            try:

                await interaction.response.defer(thinking=True, ephemeral=True)

                await channel.edit(rtc_region=new_region)

                defer_message = await interaction.edit_original_response(
                    content=f"✅ Region has been changed to `{new_region if new_region else 'Automatic'}`.",
                    view=None,
                )

                logger.info(
                    f"✅ Channel region changed to {new_region if new_region else 'Automatic'}"
                )

                try:

                    asyncio.create_task(update_channel())

                except:

                    pass

                await asyncio.sleep(10)

                try:

                    await defer_message.delete()

                except:

                    pass

            except Exception as e:

                logger.error(
                    f"Error in controller_module.switch_region_select_callback: {e}"
                )

                defer_message = await interaction.edit_original_response(
                    content=f"⚠️ An error occurred while changing the region: {e}",
                    view=None,
                )

                try:

                    asyncio.create_task(update_channel())

                except:

                    pass

                await asyncio.sleep(10)

                try:

                    await defer_message.delete()

                except:

                    pass

        async def transfer_ownership_button_callback(interaction: discord.Interaction):

            try:

                channel_Data = cache.j2c.get(str(interaction.channel.id))

                if not channel_Data:

                    return await interaction.response.send_message(
                        "⛔ This channel is not a J2C channel.",
                        ephemeral=True,
                        delete_after=10,
                    )

                if channel_Data.get("owner_id") != interaction.user.id:

                    return await interaction.response.send_message(
                        "⛔ You are not the owner of this channel.",
                        ephemeral=True,
                        delete_after=10,
                    )

                embed = discord.Embed(
                    title="Transfer Ownership",
                    description="Select a user to transfer ownership to under 60 seconds.",
                    color=color.white,
                )

                cancled = False

                view = discord.ui.View(timeout=60)

                # user select option who are in the channel

                select_user_menu = discord.ui.UserSelect(
                    placeholder="Select a user to transfer ownership to",
                    min_values=1,
                    max_values=1,
                )

                select_user_menu.callback = lambda i: select_user_menu_callback(i)

                async def select_user_menu_callback(interaction: discord.Interaction):

                    nonlocal cancled

                    if interaction.user.id != channel_Data.get("owner_id"):

                        return await interaction.response.send_message(
                            "⛔ You are not the owner of this channel.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    new_owner = interaction.data.get("values")[0]

                    try:

                        new_owner = await interaction.guild.fetch_member(new_owner)

                    except:

                        return await interaction.response.send_message(
                            "⚠️ User not found.", ephemeral=True, delete_after=10
                        )

                    if new_owner.id == channel_Data.get("owner_id"):

                        return await interaction.response.send_message(
                            "⚠️ You are already the owner of this channel.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    if new_owner.voice == None or new_owner.voice.channel != channel:

                        return await interaction.response.send_message(
                            "⚠️ The user is not in the channel.\nThis action can only be performed if the user is in the channel.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer()

                    try:

                        await on_voice_state_update.change_j2c_owner(
                            bot, channel_Data, interaction.channel, new_owner
                        )

                        await interaction.edit_original_response(
                            content=f"✅ Ownership has been transferred to {new_owner.mention}.",
                            view=None,
                            embed=None,
                        )

                        logger.info(
                            f"✅ Ownership of the channel has been transferred to {new_owner}"
                        )

                        await asyncio.sleep(10)

                        try:

                            await interaction.delete_original_message()

                        except:

                            pass

                    except Exception as e:

                        logger.error(
                            f"Error in controller_module.transfer_ownership_button_callback.select_user_menu_callback: {e}"
                        )

                        await interaction.edit_original_response(
                            content=f"⚠️ An error occurred while transferring ownership: {e}",
                            view=None,
                        )

                        await asyncio.sleep(10)

                        try:

                            await interaction.delete_original_message()

                        except:

                            pass

                    cancled = True

                view.add_item(select_user_menu)

                message = await interaction.response.send_message(
                    embed=embed, view=view, ephemeral=True
                )

                await asyncio.sleep(60)

                if not cancled:

                    return

                try:

                    await message.delete()

                except Exception as e:

                    logger.error(
                        f"Error in controller_module.transfer_ownership_button_callback: {e}"
                    )

            except Exception as e:

                logger.error(
                    f"Error in controller_module.transfer_ownership_button_callback: {e}"
                )

        async def change_user_limit_button_callback(interaction: discord.Interaction):

            channel_Data = cache.j2c.get(str(interaction.channel.id))

            if not channel_Data:

                return await interaction.response.send_message(
                    "⛔ This channel is not a J2C channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            if channel_Data.get("owner_id") != interaction.user.id:

                return await interaction.response.send_message(
                    "⛔ You are not the owner of this channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            class ChangeUserLimit(discord.ui.Modal, title="Change User Limit"):

                new_user_limit = discord.ui.TextInput(
                    label="New User Limit",
                    placeholder="Enter the limit (0 = unlimited)",
                    min_length=1,
                    max_length=2,
                    required=True,
                    style=discord.TextStyle.short,
                )

                async def on_submit(self, interaction: discord.Interaction):

                    if channel_Data.get("owner_id") != interaction.user.id:

                        return await interaction.response.send_message(
                            "⛔ You are not the owner of this channel.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    new_user_limit = self.new_user_limit.value

                    try:

                        new_user_limit = int(new_user_limit)

                    except:

                        return await interaction.response.send_message(
                            "⚠️ User limit must be a number.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    if new_user_limit < 0:

                        return await interaction.response.send_message(
                            "⚠️ User limit must be greater than or equal to `0`.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    if new_user_limit == channel.user_limit:

                        return await interaction.response.send_message(
                            "⚠️ The new user limit is the same as the current user limit.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer(thinking=True, ephemeral=True)

                    try:

                        await channel.edit(
                            user_limit=new_user_limit if new_user_limit != 0 else None
                        )

                        defer_message = await interaction.edit_original_response(
                            content=f"✅ User limit has been changed to `{new_user_limit if new_user_limit != 0 else 'Unlimited'}`.",
                            view=None,
                        )

                        try:

                            await asyncio.create_task(update_channel())

                        except:

                            pass

                        logger.info(
                            f"✅ Channel user limit changed to {new_user_limit if new_user_limit != 0 else 'Unlimited'}"
                        )

                        await asyncio.sleep(10)

                        try:

                            await defer_message.delete()

                        except:

                            pass

                    except Exception as e:

                        logger.error(
                            f"Error in controller_module.change_user_limit_button_callback.ChangeUserLimit.callback: {e}"
                        )

                        defer_message = await interaction.edit_original_response(
                            content=f"⚠️ An error occurred while changing the user limit: {e}",
                            view=None,
                        )

                        try:

                            await asyncio.create_task(update_channel())

                        except:

                            pass

                        await asyncio.sleep(10)

                        try:

                            await defer_message.delete()

                        except:

                            pass

            await interaction.response.send_modal(ChangeUserLimit())

        async def change_bitrate_button_callback(interaction: discord.Interaction):

            channel_Data = cache.j2c.get(str(interaction.channel.id))

            if not channel_Data:

                return await interaction.response.send_message(
                    "⛔ This channel is not a J2C channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            if channel_Data.get("owner_id") != interaction.user.id:

                return await interaction.response.send_message(
                    "⛔ You are not the owner of this channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            class ChangeBitrate(discord.ui.Modal, title="Change Bitrate"):

                new_bitrate_in_kbps = discord.ui.TextInput(
                    label="New Bitrate",
                    placeholder="Enter the new bitrate in kbps",
                    min_length=1,
                    max_length=3,
                    required=True,
                    style=discord.TextStyle.short,
                )

                async def on_submit(self, interaction: discord.Interaction):

                    if channel_Data.get("owner_id") != interaction.user.id:

                        return await interaction.response.send_message(
                            "⛔ You are not the owner of this channel.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    new_bitrate_in_kbps = self.new_bitrate_in_kbps.value

                    try:

                        new_bitrate_in_kbps = int(new_bitrate_in_kbps)

                    except:

                        return await interaction.response.send_message(
                            "⚠️ Bitrate must be a number.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    if new_bitrate_in_kbps < 8:

                        return await interaction.response.send_message(
                            "⚠️ Bitrate must be greater than `8kbps`.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    if (
                        new_bitrate_in_kbps
                        > int(interaction.guild.bitrate_limit) / 1000
                    ):

                        return await interaction.response.send_message(
                            f"⚠️ Bitrate cannot be greater than `{int(interaction.guild.bitrate_limit)/1000}kbps`.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    if new_bitrate_in_kbps == channel.bitrate / 1000:

                        return await interaction.response.send_message(
                            "⚠️ The new bitrate is the same as the current bitrate.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer(thinking=True, ephemeral=True)

                    try:

                        await channel.edit(bitrate=new_bitrate_in_kbps * 1000)

                        defer_message = await interaction.edit_original_response(
                            content=f"✅ Bitrate has been changed to `{new_bitrate_in_kbps}kbps`.",
                            view=None,
                        )

                        try:

                            await asyncio.create_task(update_channel())

                        except:

                            pass

                        logger.info(
                            f"✅ Channel bitrate changed to {new_bitrate_in_kbps}kbps"
                        )

                        await asyncio.sleep(10)

                        try:

                            await defer_message.delete()

                        except:

                            pass

                    except Exception as e:

                        logger.error(
                            f"Error in controller_module.change_bitrate_button_callback.ChangeBitrate.callback: {e}"
                        )

                        defer_message = await interaction.edit_original_response(
                            content=f"⚠️ An error occurred while changing the bitrate: {e}",
                            view=None,
                        )

                        try:

                            await asyncio.create_task(update_channel())

                        except:

                            pass

                        await asyncio.sleep(10)

                        try:

                            await defer_message.delete()

                        except:

                            pass

            await interaction.response.send_modal(ChangeBitrate())

        async def name_changer_button_callback(interaction: discord.Interaction):

            channel_Data = cache.j2c.get(str(interaction.channel.id))

            if not channel_Data:

                return await interaction.response.send_message(
                    "⛔ This channel is not a J2C channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            if channel_Data.get("owner_id") != interaction.user.id:

                return await interaction.response.send_message(
                    "⛔ You are not the owner of this channel.",
                    ephemeral=True,
                    delete_after=10,
                )

            class ChangeChannelName(discord.ui.Modal, title="Change Channel Name"):

                new_name = discord.ui.TextInput(
                    label="New Channel Name",
                    placeholder="Enter the new name",
                    min_length=2,
                    max_length=100,
                    required=True,
                    style=discord.TextStyle.short,
                )

                async def on_submit(self, interaction: discord.Interaction):

                    if channel_Data.get("owner_id") != interaction.user.id:

                        return await interaction.response.send_message(
                            "⛔ You are not the owner of this channel.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    new_name = self.new_name.value

                    if new_name == channel.name:

                        return await interaction.response.send_message(
                            "⛔ The new name is the same as the current name.",
                            ephemeral=True,
                            delete_after=10,
                        )

                    await interaction.response.defer(thinking=True, ephemeral=True)

                    try:

                        await channel.edit(name=new_name)

                        defer_message = await interaction.edit_original_response(
                            content="✅ Channel name has been changed.", view=None
                        )

                        try:

                            await asyncio.create_task(update_channel())

                        except:

                            pass

                        logger.info(f"Channel name changed to {new_name}")

                        await asyncio.sleep(10)

                        try:

                            await defer_message.delete()

                        except:

                            pass

                    except Exception as e:

                        logger.error(
                            f"Error in controller_module.name_changer_button_callback.ChangeChannelName.callback: {e}"
                        )

                        defer_message = await interaction.edit_original_response(
                            content=f"⚠️ An error occurred while changing the channel name: {e}",
                            view=None,
                        )

                        try:

                            await asyncio.create_task(update_channel())

                        except:

                            pass

                        await asyncio.sleep(10)

                        try:

                            await defer_message.delete()

                        except:

                            pass

            await interaction.response.send_modal(ChangeChannelName())

        embed = await get_embed()

        view = await get_view()

        if data.get("controller_message_id"):

            try:

                try:

                    message = await channel.fetch_message(
                        data.get("controller_message_id")
                    )

                except:

                    message = None

                if not message:

                    message = await channel.send(embed=embed, view=view)

                    await j2c_db.update(
                        id=data.get("id"), controller_message_id=message.id
                    )

                else:

                    await message.edit(embed=embed, view=view)

            except Exception as e:

                pass

        else:

            try:

                message = await channel.send(embed=embed, view=view)

                await j2c_db.update(id=data.get("id"), controller_message_id=message.id)

            except Exception as e:

                pass

        async def update_channel():

            embed = await get_embed()

            view = await get_view()

            await message.edit(embed=embed, view=view)

    except Exception as e:

        logger.error(
            f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}"
        )
