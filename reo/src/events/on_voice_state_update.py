import datetime,asyncio,discord
from discord.ext import commands

from reo.console.logging import logger
from reo.src.checks import checks

import traceback,sys

from reo.memory.cache import cache

from storage import j2c as j2c_db

from reo.style import color

from reo.engine.Bot import AutoShardedBot


from reo.src.modules import j2c_controller

from aiohttp import ClientResponseError

from aiohttp import ClientResponseError

async def retry_operation(operation, *args, retries=5, delay=1, backoff=2, **kwargs):
    for attempt in range(retries):
        try:
            return await operation(*args, **kwargs)
        except ClientResponseError as e:
            if e.status == 429:  # HTTP status code for Too Many Requests
                retry_after = int(e.headers.get('Retry-After', delay))
                await asyncio.sleep(retry_after)
            else:
                raise
        await asyncio.sleep(delay)
        delay *= backoff
    raise Exception("Max retries exceeded")

async def change_j2c_owner(bot,data,channel=None,new_owner=None):

        if not channel:
            channel = bot.get_channel(data.get('channel_id'))
        if not channel:
            return logger.error(f"Channel not found in change_j2c_owner")
        if not isinstance(channel,discord.VoiceChannel):
            return logger.error(f"Channel is not a voice channel in change_j2c_owner")
        if not new_owner:
            # get a random member from the channel
            members = [member for member in channel.members if not member.bot]
            new_owner = members[0]
        if not new_owner:
            return logger.error(f"New owner not found in change_j2c_owner")
        old_owner = bot.get_user(data.get('owner_id'))
        try:
            if old_owner:
                # remove old owner from the channel overwrites
                try:
                    await channel.set_permissions(old_owner,overwrite=None)
                except Exception as e:
                    logger.error(f"Error in on_voice_state_update.change_j2c_owner.remove_old_owner: {e}")
            # add new owner perms_overwrites to the channel
            permissions = discord.PermissionOverwrite(
                view_channel=True,
                manage_channels=True,
                connect=True,
                speak=True,
                mute_members=True,
                deafen_members=True,
                manage_messages=True,
                stream=True,
                send_messages=True,
                add_reactions=True,
                embed_links=True,
                attach_files=True,
                read_message_history=True
            )
            await channel.set_permissions(new_owner,overwrite=permissions)

            await j2c_db.update(id=data.get('id'),owner_id=new_owner.id)

            try:
                await retry_operation(channel.edit, name=f"{new_owner.display_name}'s VC")
            except Exception as e:
                logger.error(f"Error in on_voice_state_update.change_j2c_owner.edit_channel_name: {e}")
        except Exception as e:
            logger.error(f"Error in on_voice_state_update.change_j2c_owner: {e}")



class on_voice_state_update(commands.Cog):
    def __init__(self, bot):
        self.bot: AutoShardedBot = bot
    
    j2c_cooldown_data = {}

    async def voice_state_update_log(self,member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
        try:
            # only join or leave or move will pass else will return in action
            if before.channel == after.channel:
                return 

            if before.channel and after.channel:
                action = "move"
            elif before.channel and not after.channel:
                action = "leave"
            elif not before.channel and after.channel:
                action = "join"
            else:
                return 

            
            guilds_log_cache = cache.guilds_log.get(str(member.guild.id))
            if not guilds_log_cache:
                return
            if not guilds_log_cache.get('enabled'):
                return logger.error(f"Guild {member.guild.name} has logging disabled")
            channel_id = guilds_log_cache.get('voice_state_update_channel_id')
            if not channel_id:
                return logger.error(f"Channel ID not found for voice state update log in {member.guild.name}")
            
            if action == "move":
                embed = discord.Embed(
                    title=f'{member.display_name} has moved to a different voice channel',
                    description=f'**__User:__** {member.mention}\n**__User ID:__** `{member.id}`\n\n**__From Channel:__** {before.channel.mention}\n**__To Channel:__** {after.channel.mention}\n\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                    color=color.yellow
                )
            elif action == "join":
                embed = discord.Embed(
                    title=f'{member.display_name} has joined a voice channel',
                    description=f'**__User:__** {member.mention}\n**__User ID:__** `{member.id}`\n**__Channel:__** {after.channel.mention}\n\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                    color=color.green
                )
            elif action == "leave":
                embed = discord.Embed(
                    title=f'{member.display_name} has left a voice channel',
                    description=f'**__User:__** {member.mention}\n**__User ID:__** `{member.id}`\n**__Channel:__** {before.channel.mention}\n\n**__Time:__** <t:{int(datetime.datetime.now().timestamp())}>',
                    color=color.red
                )
            embed.set_footer(text=f'User ID: {member.id}')
            embed.set_thumbnail(url=member.display_avatar.url)
            await self.bot.log.send(guild=member.guild,embed=embed,type=f"voice_state_update")
        except Exception as e:
            logger.error(f"Error in on_voice_state_update.voice_state_update_log: {e}")

    

    async def process_existing_vc(self,data):
        try:
            channel = self.bot.get_channel(data.get('channel_id'))
            if not channel:
                return await j2c_db.delete(id=data.get('id'))
            if not isinstance(channel,discord.VoiceChannel):
                return await j2c_db.delete(id=data.get('id'))
            owner_id = data.get('owner_id')
            if owner_id in [member.id for member in channel.members]:
                return logger.info(f"Owner is still in the channel")
            if len([member for member in channel.members if not member.bot]) == 0:
                await channel.delete()
                await j2c_db.delete(id=data.get('id'))
            else:
                await change_j2c_owner(self.bot,data,channel)               
        except Exception as e:
            logger.error(f"Error in on_voice_state_update.remove_existing_vc: {e}")

    async def j2c_module(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        try:
            if str(member.guild.id) not in cache.j2c_settings:
                return
            if not cache.j2c_settings.get(str(member.guild.id),{}).get('enabled',False):
                return logger.error(f"J2C is disabled in {member.guild.name}")
        
            # only join or leave or move will pass else will return in action
            if before.channel == after.channel:
                return 

            if before.channel and after.channel:
                action = "move"
            elif before.channel and not after.channel:
                action = "leave"
            elif not before.channel and after.channel:
                action = "join"
            else:
                return 


            
            if action == "join" or action == "move":
                for channel_id,data in cache.j2c.items():
                    if data.get('owner_id') == member.id:
                        await self.process_existing_vc(data)
                
                if member.id == cache.j2c.get(str(after.channel.id),{}).get('owner_id'):
                    return logger.error(f"Owner moved the channel")
                
                if after.channel.id != cache.j2c_settings.get(str(member.guild.id),{}).get('create_vc_channel_id'):
                    return logger.error(f"Member joined a different channel")
                
                # if the member create 3 channel under 5 minutes then return
                if str(member.guild.id) in self.j2c_cooldown_data:
                    if str(member.id) in self.j2c_cooldown_data[str(member.guild.id)]:
                        if self.j2c_cooldown_data[str(member.guild.id)][str(member.id)].get('created',0) >= 3:
                            if datetime.datetime.now().timestamp() - self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['last_created'] < 300:
                                # remove the member from the channel
                                await member.move_to(None)
                                embed = discord.Embed(
                                    title="You have created 3 channels under 5 minutes",
                                    description=f"You can only create 3 channels under 5 minutes. You can try again <t:{int(self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['last_created']+300)}:R>",
                                    color=color.red
                                )
                                try:
                                    await member.send(embed=embed)
                                except Exception as e:
                                    pass               
                                return logger.error(f"Member created 3 channels under 5 minutes")
                            


                
                category = self.bot.get_channel(cache.j2c_settings.get(str(member.guild.id),{}).get('create_vc_category_id'))

                overwrites = {
                    member: discord.PermissionOverwrite(
                        view_channel=True,
                        manage_channels=True,
                        connect=True,
                        speak=True,
                        mute_members=True,
                        deafen_members=True,
                        manage_messages=True,
                        stream=True,
                        send_messages=True,
                        add_reactions=True,
                        embed_links=True,
                        attach_files=True,
                        read_message_history=True
                    )
                }

                channel = await member.guild.create_voice_channel(
                    name=f"{member.display_name}'s VC",
                    category=category,
                    reason=f"J2C Channel for {member.display_name}",
                    overwrites=overwrites,
                    rtc_region=after.channel.rtc_region
                )
                if str(member.guild.id) not in self.j2c_cooldown_data:
                    self.j2c_cooldown_data[str(member.guild.id)] = {}
                if str(member.id) not in self.j2c_cooldown_data[str(member.guild.id)]:
                    self.j2c_cooldown_data[str(member.guild.id)][str(member.id)] = {}
                if 'created' not in self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]:
                    self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['created'] = 0
                if 'last_created' not in self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]:
                    self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['last_created'] = 0
                if datetime.datetime.now().timestamp() - self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['last_created'] > 300:
                    self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['created'] = 0
                else:
                    self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['created'] += 1
                self.j2c_cooldown_data[str(member.guild.id)][str(member.id)]['last_created'] = datetime.datetime.now().timestamp()
                data = await j2c_db.insert(
                    channel_id=channel.id,
                    guild_id=member.guild.id,
                    owner_id=member.id
                )
                # move the member to the channel
                await member.move_to(channel)                
                await j2c_controller.controller_module(bot=self.bot,data=data,channel=channel)

            elif action == "leave":
                for channel_id,data in cache.j2c.items():
                    if data.get('owner_id') == member.id:
                        await self.process_existing_vc(data)

        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

    # function check if the bot is disconnected from a discord server voice channel
    async def check_bot_disconnected_from_music_player(self,member:discord.Member,before:discord.VoiceState,after:discord.VoiceState):
        try:
            if member != self.bot.user:
                return 
            if not before.channel:
                return 
            if before.channel and after.channel:
                return logger.error(f"Bot moved to a different channel")
            if before.channel and not after.channel:
                # logger.info(f"Bot left a voice channel")
                MusicCog = self.bot.get_cog("Music")
                if MusicCog:
                    await MusicCog.send_music_controls(guild=member.guild, end=True)
            else:
                return logger.error(f"Unknown action in check_bot_disconnected_from_music_player")
        except Exception as e:
            logger.error(f"Error in on_voice_state_update.check_bot_disconnected_from_music_player: {e}")


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        try:
            asyncio.create_task(self.voice_state_update_log(member,before,after))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.j2c_module(member,before,after))
        except Exception as e:
            pass
        try:
            asyncio.create_task(self.check_bot_disconnected_from_music_player(member,before,after))
        except Exception as e:
            pass
        