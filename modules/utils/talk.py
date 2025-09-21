import discord
from discord import app_commands, File, Embed, Color
from discord.ext import commands
from discord.ui import Modal, TextInput, View, Button
from typing import List, Optional
import io

class TalkContentModal(Modal):
    def __init__(self):
        super().__init__(title="Talk Command - Message Content")
        self.text_input = TextInput(
            label="Message Text (optional)", 
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=2000,
            placeholder="Enter the message content"
        )
        self.add_item(self.text_input)

        self.embed_title = TextInput(
            label="Embed Title (optional)", 
            style=discord.TextStyle.short,
            required=False,
            max_length=256,
            placeholder="Embed title"
        )
        self.add_item(self.embed_title)

        self.embed_desc = TextInput(
            label="Embed Description (optional)", 
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000,
            placeholder="Embed description"
        )
        self.add_item(self.embed_desc)

        self.embed_color = TextInput(
            label="Embed Color (hex, e.g. #00ff00, optional)", 
            style=discord.TextStyle.short,
            required=False,
            max_length=7,
            placeholder="#00ff00"
        )
        self.add_item(self.embed_color)

    async def on_submit(self, interaction: discord.Interaction):
        # Store user inputs
        interaction.client.talk_data = {
            "text": self.text_input.value,
            "embed_title": self.embed_title.value,
            "embed_desc": self.embed_desc.value,
            "embed_color": self.embed_color.value
        }

        # Show preview
        embed = None
        if self.embed_title.value or self.embed_desc.value:
            color = None
            try:
                color = Color(int(self.embed_color.value.strip("#"), 16))
            except Exception:
                color = Color.blue()
            embed = Embed(
                title=self.embed_title.value if self.embed_title.value else None,
                description=self.embed_desc.value if self.embed_desc.value else None,
                color=color
            )

        view = TalkConfirmView(interaction.client)
        await interaction.response.send_message(
            content=self.text_input.value if self.text_input.value else None,
            embed=embed,
            view=view,
            ephemeral=True
        )

class TalkConfirmView(View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Send", style=discord.ButtonStyle.green)
    async def send_button(self, interaction: discord.Interaction, button: Button):
        data = self.bot.talk_data

        # Channel selection
        channel: Optional[discord.TextChannel] = getattr(self.bot, "talk_channel", None)
        if not channel:
            await interaction.followup.send("❌ Channel not selected!", ephemeral=True)
            return

        # Prepare embed if any
        embed = None
        if data["embed_title"] or data["embed_desc"]:
            color = Color.blue()
            try:
                color = Color(int(data["embed_color"].strip("#"), 16))
            except Exception:
                pass
            embed = Embed(
                title=data["embed_title"] if data["embed_title"] else None,
                description=data["embed_desc"] if data["embed_desc"] else None,
                color=color
            )

        # Send the message
        await channel.send(content=data["text"] if data["text"] else None, embed=embed)
        await interaction.followup.send(f"✅ Message sent to {channel.mention}", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("❌ Message sending cancelled.", ephemeral=True)
        self.stop()

class TalkSelectChannel(app_commands.Choice):
    pass  # Optional for later dynamic selection

class TalkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.talk_data = {}
        self.bot.talk_channel = None

    @app_commands.command(name="talk", description="Send a custom message with embed preview")
    @app_commands.describe(channel="Select the channel or thread to send the message")
    async def talk(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.bot.talk_channel = channel
        await interaction.response.send_modal(TalkContentModal())

async def setup(bot):
    await bot.add_cog(TalkCog(bot))
