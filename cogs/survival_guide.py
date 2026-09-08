"""
The Grand Knox - Survival Guide, Cartography & Emergency Broadcasts
Includes interactive town guides, trait lookups, and the Emergency Broadcast System (AEBS).
"""

import random
import datetime
from typing import Optional, Literal
import discord
from discord import app_commands
from discord.ext import commands
import config

TRAIT_DATABASE = {
    "dextrous": {
        "name": "Dextrous",
        "type": "Positive",
        "points": -2,
        "effect": "Transfers inventory items 50% faster.",
        "meta": "Tier S (Essential). Dramatically accelerates looting and panic-swapping in combat."
    },
    "fast learner": {
        "name": "Fast Learner",
        "type": "Positive",
        "points": -6,
        "effect": "+30% XP gain to all non-physical/combat skills.",
        "meta": "Tier S. Massively cuts down grinding for Carpentry, Mechanics, Electrical, and Tailoring."
    },
    "keen hearing": {
        "name": "Keen Hearing",
        "type": "Positive",
        "points": -6,
        "effect": "Doubles the survivor's rear perception radius.",
        "meta": "Tier S (Life Saver). Gives you critical visual warning if a zombie is sneaking up behind you."
    },
    "organized": {
        "name": "Organized",
        "type": "Positive",
        "points": -6,
        "effect": "+30% capacity to all containers, bags, and vehicle trunks.",
        "meta": "Tier S. Unlocks enormous storage multipliers for vehicles and backpacks."
    },
    "athletic": {
        "name": "Athletic",
        "type": "Positive",
        "points": -10,
        "effect": "+4 Fitness level, 20% faster running/sprinting, 60% slower endurance loss.",
        "meta": "Tier S. Outrun hordes and swing heavy weapons continuously without exhaustion."
    },
    "strong": {
        "name": "Strong",
        "type": "Positive",
        "points": -10,
        "effect": "+4 Strength level, +40% melee damage, +40% knockback chance, extra carry weight.",
        "meta": "Tier S. One-hit kill potential and superior encumbrance limits."
    },
    "smoker": {
        "name": "Smoker",
        "type": "Negative (Free Points)",
        "points": +4,
        "effect": "Accumulates stress and unhappiness if cigarettes aren't smoked every few hours.",
        "meta": "Tier S 'Free' Points. Cigarettes and matches are abundant on zombies and in gas stations."
    },
    "high thirst": {
        "name": "High Thirst",
        "type": "Negative (Free Points)",
        "points": +6,
        "effect": "Thirst increases by 100%.",
        "meta": "Tier S 'Free' Points. Easily negated by carrying two water bottles in your backpack."
    },
    "slow reader": {
        "name": "Slow Reader",
        "type": "Negative",
        "points": +2,
        "effect": "Takes 30% longer to finish reading skill books and magazines.",
        "meta": "Great for singleplayer/co-op with sleep or time acceleration. Neutral on MP servers."
    },
    "prone to illness": {
        "name": "Prone to Illness",
        "type": "Negative",
        "points": +4,
        "effect": "Faster catch of common colds and increased rate of zombification if bitten/scratched.",
        "meta": "Tier A. If you get bitten you die anyway; common colds are avoided by staying dry."
    }
}

class SurvivalGuideCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="map", description="Inspect Knox County town coordinates, POI loot zones, and interactive map links.")
    @app_commands.describe(town="Select the Knox County sector to inspect")
    @app_commands.choices(town=[
        app_commands.Choice(name="Muldraugh (Highway & Hardware Warehouses)", value="muldraugh"),
        app_commands.Choice(name="West Point (Gun Store & Dense Downtown)", value="west point"),
        app_commands.Choice(name="Rosewood (Fire Station & Penitentiary)", value="rosewood"),
        app_commands.Choice(name="Riverside (Scenic River & Wealthy Estates)", value="riverside"),
        app_commands.Choice(name="Louisville (Metropolitan Cordon Breach)", value="louisville"),
        app_commands.Choice(name="March Ridge (Military Residential Blocks)", value="march ridge")
    ])
    async def map_command(self, interaction: discord.Interaction, town: app_commands.Choice[str]):
        data = config.KNOX_LOCATIONS.get(town.value)
        if not data:
            await interaction.response.send_message("Sector data not found.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🗺️ SECTOR CARTOGRAPHY: {data['name']}",
            description=(
                f"{data['description']}\n\n"
                f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"  **Grid Coordinates**: `{data['coords']}`\n"
                f"  **Threat Severity**: `{data['danger']}`\n"
                f"  **High-Value POIs**: {data['loot']}\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"🔗 **[Open Sector in PZ Map Project]({data['map_url']})**"
            ),
            color=config.KnoxColors.MILITARY_OLIVE
        )
        embed.set_footer(text="The Grand Knox • Military Topographical Division")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trait", description="Look up Project Zomboid character traits, point values, and survival meta ratings.")
    @app_commands.describe(name="Name of the trait (e.g., Dextrous, Keen Hearing, Smoker)")
    async def trait_command(self, interaction: discord.Interaction, name: str):
        query = name.strip().lower()
        trait = None

        for k, v in TRAIT_DATABASE.items():
            if query in k or k in query:
                trait = v
                break

        if not trait:
            available = ", ".join([f"`{t['name']}`" for t in TRAIT_DATABASE.values()])
            await interaction.response.send_message(
                f"❌ Unknown trait `{name}`.\n**Indexed traits:** {available}",
                ephemeral=True
            )
            return

        point_str = f"+{trait['points']} pts" if trait['points'] > 0 else f"{trait['points']} pts"
        embed = discord.Embed(
            title=f"🧬 SURVIVOR TRAIT: {trait['name']} ({point_str})",
            description=(
                f"**Classification**: `{trait['type']}`\n"
                f"**Game Mechanics**: {trait['effect']}\n\n"
                f"**Survival Meta Analysis:**\n"
                f"*{trait['meta']}*"
            ),
            color=config.KnoxColors.SURVIVOR_GREEN if "Positive" in trait['type'] else config.KnoxColors.CORDON_RED
        )
        embed.set_footer(text="The Grand Knox • Biological & Genetic Dossier")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="broadcast", description="Transmit an Emergency Broadcast System (AEBS) radio alert.")
    @app_commands.describe(
        preset="Select an emergency alert scenario",
        custom_message="Optional custom teletype message to transmit"
    )
    @app_commands.choices(preset=[
        app_commands.Choice(name="Helicopter Rotor Activity Alert", value="CHOPPER_EVENT"),
        app_commands.Choice(name="Power & Water Grid Failure Warning", value="BLACKOUT_WARNING"),
        app_commands.Choice(name="Biological Migration / Horde Surge", value="HORDE_MASSING"),
        app_commands.Choice(name="Custom Civilian Dispatch", value="CUSTOM")
    ])
    @commands.has_permissions(manage_messages=True)
    async def broadcast_command(
        self,
        interaction: discord.Interaction,
        preset: app_commands.Choice[str],
        custom_message: Optional[str] = None
    ):
        """Transmit an authentic Emergency Broadcast System teletype message."""
        selected_data = None
        for p in config.AEBS_PRESETS:
            if p["type"] == preset.value:
                selected_data = p
                break

        if preset.value == "CUSTOM" or not selected_data:
            title = "EMERGENCY BROADCAST SYSTEM — CIVIL DISPATCH"
            alert_text = custom_message or "ATTENTION CITIZENS: MAINTAIN QUARANTINE PROTOCOL. REPORT ALL SUSPICIOUS BITES TO LAW ENFORCEMENT."
            weather = "Temp: 75°F | Barometer: 29.92 | Wind: Variable 5mph"
        else:
            title = selected_data["title"]
            alert_text = custom_message or selected_data["alert"]
            weather = selected_data["weather"]

        embed = discord.Embed(
            title=f"📻 {title}",
            description=(
                f"```text\n"
                f"...BZZZZT... KNOX EXCLUSION ZONE LBMW 93.2MHz ...BZZZT...\n"
                f"----------------------------------------------------\n"
                f"{alert_text}\n"
                f"----------------------------------------------------\n"
                f"METEOROLOGY: {weather}\n"
                f"AUTOMATED TRANSMITTER: FORT KNOX CORDON FREQ\n"
                f"```"
            ),
            color=config.KnoxColors.HAZARD_AMBER
        )
        embed.set_footer(text="Emergency Broadcast System (AEBS) • Automated Teletype 1993")
        embed.timestamp = datetime.datetime.now()

        # Send to announcements if found, or reply in current channel
        guild = interaction.guild
        alerts_channel = (discord.utils.get(guild.text_channels, name="📢・announcements") or 
                          discord.utils.get(guild.text_channels, name="📢・cordon-alerts")) if guild else None

        if alerts_channel and alerts_channel != interaction.channel:
            await alerts_channel.send(content="@here 📻 **INCOMING EMERGENCY BROADCAST**", embed=embed)
            await interaction.response.send_message(f"✅ Emergency broadcast transmitted to {alerts_channel.mention}.", ephemeral=True)
        else:
            await interaction.response.send_message(content="@here 📻 **INCOMING EMERGENCY BROADCAST**", embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SurvivalGuideCog(bot))
