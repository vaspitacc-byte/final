import discord
from discord.ext import commands
from discord import app_commands, ui
from database import DatabaseManager

db = DatabaseManager()

class AdminPointsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Add points
    @app_commands.command(name="addpoints", description="Add points to a user (admin only)")
    @app_commands.describe(member="The user to add points to", amount="Amount of points to add")
    @app_commands.default_permissions(administrator=True)
    async def slash_addpoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await db.add_user_points(interaction.guild.id, member.id, amount)
        await interaction.response.send_message(f"✅ Added {amount} points to {member.display_name}.")

    # Remove points
    @app_commands.command(name="removepoints", description="Remove points from a user (admin only)")
    @app_commands.describe(member="The user to remove points from", amount="Amount of points to remove")
    @app_commands.default_permissions(administrator=True)
    async def slash_removepoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        current = await db.get_user_points(interaction.guild.id, member.id)
        new_total = max(current - amount, 0)
        await db.set_user_points(interaction.guild.id, member.id, new_total)
        await interaction.response.send_message(f"✅ Removed {amount} points from {member.display_name}. New total: {new_total}")

    # Set points
    @app_commands.command(name="setpoints", description="Set points for a user (admin only)")
    @app_commands.describe(member="The user to set points for", amount="Amount of points to set")
    @app_commands.default_permissions(administrator=True)
    async def slash_setpoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await db.set_user_points(interaction.guild.id, member.id, amount)
        await interaction.response.send_message(f"✅ Set {member.display_name}'s points to {amount}.")

    # Remove user
    @app_commands.command(name="removeuser", description="Remove a specific user from the leaderboard (admin only)")
    @app_commands.describe(member="The user to remove from leaderboard")
    @app_commands.default_permissions(administrator=True)
    async def slash_removeuser(self, interaction: discord.Interaction, member: discord.Member):
        await db.remove_user(interaction.guild.id, member.id)
        await interaction.response.send_message(f"✅ {member.display_name} has been removed from the leaderboard.")

    # Reset leaderboard
    @app_commands.command(name="resetlb", description="Reset the leaderboard with confirmation (admin only)")
    @app_commands.default_permissions(administrator=True)
    async def slash_resetlb(self, interaction: discord.Interaction):
        
        class Confirm(ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None

            @ui.button(label="Confirm Reset", style=discord.ButtonStyle.danger)
            async def confirm(self, button_interaction: discord.Interaction, button: ui.Button):
                await db.clear_all_points(interaction.guild.id)
                await button_interaction.response.edit_message(content="✅ Leaderboard has been reset!", view=None)
                self.value = True
                self.stop()

            @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel(self, button_interaction: discord.Interaction, button: ui.Button):
                await button_interaction.response.edit_message(content="❌ Leaderboard reset cancelled.", view=None)
                self.value = False
                self.stop()

        await interaction.response.send_message("⚠️ Are you sure you want to reset the leaderboard?", view=Confirm(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminPointsCog(bot))
