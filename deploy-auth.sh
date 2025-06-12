#!/bin/bash
# Deploy authentication and security services

echo "🔐 Deploying SearXNG Convivial Authentication System"
echo "=================================================="
echo ""

# Build services
echo "📦 Building auth services..."
docker compose build auth-service api-service auth-proxy

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful"
echo ""

# Stop existing services
echo "🛑 Stopping existing services..."
docker compose down

# Start all services
echo "🚀 Starting all services..."
docker compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."
echo ""

# Auth service
auth_health=$(curl -s http://localhost:5000/health 2>/dev/null | grep -o '"status":"healthy"')
if [ ! -z "$auth_health" ]; then
    echo "✅ Auth service: Healthy"
else
    echo "❌ Auth service: Not responding"
fi

# API service  
api_health=$(curl -s http://localhost:5001/health 2>/dev/null | grep -o '"status":"healthy"')
if [ ! -z "$api_health" ]; then
    echo "✅ API service: Healthy"
else
    echo "❌ API service: Not responding"
fi

# Auth proxy
proxy_health=$(curl -s http://localhost:8890/health 2>/dev/null | grep -o '"status":"healthy"')
if [ ! -z "$proxy_health" ]; then
    echo "✅ Auth proxy: Healthy"
else
    echo "❌ Auth proxy: Not responding"
fi

# MinIO
minio_health=$(curl -s http://localhost:9000/minio/health/live 2>/dev/null)
if [ "$minio_health" == "OK" ]; then
    echo "✅ MinIO storage: Healthy"
else
    echo "❌ MinIO storage: Not responding"
fi

echo ""
echo "📋 Service URLs:"
echo "- Main application: http://localhost:8890"
echo "- API documentation: http://localhost:5001/docs"
echo "- MinIO console: http://localhost:9001"
echo ""
echo "🎯 Next steps:"
echo "1. Run ./update-plugins.sh to enable custom plugins"
echo "2. Visit http://localhost:8890 to register first user"
echo "3. Start searching with your friends!"
echo ""
echo "🔒 Security Note: Change all passwords in .env for production!"