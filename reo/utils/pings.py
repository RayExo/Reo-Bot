from time import time

import discord
import discord.http
import requests

from reo.memory.cache import cache as cache_module
from reo.bridge.storage import ping as ping_storage
from reo.engine.Bot import AutoShardedBot
from reo.console.logging import logger


async def storage() -> int:
    try:
        start_time = time()
        await ping_storage()
        return round(((time() - start_time) * 1000), 2)
    except Exception as error:
        logger.error(f"Storage ping failed: {error}")
        return -1


def bot(bot: AutoShardedBot) -> int:
    return round(bot.latency * 1000, 2)


def surface() -> float:
    start_time = time()
    try:
        requests.get(discord.http.Route.BASE)
        return round(((time() - start_time) * 1000), 2)
    except Exception:
        return -1


def cache() -> float:
    start_time = time()
    try:
        cache_module.guilds.get(str(1), str(1))
        return round(((time() - start_time) * 1000), 3)
    except Exception:
        return -1


def google() -> float:
    start_time = time()
    try:
        requests.get("https://www.google.com")
        return round(((time() - start_time) * 1000), 2)
    except Exception:
        return -1


def youtube() -> float:
    start_time = time()
    try:
        requests.get("https://www.youtube.com")
        return round(((time() - start_time) * 1000), 2)
    except Exception:
        return -1


def github() -> float:
    start_time = time()
    try:
        requests.get("https://www.github.com")
        return round(((time() - start_time) * 1000), 2)
    except Exception:
        return -1


def shard(bot: AutoShardedBot, shard_id: int) -> int:
    shard_info = bot.get_shard(shard_id)
    return round(shard_info.latency * 1000, 2)


def shards(bot: AutoShardedBot) -> dict:
    for shard_id in bot.shards:
        shard = bot.get_shard(shard_id)
        latency = shard.latency
    return {str(shard[0]): round(shard[1] * 1000, 2) for shard in bot.latencies}


database = storage
