"""
The Grand Knox - Automated Server Architect & Provisioning Cog
Constructs the complete Discord server hierarchy, creates categories,
text/voice channels, sets granular role permissions, and deploys aesthetic interactive panels.
"""

import asyncio
import datetime
from typing import Dict, List, Optional
import discord
from discord import app_commands
from discord.ext import commands
import config
from cogs.roles import SurvivorRolesView
from cogs.tickets import TicketHubView

class SetupServerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setup-server",
        description="Automate and construct The Grand Knox server: roles, permissions, channels, and embeds."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_server_command(self, interaction: discord.Interaction):
        """Slash command to provision the entire Discord server."""
        if not interaction.guild:
            await interaction.response.send_message("This command must be executed within a Discord server.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.administrator and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Access Denied: Only Military High Command (Administrators) may run this protocol.", ephemeral=True)
            return

        await interaction.response.send_message(
            "⏳ **COMMENCING GRAND KNOX AUTOMATION PROTOCOL**...\n"
            "• Deploying Role Hierarchy & Permissions...\n"
            "• Constructing Categories & Channels...\n"
            "• Installing Quarantine Checkpoints & Interactive Panels...",
            ephemeral=False
        )

        progress_msg = await interaction.original_response()

        async def status_updater(text: str):
            try:
                await progress_msg.edit(content=text)
            except Exception:
                pass

        success, log = await self.provision_server(interaction.guild, status_updater)

        final_embed = discord.Embed(
            title="✅ THE GRAND KNOX — SERVER PROVISIONING COMPLETE",
            description=(
                f"**Perimeter Wire Established Successfully.**\n\n"
                f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"  **Target Guild**: `{interaction.guild.name}`\n"
                f"  **Timestamp**: <t:{int(datetime.datetime.now().timestamp())}:F>\n"
                f"  **Roles Configured**: {log['roles_created']} created / verified\n"
                f"  **Categories Established**: {log['categories_created']}\n"
                f"  **Channels Constructed**: {log['channels_created']}\n"
                f"  **Interactive Panels Deployed**: {log['panels_deployed']}\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"**Next Steps for Command:**\n"
                f"1. Move the **`Grand Knox AI`** bot role to the top of Server Settings -> Roles so it can assign all member tiers.\n"
                f"2. Inspect `#border-checkpoint` and `#survivor-specialties`.\n"
                f"3. Invite survivors through the quarantine wire!"
            ),
            color=config.KnoxColors.SURVIVOR_GREEN
        )
        final_embed.set_footer(text="The Grand Knox • Automated Municipal Architecture")
        await progress_msg.edit(content=None, embed=final_embed)

    async def provision_server(self, guild: discord.Guild, status_callback=None):
        """Core engine that sets up roles, channels, and embeds."""
        log = {
            "roles_created": 0,
            "categories_created": 0,
            "channels_created": 0,
            "panels_deployed": 0
        }

        # 1. Update Server Name if possible
        try:
            if guild.name != "The Grand Knox":
                await guild.edit(name="The Grand Knox", reason="Grand Knox Server Automated Provisioning")
        except Exception as e:
            print(f"[Setup] Could not edit guild name: {e}")

        # 2. Deploy Roles from bottom to top
        if status_callback:
            await status_callback("⚙️ **Phase 1/3**: Deploying Role Hierarchy & Security Clearance Matrix...")

        roles_by_name: Dict[str, discord.Role] = {}
        # Map existing roles
        for r in guild.roles:
            roles_by_name[r.name] = r

        # Create or update roles in order
        for r_cfg in config.ROLE_HIERARCHY:
            role = roles_by_name.get(r_cfg.name)
            if not role:
                try:
                    role = await guild.create_role(
                        name=r_cfg.name,
                        color=discord.Color(r_cfg.color),
                        hoist=r_cfg.hoist,
                        mentionable=r_cfg.mentionable,
                        permissions=r_cfg.permissions,
                        reason="Grand Knox Automated Role Deployment"
                    )
                    log["roles_created"] += 1
                except Exception as e:
                    print(f"[Setup] Error creating role {r_cfg.name}: {e}")
                    continue
            else:
                # Update properties if necessary
                try:
                    await role.edit(
                        color=discord.Color(r_cfg.color),
                        hoist=r_cfg.hoist,
                        mentionable=r_cfg.mentionable,
                        reason="Grand Knox Role Calibration"
                    )
                except Exception:
                    pass

            roles_by_name[r_cfg.name] = role
            await asyncio.sleep(0.3)

        # Retrieve key security roles
        everyone_role = guild.default_role
        survivor_role = roles_by_name.get("🌲 Knox Survivor")
        quarantine_role = roles_by_name.get("☣️ Quarantine Arrival")
        isolated_role = roles_by_name.get("🔇 Isolated / Infected")
        marshals_role = roles_by_name.get("🛡️ Knox County Marshals")
        command_role = roles_by_name.get("⚜️ Military High Command")
        bot_role = roles_by_name.get("🤖 Grand Knox AI")

        # 3. Build Category and Channel Layout with Granular Permissions
        if status_callback:
            await status_callback("🏗️ **Phase 2/3**: Constructing Categories, Secure Channels & Voice Frequencies...")

        created_channels: Dict[str, discord.abc.GuildChannel] = {}

        for cat_data in config.SERVER_STRUCTURE:
            cat_name = cat_data["category"]
            access_mode = cat_data["access"]

            # Compute Overwrites for Category
            overwrites: Dict[discord.Role, discord.PermissionOverwrite] = {}

            # Default @everyone baseline
            if access_mode == "public_read_only":
                overwrites[everyone_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    add_reactions=True,
                    read_message_history=True
                )
            elif access_mode == "verified_only":
                overwrites[everyone_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True,
                    add_reactions=True,
                    use_external_emojis=True
                )
            elif access_mode == "verified_voice":
                overwrites[everyone_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    connect=True,
                    speak=True,
                    stream=True,
                    use_voice_activation=True
                )
            elif access_mode == "support":
                overwrites[everyone_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    read_message_history=True,
                    create_public_threads=True,
                    create_private_threads=True,
                    send_messages_in_threads=True
                )
            elif access_mode == "staff_only":
                overwrites[everyone_role] = discord.PermissionOverwrite(
                    view_channel=False
                )

            # Verified Knox Survivor Overwrites
            if survivor_role:
                if access_mode == "public_read_only":
                    overwrites[survivor_role] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=False,
                        read_message_history=True,
                        add_reactions=True
                    )
                elif access_mode == "verified_only":
                    overwrites[survivor_role] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        embed_links=True,
                        attach_files=True,
                        read_message_history=True,
                        add_reactions=True,
                        use_external_emojis=True
                    )
                elif access_mode == "verified_voice":
                    overwrites[survivor_role] = discord.PermissionOverwrite(
                        view_channel=True,
                        connect=True,
                        speak=True,
                        stream=True,
                        use_voice_activation=True
                    )
                elif access_mode == "support":
                    overwrites[survivor_role] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=False,
                        read_message_history=True,
                        create_public_threads=True,
                        create_private_threads=True,
                        send_messages_in_threads=True
                    )
                elif access_mode == "staff_only":
                    overwrites[survivor_role] = discord.PermissionOverwrite(
                        view_channel=False
                    )

            # Staff & High Command Overwrites
            if marshals_role:
                overwrites[marshals_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True,
                    manage_messages=True,
                    connect=True,
                    speak=True,
                    priority_speaker=True
                )
            if command_role:
                overwrites[command_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    manage_permissions=True,
                    connect=True,
                    speak=True
                )

            # Isolated / Infected Overwrites
            if isolated_role:
                overwrites[isolated_role] = discord.PermissionOverwrite(
                    send_messages=False,
                    speak=False,
                    add_reactions=False,
                    connect=False
                )

            # Bot Role Overwrites
            if bot_role:
                overwrites[bot_role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    manage_channels=True,
                    manage_messages=True
                )

            # Find or Create Category
            category = discord.utils.get(guild.categories, name=cat_name)
            if not category:
                try:
                    category = await guild.create_category(name=cat_name, overwrites=overwrites)
                    log["categories_created"] += 1
                except Exception as e:
                    print(f"[Setup] Failed to create category {cat_name}: {e}")
                    continue
            else:
                try:
                    await category.edit(overwrites=overwrites)
                except Exception:
                    pass

            # Create Channels under Category
            for ch_data in cat_data["channels"]:
                ch_name = ch_data["name"]
                ch_type = ch_data["type"]
                topic = ch_data.get("topic", "")

                if ch_type == "text":
                    text_ch = discord.utils.get(guild.text_channels, name=ch_name)
                    if not text_ch:
                        try:
                            text_ch = await guild.create_text_channel(
                                name=ch_name,
                                category=category,
                                topic=topic,
                                reason="Grand Knox Channel Construction"
                            )
                            log["channels_created"] += 1
                        except Exception as e:
                            print(f"[Setup] Error creating text channel {ch_name}: {e}")
                            continue
                    else:
                        if text_ch.category != category:
                            await text_ch.edit(category=category, topic=topic)
                    created_channels[ch_name] = text_ch

                elif ch_type == "voice":
                    user_limit = ch_data.get("user_limit", 0)
                    vc = discord.utils.get(guild.voice_channels, name=ch_name)
                    if not vc:
                        try:
                            vc = await guild.create_voice_channel(
                                name=ch_name,
                                category=category,
                                user_limit=user_limit,
                                reason="Grand Knox Voice Frequency Construction"
                            )
                            log["channels_created"] += 1
                        except Exception as e:
                            print(f"[Setup] Error creating voice channel {ch_name}: {e}")
                            continue
                    else:
                        if vc.category != category:
                            await vc.edit(category=category, user_limit=user_limit)
                    created_channels[ch_name] = vc

                await asyncio.sleep(0.3)

        # 4. Deploy Aesthetic Messages & Embeds
        if status_callback:
            await status_callback("🎨 **Phase 3/3**: Broadcasting Protocol Manifests & Interactive Terminals...")

        await self._deploy_embeds(guild, created_channels, log)

        return True, log

    async def _deploy_embeds(self, guild: discord.Guild, channels: Dict[str, discord.abc.GuildChannel], log: dict):
        """Deploys aesthetic lore, rules, and interactive panels."""

        # 1. #rules
        ch_rules = channels.get("📜・rules") or discord.utils.get(guild.text_channels, name="📜・rules") or discord.utils.get(guild.text_channels, name="📜・survival-protocol")
        if ch_rules and isinstance(ch_rules, discord.TextChannel):
            async for m in ch_rules.history(limit=5):
                if m.author == self.bot.user:
                    break
            else:
                embed_rules = discord.Embed(
                    title="📜 THE GRAND KNOX — SERVER RULES & GUIDELINES",
                    description=(
                        "**WELCOME TO THE GRAND KNOX**\n"
                        "*Survival requires discipline, vigilance, and cooperation.*\n\n"
                        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        "  **RULE 1: NO UNPROVOKED GRIEFING**\n"
                        "  Unprovoked destruction of claimed player safehouses, theft of claimed generator fuel, "
                        "  or sabotaging farm crops outside designated PvP zones is strictly prohibited.\n\n"
                        "  **RULE 2: COMBAT CONDUCT & DISCORD ETIQUETTE**\n"
                        "  • No combat logging (disconnecting while being chased by hordes or in PvP).\n"
                        "  • Hate speech, racism, slurs, and toxic harassment will result in immediate bans.\n"
                        "  • Keep mic spam out of voice channels.\n\n"
                        "  **RULE 3: SAFEHOUSE REGISTRATION**\n"
                        "  All community factions must register their safehouse in <#tickets> "
                        "  to receive official protection.\n\n"
                        "  **RULE 4: VEHICLE PROTOCOL**\n"
                        "  Do not abandon damaged vehicles blocking major highway chokepoints.\n\n"
                        "  **RULE 5: REPORTING ISSUES**\n"
                        "  If you encounter server desync, rule breakers, or missing items due to game crashes, "
                        "  open a ticket in <#tickets>.\n"
                        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
                    ),
                    color=config.KnoxColors.CORDON_RED
                )
                embed_rules.set_footer(text="The Grand Knox • Server Administration")
                await ch_rules.send(embed=embed_rules)
                log["panels_deployed"] += 1

        # 2. #modpack (Mods & Connection Info)
        ch_mods = channels.get("📦・modpack") or discord.utils.get(guild.text_channels, name="📦・modpack") or discord.utils.get(guild.text_channels, name="📦・modpack-intel")
        if ch_mods and isinstance(ch_mods, discord.TextChannel):
            async for m in ch_mods.history(limit=5):
                if m.author == self.bot.user:
                    break
            else:
                embed_mods = discord.Embed(
                    title="📦 THE GRAND KNOX — WORKSHOP MODPACK & ASSETS",
                    description=(
                        "To guarantee high immersion, balanced survival, and true 1993 Kentucky atmosphere, "
                        "The Grand Knox runs a curated modpack.\n\n"
                        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        "  **KEY ENHANCEMENTS LOADED:**\n"
                        "  • 🚗 **Expanded 1993 Vehicles**: Period-accurate sedans, trucks, and ambulances\n"
                        "  • 🪓 **Deep Crafting & Carpentry**: Additional fortifications, gates, and defenses\n"
                        "  • 📻 **Authentic Emergency Radio Overhaul**: Realistic frequency mechanics\n"
                        "  • 🩺 **Expanded Medical & First Aid**: Advanced wound treatment and surgeries\n"
                        "  • 🗺️ **High-Res Cartography**: Detailed maps and compass waypoints\n"
                        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                        f"🔗 **[Click Here to Subscribe to the Steam Workshop Collection]({config.PZ_MODPACK_URL})**\n\n"
                        "*Note: You do not need to manually install files — Steam will automatically download all required mods upon connecting to our server!*"
                    ),
                    color=config.KnoxColors.PATROL_BLUE
                )
                embed_mods.set_footer(text="The Grand Knox • Logistics & Mod Directorate")
                await ch_mods.send(embed=embed_mods)
                log["panels_deployed"] += 1

        # 3. #server-map (Cartography)
        ch_map = channels.get("🗺️・server-map") or discord.utils.get(guild.text_channels, name="🗺️・server-map") or discord.utils.get(guild.text_channels, name="🗺️・exclusion-map")
        if ch_map and isinstance(ch_map, discord.TextChannel):
            async for m in ch_map.history(limit=5):
                if m.author == self.bot.user:
                    break
            else:
                embed_cart = discord.Embed(
                    title="🗺️ KNOX COUNTY CARTOGRAPHY & SECTOR INTEL",
                    description=(
                        "Survey the terrain before embarking on supply runs:\n\n"
                        "• **Muldraugh** (`10625 x 9750`): Heavy hardware warehouses, large police arsenal, dangerous highway choke.\n"
                        "• **West Point** (`11850 x 6850`): Gun store, dense downtown, river access, high infected concentrations.\n"
                        "• **Rosewood** (`8150 x 11550`): Fire station axes, police station, penitentiary, low density.\n"
                        "• **Riverside** (`6350 x 5350`): Unlimited water, pharmacy, country club, vehicle spawns.\n"
                        "• **Louisville** (`12500 x 2500`): Megalopolis, infinite loot, breached military cordon, fatal danger.\n\n"
                        "Use `/map [town]` in <#bot-commands> anytime for deep sector analysis and direct map links!"
                    ),
                    color=config.KnoxColors.MILITARY_OLIVE
                )
                embed_cart.set_footer(text="The Grand Knox • Cartography")
                await ch_map.send(embed=embed_cart)
                log["panels_deployed"] += 1

        # 4. #roles (Role Picker)
        ch_roles = channels.get("🎭・roles") or discord.utils.get(guild.text_channels, name="🎭・roles") or discord.utils.get(guild.text_channels, name="🎭・survivor-specialties")
        if ch_roles and isinstance(ch_roles, discord.TextChannel):
            async for m in ch_roles.history(limit=5):
                if m.author == self.bot.user and m.components:
                    break
            else:
                embed_roles = discord.Embed(
                    title="🎭 SURVIVOR SPECIALTIES & NOTIFICATION ROLES",
                    description=(
                        "Configure your roles and choose notification alerts.\n\n"
                        "**1. Trade Skill / Profession Selection:**\n"
                        "Signal your strengths to factions and safehouse groups (Medic, Carpenter, Marksman, Mechanic, etc.).\n\n"
                        "**2. Notification Frequencies:**\n"
                        "Choose which alerts ping you for major community announcements, horde night events, or server wipes.\n\n"
                        "*Use the dropdown menus below to toggle roles at will.*"
                    ),
                    color=config.KnoxColors.RADIO_CYAN
                )
                embed_roles.set_footer(text="The Grand Knox • Roles & Perks")
                await ch_roles.send(embed=embed_roles, view=SurvivorRolesView())
                log["panels_deployed"] += 1

        # 5. #tickets (Tickets & Claims)
        ch_support = channels.get("🎫・tickets") or discord.utils.get(guild.text_channels, name="🎫・tickets") or discord.utils.get(guild.text_channels, name="🎫・support-and-claims")
        if ch_support and isinstance(ch_support, discord.TextChannel):
            async for m in ch_support.history(limit=5):
                if m.author == self.bot.user and m.components:
                    break
            else:
                embed_support = discord.Embed(
                    title="🎫 SUPPORT & SAFEHOUSE CLAIMS",
                    description=(
                        "Need assistance from staff or want to claim a base?\n\n"
                        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
                        "  🏡 **Claim Safehouse**: Register your faction base and zoning coordinates.\n"
                        "  🚨 **Report Griefing**: Report base raiding, stolen vehicles, or rule infractions.\n"
                        "  ❓ **Survivor Support**: Get technical help with mods, desyncs, or character bugs.\n"
                        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                        "*Clicking an option below opens a private ticket with staff.*"
                    ),
                    color=config.KnoxColors.PATROL_BLUE
                )
                embed_support.set_footer(text="The Grand Knox • Support System")
                await ch_support.send(embed=embed_support, view=TicketHubView())
                log["panels_deployed"] += 1

        # 6. #general (Welcome Message)
        ch_lounge = channels.get("💬・general") or discord.utils.get(guild.text_channels, name="💬・general") or discord.utils.get(guild.text_channels, name="💬・survivor-lounge")
        if ch_lounge and isinstance(ch_lounge, discord.TextChannel):
            async for m in ch_lounge.history(limit=5):
                if m.author == self.bot.user:
                    break
            else:
                embed_welcome = discord.Embed(
                    title="🏕️ SAFE HAVEN COMMONS OPEN",
                    description=(
                        "Welcome behind the perimeter wire, survivors.\n\n"
                        "Pull up a chair by the campfire, share your harrowing encounters with the dead, "
                        "recruit comrades for your next Louisville run, or trade goods.\n\n"
                        "*Stay vigilant, boil your water, and keep your shotgun loaded.*"
                    ),
                    color=config.KnoxColors.SURVIVOR_GREEN
                )
                await ch_lounge.send(embed=embed_welcome)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupServerCog(bot))
