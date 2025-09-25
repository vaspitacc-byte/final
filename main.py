# main.py
import discord
from discord.ext import commands
import webserver  # start Flask server (for Railway healthcheck)
from config import TOKEN, COMMAND_PREFIX
from database import db  # singleton from database.py

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

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

async def main():
    # Initialize database tables
    await db.initialize_database()

    async with bot:
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                print(f"✅ Loaded {ext}")
            except Exception as e:
                print(f"❌ Failed to load {ext}: {e}")

        # Start webserver (healthcheck)
        webserver.start_webserver()
        await bot.start(TOKEN)

@bot.event
async def on_ready():
    print(f"🤖 {bot.user} is online and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"🔧 Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
