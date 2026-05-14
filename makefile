.PHONY: help install run-bot run-web docker-up docker-down deploy-tunnel

help:
	@echo "🏴‍☠️ One Piece Game Commands"
	@echo "  make install     - Install Python dependencies"
	@echo "  make run-bot     - Run Discord bot locally"
	@echo "  make run-web     - Serve web files locally"
	@echo "  make docker-up   - Start all services with Docker"
	@echo "  make docker-down - Stop all services"
	@echo "  make deploy-tunnel - Start Cloudflare tunnel"

install:
	pip install -r requirements.txt

run-bot:
	python -m bot.main

run-web:
	cd web && python -m http.server 8000

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

deploy-tunnel:
	chmod +x deploy/cloudflare-tunnel.sh
	./deploy/cloudflare-tunnel.sh