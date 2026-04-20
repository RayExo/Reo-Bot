from discord.ext import commands
import wavelink
import traceback, sys

from reo.console.logging import logger
from reo.config.config import users as users_config

from reo.engine.Bot import AutoShardedBot
import asyncio
import requests
from reo.style import color

import discord

from reo.src.startup import giveaways
from reo.src.startup import j2c_controller
class ready(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot


        
    @commands.Cog.listener(name="on_ready")
    async def on_ready(self):
        try:
            logger.startup_summary(self.bot)
            logger.web_startup_summary(self.bot)
            logger.success(f"Connected as {self.bot.user}")
            try:
                asyncio.create_task(self.activity())
            except:
                pass
            try:
                asyncio.create_task(self.on_ready_startups())
            except:
                pass
            await self.bot.tree.sync()
            logger.system(f"Application Commands (Tree) Synced")
            # Load developers
            dev_ids = users_config.developer
            if isinstance(dev_ids, (int, str)):
                dev_ids = [dev_ids]
            
            self.bot.developers = []
            for dev_id in dev_ids:
                try:
                    user = await self.bot.fetch_user(int(dev_id))
                    self.bot.developers.append(user)
                except Exception as e:
                    logger.warning(f"Failed to fetch developer {dev_id}: {e}")
            
            if self.bot.developers:
                self.bot.developer = self.bot.developers[0]
            else:
                self.bot.developer = self.bot.user
                self.bot.developers = [self.bot.user]

            logger.system(f"Found {len(self.bot.developers)} Authorized Developers")

        except Exception as e:
            logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
    
    async def on_ready_startups(self):
        try:
            asyncio.create_task(giveaways.resume_active_giveaway(self.bot))
        except:
            pass
        logger.cog("Active Giveaways Resumed")
        try:
            asyncio.create_task(j2c_controller.resume_j2c_controllers(self.bot))
        except:
            pass
        logger.cog("J2C Controllers Resumed")

        

    async def activity(self):
        await self.bot.wait_until_ready()

        activities = [
            lambda: discord.Activity(type=discord.ActivityType.listening, name="/help"),
            lambda: discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.guilds)} servers"),
            lambda: discord.Activity(type=discord.ActivityType.watching, name=f"{sum(g.member_count for g in self.bot.guilds if g.member_count)} users"),
            lambda: discord.Activity(type=discord.ActivityType.watching, name=f"{len(self.bot.commands)} commands"),
            lambda: discord.Activity(type=discord.ActivityType.watching, name=getattr(self.bot.urls, "WEBSITE", "Website")),
        ]

        index = 0
        while not self.bot.is_closed():
            try:
                activity = activities[index % len(activities)]()
                await self.bot.change_presence(activity=activity)
                # logger.system(f"Presence Updated -> {activity.type.name} {activity.name}")
                index += 1
                await asyncio.sleep(60)

            except discord.ConnectionClosed:
                logger.warning("Discord connection closed. Waiting to reconnect...")
                await asyncio.sleep(10)

            except Exception as e:
                tb = traceback.extract_tb(sys.exc_info()[2])[-1]
                logger.error(f"Error in {__file__}, line {tb.lineno}: {e}")
                await asyncio.sleep(300) 



    async def send_shard_log(self, msg, embed_color=color.green):
        try:
            shards_log_webhook = self.bot.channels.shards_log_webhook
            if shards_log_webhook:
                embed = discord.Embed(description=f"{self.bot.emoji.SUCCESS if embed_color == color.green else self.bot.emoji.ERROR} | {msg}", color=embed_color)
                requests.post(shards_log_webhook, json={"embeds": [embed.to_dict()]},timeout=5)
            else:
                logger.warning(f"Could not send shard log: {msg}")
        except Exception as e:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.send_shard_log("Disconnected from Discord", embed_color=color.red)
        logger.warning("Disconnected from Discord")

    @commands.Cog.listener()
    async def on_resumed(self):
        await self.send_shard_log("Reconnected to Discord", embed_color=color.orange)
        logger.info("Reconnected to Discord")

    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        await self.send_shard_log(f"Shard {shard_id} is ready", embed_color=color.green)
        logger.info(f"Shard {shard_id} is ready")

    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        await self.send_shard_log(f"Shard {shard_id} is disconnected", embed_color=color.red)
        logger.warning(f"Shard {shard_id} is disconnected")

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        await self.send_shard_log(f"Shard {shard_id} is resumed", embed_color=color.orange)
        logger.info(f"Shard {shard_id} is resumed")
    
    # event when a cog is loaded
    @commands.Cog.listener()
    async def on_cog_load(self, cog):
        logger.info(f"Cog {cog.qualified_name} loaded")