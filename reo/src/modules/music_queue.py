import discord
import wavelink

from reo.console.logging import logger


async def handle_queue(player: wavelink.Player, cog_instance, guild: discord.Guild):
        if player.queue.is_empty:
            await player.disconnect()
            await cog_instance.MusicCog.send_music_controls(guild=guild, end=True)
            logger.info(f"Queue is empty. Disconnected from {guild.name}.")
        else:
            next_track = player.queue.get()
            await player.play(next_track)
            await cog_instance.MusicCog.send_music_controls(guild=guild, update_attachments=True)
            logger.info(f"Playing next track: {next_track.title}")