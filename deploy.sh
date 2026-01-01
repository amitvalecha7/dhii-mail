#!/bin/bash

# Production deployment script for dhii-mail

set -e

echo "🚀 Starting dhii-mail production deployment..."

# Check if required environment variables are set
required_vars=("GOOGLE_API_KEY" "JWT_SECRET_KEY" "ENCRYPTION_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable is not set"
        exit 1
    fi
done

# Create necessary directories
mkdir -p data logs ssl

# Set proper permissions
chmod 700 data logs ssl

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose pull

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health check
echo "🔍 Performing health check..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    echo "📋 Container logs:"
    docker-compose logs --tail=50
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
echo "🌐 Application is available at: http://localhost"
echo "📊 Monitor logs: docker-compose logs -f"