# ☣️ The Grand Knox — Project Zomboid Discord Automation & Server Suite

> **"This is how you died."** — July 1993, Knox County Exclusion Zone, Kentucky.

A comprehensive, atmospheric, and fully automated Discord server system and custom bot named **Grand Knox**, designed specifically for hardcore *Project Zomboid* communities, roleplay servers, and survivor factions.

---

## 🌟 Key Features

### 1. 🏗️ Instant One-Click Server Architect
- **Fully Automated Provisioning**: Execute one command (`/setup-server` or `python run_setup_standalone.py`) to build the entire Discord server in seconds.
- **Hierarchical Role Matrix**: Military High Command, Knox County Marshals, Veteran Survivors, Knox Survivors, Quarantine Intake, Isolated/Infected, 7 Survivor Specialties, and 4 Emergency Notification frequencies.
- **Granular Permission Isolation**: Unverified survivors cannot view or speak in safe haven channels until biological clearance is completed at the checkpoint.
- **Atmospheric 1993 Theme**: Custom military emergency color palette (`Biohazard Crimson`, `Cordon Olive`, `Hazard Amber`, `Radio Wave Cyan`), clean unicode border framing, and retro typography.

### 2. 🪪 Automated Quarantine Checkpoint (Verification Gate)
- **ID Check & Protocol Button**: In `#border-checkpoint`, new arrivals click an interactive button to agree to the survival protocol.
- **Instant Role Swap**: Grants `🌲 Knox Survivor`, revokes `☣️ Quarantine Arrival`, and instantly unlocks all public safe haven channels.
- **Arrivals Manifest**: Automatically logs entry timestamps, survivor tags (`KZ-XXXX`), and avatars in `#manifest-arrivals`.

### 3. 🎭 Interactive Trade Specialties & Frequencies
- **Survivor Specialties Dropdown**: Self-assign up to 3 operational trade skills (`Field Medic`, `Master Carpenter`, `Woodland Scavenger`, `Marksman`, `Grease Monkey`, `Rural Farmer`, `Electrician`).
- **Emergency Notification Frequency Dropdown**: Toggle pings for server announcements, horde night invasions, restarts/wipes, or radio broadcasts.

### 4. 🟢 Live Project Zomboid Server Telemetry
- **Native Valve A2S UDP Client**: Queries live player counts, maximum capacity, map, and latency directly from your Project Zomboid dedicated server.
- **Auto-Refreshing Status Embed**: Constantly updates `#server-status` every 2 minutes without chat spam.
- **Slash Commands**:
  - `/status`: Instant telemetry sweep and ping test.
  - `/serverinfo`: Complete direct connect dossier (`steam://connect/IP:PORT`), password, and modpack links.

### 5. 🏡 Safehouse Claims & Incident Reporting
- **Persistent Ticket Panel**: Located in `#support-and-claims` with 3 automated modal intake forms:
  - 🏡 *Safehouse Base Claim*: Register base coordinates, names, and faction occupants.
  - 🚨 *Report Griefing / Infraction*: Report base raiding, stolen armored cars, or rule breakers with evidence.
  - ❓ *Survivor Technical Support*: Inquire about mod mismatch, desyncs, or character bugs.
- **Confidential Dockets**: Automatically spawns a private thread between the claimant and staff.
- **One-Click Transcript Archiving**: Automatically logs formatted message history to `#transcripts-archive` upon resolution.

### 6. 📻 Emergency Broadcast System (AEBS) & Guide
- `/map [town]`: Interactive POI guide and direct links into the Project Zomboid Interactive Map for Muldraugh, West Point, Rosewood, Riverside, Louisville, and March Ridge.
- `/broadcast [preset]`: Transmit authentic 1993 Emergency Broadcast System radio messages with retro teletype styling, weather telemetry, and siren cues.
- `/trait [name]`: Instant lookup of survivor trait costs, mechanics, and meta ratings (Dextrous, Keen Hearing, Athletic, Strong, Smoker, etc.).

---

## 📁 File Structure

```text
the-grand-knox/
├── .env.example               # Template for bot token, guild ID, and PZ server info
├── requirements.txt           # Python dependencies (discord.py, python-dotenv, aiohttp)
├── config.py                  # Core blueprints: roles, channel layouts, colors, maps, AEBS
├── bot.py                     # Main bot client with persistent views and slash command sync
├── run_setup_standalone.py    # Standalone terminal runner to provision the server in one click
├── README.md                  # Complete documentation and setup manual
└── cogs/
    ├── setup_server.py        # Automated server builder engine (/setup-server)
    ├── verification.py        # Quarantine gate button & arrivals manifest
    ├── roles.py               # Interactive specialties & alert frequency pickers
    ├── pz_monitor.py          # Real-time A2S telemetry monitor & status embeds
    ├── tickets.py             # Safehouse base claims & incident reporting modals
    └── survival_guide.py      # /map, /trait, and Emergency Broadcast System
```

---

## 🚀 Setup & Installation Guide

### Step 1: Create Your Discord Bot
1. Navigate to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Click **New Application** -> Name it **Grand Knox** (or your preferred name).
3. Under the **Bot** tab:
   - Click **Add Bot** / **Reset Token** and copy your **Bot Token**.
   - Scroll down to **Privileged Gateway Intents** and enable:
     - ✅ **Server Members Intent**
     - ✅ **Message Content Intent**
   - Click **Save Changes**.

### Step 2: Invite Bot to Your Discord Server
1. Go to **OAuth2** -> **URL Generator**.
2. Select Scopes: `bot`, `applications.commands`.
3. Select Bot Permissions: `Administrator`.
4. Copy the generated URL, open it in your browser, and authorize the bot into your Discord server.

### Step 3: Configure Environment Variables
1. Inside `the-grand-knox`, duplicate `.env.example` and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your details:
   ```env
   DISCORD_TOKEN=your_copied_bot_token_here
   GUILD_ID=your_discord_server_id_here
   PZ_SERVER_IP=127.0.0.1
   PZ_SERVER_PORT=16261
   PZ_QUERY_PORT=16261
   PZ_SERVER_NAME=The Grand Knox | Hardcore Survival & RP
   PZ_SERVER_PASSWORD=None (Open Public)
   PZ_MODPACK_URL=https://steamcommunity.com/sharedfiles/filedetails/?id=000000000
   ```
   *(To get your `GUILD_ID`: In Discord, enable Developer Mode under User Settings -> Advanced, right-click your server icon, and select **Copy Server ID**).*

### Step 4: Run the Automated Server Provisioner
You can provision the entire server using either method:

#### Option A: Run via Terminal (Easiest)
Run the standalone setup script:
```powershell
python run_setup_standalone.py
```
*This connects immediately, builds all roles, constructs all categories/channels, applies all permission locks, and posts the interactive embeds!*

#### Option B: Run via Slash Command
1. Start the main bot:
   ```powershell
   python bot.py
   ```
2. In your Discord server, type:
   ```text
   /setup-server
   ```
3. Watch as the bot automatically constructs the entire server with live progress indicators.

---

### Step 5: Critical Role Hierarchy Placement
After provisioning:
1. In Discord, go to **Server Settings** -> **Roles**.
2. Locate the **`Grand Knox AI`** (or your bot's integration role).
3. **Drag it above** `🌲 Knox Survivor` and `☣️ Quarantine Arrival`.
   *(Discord requires the bot's highest role to be above the roles it gives out to other members).*

---

## 🛠️ Bot Slash Commands Reference

| Command | Permission | Description |
| :--- | :--- | :--- |
| `/setup-server` | Administrator | Fully provisions or refreshes server layout, roles, and embeds. |
| `/status` | Public | Real-time Project Zomboid server telemetry (players, map, ping). |
| `/serverinfo` | Public | Full connection parameters, IP, port, password, and modpack links. |
| `/map [town]` | Public | Sector cartography, loot POIs, coordinates, and map project links. |
| `/trait [name]` | Public | Look up Project Zomboid traits, costs, mechanics, and survival tier ratings. |
| `/broadcast` | Staff (Manage Msgs) | Send 1993 Emergency Broadcast System radio teletypes (Chopper, Blackout, Horde). |

---

## 🛡️ Role Hierarchy & Access Architecture

```text
[TOP OF HIERARCHY]
  ⚜️ Military High Command     --> Server Owner & Root Administrators
  🛡️ Knox County Marshals      --> Moderation & Law Enforcement
  🤖 Grand Knox AI             --> Bot Automation Core
  📻 Emergency Dispatch        --> Utility Webhooks & System Alerts
  ─── SURVIVOR CLEARANCE ───
  🎖️ Veteran Survivor          --> Boosters & Trusted Community Members
  🌲 Knox Survivor             --> VERIFIED: Full access to chat & voice
  ☣️ Quarantine Arrival        --> UNVERIFIED: Confined to #border-checkpoint
  🔇 Isolated / Infected       --> TIMEOUT: Muted across all channels
  ─── SURVIVOR SPECIALTIES ───
  🩺 Field Medic               --> Surgery & First Aid
  🔨 Master Carpenter          --> Fortifications & Base Construction
  🪓 Woodland Scavenger        --> Foraging, Trapping, Axes
  🎯 Marksman / Hunter         --> Firearms & Perimeter Defense
  🚗 Grease Monkey             --> Vehicle Mechanics & Hotwiring
  🌾 Rural Farmer              --> Crops & Water Sustainability
  ⚡ Electrician               --> Generators & Power Systems
  ─── TRANSMISSION ALERTS ───
  📢 Cordon Announcements      --> Official Updates
  🧟 Knox Horde Invasions      --> In-game Horde Night & Events
  🛠️ Server Restarts & Wipes   --> Maintenance & Wipe Notices
  📻 Radio Broadcasts          --> AEBS Lore Transmissions
[BOTTOM OF HIERARCHY]
```
