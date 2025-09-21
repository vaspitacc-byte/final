import discord
from discord.ext import commands
from discord import Embed, app_commands
from database import DatabaseManager

db = DatabaseManager()

class RunnerRulesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rrules", description="Display custom rules for runners")
    async def slash_rrules(self, interaction: discord.Interaction):
        command_data = await db.get_custom_command(interaction.guild.id, "rrules")
        if not command_data:
            await interaction.response.send_message(
                "❌ Runner rules have not been configured. Use `/setup` to configure custom commands.",
                ephemeral=True
            )
            return
        
        embed = Embed(
            title="📜 Runner Rules",
            description=command_data['content'],
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(RunnerRulesCog(bot))
