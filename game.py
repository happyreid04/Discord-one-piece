import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

# ========== AI CONFIGURATION ==========
# You can plug in OpenAI, Local LLM, or free API here
AI_ENABLED = False  # Set to True when you have API key
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_API_URL = os.getenv('AI_API_URL', 'https://api.openai.com/v1/chat/completions')

# ========== GAME DATA FILE ==========
DATA_FILE = 'data/players.json'

def load_players():
    """Load player data from JSON file"""
    if not os.path.exists(DATA_FILE):
        os.makedirs('data', exist_ok=True)
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_players(data):
    """Save player data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ========== EPISODE DATA ==========
EPISODES = {
    1: {
        'name': 'Setting Sail',
        'description': 'The journey for the greatest treasure begins at Dawn Island docks.',
        'scenes': [
            {
                'id': 'meet_boat_builder',
                'text': "**🛠️ Boat Builder:** *'Captain! The ship is ready. But where are we heading?'*",
                'choices': [
                    {'text': '🏴‍☠️ "We hunt the One Piece!"', 'next_scene': 'fish_kingdom_warning', 'stat_change': {'bounty': 10000}},
                    {'text': '🌊 "To the Grand Line!"', 'next_scene': 'fish_kingdom_warning', 'stat_change': {'bounty': 5000}},
                    {'text': '🗺️ "First, we need a navigator."', 'next_scene': 'wait_navigator', 'stat_change': {}}
                ]
            },
            {
                'id': 'fish_kingdom_warning',
                'text': "**🐟 Fish Soldier emerges from water:** *'Turn back, human! The Fish Kingdom claims these waters!'*\n\n⚔️ **COMBAT INITIATED!**",
                'choices': [
                    {'text': '💪 "Gomu Gomu no Punch!" (Use rubber powers)', 'next_scene': 'victory', 'stat_change': {'bounty': 25000}},
                    {'text': '🥷 "Ninja, handle this!"', 'next_scene': 'victory', 'stat_change': {'bounty': 15000}},
                    {'text': '🏃 "Retreat to the ship!"', 'next_scene': 'retreat', 'stat_change': {}}
                ]
            },
            {
                'id': 'victory',
                'text': "**VICTORY!** The Fish Soldiers retreat to the depths.\n\n*'The Fish Kingdom knows we're coming...'*",
                'choices': [
                    {'text': '➡️ Continue to Episode 2', 'next_scene': 'episode_end', 'stat_change': {}}
                ]
            },
            {
                'id': 'retreat',
                'text': "You escape to open sea. The Fish Kingdom now knows your face.\n\n*'We'll need a better plan...'*",
                'choices': [
                    {'text': '➡️ Regroup and continue', 'next_scene': 'episode_end', 'stat_change': {}}
                ]
            },
            {
                'id': 'wait_navigator',
                'text': "**Boat Builder:** *'Smart thinking, Captain. I know a town nearby...'*",
                'choices': [
                    {'text': '➡️ Sail to the town', 'next_scene': 'episode_end', 'stat_change': {}}
                ]
            },
            {
                'id': 'episode_end',
                'text': "**📺 END OF EPISODE 1**\n\n*To be continued...*\n\nThe crew sails toward the unknown, the Fish Kingdom in pursuit, and somewhere out there... the Map Drawer waits.",
                'choices': [],
                'is_end': True
            }
        ]
    },
    2: {
        'name': 'The Open Sea',
        'description': 'Days pass on the endless blue. Something approaches on the horizon...',
        'scenes': [
            {
                'id': 'open_ocean',
                'text': "**⭐ You:** *'Land? Anyone?'*\n\n**🛠️ Boat Builder:** *'Nothing yet, Captain. But the sea feels... strange.'*\n\nThe water churns. Something large swims beneath.",
                'choices': [
                    {'text': '🔍 "Everyone on alert!"', 'next_scene': 'sea_king', 'stat_change': {}},
                    {'text': '🎣 "Let\'s fish. I\'m hungry."', 'next_scene': 'fish_catches', 'stat_change': {}}
                ]
            },
            {
                'id': 'sea_king',
                'text': "**🐉 A SEA KING erupts from the water!**\n\n*'ROOOOAR!'* It's massive – bigger than your ship!\n\n**🥷 Ninja:** *'Captain! What do we do?!'*",
                'choices': [
                    {'text': '💪 Stretch and punch it!', 'next_scene': 'sea_king_escape', 'stat_change': {'bounty': 50000}},
                    {'text': '🏃 Outrun it!', 'next_scene': 'sea_king_escape', 'stat_change': {}},
                    {'text': '🤝 Try to communicate', 'next_scene': 'sea_king_friendly', 'stat_change': {}}
                ]
            },
            {
                'id': 'sea_king_escape',
                'text': "After a desperate struggle, you escape! The Sea King dives back into the depths.\n\n**⭐ You:** *'That was too close... We need to get stronger.'*\n\nA small island appears on the horizon. Smoke rises from a town.",
                'choices': [
                    {'text': '🏝️ Head to the island', 'next_scene': 'episode_end', 'stat_change': {}}
                ]
            },
            {
                'id': 'sea_king_friendly',
                'text': "**🐉 Sea King:** *'...You're not afraid of me?'*\n\nIt speaks! This Sea King is intelligent. It reveals the location of a hidden island – where a legendary Map Drawer lives.",
                'choices': [
                    {'text': '🗺️ "Take us there!"', 'next_scene': 'episode_end', 'stat_change': {'bounty': 30000}}
                ]
            },
            {
                'id': 'fish_catches',
                'text': "**⭐ You:** *'Not bad, Boat Builder!'*\n\n**🐟 Fish Soldier (in the catch):** *'...You caught me. Please don't eat me. I can tell you about the Fish Kingdom...'*",
                'choices': [
                    {'text': '🗣️ "Talk. Now."', 'next_scene': 'fish_intel', 'stat_change': {}},
                    {'text': '🍳 "Dinner is dinner."', 'next_scene': 'episode_end', 'stat_change': {'bounty': -5000}}
                ]
            },
            {
                'id': 'fish_intel',
                'text': "**🐟 Fish Soldier:** *'The Fish King wants the One Piece. He has half a map. Your crew has the other half – with the Map Drawer... but you haven't found her yet. Find her before he does!'*",
                'choices': [
                    {'text': '🏃 "We sail faster!"', 'next_scene': 'episode_end', 'stat_change': {}}
                ]
            },
            {
                'id': 'episode_end',
                'text': "**📺 END OF EPISODE 2**\n\n*To be continued...*\n\nThe Map Drawer is out there. The Fish Kingdom is closer than ever.",
                'choices': [],
                'is_end': True
            }
        ]
    }
}

# ========== SLASH COMMAND COG ==========
class GameCog(commands.Cog):
    """One Piece Game Commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.players = load_players()
    
    @app_commands.command(name="sail", description="⭐ Begin your One Piece adventure")
    async def sail(self, interaction: discord.Interaction):
        """Start the game"""
        user_id = str(interaction.user.id)
        
        if user_id in self.players:
            embed = discord.Embed(
                title="🏴‍☠️ ALREADY SAILING",
                description=f"{interaction.user.display_name}, your journey has already begun!",
                color=0xFFA500
            )
            embed.add_field(name="Current Episode", value=f"Episode {self.players[user_id]['episode']}", inline=True)
            embed.add_field(name="Bounty", value=f"{self.players[user_id]['bounty']:,} Berries", inline=True)
            await interaction.response.send_message(embed=embed)
            return
        
        # Create new player
        self.players[user_id] = {
            'name': interaction.user.display_name,
            'episode': 1,
            'scene': 'meet_boat_builder',
            'bounty': 0,
            'crew': {
                'boat_builder': True,
                'ninja': False,
                'map_drawer': False
            },
            'rubber_powers': True,
            'completed': [],
            'started_at': datetime.now().isoformat()
        }
        save_players(self.players)
        
        embed = discord.Embed(
            title="⭐ YOUR ADVENTURE BEGINS ⭐",
            description=f"**{interaction.user.display_name}** has eaten the **Gomu Gomu no Mi** (Rubber Fruit) and set sail!",
            color=0xFF4500
        )
        embed.add_field(name="Crew", value="⭐ You (Rubber Human)\n🛠️ Boat Builder\n❌ Ninja (missing)\n❌ Map Drawer (missing)", inline=False)
        embed.add_field(name="Location", value="Dawn Island Docks", inline=True)
        embed.add_field(name="Episode", value="1 - Setting Sail", inline=True)
        embed.set_footer(text="Use /continue to begin your story!")
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"New player: {interaction.user.display_name}")
    
    @app_commands.command(name="crew", description="⭐ View your current crew")
    async def crew(self, interaction: discord.Interaction):
        """Show crew status"""
        user_id = str(interaction.user.id)
        
        if user_id not in self.players:
            await interaction.response.send_message("❌ You haven't started yet! Use `/sail` first.")
            return
        
        p = self.players[user_id]
        
        embed = discord.Embed(
            title=f"⭐ {p['name']}'S CREW",
            color=0x00BFFF
        )
        
        crew_status = []
        crew_status.append("✅ **Boat Builder** (Shipwright)")
        crew_status.append("✅ **You** (Rubber Fruit User)")
        crew_status.append("❌ **Ninja** (Not recruited yet)")
        crew_status.append("❌ **Map Drawer** (Episode 3)")
        
        embed.add_field(name="👥 Crew Members", value="\n".join(crew_status), inline=False)
        embed.add_field(name="💰 Bounty", value=f"{p['bounty']:,} Berries", inline=True)
        embed.add_field(name="📺 Episode", value=p['episode'], inline=True)
        embed.add_field(name="🏝️ Location", value="Grand Line - Unknown Seas", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="continue", description="📺 Continue the story")
    async def continue_story(self, interaction: discord.Interaction):
        """Play next scene"""
        user_id = str(interaction.user.id)
        
        if user_id not in self.players:
            await interaction.response.send_message("❌ Use `/sail` to start your adventure first!")
            return
        
        player = self.players[user_id]
        current_ep = player['episode']
        current_scene_id = player.get('scene', 'meet_boat_builder')
        
        # Get episode data
        ep_data = EPISODES.get(current_ep)
        if not ep_data:
            await interaction.response.send_message("🌊 **To be continued...** More episodes are being written!")
            return
        
        # Find current scene
        current_scene = None
        for scene in ep_data['scenes']:
            if scene['id'] == current_scene_id:
                current_scene = scene
                break
        
        if not current_scene:
            current_scene = ep_data['scenes'][0]
        
        # Build embed
        embed = discord.Embed(
            title=f"📺 EPISODE {current_ep} - {ep_data['name']}",
            description=current_scene['text'],
            color=0xFF4500
        )
        
        if current_scene['choices']:
            choice_text = []
            for i, choice in enumerate(current_scene['choices'], 1):
                choice_text.append(f"{i}️⃣ {choice['text']}")
            embed.add_field(name="⚡ YOUR CHOICE", value="\n".join(choice_text), inline=False)
            embed.set_footer(text="Reply with the number of your choice (1, 2, or 3)")
            
            # Store awaiting choice
            self.bot.awaiting_choice[user_id] = {
                'scene': current_scene,
                'episode': current_ep
            }
        else:
            embed.set_footer(text="End of episode. /continue for next episode...")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="bounty", description="💰 Check your bounty")
    async def bounty(self, interaction: discord.Interaction):
        """Show current bounty"""
        user_id = str(interaction.user.id)
        
        if user_id not in self.players:
            await interaction.response.send_message("❌ Start with `/sail` first!")
            return
        
        bounty = self.players[user_id]['bounty']
        
        if bounty < 100000:
            rank = "🪙 Rookie Pirate"
            color = 0x808080
        elif bounty < 500000:
            rank = "⚔️ Super Rookie"
            color = 0x00BFFF
        elif bounty < 1000000:
            rank = "💀 Warlord Tier"
            color = 0x800080
        else:
            rank = "👑 Emperor Level"
            color = 0xFFD700
        
        embed = discord.Embed(
            title="💰 BOUNTY POSTER 💰",
            description=f"**WANTED: {self.players[user_id]['name']}**\n\n{bounty:,} BERRIES",
            color=color
        )
        embed.add_field(name="Rank", value=rank, inline=True)
        embed.add_field(name="Devil Fruit", value="Gomu Gomu no Mi (Rubber)", inline=True)
        embed.set_footer(text="The World Government is watching...")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="help", description="🏴‍☠️ Show all commands")
    async def help_cmd(self, interaction: discord.Interaction):
        """Help menu"""
        embed = discord.Embed(
            title="🏴‍☠️ ONE PIECE BOT - COMMANDS 🏴‍☠️",
            description="Your journey to find the One Piece begins here!",
            color=0xFFD700
        )
        embed.add_field(name="/sail", value="Begin your adventure", inline=False)
        embed.add_field(name="/crew", value="View your crew", inline=False)
        embed.add_field(name="/continue", value="Continue the story", inline=False)
        embed.add_field(name="/bounty", value="Check your bounty", inline=False)
        embed.add_field(name="/help", value="Show this menu", inline=False)
        embed.set_footer(text="⚡ Episode 3: The Map Drawer - Coming Soon!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="episodes", description="📺 List all episodes")
    async def episodes(self, interaction: discord.Interaction):
        """Show episode list"""
        embed = discord.Embed(
            title="📺 ONE PIECE - EPISODE LIST",
            description="Your adventure so far...",
            color=0xFF6347
        )
        
        for ep_num, ep_data in EPISODES.items():
            status = "🟢 Available" if ep_num <= self.players.get(str(interaction.user.id), {}).get('episode', 1) else "🔒 Coming Soon"
            embed.add_field(
                name=f"Episode {ep_num}: {ep_data['name']}",
                value=f"{ep_data['description']}\n{status}",
                inline=False
            )
        
        embed.set_footer(text="Episode 3 introduces the Map Drawer!")
        await interaction.response.send_message(embed=embed)

# ========== SETUP ==========
async def setup(bot):
    await bot.add_cog(GameCog(bot))
    # Store awaiting choices
    bot.awaiting_choice = {}
    logger.info("✅ Game cog loaded")