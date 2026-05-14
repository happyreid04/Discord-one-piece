import discord
from discord.ext import commands
import asyncio
import logging
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load configuration
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='🏴‍☠️ [%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PREFIX = 'op!'  # One Piece command prefix

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# Game state (temporary - will move to database later)
active_crews = {}
episode_progress = {}

# ========== EVENTS ==========

@bot.event
async def on_ready():
    """Bot is alive and sailing"""
    logger.info(f"⚓ {bot.user} HAS SET SAIL FOR THE GRAND LINE!")
    logger.info(f"🌊 Serving {len(bot.guilds)} guilds")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🌊 The One Piece | op!help"
        )
    )
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f"⚡ Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"Slash sync failed: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Handle errors gracefully"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ That's not a known command. Try `op!help`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🔒 You don't have permission for that.")
    else:
        logger.error(f"Command error: {error}")
        await ctx.send("💀 Something went wrong. Our shipwright is fixing it.")

# ========== CORE COMMANDS ==========

@bot.command(name='start', aliases=['begin', 'sail'])
async def start_game(ctx):
    """Begin your One Piece adventure"""
    user_id = str(ctx.author.id)
    
    if user_id in active_crews:
        await ctx.send(f"🏴‍☠️ **{ctx.author.display_name}**! Your crew is already sailing! Use `op!crew` to see them.")
        return
    
    # Create new crew
    active_crews[user_id] = {
        'captain': ctx.author.display_name,
        'crew': {
            'star': {'name': ctx.author.display_name, 'fruit': 'Rubber', 'bounty': 0},
            'boat_builder': 'Not recruited',
            'ninja': 'Not recruited',
            'map_drawer': 'Unknown (episode 3)'
        },
        'location': 'Dawn Island',
        'episode': 1,
        'bounty': 0,
        'treasure_found': 0
    }
    
    embed = discord.Embed(
        title="🏴‍☠️ YOUR ADVENTURE BEGINS 🏴‍☠️",
        description=f"**{ctx.author.display_name}** has formed a crew and set sail!",
        color=0xFF4500
    )
    embed.add_field(name="Crew Name", value="The Straw Hearts", inline=True)
    embed.add_field(name="Location", value="Dawn Island", inline=True)
    embed.add_field(name="Episode", value="1 - Setting Sail", inline=False)
    embed.add_field(name="Current Crew", value="⭐ The Star (You)\n❌ Boat Builder (missing)\n❌ Ninja (missing)\n❓ Map Drawer (unknown)", inline=False)
    embed.set_footer(text="Type op!continue to begin Episode 1")
    
    await ctx.send(embed=embed)
    logger.info(f"New crew formed: {ctx.author.display_name}")

@bot.command(name='crew')
async def show_crew(ctx):
    """Show your current crew"""
    user_id = str(ctx.author.id)
    
    if user_id not in active_crews:
        await ctx.send(f"❌ **{ctx.author.display_name}**, you haven't started your journey yet. Type `op!start` first!")
        return
    
    crew_data = active_crews[user_id]
    
    embed = discord.Embed(
        title=f"⭐ {crew_data['captain']}'s CREW",
        description=f"**Bounty:** {crew_data['bounty']:,} Berries",
        color=0x00BFFF
    )
    
    embed.add_field(name="⭐ The Star", value=f"{crew_data['crew']['star']['name']}\nRubber Fruit", inline=True)
    embed.add_field(name="🛠️ Boat Builder", value=crew_data['crew']['boat_builder'], inline=True)
    embed.add_field(name="🥷 Ninja", value=crew_data['crew']['ninja'], inline=True)
    embed.add_field(name="🗺️ Map Drawer", value=crew_data['crew']['map_drawer'], inline=True)
    embed.add_field(name="📍 Location", value=crew_data['location'], inline=True)
    embed.add_field(name="📺 Episode", value=crew_data['episode'], inline=True)
    embed.add_field(name="💎 Treasure", value=f"{crew_data['treasure_found']} pieces", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='continue', aliases=['next', 'play'])
async def continue_game(ctx):
    """Continue your adventure to the next scene"""
    user_id = str(ctx.author.id)
    
    if user_id not in active_crews:
        await ctx.send(f"❌ **{ctx.author.display_name}**, start your journey with `op!start`")
        return
    
    ep = active_crews[user_id]['episode']
    
    # Episode routing
    if ep == 1:
        await episode_one(ctx, user_id)
    elif ep == 2:
        await episode_two(ctx, user_id)
    else:
        await ctx.send("🌊 **To be continued...** More episodes are being written!")

@bot.command(name='bounty')
async def check_bounty(ctx):
    """Check your current bounty"""
    user_id = str(ctx.author.id)
    
    if user_id not in active_crews:
        await ctx.send("Start your journey with `op!start` first!")
        return
    
    bounty = active_crews[user_id]['bounty']
    rank = "Rookie" if bounty < 100000 else "Super Rookie" if bounty < 500000 else "Warlord Tier"
    
    embed = discord.Embed(
        title="💰 BOUNTY POSTER 💰",
        description=f"**{ctx.author.display_name}**\n{bounty:,} Berries",
        color=0xFF0000
    )
    embed.add_field(name="Rank", value=rank, inline=True)
    embed.set_footer(text="The World Government is watching...")
    
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_command(ctx):
    """Show all commands"""
    embed = discord.Embed(
        title="🏴‍☠️ ONE PIECE BOT - COMMANDS 🏴‍☠️",
        description="Your journey to find the One Piece begins here!",
        color=0xFFD700
    )
    embed.add_field(name="op!start", value="Begin your adventure", inline=False)
    embed.add_field(name="op!crew", value="View your crew", inline=False)
    embed.add_field(name="op!continue", value="Continue the story", inline=False)
    embed.add_field(name="op!bounty", value="Check your bounty", inline=False)
    embed.add_field(name="op!help", value="Show this menu", inline=False)
    embed.set_footer(text="⚡ More commands coming soon!")
    
    await ctx.send(embed=embed)

# ========== EPISODE FUNCTIONS ==========

async def episode_one(ctx, user_id):
    """Episode 1: Setting Sail"""
    crew = active_crews[user_id]
    
    embed = discord.Embed(
        title="📺 EPISODE 1 - Setting Sail",
        description="*The journey for the greatest treasure begins...*",
        color=0xFF4500
    )
    embed.add_field(
        name="🌅 Dawn Island Docks",
        value="You stand at the harbor, your small boat ready. The Boat Builder approaches you.",
        inline=False
    )
    embed.add_field(
        name="🛠️ Boat Builder",
        value="*'Captain! The ship is ready. But where are we heading?'*",
        inline=False
    )
    embed.add_field(
        name="⭐ Your Response",
        value="1️⃣ 'We're hunting the One Piece!'\n2️⃣ 'To the Grand Line!'\n3️⃣ 'First, we need a navigator...'",
        inline=False
    )
    embed.set_footer(text="Type op!choose 1, 2, or 3 to continue")
    
    await ctx.send(embed=embed)
    episode_progress[user_id] = {'step': 'ep1_choice1'}

# ========== RUN THE BOT ==========

if __name__ == "__main__":
    if not TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN not found! Set it in .env file")
        logger.info("Create .env file with: DISCORD_BOT_TOKEN=your_token_here")
    else:
        logger.info("🚀 Raising the anchor...")
        bot.run(TOKEN)
