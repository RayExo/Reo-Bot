from __future__ import annotations

import html
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode

import httpx
import storage
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from reo.config.config import BotConfigClass
from reo.memory.cache import cache
from reo.style import urls as style_urls
from reo.surface.runtime import (
    bind_bot,
    consume_oauth_state,
    create_oauth_state,
    create_session,
    destroy_session,
    get_bot,
    get_session,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
BOT_CONFIG = BotConfigClass()
SESSION_COOKIE = "reo_surface_session"
DISCORD_API = "https://discord.com/api/v10"
ADMINISTRATOR = 0x8
MANAGE_GUILD = 0x20
LOGS_DIR = Path(__file__).resolve().parents[3] / "logs"


def _escape(value: Any) -> str:
    return html.escape(str(value or ""))


def _clean_text(value: Any) -> str:
    text = str(value or "")
    try:
        repaired = text.encode("latin1").decode("utf-8")
        weird_before = sum(text.count(token) for token in ("Ã", "â", "Å", "œ", "€"))
        weird_after = sum(repaired.count(token) for token in ("Ã", "â", "Å", "œ", "€"))
        if weird_after < weird_before:
            text = repaired
    except Exception:
        pass
    replacements = {
        "•": "-",
        "â€¢": "-",
        "✅": "[ok]",
        "âœ…": "[ok]",
        "✅": "...",
        "Ã¢ÂÅ’": "[x]",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return " ".join(text.split())


def _format_ms(ms: int | float | None) -> str:
    total_seconds = max(0, int((ms or 0) / 1000))
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _guild_icon(guild) -> str:
    if getattr(guild, "icon", None):
        return guild.icon.url
    return "https://cdn.discordapp.com/embed/avatars/0.png"


def _bool_from_form(data: dict[str, str], key: str) -> bool:
    return data.get(key) == "on"


async def _parse_form(request: Request) -> dict[str, str]:
    body = await request.body()
    parsed = parse_qs(body.decode("utf-8"), keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items()}


def _session_from_request(request: Request) -> dict[str, Any] | None:
    return get_session(request.cookies.get(SESSION_COOKIE))


def _dashboard_callback_url() -> str:
    return f"{BOT_CONFIG.DASHBOARD_BASE_URL.rstrip('/')}/dashboard/auth/callback"


def _can_manage_guild(raw_guild: dict[str, Any]) -> bool:
    permissions = int(raw_guild.get("permissions", 0) or 0)
    return bool(raw_guild.get("owner")) or bool(permissions & ADMINISTRATOR) or bool(
        permissions & MANAGE_GUILD
    )


def _manageable_guilds(session: dict[str, Any]) -> list[dict[str, Any]]:
    bot = get_bot()
    if not bot:
        return []
    bot_guild_map = {str(guild.id): guild for guild in bot.guilds}
    items = []
    for raw_guild in session.get("guilds", []):
        if not _can_manage_guild(raw_guild):
            continue
        guild = bot_guild_map.get(str(raw_guild.get("id")))
        if not guild:
            continue
        items.append(
            {
                "id": str(guild.id),
                "name": guild.name,
                "icon": _guild_icon(guild),
                "members": guild.member_count or 0,
                "channels": len(guild.channels),
                "roles": len(guild.roles),
                "owner_id": guild.owner_id,
            }
        )
    return sorted(items, key=lambda item: item["name"].lower())


def _get_accessible_guild(session: dict[str, Any], guild_id: int):
    for guild in _manageable_guilds(session):
        if guild["id"] == str(guild_id):
            bot = get_bot()
            return guild, bot.get_guild(guild_id) if bot else None
    return None, None


async def _ensure_guild_records(guild_id: int, bot_guild) -> dict[str, Any]:
    guild_config = cache.guilds.get(str(guild_id)) or await storage.guilds.insert(
        guild_id=guild_id,
        owner_id=getattr(bot_guild, "owner_id", None),
        prefix=BOT_CONFIG.PREFIX,
        language="en",
        subscription="free",
    )
    automod_config = cache.automod.get(str(guild_id)) or await storage.automod.insert(guild_id=guild_id)
    antinuke_config = cache.antinuke_settings.get(str(guild_id)) or await storage.antinuke_settings.insert(guild_id=guild_id)
    music_config = cache.music.get(str(guild_id)) or await storage.music.insert(guild_id=guild_id)
    command_config = cache.command_access.get(str(guild_id)) or await storage.command_access.insert(
        guild_id=guild_id,
        disabled_commands=[],
    )
    giveaway_permissions = cache.giveaways_permissions.get(str(guild_id)) or await storage.giveaways_permissions.insert(
        guild_id=guild_id
    )
    welcomer_config = cache.welcomer_settings.get(str(guild_id)) or await storage.welcomer_settings.insert(
        guild_id=guild_id
    )
    ticket_modules = cache.ticket_settings.get(str(guild_id), {})
    if not ticket_modules:
        created_module = await storage.ticket_settings.insert(
            guild_id=guild_id,
            enabled=False,
            support_roles=[],
            ticket_limit=1,
            open_ticket_category_id=None,
            closed_ticket_category_id=None,
            ticket_panel_channel_id=None,
            ticket_panel_message_id=None,
            ticket_panel_message_content=None,
            ticket_panel_message_embed={},
            close_ticket_message_content=None,
            close_ticket_message_embed={},
        )
        ticket_modules = {str(created_module["ticket_module_id"]): created_module}

    return {
        "guild": guild_config or cache.guilds.get(str(guild_id), {}),
        "automod": automod_config or cache.automod.get(str(guild_id), {}),
        "antinuke": antinuke_config or cache.antinuke_settings.get(str(guild_id), {}),
        "music": music_config or cache.music.get(str(guild_id), {}),
        "command_access": command_config or cache.command_access.get(str(guild_id), {}),
        "giveaway_permissions": giveaway_permissions or cache.giveaways_permissions.get(str(guild_id), {}),
        "welcomer": welcomer_config or cache.welcomer_settings.get(str(guild_id), {}),
        "ticket_modules": list(ticket_modules.values()),
    }


def _music_snapshot(bot_guild) -> dict[str, Any]:
    voice_client = getattr(bot_guild, "voice_client", None)
    current = getattr(voice_client, "current", None)
    if not voice_client or not current:
        return {"active": False}
    queue_items = list(getattr(voice_client, "queue", []))
    artwork = getattr(current, "artwork", None) or getattr(current, "artwork_url", None) or style_urls.DEFAULT_MUSIC_BANNER
    return {
        "active": True,
        "title": current.title,
        "author": current.author,
        "artwork": artwork,
        "position": _format_ms(getattr(voice_client, "position", 0)),
        "duration": _format_ms(getattr(current, "length", 0)),
        "queue_size": len(queue_items),
        "queue_titles": [getattr(track, "title", "Unknown") for track in queue_items[:5]],
        "volume": getattr(voice_client, "volume", 0),
        "paused": getattr(voice_client, "paused", False),
        "channel": getattr(getattr(voice_client, "channel", None), "name", "Unknown"),
    }


def _command_catalog() -> list[dict[str, str]]:
    bot = get_bot()
    if not bot:
        return []
    commands_out = []
    for command in sorted(bot.commands, key=lambda item: item.qualified_name.lower()):
        if getattr(command, "hidden", False):
            continue
        commands_out.append(
            {
                "name": command.qualified_name,
                "brief": _clean_text(command.help or command.brief or "No description"),
                "category": getattr(getattr(command, "cog", None), "qualified_name", "General"),
            }
        )
    return commands_out


def _render_meter(label: str, value: int, maximum: int, tone: str = "blue") -> str:
    percentage = 0 if maximum <= 0 else max(0, min(100, int((value / maximum) * 100)))
    return (
        '<div class="meter">'
        f'<div class="meter-head"><span>{_escape(label)}</span><strong>{value}</strong></div>'
        f'<div class="meter-track {tone}"><div class="meter-fill" style="width:{percentage}%"></div></div>'
        "</div>"
    )


def _guild_health(guild: dict[str, Any]) -> int:
    members_score = min(40, int((guild["members"] / 1500) * 40)) if guild["members"] else 0
    channels_score = min(30, int((guild["channels"] / 75) * 30)) if guild["channels"] else 0
    roles_score = min(30, int((guild["roles"] / 75) * 30)) if guild["roles"] else 0
    return members_score + channels_score + roles_score


def _chart_block(title: str, items: list[tuple[str, int, str]]) -> str:
    bars = []
    peak = max((item[1] for item in items), default=1)
    for label, value, tone in items:
        width = max(8, int((value / peak) * 100)) if peak else 8
        bars.append(
            '<div class="chart-row">'
            f'<span>{_escape(label)}</span>'
            f'<div class="chart-bar {tone}"><div class="chart-fill" style="width:{width}%"></div></div>'
            f'<strong>{value}</strong>'
            "</div>"
        )
    return f'<section class="panel"><h2>{_escape(title)}</h2><div class="chart-pack">{"".join(bars)}</div></section>'


def _recent_logs() -> list[str]:
    if not LOGS_DIR.exists():
        return ["No logs directory found yet."]
    log_files = sorted(LOGS_DIR.glob("*.log"), reverse=True)
    if not log_files:
        return ["No log files found yet."]
    content = log_files[0].read_text(encoding="utf-8", errors="ignore").splitlines()
    cleaned = [_clean_text(line) for line in content[-80:]]
    return cleaned or ["Latest log file is empty."]


def _music_log_lines(limit: int = 8) -> list[str]:
    lines = _recent_logs()
    music_lines = [
        line for line in lines
        if any(token in line.lower() for token in ("track ", "lavalink", "queue", "music", "player "))
    ]
    return music_lines[-limit:] or ["No recent music activity."]


def _live_payload(current_guild: dict[str, Any], bot_guild, state: dict[str, Any]) -> dict[str, Any]:
    music = _music_snapshot(bot_guild)
    metrics = _overview_metrics(current_guild, state, bot_guild)
    return {
        "music": music,
        "overview": {
            "guild_health": _guild_health(current_guild),
            "security": metrics["security"],
            "moderation": metrics["moderation"],
        },
        "music_logs": _music_log_lines(),
        "logs": _recent_logs(),
    }


def _render_layout(
    *,
    title: str,
    body: str,
    session: dict[str, Any] | None,
    guilds: list[dict[str, Any]] | None = None,
    current_guild: dict[str, Any] | None = None,
    active_tab: str | None = None,
    notice: str | None = None,
) -> str:
    user = session.get("user") if session else None

    guild_nav = ""
    if guilds:
        guild_nav = '<div class="guild-strip">' + "".join(
            f'<a class="guild-pill{" active" if current_guild and guild["id"] == current_guild["id"] else ""}" href="/dashboard/guild/{guild["id"]}">{_escape(guild["name"])}</a>'
            for guild in guilds[:10]
        ) + "</div>"

    tab_nav = ""
    if current_guild:
        tabs = [
            ("overview", "Overview"),
            ("security", "Security"),
            ("moderation", "Moderation"),
            ("music", "Music"),
            ("commands", "Commands"),
            ("logs", "Logs"),
            ("giveaways", "Giveaways"),
            ("tickets", "Tickets"),
            ("welcomer", "Welcomer"),
        ]
        links = []
        for slug, label in tabs:
            href = (
                f"/dashboard/guild/{current_guild['id']}"
                if slug == "overview"
                else f"/dashboard/guild/{current_guild['id']}/{slug}"
            )
            links.append(f'<a class="tab{" active" if slug == active_tab else ""}" href="{href}">{label}</a>')
        tab_nav = f'<nav class="tabs">{"".join(links)}</nav>'

    banner = f'<div class="notice">{_escape(_clean_text(notice))}</div>' if notice else ""
    account = (
        '<div class="account">'
        f'<img src="{_escape(user.get("avatar_url"))}" alt="avatar" />'
        f'<div><strong>{_escape(user.get("username"))}</strong><span>{_escape(user.get("global_name") or "Discord")}</span></div>'
        '<a class="ghost-btn" href="/dashboard/logout">Logout</a>'
        "</div>"
        if user
        else '<div class="account-lite">Discord required</div>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #060203;
      --panel: rgba(11, 6, 7, 0.92);
      --panel-2: rgba(7, 2, 4, 0.98);
      --line: rgba(255, 255, 255, 0.08);
      --line-strong: rgba(255, 255, 255, 0.14);
      --text: #fff4f5;
      --muted: #b69499;
      --brand: #ff5067;
      --brand-2: #8f1429;
      --shadow: 0 28px 80px rgba(0, 0, 0, 0.42);
    }}
    * {{
      box-sizing: border-box;
    }}
    html {{
      color-scheme: dark;
    }}
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: rgba(255, 255, 255, 0.02);
    }}
    ::-webkit-scrollbar-thumb {{
      background: rgba(255, 255, 255, 0.14);
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: rgba(255, 80, 103, 0.8);
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: "Manrope", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255, 80, 103, 0.16), transparent 24%),
        radial-gradient(circle at top right, rgba(143, 20, 41, 0.16), transparent 24%),
        linear-gradient(180deg, #030102 0%, #080304 46%, #050203 100%);
      background-attachment: fixed;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
      background-size: 30px 30px;
      mask-image: radial-gradient(circle at center, rgba(0,0,0,0.92), transparent 80%);
    }}
    .frame {{
      width: min(1240px, calc(100% - 24px));
      margin: 16px auto;
      border: 1px solid var(--line);
      border-radius: 28px;
      overflow: hidden;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01)),
        linear-gradient(180deg, rgba(10, 4, 6, 0.9), rgba(5, 2, 3, 0.9));
      box-shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
      backdrop-filter: blur(18px) saturate(120%);
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 14px;
      padding: 18px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(16, 8, 10, 0.72);
      backdrop-filter: blur(12px);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    .brand {{
      display: grid;
      gap: 4px;
    }}
    .brand strong {{
      font-family: "Sora", sans-serif;
      font-size: 1.16rem;
      letter-spacing: 0.06em;
    }}
    .brand span {{
      color: var(--muted);
      font-size: 0.86rem;
    }}
    .account {{
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255,255,255,0.05);
    }}
    .account img {{
      width: 40px;
      height: 40px;
      border-radius: 14px;
      object-fit: cover;
      border: 1px solid var(--line);
    }}
    .account div {{
      display: grid;
      gap: 2px;
    }}
    .account span {{
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .account-lite {{
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255,255,255,0.03);
      color: var(--muted);
      font-size: 0.85rem;
      font-weight: 700;
    }}
    .content {{
      display: grid;
      gap: 16px;
      padding: 18px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: 1.2fr .8fr;
      gap: 14px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 20px;
      background: linear-gradient(180deg, var(--panel), var(--panel-2));
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 14px 30px rgba(0, 0, 0, 0.22);
      animation: fadeInUp 0.35s ease;
    }}
    .panel h1, .panel h2, .panel h3 {{
      margin: 0 0 8px;
      font-family: "Sora", sans-serif;
    }}
    .panel h1 {{
      font-size: clamp(1.6rem, 3vw, 2.25rem);
      letter-spacing: -0.04em;
      line-height: 1;
    }}
    .panel h2 {{
      font-size: 1rem;
      letter-spacing: -0.02em;
    }}
    .muted {{
      color: var(--muted);
      line-height: 1.55;
    }}
    .notice {{
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid rgba(255, 80, 103, 0.24);
      background: rgba(255, 80, 103, 0.1);
      color: #ffe3e7;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
    }}
    .guild-strip, .tabs {{
      display: flex;
      flex-wrap: nowrap;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: thin;
    }}
    .guild-pill, .tab, .ghost-btn, .primary-btn, .save-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 14px;
      border: 1px solid var(--line);
      border-radius: 999px;
      text-decoration: none;
      font-weight: 700;
      white-space: nowrap;
      transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
    }}
    .guild-pill, .tab, .ghost-btn {{
      color: var(--text);
      background: rgba(255,255,255,0.02);
    }}
    .guild-pill:hover, .tab:hover, .ghost-btn:hover {{
      transform: translateY(-1px);
      border-color: var(--line-strong);
      background: rgba(255,255,255,0.06);
    }}
    .guild-pill.active, .tab.active {{
      background: rgba(255, 80, 103, 0.14);
      border-color: rgba(255, 80, 103, 0.28);
      box-shadow: inset 0 0 0 1px rgba(255, 80, 103, 0.24);
    }}
    .primary-btn, .save-btn {{
      color: #fff8f9;
      background: linear-gradient(135deg, var(--brand), var(--brand-2));
      border-color: rgba(255,255,255,0.08);
      box-shadow: 0 12px 24px rgba(143, 20, 41, 0.22);
      cursor: pointer;
    }}
    .primary-btn:hover, .save-btn:hover {{
      transform: translateY(-1px);
      box-shadow: 0 16px 28px rgba(143, 20, 41, 0.3);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 12px;
    }}
    .card {{
      grid-column: span 4;
      padding: 16px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.02);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
    }}
    .metric {{
      margin-top: 6px;
      font-family: "Sora", sans-serif;
      font-size: 1.6rem;
      font-weight: 800;
      letter-spacing: -0.04em;
    }}
    .guild-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 12px;
    }}
    .guild-card {{
      color: var(--text);
      text-decoration: none;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      background: rgba(255,255,255,0.02);
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .guild-card:hover {{
      transform: translateY(-2px);
      border-color: var(--line-strong);
      box-shadow: 0 14px 26px rgba(0, 0, 0, 0.22);
    }}
    .guild-card-head {{
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 6px;
    }}
    .guild-card img {{
      width: 52px;
      height: 52px;
      border-radius: 16px;
      object-fit: cover;
      border: 1px solid var(--line);
    }}
    .guild-card-copy {{
      display: grid;
      gap: 4px;
    }}
    .guild-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.82rem;
    }}
    .mini-stat, .pill, .tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 9px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.02);
      color: var(--muted);
      font-size: 0.8rem;
    }}
    .forms, form {{
      display: grid;
      gap: 12px;
    }}
    .fields {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    label {{
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    input, select, textarea {{
      width: 100%;
      padding: 11px 13px;
      border: 1px solid var(--line);
      border-radius: 14px;
      background: rgba(7, 3, 5, 0.94);
      color: var(--text);
      outline: none;
      transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
    }}
    input:focus, select:focus, textarea:focus {{
      border-color: rgba(255, 80, 103, 0.4);
      box-shadow: 0 0 0 3px rgba(255, 80, 103, 0.12);
    }}
    textarea {{
      min-height: 110px;
      resize: vertical;
    }}
    .switches {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .check {{
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 12px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.02);
      color: var(--text);
      transition: border-color 0.16s ease, background 0.16s ease;
    }}
    .check:hover {{
      border-color: var(--line-strong);
      background: rgba(255,255,255,0.04);
    }}
    .check input {{
      width: 18px;
      height: 18px;
    }}
    .music-now {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}
    .command-list {{
      display: grid;
      gap: 10px;
    }}
    .command-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
      padding: 12px 14px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.02);
    }}
    .danger-btn, .ok-btn {{
      padding: 9px 12px;
      border-radius: 12px;
      border: 1px solid transparent;
      color: var(--text);
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.16s ease, filter 0.16s ease;
    }}
    .danger-btn:hover, .ok-btn:hover {{
      transform: translateY(-1px);
      filter: brightness(1.05);
    }}
    .danger-btn {{
      background: rgba(251,113,133,0.15);
      border-color: rgba(251,113,133,0.24);
    }}
    .ok-btn {{
      background: rgba(52,211,153,0.15);
      border-color: rgba(52,211,153,0.24);
    }}
    .meter {{
      display: grid;
      gap: 6px;
      margin-top: 12px;
    }}
    .meter-head {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      font-size: 0.84rem;
      color: var(--muted);
    }}
    .meter-track, .chart-bar {{
      width: 100%;
      height: 10px;
      border-radius: 999px;
      overflow: hidden;
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(255,255,255,0.04);
    }}
    .meter-fill, .chart-fill {{
      height: 100%;
      border-radius: inherit;
      background: linear-gradient(90deg, var(--brand), #ff8796);
    }}
    .meter-track.green .meter-fill, .chart-bar.green .chart-fill {{
      background: linear-gradient(90deg, #34d399, #10b981);
    }}
    .meter-track.blue .meter-fill, .chart-bar.blue .chart-fill {{
      background: linear-gradient(90deg, #ff5067, #d22645);
    }}
    .meter-track.amber .meter-fill, .chart-bar.amber .chart-fill {{
      background: linear-gradient(90deg, #fbbf24, #f59e0b);
    }}
    .meter-track.violet .meter-fill, .chart-bar.violet .chart-fill {{
      background: linear-gradient(90deg, #c4b5fd, #8b5cf6);
    }}
    .chart-pack {{
      display: grid;
      gap: 10px;
      margin-top: 14px;
    }}
    .chart-row {{
      display: grid;
      grid-template-columns: 120px 1fr 40px;
      gap: 10px;
      align-items: center;
      color: var(--muted);
      font-size: 0.85rem;
    }}
    .section-stack {{
      display: grid;
      gap: 14px;
    }}
    .log-box {{
      max-height: 520px;
      overflow: auto;
      padding: 14px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: rgba(4, 1, 2, 0.92);
      color: #d5def1;
      font-family: Consolas, monospace;
      font-size: 0.86rem;
      line-height: 1.55;
      white-space: pre-wrap;
    }}
    .auth-shell {{
      min-height: calc(100vh - 210px);
      grid-template-columns: 1fr;
      align-items: center;
    }}
    .auth-panel {{
      width: min(440px, 100%);
      margin: 0 auto;
      text-align: center;
      padding: 26px;
    }}
    .auth-actions {{
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 18px;
    }}
    @keyframes fadeInUp {{
      from {{
        opacity: 0;
        transform: translateY(10px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
    @media (max-width: 980px) {{
      .hero, .music-now, .fields, .switches {{
        grid-template-columns: 1fr;
      }}
      .card {{
        grid-column: span 12;
      }}
      .topbar, .command-row {{
        flex-direction: column;
        align-items: flex-start;
      }}
      .chart-row {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 640px) {{
      .frame {{
        width: calc(100% - 12px);
        margin: 6px auto;
        border-radius: 20px;
      }}
      .topbar, .content {{
        padding-left: 14px;
        padding-right: 14px;
      }}
      .topbar {{
        padding-top: 16px;
        padding-bottom: 16px;
      }}
      .panel {{
        padding: 16px;
        border-radius: 16px;
      }}
      .brand strong {{
        font-size: 1rem;
      }}
      .account, .account-lite {{
        width: 100%;
        justify-content: center;
      }}
      .guild-pill, .tab, .ghost-btn, .primary-btn, .save-btn {{
        width: 100%;
      }}
      .auth-panel {{
        padding: 22px 16px;
      }}
    }}
  </style>
</head>
<body>
  <div class="frame">
    <header class="topbar">
      <div class="brand">
        <strong>REO</strong>
        <span>Dashboard</span>
      </div>
      {account}
    </header>
    <main class="content">
      {banner}
      {guild_nav}
      {tab_nav}
      {body}
    </main>
  </div>
  <script>
    (() => {{
      const guildId = "{_escape(current_guild['id']) if current_guild else ''}";
      const activeTab = "{_escape(active_tab or '')}";
      if (!guildId || !["overview", "music", "logs"].includes(activeTab)) {{
        return;
      }}

      const updateText = (selector, value) => {{
        const el = document.querySelector(selector);
        if (el && value !== undefined && value !== null) {{
          el.textContent = value;
        }}
      }};

      const updateHTML = (selector, value) => {{
        const el = document.querySelector(selector);
        if (el && value !== undefined && value !== null) {{
          el.innerHTML = value;
        }}
      }};

      const renderMusic = (music, logs) => {{
        if (!music || !music.active) {{
          return;
        }}
        updateText('[data-live=\"music-state\"]', music.paused ? 'Paused' : 'Playing');
        updateText('[data-live=\"music-title\"]', music.title || 'Unknown');
        updateText('[data-live=\"music-author\"]', music.author || 'Unknown');
        updateText('[data-live=\"music-channel\"]', `Voice channel: ${{music.channel || 'Unknown'}}`);
        updateText('[data-live=\"music-time\"]', `${{music.position || '0s'}} / ${{music.duration || '0s'}}`);
        updateText('[data-live=\"music-stats\"]', `Queue size: ${{music.queue_size || 0}} | Volume: ${{music.volume || 0}}%`);
        const artwork = document.querySelector('[data-live=\"music-artwork\"]');
        if (artwork && music.artwork) {{
          artwork.src = music.artwork;
        }}
        if (Array.isArray(music.queue_titles)) {{
          updateHTML(
            '[data-live=\"music-queue\"]',
            music.queue_titles.length
              ? music.queue_titles.map((title) => `<div class="mini-stat">${{title}}</div>`).join("")
              : '<span class="mini-stat">Queue is empty</span>'
          );
        }}
        if (Array.isArray(logs)) {{
          updateText('[data-live=\"music-log-box\"]', logs.join("\\n"));
        }}
      }};

      const renderOverview = (payload) => {{
        if (!payload || !payload.overview) {{
          return;
        }}
        updateText('[data-live=\"overview-guild-health\"]', String(payload.overview.guild_health ?? 0));
        updateText('[data-live=\"overview-security\"]', String(payload.overview.security ?? 0));
        updateText('[data-live=\"overview-moderation\"]', String(payload.overview.moderation ?? 0));
        renderMusic(payload.music, payload.music_logs);
      }};

      const renderLogs = (logs) => {{
        if (Array.isArray(logs)) {{
          updateText('[data-live=\"logs-box\"]', logs.join("\\n"));
        }}
      }};

      const tick = async () => {{
        try {{
          const response = await fetch(`/dashboard/guild/${{guildId}}/live?tab=${{activeTab}}`, {{
            headers: {{ "X-Requested-With": "fetch" }},
            credentials: "same-origin",
            cache: "no-store",
          }});
          if (!response.ok) {{
            if (response.status === 403) {{
              window.location.reload();
            }}
            return;
          }}
          const payload = await response.json();
          if (activeTab === "music") {{
            renderMusic(payload.music, payload.music_logs);
          }} else if (activeTab === "overview") {{
            renderOverview(payload);
          }} else if (activeTab === "logs") {{
            renderLogs(payload.logs);
          }}
        }} catch (_error) {{
        }}
      }};

      tick();
      window.setInterval(tick, 5000);
    }})();
  </script>
</body>
</html>"""


def _render_login(notice: str | None = None) -> str:
    auth_ready = bool(BOT_CONFIG.DISCORD_CLIENT_ID and BOT_CONFIG.DISCORD_CLIENT_SECRET)
    action = (
        '<a class="primary-btn" href="/dashboard/login">Login with Discord</a>'
        if auth_ready
        else "<div class='notice'>Set `DISCORD_CLIENT_SECRET` in `.env` to enable Discord login.</div>"
    )
    body = f"""
    <section class="hero auth-shell">
      <article class="panel auth-panel">
        <h1>Login</h1>
        <p class="muted">Use Discord to continue.</p>
        <div class="auth-actions">
          {action}
        </div>
      </article>
    </section>
    """
    return _render_layout(title="REO Login", body=body, session=None, notice=notice)


def _render_guild_picker(session: dict[str, Any], guilds: list[dict[str, Any]], notice: str | None = None) -> str:
    cards = []
    for guild in guilds:
        health = _guild_health(guild)
        cards.append(
            f"""
            <a class="guild-card" href="/dashboard/guild/{guild['id']}">
              <div class="guild-card-head">
                <img src="{_escape(guild['icon'])}" alt="{_escape(guild['name'])}">
                <div class="guild-card-copy">
                  <h3>{_escape(guild['name'])}</h3>
                  <p class="muted">Open dashboard</p>
                </div>
              </div>
              {_render_meter("Guild health", health, 100, "green")}
              <div class="guild-meta">
                <span class="mini-stat">{guild['members']} members</span>
                <span class="mini-stat">{guild['channels']} channels</span>
                <span class="mini-stat">{guild['roles']} roles</span>
              </div>
            </a>
            """
        )
    body = f"""
    <section class="panel">
      <h1>Servers</h1>
      <p class="muted">Choose a server to continue.</p>
      <div class="guild-grid" style="margin-top:16px;">
        {''.join(cards) if cards else '<div class="notice">No manageable guilds were found for this account.</div>'}
      </div>
    </section>
    """
    return _render_layout(title="REO Guilds", body=body, session=session, guilds=guilds, notice=notice)


def _overview_metrics(current_guild: dict[str, Any], state: dict[str, Any], bot_guild) -> dict[str, int]:
    active_giveaways = len(cache.giveaways.get(str(bot_guild.id), {}))
    ticket_modules = state["ticket_modules"]
    welcomer = state["welcomer"]
    automod = state["automod"]
    antinuke = state["antinuke"]
    return {
        "security": sum(1 for key in ("anti_bot_add", "anti_channel_delete", "anti_role_delete", "anti_webhook_create", "anti_everyone_mention") if antinuke.get(key)),
        "moderation": sum(1 for key in ("antilink_enabled", "antispam_enabled", "antibadwords_enabled") if automod.get(key)),
        "tickets": sum(1 for module in ticket_modules if module.get("enabled")),
        "giveaways": active_giveaways,
        "welcomer": sum(1 for key in ("welcome", "welcome_message", "welcome_embed", "autorole", "greet") if welcomer.get(key)),
        "commands": len(state["command_access"].get("disabled_commands", []) or []),
    }


def _render_overview(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], bot_guild, state: dict[str, Any], notice: str | None = None) -> str:
    guild_state = state["guild"]
    music = _music_snapshot(bot_guild)
    metrics = _overview_metrics(current_guild, state, bot_guild)
    overview_chart = _chart_block(
        "Runtime posture",
        [
            ("Security", metrics["security"], "green"),
            ("Moderation", metrics["moderation"], "blue"),
            ("Welcomer", metrics["welcomer"], "amber"),
            ("Active giveaways", metrics["giveaways"], "violet"),
        ],
    )
    structure_chart = _chart_block(
        "Guild structure",
        [
            ("Members", current_guild["members"], "blue"),
            ("Channels", current_guild["channels"], "amber"),
            ("Roles", current_guild["roles"], "violet"),
        ],
    )
    music_panel = (
        f"""
        <section class="panel">
          <h2>Live music</h2>
          <div class="music-now" style="margin-top:14px;">
            <div>
              <div class="pill" data-live="music-state">{'Paused' if music.get('paused') else 'Playing'}</div>
              <h3 style="margin-top:14px;" data-live="music-title">{_escape(music.get('title'))}</h3>
              <p class="muted" data-live="music-author">{_escape(music.get('author'))}</p>
            </div>
            <div>
              <div class="pill" data-live="music-channel">Voice channel: {_escape(music.get('channel'))}</div>
              <p class="muted" style="margin-top:14px;" data-live="music-time">{_escape(music.get('position'))} / {_escape(music.get('duration'))}</p>
              <p class="muted" data-live="music-stats">Queue size: {music.get('queue_size')} | Volume: {music.get('volume')}%</p>
            </div>
          </div>
        </section>
        """
        if music.get("active")
        else '<section class="panel"><h2>Live music</h2><div class="notice" style="margin-top:14px;">No music session is active in this guild right now.</div></section>'
    )
    body = f"""
    <section class="hero">
      <article class="panel">
        <h1>{_escape(current_guild['name'])}</h1>
        <p class="muted">Overview</p>
        <div class="grid" style="margin-top:18px;">
          <div class="card"><strong>Prefix</strong><div class="metric">{_escape(guild_state.get('prefix', BOT_CONFIG.PREFIX))}</div></div>
          <div class="card"><strong>Subscription</strong><div class="metric">{_escape((guild_state.get('subscription') or 'free').replace('_', ' ').title())}</div></div>
          <div class="card"><strong>Disabled commands</strong><div class="metric">{metrics['commands']}</div></div>
          <div class="card"><strong>Ticket modules</strong><div class="metric">{metrics['tickets']}</div></div>
          <div class="card"><strong>Giveaways</strong><div class="metric">{metrics['giveaways']}</div></div>
          <div class="card"><strong>Welcomer blocks</strong><div class="metric">{metrics['welcomer']}</div></div>
        </div>
      </article>
      {music_panel}
    </section>
    <section class="grid">
      <div class="card" style="grid-column: span 6;">
        <div data-live="overview-guild-health" style="display:none;">{_guild_health(current_guild)}</div>
        <div data-live="overview-security" style="display:none;">{metrics["security"]}</div>
        <div data-live="overview-moderation" style="display:none;">{metrics["moderation"]}</div>
        {_render_meter("Guild health", _guild_health(current_guild), 100, "green")}
        {_render_meter("Security coverage", metrics["security"], 5, "blue")}
        {_render_meter("Moderation coverage", metrics["moderation"], 3, "amber")}
      </div>
      <div class="card" style="grid-column: span 6;">
        <h2>General settings</h2>
        <form method="post" action="/dashboard/guild/{current_guild['id']}/general" style="margin-top:16px;">
          <div class="fields">
            <label>Prefix
              <input type="text" name="prefix" value="{_escape(guild_state.get('prefix', BOT_CONFIG.PREFIX))}" maxlength="5">
            </label>
            <label>Language
              <select name="language">
                <option value="en" {"selected" if (guild_state.get("language") or "en") == "en" else ""}>English</option>
                <option value="hi" {"selected" if guild_state.get("language") == "hi" else ""}>Hindi</option>
              </select>
            </label>
          </div>
          <button class="save-btn" type="submit">Save general settings</button>
        </form>
      </div>
    </section>
    <section class="hero">
      {overview_chart}
      {structure_chart}
    </section>
    """
    return _render_layout(
        title=f"REO Overview - {current_guild['name']}",
        body=body,
        session=session,
        guilds=guilds,
        current_guild=current_guild,
        active_tab="overview",
        notice=notice,
    )


def _render_security(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], state: dict[str, Any], notice: str | None = None) -> str:
    data = state["antinuke"]
    body = f"""
    <section class="panel">
      <h1>Security</h1>
      <p class="muted">Security settings</p>
      <form method="post" action="/dashboard/guild/{current_guild['id']}/security" style="margin-top:18px;">
        <div class="fields">
          <label>Protection mode
            <select name="type">
              <option value="normal" {"selected" if data.get("type") == "normal" else ""}>Normal</option>
              <option value="extream" {"selected" if data.get("type") == "extream" else ""}>Extreme</option>
              <option value="custom" {"selected" if data.get("type") == "custom" else ""}>Custom</option>
            </select>
          </label>
          <label>Bypass role ID
            <input type="text" name="bypass_role_id" value="{_escape(data.get('bypass_role_id', ''))}">
          </label>
        </div>
        <div class="switches">
          <label class="check"><input type="checkbox" name="enabled" {"checked" if data.get("enabled") else ""}> Enable antinuke core</label>
          <label class="check"><input type="checkbox" name="anti_bot_add" {"checked" if data.get("anti_bot_add") else ""}> Block unauthorized bot adds</label>
          <label class="check"><input type="checkbox" name="anti_channel_delete" {"checked" if data.get("anti_channel_delete") else ""}> Protect channel deletes</label>
          <label class="check"><input type="checkbox" name="anti_role_delete" {"checked" if data.get("anti_role_delete") else ""}> Protect role deletes</label>
          <label class="check"><input type="checkbox" name="anti_webhook_create" {"checked" if data.get("anti_webhook_create") else ""}> Protect webhook creation</label>
          <label class="check"><input type="checkbox" name="anti_everyone_mention" {"checked" if data.get("anti_everyone_mention") else ""}> Protect everyone mentions</label>
        </div>
        <div class="fields">
          <label>Bot add punishment
            <select name="anti_bot_add_punishment">
              <option value="kick" {"selected" if data.get("anti_bot_add_punishment") == "kick" else ""}>Kick</option>
              <option value="ban" {"selected" if data.get("anti_bot_add_punishment") == "ban" else ""}>Ban</option>
              <option value="mute" {"selected" if data.get("anti_bot_add_punishment") == "mute" else ""}>Mute</option>
            </select>
          </label>
          <label>Bot add limit
            <input type="number" min="1" max="10" name="anti_bot_add_limit" value="{_escape(data.get('anti_bot_add_limit', 1))}">
          </label>
        </div>
        <button class="save-btn" type="submit">Save</button>
      </form>
    </section>
    """
    return _render_layout(title=f"REO Security - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="security", notice=notice)


def _render_moderation(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], state: dict[str, Any], notice: str | None = None) -> str:
    data = state["automod"]
    body = f"""
    <section class="panel">
      <h1>Moderation Controls</h1>
      <p class="muted">Keep your chat clean.</p>
      <form method="post" action="/dashboard/guild/{current_guild['id']}/moderation" style="margin-top:18px;">
        <div class="switches">
          <label class="check"><input type="checkbox" name="antilink_enabled" {"checked" if data.get("antilink_enabled") else ""}> Enable anti-link</label>
          <label class="check"><input type="checkbox" name="antispam_enabled" {"checked" if data.get("antispam_enabled") else ""}> Enable anti-spam</label>
          <label class="check"><input type="checkbox" name="antibadwords_enabled" {"checked" if data.get("antibadwords_enabled") else ""}> Enable bad-word filter</label>
        </div>
        <div class="fields">
          <label>Max messages
            <input type="number" min="1" max="30" name="antispam_max_messages" value="{_escape(data.get('antispam_max_messages', 10))}">
          </label>
          <label>Interval seconds
            <input type="number" min="1" max="120" name="antispam_max_interval" value="{_escape(data.get('antispam_max_interval', 30))}">
          </label>
          <label>Max mentions
            <input type="number" min="1" max="20" name="antispam_max_mentions" value="{_escape(data.get('antispam_max_mentions', 5))}">
          </label>
          <label>Punishment
            <select name="antispam_punishment">
              <option value="mute" {"selected" if data.get("antispam_punishment") == "mute" else ""}>Mute</option>
              <option value="kick" {"selected" if data.get("antispam_punishment") == "kick" else ""}>Kick</option>
              <option value="ban" {"selected" if data.get("antispam_punishment") == "ban" else ""}>Ban</option>
              <option value="warn" {"selected" if data.get("antispam_punishment") == "warn" else ""}>Warn</option>
            </select>
          </label>
          <label>Punishment duration (minutes)
            <input type="number" min="1" max="1440" name="antispam_punishment_duration" value="{_escape(data.get('antispam_punishment_duration', 10))}">
          </label>
          <label>Bad words list
            <input type="text" name="antibadwords_words" value="{_escape(', '.join(data.get('antibadwords_words', []) or []))}" placeholder="word1, word2, word3">
          </label>
        </div>
        <button class="save-btn" type="submit">Save moderation settings</button>
      </form>
    </section>
    """
    return _render_layout(title=f"REO Moderation - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="moderation", notice=notice)


def _render_music(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], bot_guild, state: dict[str, Any], notice: str | None = None) -> str:
    data = state["music"]
    current = _music_snapshot(bot_guild)
    queue_lines = "".join(f'<div class="mini-stat">{_escape(title)}</div>' for title in current.get("queue_titles", []))
    music_logs = "\n".join(_escape(line) for line in _music_log_lines())
    now_playing = (
        f"""
        <section class="panel">
          <h2>Now playing</h2>
          <div class="music-now" style="margin-top:14px;">
            <div>
              <img data-live="music-artwork" src="{_escape(current.get('artwork'))}" alt="{_escape(current.get('title'))}" style="width:100%; max-width:320px; aspect-ratio:1/1; object-fit:cover; border-radius:18px; border:1px solid rgba(255,255,255,0.08); display:block; margin-bottom:14px;">
              <div class="pill" data-live="music-state">{'Paused' if current.get('paused') else 'Playing'}</div>
              <h3 style="margin-top:14px;" data-live="music-title">{_escape(current.get('title'))}</h3>
              <p class="muted" data-live="music-author">{_escape(current.get('author'))}</p>
            </div>
            <div>
              <div class="pill" data-live="music-channel">Voice channel: {_escape(current.get('channel'))}</div>
              <p class="muted" style="margin-top:14px;" data-live="music-time">{_escape(current.get('position'))} / {_escape(current.get('duration'))}</p>
              <p class="muted" data-live="music-stats">Queue size: {current.get('queue_size')} | Volume: {current.get('volume')}%</p>
              <div style="margin-top:14px;">
                <strong>Queue</strong>
                <div class="guild-meta" style="margin-top:10px;" data-live="music-queue">
                  {queue_lines or '<span class="mini-stat">Queue is empty</span>'}
                </div>
              </div>
              <div style="margin-top:16px;">
                <strong>Activity</strong>
                <div class="log-box" data-live="music-log-box" style="margin-top:10px; max-height:220px;">{music_logs}</div>
              </div>
            </div>
          </div>
        </section>
        """
        if current.get("active")
        else '<section class="panel"><h2>Now playing</h2><div class="notice" style="margin-top:14px;">No music session is active in this guild right now.</div></section>'
    )
    body = f"""
    <section class="hero">
      {now_playing}
      <section class="panel">
        <h2>Default music profile</h2>
        <form method="post" action="/dashboard/guild/{current_guild['id']}/music" style="margin-top:18px;">
          <div class="fields">
            <label>Default volume
              <input type="number" min="0" max="100" name="default_volume" value="{_escape(data.get('default_volume', 80))}">
            </label>
          </div>
          <div class="switches">
            <label class="check"><input type="checkbox" name="default_repeat" {"checked" if data.get("default_repeat") else ""}> Enable default repeat</label>
            <label class="check"><input type="checkbox" name="default_autoplay" {"checked" if data.get("default_autoplay") else ""}> Enable default autoplay</label>
          </div>
          <button class="save-btn" type="submit">Save music defaults</button>
        </form>
      </section>
    </section>
    """
    return _render_layout(title=f"REO Music - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="music", notice=notice)


def _render_commands(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], state: dict[str, Any], notice: str | None = None) -> str:
    disabled = set(state["command_access"].get("disabled_commands", []) or [])
    rows = []
    for command in _command_catalog():
        is_disabled = command["name"] in disabled
        rows.append(
            f"""
            <div class="command-row">
              <div>
                <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                  <strong>{_escape(command['name'])}</strong>
                  <span class="tag">{_escape(command['category'])}</span>
                  <span class="tag">{'Disabled' if is_disabled else 'Enabled'}</span>
                </div>
                <p class="muted" style="margin:8px 0 0;">{_escape(command['brief'])}</p>
              </div>
              <form method="post" action="/dashboard/guild/{current_guild['id']}/commands/toggle">
                <input type="hidden" name="command_name" value="{_escape(command['name'])}">
                <input type="hidden" name="action" value="{'enable' if is_disabled else 'disable'}">
                <button class="{'ok-btn' if is_disabled else 'danger-btn'}" type="submit">{'Enable' if is_disabled else 'Disable'}</button>
              </form>
            </div>
            """
        )
    body = f"""
    <section class="panel">
      <h1>Command Access</h1>
      <p class="muted">Command access</p>
      <div class="command-list" style="margin-top:18px;">
        {''.join(rows) if rows else '<div class="notice">No commands are available to manage right now.</div>'}
      </div>
    </section>
    """
    return _render_layout(title=f"REO Commands - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="commands", notice=notice)


def _render_logs(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], notice: str | None = None) -> str:
    lines = "\n".join(_escape(line) for line in _recent_logs())
    body = f"""
    <section class="section-stack">
      <section class="panel">
        <h1>Logs</h1>
      <p class="muted">Latest logs</p>
        <div class="log-box" data-live="logs-box" style="margin-top:16px;">{lines}</div>
      </section>
    </section>
    """
    return _render_layout(title=f"REO Logs - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="logs", notice=notice)


def _render_giveaways(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], state: dict[str, Any], notice: str | None = None) -> str:
    permissions = state["giveaway_permissions"]
    active = cache.giveaways.get(str(current_guild["id"]), {})
    chart = _chart_block(
        "Giveaway status",
        [
            ("Active", len(active), "violet"),
            ("Ended", len([item for item in active.values() if item.get("ended")]), "amber"),
        ],
    )
    body = f"""
    <section class="hero">
      <section class="panel">
        <h1>Giveaway Access</h1>
      <p class="muted">Giveaway access</p>
        <form method="post" action="/dashboard/guild/{current_guild['id']}/giveaways" style="margin-top:18px;">
          <div class="fields">
            <label>Required role ID
              <input type="text" name="required_role_id" value="{_escape(permissions.get('required_role_id', ''))}" placeholder="Role that can manage giveaways">
            </label>
          </div>
          <button class="save-btn" type="submit">Save giveaway access</button>
        </form>
      </section>
      {chart}
    </section>
    """
    return _render_layout(title=f"REO Giveaways - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="giveaways", notice=notice)


def _render_tickets(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], state: dict[str, Any], notice: str | None = None) -> str:
    module = sorted(state["ticket_modules"], key=lambda item: item.get("ticket_module_id", 0))[0]
    open_tickets = len([ticket for ticket in cache.tickets.get(str(current_guild["id"]), {}).values()]) if isinstance(cache.tickets.get(str(current_guild["id"])), dict) else 0
    body = f"""
    <section class="hero">
      <section class="panel">
        <h1>Ticket Module</h1>
      <p class="muted">Ticket settings</p>
        <form method="post" action="/dashboard/guild/{current_guild['id']}/tickets" style="margin-top:18px;">
          <div class="switches">
            <label class="check"><input type="checkbox" name="enabled" {"checked" if module.get("enabled") else ""}> Enable ticket module</label>
          </div>
          <div class="fields">
            <label>Support role IDs
              <input type="text" name="support_roles" value="{_escape(', '.join(str(role) for role in (module.get('support_roles') or [])))}" placeholder="123, 456">
            </label>
            <label>Ticket limit
              <input type="number" min="1" max="10" name="ticket_limit" value="{_escape(module.get('ticket_limit', 1))}">
            </label>
            <label>Open ticket category ID
              <input type="text" name="open_ticket_category_id" value="{_escape(module.get('open_ticket_category_id', ''))}">
            </label>
            <label>Closed ticket category ID
              <input type="text" name="closed_ticket_category_id" value="{_escape(module.get('closed_ticket_category_id', ''))}">
            </label>
            <label>Panel channel ID
              <input type="text" name="ticket_panel_channel_id" value="{_escape(module.get('ticket_panel_channel_id', ''))}">
            </label>
            <label>Panel message content
              <textarea name="ticket_panel_message_content">{_escape(module.get('ticket_panel_message_content', ''))}</textarea>
            </label>
          </div>
          <button class="save-btn" type="submit">Save ticket module</button>
        </form>
      </section>
      {_chart_block("Ticket flow", [("Open tickets", open_tickets, "amber"), ("Module limit", int(module.get('ticket_limit', 1) or 1), "blue")])}
    </section>
    """
    return _render_layout(title=f"REO Tickets - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="tickets", notice=notice)


def _render_welcomer(session: dict[str, Any], guilds: list[dict[str, Any]], current_guild: dict[str, Any], state: dict[str, Any], notice: str | None = None) -> str:
    data = state["welcomer"]
    body = f"""
    <section class="panel">
      <h1>Welcomer</h1>
      <p class="muted">Welcome settings</p>
      <form method="post" action="/dashboard/guild/{current_guild['id']}/welcomer" style="margin-top:18px;">
        <div class="switches">
          <label class="check"><input type="checkbox" name="welcome" {"checked" if data.get("welcome") else ""}> Enable welcome system</label>
          <label class="check"><input type="checkbox" name="welcome_message" {"checked" if data.get("welcome_message") else ""}> Send welcome message</label>
          <label class="check"><input type="checkbox" name="welcome_embed" {"checked" if data.get("welcome_embed") else ""}> Send welcome embed</label>
          <label class="check"><input type="checkbox" name="autorole" {"checked" if data.get("autorole") else ""}> Enable autorole</label>
          <label class="check"><input type="checkbox" name="autonick" {"checked" if data.get("autonick") else ""}> Enable autonick</label>
          <label class="check"><input type="checkbox" name="greet" {"checked" if data.get("greet") else ""}> Enable greet message</label>
        </div>
        <div class="fields">
          <label>Welcome channel ID
            <input type="text" name="welcome_channel" value="{_escape(data.get('welcome_channel', ''))}">
          </label>
          <label>Autorole IDs
            <input type="text" name="autoroles" value="{_escape(', '.join(str(role) for role in (data.get('autoroles') or [])))}" placeholder="123, 456">
          </label>
          <label>Autonick format
            <input type="text" name="autonick_format" value="{_escape(data.get('autonick_format', ''))}" placeholder="{{user}} | member">
          </label>
          <label>Greet channel IDs
            <input type="text" name="greet_channels" value="{_escape(', '.join(str(channel) for channel in (data.get('greet_channels') or [])))}" placeholder="123, 456">
          </label>
          <label>Welcome message content
            <textarea name="welcome_message_content">{_escape(data.get('welcome_message_content', ''))}</textarea>
          </label>
          <label>Greet message
            <textarea name="greet_message">{_escape(data.get('greet_message', 'Hello {user.mention} Welcome to {server}'))}</textarea>
          </label>
        </div>
        <button class="save-btn" type="submit">Save welcomer settings</button>
      </form>
    </section>
    """
    return _render_layout(title=f"REO Welcomer - {current_guild['name']}", body=body, session=session, guilds=guilds, current_guild=current_guild, active_tab="welcomer", notice=notice)


def _oauth_authorize_url() -> str:
    query = urlencode(
        {
            "client_id": BOT_CONFIG.DISCORD_CLIENT_ID,
            "redirect_uri": _dashboard_callback_url(),
            "response_type": "code",
            "scope": "identify guilds",
            "prompt": "consent",
            "state": create_oauth_state(),
        }
    )
    return f"https://discord.com/oauth2/authorize?{query}"


async def _discord_api_request(url: str, token: str) -> dict[str, Any] | list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.json()


async def _exchange_code(code: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": BOT_CONFIG.DISCORD_CLIENT_ID,
                "client_secret": BOT_CONFIG.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": _dashboard_callback_url(),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()


async def _load_oauth_profile(code: str) -> dict[str, Any]:
    token_payload = await _exchange_code(code)
    access_token = token_payload["access_token"]
    user = await _discord_api_request(f"{DISCORD_API}/users/@me", access_token)
    guilds = await _discord_api_request(f"{DISCORD_API}/users/@me/guilds", access_token)
    avatar_hash = user.get("avatar")
    avatar_url = (
        f"https://cdn.discordapp.com/avatars/{user['id']}/{avatar_hash}.png?size=128"
        if avatar_hash
        else "https://cdn.discordapp.com/embed/avatars/0.png"
    )
    return {
        "access_token": access_token,
        "created_at": int(time.time()),
        "user": {
            "id": user["id"],
            "username": user.get("username", "Discord User"),
            "global_name": user.get("global_name"),
            "avatar_url": avatar_url,
        },
        "guilds": guilds,
    }


@router.get("", response_class=HTMLResponse)
async def dashboard_home(request: Request, notice: str | None = None):
    session = _session_from_request(request)
    if not session:
        return HTMLResponse(_render_login(notice=notice))
    guilds = _manageable_guilds(session)
    return HTMLResponse(_render_guild_picker(session, guilds, notice=notice))


@router.get("/login")
async def dashboard_login():
    if not BOT_CONFIG.DISCORD_CLIENT_SECRET:
        return HTMLResponse(_render_login("Dashboard auth is not configured yet."), status_code=503)
    return RedirectResponse(_oauth_authorize_url(), status_code=303)


@router.get("/auth/callback")
async def dashboard_callback(code: str | None = None, state: str | None = None):
    if not code or not consume_oauth_state(state):
        return HTMLResponse(_render_login("Discord login could not be verified. Try again."), status_code=400)
    try:
        payload = await _load_oauth_profile(code)
    except Exception as error:
        return HTMLResponse(_render_login(f"Discord login failed: {_clean_text(error)}"), status_code=502)
    session_id = create_session(payload)
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="lax", secure=False, max_age=604800)
    return response


@router.get("/logout")
async def dashboard_logout(request: Request):
    destroy_session(request.cookies.get(SESSION_COOKIE))
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response


async def _require_dashboard_context(request: Request, guild_id: int):
    session = _session_from_request(request)
    if not session:
        return None, None, None, None
    guilds = _manageable_guilds(session)
    current_guild, bot_guild = _get_accessible_guild(session, guild_id)
    if not current_guild or not bot_guild:
        return session, guilds, None, None
    state = await _ensure_guild_records(guild_id, bot_guild)
    return session, guilds, current_guild, state


@router.get("/guild/{guild_id}", response_class=HTMLResponse)
async def dashboard_overview(request: Request, guild_id: int, notice: str | None = None):
    session, guilds, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session:
        return RedirectResponse("/dashboard", status_code=303)
    if not current_guild:
        return HTMLResponse(_render_guild_picker(session, guilds, "You do not have access to that server."), status_code=403)
    return HTMLResponse(_render_overview(session, guilds, current_guild, get_bot().get_guild(guild_id), state, notice=notice))


@router.get("/guild/{guild_id}/live")
async def dashboard_live(request: Request, guild_id: int, tab: str | None = None):
    session, guilds, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return JSONResponse({"error": "forbidden"}, status_code=403)
    bot_guild = get_bot().get_guild(guild_id)
    return JSONResponse(_live_payload(current_guild, bot_guild, state))


@router.get("/guild/{guild_id}/{tab}", response_class=HTMLResponse)
async def dashboard_tab(request: Request, guild_id: int, tab: str, notice: str | None = None):
    session, guilds, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session:
        return RedirectResponse("/dashboard", status_code=303)
    if not current_guild:
        return HTMLResponse(_render_guild_picker(session, guilds, "You do not have access to that server."), status_code=403)
    bot_guild = get_bot().get_guild(guild_id)
    renderers = {
        "overview": lambda: _render_overview(session, guilds, current_guild, bot_guild, state, notice=notice),
        "security": lambda: _render_security(session, guilds, current_guild, state, notice=notice),
        "moderation": lambda: _render_moderation(session, guilds, current_guild, state, notice=notice),
        "music": lambda: _render_music(session, guilds, current_guild, bot_guild, state, notice=notice),
        "commands": lambda: _render_commands(session, guilds, current_guild, state, notice=notice),
        "logs": lambda: _render_logs(session, guilds, current_guild, notice=notice),
        "giveaways": lambda: _render_giveaways(session, guilds, current_guild, state, notice=notice),
        "tickets": lambda: _render_tickets(session, guilds, current_guild, state, notice=notice),
        "welcomer": lambda: _render_welcomer(session, guilds, current_guild, state, notice=notice),
    }
    renderer = renderers.get(tab)
    if not renderer:
        return RedirectResponse(f"/dashboard/guild/{guild_id}", status_code=303)
    return HTMLResponse(renderer())


@router.post("/guild/{guild_id}/general")
async def update_general_settings(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    prefix = (data.get("prefix") or BOT_CONFIG.PREFIX).strip()[:5] or BOT_CONFIG.PREFIX
    language = (data.get("language") or "en").strip()[:8]
    await storage.guilds.update(id=state["guild"]["id"], prefix=prefix, language=language, owner_id=current_guild["owner_id"])
    return RedirectResponse(f"/dashboard/guild/{guild_id}?notice=General%20settings%20saved", status_code=303)


@router.post("/guild/{guild_id}/security")
async def update_security_settings(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    await storage.antinuke_settings.update(
        id=state["antinuke"]["id"],
        enabled=_bool_from_form(data, "enabled"),
        type=(data.get("type") or "normal").lower(),
        bypass_role_id=int(data["bypass_role_id"]) if data.get("bypass_role_id", "").isdigit() else None,
        anti_bot_add=_bool_from_form(data, "anti_bot_add"),
        anti_bot_add_limit=int(data.get("anti_bot_add_limit", 1) or 1),
        anti_bot_add_punishment=(data.get("anti_bot_add_punishment") or "kick").lower(),
        anti_channel_delete=_bool_from_form(data, "anti_channel_delete"),
        anti_role_delete=_bool_from_form(data, "anti_role_delete"),
        anti_webhook_create=_bool_from_form(data, "anti_webhook_create"),
        anti_everyone_mention=_bool_from_form(data, "anti_everyone_mention"),
    )
    return RedirectResponse(f"/dashboard/guild/{guild_id}/security?notice=Security%20settings%20saved", status_code=303)


@router.post("/guild/{guild_id}/moderation")
async def update_moderation_settings(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    badwords = [word.strip() for word in (data.get("antibadwords_words") or "").split(",") if word.strip()]
    await storage.automod.update(
        id=state["automod"]["id"],
        antilink_enabled=_bool_from_form(data, "antilink_enabled"),
        antispam_enabled=_bool_from_form(data, "antispam_enabled"),
        antibadwords_enabled=_bool_from_form(data, "antibadwords_enabled"),
        antispam_max_messages=int(data.get("antispam_max_messages", 10) or 10),
        antispam_max_interval=int(data.get("antispam_max_interval", 30) or 30),
        antispam_max_mentions=int(data.get("antispam_max_mentions", 5) or 5),
        antispam_punishment=(data.get("antispam_punishment") or "mute").lower(),
        antispam_punishment_duration=int(data.get("antispam_punishment_duration", 10) or 10),
        antibadwords_words=badwords,
    )
    return RedirectResponse(f"/dashboard/guild/{guild_id}/moderation?notice=Moderation%20settings%20saved", status_code=303)


@router.post("/guild/{guild_id}/music")
async def update_music_settings(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    volume = max(0, min(100, int(data.get("default_volume", 80) or 80)))
    await storage.music.update(id=state["music"]["id"], default_volume=volume, default_repeat=_bool_from_form(data, "default_repeat"), default_autoplay=_bool_from_form(data, "default_autoplay"))
    return RedirectResponse(f"/dashboard/guild/{guild_id}/music?notice=Music%20defaults%20saved", status_code=303)


@router.post("/guild/{guild_id}/commands/toggle")
async def toggle_command(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    command_name = (data.get("command_name") or "").strip()
    action = (data.get("action") or "disable").strip().lower()
    disabled = set(state["command_access"].get("disabled_commands", []) or [])
    if command_name:
        if action == "enable":
            disabled.discard(command_name)
        else:
            disabled.add(command_name)
        await storage.command_access.update(id=state["command_access"]["id"], disabled_commands=sorted(disabled))
    return RedirectResponse(f"/dashboard/guild/{guild_id}/commands?notice=Command%20access%20updated", status_code=303)


@router.post("/guild/{guild_id}/giveaways")
async def update_giveaway_settings(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    required_role_id = int(data["required_role_id"]) if data.get("required_role_id", "").isdigit() else None
    await storage.giveaways_permissions.update(id=state["giveaway_permissions"]["id"], required_role_id=required_role_id)
    return RedirectResponse(f"/dashboard/guild/{guild_id}/giveaways?notice=Giveaway%20access%20saved", status_code=303)


@router.post("/guild/{guild_id}/tickets")
async def update_ticket_settings(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    module = sorted(state["ticket_modules"], key=lambda item: item.get("ticket_module_id", 0))[0]
    support_roles = [int(item.strip()) for item in (data.get("support_roles") or "").split(",") if item.strip().isdigit()]
    await storage.ticket_settings.update(
        id=module["id"],
        enabled=_bool_from_form(data, "enabled"),
        support_roles=support_roles,
        ticket_limit=int(data.get("ticket_limit", 1) or 1),
        open_ticket_category_id=int(data["open_ticket_category_id"]) if data.get("open_ticket_category_id", "").isdigit() else None,
        closed_ticket_category_id=int(data["closed_ticket_category_id"]) if data.get("closed_ticket_category_id", "").isdigit() else None,
        ticket_panel_channel_id=int(data["ticket_panel_channel_id"]) if data.get("ticket_panel_channel_id", "").isdigit() else None,
        ticket_panel_message_content=(data.get("ticket_panel_message_content") or "").strip() or None,
    )
    return RedirectResponse(f"/dashboard/guild/{guild_id}/tickets?notice=Ticket%20module%20saved", status_code=303)


@router.post("/guild/{guild_id}/welcomer")
async def update_welcomer_settings(request: Request, guild_id: int):
    session, _, current_guild, state = await _require_dashboard_context(request, guild_id)
    if not session or not current_guild:
        return RedirectResponse("/dashboard", status_code=303)
    data = await _parse_form(request)
    autoroles = [int(item.strip()) for item in (data.get("autoroles") or "").split(",") if item.strip().isdigit()]
    greet_channels = [int(item.strip()) for item in (data.get("greet_channels") or "").split(",") if item.strip().isdigit()]
    await storage.welcomer_settings.update(
        id=state["welcomer"]["id"],
        welcome=_bool_from_form(data, "welcome"),
        welcome_message=_bool_from_form(data, "welcome_message"),
        welcome_embed=_bool_from_form(data, "welcome_embed"),
        autorole=_bool_from_form(data, "autorole"),
        autonick=_bool_from_form(data, "autonick"),
        greet=_bool_from_form(data, "greet"),
        welcome_channel=int(data["welcome_channel"]) if data.get("welcome_channel", "").isdigit() else None,
        autoroles=autoroles,
        autonick_format=(data.get("autonick_format") or "").strip() or None,
        greet_channels=greet_channels,
        welcome_message_content=(data.get("welcome_message_content") or "").strip() or None,
        greet_message=(data.get("greet_message") or "").strip() or None,
    )
    return RedirectResponse(f"/dashboard/guild/{guild_id}/welcomer?notice=Welcomer%20settings%20saved", status_code=303)


__all__ = ["router", "bind_bot"]
