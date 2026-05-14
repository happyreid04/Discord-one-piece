import discord
from discord.ext import commands, tasks
import logging
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import aiohttp

# Load environment variables
load_dotenv()

# ========== LOGGING SETUP ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== BOT SETUP ==========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='op!', intents=intents)

# ========== GAME STATE ==========
active_crews = {}
player_data_file = 'data/players.json'

def load_players():
    """Load player data from JSON"""
    if os.path.exists(player_data_file):
        with open(player_data_file, 'r') as f:
            return json.load(f)
    return {}

def save_players():
    """Save player data to JSON"""
    with open(player_data_file, 'w') as f:
        json.dump(active_crews, f, indent=2)

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
    save_players()
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
        title=f"🏴‍☠️ {crew_data['captain']}'s Crew",
        description=f"Location: {crew_data['location']} | Episode: {crew_data['episode']}",
        color=0xFF4500
    )
    embed.add_field(name="Captain", value=f"⭐ {crew_data['captain']} (You)", inline=False)
    embed.add_field(name="Boat Builder", value=str(crew_data['crew']['boat_builder']), inline=True)
    embed.add_field(name="Ninja", value=str(crew_data['crew']['ninja']), inline=True)
    embed.add_field(name="Bounty", value=f"{crew_data['bounty']:,} Berries", inline=True)
    
    await ctx.send(embed=embed)

# ========== LOAD COGS ==========

async def load_cogs():
    """Load all cogs from bot/cogs folder"""
    cogs_path = 'bot/cogs'
    if os.path.exists(cogs_path):
        for filename in os.listdir(cogs_path):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await bot.load_extension(f'bot.cogs.{filename[:-3]}')
                    logger.info(f"✅ Loaded cog: {filename}")
                except Exception as e:
                    logger.error(f"❌ Failed to load cog {filename}: {e}")

async def load_events():
    """Load all event handlers from bot/events folder"""
    events_path = 'bot/events'
    if os.path.exists(events_path):
        for filename in os.listdir(events_path):
            if filename.endswith('.py') and filename != '__init__.py':
                try:
                    await bot.load_extension(f'bot.events.{filename[:-3]}')
                    logger.info(f"✅ Loaded event: {filename}")
                except Exception as e:
                    logger.error(f"❌ Failed to load event {filename}: {e}")

# ========== MAIN BOT RUN ==========

async def main():
    """Start the bot"""
    async with bot:
        await load_cogs()
        await load_events()
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("❌ DISCORD_TOKEN not found in .env file")
            exit(1)
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())