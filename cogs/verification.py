"""
The Grand Knox - Bulletproof Auto-Role & Welcome Manifest Engine
Guarantees every member who joins is instantly auto-assigned the Knox Survivor role,
scans on startup to catch any missed members, and posts clean arrival logs in #welcome.
"""

import random
import datetime
import discord
from discord import app_commands
from discord.ext import commands, tasks
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
                edit_kwargs = {}
                if target_vc.name != target_name:
                    edit_kwargs["name"] = target_name
                if target_vc.position != 0 or target_vc.category is not None:
                    edit_kwargs["position"] = 0
                    edit_kwargs["category"] = None
                    edit_kwargs["overwrites"] = overwrites
                if edit_kwargs:
                    await target_vc.edit(**edit_kwargs, reason="Member count update")
                    print(f"[MemberCount] Updated counter VC: {target_name}")
        except discord.HTTPException as e:
            # Respect Discord channel edit rate limits gracefully
            if e.status == 429:
                print(f"[MemberCount] Rate limited updating member count: {e}")
            else:
                print(f"[MemberCount] HTTPException: {e}")
        except Exception as e:
            print(f"[MemberCount] Error updating member count VC: {e}")

    async def sync_member_dividers(self, member: discord.Member):
        """Automatically assigns or removes visual divider roles based on member's active roles."""
        if member.bot:
            return
        guild = member.guild
        current_role_names = {r.name for r in member.roles}

        roles_to_add = []
        roles_to_remove = []

        for divider_name, category_roles in config.DIVIDER_MAPPING.items():
            divider_obj = discord.utils.get(guild.roles, name=divider_name)
            if not divider_obj:
                continue

            has_category_role = any(r in current_role_names for r in category_roles)
            has_divider = divider_name in current_role_names

            if has_category_role and not has_divider:
                roles_to_add.append(divider_obj)
            elif not has_category_role and has_divider:
                roles_to_remove.append(divider_obj)

        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add, reason="Auto-assign category dividers")
                print(f"[Dividers] Added {[r.name for r in roles_to_add]} to {member.name}")
            except Exception as e:
                print(f"[Dividers] Error adding dividers to {member.name}: {e}")

        if roles_to_remove:
            try:
                await member.remove_roles(*roles_to_remove, reason="Remove unused category dividers")
                print(f"[Dividers] Removed {[r.name for r in roles_to_remove]} from {member.name}")
            except Exception as e:
                print(f"[Dividers] Error removing dividers from {member.name}: {e}")

    async def audit_and_autorole_guild(self, guild: discord.Guild) -> dict:
        """Audits guild members, assigns survivor role, and synchronizes dividers."""
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

            # Automatically sync category dividers for this member
            await self.sync_member_dividers(member)

        return stats

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Automatically adjusts divider roles whenever a member's roles change."""
        if before.roles != after.roles:
            await self.sync_member_dividers(after)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Event listener: triggers the moment someone joins."""
        guild = member.guild
        if not guild:
            return

        # 1. Instant Auto-Role & Category Dividers
        survivor_role = discord.utils.get(guild.roles, name="🌲 Knox Survivor")
        if survivor_role:
            try:
                await member.add_roles(survivor_role, reason="Grand Knox Instant Auto-Role on join")
                print(f"[AutoRole] SUCCESS: Granted 🌲 Knox Survivor to new arrival: {member.name} ({member.id})")
            except Exception as e:
                print(f"[AutoRole] FAILED to auto-role {member.name}: {e}")

        # Automatically grant Survivor Tiers divider
        await self.sync_member_dividers(member)

        # 2. Update Member Count VC
        await self.update_member_count_vc(guild)

        # 3. Locate channels for quick guide
        general_ch = (discord.utils.get(guild.text_channels, name="💬・general") or 
                      discord.utils.get(guild.text_channels, name="general"))
        
        rules_ch = (discord.utils.get(guild.text_channels, name="📜・rules") or 
                    discord.utils.get(guild.text_channels, name="rules"))
        
        roles_ch = (discord.utils.get(guild.text_channels, name="🎭・roles") or 
                    discord.utils.get(guild.text_channels, name="roles"))

        status_ch = (discord.utils.get(guild.text_channels, name="🟢・server-status") or 
                     discord.utils.get(guild.text_channels, name="server-status"))

        # 4. Greet new arrival directly in #general with quick server guide
        if general_ch:
            rules_ref = rules_ch.mention if rules_ch else "#rules"
            roles_ref = roles_ch.mention if roles_ch else "#roles"
            status_ref = status_ch.mention if status_ch else "#server-status"

            welcome_msg = (
                f"👋 Welcome {member.mention} to The Grand Knox! You are survivor #{guild.member_count}.\n"
                f"• Check the server guidelines in {rules_ref}\n"
                f"• Choose your trade specialties & alerts in {roles_ref}\n"
                f"• View live PZ server telemetry in {status_ref}\n"
                f"Good luck out there, and don't get bitten! 🌲"
            )
            try:
                await general_ch.send(welcome_msg)
                print(f"[AutoRole] Sent general chat welcome guide for {member.name}")
            except Exception as e:
                print(f"[AutoRole] Could not send welcome message to #general: {e}")

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
