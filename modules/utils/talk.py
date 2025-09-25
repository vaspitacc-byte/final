# talk.py
import discord
from discord.ext import commands
from discord import app_commands, Embed, Color
from discord.ui import Modal, TextInput, View, Button
from typing import Optional
import aiohttp
import io

class TalkContentModal(Modal):
    def __init__(self):
        super().__init__(title="Talk Command - Message Content")
        self.text_input = TextInput(label="Message Text (optional)", style=discord.TextStyle.paragraph, required=False, max_length=2000)
        self.add_item(self.text_input)
        self.embed_title = TextInput(label="Embed Title (optional)", style=discord.TextStyle.short, required=False, max_length=256)
        self.add_item(self.embed_title)
        self.embed_desc = TextInput(label="Embed Description (optional)", style=discord.TextStyle.paragraph, required=False, max_length=4000)
        self.add_item(self.embed_desc)
        self.embed_color = TextInput(label="Embed Color (hex, e.g. #00ff00, optional)", style=discord.TextStyle.short, required=False, max_length=7)
        self.add_item(self.embed_color)
        self.attachments_input = TextInput(label="Attachment URLs (comma-separated, optional)", style=discord.TextStyle.paragraph, required=False, max_length=2000)
        self.add_item(self.attachments_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        bot = interaction.client
        # Store user-specific talk data
        if not hasattr(bot, "talk_data"):
            bot.talk_data = {}
        bot.talk_data[user_id] = {
            "text": self.text_input.value,
            "embed_title": self.embed_title.value,
            "embed_desc": self.embed_desc.value,
            "embed_color": self.embed_color.value,
            "attachments": self.attachments_input.value.split(",") if self.attachments_input.value else []
        }

        # Prepare embed preview
        embed = None
        if self.embed_title.value or self.embed_desc.value:
            color = Color.blue()
            try:
                color = Color(int(self.embed_color.value.strip("#"), 16))
            except Exception:
                pass
            embed = Embed(title=self.embed_title.value or None, description=self.embed_desc.value or None, color=color)

        await interaction.response.send_message(content=self.text_input.value or None, embed=embed, ephemeral=True, view=TalkConfirmView(bot, user_id))

class TalkConfirmView(View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id

    @discord.ui.button(label="Send", style=discord.ButtonStyle.green)
    async def send_button(self, interaction: discord.Interaction, button: Button):
        data = self.bot.talk_data.get(self.user_id)
        if not data:
            await interaction.response.send_message("❌ Data missing!", ephemeral=True)
            return

        channel: Optional[discord.TextChannel] = getattr(self.bot, "talk_channel", None)
        if not channel:
            await interaction.response.send_message("❌ Channel not selected!", ephemeral=True)
            return

        # Process attachments from URLs
        files = []
        async with aiohttp.ClientSession() as session:
            for url in data["attachments"]:
                url = url.strip()
                if not url:
                    continue
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            file_bytes = await resp.read()
                            files.append(discord.File(io.BytesIO(file_bytes), filename=url.split("/")[-1]))
                except:
                    continue

        # Prepare embed
        embed = None
        if data["embed_title"] or data["embed_desc"]:
            color = Color.blue()
            try:
                color = Color(int(data["embed_color"].strip("#"), 16))
            except:
                pass
            embed = Embed(title=data["embed_title"] or None, description=data["embed_desc"] or None, color=color)

        # Send the message
        await channel.send(content=data["text"] or None, embed=embed, files=files if files else None)
        await interaction.response.send_message(f"✅ Message sent to {channel.mention}", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("❌ Message sending cancelled.", ephemeral=True)
        self.stop()

class TalkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.talk_data = {}
        self.bot.talk_channel = None

    @app_commands.command(name="talk", description="Send a custom message with embed preview")
    @app_commands.describe(channel="Select the channel to send the message")
    async def talk(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.bot.talk_channel = channel
        await interaction.response.send_modal(TalkContentModal())

async def setup(bot):
    await bot.add_cog(TalkCog(bot))
