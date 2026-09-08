"""
The Grand Knox - Configuration & Server Architecture Module
Defines colors, role hierarchies, channel layouts, permission matrices,
Project Zomboid lore assets, and embed layouts.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import discord
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==============================================================================
# ENVIRONMENT & RUNTIME SETTINGS
# ==============================================================================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
GUILD_ID = int(os.getenv("GUILD_ID", "0")) if os.getenv("GUILD_ID", "0").isdigit() else 0

# Project Zomboid Server Settings
PZ_SERVER_IP = os.getenv("PZ_SERVER_IP", "127.0.0.1")
PZ_SERVER_PORT = int(os.getenv("PZ_SERVER_PORT", "16261"))
PZ_QUERY_PORT = int(os.getenv("PZ_QUERY_PORT", "16261"))
PZ_SERVER_NAME = os.getenv("PZ_SERVER_NAME", "The Grand Knox | Hardcore Survival & RP")
PZ_SERVER_PASSWORD = os.getenv("PZ_SERVER_PASSWORD", "None (Open Public)")
PZ_MODPACK_URL = os.getenv("PZ_MODPACK_URL", "https://steamcommunity.com/sharedfiles/filedetails/?id=000000000")
STATUS_UPDATE_INTERVAL = int(os.getenv("STATUS_UPDATE_INTERVAL", "120"))

# ==============================================================================
# VISUAL THEME & PALETTE (KNOX COUNTY 1993)
# ==============================================================================
class KnoxColors:
    CORDON_RED = 0x8A1C14       # Biohazard Crimson / Danger
    MILITARY_OLIVE = 0x3D4E37   # Cordon Army Olive
    HAZARD_AMBER = 0xD4AC0D     # Warning / Alert Amber
    PATROL_BLUE = 0x2980B9      # Marshal / Law Enforcement
    SURVIVOR_GREEN = 0x27AE60   # Safe Haven / Verified Survivor
    RADIO_CYAN = 0x16A085       # AEBS Radio Frequency
    BUNKER_DARK = 0x1A1C1E      # Deep Cordon Night
    MUTED_GREY = 0x7F8C8D       # Quarantine Neutral
    DECEASED_BLACK = 0x111111   # Infected / Fallen

# ==============================================================================
# ROLE DEFINITIONS & PERMISSIONS
# Order defined from LOWEST priority to HIGHEST priority for creation order.
# ==============================================================================
@dataclass
class RoleConfig:
    name: str
    color: int
    hoist: bool = False
    mentionable: bool = False
    permissions: discord.Permissions = discord.Permissions.none()
    is_divider: bool = False
    group: str = "general"

# Ordered from TOP to BOTTOM: In Discord, creating a role places it at pos 1,
# pushing all previously created roles UP. So the FIRST created role ends up at the VERY TOP!
ROLE_HIERARCHY: List[RoleConfig] = [
    # --- COMMAND & DISPATCH ---
    RoleConfig(
        name="⚜️ Military High Command",
        color=KnoxColors.CORDON_RED,
        hoist=True,
        mentionable=True,
        permissions=discord.Permissions(administrator=True),
        group="staff"
    ),
    RoleConfig(
        name="🛡️ Knox County Marshals",
        color=KnoxColors.PATROL_BLUE,
        hoist=True,
        mentionable=True,
        permissions=discord.Permissions(
            kick_members=True,
            ban_members=True,
            manage_channels=True,
            manage_messages=True,
            mute_members=True,
            deafen_members=True,
            move_members=True,
            moderate_members=True,
            view_audit_log=True
        ),
        group="staff"
    ),
    RoleConfig(
        name="🤖 Grand Knox AI",
        color=KnoxColors.RADIO_CYAN,
        hoist=True,
        mentionable=False,
        permissions=discord.Permissions.all(),
        group="bot"
    ),
    RoleConfig(
        name="📻 Emergency Dispatch",
        color=KnoxColors.MUTED_GREY,
        hoist=True,
        mentionable=False,
        permissions=discord.Permissions(
            manage_messages=True,
            embed_links=True,
            attach_files=True
        ),
        group="staff"
    ),
    # --- ADMINISTRATION DIVIDER (BELOW STAFF) ---
    RoleConfig(
        name="─── ADMINISTRATION ───",
        color=0x2C2F33,
        hoist=False,
        mentionable=False,
        is_divider=True,
        group="divider"
    ),

    # --- CLEARANCE TIERS ---
    RoleConfig(
        name="🎖️ Veteran Survivor",
        color=KnoxColors.HAZARD_AMBER,
        hoist=True,
        mentionable=False,
        permissions=discord.Permissions(
            priority_speaker=True,
            use_voice_activation=True
        ),
        group="tier"
    ),
    RoleConfig(
        name="🌲 Knox Survivor",
        color=KnoxColors.SURVIVOR_GREEN,
        hoist=True,
        mentionable=False,
        permissions=discord.Permissions(
            view_channel=True,
            send_messages=True,
            send_messages_in_threads=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            use_external_emojis=True,
            connect=True,
            speak=True,
            stream=True,
            use_application_commands=True
        ),
        group="tier"
    ),
    RoleConfig(
        name="🔇 Isolated / Infected",
        color=KnoxColors.DECEASED_BLACK,
        hoist=True,
        mentionable=False,
        permissions=discord.Permissions.none(),
        group="tier"
    ),
    # --- SURVIVOR TIERS DIVIDER (BELOW TIERS) ---
    RoleConfig(
        name="─── SURVIVOR TIERS ───",
        color=0x2C2F33,
        hoist=False,
        mentionable=False,
        is_divider=True,
        group="divider"
    ),

    # --- SURVIVOR SPECIALTIES ---
    RoleConfig(
        name="🩺 Field Medic",
        color=0xE74C3C,
        hoist=False,
        mentionable=False,
        group="specialty"
    ),
    RoleConfig(
        name="🔨 Master Carpenter",
        color=0xD35400,
        hoist=False,
        mentionable=False,
        group="specialty"
    ),
    RoleConfig(
        name="🪓 Woodland Scavenger",
        color=0x2ECC71,
        hoist=False,
        mentionable=False,
        group="specialty"
    ),
    RoleConfig(
        name="🎯 Marksman / Hunter",
        color=0x9B59B6,
        hoist=False,
        mentionable=False,
        group="specialty"
    ),
    RoleConfig(
        name="🚗 Grease Monkey",
        color=0x34495E,
        hoist=False,
        mentionable=False,
        group="specialty"
    ),
    RoleConfig(
        name="🌾 Rural Farmer",
        color=0xF1C40F,
        hoist=False,
        mentionable=False,
        group="specialty"
    ),
    RoleConfig(
        name="⚡ Electrician",
        color=0x3498DB,
        hoist=False,
        mentionable=False,
        group="specialty"
    ),
    # --- SURVIVOR SPECIALTIES DIVIDER (BELOW SPECIALTIES) ---
    RoleConfig(
        name="─── SURVIVOR SPECIALTIES ───",
        color=0x2C2F33,
        hoist=False,
        mentionable=False,
        is_divider=True,
        group="divider"
    ),

    # --- NOTIFICATION ALERTS ---
    RoleConfig(
        name="📢 Cordon Announcements",
        color=0xE67E22,
        hoist=False,
        mentionable=False,
        group="alert"
    ),
    RoleConfig(
        name="🧟 Knox Horde Invasions",
        color=0xC0392B,
        hoist=False,
        mentionable=False,
        group="alert"
    ),
    RoleConfig(
        name="🛠️ Server Restarts & Wipes",
        color=0x95A5A6,
        hoist=False,
        mentionable=False,
        group="alert"
    ),
    RoleConfig(
        name="📻 Radio Broadcasts",
        color=0x1ABC9C,
        hoist=False,
        mentionable=False,
        group="alert"
    ),
    # --- TRANSMISSION ALERTS DIVIDER (BELOW ALERTS / BOTTOM) ---
    RoleConfig(
        name="─── TRANSMISSION ALERTS ───",
        color=0x2C2F33,
        hoist=False,
        mentionable=False,
        is_divider=True,
        group="divider"
    )
]

# Mapping of divider roles to the roles that belong to that section
DIVIDER_MAPPING: Dict[str, List[str]] = {
    "─── ADMINISTRATION ───": [
        "⚜️ Military High Command",
        "🛡️ Knox County Marshals",
        "🤖 Grand Knox AI",
        "📻 Emergency Dispatch"
    ],
    "─── SURVIVOR TIERS ───": [
        "🎖️ Veteran Survivor",
        "🌲 Knox Survivor",
        "🔇 Isolated / Infected"
    ],
    "─── SURVIVOR SPECIALTIES ───": [
        "🩺 Field Medic",
        "🔨 Master Carpenter",
        "🪓 Woodland Scavenger",
        "🎯 Marksman / Hunter",
        "🚗 Grease Monkey",
        "🌾 Rural Farmer",
        "⚡ Electrician"
    ],
    "─── TRANSMISSION ALERTS ───": [
        "📢 Cordon Announcements",
        "🧟 Knox Horde Invasions",
        "🛠️ Server Restarts & Wipes",
        "📻 Radio Broadcasts"
    ]
}

# ==============================================================================
# CATEGORY & CHANNEL BLUEPRINTS
# ==============================================================================
SERVER_STRUCTURE = [
    {
        "category": "📢 ︱ INFORMATION",
        "type": "category",
        "access": "public_read_only",
        "channels": [
            {
                "name": "📢・announcements",
                "type": "text",
                "topic": "Official community announcements, updates, and important bulletins."
            },
            {
                "name": "📜・rules",
                "type": "text",
                "topic": "Official server guidelines, conduct rules, and survival etiquette."
            },
            {
                "name": "🟢・server-status",
                "type": "text",
                "topic": "Real-time Project Zomboid dedicated server telemetry, player counts, and ping."
            },
            {
                "name": "🗺️・server-map",
                "type": "text",
                "topic": "Knox County cartography, town coordinates, and interactive map links."
            },
            {
                "name": "📦・modpack",
                "type": "text",
                "topic": "Official Project Zomboid Steam Workshop collection and connection info."
            }
        ]
    },
    {
        "category": "🎭 ︱ ROLES",
        "type": "category",
        "access": "public_read_only",
        "channels": [
            {
                "name": "🎭・roles",
                "type": "text",
                "topic": "Pick your survivor skills, profession tags, and notification roles."
            }
        ]
    },
    {
        "category": "💬 ︱ GENERAL & COMMUNITY",
        "type": "category",
        "access": "verified_only",
        "channels": [
            {
                "name": "💬・general",
                "type": "text",
                "topic": "Main community chat for all survivors."
            },
            {
                "name": "📸・media",
                "type": "text",
                "topic": "Screenshots, base showcases, clips, and loot hauls."
            },
            {
                "name": "🤝・factions",
                "type": "text",
                "topic": "Recruit faction members, form alliances, and find teammates."
            },
            {
                "name": "🥫・trading",
                "type": "text",
                "topic": "Trade items, vehicles, ammo calibers, and building materials."
            },
            {
                "name": "💡・pz-tips",
                "type": "text",
                "topic": "Guides, trait tips, mechanics, farming, and survival advice."
            },
            {
                "name": "🤖・bot-commands",
                "type": "text",
                "topic": "Use bot commands: /status, /serverinfo, /map, /trait, and /broadcast."
            }
        ]
    },
    {
        "category": "🔊 ︱ VOICE CHANNELS",
        "type": "category",
        "access": "verified_voice",
        "channels": [
            {
                "name": "🔊・General Lounge",
                "type": "voice",
                "user_limit": 0
            },
            {
                "name": "🔊・Squad 1",
                "type": "voice",
                "user_limit": 8
            },
            {
                "name": "🔊・Squad 2",
                "type": "voice",
                "user_limit": 8
            },
            {
                "name": "🔊・Squad 3",
                "type": "voice",
                "user_limit": 10
            },
            {
                "name": "🔊・Duo 1",
                "type": "voice",
                "user_limit": 4
            },
            {
                "name": "🔊・Duo 2",
                "type": "voice",
                "user_limit": 4
            }
        ]
    },
    {
        "category": "🎫 ︱ SUPPORT & CLAIMS",
        "type": "category",
        "access": "support",
        "channels": [
            {
                "name": "🎫・tickets",
                "type": "text",
                "topic": "Open a ticket for safehouse base claims, grief reports, or questions."
            },
            {
                "name": "🔒・ticket-logs",
                "type": "text",
                "topic": "Staff archive of resolved incident dockets and claims."
            }
        ]
    },
    {
        "category": "🛡️ ︱ STAFF",
        "type": "category",
        "access": "staff_only",
        "channels": [
            {
                "name": "💬・staff-chat",
                "type": "text",
                "topic": "Staff-only discussion and administration."
            },
            {
                "name": "📝・mod-logs",
                "type": "text",
                "topic": "Audit logs and moderation actions."
            },
            {
                "name": "🔊・Staff Voice",
                "type": "voice",
                "user_limit": 0
            }
        ]
    }
]

# ==============================================================================
# PROJECT ZOMBOID TOWN DIRECTORY & MAP DATA
# ==============================================================================
KNOX_LOCATIONS = {
    "muldraugh": {
        "name": "Muldraugh, KY",
        "coords": "10625 x 9750",
        "danger": "High (Highway Congestion)",
        "loot": "Cortman Medical, Large Police Station, Mass-Genfac Warehouses, North Highway Strip",
        "map_url": "https://map.projectzomboid.com/#10625x9750",
        "description": "Dense residential sprawl split by the perilous Highway 31W. Packed with industrial tools and hardware."
    },
    "west point": {
        "name": "West Point, KY",
        "coords": "11850 x 6850",
        "danger": "Extreme (Suburban Chokepoints)",
        "loot": "Twin Rivers Gun Store, Police Department, Food Market, Hardware Emporium",
        "map_url": "https://map.projectzomboid.com/#11850x6850",
        "description": "High-density riverside town with extraordinary firearm and hardware stockpiles, swarming with infected."
    },
    "rosewood": {
        "name": "Rosewood, KY",
        "coords": "8150 x 11550",
        "danger": "Moderate (Ideal for New Survivors)",
        "loot": "Rosewood Fire Station (Axes & Gear), Police Station, Knox County Penitentiary, Book Store",
        "map_url": "https://map.projectzomboid.com/#8150x11550",
        "description": "A tranquil southern town with top-tier starter facilities, though the massive prison south lurks with danger."
    },
    "riverside": {
        "name": "Riverside, KY",
        "coords": "6350 x 5350",
        "danger": "Low-Moderate (Scenic Riverbank)",
        "loot": "Country Club, Giga Mart, Police Station, Pharmacy, Spiffo's, Bait Shop",
        "map_url": "https://map.projectzomboid.com/#6350x5350",
        "description": "Wealthy river town offering abundant fresh water access, vast residential neighborhoods, and reliable vehicle spawns."
    },
    "louisville": {
        "name": "Louisville Metropolitan Outpost",
        "coords": "12500 x 2500",
        "danger": "Catastrophic (Metropolis Infestation)",
        "loot": "Military Checkpoint Cordon, St. Peregrin Hospital, Malls, Military Surplus, Grand Hotels",
        "map_url": "https://map.projectzomboid.com/#12500x2500",
        "description": "The crown jewel of Kentucky behind the breached military cordon. Infinite loot, towering skyscrapers, millions of dead."
    },
    "march ridge": {
        "name": "March Ridge (Military Dormitories)",
        "coords": "10150 x 12700",
        "danger": "High (Enclosed Residential)",
        "loot": "Large Community Center, Movie Theater, High School, Dense Apartment Blocks",
        "map_url": "https://map.projectzomboid.com/#10150x12700",
        "description": "A dedicated military family township consisting of identical high-density multi-story dormitories."
    }
}

# ==============================================================================
# EMERGENCY BROADCAST SYSTEM (AEBS) PRESETS
# ==============================================================================
AEBS_PRESETS = [
    {
        "type": "CHOPPER_EVENT",
        "title": "EMERGENCY BROADCAST SYSTEM — UNIDENTIFIED ROTOR TRAFFIC",
        "alert": "PRIORITY 1: UNIDENTIFIED LOW-ALTITUDE ROTORCRAFT ACTIVE OVER KNOX EXCLUSION ZONE. INFECTED POPULATIONS AGITATED. REMAIN INDOORS UNDER COVER.",
        "weather": "Temp: 78°F | Barometer: 29.82 falling | Wind: SW 14mph | Visibility: Reduced"
    },
    {
        "type": "BLACKOUT_WARNING",
        "title": "EMERGENCY BROADCAST SYSTEM — GRID TELEMETRY FAILURE",
        "alert": "CIVIL INFRASTRUCTURE COMPROMISED. REGIONAL WATER PUMP PRESSURE COLLAPSING. POWER GRID RELAYS UNRESPONSIVE. PREPARE GENERATORS AND RAIN CISTERNS.",
        "weather": "Temp: 84°F | Barometer: 30.12 steady | Wind: E 6mph | Visibility: Clear"
    },
    {
        "type": "HORDE_MASSING",
        "title": "EMERGENCY BROADCAST SYSTEM — BIOLOGICAL MIGRATION VECTOR",
        "alert": "SURVEILLANCE RADAR DETECTS SIGNIFICANT VECTOR MOVEMENT ALONG HIGHWAY 31W AND TRANSIT CORRIDORS. REINFORCE SAFEHOUSES IMMEDIATELY.",
        "weather": "Temp: 69°F | Barometer: 29.50 falling rapidly | Wind: N 22mph (Storm Approaching) | Heavy Rain"
    }
]
