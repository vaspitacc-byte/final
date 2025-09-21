import discord
from discord.ext import commands
from discord import Embed, app_commands
from database import DatabaseManager

db = DatabaseManager()

class ProofCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="proof", description="Display proof submission instructions")
    async def slash_proof(self, interaction: discord.Interaction):
        command_data = await db.get_custom_command(interaction.guild.id, "proof")
        if not command_data:
            await interaction.response.send_message(
                "❌ Proof instructions have not been configured. Use `/setup` to configure custom commands.",
                ephemeral=True
            )
            return
        
        embed = Embed(
            title="📸 Proof Submission",
            description=command_data['content'],
            color=discord.Color.gold()
        )
        
        if command_data.get('image_url'):
            embed.set_image(url=command_data['image_url'])
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProofCommandsCog(bot))
