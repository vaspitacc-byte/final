import discord
from discord.ext import commands
from discord import Embed
from discord.ui import View, Button, Select, Modal, TextInput
from database import DatabaseManager
import asyncio

db = DatabaseManager()

# Category configuration
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

# -------------------- Ticket Modal --------------------
class TicketModal(Modal):
    def __init__(self, category: str, guild_id: int):
        super().__init__(title=f"{category} Ticket Form")
        self.category = category
        self.guild_id = guild_id

        self.in_game_name = TextInput(label="In-game Name", placeholder="Enter your in-game name", max_length=100)
        self.add_item(self.in_game_name)
        self.server_name = TextInput(label="Server Name", placeholder="Enter server name", max_length=100)
        self.add_item(self.server_name)
        self.room_number = TextInput(label="Room Number", placeholder="Enter room number", max_length=50)
        self.add_item(self.room_number)
        self.additional_info = TextInput(label="Additional Info (Optional)", placeholder="Extra info", max_length=500, required=False)
        self.add_item(self.additional_info)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        ticket_cog = interaction.client.get_cog("TicketCreationCog")
        if not ticket_cog:
            await interaction.followup.send("❌ Ticket system not available!", ephemeral=True)
            return

        answers = {
            "In-game Name": self.in_game_name.value,
            "Server Name": self.server_name.value,
            "Room Number": self.room_number.value,
            "Additional Info": self.additional_info.value if self.additional_info.value else None
        }
        await ticket_cog.create_ticket(interaction, self.category, answers)

# -------------------- Ticket View --------------------
class TicketView(View):
    def __init__(self, owner: discord.Member, category: str, slots: int, guild_id: int, channel: discord.TextChannel):
        super().__init__(timeout=None)
        self.owner = owner
        self.category = category
        self.slots = slots
        self.guild_id = guild_id
        self.channel = channel
        self.helpers = []

        self.add_item(JoinButton(self))
        self.add_item(LeaveButton(self))
        self.add_item(CloseButton(self))

    async def update_helpers_embed(self, interaction=None):
        message = interaction.message if interaction else await self.channel.fetch_message(self.channel.last_message.id)
        embed = message.embeds[0]
        helper_list = [f"{i+1}. {self.helpers[i].mention}" if i < len(self.helpers) else f"{i+1}. [Empty]" for i in range(self.slots)]
        for i, field in enumerate(embed.fields):
            if field.name == "👥 Helpers":
                embed.set_field_at(i, name="👥 Helpers", value="\n".join(helper_list), inline=False)
                break
        if interaction:
            await interaction.message.edit(embed=embed, view=self)
        else:
            await message.edit(embed=embed, view=self)

# -------------------- Buttons --------------------
class JoinButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Join as Helper", style=discord.ButtonStyle.success, emoji="🙋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user in self.ticket_view.helpers:
            await interaction.response.send_message("❌ Already helping!", ephemeral=True); return
        if len(self.ticket_view.helpers) >= self.ticket_view.slots:
            await interaction.response.send_message("❌ Ticket full!", ephemeral=True); return
        self.ticket_view.helpers.append(interaction.user)
        await self.ticket_view.channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        await db.update_ticket_helpers(self.ticket_view.guild_id, self.ticket_view.channel.id, [h.id for h in self.ticket_view.helpers])
        await self.ticket_view.update_helpers_embed(interaction)
        await interaction.response.send_message("✅ Joined as helper!", ephemeral=True)

class LeaveButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Leave Ticket", style=discord.ButtonStyle.secondary, emoji="👋")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.ticket_view.helpers:
            await interaction.response.send_message("❌ Not helping!", ephemeral=True); return
        self.ticket_view.helpers.remove(interaction.user)
        await self.ticket_view.channel.set_permissions(interaction.user, overwrite=None)
        await db.update_ticket_helpers(self.ticket_view.guild_id, self.ticket_view.channel.id, [h.id for h in self.ticket_view.helpers])
        await self.ticket_view.update_helpers_embed(interaction)
        await interaction.response.send_message("👋 You left the ticket.", ephemeral=True)

class CloseButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        config = await db.get_server_config(interaction.guild.id)
        is_owner = interaction.user == self.ticket_view.owner
        is_admin = interaction.user.guild_permissions.administrator
        is_staff = False
        if config:
            admin_role_id = config.get("admin_role_id")
            staff_role_id = config.get("staff_role_id")
            role_ids = [r.id for r in interaction.user.roles]
            if admin_role_id in role_ids: is_admin=True
            if staff_role_id in role_ids: is_staff=True
        if not (is_owner or is_admin or is_staff):
            await interaction.response.send_message("❌ Only owner/staff/admin can close!", ephemeral=True); return

        # Hide ticket from everyone
        await self.ticket_view.channel.set_permissions(interaction.guild.default_role, view_channel=False)
        for h in self.ticket_view.helpers:
            await self.ticket_view.channel.set_permissions(h, view_channel=False)
        await self.ticket_view.channel.set_permissions(self.ticket_view.owner, view_channel=False)

        # Add Delete button for staff/admin
        delete_view = View(timeout=None)
        delete_view.add_item(DeleteTicketButton(self.ticket_view))
        await interaction.response.send_message("🔒 Ticket closed. Staff/admin can delete it.", view=delete_view, ephemeral=True)

# -------------------- Delete Ticket --------------------
class DeleteTicketButton(Button):
    def __init__(self, ticket_view: TicketView):
        super().__init__(label="Delete Ticket", style=discord.ButtonStyle.danger, emoji="🗑️")
        self.ticket_view = ticket_view

    async def callback(self, interaction: discord.Interaction):
        config = await db.get_server_config(interaction.guild.id)
        is_admin = interaction.user.guild_permissions.administrator
        is_staff = False
        role_ids = [r.id for r in interaction.user.roles]
        if config:
            admin_role_id = config.get("admin_role_id")
            staff_role_id = config.get("staff_role_id")
            if admin_role_id in role_ids: is_admin=True
            if staff_role_id in role_ids: is_staff=True
        if not (is_admin or is_staff):
            await interaction.response.send_message("❌ Only staff/admin can delete!", ephemeral=True); return

        # Ask if helpers should be rewarded
        reward_view = RewardChoiceView(self.ticket_view)
        await interaction.response.send_message("💰 Reward helpers?", view=reward_view, ephemeral=True)

# -------------------- Reward Choice --------------------
class RewardChoiceView(View):
    def __init__(self, ticket_view: TicketView):
        super().__init__(timeout=60)
        self.ticket_view = ticket_view

    @discord.ui.button(label="Yes, Reward", style=discord.ButtonStyle.success)
    async def reward(self, interaction: discord.Interaction, button: Button):
        points = CATEGORY_POINTS.get(self.ticket_view.category, 0)
        for helper in self.ticket_view.helpers:
            await db.add_user_points(self.ticket_view.guild_id, helper.id, points)
        await self.finalize(interaction, rewarded=True)

    @discord.ui.button(label="No Reward", style=discord.ButtonStyle.secondary)
    async def no_reward(self, interaction: discord.Interaction, button: Button):
        await self.finalize(interaction, rewarded=False)

    async def finalize(self, interaction, rewarded: bool):
        await save_transcript(self.ticket_view, interaction.user, rewarded)
        await db.remove_active_ticket(self.ticket_view.guild_id, self.ticket_view.channel.id)
        await self.ticket_view.channel.delete(reason=f"Deleted by {interaction.user.display_name}")
        await interaction.response.send_message("✅ Ticket deleted.", ephemeral=True)

# -------------------- Transcript --------------------
async def save_transcript(ticket_view: TicketView, closed_by: discord.Member, rewarded: bool):
    config = await db.get_server_config(ticket_view.guild_id)
    transcript_channel_id = config.get("transcript_channel_id") if config else None
    if not transcript_channel_id: return
    transcript_channel = ticket_view.channel.guild.get_channel(transcript_channel_id)
    if not transcript_channel: return

    messages = []
    async for m in ticket_view.channel.history(limit=None, oldest_first=True):
        content = m.content or "[No text content]"
        timestamp = m.created_at.strftime('%Y-%m-%d %H:%M:%S')
        messages.append(f"[{timestamp}] {m.author.display_name}: {content}")
        for att in m.attachments:
            messages.append(f"📎 {att.filename}")
    transcript_file = discord.File(fp=discord.utils.BytesIO("\n".join(messages).encode('utf-8')), filename=f"transcript-{ticket_view.channel.name}.txt")

    embed = Embed(title=f"📄 Ticket Transcript: {ticket_view.category}", color=discord.Color.red())
    embed.add_field(name="Ticket Owner", value=ticket_view.owner.mention, inline=True)
    embed.add_field(name="Closed By", value=closed_by.mention, inline=True)
    embed.add_field(name="Helpers", value=f"{len(ticket_view.helpers)}", inline=True)
    embed.add_field(name="Rewarded", value="Yes" if rewarded else "No", inline=True)
    await transcript_channel.send(embed=embed, file=transcript_file)

# -------------------- Ticket Creation Cog --------------------
class TicketCreationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CATEGORY_POINTS = CATEGORY_POINTS
        self.CATEGORY_SLOTS = CATEGORY_SLOTS
        self.CATEGORY_CHANNEL_NAMES = CATEGORY_CHANNEL_NAMES

    @commands.command(name="create")
    @commands.has_permissions(administrator=True)
    async def create_ticket_panel(self, ctx):
        embed = Embed(title="🎫 Create a Ticket", description="Select the type of ticket:", color=discord.Color.blue())
        for cat, pts in CATEGORY_POINTS.items():
            slots = CATEGORY_SLOTS[cat]
            embed.add_field(name=f"🎯 {cat}", value=f"Points: {pts} | Helpers: {slots}", inline=True)
        await ctx.send(embed=embed, view=TicketSelectView())

    async def create_ticket(self, interaction, category, answers):
        guild_id = interaction.guild.id
        ticket_number = await db.get_next_ticket_number(guild_id, category)
        channel_name = f"{CATEGORY_CHANNEL_NAMES[category]}-{ticket_number}"
        server_config = await db.get_server_config(guild_id)
        if not server_config or not server_config.get("ticket_category_id"):
            await interaction.followup.send("❌ Ticket category not configured!", ephemeral=True)
            return

        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                      interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                      interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)}

        for r_id in [server_config.get("admin_role_id"), server_config.get("staff_role_id")]:
            if r_id:
                role = interaction.guild.get_role(r_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        category_channel = interaction.guild.get_channel(server_config["ticket_category_id"])
        ticket_channel = await interaction.guild.create_text_channel(name=channel_name, category=category_channel, overwrites=overwrites)

        slots = CATEGORY_SLOTS[category]
        ticket_view = TicketView(interaction.user, category, slots, guild_id, ticket_channel)

        embed = Embed(title=f"🎫 {category} Ticket #{ticket_number}", color=discord.Color.green())
        embed.add_field(name="👤 Created by", value=interaction.user.mention)
        for k, v in answers.items():
            if v: embed.add_field(name=k, value=v)
        helper_list = [f"{i+1}. [Empty]" for i in range(slots)]
        embed.add_field(name="👥 Helpers", value="\n".join(helper_list))
        embed.add_field(name="🏆 Points Value", value=f"{CATEGORY_POINTS[category]} points")

        await ticket_channel.send(f"Hello {interaction.user.mention}! Your **{category}** ticket has been created.", embed=embed, view=ticket_view)
        await db.save_active_ticket(guild_id, ticket_channel.id, interaction.user.id, category, ticket_number)

# -------------------- Ticket Selection View --------------------
class TicketSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)
        options = [discord.SelectOption(label=c, value=c, emoji="🎫") for c in CATEGORY_POINTS.keys()]
        self.add_item(TicketSelect(options))

class TicketSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Choose a ticket type...", options=options)

    async def callback(self, interaction: discord.Interaction):
        from ticket_modal_module import TicketModal  # import your TicketModal file here
        modal = TicketModal(self.values[0], interaction.guild.id)
        await interaction.response.send_modal(modal)

# -------------------- Setup Cog --------------------
async def setup(bot):
    await bot.add_cog(TicketCreationCog(bot))
