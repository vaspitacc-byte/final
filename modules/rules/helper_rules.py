import discord
from discord.ext import commands
from discord import Embed, app_commands
from database import DatabaseManager

db = DatabaseManager()

class HelperRulesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hrules", description="Display custom rules for helpers")
    async def slash_hrules(self, interaction: discord.Interaction):
        command_data = await db.get_custom_command(interaction.guild.id, "hrules")
        if not command_data:
            await interaction.response.send_message(
                "❌ Helper rules have not been configured. Use `/setup` to configure custom commands.",
                ephemeral=True
            )
            return

        embed = Embed(
            title="📋 Helper Rules",
            description=command_data['content'],
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelperRulesCog(bot))
