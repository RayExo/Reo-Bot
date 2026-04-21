import asyncio
import traceback

import discord
import discord.http
import uvicorn

from reo.engine.Bot import AutoShardedBot
from reo.console.logging import logger
from reo.config.config import BotConfigClass

BotConfig = BotConfigClass()
bot = AutoShardedBot()


async def main():
    try:
        from reo.workflows.bootstrap import prepare_runtime
        from reo.surface import server as surface_server
        from reo.style.sync_emojis import run_sync

        await prepare_runtime()
        surface_server.bind_bot(bot)
        logger.separator()
        
        # Fast Emoji Synchronization
        if BotConfig.SYNC_EMOJIS:
            run_sync()
        else:
            logger.info("EmojiSync is currently disabled via config.")
        logger.separator()
        
        await bot.load_extension("reo.src")

        tasks = []

        async def start_bot():
            try:
                await bot.start(BotConfig.TOKEN, reconnect=True)
            except KeyboardInterrupt:
                logger.error("Bot has been stopped")
            except discord.RateLimited as error:
                logger.error(f"Bot is rate limited. Retrying in {error.retry_after} seconds")
            except discord.LoginFailure as error:
                logger.error(f"Login failed. {error}")
            except discord.HTTPException as error:
                retry_after = error.response.headers.get("Retry-After", "N/A")
                logger.error(f"Bot is rate limited. Retrying in {retry_after} seconds")
                if retry_after == "N/A":
                    return
                logger.error(f"Rate limit details: {error.response.status} {error.response.reason}")
                logger.error(f"Response headers: {error.response.headers}")
                logger.error(f"Response text: {error.status} {error.text}")
                await asyncio.sleep(int(retry_after))

        async def start_web():
            try:
                import logging
                class EndpointFilter(logging.Filter):
                    def filter(self, record: logging.LogRecord) -> bool:
                        return "/live" not in record.getMessage()
                
                logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
                
                web_config = uvicorn.Config(
                    surface_server.app,
                    host=BotConfig.WEB_HOST,
                    port=BotConfig.WEB_PORT,
                )
                server = uvicorn.Server(web_config)
                await server.serve()
            except Exception:
                logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

        if BotConfig.DASHBOARD_ENABLED:
            try:
                tasks.append(asyncio.create_task(start_web()))
            except Exception:
                logger.error(f"Error in file {__file__}: {traceback.format_exc()}")
        else:
            logger.info("\033[1;31mDashboard is disabled via config.\033[0m")
        try:
            tasks.append(asyncio.create_task(start_bot()))
        except Exception:
            logger.error(f"Error in file {__file__}: {traceback.format_exc()}")

        await asyncio.gather(*tasks)
    except Exception:
        logger.error(f"Error in file {__file__}: {traceback.format_exc()}")


if __name__ == "__main__":
    asyncio.run(main())
