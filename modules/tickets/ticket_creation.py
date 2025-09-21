import discord
from discord.ext import commands
from discord import Embed
from database import DatabaseManager

db = DatabaseManager()

# Points and slots configuration
CATEGORY_POINTS = {
    "Ultra Speaker Express": 8,
    "Ultra Gramiel Express": 7,
    "4-Man Ultra Daily Express": 4,
    "7-Man Ultra Daily Express": 7,
    "Ultra Weekly Express": 12,
    "Grim Express": 10,
    "Daily Temple Express": 6
}

CATEGORY_SLOTS = {
    "Ultra Speaker Express": 3,
    "Ultra Gramiel Express": 3,
    "4-Man Ultra Daily Express": 3,
    "7-Man Ultra Daily Express": 6,
    "Ultra Weekly Express": 3,
    "Grim Express": 6,
    "Daily Temple Express": 3
}

CATEGORY_CHANNEL_NAMES = {
    "Ultra Speaker Express": "ultra-speaker",
    "Ultra Gramiel Express": "ultra-gramiel",
    "4-Man Ultra Daily Express": "4-man-daily",
    "7-Man Ultra Daily Express": "7-man-daily",
    "Ultra Weekly Express": "weekly-ultra",
    "Grim Express": "grimchallenge",
    "Daily Temple Express": "templeshrine"
}

from modules.tickets.ticket_views import TicketView
from modules.tickets.ticket_modal import TicketModal

class TicketCreationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CATEGORY_POINTS = CATEGORY_POINTS
        self.CATEGORY_SLOTS = CATEGORY_SLOTS
        self.CATEGORY_CHANNEL_NAMES = CATEGORY_CHANNEL_NAMES

    @commands.command(name="create")
    @commands.has_permissions(administrator=True)
    async def create_ticket_panel(self, ctx):
        """Create ticket selection panel"""
        embed = Embed(
            title="🎫 Create a Ticket",
            description="Select the type of ticket you want to create:",
            color=discord.Color.blue()
        )
        for category, points in CATEGORY_POINTS.items():
            slots = CATEGORY_SLOTS[category]
            embed.add_field(
                name=f"🎯 {category}",
                value=f"Points: {points} | Helpers: {slots}",
                inline=True
            )
        from discord.ui import View, Select
        class TicketSelect(Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label=c, value=c, emoji="🎫") 
                    for c in CATEGORY_POINTS.keys()
                ]
                super().__init__(placeholder="Choose a ticket type...", options=options)

            async def callback(self, interaction: discord.Interaction):
                modal = TicketModal(self.values[0], interaction.guild.id)
                await interaction.response.send_modal(modal)

        view = View()
        view.add_item(TicketSelect())
        await ctx.send(embed=embed, view=view)

    async def create_ticket(self, interaction, category, answers):
        """Create a ticket with category and modal answers"""
        guild_id = interaction.guild.id

        # Next ticket number
        ticket_number = await db.get_next_ticket_number(guild_id, category)
        channel_name = f"{self.CATEGORY_CHANNEL_NAMES[category]}-{ticket_number}"

        # Server config
        server_config = await db.get_server_config(guild_id)
        if not server_config or not server_config.get("ticket_category_id"):
            await interaction.followup.send("❌ Ticket category not configured! Use `/setup`.", ephemeral=True)
            return

        # Permissions
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        }
        # Staff/admin permissions
        if server_config.get("admin_role_id"):
            role = interaction.guild.get_role(server_config["admin_role_id"])
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)
        if server_config.get("staff_role_id"):
            role = interaction.guild.get_role(server_config["staff_role_id"])
            if role: overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        # Create channel
        category_channel = interaction.guild.get_channel(server_config["ticket_category_id"])
        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category_channel,
            overwrites=overwrites,
            reason=f"{category} ticket created by {interaction.user.display_name}"
        )

        # Ticket view
        slots = self.CATEGORY_SLOTS[category]
        ticket_view = TicketView(interaction.user, category, slots, guild_id, ticket_channel)

        # Embed
        embed = Embed(title=f"🎫 {category} Ticket #{ticket_number}", color=discord.Color.green())
        embed.add_field(name="👤 Created by", value=interaction.user.mention, inline=True)
        for k,v in answers.items():
            if v:
                embed.add_field(name=f"{k}", value=v, inline=True)
        helper_list = [f"{i+1}. [Empty]" for i in range(slots)]
        embed.add_field(name="👥 Helpers", value="\n".join(helper_list), inline=False)
        embed.add_field(name="🏆 Points Value", value=f"{self.CATEGORY_POINTS[category]} points", inline=True)

        await ticket_channel.send(f"Hello {interaction.user.mention}! Your **{category}** ticket has been created.", embed=embed, view=ticket_view)

        # Save ticket in DB
        await db.save_active_ticket(guild_id, ticket_channel.id, interaction.user.id, category, ticket_number)

        # Add points to requestor (from setup)
        requestor_points = server_config.get("requestor_points", 0)
        if requestor_points > 0:
            await db.add_user_points(guild_id, interaction.user.id, requestor_points)

        # Notify user
        await interaction.followup.send(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCreationCog(bot))
