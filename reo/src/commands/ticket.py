import discord
from discord.ext import commands
import datetime
import traceback, sys

from reo.src.checks import checks
from reo.memory.cache import cache

import storage.ticket_settings
import storage.tickets
from reo.console.logging import logger

from reo.style import color
from reo.utils import pings
import asyncio

import json

from reo.engine.Bot import AutoShardedBot

import storage
from reo.src.modules import ticket_panel

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Ticket"
            category = "Main"
            description =  "Ticket system"
            hidden =  False
            emoji = self.bot.emoji.TICKET
        self.cog_info = cog_info

    
    @commands.hybrid_group(
        name="ticket",
        help="Set of commands to manage tickets",
        aliases=["tickets"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def ticket(self, ctx):
        try:
            embed = discord.Embed(
                title="Ticket Commands",
                description="Use these commands to manage tickets",
                color=color.random_color()
            )
            if hasattr(ctx.command,'commands'):
                for command in ctx.command.commands:
                    embed.description += f"\n\n`{self.bot.BotConfig.PREFIX}{ctx.command.name} {command.name}` : {command.help}"
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @ticket.command(
        name='setup',
        help="Setup the ticket system in the current server",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def ticket_setup(self,ctx: commands.Context):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator'):
                return
            

            view_timeout = 60
            cancled = False
            def reset_view_timeout():
                nonlocal view_timeout
                view_timeout = 60
            current_page_index = 0
            
            async def get_embed():
                try:
                    nonlocal current_page_index
                    ticket_settings_cache = cache.ticket_settings.get(str(ctx.guild.id),{})
                    embed = discord.Embed(
                        title="Ticket Setup",
                        description="Here you can setup the ticket system\n\n",
                        color=color.green
                    )

                    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)

                    if len(ticket_settings_cache) == 0:
                        embed.description += f"**No ticket Is Setup Yet**"
                        embed.set_footer(
                            text=f"Page {1}/{1}",
                            icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url
                        )
                    else:
                        if current_page_index >= len(ticket_settings_cache):
                            current_page_index = len(ticket_settings_cache)-1
                        ticket_module_id = list(ticket_settings_cache.keys())[current_page_index]
                        ticket_settings_data = ticket_settings_cache.get(ticket_module_id,{})
                        support_roles_text = ", ".join(
                            [f"<@&{role_id}>" for role_id in json.loads(ticket_settings_data.get("support_roles", "[]"))]
                        )
                        if not support_roles_text:
                            support_roles_text = "`Not Set Yet`"
                        open_category_id = ticket_settings_data.get("open_ticket_category_id")
                        closed_category_id = ticket_settings_data.get("closed_ticket_category_id")
                        panel_channel_id = ticket_settings_data.get("ticket_panel_channel_id")
                        panel_message_id = ticket_settings_data.get("ticket_panel_message_id")
                        open_category_text = f"<#{open_category_id}>" if open_category_id else "`Not Set Yet`"
                        closed_category_text = f"<#{closed_category_id}>" if closed_category_id else "`Not Set Yet`"
                        panel_channel_text = f"<#{panel_channel_id}>" if panel_channel_id else "`Not Set Yet`"
                        panel_message_text = (
                            f"[Click Here](https://discord.com/channels/{ctx.guild.id}/{panel_channel_id}/{panel_message_id})"
                            if panel_message_id else "`Not Set Yet`"
                        )
                        embed.description += f"""> {self.bot.emoji.ID} **Ticket Module ID:** `{ticket_module_id}`
> {self.bot.emoji.TICKET} **Enabled:** {self.bot.emoji.ENABLED_BUNDLE if ticket_settings_data.get('enabled',False) else self.bot.emoji.DISABLED_BUNDLE}
> {self.bot.emoji.GUILD} **Guild ID:** `{ticket_settings_data.get('guild_id')}`
> {self.bot.emoji.ROLE} **Support Roles:** {support_roles_text}
> {self.bot.emoji.LIMIT} **Ticket Limit:** `{ticket_settings_data.get('ticket_limit')}`
> {self.bot.emoji.CATEGORY} **Open Ticket Category:** {open_category_text}
> {self.bot.emoji.CATEGORY} **Closed Ticket Category:** {closed_category_text}
> {self.bot.emoji.CHANNEL} **Ticket Panel Channel:** {panel_channel_text}
> {self.bot.emoji.MESSAGE} **Ticket Panel Message:** {panel_message_text}
"""
                        embed.set_footer(
                            text=f"Page {current_page_index+1}/{len(ticket_settings_cache)}",
                            icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url
                        )                  
                    
                    return embed
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            
            async def get_view(disabled:bool=False):
                try:
                    nonlocal current_page_index
                    view = discord.ui.View(timeout=80)
                    reset_view_timeout()
                    ticket_settings_cache = cache.ticket_settings.get(str(ctx.guild.id),{})
                    
                    previous_button = discord.ui.Button(
                        label="Previous",
                        row=0,
                        style=discord.ButtonStyle.blurple,
                        emoji=self.bot.emoji.PREVIOUS,
                        disabled=current_page_index <= 0                    
                    )
                    stop_button = discord.ui.Button(
                        label="Stop",
                        row=0,
                        style=discord.ButtonStyle.red,
                        emoji=self.bot.emoji.STOP,
                        disabled=len(ticket_settings_cache) <= 1
                    )
                    next_button = discord.ui.Button(
                        label="Next",
                        row=0,
                        style=discord.ButtonStyle.blurple,
                        emoji=self.bot.emoji.NEXT,
                        disabled=current_page_index >= len(ticket_settings_cache)-1 or len(ticket_settings_cache) <= 1
                    )
                    previous_button.callback = lambda i: previous_button_callback(i)
                    stop_button.callback = lambda i: stop_button_callback(i)
                    next_button.callback = lambda i: next_button_callback(i)
                    view.add_item(previous_button)
                    view.add_item(stop_button)
                    view.add_item(next_button)

                    create_button = discord.ui.Button(
                        label="Create",
                        row=1,
                        style=discord.ButtonStyle.green,
                        emoji=self.bot.emoji.CREATE
                    )
                    create_button.callback = lambda i: create_button_callback(i)
                    view.add_item(create_button)
                    delete_button = discord.ui.Button(
                        label="Delete This",
                        row=1,
                        style=discord.ButtonStyle.red,
                        emoji=self.bot.emoji.DELETE
                    )
                    delete_button.callback = lambda i: delete_button_callback(i)
                    view.add_item(delete_button)

                    edit_select = discord.ui.Select(
                        placeholder="Select a ticket module to edit",
                        options=[
                            discord.SelectOption(
                                label=f"{ticket_module_id}",
                                value=f"{ticket_module_id}"
                            ) for ticket_module_id in ticket_settings_cache
                        ] if len(ticket_settings_cache) > 0 else None,
                        min_values=1,
                        max_values=1,
                        row=2
                    )
                    edit_select.callback = lambda i: edit_select_callback(i)
                    if len(ticket_settings_cache) > 0:
                        view.add_item(edit_select)
                    

                    if disabled:
                        for item in view.children:
                            item.disabled = True
                    return view
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            
            async def create_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)

                    ticket_settings_cache = cache.ticket_settings.get(str(ctx.guild.id),{})

                    guilds_subscription = cache.guilds.get(str(ctx.guild.id),{}).get('subscription','free')

                    if guilds_subscription == 'free':
                        ticket_module_limit = 1
                    elif guilds_subscription == 'silver_guild_preminum':
                        ticket_module_limit = 3
                    elif guilds_subscription == 'golden_guild_premium':
                        ticket_module_limit = 5
                    elif guilds_subscription == 'diamond_guild_premium':
                        ticket_module_limit = 10
                    else:
                        ticket_module_limit = 1
                    
                    if len(ticket_settings_cache) >= ticket_module_limit:
                        return await interaction.response.send_message(embed=discord.Embed(description=f"You have reached the limit of {ticket_module_limit} ticket modules",color=color.red),ephemeral=True,delete_after=10)
                    
                    await interaction.response.defer()

                    await storage.ticket_settings.insert(
                        guild_id=ctx.guild.id
                    )
                    await interaction.message.edit(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def delete_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)

                    ticket_settings_cache = cache.ticket_settings.get(str(ctx.guild.id),{})
                    ticket_module_id = list(ticket_settings_cache.keys())[current_page_index]

                    await interaction.response.defer()

                    # delete the ticket creator message if exists
                    try:
                        ticket_settings_data = ticket_settings_cache.get(ticket_module_id,{})
                        ticket_panel_channel = ctx.guild.get_channel(ticket_settings_data.get('ticket_panel_channel_id'))
                        if ticket_panel_channel:
                            try:
                                ticket_panel_message = await ticket_panel_channel.fetch_message(ticket_settings_data.get('ticket_panel_message_id'))
                                await ticket_panel_message.delete()
                            except:
                                pass
                    except:
                        pass

                    await storage.ticket_settings.delete(
                        guild_id=ctx.guild.id,
                        ticket_module_id=ticket_module_id
                    )
                    await interaction.message.edit(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def edit_select_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                    nonlocal current_page_index

                    MODULE_ID = interaction.data['values'][0]

                    ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                    if not ticket_settings_data:
                        return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)

                    await interaction.response.defer()

                    async def get_selected_edit_embed():
                        ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                        if not ticket_settings_data:
                            return discord.Embed(
                                title=F"Edit Ticket Module {MODULE_ID}",
                                description="Ticket module not found",
                                color=color.red
                            )
                        embed = discord.Embed(
                            title=F"Edit Ticket Module {MODULE_ID}",
                            description="Here you can edit the ticket module",
                            color=color.green
                        )
                        embed.add_field(
                            name="Enabled",
                            value=f"{self.bot.emoji.ENABLED_BUNDLE if ticket_settings_data.get('enabled',False) else self.bot.emoji.DISABLED_BUNDLE}",
                            inline=True
                        )
                        embed.add_field(
                            name="Ticket Limit",
                            value=f"`{ticket_settings_data.get('ticket_limit')}` Per User" if ticket_settings_data.get('ticket_limit') else "`Not Set Yet`",
                            inline=True
                        )

                        embed.add_field(
                            name="",
                            value="",
                            inline=False
                        )

                        embed.add_field(
                            name="Open Ticket Category",
                            value=f"<#{ticket_settings_data.get('open_ticket_category_id')}> `{ticket_settings_data.get('open_ticket_category_id')}`" if ticket_settings_data.get('open_ticket_category_id') else "`Not Set Yet`",
                            inline=True
                        )

                        embed.add_field(
                            name="Closed Ticket Category",
                            value=f"<#{ticket_settings_data.get('closed_ticket_category_id')}> `{ticket_settings_data.get('closed_ticket_category_id')}`" if ticket_settings_data.get('closed_ticket_category_id') else "`Not Set Yet`",
                            inline=True
                        )
                        embed.add_field(
                            name="",
                            value="",
                            inline=False
                        )
                        embed.add_field(
                            name="Ticket Creator Channel",
                            value=f"<#{ticket_settings_data.get('ticket_panel_channel_id')}>" if ticket_settings_data.get('ticket_panel_channel_id') else "`Not Set Yet`",
                            inline=True
                        )
                        embed.add_field(
                            name="Ticket Creator Message",
                            value=f"[Click Here](https://discord.com/channels/{ctx.guild.id}/{ticket_settings_data.get('ticket_panel_channel_id')}/{ticket_settings_data.get('ticket_panel_message_id')})" if ticket_settings_data.get('ticket_panel_message_id') and ticket_settings_data.get('ticket_panel_channel_id') else "`Not Set Yet`",
                            inline=True
                        )
                        embed.add_field(
                            name="",
                            value="",
                            inline=False
                        )
                        embed.add_field(
                            name="Support Roles",
                            value=', '.join([f"<@&{role_id}>" for role_id in json.loads(ticket_settings_data.get('support_roles','[]'))]) if len(json.loads(ticket_settings_data.get('support_roles','[]'))) > 0 else '`Not Set Yet`',
                            inline=True
                        )
                        embed.add_field(
                            name="Created At",
                            value=f"<t:{int(ticket_settings_data.get('created_at').timestamp())}:F>",
                            inline=True
                        )
                        embed.set_footer(
                            text=f"Edit Ticket Module: {MODULE_ID}",
                            icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url
                        )
                        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)
                        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)
                        return embed
                    
                    async def get_selected_view(disabled:bool=False):
                        view = discord.ui.View(timeout=80)
                        reset_view_timeout()
                        ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})

                        enable_disable_button = discord.ui.Button(
                            label="Click to Enable" if not ticket_settings_data.get('enabled',False) else "Click to Disable",
                            row=0,
                            style=discord.ButtonStyle.green if not ticket_settings_data.get('enabled',False) else discord.ButtonStyle.gray,
                            emoji=self.bot.emoji.ENABLED if not ticket_settings_data.get('enabled',False) else self.bot.emoji.DISABLED
                        )
                        enable_disable_button.callback = lambda i: enable_disable_button_callback(i)
                        view.add_item(enable_disable_button)
                    
                        edit_ticket_limit_button = discord.ui.Button(
                            label="Open Limit",
                            row=0,
                            style=discord.ButtonStyle.blurple,
                            emoji=self.bot.emoji.LIMIT
                        )
                        edit_ticket_limit_button.callback = lambda i: edit_ticket_limit_button_callback(i)
                        view.add_item(edit_ticket_limit_button)

                        send_ticket_panel_button = discord.ui.Button(
                            label="Send Ticket Panel",
                            row=0,
                            style=discord.ButtonStyle.blurple,
                            emoji=self.bot.emoji.MESSAGE,
                            disabled=not ticket_settings_data.get('ticket_panel_channel_id',False)
                        )
                        send_ticket_panel_button.callback = lambda i: send_ticket_panel_button_callback(i)
                        view.add_item(send_ticket_panel_button)

                        back_button = discord.ui.Button(
                            label="Back",
                            row=0,
                            style=discord.ButtonStyle.red,
                            emoji=self.bot.emoji.BACK
                        )
                        back_button.callback = lambda i: back_button_callback(i)
                        view.add_item(back_button)

                        edit_open_ticket_category_select = discord.ui.ChannelSelect(
                            channel_types=[discord.ChannelType.category],
                            placeholder="Select a Category for Open Tickets",
                            row=1,
                            max_values=1,
                            min_values=0,
                            default_values=[ctx.guild.get_channel(ticket_settings_data.get('open_ticket_category_id'))] if ticket_settings_data.get('open_ticket_category_id') else None
                        )
                        edit_open_ticket_category_select.callback = lambda i: edit_open_ticket_category_select_callback(i)
                        view.add_item(edit_open_ticket_category_select)
                        
                        edit_closed_ticket_category_select = discord.ui.ChannelSelect(
                            channel_types=[discord.ChannelType.category],
                            placeholder="Select a Category for Closed Tickets",
                            row=2,
                            max_values=1,
                            min_values=0,
                            default_values=[ctx.guild.get_channel(ticket_settings_data.get('closed_ticket_category_id'))] if ticket_settings_data.get('closed_ticket_category_id') else None
                        )
                        edit_closed_ticket_category_select.callback = lambda i: edit_closed_ticket_category_select_callback(i)
                        view.add_item(edit_closed_ticket_category_select)

                        select_ticket_channel = discord.ui.ChannelSelect(
                            channel_types=[discord.ChannelType.text],
                            placeholder="Select a Channel for Ticket Panel",
                            row=3,
                            max_values=1,
                            min_values=0,
                            default_values=[ctx.guild.get_channel(ticket_settings_data.get('ticket_panel_channel_id'))] if ticket_settings_data.get('ticket_panel_channel_id') else None
                        )

                        select_ticket_channel.callback = lambda i: select_ticket_channel_callback(i)
                        view.add_item(select_ticket_channel)

                        support_roles = discord.ui.RoleSelect(
                            placeholder="Select Support Roles",
                            row=4,
                            max_values=10,
                            min_values=0,
                            default_values=[ctx.guild.get_role(role_id) for role_id in json.loads(ticket_settings_data.get('support_roles','[]'))] if len(json.loads(ticket_settings_data.get('support_roles','[]'))) > 0 else None
                        )
                        support_roles.callback = lambda i: support_roles_callback(i)
                        view.add_item(support_roles)

                        
                        if disabled:
                            for item in view.children:
                                item.disabled = True

                        return view
                    
                    async def back_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            await interaction.response.defer()
                            await interaction.message.edit(embed=await get_embed(),view=await get_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    
                    async def support_roles_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                            if not ticket_settings_data:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                            await interaction.response.defer()
                            new_support_roles = [int(role) for role in interaction.data['values']]
                            print(new_support_roles)
                            await storage.ticket_settings.update(
                                id=ticket_settings_data.get('id'),
                                guild_id=ctx.guild.id,
                                ticket_module_id=MODULE_ID,
                                support_roles=json.dumps(new_support_roles)
                            )
                            await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    
                    async def send_ticket_panel_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                            if not ticket_settings_data:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                            await interaction.response.defer()
                            ticket_panel_channel = ctx.guild.get_channel(ticket_settings_data.get('ticket_panel_channel_id'))
                            if not ticket_panel_channel:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket panel channel not found",color=color.red),ephemeral=True,delete_after=10)

                            await ticket_panel.send_ticket_panel_message(ticket_settings_data,self.bot)
                            await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    
                    async def select_ticket_channel_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})

                            if not ticket_settings_data:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                            await interaction.response.defer()
                            new_ticket_panel_channel_id = interaction.data['values'][0]
                            await storage.ticket_settings.update(
                                id=ticket_settings_data.get('id'),
                                guild_id=ctx.guild.id,
                                ticket_module_id=MODULE_ID,
                                ticket_panel_channel_id=new_ticket_panel_channel_id
                            )
                            # delete the old message if exists
                            try:
                                ticket_panel_channel = ctx.guild.get_channel(ticket_settings_data.get('ticket_panel_channel_id'))
                                if ticket_panel_channel:
                                    try:
                                        ticket_panel_message = await ticket_panel_channel.fetch_message(ticket_settings_data.get('ticket_panel_message_id'))
                                        await ticket_panel_message.delete()
                                    except:
                                        pass
                                await storage.ticket_settings.update(
                                    id=ticket_settings_data.get('id'),
                                    guild_id=ctx.guild.id,
                                    ticket_module_id=MODULE_ID,
                                    ticket_panel_message_id=""
                                )
                            except:
                                pass
                            await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

                    async def edit_closed_ticket_category_select_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})

                            if not ticket_settings_data:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                            await interaction.response.defer()
                            new_closed_ticket_category_id = interaction.data['values'][0]
                            await storage.ticket_settings.update(
                                id=ticket_settings_data.get('id'),
                                guild_id=ctx.guild.id,
                                ticket_module_id=MODULE_ID,
                                closed_ticket_category_id=new_closed_ticket_category_id
                            )
                            await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

                    
                    async def enable_disable_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                            if not ticket_settings_data:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                            await interaction.response.defer()
                            await storage.ticket_settings.update(
                                id=ticket_settings_data.get('id'),
                                guild_id=ctx.guild.id,
                                ticket_module_id=MODULE_ID,
                                enabled=not ticket_settings_data.get('enabled',False)
                            )
                            await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

                    async def edit_ticket_limit_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                            if not ticket_settings_data:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                            
                            class set_ticket_limit(discord.ui.Modal,title="Set Ticket Limit"):
                                new_ticket_limit_field = discord.ui.TextInput(
                                    label="Enter the new ticket limit",
                                    placeholder="Enter the new ticket limit",
                                    row=0,
                                    default=str(ticket_settings_data.get('ticket_limit','1')),
                                    required=True
                                )
                                async def on_submit(self, interaction: discord.Interaction):
                                    try:
                                        if interaction.user.id != ctx.author.id:
                                            return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                                        new_ticket_limit = int(self.new_ticket_limit_field.value)
                                        if new_ticket_limit < 1:
                                            return await interaction.response.send_message(embed=discord.Embed(description="Ticket limit should be greater than 0",color=color.red),ephemeral=True,delete_after=10)
                                        ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                                        if not ticket_settings_data:
                                            return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                                        await interaction.response.defer()
                                        await storage.ticket_settings.update(
                                            id=ticket_settings_data.get('id'),
                                            guild_id=ctx.guild.id,
                                            ticket_module_id=MODULE_ID,
                                            ticket_limit=new_ticket_limit
                                        )
                                        await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                                    except Exception as e:
                                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                            await interaction.response.send_modal(set_ticket_limit())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

                    async def edit_open_ticket_category_select_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != ctx.author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                            ticket_settings_data = cache.ticket_settings.get(str(ctx.guild.id),{}).get(MODULE_ID,{})
                            if not ticket_settings_data:
                                return await interaction.response.send_message(embed=discord.Embed(description="Ticket module not found",color=color.red),ephemeral=True,delete_after=10)
                            await interaction.response.defer()
                            new_open_ticket_category_id = interaction.data['values'][0]
                            await storage.ticket_settings.update(
                                id=ticket_settings_data.get('id'),
                                guild_id=ctx.guild.id,
                                ticket_module_id=MODULE_ID,
                                open_ticket_category_id=new_open_ticket_category_id
                            )
                            await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    await interaction.message.edit(embed=await get_selected_edit_embed(),view=await get_selected_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            
            async def previous_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                    nonlocal current_page_index
                    current_page_index -= 1
                    await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def stop_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                    nonlocal cancled
                    cancled = True
                    await interaction.response.edit_message(embed=await get_embed(),view=await get_view(disabled=True))
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def next_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not authorized to use this button",color=color.red),ephemeral=True,delete_after=10)
                    nonlocal current_page_index
                    current_page_index += 1
                    await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")




            message = await ctx.send(embed=await get_embed(),view=await get_view())

            while not cancled:
                try:
                    view_timeout -= 1
                    if view_timeout <= 0:
                        await message.edit(view=await get_view(disabled=True))
                        break
                    await asyncio.sleep(1)
                except:
                    break
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @ticket.command(
        name='close',
        help="Close a ticket",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def ticket_close(self,ctx: commands.Context,module_id:int=None,ticket_id:int=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator'):
                return
            if not module_id and not ticket_id:
                ticket_data = await storage.tickets.get(guild_id=ctx.guild.id,channel_id=ctx.channel.id)
                if not ticket_data:
                    return await ctx.send(embed=discord.Embed(description="This is not a ticket channel",color=color.red))
            else:
                ticket_data = await storage.tickets.get(guild_id=ctx.guild.id,ticket_module_id=module_id,ticket_id=ticket_id)
                if not ticket_data:
                    return await ctx.send(embed=discord.Embed(description="Ticket not found",color=color.red))
            if ticket_data.get('closed',False):
                return await ctx.send(embed=discord.Embed(description=f"Ticket: {ticket_data.get('ticket_id')} is already closed",color=color.red))
            if await ticket_panel.ticket_close_action(guild=ctx.guild,ticket_data=ticket_data,bot=self.bot,closed_by=ctx.author):
                await ctx.send(embed=discord.Embed(description="Ticket closed successfully",color=color.green))
            else:
                await ctx.send(embed=discord.Embed(description="Failed to close the ticket",color=color.red))
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")


    @ticket.command(
        name='delete',
        help="Delete a ticket",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    async def ticket_delete(self,ctx: commands.Context,module_id:int=None,ticket_id:int=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator'):
                return
            if not module_id and not ticket_id:
                ticket_data = await storage.tickets.get(guild_id=ctx.guild.id,channel_id=ctx.channel.id)
                if not ticket_data:
                    return await ctx.send(embed=discord.Embed(description="This is not a ticket channel",color=color.red))
            else:
                ticket_data = await storage.tickets.get(guild_id=ctx.guild.id,ticket_module_id=module_id,ticket_id=ticket_id)
                if not ticket_data:
                    return await ctx.send(embed=discord.Embed(description="Ticket not found",color=color.red))
            
            if not ticket_data.get('closed',False):
                return await ctx.send(embed=discord.Embed(description=f"Ticket: {ticket_data.get('ticket_id')} is not closed yet",color=color.red))

            embed = discord.Embed(
                title="Delete Confirmation",
                description="Do you want to delete the Ticket Channel?",
                color=color.red
            )
            view = discord.ui.View(timeout=None)
            DeleteButton = discord.ui.Button(
                label="Delete Channel",
                style=discord.ButtonStyle.red,
                emoji=self.bot.emoji.DELETE,
                custom_id="delete_channel"
            )
            DeleteButton.callback = lambda i: ticket_panel.delete_channel_callback(i,self.bot,ticket_data)
            view.add_item(DeleteButton)
            await ctx.send(embed=embed,view=view)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
