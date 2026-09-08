"""
Script to rebuild the roles on The Grand Knox with all dividers cleanly placed
and auto-role assigned to existing members.
"""

import sys
import os
import asyncio
import discord
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
load_dotenv()

import config

async def main():
    client = discord.Client(intents=discord.Intents.all())

    @client.event
    async def on_ready():
        guild = client.get_guild(int(os.getenv('GUILD_ID')))
        print(f'Target Guild: {guild.name}')

        # 1. Clean old custom roles
        print('\n[1/3] Deleting current custom roles...')
        for r in list(guild.roles):
            if r.name not in ['@everyone', 'Grand Knox'] and not r.managed:
                try:
                    await r.delete(reason='Rebuilding with dividers')
                    print(f'  Deleted: {r.name}')
                    await asyncio.sleep(0.12)
                except Exception as e:
                    print(f'  Failed to delete {r.name}: {e}')

        # 2. Create roles in order from TOP to BOTTOM
        # (In Discord, creating inserts at pos 1, pushing earlier roles UP.
        # So creating Administration first means it ends up at the very top!)
        print('\n[2/3] Constructing roles with dividers...')
        created_roles = {}
        for r_cfg in config.ROLE_HIERARCHY:
            try:
                role = await guild.create_role(
                    name=r_cfg.name,
                    color=discord.Color(r_cfg.color),
                    hoist=r_cfg.hoist,
                    mentionable=r_cfg.mentionable,
                    permissions=r_cfg.permissions,
                    reason='The Grand Knox Pristine Role Hierarchy with Dividers'
                )
                created_roles[r_cfg.name] = role
                print(f'  Created: {r_cfg.name}')
                await asyncio.sleep(0.18)
            except Exception as e:
                print(f'  Failed to create {r_cfg.name}: {e}')

        # 3. Assign roles to owner and members
        print('\n[3/3] Assigning owner and member auto-roles...')
        high_cmd = created_roles.get('⚜️ Military High Command')
        survivor_role = created_roles.get('🌲 Knox Survivor')

        if high_cmd and guild.owner:
            try:
                await guild.owner.add_roles(high_cmd, reason='Server Owner clearance')
                print(f'  [+] Assigned ⚜️ Military High Command to owner {guild.owner.name}')
            except Exception as e:
                print(f'  Error assigning owner role: {e}')

        if survivor_role:
            for member in guild.members:
                if not member.bot:
                    try:
                        await member.add_roles(survivor_role, reason='Auto-role assign')
                        print(f'  [+] Assigned 🌲 Knox Survivor to {member.name}')
                    except Exception as e:
                        print(f'  Error assigning survivor role to {member.name}: {e}')

        print('\n[+] Role reconstruction with dividers complete!')
        await client.close()

    await client.start(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
