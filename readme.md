# REO

Reo is a modern, multipurpose Discord bot featuring a seamless web dashboard, comprehensive server security, advanced music playback, and automated community management tools.

## Showcase

### Overview

![REO Overview](https://media.discordapp.net/attachments/1491710555587874846/1495749350511476926/reo1.png?ex=69e760a2&is=69e60f22&hm=f48dcad7762fd1059338292eebb5022ce1b0209cf82d1160e1b0c3aa840b38cc&=&format=webp&quality=lossless&width=1573&height=884)

### Music

![REO Music](https://media.discordapp.net/attachments/1491710555587874846/1495749589700186202/image.png?ex=69e760db&is=69e60f5b&hm=0533ad53b73cebddd94d9345304b6579eaed54413f12ff9700355a7f573882f0&=&format=webp&quality=lossless&width=1573&height=884)


### Bot UI

![REO Help Command UI](https://media.discordapp.net/attachments/1491710555587874846/1495750041191841913/image.png?ex=69e76147&is=69e60fc7&hm=a7dee9c78d710f873a827796b27ffb286ebf0eb4e3921659900c7db455456972&=&format=webp&quality=lossless&width=724&height=933)

![REO Music Command UI](https://media.discordapp.net/attachments/1491710555587874846/1495750051836858548/image.png?ex=69e7614a&is=69e60fca&hm=bb4f986480a22cd1e2dfff28c58a4b1c5ef2df155f6841ea9c82a0ccf44e8bbf&=&format=webp&quality=lossless&width=823&height=603)


## Features

- Discord bot with hybrid commands
- MongoDB Database
- FastAPI dashboard
- Music controller with live artwork, queue, and activity
- Security and automod controls
- Tickets, giveaways, welcomer, and command management
- English and Hindi help menu support

## Stack

- Python
- `discord.py`
- `wavelink`
- FastAPI
- MongoDB

## Project Layout

- `main.py` - bot entry point
- `reo/src` - commands, events, and runtime modules
- `reo/surface` - dashboard and web routes
- `reo/engine` - bot core
- `storage` - Mongo-backed storage layer
- `.env` - local environment config

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create environment file

Create `.env`:

```env
TOKEN=""

PREFIX=""

SHARD_COUNT=""

BOT_NAME="Reo"

# Web / API Hosting
WEB_HOST="0.0.0.0"
WEB_PORT="25572"


# Automation Features
SYNC_EMOJIS="False"

# OAuth2 / Dashboard Configuration
DISCORD_CLIENT_ID=""
DISCORD_CLIENT_SECRET=""
DASHBOARD_SECRET=""
DASHBOARD_BASE_URL="http://localhost:25572"

# MongoDB Database Configuration
MONGO_URI=""
```

### 3. Discord application setup

In the Discord Developer Portal:

- copy your `Application ID` into `DISCORD_CLIENT_ID`
- copy your `Client Secret` into `DISCORD_CLIENT_SECRET`
- add this redirect URL:

```text
http://localhost:25572/dashboard/auth/callback
```

If you use a custom domain, replace the localhost URL with your real dashboard domain in both the portal and `DASHBOARD_BASE_URL`.

### 4. Start the bot

```bash
python main.py
```

### 5. Open the dashboard

```text
http://localhost:25572/dashboard
```

Login with Discord, choose a server you manage, and configure it from the dashboard.

## Dashboard Areas

- Overview
- Security
- Moderation
- Music
- Commands
- Logs
- Giveaways
- Tickets
- Welcomer

## Notes

- Only guild owners, administrators, or members with manage server access can manage a server in the dashboard.
- The music page updates live while the bot is running.
- The server language setting affects the help menu output.

## License

MIT License

Copyright (c) 2026 Codex Development
