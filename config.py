# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Discord bot token
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not found in environment variables!")

# Bot command prefix (not really needed for slash commands, but kept for reference)
COMMAND_PREFIX = "/"  # Using "/" because your bot uses slash commands

# Database path
DB_PATH = os.getenv("DB_PATH", "ticket_bot.db")
