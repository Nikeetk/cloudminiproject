#!/bin/bash
set -e

echo "=========================================================="
echo "🚀 Setting up AI Career Recommendation System on AWS EC2"
echo "=========================================================="

# 1. Update system packages
echo "📦 Updating package lists..."
sudo apt-get update -y

# 2. Install Docker & Docker Compose if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker and Docker Compose..."
    sudo apt-get install -y docker.io docker-compose git
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

# 3. Stop any existing running container
echo "🔄 Stopping any older containers..."
sudo docker-compose down || true

# 4. Build and run application in background
echo "🔨 Building Docker image and starting service..."
sudo docker-compose up -d --build

# 5. Check container status
echo "🔍 Checking container status..."
sudo docker ps

echo ""
echo "=========================================================="
echo "✅ Deployment Successful!"
echo "🌐 Your app is now live! Open your browser and visit:"
echo "   http://$(curl -s http://checkip.amazonaws.com)"
echo "=========================================================="
