#!/bin/bash

# GP-JADE Docker Quick Start Script
set -e

echo "🚀 GP-JADE Docker Deployment"
echo "=============================="

# Check prerequisites
echo ""
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi
echo "✅ Docker Compose found: $(docker-compose --version)"

# Check for GPU
echo ""
echo "🎮 Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

    # Check if NVIDIA Docker runtime is available
    if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null 2>&1; then
        echo "✅ NVIDIA Docker runtime available"
        GPU_AVAILABLE=true
    else
        echo "⚠️  NVIDIA Docker runtime not configured"
        echo "   Install with: sudo apt-get install nvidia-container-toolkit"
        GPU_AVAILABLE=false
    fi
else
    echo "⚠️  No GPU detected - will run in CPU mode (slower)"
    GPU_AVAILABLE=false
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p GP-DATA/vector-db
mkdir -p GP-DATA/ai-models
mkdir -p opa-policies
mkdir -p gatekeeper-policies
echo "✅ Directories created"

# Display deployment options
echo ""
echo "🎯 Deployment Options:"
echo "1. Full deployment (GP-JADE + OPA + Gatekeeper)"
echo "2. Standard deployment (GP-JADE + OPA)"
echo "3. Minimal deployment (GP-JADE only)"
echo ""
read -p "Select option [1-3] (default: 2): " DEPLOY_OPTION
DEPLOY_OPTION=${DEPLOY_OPTION:-2}

# Set docker-compose profile
case $DEPLOY_OPTION in
    1)
        echo "🚀 Starting full deployment with Kubernetes support..."
        PROFILE="--profile kubernetes"
        ;;
    2)
        echo "🚀 Starting standard deployment..."
        PROFILE=""
        ;;
    3)
        echo "🚀 Starting minimal deployment..."
        # Remove OPA dependency temporarily
        PROFILE=""
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

# Build and start services
echo ""
echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose $PROFILE up -d

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."

# Check GP-JADE
if docker ps | grep -q gp-jade; then
    echo "✅ GP-JADE container running"

    # Wait for model download/initialization (can take a while on first run)
    echo ""
    echo "⏳ Initializing AI model (this may take 10-30 minutes on first run)..."
    echo "   Monitor progress with: docker-compose logs -f gp-jade"

    # Check if model is already cached
    if docker exec gp-jade ls /root/.cache/huggingface/hub/ 2>/dev/null | grep -q "Qwen"; then
        echo "✅ Model cache found - startup will be quick"
    else
        echo "📥 Model will be downloaded on first use"
    fi
else
    echo "❌ GP-JADE container not running"
fi

# Check OPA
if [ "$DEPLOY_OPTION" != "3" ]; then
    if docker ps | grep -q gp-opa; then
        echo "✅ OPA container running"

        # Test OPA
        if curl -s http://localhost:8181/health > /dev/null 2>&1; then
            echo "✅ OPA is responsive"
        else
            echo "⚠️  OPA not responsive yet"
        fi
    else
        echo "⚠️  OPA container not running"
    fi
fi

# Display access information
echo ""
echo "=============================="
echo "🎉 GP-JADE is starting!"
echo "=============================="
echo ""
echo "📍 Access points:"
echo "   API:  http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
if [ "$DEPLOY_OPTION" != "3" ]; then
    echo "   OPA:  http://localhost:8181"
fi
echo ""
echo "🔧 Useful commands:"
echo "   View logs:       docker-compose logs -f gp-jade"
echo "   Enter container: docker exec -it gp-jade bash"
echo "   Stop services:   docker-compose down"
echo "   Restart:         docker-compose restart"
echo ""
echo "🧪 Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "📖 Full documentation: README-DOCKER.md"
echo ""

# Ask if user wants to view logs
read -p "View logs now? [y/N]: " VIEW_LOGS
if [[ "$VIEW_LOGS" =~ ^[Yy]$ ]]; then
    docker-compose logs -f
fi