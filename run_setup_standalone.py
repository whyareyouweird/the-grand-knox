"""
The Grand Knox - Standalone One-Click Server Provisioner
Execute this script from your terminal to automatically build the entire
Discord server structure, roles, granular permissions, and embeds in seconds.

Usage:
    python run_setup_standalone.py
"""

import sys
import os
import asyncio
import discord
from dotenv import load_dotenv

# Reconfigure terminal for UTF-8 output on Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import config
from cogs.setup_server import SetupServerCog

load_dotenv()

async def run_standalone_setup():
    print("=" * 80)
    print("      THE GRAND KNOX — ONE-CLICK SERVER AUTOMATION PROVISIONER")
    print("=" * 80)

    token = config.DISCORD_TOKEN
    guild_id = config.GUILD_ID

    if not token or token == "your_bot_token_here":
        print("\n[!] Error: DISCORD_TOKEN is missing from .env.")
        print("    Please add your Discord bot token to .env before running this script.\n")
        return

    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True

    client = discord.Client(intents=intents)

    async def execute_provisioning(target_guild: discord.Guild):
        print(f"\n[+] Target Guild Selected: '{target_guild.name}' (ID: {target_guild.id})")
        print(f"[+] Total Members: {target_guild.member_count}")
        print("\n[*] Commencing automated deployment of The Grand Knox architecture...")

        setup_cog = SetupServerCog(client)

        async def terminal_logger(status_text: str):
            print(f"    --> {status_text}")

        try:
            success, log = await setup_cog.provision_server(target_guild, status_callback=terminal_logger)

            print("\n" + "=" * 80)
            print("  [SUCCESS] THE GRAND KNOX SERVER PROVISIONING COMPLETE!")
            print("=" * 80)
            print(f"  • Roles Created / Verified   : {log['roles_created']}")
            print(f"  • Categories Established     : {log['categories_created']}")
            print(f"  • Channels Constructed       : {log['channels_created']}")
            print(f"  • Interactive Panels Deployed: {log['panels_deployed']}")
            print("\n  [IMPORTANT NEXT STEP]")
            print("  In Discord, navigate to Server Settings -> Roles, and drag the")
            print("  'Grand Knox AI' (or your bot's role) above '🌲 Knox Survivor'")
            print("  and 'Quarantine Arrival' so it can assign roles to members.\n")

        except Exception as e:
            print(f"\n[!] Error during provisioning: {e}")
            import traceback
            traceback.print_exc()

        await client.close()

    @client.event
    async def on_ready():
        print(f"\n[+] Logged in as: {client.user.name} ({client.user.id})")

        target_guild = None
        if guild_id:
            target_guild = client.get_guild(guild_id)
            if not target_guild:
                try:
                    target_guild = await client.fetch_guild(guild_id)
                except Exception:
                    pass

        if target_guild:
            await execute_provisioning(target_guild)
            return

        if client.guilds:
            print(f"[!] Target GUILD_ID ({guild_id}) not matched directly. Using first joined server:")
            await execute_provisioning(client.guilds[0])
            return

        invite_url = f"https://discord.com/oauth2/authorize?client_id={client.user.id}&scope=bot%20applications.commands&permissions=8"
        print("\n[!] The bot is not currently in any Discord server!")
        print(f"    INVITE URL: {invite_url}")
        print(f"    Waiting for you to authorize the bot into Guild ID: {guild_id}...")

    @client.event
    async def on_guild_join(guild: discord.Guild):
        print(f"\n[+] Bot was successfully invited to: '{guild.name}' (ID: {guild.id})!")
        await execute_provisioning(guild)

    try:
        await client.start(token)
    except discord.LoginFailure:
        print("\n[!] Error: Invalid DISCORD_TOKEN provided in .env.")
    except Exception as e:
        print(f"\n[!] Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(run_standalone_setup())
