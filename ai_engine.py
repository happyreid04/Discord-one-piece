import aiohttp
import asyncio
import json
import os
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ========== CONFIGURATION ==========
AI_ENABLED = os.getenv('AI_ENABLED', 'false').lower() == 'true'
AI_API_KEY = os.getenv('AI_API_KEY', '')
AI_API_URL = os.getenv('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')  # or 'gpt-4', or free alternative

# Telegram config
TELEGRAM_ENABLED = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Free AI alternative endpoints (no API key required for some)
FREE_AI_ENDPOINTS = {
    'huggingface': 'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
    'ollama': 'http://localhost:11434/api/generate',  # Local LLM
}

# ========== AI DECISION ENGINE ==========

class AIEngine:
    """Handles AI-powered story generation and dynamic choices"""
    
    def __init__(self):
        self.session = None
        self.use_free_api = not AI_API_KEY and AI_ENABLED
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate_story_beat(self, player_data: Dict, choice: str, context: str) -> Dict:
        """
        Generate dynamic story continuation using AI
        
        Returns:
            {
                'narrative': str,
                'choices': list,
                'stat_changes': dict,
                'combat': bool
            }
        """
        if not AI_ENABLED:
            return self._fallback_response(context)
        
        prompt = self._build_prompt(player_data, choice, context)
        
        try:
            if AI_API_KEY:
                response = await self._call_openai(prompt)
            elif self.use_free_api:
                response = await self._call_free_api(prompt)
            else:
                return self._fallback_response(context)
            
            return self._parse_ai_response(response)
        
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return self._fallback_response(context)
    
    def _build_prompt(self, player_data: Dict, choice: str, context: str) -> str:
        """Build prompt for AI"""
        return f"""
You are the Game Master for a One Piece inspired adventure game.

PLAYER STATUS:
- Name: {player_data.get('name', 'Captain')}
- Bounty: {player_data.get('bounty', 0)} Berries
- Crew: Boat Builder (yes), Ninja ({player_data.get('crew', {}).get('ninja', False)}), Map Drawer ({player_data.get('crew', {}).get('map_drawer', False)})
- Rubber Powers: {player_data.get('rubber_powers', True)}
- Current Episode: {player_data.get('episode', 1)}

CURRENT SCENE CONTEXT:
{context}

PLAYER'S CHOICE:
{choice}

Generate a short, exciting story continuation (2-3 sentences) that:
1. Respects One Piece tone (adventure, humor, epic)
2. Acknowledges the player's rubber powers
3. Creates tension with the Fish Kingdom enemies
4. Ends with 3 clear choices for the player

Return ONLY valid JSON:
{{
    "narrative": "The story text here...",
    "choices": ["Choice 1 text", "Choice 2 text", "Choice 3 text"],
    "bounty_change": 0,
    "combat": false
}}
"""
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        session = await self.get_session()
        headers = {
            'Authorization': f'Bearer {AI_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': AI_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.8,
            'max_tokens': 300
        }
        
        async with session.post(AI_API_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI error: {resp.status}")
                return ""
    
    async def _call_free_api(self, prompt: str) -> str:
        """Call free alternative API (HuggingFace or local Ollama)"""
        session = await self.get_session()
        
        # Try Ollama first (local, free)
        try:
            payload = {'model': 'llama2', 'prompt': prompt, 'stream': False}
            async with session.post(FREE_AI_ENDPOINTS['ollama'], json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('response', '')
        except:
            pass
        
        return ""
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI JSON response"""
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {
                    'narrative': data.get('narrative', 'The adventure continues...'),
                    'choices': data.get('choices', ['Continue forward', 'Look around', 'Talk to crew']),
                    'bounty_change': data.get('bounty_change', 0),
                    'combat': data.get('combat', False)
                }
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI response as JSON")
        
        return self._fallback_response("")
    
    def _fallback_response(self, context: str) -> Dict:
        """Fallback when AI is unavailable"""
        return {
            'narrative': "The sea stretches endlessly before you. The wind fills your sails as adventure calls...",
            'choices': ['Continue sailing', 'Search for islands', 'Train your crew'],
            'bounty_change': 0,
            'combat': False
        }
    
    async def generate_combat_outcome(self, player_stats: Dict, enemy: str, player_choice: str) -> Dict:
        """Generate combat results dynamically"""
        if not AI_ENABLED:
            return {
                'victory': True,
                'narrative': f"You defeat the {enemy} with your rubber powers!",
                'bounty_gain': 10000,
                'damage_taken': 0
            }
        
        prompt = f"""
One Piece combat:
Player (Rubber Human, Bounty {player_stats.get('bounty', 0)}) vs {enemy}
Player action: {player_choice}
Generate outcome as JSON: {{"victory": true/false, "narrative": "text", "bounty_gain": number, "damage_taken": number}}
"""
        response = await self._call_openai(prompt) if AI_API_KEY else ""
        
        if response:
            try:
                return json.loads(response)
            except:
                pass
        
        return {'victory': True, 'narrative': f"Gomu Gomu no Punch! The {enemy} is defeated!", 'bounty_gain': 5000, 'damage_taken': 0}


# ========== TELEGRAM BRIDGE ==========

class TelegramBridge:
    """Bridge between Discord and Telegram"""
    
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = TELEGRAM_ENABLED and self.bot_token and self.chat_id
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def send_message(self, message: str, parse_mode: str = 'HTML'):
        """Send message to Telegram channel"""
        if not self.enabled:
            return False
        
        try:
            session = await self.get_session()
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    logger.info(f"📱 Telegram message sent")
                    return True
                else:
                    logger.error(f"Telegram error: {resp.status}")
                    return False
        except Exception as e:
            logger.error(f"Telegram bridge failed: {e}")
            return False
    
    async def send_game_event(self, event_type: str, player_name: str, details: str):
        """Send formatted game event to Telegram"""
        if not self.enabled:
            return
        
        emojis = {
            'bounty': '💰',
            'combat': '⚔️',
            'treasure': '💎',
            'episode': '📺',
            'crew': '⭐'
        }
        emoji = emojis.get(event_type, '🏴‍☠️')
        
        message = f"""
{emoji} <b>ONE PIECE GAME EVENT</b> {emoji}

<b>Event:</b> {event_type.upper()}
<b>Player:</b> {player_name}
<b>Details:</b> {details}

#OnePieceGame
"""
        await self.send_message(message.strip())
    
    async def broadcast_to_all(self, title: str, content: str, discord_channel=None):
        """Broadcast to both Discord and Telegram"""
        # Send to Telegram
        if self.enabled:
            await self.send_message(f"<b>{title}</b>\n\n{content}")
        
        # Return formatted string for Discord
        return f"**{title}**\n{content}"
    
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None


# ========== NOTIFICATION ENGINE ==========

class NotificationEngine:
    """Real-time notifications for Discord and Telegram"""
    
    def __init__(self, bot, telegram_bridge: TelegramBridge):
        self.bot = bot
        self.telegram = telegram_bridge
        self.subscribers = {}  # channel_id -> settings
    
    async def notify_raid(self, location: str, time_minutes: int):
        """Send raid alert"""
        embed = {
            'title': '⚔️ FISH KINGDOM RAID ⚔️',
            'description': f"The Fish Army is attacking **{location}**!",
            'fields': [
                ('Time', f"Starts in {time_minutes} minutes", True),
                ('Reward', 'Devil Fruit Fragment', True),
                ('Threat Level', '⚠️ HIGH ⚠️', False)
            ]
        }
        
        await self._broadcast(embed, f"🚨 RAID ALERT: {location}")
    
    async def notify_treasure(self, location: str, rarity: str):
        """Notify treasure discovery"""
        embed = {
            'title': '💎 TREASURE DISCOVERED 💎',
            'description': f"A **{rarity}** treasure was found at {location}!",
            'fields': [
                ('Location', location, True),
                ('Rarity', rarity.upper(), True)
            ]
        }
        await self._broadcast(embed, f"💎 Treasure spotted at {location}!")
    
    async def notify_episode_release(self, episode_num: int, title: str):
        """New episode notification"""
        embed = {
            'title': f'📺 EPISODE {episode_num} RELEASED 📺',
            'description': f"**{title}** is now available!",
            'footer': 'To be continued...',
            'color': 0xFF4500
        }
        await self._broadcast(embed, f"📺 Episode {episode_num}: {title} is live!")
    
    async def notify_player_achievement(self, player_name: str, achievement: str, bounty_change: int):
        """Individual player achievement notification"""
        message = f"🏆 **{player_name}** achieved: {achievement}!\n💰 Bounty +{bounty_change:,} Berries"
        
        # Send to player's Discord DM
        # (Requires member lookup - implement as needed)
        
        # Also broadcast to Telegram if enabled
        await self.telegram.send_game_event('bounty', player_name, f"{achievement} (+{bounty_change} bounty)")
    
    async def _broadcast(self, embed_data: Dict, plain_text: str):
        """Broadcast to all subscribed channels"""
        # This will be expanded when we have channel subscriptions
        logger.info(f"Broadcasting: {plain_text}")
        
        # Send to Telegram
        await self.telegram.send_message(plain_text)


# ========== SINGLETON INSTANCES ==========

_ai_engine = None
_telegram_bridge = None
_notification_engine = None

def get_ai_engine() -> AIEngine:
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine

def get_telegram_bridge() -> TelegramBridge:
    global _telegram_bridge
    if _telegram_bridge is None:
        _telegram_bridge = TelegramBridge()
    return _telegram_bridge

def get_notification_engine(bot=None) -> NotificationEngine:
    global _notification_engine
    if _notification_engine is None and bot:
        _notification_engine = NotificationEngine(bot, get_telegram_bridge())
    return _notification_engine

async def close_all():
    global _ai_engine, _telegram_bridge
    if _ai_engine:
        await _ai_engine.close()
    if _telegram_bridge:
        await _telegram_bridge.close()