#!/bin/bash
# Test script for SearXNG Convivial Instance

echo "🧪 Testing SearXNG Convivial Instance..."
echo ""

# Test 1: Infrastructure
echo "1️⃣ Testing Docker containers..."
docker compose ps --format "table {{.Name}}\t{{.Status}}"
echo ""

# Test 2: SearXNG accessibility
echo "2️⃣ Testing SearXNG accessibility..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8890)
if [ "$response" -eq 200 ]; then
    echo "✅ SearXNG is accessible on port 8890"
else
    echo "❌ SearXNG is not accessible (HTTP $response)"
fi
echo ""

# Test 3: Database connectivity
echo "3️⃣ Testing PostgreSQL database..."
docker exec searxng-postgres psql -U searxng -d searxng_convivial -c "SELECT COUNT(*) FROM users;" 2>/dev/null
echo ""

# Test 4: Redis connectivity
echo "4️⃣ Testing Redis instances..."
docker exec searxng-redis-cache redis-cli ping
docker exec searxng-redis-pubsub redis-cli -p 6380 ping
echo ""

# Test 5: WebSocket server
echo "5️⃣ Testing WebSocket server..."
websocket_health=$(curl -s http://localhost:3000/health 2>/dev/null | grep -o '"status":"healthy"')
if [ ! -z "$websocket_health" ]; then
    echo "✅ WebSocket server is healthy"
else
    echo "❌ WebSocket server is not responding"
fi
echo ""

# Test 6: Search functionality
echo "6️⃣ Testing search functionality..."
search_result=$(curl -s "http://localhost:8890/search?q=test" | grep -o '<title>.*</title>')
if [ ! -z "$search_result" ]; then
    echo "✅ Search functionality is working"
else
    echo "❌ Search functionality is not working"
fi
echo ""

echo "✨ Testing complete!"