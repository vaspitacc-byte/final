import os

# ---------------- Bot Token ----------------
# Read the bot token from environment variable (set in Render dashboard)
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Bot token not found! Please set the TOKEN environment variable.")

# ---------------- Command Prefix ----------------
# Even though the bot uses slash commands (/), legacy prefix commands may still use this
COMMAND_PREFIX = "/"

# ---------------- Database Path ----------------
# Path to your SQLite database file (stored locally in the same folder as main.py)
DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")
