import discord
import chat_exporter
from discord.ext import commands

from io import BytesIO

from reo.console.logging import logger

import traceback

async def export_chat(bot,guild,channel):
    try:
        messages = await chat_exporter.export(
            channel=channel,
            limit=1000,
            guild=guild,
            bot=bot
        )
        bytes = BytesIO(messages.encode())
        bytes.seek(0)
        return bytes
    except Exception as e:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        return False