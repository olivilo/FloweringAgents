#!/bin/bash
# FloweringAgents — first-time deployment script
# Run as root on a fresh Ubuntu 24.04 VPS
# Usage: bash deploy.sh

set -e

echo "🌸 FloweringAgents deployment starting..."
echo "   Target: floweringagents.ai.in.rs"
echo ""

# 1. Install Docker + Certbot
apt-get update -q
apt-get install -y docker.io docker-compose-plugin curl certbot

# 2. Create .env with random secrets if it doesn't exist
if [ ! -f .env ]; then
    printf "POSTGRES_PASSWORD=%s\nSECRET_KEY=%s\n" \
        "$(openssl rand -hex 32)" \
        "$(openssl rand -hex 32)" > .env
    echo "✅ .env created — keep this file safe, never commit it to git"
fi

# 3. Get SSL certificate (port 80 must be free)
certbot certonly --standalone \
    -d floweringagents.ai.in.rs \
    --non-interactive --agree-tos \
    -m olivilo@diceteach.in.rs

echo "✅ SSL certificate obtained"

# 4. Start all services
docker compose up -d

echo ""
echo "🌸 FloweringAgents is live at https://floweringagents.ai.in.rs"
echo ""
echo "Useful commands:"
echo "  docker compose logs -f backend   — watch API logs"
echo "  docker compose ps                — check service status"
echo "  docker compose down              — stop everything"
