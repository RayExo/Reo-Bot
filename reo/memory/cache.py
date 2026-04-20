from reo.config.config import users as users_config

class cache:
    guilds = {}
    guilds_log = {}
    users = {}
    j2c = {}
    j2c_settings = {}
    antinuke_settings = {}
    antinuke_bypass = {}
    welcomer_settings = {}
    redeem_codes = {}
    guilds_backup = {}
    afk = {
        "guilds": {},
        "global": {}
    }
    snipe_data = {
        "delete": {},
        "edit": {}
    }
    ignore_data = {
        "users": {},
        "channels": {}
    }
    ban_data = {
        "guilds": {},
        "users": {},
    }
    automod = {}

    custom_roles = {}
    custom_roles_permissions = {}

    media_channels = {}
    auto_responder = {}
    command_access = {}

    giveaways = {}
    giveaways_permissions = {}

    ticket_settings = {}
    tickets = {}
    shop = {}
    music = {}
    
    owners = []
    admins = []
    developer = users_config.developer
