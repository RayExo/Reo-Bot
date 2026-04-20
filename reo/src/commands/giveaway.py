import discord
from discord.ext import commands
import asyncio
import traceback,sys

import storage.custom_roles
import storage.custom_roles_permissions
import storage.giveaway_participants
import storage.giveaways
import storage.giveaways_permissions
from reo.console.logging import logger
from reo.memory.cache import cache
from reo.src.checks import checks
import json



from reo.style import color

from reo.engine.Bot import AutoShardedBot

import storage
import datetime

import random

def get_winner(participents,winner_limit):
    if len(participents) == 0:
        return []
    if len(participents) < winner_limit:
        winner_limit = len(participents)
    winners_list = random.choices(population=[partcipent['user_id'] for partcipent in participents],weights=[partcipent.get('winning_rate',50) for partcipent in participents],k=winner_limit)
    return winners_list

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        class cog_info:
            name =  "Giveaway"
            category = "Extra"
            description =  "Giveaway related commands"
            hidden =  False
            emoji = self.bot.emoji.GIVEAWAY
        self.cog_info = cog_info
        self.all_app_commands = None
    
    # Giveaway create only slash command
    @commands.hybrid_group(
        name="giveaway",
        help="Giveaway related commands",
        invoke_without_command=True,
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def giveaway_command(self, ctx:commands.Context):
        try:
            if not await checks.check_is_owner(ctx,notify=True):
                return
            
            if not self.all_app_commands:
                self.all_app_commands = await self.bot.tree.fetch_commands()
            
            embed = discord.Embed(
                title="Giveaway Commands",
                description="Here are the available giveaway commands",
                color=color.random_color()
            )
            
            def get_app_command(name):
                for cmd in self.all_app_commands:
                    if cmd.name == name:
                        return cmd
                return None
            
            app_command = get_app_command(ctx.command.name)

            if app_command:
                if app_command.options:
                    embed.description += f"\n\n**• Primary Command:** `{self.bot.BotConfig.PREFIX}{app_command.name} {' '.join([f'<{arg}>' for arg in ctx.command.clean_params])}`"
                    embed.description += f"\n\n**• Options:**\n"
                    for option in app_command.options:
                        embed.description += f"\n> {option.mention}\n> {option.description}\n"
                else:
                    embed.description += f"\n\n**• Primary Command:** {app_command.mention}"
            else:
                embed.description += f"\n\n**• Primary Command:** `{self.bot.BotConfig.PREFIX}{ctx.command.name} {' '.join([f'<{arg}>' for arg in ctx.command.clean_params])}`"

            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @giveaway_command.command(
        name="create",
        help="Create a giveaway Event",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def giveaway_create(self, ctx:commands.Context,time:str,winners:int,prize:str,channel:discord.TextChannel=None):
        if not ctx.interaction:
            await ctx.send(embed=discord.Embed(description="This command can only be used as a slash command",color=color.red),delete_after=5)
            return
        try:
            if not await checks.check_for_giveaway_permissions(ctx,permission="manage_guild"):
                return
            if not channel:
                channel = ctx.channel
            await self.start_giveaway(ctx=ctx,time=time,winners=winners,prize=prize,channel=channel)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")


    @commands.hybrid_command(
        name="gstart",
        help="Create a giveaway Event",
        aliases=["gcreate"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def gstart(self, ctx:commands.Context,time:str,winners:int,*,prize:str):
        try:
            if not await checks.check_for_giveaway_permissions(ctx,permission="manage_guild"):
                return
            await ctx.message.delete()
            await self.start_giveaway(ctx=ctx,time=time,winners=winners,prize=prize,channel=ctx.channel)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")



    async def start_giveaway(self,ctx:commands.Context,time:str,winners:int,prize:str,channel:discord.TextChannel):
        try:
            try:
                time = time.lower()
                if time:
                    time = time.replace('s','').replace('m','*60').replace('h','*60*60').replace('d','*60*60*24')
                    time = eval(time)
            except Exception as e:
                time = None
            if not time:
                await ctx.send(embed=discord.Embed(description="Invalid time format. Example: `1d 1h 1m 1s`",color=color.red),delete_after=5)
                return

            if ctx.interaction:
                await ctx.interaction.response.defer(thinking=True,ephemeral=True)
            else:
                message = await channel.send(embed=discord.Embed(
                    description=f"{self.bot.emoji.LOADING} Creating giveaway...",
                    color=color.orange
                ))
                if not message:
                    await ctx.send(embed=discord.Embed(description="Something went wrong while creating the giveaway",color=color.red),delete_after=5)
                    return
            
            guilds_subscription = cache.guilds.get(str(ctx.guild.id),{}).get('subscription','free')

            if guilds_subscription == 'free':
                giveaway_limit = 1
            elif guilds_subscription == 'silver_guild_preminum':
                giveaway_limit = 3
            elif guilds_subscription == 'golden_guild_premium':
                giveaway_limit = 5
            elif guilds_subscription == 'diamond_guild_premium':
                giveaway_limit = 10
            else:
                giveaway_limit = 1

            guild_giveaways = cache.giveaways.get(str(ctx.guild.id),{})
            if len(guild_giveaways) >= giveaway_limit:
                embed = discord.Embed(description=f"Your server has reached the maximum giveaway limit of {giveaway_limit}",color=color.red)
                if ctx.interaction:
                    await ctx.interaction.edit_original_response(embed=embed)
                else:
                    await message.edit(embed=embed,delete_after=10)
                return
            
            giveaway = await storage.giveaways.insert(
                guild_id=ctx.guild.id,
                channel_id=channel.id,
                host_id=ctx.author.id,
                winner_limit=winners,
                prize=prize,
                ends_at=(datetime.datetime.utcnow() + datetime.timedelta(seconds=time)).isoformat(),
                created_at=datetime.datetime.utcnow().isoformat()
            )
            await self.create_giveaway_message(data=giveaway,channel=channel,waiting_message=message if not ctx.interaction else ctx.interaction)

        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    async def create_giveaway_message(self,data,channel:discord.TextChannel=None,waiting_message:any=None):
        try:
            giveaway_id = data.get('giveaway_id')
            if not giveaway_id:
                return logger.error(f"Giveaway ID not found in data: {data}")
            if not channel:
                channel = await self.bot.fetch_channel(data.get('channel_id'))
                if not channel:
                    return logger.error(f"Channel not found for giveaway {giveaway_id}")
                
            
            message_id = data.get('message_id')
            winners = data.get('winners')
            winner_limit = data.get('winner_limit')
            prize = data.get('prize')
            ends_at = data.get('ends_at')
            host_id = data.get('host_id')

            # participents = await storage.giveaway_participants.gets(guild_id=channel.guild.id,giveaway_id=giveaway_id)

            embed = discord.Embed(
                description=f"""**Prize:** {prize}\n**Ends at:** <t:{int(ends_at.timestamp())}:R>\n**Hosted by:** <@{host_id}>\n{f'**Winners:** {winner_limit}' if winner_limit > 1 else ''}""",
                color=color.green
            )
            embed.set_thumbnail(url=self.bot.urls.GIVEAWAY)
            embed.set_author(name="Giveaway Started",icon_url=channel.guild.icon.url if channel.guild.icon else self.bot.user.display_avatar.url,url=self.bot.urls.WEBSITE)
            embed.set_footer(text=f"Giveaway ID: {giveaway_id} | Ends at: ",icon_url=channel.guild.icon.url if channel.guild.icon else self.bot.user.display_avatar.url)
            embed.timestamp = ends_at

            
            async def get_view():
                total_participants = await storage.giveaway_participants.count(guild_id=channel.guild.id,giveaway_id=giveaway_id)
                view = discord.ui.View(timeout=None)

                enter_button = discord.ui.Button(
                    label=f"{total_participants}",
                    style=discord.ButtonStyle.green,
                    emoji=self.bot.emoji.GIVEAWAY
                )
                enter_button.callback = lambda i: enter_button_callback(i)
                view.add_item(enter_button)

                participants_button = discord.ui.Button(
                    label="Participants",
                    style=discord.ButtonStyle.gray,
                    emoji=self.bot.emoji.PARTICIPANTS
                )
                participants_button.callback = lambda i: participants_button_callback(i)
                view.add_item(participants_button)
                return view


            
            try:
                message = await channel.fetch_message(message_id)
            except:
                message = None
            if message:
                logger.info(f"Giveaway message already created in channel {channel.id}")
                try:
                    await message.edit(embed=embed,view=await get_view())
                    logger.info(f"Giveaway message updated in channel {channel.id}")
                except:
                    logger.error(f"Failed to update giveaway message in channel {channel.id}")
                    message = await channel.send(embed=embed,view=await get_view())
                    if not message:
                        return logger.error(f"Failed to send giveaway message in channel {channel.id}")
                    await storage.giveaways.update(id=data['id'],message_id=message.id)
                    logger.info(f"Giveaway message created in channel {channel.id}")
            else:
                message = await channel.send(embed=embed,view=await get_view())
                if not message:
                    return logger.error(f"Failed to send giveaway message in channel {channel.id}")
                await storage.giveaways.update(id=data['id'],message_id=message.id)
                logger.info(f"Giveaway message created in channel {channel.id}")
            
            # add the giveaway view update to queue to update it in intervals with 10s if many users are entering the giveaway
            update_participants_tasks = {}  # {message_id: asyncio.Task}

            async def update_participants():
                try:
                    message_id = message.id

                    # Cancel the previous task if it exists
                    if message_id in update_participants_tasks:
                        update_participants_tasks[message_id].cancel()

                    async def debounce_update():
                        try:
                            await asyncio.sleep(5)  # Debounce interval
                            await message.edit(view=await get_view())
                        except asyncio.CancelledError:
                            # Task was cancelled, do nothing
                            pass
                        except Exception as e:
                            logger.error(f"Failed to update giveaway message in channel {channel.id}: {e}")

                    # Create a new task for the debounce update
                    update_participants_tasks[message_id] = asyncio.create_task(debounce_update())

                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            enter_button_timeout = {} # user_id:time when the button was clicked
            async def enter_button_callback(interaction:discord.Interaction):
                try:
                    nonlocal enter_button_timeout
                    if interaction.user.id in enter_button_timeout:
                        if (datetime.datetime.now() - enter_button_timeout[interaction.user.id]).total_seconds() < 5:
                            return await interaction.response.send_message(content=f"{self.bot.emoji.ERROR} You are clicking too fast",ephemeral=True,delete_after=5)
                        else:
                            del enter_button_timeout[interaction.user.id]
                    enter_button_timeout[interaction.user.id] = datetime.datetime.now()

                    cache_data = cache.giveaways.get(str(channel.guild.id),{}).get(str(giveaway_id),{})
                    if not cache_data:
                        return await interaction.response.send_message(content=f"{self.bot.emoji.ERROR} Giveaway already ended",ephemeral=True)
                    if cache_data.get('ended'):
                        return await interaction.response.send_message(content=f"{self.bot.emoji.ERROR} Giveaway already ended",ephemeral=True)

                    await interaction.response.defer(thinking=True,ephemeral=True)
                    view = discord.ui.View(timeout=60)
                    exit_button = discord.ui.Button(
                        label="Exit",
                        style=discord.ButtonStyle.gray,
                        emoji=self.bot.emoji.STOP
                    )
                    exit_button.callback = lambda i: exit_button_callback(i)
                    view.add_item(exit_button)

                    user = interaction.user

                    async def exit_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != user.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                            await storage.giveaway_participants.delete(guild_id=interaction.guild.id,giveaway_id=giveaway_id,user_id=user.id)
                            await interaction.response.edit_message(content=f"{self.bot.emoji.SUCCESS} You have exited the giveaway!",view=None)
                            try:
                                asyncio.create_task(update_participants())
                            except:
                                pass
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                    
                    participated = await storage.giveaway_participants.get(guild_id=interaction.guild.id,giveaway_id=giveaway_id,user_id=interaction.user.id)
                    if participated:
                        return await interaction.edit_original_response(content=f"{self.bot.emoji.ERROR} You have already entered the giveaway!",view=view)
                    await storage.giveaway_participants.insert(
                        guild_id=interaction.guild.id,
                        giveaway_id=giveaway_id,
                        user_id=interaction.user.id,
                    )
                    await interaction.edit_original_response(content=f"{self.bot.emoji.SUCCESS} You have entered the giveaway!")
                    try:
                        asyncio.create_task(update_participants())
                    except:
                        pass
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            participants_button_timeout = {} # user_id:time when the button was clicked
            async def participants_button_callback(interaction:discord.Interaction):
                try:
                    nonlocal participants_button_timeout
                    if interaction.user.id in participants_button_timeout:
                        if (datetime.datetime.now() - participants_button_timeout[interaction.user.id]).total_seconds() < 60:
                            return await interaction.response.send_message(content=f"{self.bot.emoji.ERROR} You are clicking too fast",ephemeral=True,delete_after=5)
                        else:
                            del participants_button_timeout[interaction.user.id]
                    participants_button_timeout[interaction.user.id] = datetime.datetime.now()
                    await interaction.response.defer(thinking=True,ephemeral=True)
                    participants = await storage.giveaway_participants.gets(guild_id=interaction.guild.id,giveaway_id=giveaway_id)
                    if not participants:
                        return await interaction.edit_original_response(content=f"{self.bot.emoji.ERROR} No participants found")
                    
                    # make participants 5 by 5 pages
                    data_per_page = 10
                    participants = [participants[i:i + data_per_page] for i in range(0, len(participants), data_per_page)]

                    current_page_index = 0

                    async def get_embed():
                        nonlocal current_page_index
                        if current_page_index >= len(participants):
                            current_page_index = 0
                        datas = participants[current_page_index]
                        
                        embed = discord.Embed(
                            description=f"**Giveaway `{giveaway_id}` Participants**\n\n",
                            color=color.green
                        )
                        embed.set_author(
                            name=f"{channel.guild.name} Participants",
                            icon_url=channel.guild.icon.url if channel.guild.icon else self.bot.user.display_avatar.url,
                            url=self.bot.urls.WEBSITE
                        )
                        embed.set_footer(text=f"Page {current_page_index+1}/{len(participants)}")
                        for index,data in enumerate(datas):
                            user_id = data.get('user_id')
                            embed.description+=f"{index+1}. <@{user_id}>\n"

                        return embed
                    
                    timeout_time = 60
                    cancled = False
                    def reset_timeout():
                        nonlocal timeout_time
                        timeout_time = 60

                    async def get_view(disabled=False):
                        if len(participants) == 1:
                            nonlocal cancled
                            cancled = True
                            return None
                        view = discord.ui.View(timeout=60)
                        reset_timeout()
                        previous_page = discord.ui.Button(
                            label="Previous",
                            emoji=self.bot.emoji.PREVIOUS,
                            style=discord.ButtonStyle.gray,
                            row=0,
                            disabled=current_page_index == 0
                        )
                        previous_page.callback = lambda i: previous_page_callback(i)
                        view.add_item(previous_page)

                        stop_button = discord.ui.Button(
                            label="Stop",
                            emoji=self.bot.emoji.STOP,
                            style=discord.ButtonStyle.red,
                            row=0
                        )
                        stop_button.callback = lambda i: stop_button_callback(i)
                        view.add_item(stop_button)

                        next_page = discord.ui.Button(
                            label="Next",
                            emoji=self.bot.emoji.NEXT,
                            style=discord.ButtonStyle.gray,
                            row=0,
                            disabled=current_page_index == len(participants)-1
                        )
                        next_page.callback = lambda i: next_page_callback(i)
                        view.add_item(next_page)

                        if disabled:
                            for item in view.children:
                                item.disabled = True
                        return view

                    author = interaction.user
                    
                    async def previous_page_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                            nonlocal current_page_index
                            current_page_index -= 1
                            embed = await get_embed()
                            view = await get_view()
                            await interaction.response.edit_message(embed=embed,view=view)
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")

                    async def stop_button_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                            nonlocal cancled
                            cancled = True
                            await interaction.response.edit_message(view=await get_view(disabled=True))
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")


                    async def next_page_callback(interaction:discord.Interaction):
                        try:
                            if interaction.user.id != author.id:
                                return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                            nonlocal current_page_index
                            current_page_index += 1
                            embed = await get_embed()
                            view = await get_view()
                            await interaction.response.edit_message(embed=embed,view=view)
                        except Exception as e:
                            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")

                    await interaction.edit_original_response(embed=await get_embed(),view=await get_view())

                    while not cancled:
                        if timeout_time <= 0:
                            await interaction.edit_original_response(view=await get_view(disabled=True))
                            break
                        await asyncio.sleep(1)
                        timeout_time -= 1
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")


            if waiting_message:
                if isinstance(waiting_message,discord.Interaction):
                    await waiting_message.edit_original_response(content=f"{self.bot.emoji.SUCCESS} Giveaway created! to <#{channel.id}>")
                elif isinstance(waiting_message,discord.Message):
                    await waiting_message.delete()
            time_to_sleep = (ends_at - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
            logger.info(f"Sleeping for {time_to_sleep} seconds for giveaway {giveaway_id} in channel {channel.id}")
            await asyncio.sleep(time_to_sleep if time_to_sleep > 0 else 0)
            await self.end_giveaway(guild_id=channel.guild.id,giveaway_id=giveaway_id)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    async def end_giveaway(self,guild_id:int,giveaway_id:int):
        try:
            data = cache.giveaways.get(str(guild_id),{}).get(str(giveaway_id),{})
            if not data:
                return logger.error(f"Giveaway data not found for giveaway {giveaway_id} in guild {guild_id} in cache. Maybe it was deleted?")
            if data.get('ended'):
                return logger.error(f"Giveaway {giveaway_id} in guild {guild_id} is already ended")
            
            participents = await storage.giveaway_participants.gets(guild_id=guild_id,giveaway_id=giveaway_id)
            
            # every perciptent has a winning rate of 1 - 100
            # i want to get winners amount of participents as winners by their winning rate

            winner_limit = data.get('winner_limit')

            
            winners_list = get_winner(participents,winner_limit)

            channel = self.bot.get_channel(data.get('channel_id',None))
            if not channel:
                return logger.error(f"Channel not found for giveaway {giveaway_id} in guild {guild_id}")
            
            prize = data.get('prize')
            host_id = data.get('host_id')
            ends_at = data.get('ends_at')
            


            winners_text = "No winners Selected" if not winners_list else ", ".join(
                [f"<@{winner}>" for winner in winners_list]
            )
            embed = discord.Embed(
                description=(
                    f"**Prize:** {prize}\n"
                    f"**Ended:** <t:{int(ends_at.timestamp())}:R>\n"
                    f"**Hosted by:** <@{host_id}>\n"
                    f"**Winners:** {winners_text}"
                ),
                color=color.orange
            )
            embed.set_author(name="Giveaway Ended!",icon_url=channel.guild.icon.url if channel.guild.icon else self.bot.user.display_avatar.url)
            embed.set_footer(text=f"Giveaway ID: {giveaway_id} | Ended: ",icon_url=channel.guild.icon.url if channel.guild.icon else self.bot.user.display_avatar.url)
            embed.timestamp = ends_at
            embed.set_thumbnail(url=self.bot.urls.GIVEAWAY)
            message_id = data.get('message_id')
            try:
                message = await channel.fetch_message(message_id) if message_id else None
            except:
                message = None
            if message:
                view = discord.ui.View.from_message(message)
                for item in view.children:
                    item.disabled = True
                await message.edit(embed=embed,view=view)
            else:
                message = await channel.send(embed=embed)
                if not message:
                    return logger.error(f"Failed to send giveaway message in channel {channel.id}")
                await storage.giveaways.update(id=data['id'],message_id=message.id)
                logger.info(f"Giveaway message created in channel {channel.id}")
            await storage.giveaways.update(id=data['id'],ended=True,winners=json.dumps(winners_list))

            if not winners_list:
                return await message.reply(f"**Giveaway Ended!** No one participated in the giveaway!,Hosted by <@{host_id}>")
            
            await message.reply(f"**Congratulations** {' | '.join([f'<@{winner}>' for winner in winners_list])}! You have won the **{prize}** giveaway!,Hosted by <@{host_id}>")
            logger.info(f"Giveaway {giveaway_id} in guild {guild_id} ended")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        
    @giveaway_command.command(
        name="delete",
        help="Delete a giveaway Event",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def giveaway_delete(self, ctx:commands.Context,giveaway_id:int):
        try:
            await ctx.invoke(self.gdelete,giveaway_id=giveaway_id)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @commands.hybrid_command(
        name="gdelete",
        help="Delete a giveaway Event",
        aliases=["gremove"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def gdelete(self,ctx:commands.Context,giveaway_id:int):
        try:
            if ctx.interaction:
                await ctx.interaction.response.defer(thinking=True,ephemeral=True)
            if not await checks.check_for_giveaway_permissions(ctx,'administrator'):
                return
            message = await ctx.send(embed=discord.Embed(
                description=f"{self.bot.emoji.LOADING} Deleting giveaway...",
                color=color.orange
            ))
            data = await storage.giveaways.get(guild_id=ctx.guild.id,giveaway_id=giveaway_id)
            if not data:
                if ctx.interaction:
                    return await ctx.interaction.edit_original_response(embed=discord.Embed(description=f"Giveaway {giveaway_id} not found",color=color.red))
                return await message.edit(embed=discord.Embed(description=f"Giveaway {giveaway_id} not found",color=color.red),delete_after=30)
            await storage.giveaways.delete(id=data.get('id'))
            await storage.giveaway_participants.delete(guild_id=ctx.guild.id,giveaway_id=giveaway_id)
            if ctx.interaction:
                await ctx.interaction.edit_original_response(embed=discord.Embed(description=f"Giveaway {giveaway_id} deleted",color=color.green))
            else:
                await message.edit(embed=discord.Embed(description=f"Giveaway {giveaway_id} deleted",color=color.green),delete_after=30)
            channel = await self.bot.fetch_channel(data.get('channel_id'))
            if not channel:
                return logger.error(f"Channel not found for giveaway {giveaway_id} in guild {ctx.guild.id}")
            message = await channel.fetch_message(data.get('message_id'))
            if message:
                await message.delete()
            else:
                return logger.error(f"Message not found for giveaway {giveaway_id} in guild {ctx.guild.id}")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    @giveaway_command.command(
        name="end",
        help="End a giveaway Event",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def giveaway_end(self, ctx:commands.Context,giveaway_id:int):
        await ctx.invoke(self.gend,giveaway_id=giveaway_id)

    @commands.hybrid_command(
        name="gend",
        help="End a giveaway Event",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def gend(self, ctx:commands.Context,giveaway_id:int):
        try:
            if ctx.interaction:
                await ctx.interaction.response.defer(thinking=True,ephemeral=True)
            if not await checks.check_for_giveaway_permissions(ctx,'administrator'):
                return
            message = await ctx.send(embed=discord.Embed(
                description=f"{self.bot.emoji.LOADING} Ending giveaway...",
                color=color.orange
            ))
            data = cache.giveaways.get(str(ctx.guild.id),{}).get(str(giveaway_id),{})
            if not data:
                if ctx.interaction:
                    return await ctx.interaction.edit_original_response(embed=discord.Embed(description=f"Giveaway {giveaway_id} not found",color=color.red))
                else:
                    return await message.edit(embed=discord.Embed(description=f"Giveaway {giveaway_id} not found",color=color.red),delete_after=30)
            await self.end_giveaway(guild_id=ctx.guild.id,giveaway_id=giveaway_id)
            if ctx.interaction:
                await ctx.interaction.edit_original_response(embed=discord.Embed(description=f"Giveaway {giveaway_id} ended",color=color.green))
            else:
                await message.edit(embed=discord.Embed(description=f"Giveaway {giveaway_id} ended",color=color.green),delete_after=30)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")


    
    @giveaway_command.command(
        name="list",
        help="List all giveaways",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def giveaway_list(self, ctx:commands.Context):
        await ctx.invoke(self.glist)
    
    @commands.hybrid_command(
        name="glist",
        help="List all giveaways",
        aliases=["gall"],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def glist(self, ctx:commands.Context):
        try:
            if not await checks.check_for_giveaway_permissions(ctx,permission="manage_guild"):
                return
            
            message = await ctx.send(embed=discord.Embed(
                description=f"{self.bot.emoji.LOADING} Fetching giveaways...",
                color=color.orange
            ))

            all_giveaways = await storage.giveaways.gets(guild_id=ctx.guild.id)

            if not all_giveaways:
                return await message.edit(embed=discord.Embed(description="No giveaways found",color=color.red),delete_after=30)

            running_giveaways = []
            ended_giveaways = []

            # reverse the giveaways to show the latest giveaways first by id
            all_giveaways = all_giveaways[::-1]

            for giveaway in all_giveaways:
                id = giveaway.get('id')
                giveaway_id = giveaway.get('giveaway_id')
                guild_id = giveaway.get('guild_id')
                channel_id = giveaway.get('channel_id')
                message_id = giveaway.get('message_id')
                host_id = giveaway.get('host_id')
                winners = giveaway.get('winners')
                winner_limit = giveaway.get('winner_limit')
                prize = giveaway.get('prize')
                ends_at = giveaway.get('ends_at')
                ended = giveaway.get('ended')
                created_at = giveaway.get('created_at')

                participants = await storage.giveaway_participants.gets(guild_id=ctx.guild.id,giveaway_id=giveaway_id)

                data = {
                    'id':id,
                    'giveaway_id':giveaway_id,
                    'guild_id':guild_id,
                    'channel_id':channel_id,
                    'message_id':message_id,
                    'host_id':host_id,
                    'winners':winners,
                    'winner_limit':winner_limit,
                    'prize':prize,
                    'ends_at':ends_at,
                    'ended':ended,
                    'participants':participants,
                    'created_at':created_at
                }
                if ended:
                    ended_giveaways.append(data)
                else:
                    running_giveaways.append(data)


            # make running_giveaways 5 by 5 pages
            data_per_page = 2
            running_giveaways = [running_giveaways[i:i + data_per_page] for i in range(0, len(running_giveaways), data_per_page)]
            ended_giveaways = [ended_giveaways[i:i + data_per_page] for i in range(0, len(ended_giveaways), data_per_page)]


            current_selected_category = running_giveaways if running_giveaways else ended_giveaways

            current_page_index = 0

            async def get_embed():
                nonlocal current_selected_category,current_page_index
                if not current_selected_category:
                    return discord.Embed(description="No giveaways found",color=color.red)
                if current_page_index >= len(current_selected_category):
                    current_page_index = 0
                datas = current_selected_category[current_page_index]
                
                embed = discord.Embed(
                    description=("Here are the Active Giveaways" if current_selected_category == running_giveaways else "Here are the Ended Giveaways") + "\n\n",
                    color=color.green if current_selected_category == running_giveaways else color.red
                )
                embed.set_author(
                    name=f"{ctx.guild.name} Giveaways",
                    icon_url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url,
                    url=self.bot.urls.WEBSITE
                )
                embed.set_footer(text=f"Page {current_page_index+1}/{len(current_selected_category)}")
                for data in datas:
                    record_id = data.get('id')
                    giveaway_id = data.get('giveaway_id')
                    guild_id = data.get('guild_id')
                    channel_id = data.get('channel_id')
                    message_id = data.get('message_id')
                    host_id = data.get('host_id')
                    winners = json.loads(data.get('winners'))
                    winner_limit = data.get('winner_limit')
                    prize = data.get('prize')
                    ends_at = data.get('ends_at')
                    ended = data.get('ended')
                    created_at = data.get('created_at')
                    participants = data.get('participants')

                    embed.description+=f"""> {self.bot.emoji.ID} **Giveaway ID:** `{giveaway_id}`
> {self.bot.emoji.CHANNEL} **Channel:** <#{channel_id}>
> {self.bot.emoji.MESSAGE} **Message:** [Click here](https://discord.com/channels/{guild_id}/{channel_id}/{message_id})
> {self.bot.emoji.HOST} **Host:** <@{host_id}>
> {self.bot.emoji.WINNERS} **Winners:** {'`No winners Selected`' if not winners else ', '.join([f'<@{winner}>' for winner in winners])}
> {self.bot.emoji.LIMIT} **Winner Limit:** `{winner_limit}`
> {self.bot.emoji.PRIZE} **Prize:** `{prize}`
> {self.bot.emoji.PARTICIPANTS} **Participants:** `{len(participants)}`
> {self.bot.emoji.ENDS} **Ended:** `{ended}`
> {self.bot.emoji.TIME} **Ends at:** <t:{int(ends_at.timestamp())}:d> <t:{int(ends_at.timestamp())}:R>
> {self.bot.emoji.CREATED} **Created at:** <t:{int(created_at.timestamp())}:d> <t:{int(created_at.timestamp())}:R>
\n"""
                
                return embed
            

            timeout_time = 60
            cancled = False
            def reset_timeout():
                nonlocal timeout_time
                timeout_time = 60
            

            async def get_view(disabled=False):
                view = discord.ui.View(timeout=60)
                reset_timeout()
                select_runing_giveaways = discord.ui.Button(
                    label="Active",
                    emoji=self.bot.emoji.ONLINE,
                    style=discord.ButtonStyle.primary,
                    row=0,
                    disabled=current_selected_category == running_giveaways or not running_giveaways
                )
                select_runing_giveaways.callback = lambda i: select_runing_giveaways_callback(i)
                view.add_item(select_runing_giveaways)

                select_ended_giveaways = discord.ui.Button(
                    label="Ended",
                    emoji=self.bot.emoji.OFFLINE,
                    style=discord.ButtonStyle.primary,
                    row=0,
                    disabled=current_selected_category == ended_giveaways or not ended_giveaways
                )
                select_ended_giveaways.callback = lambda i: select_ended_giveaways_callback(i)
                view.add_item(select_ended_giveaways)

                previous_page = discord.ui.Button(
                    label="Previous",
                    emoji=self.bot.emoji.PREVIOUS,
                    style=discord.ButtonStyle.gray,
                    row=1,
                    disabled=current_page_index == 0
                )
                previous_page.callback = lambda i: previous_page_callback(i)
                view.add_item(previous_page)

                stop_button = discord.ui.Button(
                    label="Stop",
                    emoji=self.bot.emoji.STOP,
                    style=discord.ButtonStyle.red,
                    row=1
                )
                stop_button.callback = lambda i: stop_button_callback(i)
                view.add_item(stop_button)

                next_page = discord.ui.Button(
                    label="Next",
                    emoji=self.bot.emoji.NEXT,
                    style=discord.ButtonStyle.gray,
                    row=1,
                    disabled=current_page_index == len(current_selected_category) - 1
                )

                next_page.callback = lambda i: next_page_callback(i)
                view.add_item(next_page)

                if disabled:
                    for item in view.children:
                        item.disabled = True
                return view

            async def select_runing_giveaways_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                    nonlocal current_selected_category,current_page_index
                    current_selected_category = running_giveaways
                    current_page_index = 0
                    await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def select_ended_giveaways_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                    nonlocal current_selected_category,current_page_index
                    current_selected_category = ended_giveaways
                    current_page_index = 0
                    await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def previous_page_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                    nonlocal current_page_index
                    current_page_index -= 1
                    await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def next_page_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                    nonlocal current_page_index
                    current_page_index += 1
                    await interaction.response.edit_message(embed=await get_embed(),view=await get_view())
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

            async def stop_button_callback(interaction:discord.Interaction):
                try:
                    if interaction.user.id != ctx.author.id:
                        return await interaction.response.send_message(embed=discord.Embed(description="You are not allowed to use this button",color=color.red),ephemeral=True)
                    nonlocal cancled
                    cancled = True
                    await interaction.response.edit_message(view=await get_view(disabled=True))
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                
            embed = await get_embed()
            view = await get_view()

            message = await message.edit(embed=embed,view=view)

            while not cancled:
                try:
                    if timeout_time <= 0:
                        await message.edit(view=await get_view(disabled=True))
                        break
                    await asyncio.sleep(1)
                    timeout_time -= 1
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    @giveaway_command.command(
        name="reroll",
        help="Reroll a giveaway Event",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def giveaway_reroll(self, ctx:commands.Context,giveaway_id:int,winners:int=1):
        await ctx.invoke(self.greroll,giveaway_id=giveaway_id,winners=winners)

    @commands.hybrid_command(
        name="greroll",
        help="Reroll a giveaway Event",
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def greroll(self, ctx:commands.Context,giveaway_id:int,winners:int=1):
        try:
            if not await checks.check_for_giveaway_permissions(ctx,'administrator'):
                return
            waiting_message = await ctx.send(embed=discord.Embed(
                description=f"{self.bot.emoji.LOADING} Rerolling giveaway...",
                color=color.orange
            ))
            data = await storage.giveaways.get(guild_id=ctx.guild.id,giveaway_id=giveaway_id)
            if not data:
                return await waiting_message.edit(embed=discord.Embed(description=f"Giveaway {giveaway_id} not found",color=color.red),delete_after=30)
            if not data.get('ended'):
                return await waiting_message.edit(embed=discord.Embed(description=f"Giveaway {giveaway_id} is not ended yet",color=color.red),delete_after=30)
            
            participents = await storage.giveaway_participants.gets(guild_id=ctx.guild.id,giveaway_id=giveaway_id)

            winners_list = get_winner(participents,winner_limit=winners)

            await storage.giveaways.update(id=data.get('id'),winners=json.dumps(winners_list))

            message_id = data.get('message_id')
            channel = await self.bot.fetch_channel(data.get('channel_id'))
            if channel:
                message = await channel.fetch_message(message_id) if message_id else None
            else:
                message = None
            if message:
                await message.reply(f"**Congratulations** {' | '.join([f'<@{winner}>' for winner in winners_list])}! You have won the **{data.get('prize')}** giveaway!,Hosted by <@{data.get('host_id')}>")
            else:
                await channel.send(f"**Congratulations** {' | '.join([f'<@{winner}>' for winner in winners_list])}! You have won the **{data.get('prize')}** giveaway!,Hosted by <@{data.get('host_id')}>")
            await waiting_message.delete()
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    

    @commands.hybrid_command(
        name='greqrole',
        help="Show the role set for giveaway access",
        aliases=['giveawayreqrole'],
        with_app_command=True
    )
    @checks.ignore_check()
    @checks.blacklist_check()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def giveawayrole(self,ctx:commands.Context,new_role:discord.Role=None):
        try:
            if not await checks.check_is_moderator_permissions(ctx,'administrator',role_position_check=True):
                return
            giveaway_permissions_cache = cache.giveaways_permissions.get(str(ctx.guild.id),{})
            required_role_id = giveaway_permissions_cache.get('required_role_id')
            if required_role_id:
                check_role = ctx.guild.get_role(required_role_id)
                if not check_role:
                    await storage.giveaways_permissions.delete(id=giveaway_permissions_cache.get('id'))
            giveaway_permissions_cache = cache.giveaways_permissions.get(str(ctx.guild.id),{})
            required_role_id = giveaway_permissions_cache.get('required_role_id')
            if not new_role:
                if not required_role_id:
                    return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} No giveaway role set",color=color.red).set_footer(text=f"Set a role using `{ctx.prefix}greqrole <role>`"),delete_after=30)
                return await ctx.send(embed=discord.Embed(description=f"Giveaway role is set to <@&{required_role_id}>",color=color.green).set_footer(text=f"Set a role using `{ctx.prefix}greqrole <role>`"),delete_after=30)
            else:
                if required_role_id == new_role.id:
                    return await ctx.send(embed=discord.Embed(description=f"{self.bot.emoji.ERROR} {new_role.mention} is already set as giveaway role",color=color.red),delete_after=30)
                if giveaway_permissions_cache:
                    await storage.giveaways_permissions.update(id=giveaway_permissions_cache.get('id'),required_role_id=new_role.id)
                else:
                    await storage.giveaways_permissions.insert(guild_id=ctx.guild.id,required_role_id=new_role.id)
                await ctx.send(embed=discord.Embed(description=f"Giveaway role set to {new_role.mention}",color=color.green),delete_after=30)
        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")
