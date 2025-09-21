import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class TalkCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="say",
        description="Send a message as the bot to a selected channel or thread"
    )
    @app_commands.describe(
        channel="Select the channel or thread to send the message",
        content="The message text to send",
        attachments="Optional attachment URLs (comma-separated)"
    )
    async def slash_say(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        content: Optional[str] = None,
        attachments: Optional[str] = None
    ):
        """Slash command to let staff/admins make the bot speak anywhere"""

        # Permission check
        config = await self.bot.db.get_server_config(interaction.guild.id)
        is_admin = interaction.user.guild_permissions.administrator
        is_staff = False
        if config:
            admin_role_id = config.get("admin_role_id")
            staff_role_id = config.get("staff_role_id")
            user_role_ids = [role.id for role in interaction.user.roles]
            if admin_role_id and admin_role_id in user_role_ids:
                is_admin = True
            if staff_role_id and staff_role_id in user_role_ids:
                is_staff = True

        if not (is_admin or is_staff):
            await interaction.response.send_message(
                "❌ Only staff/admins can use this command!", ephemeral=True
            )
            return

        # Process attachments
        files = []
        if attachments:
            urls = [url.strip() for url in attachments.split(",")]
            for url in urls:
                try:
                    files.append(discord.File(fp=url, filename=url.split("/")[-1]))
                except Exception:
                    continue

        if not content and not files:
            await interaction.response.send_message(
                "❌ You must provide some text or at least one attachment!", ephemeral=True
            )
            return

        try:
            await channel.send(content=content, files=files if files else None)
            await interaction.response.send_message(
                f"✅ Message sent to {channel.mention}", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to send message: {e}", ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(TalkCog(bot))
