import os

# Discord bot token from Railway environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not found!")

# Bot command prefix (for reference; not needed for slash commands)
COMMAND_PREFIX = "/"  

# Database path from Railway environment variables (optional)
DB_PATH = os.getenv("DB_PATH", "ticket_bot.db")
