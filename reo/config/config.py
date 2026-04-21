import os
import dotenv

dotenv.load_dotenv()


class BotConfigClass:
    TOKEN = os.getenv("TOKEN", "")
    PREFIX = os.getenv("PREFIX", "?")
    SHARD_COUNT = int(os.getenv("SHARD_COUNT", 2))
    NAME = os.getenv("BOT_NAME", "Reo")
    DASHBOARD_ENABLED = os.getenv("DASHBOARD_ENABLED", "True").lower() == "true"
    WEB_HOST = os.getenv("WEB_HOST", "0.0.0.0")
    WEB_PORT = int(os.getenv("WEB_PORT", 25572))
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
    DASHBOARD_SECRET = os.getenv("DASHBOARD_SECRET", "")
    DASHBOARD_BASE_URL = os.getenv("DASHBOARD_BASE_URL", f"http://localhost:{WEB_PORT}")
    API_HOST = WEB_HOST
    API_PORT = WEB_PORT
    SYNC_EMOJIS = os.getenv("SYNC_EMOJIS", "True").lower() == "true"


class urls:
    gif_api_base = "https://tenor.googleapis.com/v2/search"
    gif_api_key = "AIzaSyBx9qncGCjblFYGOfyqta6WUoYJTOtK5Co"


class channels:
    report_channel = int(os.getenv("REPORT_CHANNEL"))
    guild_join_webhook = os.getenv("GUILD_JOIN_WEBHOOK", "")
    guild_leave_webhook = os.getenv("GUILD_LEAVE_WEBHOOK", "")
    shards_log_webhook = os.getenv("SHARDS_LOG_WEBHOOK", "")


_dev_env = os.getenv("DEVELOPER_IDS", "870179991462236170, 767979794411028491")
_dev_parsed = [int(u.strip()) for u in _dev_env.split(",") if u.strip().isdigit()]

class users:
    developer = tuple(_dev_parsed)
    root = list(_dev_parsed)


class Types:

    redeem_code_types = {
        "silver_guild_preminum": "Silver Guild Premium",
        "golden_guild_premium": "Golden Guild Premium",
        "diamond_guild_premium": "Diamond Guild Premium",
        "user_no_prefix": "User No Prefix",
    }


class storage:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI", "")
        self.name = os.getenv("MONGO_NAME", "reo")


class database(storage):
    pass
