"""
The Grand Knox - Main Discord Bot Entry Point
An advanced, highly aesthetic Discord bot and server automation system
for Project Zomboid communities.
"""

import sys
import os
import asyncio
import logging
import discord
from discord.ext import commands
import config
from cogs.roles import SurvivorRolesView
from cogs.tickets import TicketHubView, TicketControlView

# Ensure terminal uses UTF-8 encoding for clean Unicode / ASCII rendering on Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Configure clean logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GrandKnox")

BANNER = r"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║   ████████╗██╗  ██╗███████╗     ██████╗ ██████╗  █████╗ ███╗   ██╗██████╗            ║
║   ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝ ██╔══██╗██╔══██╗████╗  ██║██╔══██╗           ║
║      ██║   ███████║█████╗      ██║  ███╗██████╔╝███████║██╔██╗ ██║██║  ██║           ║
║      ██║   ██╔══██║██╔══╝      ██║   ██║██╔══██╗██╔══██║██║╚██╗██║██║  ██║           ║
║      ██║   ██║  ██║███████╗    ╚██████╔╝██║  ██║██║  ██║██║ ╚████║██████╔╝           ║
║      ╚═╝   ╚═╝  ╚═╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝            ║
║                         K N O X   C O U N T Y                                        ║
║          MILITARY QUARANTINE ZONE • JULY 1993 • PROTOCOL ENGAGED                     ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

class GrandKnoxBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!knox ",
            intents=intents,
            help_command=None,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="LBMW 93.2MHz | /status"
            ),
            status=discord.Status.online
        )

    async def setup_hook(self):
        """Called automatically when bot initializes before connecting to Discord."""
        # 0. Start Web Health Check Server for Render hosting if PORT is set
        port_env = os.getenv("PORT")
        if port_env and port_env.isdigit():
            port = int(port_env)
            try:
                from aiohttp import web
                async def handle_ping(request):
                    return web.Response(text="The Grand Knox AI is online and operational!")
                health_app = web.Application()
                health_app.router.add_get("/", handle_ping)
                health_app.router.add_get("/health", handle_ping)
                runner = web.AppRunner(health_app)
                await runner.setup()
                site = web.TCPSite(runner, "0.0.0.0", port)
                await site.start()
                logger.info(f"Render health check web server bound to 0.0.0.0:{port}")
            except Exception as e:
                logger.warning(f"Could not bind Render health server: {e}")

        # 1. Register Persistent UI Views (so buttons/dropdowns work across restarts)
        self.add_view(SurvivorRolesView())
        self.add_view(TicketHubView())
        self.add_view(TicketControlView())
        logger.info("Registered all persistent interactive UI views.")

        # 2. Dynamically Load Cogs
        initial_extensions = [
            "cogs.setup_server",
            "cogs.verification",
            "cogs.roles",
            "cogs.pz_monitor",
            "cogs.tickets",
            "cogs.survival_guide"
        ]

        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded extension: {ext}")
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}", exc_info=True)

    async def on_ready(self):
        print(BANNER)
        print(f"  [+] Grand Knox AI Online: {self.user.name} ({self.user.id})")
        print(f"  [+] Active Guilds: {len(self.guilds)}")
        for g in self.guilds:
            print(f"      • {g.name} (ID: {g.id}) | Members: {g.member_count}")
        print(f"  [+] Project Zomboid Target: {config.PZ_SERVER_IP}:{config.PZ_QUERY_PORT}")
        print(f"  [+] Latency: {round(self.latency * 1000, 1)}ms")
        print(f"  [+] Ready for survivor intake and quarantine enforcement.\n")

        # Sync slash commands
        try:
            if config.GUILD_ID:
                guild_obj = discord.Object(id=config.GUILD_ID)
                self.tree.copy_global_to(guild=guild_obj)
                synced = await self.tree.sync(guild=guild_obj)
                logger.info(f"Instantly synchronized {len(synced)} slash commands to Guild ID: {config.GUILD_ID}")
            else:
                synced = await self.tree.sync()
                logger.info(f"Synchronized {len(synced)} slash commands globally.")
        except Exception as e:
            logger.warning(f"Command sync notice: {e}")

async def main():
    if not config.DISCORD_TOKEN or config.DISCORD_TOKEN == "your_bot_token_here":
        print("\n" + "="*80)
        print("  [!] CONFIGURATION REQUIRED: DISCORD_TOKEN is missing or not configured.")
        print("  [!] Please open '.env' and paste your Discord bot token.")
        print("  [!] For setup instructions, read README.md")
        print("="*80 + "\n")
        return

    bot = GrandKnoxBot()
    async with bot:
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Grand Knox AI shutdown gracefully by operator.")
