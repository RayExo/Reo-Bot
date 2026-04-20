import discord
import asyncio
import datetime
import traceback
import sys

from reo.engine.Bot import AutoShardedBot

from reo.memory.cache import cache
import storage.auto_responder
import storage.guilds
import storage.media_channels
import storage.users
import storage.welcomer_settings
from reo.console.logging import logger
from reo.style import color

from reo.config.config import Types

redeem_code_types = Types.redeem_code_types

import storage
import json



async def change_user_subscription(bot:AutoShardedBot,user_id:int,subscription:str=None,valid_for_days:int=None):
    try:
        redeem_code_types = {
            "user_no_prefix": "User No Prefix"
        }
        if subscription:
            if subscription.lower() not in redeem_code_types.keys():
                return logger.error(f"Invalid Subscription Type: {subscription} for user_id: {user_id}")
        else:
            subscription = 'free'
            
        user_cache = cache.users.get(str(user_id),{})
        if not user_cache:
            await storage.users.insert(
                user_id=user_id
            )
            user_cache = cache.users.get(str(user_id),{})
        
        if subscription.lower() == 'user_no_prefix':
            if not valid_for_days:
                expires_at = ""
            else:
                no_prefix_end = user_cache.get('no_prefix_end')
                if no_prefix_end:
                    expires_at = no_prefix_end.astimezone() + datetime.timedelta(days=valid_for_days)
                else:
                    expires_at = datetime.datetime.now() + datetime.timedelta(days=valid_for_days)
                expires_at = expires_at.replace(tzinfo=None)

            try:
                await storage.users.update(
                    id=user_cache.get("id"),
                    user_id=user_id,
                    no_prefix=True,
                    no_prefix_subscription=True,
                    no_prefix_end=expires_at
                )
                logger.info(f"Updated User Subscription to User No Prefix for user_id: {user_id}")
                async def send_no_prefix_added_dm():
                    try:
                        user = await bot.fetch_user(user_id)
                        embed = discord.Embed(
                            title="No Prefix Subscription Added",
                            description=f"You Have Claimed No Prefix Subscription for {f'<t:{int(expires_at.timestamp())}:F>' if expires_at else 'Lifetime'}",
                            color=color.green
                        )
                        await user.send(embed=embed)
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                try:
                    asyncio.create_task(send_no_prefix_added_dm())
                except:
                    pass
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        elif subscription.lower() == 'free':
            try:
                await storage.users.update(
                    id=user_cache.get("id"),
                    user_id=user_id,
                    no_prefix=False,
                    no_prefix_subscription=False,
                    no_prefix_end=""
                )
                logger.info(f"Updated User Subscription to Free for user_id: {user_id}")
                async def send_no_prefix_removed_dm():
                    try:
                        user = await bot.fetch_user(user_id)
                        await user.send(embed=discord.Embed(description="Your No Prefix Subscription has been removed",color=color.red))
                    except Exception as e:
                        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
                try:
                    asyncio.create_task(send_no_prefix_removed_dm())
                except:
                    pass
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        else:
            logger.error(f"Invalid Subscription Type: {subscription} for user_id: {user_id}")
    except Exception as e:
        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

async def change_guild_subscription(bot:AutoShardedBot,guild_id:int,subscription:str=None,valid_for_days:int=None):
    try:
        if subscription:
            if subscription.lower() not in redeem_code_types.keys() and subscription.lower() not in ['free']:
                return logger.error(f"Invalid Subscription Type: {subscription} for guild_id: {guild_id}")
        else:
            subscription = 'free'
            
        guild_cache = cache.guilds.get(str(guild_id),{})
        if not guild_cache:
            await storage.guilds.insert(
                guild_id=guild_id
            )
            guild_cache = cache.guilds.get(str(guild_id),{})
        welcomer_cache = cache.welcomer_settings.get(str(guild_id),{})
        if not welcomer_cache:
            await storage.welcomer_settings.insert(
                guild_id=guild_id
            )
            welcomer_cache = cache.welcomer_settings.get(str(guild_id),{})

        if not valid_for_days:
            expires_at = ""
        else:
            subscription_end = guild_cache.get('subscription_end')
            if subscription_end:
                expires_at = subscription_end.astimezone() + datetime.timedelta(days=valid_for_days)
            else:
                expires_at = datetime.datetime.now() + datetime.timedelta(days=valid_for_days)
            expires_at = expires_at.replace(tzinfo=None)

        if subscription.lower() == 'silver_guild_preminum':
            try:
                await storage.guilds.update(
                    id=guild_cache.get("id"),
                    guild_id=guild_id,
                    subscription="silver_guild_preminum",
                    subscription_end=expires_at
                )
                logger.info(f"Updated Guild Subscription to Silver Guild Premium for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                await storage.welcomer_settings.update(
                    id=welcomer_cache.get("id"),
                    guild_id=guild_id,
                    autoroles_limit=5
                )
                logger.info(f"Updated Autoroles Limit to 5 for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            async def send_silver_guild_premium_dm():
                try:
                    guild = bot.get_guild(guild_id)
                    embed = discord.Embed(
                        title="Silver Guild Premium Subscription Added",
                        description=f"Guild **{guild.name}'s** Subscription has been updated to Silver Guild Premium for {f'<t:{int(expires_at.timestamp())}:F>' if expires_at else 'Lifetime'}",
                        color=color.green
                    )
                    await guild.owner.send(embed=embed)
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                asyncio.create_task(send_silver_guild_premium_dm())
            except:
                pass
            # change the bot's nickname to the name+ Prime
            try:
                guild = bot.get_guild(guild_id)
                await guild.me.edit(nick=f"{guild.me.display_name} Prime")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        elif subscription.lower() == 'golden_guild_premium':
            try:
                await storage.guilds.update(
                    id=guild_cache.get("id"),
                    guild_id=guild_id,
                    subscription="golden_guild_premium",
                    subscription_end=expires_at
                )
                logger.info(f"Updated Guild Subscription to Golden Guild Premium for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                await storage.welcomer_settings.update(
                    id=welcomer_cache.get("id"),
                    guild_id=guild_id,
                    autoroles_limit=10
                )
                logger.info(f"Updated Autoroles Limit to 10 for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            async def send_golden_guild_premium_dm():
                try:
                    guild = bot.get_guild(guild_id)
                    embed = discord.Embed(
                        title="Golden Guild Premium Subscription Added",
                        description=f"Guild **{guild.name}'s** Subscription has been updated to Golden Guild Premium for {f'<t:{int(expires_at.timestamp())}:F>' if expires_at else 'Lifetime'}",
                        color=color.green
                    )
                    await guild.owner.send(embed=embed)
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                asyncio.create_task(send_golden_guild_premium_dm())
            except:
                pass
            # change the bot's nickname to the name+ Prime
            try:
                guild = bot.get_guild(guild_id)
                await guild.me.edit(nick=f"{guild.me.display_name} Prime")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        elif subscription.lower() == 'diamond_guild_premium':
            try:
                await storage.guilds.update(
                    id=guild_cache.get("id"),
                    guild_id=guild_id,
                    subscription="diamond_guild_premium",
                    subscription_end=expires_at
                )
                logger.info(f"Updated Guild Subscription to Diamond Guild Premium for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                await storage.welcomer_settings.update(
                    id=welcomer_cache.get("id"),
                    guild_id=guild_id,
                    autoroles_limit=15
                )
                logger.info(f"Updated Autoroles Limit to 15 for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")
            async def send_diamond_guild_premium_dm():
                try:
                    guild = bot.get_guild(guild_id)
                    embed = discord.Embed(
                        title="Diamond Guild Premium Subscription Added",
                        description=f"Guild {guild.name} Has Claimed Diamond Guild Premium Subscription for {f'<t:{int(expires_at.timestamp())}:F>' if expires_at else 'Lifetime'}",
                        color=color.green
                    )
                    await guild.owner.send(embed=embed)
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                asyncio.create_task(send_diamond_guild_premium_dm())
            except:
                pass
            # change the bot's nickname to the name+ Prime
            try:
                guild = bot.get_guild(guild_id)
                await guild.me.edit(nick=f"{guild.me.display_name} Prime")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        elif subscription.lower() == 'free':
            try:
                await storage.guilds.update(
                    id=guild_cache.get("id"),
                    guild_id=guild_id,
                    subscription="free",
                    subscription_end=""
                )
                logger.info(f"Updated Guild Subscription to Free for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                # update autoroles limit to 3 if subscription is free
                cuted_autoroles = json.loads(welcomer_cache.get("autoroles", '[]'))[:3]
                greet_channels = json.loads(welcomer_cache.get("greet_channels", '[]'))[:5]
                await storage.welcomer_settings.update(
                    id=welcomer_cache.get("id"),
                    guild_id=guild_id,
                    autoroles_limit=3,
                    autoroles=json.dumps(cuted_autoroles),
                    autonick=False,
                    greet_channels=json.dumps(greet_channels)
                )
                logger.info(f"Updated Autoroles Limit to 1 for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")

            
            try:
                # delete limited media channels if any for the guild if subscription is free
                await storage.media_channels.delete_limited(limit=1,guild_id=guild_id)
                logger.info(f"Deleted Limited Media Channels for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")

            try:
                await storage.auto_responder.delete_limited(limit=5,guild_id=guild_id)
                logger.info(f"Deleted Limited Auto Responders for guild_id: {guild_id}")
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info())[0][1]}: {e}")

            async def send_free_dm():
                try:
                    guild = bot.get_guild(guild_id)
                    embed = discord.Embed(
                        title="Subscription Removed",
                        description=f"Your Guild **{guild.name}'s** Subscription has been removed",
                        color=color.green
                    )
                    await guild.owner.send(embed=embed)
                except Exception as e:
                    logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
            try:
                asyncio.create_task(send_free_dm())
            except:
                pass
            # change the bot's nickname to the name+ Prime
            try:
                guild = bot.get_guild(guild_id)
                await guild.me.edit(nick=None if guild.me.display_name.endswith(" Prime") else guild.me.display_name)
            except Exception as e:
                logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")
        else:
            logger.error(f"Invalid Subscription Type: {subscription} for guild_id: {guild_id}")
    except Exception as e:
        logger.error(f"Error in file {__file__} at line {traceback.extract_tb(sys.exc_info()[2])[0][1]}: {e}")

