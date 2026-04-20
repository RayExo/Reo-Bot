from discord.ext import commands
import wavelink
import traceback, sys
import datetime

from reo.console.logging import logger
from reo.config.config import users as users_config

from reo.engine.Bot import AutoShardedBot
import asyncio
import requests
from reo.style import color

import discord

from reo.src.startup import giveaways
from reo.src.startup import j2c_controller
class Wavelink(commands.Cog):
    def __init__(self, bot):
        self.bot:AutoShardedBot = bot
        self._controller_refresh_times: dict[int, datetime.datetime] = {}
        self._controller_refresh_tasks: dict[int, asyncio.Task] = {}

    def _stop_controller_refresh_task(self, guild_id: int) -> None:
        task = self._controller_refresh_tasks.pop(guild_id, None)
        if task and not task.done():
            task.cancel()

    def _ensure_controller_refresh_task(self, guild_id: int) -> None:
        existing = self._controller_refresh_tasks.get(guild_id)
        if existing and not existing.done():
            return
        self._controller_refresh_tasks[guild_id] = asyncio.create_task(
            self._controller_refresh_loop(guild_id)
        )

    async def _controller_refresh_loop(self, guild_id: int) -> None:
        try:
            while True:
                await asyncio.sleep(5)
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    break
                player = guild.voice_client
                if not player or not getattr(player, "current", None):
                    break
                music_cog = self.bot.get_cog("Music")
                if not music_cog:
                    break
                self._controller_refresh_times[guild_id] = datetime.datetime.now(datetime.timezone.utc)
                await music_cog.send_music_controls(guild=guild, update_attachments=True)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.error(f"Error in controller refresh loop: {traceback.format_exc()}")
        finally:
            self._controller_refresh_tasks.pop(guild_id, None)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        logger.warning(f"Node {payload.node.uri} is ready!")

    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, node: wavelink.Node, disconnected: list[wavelink.Player]):
        logger.warning(f"Node {node.uri} has been closed and cleaned-up. Disconnected players: {len(disconnected)}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        guild = getattr(payload.player, "guild", None)
        if guild:
            self._ensure_controller_refresh_task(guild.id)
            logger.warning(f"Track {payload.track} has started playing on player {guild.name}")

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload: wavelink.TrackExceptionEventPayload):
        logger.error(f"An exception occurred while playing track {payload.track} on player {payload.player.guild.name}: {payload.exception}")

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload: wavelink.TrackStuckEventPayload):
        logger.error(f"Track {payload.track} got stuck on player {payload.player.guild.name}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        try:
            logger.info(f"Track end event received for track: {payload.track.title if payload.track else 'Unknown'}")

            player = payload.player
            guild = getattr(player, "guild", None)
            if not player or not guild:
                return
            self._stop_controller_refresh_task(guild.id)
            
            MusicCog = self.bot.get_cog("Music")
            if not MusicCog:
                return logger.error("Music Cog not found in track end handler.")

            if player.autoplay != wavelink.AutoPlayMode.disabled:
                for i in range(5):
                    if player.current:
                        break
                    await asyncio.sleep(1)
                if guild.voice_client:
                    return await MusicCog.send_music_controls(guild=guild, update_attachments=True)
                return

            # Check if the queue is empty
            if player.queue.is_empty and not player.queue.mode == wavelink.QueueMode.loop:
                # If the queue is empty but the player is still playing, log it
                if player.current:
                    logger.info(f"Queue is empty, but the player is still playing {player.current.title}")
                    return
                
                # Disconnect if there's nothing left to play
                await player.disconnect()
                logger.info(f"Queue is empty. Disconnected from {guild.name}.")
                await MusicCog.send_music_controls(guild=guild, end=True)
            else:
                try:
                    next_track = player.queue.get()
                except wavelink.exceptions.QueueEmpty:
                    await player.disconnect()
                    await MusicCog.send_music_controls(guild=guild, end=True)
                    return
                await player.play(next_track)
                logger.info(f"Playing next track: {next_track.title}")
                await MusicCog.send_music_controls(guild=guild, update_attachments=True)
        except Exception as e:
            logger.error(f"Error in track end handler: {traceback.format_exc()}")
    
    @commands.Cog.listener()
    async def on_wavelink_stats_update(self, payload: wavelink.StatsEventPayload):
        # logger.warning(f"WaveLink Stats updated: {payload.players} players total ({payload.playing} playing)")
        pass




    @commands.Cog.listener()
    async def on_wavelink_player_update(self, payload: wavelink.PlayerUpdateEventPayload):
        try:
            player = payload.player
            guild = getattr(player, "guild", None)
            if not player or not guild or not guild.voice_client or not player.current:
                return

            self._ensure_controller_refresh_task(guild.id)

            now = datetime.datetime.now(datetime.timezone.utc)
            last_refresh = self._controller_refresh_times.get(guild.id)
            if last_refresh and (now - last_refresh).total_seconds() < 5:
                return

            MusicCog = self.bot.get_cog("Music")
            if not MusicCog:
                return

            self._controller_refresh_times[guild.id] = now
            await MusicCog.send_music_controls(guild=guild, update_attachments=True)
        except Exception:
            logger.error(f"Error in player update handler: {traceback.format_exc()}")

    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        guild = getattr(player, "guild", None)
        if guild:
            self._stop_controller_refresh_task(guild.id)
        await player.channel.send(f"The player has been inactive for `{player.inactive_timeout}` seconds. Goodbye!")
        # await player.disconnect()
