import discord
from discord.ext import commands
from discord import app_commands
from database import DatabaseManager

db = DatabaseManager()

class PointsInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="history", description="Show a user's points history")
    @app_commands.describe(member="The user to view history for")
    async def slash_history(self, interaction: discord.Interaction, member: discord.Member = None):
        """Show a user's points history (currently only shows current points)"""
        member = member or interaction.user
        points = await db.get_user_points(interaction.guild.id, member.id)
        # TODO: Extend DB to track full history
        await interaction.response.send_message(
            f"📜 {member.display_name} has {points} points (history tracking not yet implemented).",
            ephemeral=True
        )

    @app_commands.command(name="pointsinfo", description="Explain the points system")
    async def slash_pointsinfo(self, interaction: discord.Interaction):
        """Explain how points work in the server"""
        info = (
            "💠 **Points System Info** 💠\n"
            "- Users earn points for completing tasks.\n"
            "- Admins can add, remove, or set points using `/addpoints`, `/removepoints`, `/setpoints`.\n"
            "- Check your points with `/history`.\n"
            "- See top users with `/leaderboard`.\n"
            "- Reset the leaderboard with `/resetlb` (admin only).\n"
            "- Remove users from the leaderboard with `/removeuser` (admin only)."
        )
        await interaction.response.send_message(info, ephemeral=True)


async def setup(bot):
    await bot.add_cog(PointsInfoCog(bot))
