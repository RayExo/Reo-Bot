import os
import re
import base64
import requests
from dotenv import load_dotenv
from colorama import Fore, Style

from reo.console.logging import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
TOKEN = os.getenv("TOKEN")

def fetch_emoji_image(emoji_id, animated):
    ext = 'gif' if animated else 'webp'
    url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.content
        elif r.status_code in (301, 302):
            location = r.headers.get('Location')
            if location:
                r2 = requests.get(location)
                if r2.status_code == 200:
                    return r2.content
    except Exception:
        pass
    return None


def run_sync():
    """Runs the emoji sync sequence native to emoji.py. Safe to be executed at startup."""
    if not TOKEN:
        logger.warning(f"{Fore.YELLOW}✖ Skipping EmojiSync:{Style.RESET_ALL} No token found in .env files.")
        return

    emoji_py_path = os.path.join(BASE_DIR, "reo", "style", "emoji.py")
    try:
        with open(emoji_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as err:
        logger.error(f"{Fore.RED}✖ EmojiSync Failed:{Style.RESET_ALL} Could not read emoji.py {Fore.LIGHTBLACK_EX}({err}){Style.RESET_ALL}")
        return

    # Extract all custom discord emojis from the file
    matches = set(re.findall(r"<(a?):(\w+):(\d+)>", content))
    
    if not matches:
        logger.info(f"{Fore.CYAN}◈ EmojiSync:{Style.RESET_ALL} No custom emojis found in emoji.py to sync.")
        return

    logger.system(f"{Fore.MAGENTA}★ Starting Native Application Emoji Sync...{Style.RESET_ALL}")

    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }

    r = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
    if r.status_code != 200:
        logger.error(f"{Fore.RED}✖ EmojiSync API Error:{Style.RESET_ALL} Failed to fetch bot info {Fore.LIGHTBLACK_EX}[HTTP {r.status_code}]{Style.RESET_ALL}")
        return
    bot_info = r.json()
    app_id = bot_info.get("id")

    r = requests.get(f"https://discord.com/api/v10/applications/{app_id}/emojis", headers=headers)
    if r.status_code != 200:
        logger.error(f"{Fore.RED}✖ EmojiSync API Error:{Style.RESET_ALL} Failed to fetch application emojis {Fore.LIGHTBLACK_EX}[HTTP {r.status_code}]{Style.RESET_ALL}")
        return
    
    data = r.json()
    app_emojis = data.get("items", []) if isinstance(data, dict) else data

    logger.info(f"{Fore.CYAN}◈ Config Search:{Style.RESET_ALL} Found {Fore.YELLOW}{len(matches)}{Style.RESET_ALL} unique templates {Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} Application hosts {Fore.GREEN}{len(app_emojis)}{Style.RESET_ALL} App Emojis")

    updated = False
    skipped = 0
    uploaded = 0
    fixed = 0
    failed = 0

    for animated_str, name, old_id in matches:
        animated = (animated_str == 'a')
        
        existing = next((e for e in app_emojis if e['id'] == old_id), None) or next((e for e in app_emojis if e['name'] == name), None)

        if existing:
            new_id = existing['id']
            if old_id != new_id:
                old_str = f"<{animated_str}:{name}:{old_id}>"
                new_str = f"<{animated_str}:{existing['name']}:{new_id}>"
                content = content.replace(old_str, new_str)
                updated = True
                fixed += 1
                logger.warning(f"{Fore.YELLOW}↻ Auto-Fixing ID:{Style.RESET_ALL} {name} {Fore.LIGHTBLACK_EX}->{Style.RESET_ALL} {new_id}")
            else:
                skipped += 1
            continue

        logger.info(f"{Fore.BLUE}↑ Uploading:{Style.RESET_ALL} {name} {Fore.LIGHTBLACK_EX}(Not found on Discord){Style.RESET_ALL}")

        image_data = fetch_emoji_image(old_id, animated)
        if not image_data:
            logger.error(f"{Fore.RED}✖ Error Image Loading:{Style.RESET_ALL} {name} {Fore.LIGHTBLACK_EX}[ID: {old_id}]{Style.RESET_ALL}")
            failed += 1
            continue

        mime_type = "image/gif" if animated else "image/webp"
        base64_data = base64.b64encode(image_data).decode('utf-8')
        image_uri = f"data:{mime_type};base64,{base64_data}"

        post_data = {"name": name, "image": image_uri}
        r2 = requests.post(f"https://discord.com/api/v10/applications/{app_id}/emojis", headers=headers, json=post_data)
        
        if r2.status_code in (200, 201):
            new_emoji = r2.json()
            new_id = new_emoji['id']
            
            old_str = f"<{animated_str}:{name}:{old_id}>"
            new_str = f"<{animated_str}:{new_emoji['name']}:{new_id}>"
            content = content.replace(old_str, new_str)
            
            app_emojis.append(new_emoji)
            
            updated = True
            uploaded += 1
            logger.success(f"{Fore.GREEN}✔ Target Uploaded:{Style.RESET_ALL} {name} {Fore.LIGHTBLACK_EX}[Saved as ID: {new_id}]{Style.RESET_ALL}")
        else:
            logger.error(f"{Fore.RED}✖ Discord Rejected:{Style.RESET_ALL} {name} {Fore.LIGHTBLACK_EX}->{Style.RESET_ALL} {r2.text}")
            failed += 1

    if updated:
        try:
            with open(emoji_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.success(f"{Fore.MAGENTA}★ EmojiSync Snapshot Saved:{Style.RESET_ALL} Dynamically overwrote {Fore.YELLOW}emoji.py{Style.RESET_ALL} to reflect API state.")
        except Exception as err:
            logger.error(f"{Fore.RED}✖ Sync Write Blocked:{Style.RESET_ALL} Could not patch emoji.py {Fore.LIGHTBLACK_EX}({err}){Style.RESET_ALL}")

    summary_parts = []
    if skipped: summary_parts.append(f"{Fore.GREEN}{skipped} perfectly matching{Style.RESET_ALL}")
    if fixed: summary_parts.append(f"{Fore.YELLOW}{fixed} ID mismatches fixed{Style.RESET_ALL}")
    if uploaded: summary_parts.append(f"{Fore.CYAN}{uploaded} newly uploaded{Style.RESET_ALL}")
    if failed: summary_parts.append(f"{Fore.RED}{failed} download/upload failures{Style.RESET_ALL}")

    if summary_parts:
        logger.system(f"{Fore.MAGENTA}★ EmojiSync Completed:{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} ".join(summary_parts))

if __name__ == "__main__":
    run_sync()
