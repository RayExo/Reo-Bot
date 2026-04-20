import os
import dotenv

dotenv.load_dotenv()


class BotConfigClass:
    TOKEN = os.getenv("TOKEN", "")
    PREFIX = os.getenv("PREFIX", "?")
    SHARD_COUNT = int(os.getenv("SHARD_COUNT", 2))
    NAME = os.getenv("BOT_NAME", "Reo")
    WEB_HOST = os.getenv("WEB_HOST", os.getenv("API_HOST", "0.0.0.0"))
    WEB_PORT = int(os.getenv("WEB_PORT", os.getenv("API_PORT", 25572)))
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
    DASHBOARD_SECRET = os.getenv("DASHBOARD_SECRET", "")
    DASHBOARD_BASE_URL = os.getenv("DASHBOARD_BASE_URL", f"http://localhost:{WEB_PORT}")
    API_HOST = WEB_HOST
    API_PORT = WEB_PORT


class urls:
    gif_api_base = "https://tenor.googleapis.com/v2/search"
    gif_api_key = "AIzaSyBx9qncGCjblFYGOfyqta6WUoYJTOtK5Co"


class channels:
    report_channel = 1464913496537042995
    guild_join_webhook = ""
    guild_leave_webhook = ""

    shards_log_webhook = ""


class users:
    developer = 870179991462236170, 767979794411028491, 1175647859614429240
    root = [870179991462236170, 767979794411028491, 1175647859614429240]


class Types:

    redeem_code_types = {
        "silver_guild_preminum": "Silver Guild Premium",
        "golden_guild_premium": "Golden Guild Premium",
        "diamond_guild_premium": "Diamond Guild Premium",
        "user_no_prefix": "User No Prefix",
    }


class storage:
    def __init__(self):
        self.uri = os.getenv("MONGO_URI", "mongodb+srv://CodeXmongodb:codexop@codexcluster.tebuglj.mongodb.net/?appName=CodeXCluster")
        self.name = os.getenv("MONGO_NAME", "reo")


class database(storage):
    pass
