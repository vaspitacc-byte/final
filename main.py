# main.py
import discord
from discord.ext import commands
import os
import asyncio
import webserver  # start Flask server
from config import TOKEN, COMMAND_PREFIX
from modules import points, rules, setup, tickets, utils

# Intents
intents = discord.Intents.default()
intents.message_content = True  # Required if you read message content

# Bot initialization
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# -------------------------
# LOAD MODULE COMMANDS
# -------------------------
# Points commands
bot.load_extension("modules.points.admin_points")
bot.load_extension("modules.points.check_points")
bot.load_extension("modules.points.leaderboard")
bot.load_extension("modules.points.points_info")
bot.load_extension("modules.points.rank")

# Rules commands
bot.load_extension("modules.rules.helper_rules")
bot.load_extension("modules.rules.proof_commands")
bot.load_extension("modules.rules.runner_rules")

# Setup commands
bot.load_extension("modules.setup.custom_commands_setup")
bot.load_extension("modules.setup.role_setup")
bot.load_extension("modules.setup.setup_reset")

# Tickets commands
bot.load_extension("modules.tickets.ticket_creation")
bot.load_extension("modules.tickets.ticket_modal")
bot.load_extension("modules.tickets.ticket_views")

# Utils
bot.load_extension("modules.utils.help_commands")
bot.load_extension("modules.utils.talk")

# -------------------------
# Events
# -------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

# Example simple command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# -------------------------
# RUN BOT
# -------------------------
bot.run(TOKEN)
