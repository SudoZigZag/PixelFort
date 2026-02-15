#!/bin/bash
# Production Deployment Script for PixelFort

set -e  # Exit on error

echo "🚀 PixelFort Production Deployment"
echo "=================================="
echo ""

# Check for Docker
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Error: Docker is not installed!"
    echo "📦 Install Docker:"
    echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "   sudo sh get-docker.sh"
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Detect Docker Compose command (new vs old)
COMPOSE=""
if docker compose version >/dev/null 2>&1; then
    COMPOSE="docker compose"
    echo "✅ Found: docker compose (modern)"
    echo "   Version: $(docker compose version --short 2>/dev/null || echo 'v2+')"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
    echo "✅ Found: docker-compose (legacy)"
    echo "   Version: $(docker-compose version --short 2>/dev/null || echo 'v1+')"
else
    echo "❌ Error: Docker Compose not found!"
    echo "📦 Install: sudo apt-get install docker-compose-plugin"
    exit 1
fi

echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Create it from template:"
    echo "   cp .env.production.example .env"
    echo "   nano .env"
    exit 1
fi

# Check if ENVIRONMENT is set to production
if ! grep -q "ENVIRONMENT=production" .env; then
    echo "⚠️  Warning: ENVIRONMENT is not set to 'production' in .env"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Building production image..."
$COMPOSE -f docker-compose.prod.yml build

echo ""
echo "🗄️  Initializing database..."
mkdir -p storage/db storage/photos
$COMPOSE -f docker-compose.prod.yml run --rm api python -m api.init_db

echo ""
echo "🔄 Starting production container..."
$COMPOSE -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for service to start..."
sleep 5

# Check if service is up
if $COMPOSE -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "✅ Deployment successful!"
    
    # Try health check
    if command -v curl >/dev/null 2>&1; then
        API_PORT=$(grep API_PORT .env | cut -d '=' -f2 | tr -d ' ' 2>/dev/null || echo "8000")
        sleep 2
        if curl -s http://localhost:${API_PORT}/health >/dev/null 2>&1; then
            echo "💚 Health check: PASSED"
        else
            echo "⚠️  Health check: pending..."
        fi
    fi
else
    echo "⚠️  Service may not have started"
    echo "📊 Check: $COMPOSE -f docker-compose.prod.yml ps"
    echo "📋 Logs: $COMPOSE -f docker-compose.prod.yml logs"
fi

echo ""
echo "📋 Service Information:"
echo "   Container: pixelfort-api-prod"
API_PORT=$(grep API_PORT .env | cut -d '=' -f2 | tr -d ' ' 2>/dev/null || echo "8000")
echo "   Port: ${API_PORT}"
echo "   API: http://localhost:${API_PORT}"
echo "   Docs: http://localhost:${API_PORT}/docs"
echo ""
echo "📊 Useful commands:"
echo "   Logs:    $COMPOSE -f docker-compose.prod.yml logs -f"
echo "   Stop:    $COMPOSE -f docker-compose.prod.yml down"
echo "   Restart: $COMPOSE -f docker-compose.prod.yml restart"
echo "   Status:  $COMPOSE -f docker-compose.prod.yml ps"
echo ""