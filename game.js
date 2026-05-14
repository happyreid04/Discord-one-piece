// ONE PIECE - Browser Game Engine
// Cinematic episode-based adventure

// ========== GAME STATE ==========
let gameState = {
    player: {
        name: 'Straw Hat',
        bounty: 0,
        crew: {
            boatBuilder: true,
            ninja: false,
            mapDrawer: false
        },
        rubberPowers: true,
        episode: 1,
        scene: 'start'
    },
    currentEpisode: 1,
    currentScene: null,
    processingChoice: false
};

// ========== EPISODE DATA ==========
const EPISODES = {
    1: {
        title: 'SETTING SAIL',
        location: 'Dawn Island Docks',
        scenes: {
            start: {
                id: 'start',
                narrative: `🌅 **The sun rises over Dawn Island.**

A young pirate wearing a straw hat stands at the dock, the wind catching their coat. Behind them, a sturdy ship bobs gently on the waves.

**🛠️ Boat Builder:** *"Captain! The ship is ready. But... where exactly are we heading?"*

The horizon stretches endlessly. Somewhere out there, the greatest treasure ever known waits.`,
                choices: [
                    { text: '🏴‍☠️ "We hunt the One Piece!"', nextScene: 'fishWarning', statChange: { bounty: 10000 } },
                    { text: '🌊 "To the Grand Line!"', nextScene: 'fishWarning', statChange: { bounty: 5000 } },
                    { text: '🗺️ "First, we need a navigator."', nextScene: 'needNavigator', statChange: {} }
                ]
            },
            fishWarning: {
                id: 'fishWarning',
                narrative: `**🐟 A Fish Soldier emerges from the water!**

*"Turn back, human! The Fish Kingdom claims these waters! The One Piece belongs to our king!"*

**⚔️ COMBAT INITIATED!**

The creature lunges, razor-sharp scales glinting in the sunlight.`,
                choices: [
                    { text: '💪 "Gomu Gomu no Punch!" (Rubber powers)', nextScene: 'victory', statChange: { bounty: 25000 } },
                    { text: '🥷 "Boat Builder, handle this!"', nextScene: 'victory', statChange: { bounty: 15000 } },
                    { text: '🏃 "Retreat to the ship!"', nextScene: 'retreat', statChange: {} }
                ]
            },
            victory: {
                id: 'victory',
                narrative: `**VICTORY!**

Your fist stretches impossibly far, slamming into the Fish Soldier. It spirals into the depths with a terrified shriek.

**⭐ You:** *"That's just a taste. The Fish Kingdom knows we're coming now..."*

The crew cheers. The first battle is won. But the real journey has just begun.`,
                choices: [
                    { text: '➡️ CONTINUE TO EPISODE 2', nextScene: 'episodeEnd', statChange: {} }
                ]
            },
            retreat: {
                id: 'retreat',
                narrative: `**You escape to open sea.**

The Fish Soldier laughs as you sail away.

**🐟 Fish Soldier:** *"Run, little pirate! The Fish King will hear of this!"*

The crew looks worried. The bounty on your head might grow... but the adventure continues.`,
                choices: [
                    { text: '➡️ REGROUP AND CONTINUE', nextScene: 'episodeEnd', statChange: { bounty: -5000 } }
                ]
            },
            needNavigator: {
                id: 'needNavigator',
                narrative: `**🛠️ Boat Builder:** *"Smart thinking, Captain. There's a town on the next island. I hear a legendary map drawer lives there..."*

The sails catch the wind. A new destination appears on the horizon.`,
                choices: [
                    { text: '⛵ "Set course for that town!"', nextScene: 'episodeEnd', statChange: {} }
                ]
            },
            episodeEnd: {
                id: 'episodeEnd',
                narrative: `**📺 END OF EPISODE 1**

*To be continued...*

The crew sails toward the unknown, the Fish Kingdom in pursuit, and somewhere out there... the Map Drawer waits.

**Next Episode:** The Open Sea – New allies, new enemies, and the first clue to the One Piece.`,
                choices: [
                    { text: '🌊 PREPARE FOR EPISODE 2', nextScene: 'nextEpisode', statChange: {} }
                ]
            }
        }
    },
    2: {
        title: 'THE OPEN SEA',
        location: 'Endless Blue',
        scenes: {
            start: {
                id: 'start',
                narrative: `**Days pass on the endless blue.**

The sun beats down. The wind fills your sails. The Fish Kingdom hasn't been seen since the first encounter.

**⭐ You:** *"Land? Anyone?"*

**🛠️ Boat Builder:** *"Nothing yet, Captain. But the sea feels... strange."*

The water churns. Something large swims beneath.`,
                choices: [
                    { text: '🔍 "Everyone on alert!"', nextScene: 'seaKing', statChange: {} },
                    { text: '🎣 "Let\'s fish. I\'m hungry."', nextScene: 'fishCatches', statChange: {} }
                ]
            },
            seaKing: {
                id: 'seaKing',
                narrative: `**🐉 A SEA KING erupts from the water!**

*"ROOOOAR!"* It's massive – bigger than your entire ship!

**🥷 (If recruited):** *"Captain! What do we do?!"*

The creature's eyes lock onto you. This is no ordinary fish.`,
                choices: [
                    { text: '💪 Stretch and punch it!', nextScene: 'seaKingEscape', statChange: { bounty: 50000 } },
                    { text: '🏃 Outrun it!', nextScene: 'seaKingEscape', statChange: {} },
                    { text: '🤝 Try to communicate', nextScene: 'seaKingFriendly', statChange: {} }
                ]
            },
            seaKingEscape: {
                id: 'seaKingEscape',
                narrative: `**After a desperate struggle, you escape!**

The Sea King dives back into the depths, wounded but alive.

**⭐ You:** *"That was too close... We need to get stronger."*

A small island appears on the horizon. Smoke rises from a town.`,
                choices: [
                    { text: '🏝️ Head to the island', nextScene: 'episodeEnd', statChange: {} }
                ]
            },
            seaKingFriendly: {
                id: 'seaKingFriendly',
                narrative: `**🐉 Sea King:** *"...You're not afraid of me?"*

It speaks! This Sea King is intelligent. 

**🐉 Sea King:** *"The Map Drawer you seek... she lives on the hidden island of Cartographia. I will take you there."*`,
                choices: [
                    { text: '🗺️ "Take us there, friend!"', nextScene: 'episodeEnd', statChange: { bounty: 30000 } }
                ]
            },
            fishCatches: {
                id: 'fishCatches',
                narrative: `**⭐ You:** *"Not bad, Boat Builder!"* 

**🐟 Fish Soldier (in the catch):** *"...You caught me. Please don't eat me. I can tell you about the Fish Kingdom..."* 

The Fish Soldier trembles, clearly terrified.`,
                choices: [
                    { text: '🗣️ "Talk. Now."', nextScene: 'fishIntel', statChange: {} },
                    { text: '🍳 "Dinner is dinner."', nextScene: 'episodeEnd', statChange: { bounty: -5000 } }
                ]
            },
            fishIntel: {
                id: 'fishIntel',
                narrative: `**🐟 Fish Soldier:** *"The Fish King wants the One Piece. He has half a map. Your crew has the other half – with the Map Drawer... but you haven't found her yet. Find her before he does!"*

The Fish Soldier dives overboard and disappears.

The crew exchanges worried glances.`,
                choices: [
                    { text: '🏃 "We sail faster!"', nextScene: 'episodeEnd', statChange: {} }
                ]
            },
            episodeEnd: {
                id: 'episodeEnd',
                narrative: `**📺 END OF EPISODE 2**

*To be continued...*

The Map Drawer is out there. The Fish Kingdom is closer than ever.

**Next Episode:** The Map Drawer – A mysterious cartographer joins the crew as the race for the One Piece intensifies.`,
                choices: [
                    { text: '🗺️ CONTINUE TO EPISODE 3 (Coming Soon)', nextScene: 'comingSoon', statChange: {} }
                ]
            },
            comingSoon: {
                id: 'comingSoon',
                narrative: `**🌊 TO BE CONTINUED...**

Episode 3: The Map Drawer is in development!

The crew continues sailing toward their destiny. The Fish Kingdom grows bolder. And somewhere out there... the One Piece waits.

*Thank you for playing!*`,
                choices: [],
                isEnd: true
            }
        }
    }
};

// ========== CANVAS ANIMATION (Cinematic Waves) ==========
const canvas = document.getElementById('gameCanvas');
let ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Animated wave effect
let waveOffset = 0;
function drawBackground() {
    if (!ctx) return;
    
    // Gradient sky
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#0a0a2a');
    gradient.addColorStop(0.5, '#1a3a5a');
    gradient.addColorStop(1, '#0a2a3a');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw sun/moon
    ctx.beginPath();
    ctx.arc(canvas.width - 80, 80, 40, 0, Math.PI * 2);
    ctx.fillStyle = '#FFD700';
    ctx.fill();
    ctx.shadowBlur = 20;
    ctx.shadowColor = '#FFD700';
    ctx.fill();
    ctx.shadowBlur = 0;
    
    // Animated waves
    ctx.beginPath();
    for (let x = 0; x <= canvas.width; x += 20) {
        const y = canvas.height - 60 + Math.sin(x * 0.01 + waveOffset) * 15;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.lineTo(canvas.width, canvas.height);
    ctx.lineTo(0, canvas.height);
    ctx.closePath();
    ctx.fillStyle = 'rgba(0, 100, 150, 0.5)';
    ctx.fill();
    
    waveOffset += 0.02;
    requestAnimationFrame(drawBackground);
}

drawBackground();

// ========== UI RENDERING ==========
async function loadScene(episodeNum, sceneId) {
    if (gameState.processingChoice) return;
    
    const episode = EPISODES[episodeNum];
    if (!episode) {
        console.error('Episode not found');
        return;
    }
    
    const scene = episode.scenes[sceneId];
    if (!scene) {
        console.error('Scene not found');
        return;
    }
    
    gameState.currentEpisode = episodeNum;
    gameState.currentScene = scene;
    
    // Hide loading screen, show UI
    document.getElementById('loadingScreen').style.opacity = '0';
    setTimeout(() => {
        document.getElementById('loadingScreen').style.display = 'none';
        document.getElementById('uiOverlay').style.display = 'block';
    }, 1000);
    
    // Update UI
    document.getElementById('episodeTitle').innerHTML = `EPISODE ${episodeNum}: ${episode.title}`;
    document.getElementById('sceneLocation').innerHTML = `📍 ${episode.location}`;
    document.getElementById('narrativeText').innerHTML = scene.narrative;
    document.getElementById('bountyStatus').innerHTML = `${gameState.player.bounty.toLocaleString()} Berries`;
    document.getElementById('episodeStatus').innerHTML = `Ep ${episodeNum}`;
    
    // Count crew
    let crewCount = 1; // Star
    if (gameState.player.crew.boatBuilder) crewCount++;
    if (gameState.player.crew.ninja) crewCount++;
    if (gameState.player.crew.mapDrawer) crewCount++;
    document.getElementById('crewStatus').innerHTML = `Crew: ${crewCount}`;
    
    // Render choices
    const choicesContainer = document.getElementById('choicesContainer');
    choicesContainer.innerHTML = '';
    
    if (scene.choices && scene.choices.length > 0) {
        scene.choices.forEach((choice, index) => {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.textContent = choice.text;
            btn.onclick = () => makeChoice(choice);
            choicesContainer.appendChild(btn);
        });
    } else {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.textContent = '🏴‍☠️ THE ADVENTURE CONTINUES...';
        btn.onclick = () => {
            if (typeof window.DiscordSDK !== 'undefined') {
                // Notify Discord that episode ended
                console.log('Episode complete - ready for next');
            }
        };
        choicesContainer.appendChild(btn);
    }
}

async function makeChoice(choice) {
    if (gameState.processingChoice) return;
    gameState.processingChoice = true;
    
    // Apply stat changes
    if (choice.statChange) {
        if (choice.statChange.bounty) {
            gameState.player.bounty += choice.statChange.bounty;
        }
    }
    
    // Play sound effect (if any)
    // (Add sound later)
    
    // Determine next scene
    let nextSceneId = choice.nextScene;
    
    // Special handling for next episode
    if (nextSceneId === 'nextEpisode') {
        const nextEp = gameState.currentEpisode + 1;
        if (EPISODES[nextEp]) {
            gameState.player.episode = nextEp;
            await loadScene(nextEp, 'start');
            gameState.processingChoice = false;
            return;
        }
    }
    
    // Load next scene in same episode
    const episode = EPISODES[gameState.currentEpisode];
    const nextScene = episode.scenes[nextSceneId];
    
    if (nextScene) {
        gameState.currentScene = nextScene;
        document.getElementById('narrativeText').innerHTML = nextScene.narrative;
        document.getElementById('bountyStatus').innerHTML = `${gameState.player.bounty.toLocaleString()} Berries`;
        
        // Update choices
        const choicesContainer = document.getElementById('choicesContainer');
        choicesContainer.innerHTML = '';
        
        if (nextScene.choices && nextScene.choices.length > 0) {
            nextScene.choices.forEach((nextChoice) => {
                const btn = document.createElement('button');
                btn.className = 'choice-btn';
                btn.textContent = nextChoice.text;
                btn.onclick = () => makeChoice(nextChoice);
                choicesContainer.appendChild(btn);
            });
        } else {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.textContent = '🏴‍☠️ TO BE CONTINUED...';
            choicesContainer.appendChild(btn);
        }
    }
    
    gameState.processingChoice = false;
}

// ========== DISCORD ACTIVITY INTEGRATION ==========
async function initDiscord() {
    // Check if running in Discord
    const isInDiscord = window.location.hostname.includes('discord.com') ||
                        window.location.hostname.includes('discordapp.com') ||
                        window.location.hostname.includes('discordsays.com');
    
    if (isInDiscord && typeof DiscordSDK !== 'undefined') {
        try {
            const discordSdk = new DiscordSDK('YOUR_CLIENT_ID');
            await discordSdk.ready();
            console.log('🎮 Running inside Discord Activity');
            
            // Get user info
            const { code } = await discordSdk.commands.authorize({
                client_id: 'YOUR_CLIENT_ID',
                scope: ['identify']
            });
            
            // Set player name from Discord
            const user = await discordSdk.commands.getUser();
            if (user && user.username) {
                gameState.player.name = user.username;
                document.getElementById('episodeTitle').innerHTML = `⭐ ${user.username}'S JOURNEY`;
            }
        } catch (e) {
            console.log('Discord SDK error:', e);
        }
    }
}

// ========== START GAME ==========
window.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        loadScene(1, 'start');
    }, 2000);
    
    initDiscord();
});