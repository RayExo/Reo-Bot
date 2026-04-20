import discord
import asyncio
import datetime

from reo.engine.Bot import AutoShardedBot
import storage.afk
from reo.console.logging import logger

from reo.memory.cache import cache

from reo.workflows.actions import change_guild_subscription, change_user_subscription
from reo.workflows.afk_delay import afk_delay

import json

import storage
check_guilds_subscription_running = False
async def check_guilds_subscription(bot: AutoShardedBot):
    global check_guilds_subscription_running
    if check_guilds_subscription_running:
        return logger.warning("Subscription check is already running")
    check_guilds_subscription_running = True
    while not bot.is_ready():
        await asyncio.sleep(1)
    # logger.info("Checking Subscriptions")
    while True:
        for guild_id,data in cache.guilds.items():
            if data.get('subscription') == 'free':
                continue
            if not data.get('subscription_end'):
                logger.warning(f"Infinite subscription found for guild {guild_id}")
                continue
            
            # if subscription has less than 3 days left notify the owner
            if data.get('subscription_end',datetime.datetime.now()).astimezone() < datetime.datetime.now().astimezone() + datetime.timedelta(days=3) and data.get('subscription_end',datetime.datetime.now()).astimezone() > datetime.datetime.now().astimezone():
                logger.info(f"Subscription ending soon for guild {guild_id}")
                try:
                    guild = await bot.fetch_guild(int(guild_id))
                    if guild:
                        guild_cache = cache.guilds.get(str(guild.id))
                        owners = [guild.owner]
                        for extra_owner_id in json.loads(guild_cache.get('extra_owner_ids','[]')):
                            owner = await bot.fetch_user(extra_owner_id)
                            if owner:
                                owners.append(owner)
                        for owner in owners:
                            try:
                                await owner.send(f"Your subscription for {guild.name} is ending in less than 3 days, please renew it.")
                            except:
                                logger.error(f"Error sending message to owner of guild {guild_id} - {owner.id}")
                    else:
                        logger.error(f"Guild {guild_id} not found")
                except Exception as e:
                    logger.warning(f"Error sending message to owner of guild {guild_id}: {e}")

            if data.get('subscription_end',datetime.datetime.now()).astimezone() > datetime.datetime.now().astimezone():
                logger.info(f"Subscription has not ended for guild {guild_id}")
                continue
            
            logger.warning(f"Subscription ended for guild {guild_id}")

            await change_guild_subscription(
                bot=bot,
                guild_id=int(guild_id),
                subscription='free',
                valid_for_days=None
            )
        await asyncio.sleep(12*60*60)

check_users_subscription_running = False
async def check_users_subscription(bot: AutoShardedBot):
    global check_users_subscription_running
    if check_users_subscription_running:
        return logger.warning("Subscription check is already running")
    check_users_subscription_running = True
    while not bot.is_ready():
        await asyncio.sleep(1)
    # logger.info("Checking Subscriptions")
    while True:
        for user_id,data in cache.users.items():
            if data.get('subscription') == 'free':
                continue
            if not data.get('no_prefix_subscription'):
                continue
                
            if not data.get('no_prefix_end'):
                logger.warning(f"Infinite subscription found for user {user_id}")
                continue
            
            # if subscription has less than 3 days left notify the owner
            if data.get('no_prefix_end',datetime.datetime.now()).astimezone() < datetime.datetime.now().astimezone() + datetime.timedelta(days=3):
                logger.info(f"Subscription ending soon for user {user_id}")
                try:
                    user = bot.get_user(int(user_id))
                    if user:
                        await user.send(f"Your subscription is ending soon, please renew it.")
                    else:
                        logger.error(f"User {user_id} not found")
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")

            if data.get('no_prefix_end',datetime.datetime.now()).astimezone() > datetime.datetime.now().astimezone():
                logger.info(f"Subscription has not ended for user {user_id}")
                continue
            
            logger.info(f"Subscription ended for user {user_id}")

            await change_user_subscription(
                bot=bot,
                user_id=int(user_id),
                subscription=None,
                valid_for_days=None
            )
        
        # 12 hours
        await asyncio.sleep(12*60*60)

restart_afk_functions_running = False
async def resume_afk_functions(bot: AutoShardedBot):
    global restart_afk_functions_running
    if restart_afk_functions_running:
        return logger.warning("AFK functions are already running")
    restart_afk_functions_running = True
    while not bot.is_ready():
        await asyncio.sleep(1)
    all_afk_data = await storage.afk.get_all()
    for afk_data in all_afk_data:
        asyncio.create_task(afk_delay(bot=bot, data=afk_data))