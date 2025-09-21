from discord.ext import commands
from discord import app_commands
from database import DatabaseManager

db = DatabaseManager()

class SetupResetCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="resetsetup", description="Reset all server setup to defaults")
    @app_commands.default_permissions(administrator=True)
    async def slash_resetsetup(self, interaction):
        await db.update_server_config(interaction.guild.id,
                                      admin_role_id=None,
                                      staff_role_id=None,
                                      helper_role_id=None,
                                      viewer_role_id=None,
                                      blocked_role_id=None,
                                      reward_role_id=None,
                                      ticket_category_id=None,
                                      transcript_channel_id=None,
                                      requestor_points=0)
        await interaction.response.send_message("⚠️ Setup has been fully reset!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetupResetCog(bot))
