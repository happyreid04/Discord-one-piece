#!/bin/bash
# Cloudflare Tunnel setup for Discord Activity

# Install cloudflared
# macOS: brew install cloudflared
# Linux: wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

echo "🚀 Setting up Cloudflare Tunnel for Discord Activity"

# Login to Cloudflare
cloudflared tunnel login

# Create a tunnel
cloudflared tunnel create one-piece-tunnel

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep one-piece-tunnel | awk '{print $1}')

echo "✅ Tunnel ID: $TUNNEL_ID"

# Run tunnel (point to localhost:80 for web, or :5000 for bot)
echo "▶️ Run this command to start tunnel:"
echo "cloudflared tunnel run one-piece-tunnel --url http://localhost:80"

# For Discord Activity, you need a public HTTPS URL
# cloudflared provides this automatically