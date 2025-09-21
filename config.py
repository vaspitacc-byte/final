# config.py
import os

# Discord bot token from environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables!")

# Bot command prefix (slash commands)
COMMAND_PREFIX = "/"  

# Database path
DB_PATH = os.getenv("DB_PATH", "ticket_bot.db")
