#!/bin/bash
# Register slash commands with Discord

CLIENT_ID="YOUR_DISCORD_CLIENT_ID"
BOT_TOKEN="YOUR_BOT_TOKEN"
GUILD_ID="YOUR_TEST_GUILD_ID"  # Optional: for guild-specific commands

echo "🔧 Registering slash commands for One Piece Bot"

# Register command: /sail
curl -X POST \
  -H "Authorization: Bot $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "sail",
    "description": "⭐ Begin your One Piece adventure",
    "type": 1
  }' \
  "https://discord.com/api/v10/applications/$CLIENT_ID/commands"

# Register command: /crew
curl -X POST \
  -H "Authorization: Bot $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "crew",
    "description": "⭐ View your current crew",
    "type": 1
  }' \
  "https://discord.com/api/v10/applications/$CLIENT_ID/commands"

# Register command: /continue
curl -X POST \
  -H "Authorization: Bot $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "continue",
    "description": "📺 Continue the story",
    "type": 1
  }' \
  "https://discord.com/api/v10/applications/$CLIENT_ID/commands"

# Register command: /bounty
curl -X POST \
  -H "Authorization: Bot $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "bounty",
    "description": "💰 Check your bounty",
    "type": 1
  }' \
  "https://discord.com/api/v10/applications/$CLIENT_ID/commands"

# Register command: /episodes
curl -X POST \
  -H "Authorization: Bot $BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "episodes",
    "description": "📺 List all episodes",
    "type": 1
  }' \
  "https://discord.com/api/v10/applications/$CLIENT_ID/commands"

echo "✅ Slash commands registered!"