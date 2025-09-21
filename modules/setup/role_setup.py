import discord
from discord.ext import commands
from discord import Embed, app_commands
import discord
from discord.ext import commands
from discord import Embed, app_commands
from discord.ui import View, Button, Modal, TextInput
from database import DatabaseManager

db = DatabaseManager()

class RoleChannelModal(Modal):
    def __init__(self):
        super().__init__(title="Set Role or Channel")

        self.role_type = TextInput(
            label="Type (admin/staff/helper/viewer/blocked/reward/ticket_category/transcript_channel/requestor_points)",
            placeholder="Type role, channel type, or requestor points...",
            required=True, 
            max_length=50
        )
        self.add_item(self.role_type)

        self.id_input = TextInput(
            label="ID or Value", 
            placeholder="Enter the ID or value here", 
            required=True
        )
        self.add_item(self.id_input)

    async def on_submit(self, interaction: discord.Interaction):
        field_type = self.role_type.value.lower()
        field_id = self.id_input.value

        role_fields = {
            "admin": "admin_role_id",
            "staff": "staff_role_id", 
            "helper": "helper_role_id",
            "viewer": "viewer_role_id",
            "blocked": "blocked_role_id",
            "reward": "reward_role_id"
        }

        channel_fields = {
            "ticket_category": "ticket_category_id",
            "transcript_channel": "transcript_channel_id"
        }

        if field_type in role_fields:
            await db.update_server_config(interaction.guild.id, **{role_fields[field_type]: int(field_id)})
        elif field_type in channel_fields:
            await db.update_server_config(interaction.guild.id, **{channel_fields[field_type]: int(field_id)})
        elif field_type == "requestor_points":
            value = int(field_id)
            if value < 0 or value > 999999:
                await interaction.response.send_message(
                    "❌ Requestor points must be between 0 and 999,999.", ephemeral=True
                )
                return
            await db.update_server_config(interaction.guild.id, requestor_points=value)
        else:
            await interaction.response.send_message("❌ Invalid type!", ephemeral=True)
            return

        await interaction.response.send_message(f"✅ `{field_type}` set to `{field_id}`.", ephemeral=True)

class SetupView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Set Roles/Channels", style=discord.ButtonStyle.primary)
    async def set_roles_channels(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RoleChannelModal())

    @discord.ui.button(label="Reset Setup", style=discord.ButtonStyle.danger)
    async def reset_setup(self, interaction: discord.Interaction, button: Button):
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
        await interaction.response.send_message("⚠️ Setup has been reset!", ephemeral=True)

class RoleSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Setup roles, channels, and requestor points")
    @app_commands.default_permissions(administrator=True)
    async def slash_setup(self, interaction: discord.Interaction):
        embed = Embed(
            title="Bot Setup",
            description="Use the buttons below to set roles/channels or reset setup.",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, view=SetupView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleSetupCog(bot))
