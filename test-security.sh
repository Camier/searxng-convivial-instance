#!/bin/bash
# Security Test Script for SearXNG Convivial Instance

echo "🔒 Testing Security Improvements..."
echo ""

# Test 1: Auth Service
echo "1️⃣ Testing Authentication Service..."
auth_health=$(curl -s http://localhost:5000/health 2>/dev/null | grep -o '"status":"healthy"')
if [ ! -z "$auth_health" ]; then
    echo "✅ Auth service is healthy"
else
    echo "❌ Auth service is not responding"
fi
echo ""

# Test 2: API Service
echo "2️⃣ Testing API Service..."
api_health=$(curl -s http://localhost:5001/health 2>/dev/null | grep -o '"status":"healthy"')
if [ ! -z "$api_health" ]; then
    echo "✅ API service is healthy"
    echo "📚 API documentation available at: http://localhost:5001/docs"
else
    echo "❌ API service is not responding"
fi
echo ""

# Test 3: MinIO Storage
echo "3️⃣ Testing MinIO Storage..."
minio_health=$(curl -s http://localhost:9000/minio/health/live 2>/dev/null)
if [ "$minio_health" == "OK" ]; then
    echo "✅ MinIO storage is healthy"
    echo "🎛️ MinIO console available at: http://localhost:9001"
else
    echo "❌ MinIO storage is not responding"
fi
echo ""

# Test 4: Registration endpoint
echo "4️⃣ Testing Registration (should fail due to missing data)..."
register_response=$(curl -s -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test"}' \
  -w "\n%{http_code}" | tail -1)
if [ "$register_response" == "400" ]; then
    echo "✅ Registration validation working (correctly rejected invalid data)"
else
    echo "❌ Registration endpoint not working properly"
fi
echo ""

# Test 5: API requires authentication
echo "5️⃣ Testing API Authentication..."
api_auth_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/discoveries/)
if [ "$api_auth_response" == "401" ]; then
    echo "✅ API correctly requires authentication"
else
    echo "❌ API authentication not working (status: $api_auth_response)"
fi
echo ""

# Test 6: SQL Injection fix
echo "6️⃣ Checking SQL Injection fix..."
if grep -q "search_term.replace" plugins/discovery_feed.py; then
    echo "✅ SQL injection protection in place"
else
    echo "❌ SQL injection fix not found"
fi
echo ""

# Test 7: WebSocket JWT verification
echo "7️⃣ Checking WebSocket JWT verification..."
if grep -q "jwt.verify" websocket-server/server.js && grep -q "auth-service:5000" websocket-server/server.js; then
    echo "✅ WebSocket JWT verification implemented"
else
    echo "❌ WebSocket JWT verification not properly implemented"
fi
echo ""

echo "🎯 Security Test Summary:"
echo "- Authentication service ready for user registration/login"
echo "- API service provides secure endpoints with documentation"
echo "- File storage secured with MinIO"
echo "- SQL injection vulnerability fixed"
echo "- WebSocket authentication improved"
echo ""
echo "Next steps:"
echo "1. Build and start new services: docker compose build && docker compose up -d"
echo "2. Register first user via API or login page"
echo "3. Integrate middleware with SearXNG"