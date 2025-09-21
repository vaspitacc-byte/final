import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View
from discord import app_commands, Interaction
from database import DatabaseManager

db = DatabaseManager()

class CustomCommandModal(Modal):
    def __init__(self, command_name: str, existing_content: str = "", existing_image: str = ""):
        super().__init__(title=f"Setup {command_name} Command")
        self.command_name = command_name

        self.content_input = TextInput(
            label="Command Content", 
            placeholder="Enter content...", 
            default=existing_content, 
            style=discord.TextStyle.long, 
            max_length=2000
        )
        self.add_item(self.content_input)

        if command_name == "proof":
            self.image_input = TextInput(
                label="Image URL (Optional)", 
                placeholder="Image URL", 
                default=existing_image, 
                required=False
            )
            self.add_item(self.image_input)

    async def on_submit(self, interaction: Interaction):
        content = self.content_input.value
        image_url = getattr(self, 'image_input', None)
        image_url = image_url.value if image_url else ""
        await db.set_custom_command(interaction.guild.id, self.command_name, content, image_url)
        await interaction.response.send_message(f"✅ Custom command `{self.command_name}` configured!", ephemeral=True)

class CustomCommandView(View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Setup rrules", style=discord.ButtonStyle.primary, emoji="📜")
    async def setup_rrules(self, interaction: Interaction, button: discord.ui.Button):
        existing = await db.get_custom_command(interaction.guild.id, "rrules")
        content = existing['content'] if existing else ""
        await interaction.response.send_modal(CustomCommandModal("rrules", content))

    @discord.ui.button(label="Setup hrules", style=discord.ButtonStyle.primary, emoji="📋")
    async def setup_hrules(self, interaction: Interaction, button: discord.ui.Button):
        existing = await db.get_custom_command(interaction.guild.id, "hrules")
        content = existing['content'] if existing else ""
        await interaction.response.send_modal(CustomCommandModal("hrules", content))

    @discord.ui.button(label="Setup proof", style=discord.ButtonStyle.primary, emoji="📸")
    async def setup_proof(self, interaction: Interaction, button: discord.ui.Button):
        existing = await db.get_custom_command(interaction.guild.id, "proof")
        content = existing['content'] if existing else ""
        image = existing['image_url'] if existing else ""
        await interaction.response.send_modal(CustomCommandModal("proof", content, image))

class CustomCommandsSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setupcommands", description="Setup custom commands for helpers and runners")
    @app_commands.default_permissions(administrator=True)
    async def slash_setupcommands(self, interaction: Interaction):
        embed = discord.Embed(
            title="🛠️ Setup Custom Commands",
            description="Click the buttons below to configure custom commands:",
            color=discord.Color.blue()
        )
        embed.add_field(name="📜 rrules", value="Runner rules command", inline=True)
        embed.add_field(name="📋 hrules", value="Helper rules command", inline=True)
        embed.add_field(name="📸 proof", value="Proof submission command", inline=True)
        
        await interaction.response.send_message(embed=embed, view=CustomCommandView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(CustomCommandsSetupCog(bot))
