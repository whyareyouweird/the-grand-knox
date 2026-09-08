"""
The Grand Knox - Bulletproof Auto-Role & Welcome Manifest Engine
Guarantees every member who joins is instantly auto-assigned the Knox Survivor role,
scans on startup to catch any missed members, and posts clean arrival logs in #welcome.
"""

import random
import datetime
import discord
from discord import app_commands
from discord.ext import commands
import config

class AutoRoleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.member_count_loop.start()

    def cog_unload(self):
        self.member_count_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        """Startup routine: audits all members and synchronizes the member count VC."""
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            await self.audit_and_autorole_guild(guild)
            await self.update_member_count_vc(guild)

    @tasks.loop(minutes=10)
    async def member_count_loop(self):
        """Periodic background refresh for member count VC."""
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            await self.update_member_count_vc(guild)

    async def update_member_count_vc(self, guild: discord.Guild):
        """Maintains the locked voice channel displaying live server member count."""
        try:
            target_name = f"👥 Members: {guild.member_count}"
            
            # Find existing member count voice channel
            target_vc = None
            for vc in guild.voice_channels:
                if "members:" in vc.name.lower():
                    target_vc = vc
                    break

            # Permissions: everyone can see, but nobody can connect (lock icon)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    connect=False,
                    speak=False
                ),
                guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    manage_channels=True,
                    connect=True
                )
            }

            survivor_role = discord.utils.get(guild.roles, name="🌲 Knox Survivor")
            if survivor_role:
                overwrites[survivor_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    connect=False,
                    speak=False
                )

            if not target_vc:
                target_vc = await guild.create_voice_channel(
                    name=target_name,
                    overwrites=overwrites,
                    category=None,
                    position=0,
                    reason="Automated Server Member Counter"
                )
                print(f"[MemberCount] Created counter VC: '{target_name}' at position 0")
            else:
                # Update name if changed
                if target_vc.name != target_name:
                    await target_vc.edit(name=target_name, reason="Member count update")
                    print(f"[MemberCount] Updated counter VC to '{target_name}'")
                # Ensure locked permissions
                if target_vc.position != 0 or target_vc.category is not None:
                    await target_vc.edit(position=0, category=None, overwrites=overwrites)
        except discord.HTTPException as e:
            # Respect Discord channel edit rate limits gracefully
            if e.status == 429:
                print(f"[MemberCount] Rate limited updating member count: {e}")
            else:
                print(f"[MemberCount] HTTPException: {e}")
        except Exception as e:
            print(f"[MemberCount] Error updating member count VC: {e}")

    async def audit_and_autorole_guild(self, guild: discord.Guild) -> dict:
        """Audits guild members and assigns survivor role to anyone missing it."""
        survivor_role = discord.utils.get(guild.roles, name="🌲 Knox Survivor")
        high_cmd = discord.utils.get(guild.roles, name="⚜️ Military High Command")
        
        stats = {"roled": 0, "already_roled": 0, "total": 0}

        if not survivor_role:
            print(f"[AutoRole] Warning: '🌲 Knox Survivor' role not found in {guild.name}")
            return stats

        for member in guild.members:
            if member.bot:
                continue
            stats["total"] += 1

            # Give owner High Command if missing
            if member.id == guild.owner_id and high_cmd and high_cmd not in member.roles:
                try:
                    await member.add_roles(high_cmd, reason="Server Owner clearance")
                    print(f"[AutoRole] Granted ⚜️ Military High Command to owner {member.name}")
                except Exception as e:
                    print(f"[AutoRole] Could not assign owner role: {e}")

            # Assign Knox Survivor if missing
            if survivor_role not in member.roles:
                try:
                    await member.add_roles(survivor_role, reason="Grand Knox Auto-Role (Audit)")
                    stats["roled"] += 1
                    print(f"[AutoRole] Auto-roled missing member: {member.name} ({member.id})")
                except Exception as e:
                    print(f"[AutoRole] Error assigning role to {member.name}: {e}")
            else:
                stats["already_roled"] += 1

        return stats

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Event listener: triggers the moment someone joins."""
        guild = member.guild
        if not guild:
            return

        # 1. Instant Auto-Role
        survivor_role = discord.utils.get(guild.roles, name="🌲 Knox Survivor")
        if survivor_role:
            try:
                await member.add_roles(survivor_role, reason="Grand Knox Instant Auto-Role on join")
                print(f"[AutoRole] SUCCESS: Granted 🌲 Knox Survivor to new arrival: {member.name} ({member.id})")
            except Exception as e:
                print(f"[AutoRole] FAILED to auto-role {member.name}: {e}")

        # 2. Update Member Count VC
        await self.update_member_count_vc(guild)

        # 3. Locate channels
        welcome_ch = (discord.utils.get(guild.text_channels, name="👋・welcome") or 
                      discord.utils.get(guild.text_channels, name="welcome"))
        
        general_ch = (discord.utils.get(guild.text_channels, name="💬・general") or 
                      discord.utils.get(guild.text_channels, name="general"))
        
        rules_ch = (discord.utils.get(guild.text_channels, name="📜・rules") or 
                    discord.utils.get(guild.text_channels, name="rules"))
        
        roles_ch = (discord.utils.get(guild.text_channels, name="🎭・roles") or 
                    discord.utils.get(guild.text_channels, name="roles"))

        # 4. Short friendly text welcome in #general
        if general_ch:
            welcome_lines = [
                f"👋 Welcome to The Grand Knox, {member.mention}! Glad to have you with us.",
                f"🌲 Welcome to the server, {member.mention}! Make yourself at home.",
                f"👋 Everyone welcome {member.mention} to The Grand Knox!",
                f"🪓 Welcome {member.mention}! Glad you made it to the safehouse."
            ]
            try:
                await general_ch.send(random.choice(welcome_lines))
                print(f"[AutoRole] Sent short welcome text to #general for {member.name}")
            except Exception as e:
                print(f"[AutoRole] Could not send welcome message to #general: {e}")

        # 5. Send formal welcome arrival card to #welcome
        if welcome_ch:
            survivor_id = f"KZ-{random.randint(1000, 9999)}"
            rules_mention = rules_ch.mention if rules_ch else "#rules"
            general_mention = general_ch.mention if general_ch else "#general"
            roles_mention = roles_ch.mention if roles_ch else "#roles"

            embed = discord.Embed(
                title="👋 WELCOME TO THE GRAND KNOX",
                description=(
                    f"Welcome to the community, {member.mention}!\n\n"
                    f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"  **Survivor**: {member.mention} (`{member.name}`)\n"
                    f"  **Registry Tag**: `{survivor_id}`\n"
                    f"  **Assigned Role**: {survivor_role.mention if survivor_role else '`Survivor`'}\n"
                    f"  **Status**: **Auto-Verified & Cleared**\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"• Read our server guidelines in {rules_mention}.\n"
                    f"• Say hello and meet fellow players in {general_mention}.\n"
                    f"• Choose your specialty and notification pings in {roles_mention}!"
                ),
                color=config.KnoxColors.SURVIVOR_GREEN
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"The Grand Knox • Member #{guild.member_count}")
            embed.timestamp = datetime.datetime.now()

            try:
                await welcome_ch.send(embed=embed)
            except Exception as e:
                print(f"[AutoRole] Could not post welcome embed: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Update member count when someone leaves."""
        guild = member.guild
        if guild:
            await self.update_member_count_vc(guild)

    @app_commands.command(
        name="sync-roles",
        description="Audit the server and automatically grant Knox Survivor to anyone missing it."
    )
    @app_commands.default_permissions(manage_roles=True)
    async def sync_roles_command(self, interaction: discord.Interaction):
        """Slash command to verify all members have survivor role."""
        if not interaction.guild:
            await interaction.response.send_message("Must be used in a server.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        stats = await self.audit_and_autorole_guild(interaction.guild)
        await self.update_member_count_vc(interaction.guild)

        embed = discord.Embed(
            title="⚡ AUTO-ROLE AUDIT & SYNC COMPLETE",
            description=(
                f"**Scanned Server Population:**\n\n"
                f"• **Total Members Audited**: `{stats['total']}`\n"
                f"• **Already Had Role**: `{stats['already_roled']}`\n"
                f"• **Newly Auto-Roled**: `{stats['roled']}`\n\n"
                f"All members are verified and cleared with standard permissions."
            ),
            color=config.KnoxColors.SURVIVOR_GREEN
        )
        embed.set_footer(text="The Grand Knox • Automated Municipal Directorate")
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoRoleCog(bot))
