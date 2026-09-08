"""
Script to rename server channels and categories from heavy roleplay/larp
to clean, recognizable, standard Discord channel conventions.
"""

import sys
import os
import asyncio
import discord
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv()

CATEGORY_RENAMES = {
    '📊 ︱ KNOX STATUS & INTEL': '📢 ︱ INFORMATION',
    '📋 ︱ SURVIVOR REGISTRY': '👋 ︱ WELCOME & ROLES',
    '🏕️ ︱ SAFE HAVEN COMMONS': '💬 ︱ GENERAL & COMMUNITY',
    '📻 ︱ FREQUENCY DISPATCH': '🔊 ︱ VOICE CHANNELS',
    '🚨 ︱ EMERGENCY DISPATCH': '🎫 ︱ SUPPORT & CLAIMS',
    '🛡️ ︱ COMMAND BUNKER': '🛡️ ︱ STAFF'
}

CHANNEL_RENAMES = {
    '📢・cordon-alerts': '📢・announcements',
    '📜・survival-protocol': '📜・rules',
    '🟢・server-status': '🟢・server-status',
    '🗺️・exclusion-map': '🗺️・server-map',
    '📦・modpack-intel': '📦・modpack',
    '📋・manifest-arrivals': '👋・welcome',
    '🎭・survivor-specialties': '🎭・roles',
    '💬・survivor-lounge': '💬・general',
    '📸・polaroids-and-clips': '📸・media',
    '🤝・safehouse-recruitment': '🤝・factions',
    '🥫・barter-and-trade': '🥫・trading',
    '💡・survival-tips': '💡・pz-tips',
    '🤖・knox-terminal': '🤖・bot-commands',
    '🔊・Campfire (Lounge)': '🔊・General Lounge',
    '📻・AM 93.2 (Muldraugh Cordon)': '🔊・Squad 1',
    '📻・AM 98.6 (West Point Outpost)': '🔊・Squad 2',
    '📻・AM 102.4 (Louisville Safezone)': '🔊・Squad 3',
    '📻・AM 107.0 (Tactical Scavenge 1)': '🔊・Duo 1',
    '📻・AM 107.8 (Tactical Scavenge 2)': '🔊・Duo 2',
    '🎫・support-and-claims': '🎫・tickets',
    '🔒・transcripts-archive': '🔒・ticket-logs',
    '💬・marshals-hq': '💬・staff-chat',
    '📝・cordon-logs': '📝・mod-logs',
    '🔊・War Room': '🔊・Staff Voice'
}

async def main():
    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        guild = client.get_guild(int(os.getenv('GUILD_ID')))
        print(f'=== Renaming Categories & Channels on {guild.name} ===\n')

        for old_cat, new_cat in CATEGORY_RENAMES.items():
            cat = discord.utils.get(guild.categories, name=old_cat)
            if cat:
                try:
                    await cat.edit(name=new_cat)
                    print(f'[+] Category: {old_cat} -> {new_cat}')
                except Exception as e:
                    print(f'Error renaming category {old_cat}: {e}')

        for old_name, new_name in CHANNEL_RENAMES.items():
            ch = discord.utils.get(guild.channels, name=old_name)
            if ch:
                try:
                    await ch.edit(name=new_name)
                    print(f'  [+] Channel: {old_name} -> {new_name}')
                    await asyncio.sleep(0.35)
                except Exception as e:
                    print(f'  Error renaming channel {old_name}: {e}')

        print('\n[+] Renaming complete!')
        await client.close()

    await client.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
