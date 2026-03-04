#!/bin/bash
# Install Docker and Docker Compose on Raspberry Pi

set -e

echo "🐳 Installing Docker on Raspberry Pi"
echo "====================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "❌ Please run as normal user (not root/sudo)"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    echo "📋 Detected OS: $OS"
else
    echo "❌ Cannot detect OS"
    exit 1
fi

# Check if Docker already installed
if command -v docker &> /dev/null; then
    echo "✅ Docker already installed: $(docker --version)"
    DOCKER_INSTALLED=true
else
    DOCKER_INSTALLED=false
fi

# Install Docker
if [ "$DOCKER_INSTALLED" = false ]; then
    echo ""
    echo "📦 Installing Docker..."
    
    # Download and run Docker install script
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    
    echo "✅ Docker installed"
fi

# Add user to docker group
echo ""
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Check Docker Compose
echo ""
if docker compose version &> /dev/null; then
    echo "✅ Docker Compose plugin already installed: $(docker compose version --short)"
else
    echo "📦 Installing Docker Compose plugin..."
    
    # Install compose plugin
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    
    echo "✅ Docker Compose installed"
fi

# Enable Docker service
echo ""
echo "🚀 Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# Verify installation
echo ""
echo "🔍 Verifying installation..."
docker --version
docker compose version

echo ""
echo "✅ Docker installation complete!"
echo ""
echo "⚠️  IMPORTANT: You must log out and log back in for group changes to take effect"
echo ""
echo "After logging back in, verify with:"
echo "  docker ps"
echo ""