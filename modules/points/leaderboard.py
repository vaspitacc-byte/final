import discord
from discord.ext import commands
from discord import app_commands, ui
from database import DatabaseManager

db = DatabaseManager()

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show the leaderboard with pages")
    async def slash_leaderboard(self, interaction: discord.Interaction):
        """Slash command leaderboard with pagination"""
        all_points = await db.get_all_user_points(interaction.guild.id)
        if not all_points:
            await interaction.response.send_message("No points recorded yet.")
            return

        # Sort by points (descending)
        sorted_points = sorted(all_points.items(), key=lambda x: x[1], reverse=True)

        # Split into pages of 10 entries
        pages = []
        for i in range(0, len(sorted_points), 10):
            chunk = sorted_points[i:i+10]
            leaderboard = ""
            for rank, (user_id, points) in enumerate(chunk, start=i+1):
                member = interaction.guild.get_member(user_id)
                name = member.display_name if member else f"User ID {user_id}"
                leaderboard += f"{rank}. {name} — {points} points\n"
            embed = discord.Embed(
                title="🏆 Leaderboard 🏆",
                description=leaderboard,
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Page {len(pages)+1}/{(len(sorted_points)-1)//10+1}")
            pages.append(embed)

        # Simple paginator view
        class Paginator(ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.index = 0

            @ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
            async def previous(self, interaction2: discord.Interaction, button: ui.Button):
                self.index = (self.index - 1) % len(pages)
                await interaction2.response.edit_message(embed=pages[self.index], view=self)

            @ui.button(label="➡️", style=discord.ButtonStyle.secondary)
            async def next(self, interaction2: discord.Interaction, button: ui.Button):
                self.index = (self.index + 1) % len(pages)
                await interaction2.response.edit_message(embed=pages[self.index], view=self)

        await interaction.response.send_message(embed=pages[0], view=Paginator())

async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
