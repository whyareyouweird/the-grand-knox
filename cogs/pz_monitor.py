"""
The Grand Knox - Project Zomboid Dedicated Server Telemetry Monitor
Natively queries Steam A2S UDP endpoints for live survivor counts, latency,
and status, updating Discord channels and embeds in real time.
"""

import asyncio
import socket
import struct
import time
import datetime
from typing import Optional, Dict, Any
import discord
from discord import app_commands
from discord.ext import commands, tasks
import config

class A2SQueryClient:
    """Lightweight native Valve A2S UDP Query client for Project Zomboid."""

    A2S_INFO_HEADER = b'\xFF\xFF\xFF\xFF\x54Source Engine Query\x00'

    @classmethod
    async def query_server(cls, ip: str, port: int, timeout: float = 3.0) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, cls._sync_query, ip, port, timeout)

    @classmethod
    def _sync_query(cls, ip: str, port: int, timeout: float) -> Dict[str, Any]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        start_time = time.perf_counter()

        try:
            # Send initial A2S_INFO query
            sock.sendto(cls.A2S_INFO_HEADER, (ip, port))
            data, _ = sock.recvfrom(4096)
            latency = int((time.perf_counter() - start_time) * 1000)

            # Check if challenge response received (0x41)
            if len(data) >= 9 and data[4] == 0x41:
                challenge = data[5:9]
                sock.sendto(cls.A2S_INFO_HEADER + challenge, (ip, port))
                data, _ = sock.recvfrom(4096)
                latency = int((time.perf_counter() - start_time) * 1000)

            # Check if valid A2S_INFO response (0x49)
            if len(data) > 5 and data[4] == 0x49:
                return cls._parse_a2s_info(data[5:], latency)

            return {"online": False, "error": "Invalid response packet"}

        except socket.timeout:
            return {"online": False, "error": "Connection timed out (Radio Silence)"}
        except Exception as e:
            return {"online": False, "error": str(e)}
        finally:
            sock.close()

    @classmethod
    def _parse_a2s_info(cls, payload: bytes, latency: int) -> Dict[str, Any]:
        offset = 0

        def read_cstring():
            nonlocal offset
            end = payload.find(b'\x00', offset)
            if end == -1:
                result = payload[offset:].decode('utf-8', errors='replace')
                offset = len(payload)
                return result
            result = payload[offset:end].decode('utf-8', errors='replace')
            offset = end + 1
            return result

        protocol = payload[offset]
        offset += 1
        name = read_cstring()
        map_name = read_cstring()
        folder = read_cstring()
        game = read_cstring()

        steam_id = struct.unpack_from('<H', payload, offset)[0]
        offset += 2
        players = payload[offset]
        offset += 1
        max_players = payload[offset]
        offset += 1
        bots = payload[offset]
        offset += 1

        version = "Unknown"
        if offset < len(payload):
            try:
                version = read_cstring()
            except Exception:
                pass

        return {
            "online": True,
            "name": name,
            "map": map_name or "Knox County, KY",
            "game": game,
            "players": players,
            "max_players": max_players,
            "bots": bots,
            "latency": latency,
            "version": version
        }


class PZMonitorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.last_status_message_id: Optional[int] = None
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    @tasks.loop(seconds=config.STATUS_UPDATE_INTERVAL)
    async def status_loop(self):
        """Background routine to refresh telemetry in the server status channel."""
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(config.GUILD_ID) if config.GUILD_ID else None
        if not guild and self.bot.guilds:
            guild = self.bot.guilds[0]
        if not guild:
            return

        status_channel = discord.utils.get(guild.text_channels, name="🟢・server-status")
        if not status_channel:
            return

        # Query the Project Zomboid Server
        result = await A2SQueryClient.query_server(config.PZ_SERVER_IP, config.PZ_QUERY_PORT, timeout=3.0)

        embed = self._build_status_embed(result)

        try:
            # Edit existing message or send a new pinned status embed
            if self.last_status_message_id:
                try:
                    msg = await status_channel.fetch_message(self.last_status_message_id)
                    await msg.edit(embed=embed)
                    return
                except discord.NotFound:
                    self.last_status_message_id = None

            # Look through recent channel history for an existing status message from the bot
            async for old_msg in status_channel.history(limit=10):
                if old_msg.author == self.bot.user and old_msg.embeds:
                    if "TELEMETRY" in (old_msg.embeds[0].title or ""):
                        self.last_status_message_id = old_msg.id
                        await old_msg.edit(embed=embed)
                        return

            # If none found, post new
            new_msg = await status_channel.send(embed=embed)
            self.last_status_message_id = new_msg.id
            try:
                await new_msg.pin(reason="Sticky Knox County server status telemetry")
            except Exception:
                pass

        except Exception as e:
            print(f"[PZ Monitor] Error updating status message: {e}")

    def _build_status_embed(self, result: Dict[str, Any]) -> discord.Embed:
        timestamp_now = int(datetime.datetime.now().timestamp())

        if result.get("online"):
            embed = discord.Embed(
                title="🟢 THE GRAND KNOX — LIVE TELEMETRY",
                description=(
                    f"**Quarantine Perimeter Signal**: `ONLINE & ACTIVE`\n"
                    f"*{config.PZ_SERVER_NAME}*\n\n"
                    f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"  **Surviving Population**: `{result['players']} / {result['max_players']}` Survivors\n"
                    f"  **Sector Cartography**: `{result['map']}`\n"
                    f"  **Signal Latency**: `{result['latency']} ms`\n"
                    f"  **Telemetry Version**: `Build {result.get('version', '41.78+')}`\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"**Direct Connection Info:**\n"
                    f"• **IP Address**: `{config.PZ_SERVER_IP}`\n"
                    f"• **Game Port**: `{config.PZ_SERVER_PORT}`\n"
                    f"• **Server Password**: `{config.PZ_SERVER_PASSWORD}`\n"
                    f"• **Steam Direct**: [Click to Connect](steam://connect/{config.PZ_SERVER_IP}:{config.PZ_SERVER_PORT})"
                ),
                color=config.KnoxColors.SURVIVOR_GREEN
            )
            embed.set_footer(text=f"Last Radar Sweep: Telemetry Active • Auto-updates every {config.STATUS_UPDATE_INTERVAL}s")
        else:
            embed = discord.Embed(
                title="🔴 THE GRAND KNOX — RADIO SILENCE (OFFLINE)",
                description=(
                    f"**Quarantine Perimeter Signal**: `SIGNAL LOST / DORMANT`\n\n"
                    f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                    f"  **Status**: Server unreachable or performing maintenance\n"
                    f"  **Target Address**: `{config.PZ_SERVER_IP}:{config.PZ_SERVER_PORT}`\n"
                    f"  **Notice**: Check <#cordon-alerts> for scheduled wipes or updates\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                    f"*If the server is undergoing a restart or modpack installation, signal will restore automatically.*"
                ),
                color=config.KnoxColors.CORDON_RED
            )
            embed.set_footer(text=f"Last Radar Sweep: Offline • Retrying in {config.STATUS_UPDATE_INTERVAL}s")

        return embed

    @app_commands.command(name="status", description="Check live status, survivor count, and latency of The Grand Knox server.")
    async def status_command(self, interaction: discord.Interaction):
        """Slash command for immediate manual status query."""
        await interaction.response.defer(ephemeral=False)
        result = await A2SQueryClient.query_server(config.PZ_SERVER_IP, config.PZ_QUERY_PORT, timeout=3.5)
        embed = self._build_status_embed(result)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="serverinfo", description="Get full direct connection details, modpack link, and server guidelines.")
    async def serverinfo_command(self, interaction: discord.Interaction):
        """Slash command showing full server connect details."""
        embed = discord.Embed(
            title="🗺️ THE GRAND KNOX — CONNECTION DOSSIER",
            description=(
                f"Complete connection parameters for joining our Project Zomboid dedicated server:\n\n"
                f"┃ **Server Name**: {config.PZ_SERVER_NAME}\n"
                f"┃ **IP Address**: `{config.PZ_SERVER_IP}`\n"
                f"┃ **Port**: `{config.PZ_SERVER_PORT}`\n"
                f"┃ **Server Password**: `{config.PZ_SERVER_PASSWORD}`\n"
                f"┃ **Workshop Modpack**: [Grand Knox Steam Collection]({config.PZ_MODPACK_URL})\n\n"
                f"**How to Connect:**\n"
                f"1. Launch Project Zomboid (Steam).\n"
                f"2. Click **Join** -> Select **Internet** or **Favorites**.\n"
                f"3. In the right panel, fill in `IP: {config.PZ_SERVER_IP}` and `Port: {config.PZ_SERVER_PORT}`.\n"
                f"4. Enter your preferred account username & password, then click **Save** & **Join**!\n"
                f"5. All server mods will automatically download via Steam Workshop."
            ),
            color=config.KnoxColors.RADIO_CYAN
        )
        embed.set_footer(text="The Grand Knox • Department of Civil Defense")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(PZMonitorCog(bot))
