import discord
from discord.ext import commands
import storage.ticket_settings
import storage.tickets
from reo.style import color
import traceback
import json

from reo.memory.cache import cache
from reo.src.checks import checks

from reo.console.logging import logger

from reo.engine.Bot import AutoShardedBot
import storage
import datetime

import asyncio
import os

from reo.utils import chat_exporter

from io import BytesIO


async def save_transcript_file(
    transcript_bytes: BytesIO,
    creator_id: int,
    guild_id: int,
    channel_id: int,
):
    try:
        if not os.path.exists(f"./transcripts"):
            os.makedirs(f"./transcripts")
        file_path = f"./transcripts/{guild_id}-{channel_id}-{creator_id}.html"
        with open(file_path, "wb") as f:
            f.write(transcript_bytes.read())

        # return the file path without the ".""
        return file_path[1:]
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        return False


async def delete_channel_callback(
    interaction: discord.Interaction, bot: AutoShardedBot, ticket_data
):
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
        ticket_data = await storage.tickets.get(id=ticket_data["id"])
        if not ticket_data:
            return await interaction.edit_original_response(
                content=f"{bot.emoji.ERROR} Ticket not found"
            )
        if not ticket_data.get("closed", False):
            return await interaction.edit_original_response(
                content=f"{bot.emoji.ERROR} Ticket is not closed"
            )
        guild_id_str = str(interaction.guild.id)
        ticket_module_id_str = str(ticket_data.get("ticket_module_id", 0))
        ticket_settings = cache.ticket_settings.get(guild_id_str, {})
        support_roles_str = ticket_settings.get(ticket_module_id_str, {}).get(
            "support_roles", "[]"
        )
        support_role_ids = json.loads(support_roles_str)

        if not await checks.close_ticket_permissions(
            user=interaction.user,
            guild=interaction.guild,
            creator_id=None,
            support_role_ids=support_role_ids,
            notify=False,
        ):
            return await interaction.edit_original_response(
                content=f"{bot.emoji.ERROR} You don't have permission to delete this ticket channel"
            )

        try:
            channel = interaction.guild.get_channel(ticket_data.get("channel_id"))
            if channel:
                await channel.delete()
                try:
                    await storage.tickets.update(id=ticket_data["id"], deleted=True)
                except Exception as e:
                    logger.error(f"Error updating ticket: {e}")
        except Exception as e:
            logger.error(f"Error deleting channel: {e}")

        await interaction.edit_original_response(
            content=f"{bot.emoji.SUCCESS} Channel deleted successfully"
        )
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


async def ticket_close_action(
    guild: discord.Guild, ticket_data, bot: AutoShardedBot, closed_by: discord.Member
):
    try:
        if ticket_data.get("closed", False):
            logger.warning(f"Ticket already closed: {ticket_data['id']}")
            return
        ticket_data = await storage.tickets.update(
            id=ticket_data.get("id"),
            closed=True,
            closed_at=datetime.datetime.utcnow().isoformat(),
        )
        if ticket_data.get("closed", False) == False:
            logger.warning(f"Error closing ticket: {ticket_data['id']}")
            return False
        try:
            creator = await guild.fetch_member(ticket_data.get("creator_id"))
        except:
            creator = None

        try:
            channel = guild.get_channel(ticket_data.get("channel_id"))
        except:
            channel = None
        if not channel:
            logger.warning(f"Channel not found for ticket: {ticket_data['id']}")
            return False

        transcript_bytes = await chat_exporter.export_chat(bot, guild, channel)

        if channel:
            try:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    guild.me: discord.PermissionOverwrite(view_channel=True),
                }
                ticket_module_id = ticket_data.get("ticket_module_id", 0)
                ticket_settings_data = cache.ticket_settings.get(str(guild.id), {}).get(
                    str(ticket_module_id), {}
                )
                for support_role_id in json.loads(
                    ticket_settings_data.get("support_roles", "[]")
                ):
                    support_role = guild.get_role(support_role_id)
                    if support_role:
                        overwrites[support_role] = discord.PermissionOverwrite(
                            view_channel=True
                        )
                closed_category_id = ticket_settings_data.get(
                    "closed_ticket_category_id", None
                )

                closed_category = None
                if closed_category_id:
                    closed_category = guild.get_channel(closed_category_id)
                    if len(closed_category.channels) >= 50:
                        closed_category = None

                await channel.edit(
                    category=closed_category,
                    overwrites=overwrites,
                    name=channel.name.replace("ticket-", "closed-"),
                    topic=f"Closed by {closed_by.mention if closed_by else 'Unknown'}",
                )
            except Exception as e:
                logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

        transcript_url = None
        if transcript_bytes:
            transcript_file_path = await save_transcript_file(
                transcript_bytes=transcript_bytes,
                creator_id=ticket_data["creator_id"],
                guild_id=ticket_data["guild_id"],
                channel_id=ticket_data["channel_id"],
            )
            if transcript_file_path:
                transcript_url = f"{bot.urls.TRANSCRIPT_BASE_URL}{transcript_file_path}"

        try:
            embed = discord.Embed(
                title=f"Ticket #{str(ticket_data.get('ticket_id')).zfill(4)} Closed",
                description=f"""**{bot.emoji.ID} ID**: `{ticket_data.get('ticket_id')}`
**{bot.emoji.GUILD} Guild**: {guild.name}
**{bot.emoji.USER} Creator**: {f"<@{ticket_data.get('creator_id')}>"}
**{bot.emoji.CLOSE} Closed By**: {closed_by.mention if closed_by else "Unknown"}
**{bot.emoji.CREATED} Created At**: <t:{int(ticket_data.get('created_at').timestamp())}:F>
**{bot.emoji.CREATED} Closed At**: <t:{int(ticket_data.get('closed_at').timestamp())}:F>
**{bot.emoji.TOPIC} Topic**: {channel.topic if channel.topic else "No topic provided"}
**{bot.emoji.CHANNEL} Channel ID**: `{channel.id}`""",
                color=color.red,
            )
            view = discord.ui.View()
            if transcript_url:
                transcript_button = discord.ui.Button(
                    label="Transcript",
                    style=discord.ButtonStyle.gray,
                    url=transcript_url,
                    emoji=bot.emoji.TRANSCRIPT,
                )
                view.add_item(transcript_button)
            embed.set_footer(
                text=f"Powered by {bot.user.name}", icon_url=bot.user.display_avatar.url
            )
            if channel:
                try:
                    await channel.send(embed=embed, view=view)
                except:
                    logger.error(f"Error sending ticket closed message to channel: {e}")
            if creator:
                try:
                    await creator.send(embed=embed, view=view)
                except:
                    logger.error(f"Error sending ticket closed message to creator: {e}")
        except Exception as e:
            logger.error(f"Error sending ticket closed message to creator: {e}")
        return True
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        return False


async def close_ticket_callback(interaction: discord.Interaction, bot: AutoShardedBot):
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)
        ticket_data = await storage.tickets.get(
            channel_id=interaction.channel.id,
            close_ticket_message_id=interaction.message.id,
            guild_id=interaction.guild.id,
        )
        if not ticket_data:
            return await interaction.edit_original_response(
                content=f"{bot.emoji.ERROR} Ticket not found"
            )
        if ticket_data.get("closed", False):
            return await interaction.edit_original_response(
                content=f"{bot.emoji.ERROR} Ticket already closed"
            )

        guild_id_str = str(interaction.guild.id)
        ticket_module_id_str = str(ticket_data.get("ticket_module_id", 0))
        ticket_settings = cache.ticket_settings.get(guild_id_str, {})
        support_roles_str = ticket_settings.get(ticket_module_id_str, {}).get(
            "support_roles", "[]"
        )
        support_role_ids = json.loads(support_roles_str)

        if not await checks.close_ticket_permissions(
            user=interaction.user,
            guild=interaction.guild,
            creator_id=ticket_data.get("creator_id"),
            support_role_ids=support_role_ids,
            notify=False,
        ):
            return await interaction.edit_original_response(
                content=f"{bot.emoji.ERROR} You don't have permission to close this ticket"
            )

        message_view = discord.ui.View.from_message(interaction.message)
        for item in message_view.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await interaction.message.edit(view=message_view)

        if await ticket_close_action(
            interaction.guild, ticket_data, bot, interaction.user
        ):
            await interaction.message.edit(
                embed=discord.Embed(
                    title=f"Ticket #{str(ticket_data.get('ticket_id')).zfill(4)}",
                    description="This ticket has been closed",
                    color=color.red,
                ),
                content=f"<@{ticket_data.get('creator_id')}>",
                view=None,
            )
            await interaction.edit_original_response(
                content=f"{bot.emoji.SUCCESS} Ticket closed successfully"
            )
            # send embed if they want to delete the channel only adminstrators or support roles can delete the channel
            embed = discord.Embed(
                title="Delete Confirmation",
                description="Do you want to delete the Ticket Channel?",
                color=color.red,
            )
            view = discord.ui.View(timeout=None)
            DeleteButton = discord.ui.Button(
                label="Delete Channel",
                style=discord.ButtonStyle.red,
                emoji=bot.emoji.DELETE,
                custom_id="delete_channel",
            )
            DeleteButton.callback = lambda i: delete_channel_callback(
                i, bot, ticket_data
            )
            view.add_item(DeleteButton)
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.edit_original_response(
                content=f"{bot.emoji.ERROR} Error closing ticket"
            )
    except Exception as e:
        try:
            message_view = discord.ui.View.from_message(interaction.message)
            for item in message_view.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = False
            await interaction.message.edit(view=message_view)
        except:
            pass
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


async def send_close_ticket_module(ticket_data, bot: AutoShardedBot):
    try:
        guild = bot.get_guild(ticket_data["guild_id"])
        if not guild:
            logger.warning(
                f"Guild not found for close ticket message: {ticket_data['guild_id']}"
            )
            return
        try:
            channel = (
                guild.get_channel(ticket_data.get("channel_id"))
                if ticket_data.get("channel_id")
                else None
            )
        except:
            channel = None
        if not channel:
            logger.warning(
                f"Channel not found for close ticket message: {ticket_data.get('channel_id')}"
            )
            return
        try:
            message = await channel.fetch_message(
                ticket_data.get("close_ticket_message_id", None)
            )
        except:
            message = None
        if json.loads(ticket_data.get("close_ticket_message_embed", r"{}")):
            embed = discord.Embed.from_dict(
                json.loads(ticket_data.get("close_ticket_message_embed", r"{}"))
            )
        else:
            embed = discord.Embed(
                title=f"Ticket #{str(ticket_data.get('ticket_id')).zfill(4)}",
                description="Click the button below to close this ticket",
                color=color.gray,
            )
            embed.set_footer(
                text=f"Powered by {bot.user.name}", icon_url=bot.user.display_avatar.url
            )
            embed.set_thumbnail(url=bot.urls.TICKET)

        view = discord.ui.View(timeout=None)

        CloseTicketButton = discord.ui.Button(
            label="Close Ticket",
            style=discord.ButtonStyle.gray,
            emoji=bot.emoji.CLOSE,
            custom_id="close_ticket",
        )
        CloseTicketButton.callback = lambda i: close_ticket_callback(i, bot)
        view.add_item(CloseTicketButton)

        content = (
            f"<@{ticket_data.get('creator_id')}>"
            if ticket_data.get("creator_id")
            else ""
        )

        guild_id_str = str(guild.id)
        ticket_module_id_str = str(ticket_data.get("ticket_module_id", 0))
        ticket_settings = cache.ticket_settings.get(guild_id_str, {})
        print(ticket_settings)
        support_roles_str = ticket_settings.get(ticket_module_id_str, {}).get(
            "support_roles", "[]"
        )
        support_role_ids = json.loads(support_roles_str)

        print(support_role_ids)

        if support_role_ids:
            content += "\n" + " ".join(f"<@&{role_id}>" for role_id in support_role_ids)

        if message:
            await message.edit(embed=embed, view=view, content=content)
        else:
            allowed_mentions = discord.AllowedMentions(
                everyone=False, roles=True, users=True
            )
            message = await channel.send(
                embed=embed,
                view=view,
                content=content,
                allowed_mentions=allowed_mentions,
            )
            await storage.tickets.update(
                id=ticket_data["id"], close_ticket_message_id=message.id
            )
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


create_ticket_timeout = {}  # {guild_id: {user_id: datetime.datetime}}


async def create_ticket_callback(interaction: discord.Interaction, bot: AutoShardedBot):
    global create_ticket_timeout
    try:
        if interaction.guild.id not in create_ticket_timeout:
            create_ticket_timeout[interaction.guild.id] = {}
        if interaction.user.id in create_ticket_timeout[interaction.guild.id]:
            if (
                datetime.datetime.utcnow()
                - create_ticket_timeout[interaction.guild.id][interaction.user.id]
            ).total_seconds() < 10:
                return await interaction.response.send_message(
                    content=f"{bot.emoji.ERROR} You are creating tickets too fast",
                    ephemeral=True,
                    delete_after=10,
                )
        create_ticket_timeout[interaction.guild.id][
            interaction.user.id
        ] = datetime.datetime.utcnow()
        ticket_settings_data = cache.ticket_settings.get(str(interaction.guild.id), {})
        if not ticket_settings_data:
            return await interaction.response.send_message(
                content=f"{bot.emoji.ERROR} Ticket module is not **Setup** in this server",
                ephemeral=True,
                delete_after=10,
            )
        if len(interaction.guild.channels) >= 500:
            return await interaction.response.send_message(
                content=f"{bot.emoji.ERROR} You can't open a ticket because the server has reached the maximum `500` channels limit",
                ephemeral=True,
                delete_after=10,
            )
        ticket_module_id = None
        for ticket_module in ticket_settings_data.values():
            if (
                ticket_module["ticket_panel_channel_id"] == interaction.channel.id
                and ticket_module["ticket_panel_message_id"] == interaction.message.id
            ):
                ticket_module_id = ticket_module["ticket_module_id"]
                break
        if not ticket_module_id:
            return await interaction.response.send_message(
                content=f"{bot.emoji.ERROR} Ticket module is not **Setup** in this server",
                ephemeral=True,
                delete_after=10,
            )
        ticket_module_data = ticket_settings_data.get(str(ticket_module_id), {})
        if not ticket_module_data:
            return await interaction.response.send_message(
                content=f"{bot.emoji.ERROR} Ticket module is not **Setup** in this server",
                ephemeral=True,
                delete_after=10,
            )

        if ticket_module_data.get("enabled", False) == False:
            return await interaction.response.send_message(
                content=f"{bot.emoji.DISABLED_BUNDLE} Ticket module is **Disabled** in this server",
                ephemeral=True,
                delete_after=10,
            )

        class SelectTopic(discord.ui.Modal, title="Ticket Info"):
            ticket_topic_field = discord.ui.TextInput(
                placeholder="Why are you opening this ticket?",
                label="Ticket Topic",
                max_length=100,
                style=discord.TextStyle.short,
                required=False,
            )

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    await interaction.response.defer(ephemeral=True, thinking=True)
                    opened_tickets = await storage.tickets.count(
                        ticket_module_id=ticket_module_id,
                        guild_id=interaction.guild.id,
                        creator_id=interaction.user.id,
                        closed=False,
                    )
                    if opened_tickets >= ticket_module_data.get("ticket_limit", 1):
                        return await interaction.edit_original_response(
                            content=f"{bot.emoji.ERROR} You can't open more than `{ticket_module_data.get('ticket_limit',1)}` tickets at a time"
                        )

                    open_ticket_category = (
                        interaction.guild.get_channel(
                            ticket_module_data.get("open_ticket_category_id")
                        )
                        if ticket_module_data.get("open_ticket_category_id")
                        else None
                    )

                    category_limited = False
                    if open_ticket_category:
                        if len(open_ticket_category.channels) >= 50:
                            category_limited = True

                    ticket_data = await storage.tickets.insert(
                        ticket_module_id=ticket_module_id,
                        guild_id=interaction.guild.id,
                        creator_id=interaction.user.id,
                        closed=False,
                    )
                    if not ticket_data:
                        return await interaction.edit_original_response(
                            content=f"{bot.emoji.ERROR} Error opening ticket"
                        )

                    overwrites = {
                        interaction.guild.default_role: discord.PermissionOverwrite(
                            view_channel=False
                        ),
                        interaction.user: discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_message_history=True,
                            read_messages=True,
                            attach_files=True,
                            embed_links=True,
                            add_reactions=True,
                        ),
                    }
                    support_roles = json.loads(
                        ticket_module_data.get("support_roles", r"[]")
                    )
                    for role_id in support_roles:
                        role = interaction.guild.get_role(role_id)
                        if role:
                            overwrites[role] = discord.PermissionOverwrite(
                                view_channel=True,
                                send_messages=True,
                                read_message_history=True,
                                read_messages=True,
                                attach_files=True,
                                embed_links=True,
                                add_reactions=True,
                                manage_messages=True,
                            )

                    ticket_channel = await interaction.guild.create_text_channel(
                        name=f"ticket-{str(ticket_data['ticket_id']).zfill(4)}",
                        category=(
                            open_ticket_category
                            if open_ticket_category and not category_limited
                            else None
                        ),
                        topic=(
                            self.ticket_topic_field.value
                            if self.ticket_topic_field.value != ""
                            else "No topic provided"
                        ),
                        overwrites=overwrites,
                    )
                    if not ticket_channel:
                        await storage.tickets.delete(id=ticket_data["id"])
                        return await interaction.edit_original_response(
                            content=f"{bot.emoji.ERROR} Error Creating Ticket Channel"
                        )
                    await storage.tickets.update(
                        id=ticket_data["id"], channel_id=ticket_channel.id
                    )
                    await interaction.edit_original_response(
                        content=f"{bot.emoji.SUCCESS} Ticket opened successfully in {ticket_channel.mention}"
                    )
                    ticket_data = await storage.tickets.get(id=ticket_data["id"])
                    await send_close_ticket_module(ticket_data, bot)
                except Exception as e:
                    logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

        await interaction.response.send_modal(SelectTopic())
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


async def send_ticket_panel_message(ticket_settings_data, bot: AutoShardedBot):
    try:
        guild = bot.get_guild(ticket_settings_data["guild_id"])
        if not guild:
            logger.warning(
                f"Guild not found for ticket panel message: {ticket_settings_data['guild_id']}"
            )
            return
        panel_channel_id = ticket_settings_data.get("ticket_panel_channel_id")
        try:
            channel = guild.get_channel(panel_channel_id) if panel_channel_id else None
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
            channel = None
        if not channel:
            logger.warning(
                f"Channel not found for ticket panel message: {panel_channel_id}"
            )
            return
        try:
            message = await channel.fetch_message(
                ticket_settings_data.get("ticket_panel_message_id", None)
            )
        except:
            message = None

        if json.loads(ticket_settings_data.get("ticket_panel_message_embed", r"{}")):
            embed = discord.Embed.from_dict(
                json.loads(
                    ticket_settings_data.get("ticket_panel_message_embed", r"{}")
                )
            )
        else:
            embed = discord.Embed(
                title="Open a ticket",
                description="Click the button below to open a ticket",
                color=color.gray,
            )
            embed.set_author(
                name=guild.name, icon_url=guild.icon.url if guild.icon else None
            )
            embed.set_footer(
                text=f"Powered by {bot.user.name}", icon_url=bot.user.display_avatar.url
            )
            embed.set_thumbnail(url=bot.urls.TICKET)

        view = discord.ui.View(timeout=None)

        CreateTicketButton = discord.ui.Button(
            label="Create Ticket",
            style=discord.ButtonStyle.gray,
            emoji=bot.emoji.TICKET,
            custom_id="create_ticket",
        )
        CreateTicketButton.callback = lambda i: create_ticket_callback(i, bot)
        view.add_item(CreateTicketButton)

        if message:
            await message.edit(embed=embed, view=view)
        else:
            message = await channel.send(embed=embed, view=view)
            await storage.ticket_settings.update(
                id=ticket_settings_data["id"],
                guild_id=ticket_settings_data["guild_id"],
                ticket_module_id=ticket_settings_data["ticket_module_id"],
                ticket_panel_message_id=message.id,
            )
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
