import discord
from discord.ext import commands
from discord import app_commands
from database import DatabaseManager

db = DatabaseManager()

class RankCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="myrank", description="Show your current rank in the leaderboard")
    async def slash_myrank(self, interaction: discord.Interaction):
        """Slash command to show your leaderboard rank"""
        all_points = await db.get_all_user_points(interaction.guild.id)
        if not all_points:
            await interaction.response.send_message("📊 The leaderboard is currently empty.", ephemeral=True)
            return

        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)
        for i, (user_id, points) in enumerate(sorted_points, start=1):
            if user_id == interaction.user.id:
                await interaction.response.send_message(
                    f"📊 {interaction.user.display_name}, your rank is #{i} with {points} points.",
                    ephemeral=True
                )
                return

        # If user not found in leaderboard
        await interaction.response.send_message(
            f"📊 {interaction.user.display_name}, you have 0 points and are not on the leaderboard.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(RankCog(bot))
