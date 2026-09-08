"""
The Grand Knox - Safehouse Claims & Incident Reporting System
Provides interactive modals and private ticket channels/threads for base claims,
grief reports, and administrative triage.
"""

import datetime
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
import config

# ==============================================================================
# MODALS FOR TICKET DATA INTAKE
# ==============================================================================
class SafehouseModal(discord.ui.Modal, title="🏡 Safehouse Base Claim Registration"):
    base_name = discord.ui.TextInput(
        label="Safehouse Designation / Name",
        placeholder="e.g., Cortman Medical Fort, Twiggy's Bar Compound",
        max_length=80,
        required=True
    )
    location = discord.ui.TextInput(
        label="Town & Coordinates (or Description)",
        placeholder="e.g., Muldraugh North Highway, 10600 x 9700",
        max_length=100,
        required=True
    )
    members = discord.ui.TextInput(
        label="Faction Members / Occupants",
        placeholder="List in-game survivor names who reside in this safehouse",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_session(
            interaction,
            ticket_type="Safehouse Claim",
            emoji="🏡",
            details={
                "Base Name": self.base_name.value,
                "Location": self.location.value,
                "Registered Occupants": self.members.value
            }
        )

class GriefReportModal(discord.ui.Modal, title="🚨 Report Rule Infraction / Griefing"):
    incident_type = discord.ui.TextInput(
        label="Nature of Violation",
        placeholder="e.g., Base Raiding, Stolen Armored Vehicle, Combat Logging",
        max_length=80,
        required=True
    )
    suspect = discord.ui.TextInput(
        label="Suspect Name (In-game / Discord)",
        placeholder="Enter known username, or 'Unknown Raider'",
        max_length=80,
        required=False
    )
    description = discord.ui.TextInput(
        label="Incident Description & Location",
        placeholder="Describe what occurred, time of event, coordinates, and any evidence links.",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_session(
            interaction,
            ticket_type="Grief Report",
            emoji="🚨",
            details={
                "Violation": self.incident_type.value,
                "Suspect": self.suspect.value or "Unidentified",
                "Incident Details": self.description.value
            }
        )

class SupportModal(discord.ui.Modal, title="❓ Survivor Technical Support"):
    subject = discord.ui.TextInput(
        label="Inquiry Subject",
        placeholder="e.g., Mod mismatch error, character desync, missing car keys",
        max_length=80,
        required=True
    )
    details = discord.ui.TextInput(
        label="Description of Issue",
        placeholder="Provide complete details so Marshals can assist you quickly.",
        style=discord.TextStyle.paragraph,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_session(
            interaction,
            ticket_type="Support Inquiry",
            emoji="❓",
            details={
                "Subject": self.subject.value,
                "Details": self.details.value
            }
        )

# ==============================================================================
# TICKET CREATION ENGINE
# ==============================================================================
async def create_ticket_session(interaction: discord.Interaction, ticket_type: str, emoji: str, details: dict):
    guild = interaction.guild
    user = interaction.user
    if not guild or not isinstance(user, discord.Member):
        return

    # Check for channel tickets
    claims_channel = discord.utils.get(guild.text_channels, name="🎫・tickets") or discord.utils.get(guild.text_channels, name="🎫・support-and-claims")
    target_channel = claims_channel or interaction.channel

    marshals_role = discord.utils.get(guild.roles, name="🛡️ Knox County Marshals")
    command_role = discord.utils.get(guild.roles, name="⚜️ Military High Command")

    # Clean channel/thread name
    clean_username = "".join(c for c in user.name.lower() if c.isalnum())[:12]
    ticket_title = f"{emoji}・{ticket_type.lower().replace(' ', '-')}-{clean_username}"

    # Defer response
    await interaction.response.defer(ephemeral=True)

    try:
        # Create private thread within the channel
        thread = await target_channel.create_thread(
            name=ticket_title,
            type=discord.ChannelType.private_thread,
            reason=f"Quarantine ticket opened by {user.name} ({ticket_type})"
        )

        # Add opener to thread
        await thread.add_user(user)

        # Build initial case embed
        embed = discord.Embed(
            title=f"{emoji} {ticket_type.upper()} — CASE FILE",
            description=(
                f"**Claimant / Reporter**: {user.mention} (`{user.name}`)\n"
                f"**Submitted**: <t:{int(datetime.datetime.now().timestamp())}:F>\n"
                f"**Status**: `Awaiting Marshal Inspection`\n\n"
                f"Staff members from {marshals_role.mention if marshals_role else 'Staff'} have been dispatched to review this dossier."
            ),
            color=config.KnoxColors.CORDON_RED if "Grief" in ticket_type else config.KnoxColors.PATROL_BLUE
        )

        for k, v in details.items():
            embed.add_field(name=f"📋 {k}", value=v, inline=False)

        embed.set_footer(text="The Grand Knox • Military Police Incident Triage")
        embed.set_thumbnail(url=user.display_avatar.url)

        # Send control view with Close Ticket button
        view = TicketControlView()
        await thread.send(
            content=f"{user.mention} {marshals_role.mention if marshals_role else ''}",
            embed=embed,
            view=view
        )

        # Notify user ephemerally
        await interaction.followup.send(
            f"✅ Your incident docket has been opened: {thread.mention}. Proceed there to converse with Marshals.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ Failed to initialize docket: {str(e)}", ephemeral=True)


class TicketCloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="CLOSE & ARCHIVE DOCKET",
            style=discord.ButtonStyle.danger,
            emoji="🔒",
            custom_id="grand_knox_close_ticket_btn"
        )

    async def callback(self, interaction: discord.Interaction):
        thread = interaction.channel
        guild = interaction.guild
        if not isinstance(thread, discord.Thread) or not guild:
            await interaction.response.send_message("This action can only be run inside a docket thread.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Archiving incident docket and compiling transcript...", ephemeral=False)

        # Compile message summary
        transcript_lines = []
        async for msg in thread.history(limit=100, oldest_first=True):
            author_tag = f"{msg.author.name}#{msg.author.discriminator}" if msg.author.discriminator != "0" else msg.author.name
            timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
            transcript_lines.append(f"[{timestamp}] {author_tag}: {msg.clean_content}")

        transcript_text = "\n".join(transcript_lines)
        if len(transcript_text) > 3500:
            transcript_text = transcript_text[:3500] + "\n... [Transcript truncated]"

        # Post to ticket logs archive
        archive_channel = discord.utils.get(guild.text_channels, name="🔒・ticket-logs") or discord.utils.get(guild.text_channels, name="🔒・transcripts-archive")
        if archive_channel:
            archive_embed = discord.Embed(
                title=f"🔒 RESOLVED DOCKET: {thread.name}",
                description=(
                    f"┃ **Closed By**: {interaction.user.mention}\n"
                    f"┃ **Closed At**: <t:{int(datetime.datetime.now().timestamp())}:F>\n"
                    f"┃ **Thread**: `#{thread.name}`\n\n"
                    f"**Docket Transcript Preview:**\n"
                    f"```text\n{transcript_text or 'No text messages recorded.'}\n```"
                ),
                color=config.KnoxColors.BUNKER_DARK
            )
            archive_embed.set_footer(text="The Grand Knox • Military Archive Registry")
            await archive_channel.send(embed=archive_embed)

        # Archive and lock thread
        await thread.edit(archived=True, locked=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCloseButton())

# ==============================================================================
# MAIN TICKET HUB VIEW (PERSISTENT BUTTONS IN #support-and-claims)
# ==============================================================================
class TicketHubView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim Safehouse", style=discord.ButtonStyle.primary, emoji="🏡", custom_id="gk_ticket_safehouse")
    async def safehouse_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SafehouseModal())

    @discord.ui.button(label="Report Griefing", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="gk_ticket_grief")
    async def grief_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(GriefReportModal())

    @discord.ui.button(label="Survivor Support", style=discord.ButtonStyle.secondary, emoji="❓", custom_id="gk_ticket_support")
    async def support_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SupportModal())

class TicketsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketsCog(bot))
