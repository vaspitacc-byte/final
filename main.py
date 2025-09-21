# main.py
import discord
from discord.ext import commands
import webserver  # start Flask server
from config import TOKEN, COMMAND_PREFIX

# Intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content

# Bot initialization
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# -------------------------
# LOAD MODULE COMMANDS
# -------------------------
extensions = [
    # Points commands
    "modules.points.admin_points",
    "modules.points.check_points",
    "modules.points.leaderboard",
    "modules.points.points_info",
    "modules.points.rank",

    # Rules commands
    "modules.rules.helper_rules",
    "modules.rules.proof_commands",
    "modules.rules.runner_rules",

    # Setup commands
    "modules.setup.custom_commands_setup",
    "modules.setup.role_setup",
    "modules.setup.setup_reset",

    # Tickets commands
    "modules.tickets.ticket_creation",
    "modules.tickets.ticket_modal",
    "modules.tickets.ticket_views",

    # Utils
    "modules.utils.help_commands",
    "modules.utils.talk",
]

for ext in extensions:
    try:
        bot.load_extension(ext)
        print(f"✅ Loaded {ext}")
    except Exception as e:
        print(f"❌ Failed to load {ext}: {e}")

# -------------------------
# EVENTS
# -------------------------
@bot.event
async def on_ready():
    print(f"🤖 {bot.user} is online and ready!")
    try:
        synced = await bot.tree.sync()  # Sync slash commands globally
        print(f"🔧 Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# -------------------------
# SIMPLE TEST COMMAND
# -------------------------
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# -------------------------
# RUN BOT
# -------------------------
if __name__ == "__main__":
    # Start Flask webserver for Railway healthcheck
    webserver.start_webserver()
    bot.run(TOKEN)
