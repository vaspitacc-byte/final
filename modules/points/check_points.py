import discord
from discord.ext import commands
from discord import app_commands
from database import DatabaseManager

db = DatabaseManager()

class CheckPointsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # /points command
    @app_commands.command(name="points", description="Check points for yourself or another user")
    @app_commands.describe(member="The user to check points for (optional)")
    async def slash_points(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        points = await db.get_user_points(interaction.guild.id, member.id)
        await interaction.response.send_message(f"💰 {member.display_name} has {points} points.")

    # /mypoints command (alias, just for yourself)
    @app_commands.command(name="mypoints", description="See your own points")
    async def slash_mypoints(self, interaction: discord.Interaction):
        points = await db.get_user_points(interaction.guild.id, interaction.user.id)
        await interaction.response.send_message(f"💰 {interaction.user.display_name} has {points} points.")

async def setup(bot):
    await bot.add_cog(CheckPointsCog(bot))
