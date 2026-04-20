from reo.memory.cache import cache
from reo.console.logging import logger
from reo.src.modules import j2c_controller

import asyncio
from storage import j2c as j2c_db


resume_j2c_controllers_running = False
async def resume_j2c_controllers(bot):
    global resume_j2c_controllers_running
    if resume_j2c_controllers_running:
        return logger.info("Already running resume_j2c_controllers")
    resume_j2c_controllers_running = True
    while not bot.is_ready():
        await asyncio.sleep(1)

    async def create_j2c_message(data):
        channel = bot.get_channel(int(channel_id))
        if not channel:
            await j2c_db.delete(id=data.get("id"))
            return
        if len(channel.members) == 0:
            await channel.delete()
            logger.info(f"Deleted J2C Channel {channel.name}")
            await j2c_db.delete(id=data.get("id"))
            logger.info(f"Deleted J2C Data {data.get('id')}")
            return
        await j2c_controller.controller_module(bot,data,channel=channel)
        logger.info(f"Resumed J2C Controller for {channel.name}")
        
    tasks = []
    for channel_id,data in cache.j2c.items():
        try:
            tasks.append(create_j2c_message(data))
        except Exception as e:
            logger.error(e)
            continue

    await asyncio.gather(*tasks)
