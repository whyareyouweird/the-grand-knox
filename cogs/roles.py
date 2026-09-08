"""
The Grand Knox - Self-Assignable Roles & Transmission Frequencies
Provides persistent interactive dropdown menus and buttons for survivor
professions/specialties and alert notifications.
"""

import discord
from discord.ext import commands
import config

class SpecialtySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Field Medic",
                value="🩺 Field Medic",
                description="Expertise in surgery, suture needles, splints, and infection care.",
                emoji="🩺"
            ),
            discord.SelectOption(
                label="Master Carpenter",
                value="🔨 Master Carpenter",
                description="Fortify safehouses, build rain collector barrels, and construct towers.",
                emoji="🔨"
            ),
            discord.SelectOption(
                label="Woodland Scavenger",
                value="🪓 Woodland Scavenger",
                description="Master of the wilderness: foraging, trapping, campfires, and axes.",
                emoji="🪓"
            ),
            discord.SelectOption(
                label="Marksman / Hunter",
                value="🎯 Marksman / Hunter",
                description="Precision ballistic defense, ammo management, and shotgun clearing.",
                emoji="🎯"
            ),
            discord.SelectOption(
                label="Grease Monkey",
                value="🚗 Grease Monkey",
                description="Vehicle maintenance, hotwiring, performance engines, and tire repair.",
                emoji="🚗"
            ),
            discord.SelectOption(
                label="Rural Farmer",
                value="🌾 Rural Farmer",
                description="Agriculture, crop disease treatment, cabbage yields, and food security.",
                emoji="🌾"
            ),
            discord.SelectOption(
                label="Electrician",
                value="⚡ Electrician",
                description="Generator repairs, wire linking, battery systems, and communication rigs.",
                emoji="⚡"
            )
        ]
        super().__init__(
            placeholder="🪓 Select your Survivor Trade Skill / Specialty...",
            min_values=1,
            max_values=3,
            options=options,
            custom_id="grand_knox_specialty_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        if not guild or not isinstance(member, discord.Member):
            return

        added_roles = []
        removed_roles = []

        all_specialty_names = [
            "🩺 Field Medic", "🔨 Master Carpenter", "🪓 Woodland Scavenger",
            "🎯 Marksman / Hunter", "🚗 Grease Monkey", "🌾 Rural Farmer", "⚡ Electrician"
        ]

        for role_name in all_specialty_names:
            role_obj = discord.utils.get(guild.roles, name=role_name)
            if not role_obj:
                continue

            if role_name in self.values:
                if role_obj not in member.roles:
                    await member.add_roles(role_obj, reason="Survivor specialty self-selection")
                    added_roles.append(role_obj.name)
            else:
                if role_obj in member.roles:
                    await member.remove_roles(role_obj, reason="Survivor specialty self-selection")
                    removed_roles.append(role_obj.name)

        # Synchronize specialties divider
        specialty_div = discord.utils.get(guild.roles, name="─── SURVIVOR SPECIALTIES ───")
        if specialty_div:
            has_specialties = any(discord.utils.get(guild.roles, name=r) in member.roles for r in all_specialty_names)
            if has_specialties and specialty_div not in member.roles:
                await member.add_roles(specialty_div, reason="Auto-assign specialties divider")
            elif not has_specialties and specialty_div in member.roles:
                await member.remove_roles(specialty_div, reason="Remove unused specialties divider")

        embed = discord.Embed(
            title="🛠️ Survivor Trade Specialty Updated",
            description="Your dossier in the Knox County registry has been updated with your operational roles.",
            color=config.KnoxColors.RADIO_CYAN
        )
        if added_roles:
            embed.add_field(name="✅ Added Specialties", value="\n".join([f"• {r}" for r in added_roles]), inline=False)
        if removed_roles:
            embed.add_field(name="➖ Removed Specialties", value="\n".join([f"• {r}" for r in removed_roles]), inline=False)
        if not added_roles and not removed_roles:
            embed.description = "No changes were made to your active trade specialties."

        embed.set_footer(text="The Grand Knox • Department of Civil Defense")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class NotificationSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Cordon Announcements",
                value="📢 Cordon Announcements",
                description="Official community news, major server rules, and development posts.",
                emoji="📢"
            ),
            discord.SelectOption(
                label="Knox Horde Invasions",
                value="🧟 Knox Horde Invasions",
                description="Pings for in-game horde night events, helicopter drops, and group hunts.",
                emoji="🧟"
            ),
            discord.SelectOption(
                label="Server Restarts & Wipes",
                value="🛠️ Server Restarts & Wipes",
                description="Timely warnings for maintenance, modpack updates, and season wipes.",
                emoji="🛠️"
            ),
            discord.SelectOption(
                label="Radio Broadcasts",
                value="📻 Radio Broadcasts",
                description="In-character Emergency Broadcast System transmissions and radio lore.",
                emoji="📻"
            )
        ]
        super().__init__(
            placeholder="📻 Select your Transmission Notification Frequencies...",
            min_values=0,
            max_values=4,
            options=options,
            custom_id="grand_knox_notification_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        if not guild or not isinstance(member, discord.Member):
            return

        all_alert_names = [
            "📢 Cordon Announcements", "🧟 Knox Horde Invasions",
            "🛠️ Server Restarts & Wipes", "📻 Radio Broadcasts"
        ]

        added_roles = []
        removed_roles = []

        for role_name in all_alert_names:
            role_obj = discord.utils.get(guild.roles, name=role_name)
            if not role_obj:
                continue

            if role_name in self.values:
                if role_obj not in member.roles:
                    await member.add_roles(role_obj, reason="Notification ping self-selection")
                    added_roles.append(role_obj.name)
            else:
                if role_obj in member.roles:
                    await member.remove_roles(role_obj, reason="Notification ping self-selection")
                    removed_roles.append(role_obj.name)

        # Synchronize transmission alerts divider
        alerts_div = discord.utils.get(guild.roles, name="─── TRANSMISSION ALERTS ───")
        if alerts_div:
            has_alerts = any(discord.utils.get(guild.roles, name=r) in member.roles for r in all_alert_names)
            if has_alerts and alerts_div not in member.roles:
                await member.add_roles(alerts_div, reason="Auto-assign alerts divider")
            elif not has_alerts and alerts_div in member.roles:
                await member.remove_roles(alerts_div, reason="Remove unused alerts divider")

        embed = discord.Embed(
            title="📻 Radio Frequency Preferences Saved",
            description="Your personal radio receiver has been calibrated to the chosen emergency bands.",
            color=config.KnoxColors.HAZARD_AMBER
        )
        if added_roles:
            embed.add_field(name="📶 Tuned In To", value="\n".join([f"• {r}" for r in added_roles]), inline=False)
        if removed_roles:
            embed.add_field(name="🔇 Muted Frequencies", value="\n".join([f"• {r}" for r in removed_roles]), inline=False)
        if not added_roles and not removed_roles:
            embed.description = "All notification frequencies remain in their current configuration."

        embed.set_footer(text="Emergency Broadcast System (AEBS) • Frequency Hub")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SurvivorRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SpecialtySelect())
        self.add_item(NotificationSelect())


class RolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(RolesCog(bot))
