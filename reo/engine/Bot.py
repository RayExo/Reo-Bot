import discord
from discord.ext import commands
import inspect
import datetime

from reo.config import config
BotConfig = config.BotConfigClass()

from reo.memory.cache import cache

from reo.style import color
from reo.console.logging import logger

from storage import guilds_log as guilds_log_db
import storage
from reo.style import emoji,urls
import importlib
import asyncio
import wavelink
from collections import defaultdict
import time
import traceback

def get_function_args(func):
    signature = inspect.signature(func)
    return [param.name for param in signature.parameters.values()]



class Log:
    def __init__(self, bot):
        self.bot = bot
        self.log_error_type = [type for type in get_function_args(guilds_log_db.get) if type not in ['guild_id', 'id', 'enabled', 'updated_at', 'created_at']]
        
        # Initialize timeout_data to track the number of logs sent per guild and their log queues
        self.timeout_data = defaultdict(lambda: {"count": 0, "last_log_time": 0, "queue": None})
    
    async def send(self, guild: discord.Guild, type: str, embed: discord.Embed = None, content: str = None):
        type = type.lower() + "_channel_id"
        guilds_log_cache = cache.guilds_log.get(str(guild.id))
        
        if not guilds_log_cache or not guilds_log_cache.get('enabled'):
            return
        
        if type not in self.log_error_type:
            return
        
        channel_id = guilds_log_cache.get(type)
        if not channel_id:
            return
        
        channel = guild.get_channel(int(channel_id))
        if not channel:
            return
        
        if not embed and not content:
            return
        
        if not embed:
            embed = discord.Embed(
                title="Error",
                description=content,
                color=color.red
            )
        
        # Initialize the queue for the guild if it doesn't exist
        guild_data = self.timeout_data[guild.id]
        if guild_data["queue"] is None:
            guild_data["queue"] = asyncio.Queue()
            asyncio.create_task(self.process_queue(guild))  # Start a background task to process the queue
        
        # Add both the channel and the embed (log entry) to the queue
        await guild_data["queue"].put((channel, embed))
    
    async def process_queue(self, guild: discord.Guild):
        guild_data = self.timeout_data[guild.id]
        queue = guild_data["queue"]
        
        while True:
            # Fetch the next (channel, embed) tuple from the queue
            channel, embed = await queue.get()
            
            current_time = time.time()
            
            # Reset count if more than 60 seconds have passed since the last log
            if current_time - guild_data["last_log_time"] > 60:
                guild_data["count"] = 0
            
            # If more than 5 logs have been sent within 60 seconds, introduce a 5-second delay
            if guild_data["count"] >= 20:
                await asyncio.sleep(5)
            
            # Try to send the log
            try:
                await channel.send(embed=embed)
                guild_data["count"] += 1
                guild_data["last_log_time"] = current_time
            except Exception as e:
                logger.error(f"Error in Log.process_queue: {e}")
            
            # Mark the task as done
            queue.task_done()
    
    async def wait_for_all_queues(self):
        # Wait until all queues are empty before proceeding (useful for shutdowns or graceful exits)
        tasks = []
        for guild_id, guild_data in self.timeout_data.items():
            if guild_data["queue"] is not None:
                tasks.append(guild_data["queue"].join())
        await asyncio.gather(*tasks)


        
class antinuke_log:
    def __init__(self, bot):
        self.bot = bot
        self.log_error_type = [type for type in get_function_args(guilds_log_db.get) if type not in ['guild_id','id','enabled','updated_at','created_at']]
    
    async def send(self,guild:discord.Guild,type:str,embed:discord.Embed=None,content:str=None):
        type = type.lower()+ "_channel_id"
        guilds_log_cache = cache.guilds_log[str(guild.id)]
        if not guilds_log_cache.get('enabled'):
            return
        
        if type not in self.log_error_type:
            return
        

        channel_id = guilds_log_cache.get(type)

        if not channel_id:
            return
        
        channel = guild.get_channel(int(channel_id))
        if not channel:
            return

        if not embed and not content:
            return
        if not embed:
            embed = discord.Embed(
                title="Error",
                description=content,
                color=color.red
            )
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Error in Log.error: {e}")

class EmojiManager:
    def __init__(self, default_emoji="x"):
        self.default_emoji = default_emoji

    def __getattr__(self, item):
        # Check if the emoji exists as a variable in the emoji module
        return getattr(emoji, item, self.default_emoji)

class AutoShardedBot(commands.AutoShardedBot):
    def __init__(self, *arg, **kwargs):
        super().__init__(command_prefix=self.get_prefix,
                        case_insensitive=True,
                        intents=discord.Intents.all(),
                        status=discord.Status.dnd,
                        strip_after_prefix=True,
                        sync_commands_debug=True,
                        sync_commands=True,
                        help_command=None,
                        shard_count=BotConfig.SHARD_COUNT,
                        allowed_mentions=discord.AllowedMentions(everyone=False,replied_user=False,roles=False)
                        )
        self.developer:discord.User = self.user
        self.developers: list[discord.User] = []

        self.log = Log(self)
        self.users_data = config.users
        self.emoji = emoji # EmojiManager()
        self.cache = cache
        self.BotConfig = BotConfig
        self.channels = config.channels
        self.storage = storage
        self.database = self.storage
        self.antinuke_log = antinuke_log(self)
        self.urls = urls
        self.variables = {
                        "{user}": "The user's name",
                        "{user.id}": "The user's id",
                        "{user.tag}": "The user's tag",
                        "{user.mention}": "The user's mention",
                        "{user.avatar}": "The user's avatar",
                        "{user.created_at}": "The user's account creation date",
                        "{user.joined_at}": "The user's join date",
                        "{guild}": "The server name",
                        "{server}": "The server name",
                        "{server.id}": "The server id",
                        "{server.icon}": "The server icon",
                        "{guild.id}": "The server id",
                        "{guild.icon}": "The server icon",
                        "{guild.owner}": "The server owner",
                        "{guild.owner.id}": "The server owner id",
                        "{time}": "The current time",
                        "{member.count}": "The server member count"
                    }
        self.VERSION = '1.0.0'
        self.start_time = datetime.datetime.now(tz=datetime.timezone.utc)
        self.add_check(self._check_command_access)


    async def _check_command_access(self, ctx: commands.Context) -> bool:
        if not ctx.guild or not ctx.command:
            return True
        from reo.src.checks.checks import check_is_admin_predicate, check_is_owner_raw
        if check_is_admin_predicate(ctx.author):
            return True
        if await check_is_owner_raw(ctx.author, ctx.guild):
            return True

        command_access = cache.command_access.get(str(ctx.guild.id), {})
        disabled_commands = set(command_access.get("disabled_commands", []) or [])
        qualified_name = getattr(ctx.command, "qualified_name", ctx.command.name)
        parts = qualified_name.split()
        command_chain = [" ".join(parts[:index]) for index in range(1, len(parts) + 1)]
        if any(name in disabled_commands for name in command_chain):
            raise commands.CheckFailure("This command is disabled in this server.")
        return True

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        # Ignore common errors that don't need logging
        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure, commands.CommandOnCooldown, commands.MissingRequiredArgument)):
            return

        # Log to console
        logger.error(f"Command Error: {ctx.command} - {ctx.author}: {error}")
        
        # Send to report channel
        channel = self.get_channel(self.channels.report_channel)
        if channel:
            try:
                embed = discord.Embed(
                    title="Command Error",
                    description=f"An error occurred while executing the command: `{ctx.command}`",
                    color=color.red,
                    timestamp=datetime.datetime.now(tz=datetime.timezone.utc)
                )
                embed.add_field(name="Command", value=f"`{ctx.command}`", inline=True)
                embed.add_field(name="User", value=f"{ctx.author}\n({ctx.author.id})", inline=True)
                embed.add_field(name="Guild", value=f"{ctx.guild.name}\n({ctx.guild.id})" if ctx.guild else "DMs", inline=True)
                
                # Traceback formatting
                tb = "".join(traceback.format_exception(type(error), error, error.__traceback__))
                if len(tb) > 950:
                    tb = tb[:950] + "\n... [Truncated]"
                
                embed.add_field(name="Traceback", value=f"```py\n{tb}\n```", inline=False)
                embed.set_footer(text=f"Shard {ctx.guild.shard_id}" if ctx.guild else "No Shard")
                
                await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Failed to send command error to Discord: {e}")

    async def on_error(self, event_method, *args, **kwargs):
        # Log to console
        logger.error(f"Event Error in {event_method}: {traceback.format_exc()}")
        
        # Send to report channel
        channel = self.get_channel(self.channels.report_channel)
        if channel:
            try:
                embed = discord.Embed(
                    title="Event Error",
                    description=f"An error occurred in event: `{event_method}`",
                    color=color.red,
                    timestamp=datetime.datetime.now(tz=datetime.timezone.utc)
                )
                embed.add_field(name="Event Method", value=f"`{event_method}`", inline=False)
                
                tb = traceback.format_exc()
                if len(tb) > 950:
                    tb = tb[:950] + "\n... [Truncated]"
                
                embed.add_field(name="Traceback", value=f"```py\n{tb}\n```", inline=False)
                
                await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Failed to send event error to Discord: {e}")
    


    
    async def reload(self):
        importlib.reload(config)
        importlib.reload(emoji)
        importlib.reload(urls)
        importlib.reload(storage)
        self.users_data = config.users
        self.channels = config.channels
        self.BotConfig = config.BotConfigClass()
        self.urls = urls
        self.emoji = EmojiManager()
        self.storage = storage
        self.database = self.storage



    
    async def get_prefix(self, message: discord.Message):
            default_prefix = str(BotConfig.PREFIX)
            if message.guild:
                guild_id = str(message.guild.id)                
                if cache.users.get(str(message.author.id),{}).get('no_prefix',False) == True and cache.users.get(str(message.author.id),{}).get('no_prefix_subscription',False) == True:
                    if guild_id in cache.guilds:
                        guild_cache = cache.guilds[guild_id]
                        prefix = guild_cache.get('prefix', default_prefix)
                        return commands.when_mentioned_or(prefix, '')(self, message)
                    else:
                        return commands.when_mentioned_or(default_prefix, '')(self, message)
                else:
                    if guild_id in cache.guilds:
                        guild_cache = cache.guilds[guild_id]
                        prefix = guild_cache.get('prefix', default_prefix)
                        return commands.when_mentioned_or(prefix)(self, message)
                    else:
                        return commands.when_mentioned_or(default_prefix)(self, message)
            else:
                return commands.when_mentioned_or(default_prefix)(self, message)
