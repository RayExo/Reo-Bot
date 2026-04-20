import datetime
import io
import os
import sys

import pyfiglet
import pytz
from colorama import Fore, Style, init

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

init(autoreset=True)
timezone = pytz.timezone("Asia/Kolkata")


class Logger:
    def __init__(self) -> None:
        os.makedirs("logs", exist_ok=True)
        stamp = datetime.datetime.now(timezone).strftime("%Y-%m-%d_%H-%M-%S")
        self.logging_file = f"logs/{stamp}.log"
        self.file = open(self.logging_file, "a", encoding="utf-8")
        self.banner()

    def banner(self):
        try:
            art = pyfiglet.figlet_format("REO", font="slant")
        except Exception:
            art = "REO"
        print(f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}{art}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}+{'-' * 78}+")
        print(
            f"{Fore.CYAN}| "
            f"{Fore.WHITE}{Style.BRIGHT}Name: Reo"
            f"{' ' * 14}"
            f"{Fore.LIGHTBLACK_EX}Credits"
            f"{Fore.WHITE}: CodeX Development"
            f"{' ' * 10}{Fore.CYAN}|"
        )
        print(f"{Fore.CYAN}+{'-' * 78}+{Style.RESET_ALL}\n")

    def startup_summary(self, bot):
        print(f"{Fore.LIGHTBLACK_EX}Session Snapshot")
        print(f"{Fore.BLUE}|- User   {Fore.WHITE}{bot.user}")
        print(f"{Fore.BLUE}|- ID     {Fore.WHITE}{bot.user.id}")
        print(f"{Fore.BLUE}|- Guilds {Fore.WHITE}{len(bot.guilds)}")
        print(f"{Fore.BLUE}|- Users  {Fore.WHITE}{sum(g.member_count or 0 for g in bot.guilds)}")
        print(f"{Fore.BLUE}|- Shards {Fore.WHITE}{bot.shard_count}\n")
        
    def web_startup_summary(self, bot):
        print(f"{Fore.LIGHTBLACK_EX}Web Dashboard Snapshot")
        print(f"{Fore.BLUE}|- Host   {Fore.WHITE}{bot.BotConfig.WEB_HOST}")
        print(f"{Fore.BLUE}|- Port   {Fore.WHITE}{bot.BotConfig.WEB_PORT}")
        print(f"{Fore.BLUE}|- URL    {Fore.WHITE}{bot.BotConfig.DASHBOARD_BASE_URL}")


    def _get_timestamp(self):
        return datetime.datetime.now(timezone).strftime("%H:%M:%S")

    def _clean_console_text(self, message) -> str:
        text = str(message)
        try:
            repaired = text.encode("latin1").decode("utf-8")
            weird_before = sum(text.count(token) for token in ("Ã", "â", "œ", "€"))
            weird_after = sum(repaired.count(token) for token in ("Ã", "â", "œ", "€"))
            if weird_after < weird_before:
                text = repaired
        except Exception:
            pass

        replacements = {
            "â€¢": "-",
            "•": "-",
            "âœ…": "[ok]",
            "✅": "[ok]",
            "âŒ": "[x]",
            "❌": "[x]",
            "âš ": "[!]",
            "⚠️": "[!]",
            "⚠": "[!]",
        }
        for source, target in replacements.items():
            text = text.replace(source, target)
        if any(token in text for token in ("Ã", "â", "œ", "€")):
            text = "".join(ch if ord(ch) < 128 else " " for ch in text)
            text = " ".join(text.split())
        return text

    def log(self, message, level="INFO", color=Fore.BLUE):
        message = self._clean_console_text(message)
        timestamp = self._get_timestamp()
        level_styles = {
            "INFO": f"{Fore.CYAN}info",
            "SUCCESS": f"{Fore.GREEN}pass",
            "WARNING": f"{Fore.YELLOW}warn",
            "ERROR": f"{Fore.RED}fail",
            "DATABASE": f"{Fore.MAGENTA}data",
            "STORAGE": f"{Fore.MAGENTA}data",
            "SURFACE": f"{Fore.LIGHTYELLOW_EX}edge",
            "COG": f"{Fore.LIGHTBLUE_EX}src",
            "SYSTEM": f"{Fore.LIGHTWHITE_EX}sys",
        }
        level_label = level_styles.get(level, f"{Fore.WHITE}{level.lower()}")
        console_entry = (
            f"{Style.DIM}{timestamp}{Style.RESET_ALL} "
            f"{Fore.LIGHTBLACK_EX}>{Style.RESET_ALL} "
            f"{Style.BRIGHT}{level_label:<7}{Style.RESET_ALL} "
            f"{Fore.LIGHTBLACK_EX}|{Style.RESET_ALL} "
            f"{color}{message}"
        )
        print(console_entry)
        self.file.write(f"[{timestamp}] [{level}] {message}\n")
        self.file.flush()

    def info(self, message):
        self.log(message, "INFO", Fore.LIGHTCYAN_EX)

    def success(self, message):
        self.log(message, "SUCCESS", Fore.GREEN)

    def warning(self, message):
        self.log(message, "WARNING", Fore.YELLOW)

    def error(self, message):
        self.log(message, "ERROR", Fore.RED)

    def database(self, message):
        self.log(message, "STORAGE", Fore.MAGENTA)

    def storage(self, message):
        self.log(message, "STORAGE", Fore.MAGENTA)

    def surface(self, message):
        self.log(message, "SURFACE", Fore.LIGHTYELLOW_EX)

    def cog(self, message):
        self.log(message, "COG", Fore.LIGHTBLUE_EX)

    def system(self, message):
        self.log(message, "SYSTEM", Fore.LIGHTWHITE_EX)

    def separator(self):
        print(f"{Fore.LIGHTBLACK_EX}{'- ' * 30}")

    def close(self):
        self.file.write(f"Log file closed at {datetime.datetime.now(timezone)}\n")
        self.file.close()


logger = Logger()
