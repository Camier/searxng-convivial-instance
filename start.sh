#!/bin/bash
# Searxng Convivial Instance Startup Script

set -e

echo "🌟 Starting Searxng Convivial Instance..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required variables
if [ -z "$SEARXNG_SECRET_KEY" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ Error: Required environment variables not set!"
    echo "Please configure SEARXNG_SECRET_KEY and POSTGRES_PASSWORD in .env"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p searxng nginx/conf.d certbot/www certbot/conf

# Generate Nginx config if it doesn't exist
if [ ! -f nginx/conf.d/searxng.conf ]; then
    echo "📝 Generating Nginx configuration..."
    cat > nginx/conf.d/searxng.conf << EOF
server {
    listen 80;
    server_name ${SEARXNG_HOSTNAME};
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name ${SEARXNG_HOSTNAME};
    
    ssl_certificate /etc/letsencrypt/live/${SEARXNG_HOSTNAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${SEARXNG_HOSTNAME}/privkey.pem;
    
    location / {
        proxy_pass http://searxng:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /socket.io/ {
        proxy_pass http://websocket-server:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF
fi

# Build WebSocket server
echo "🔨 Building WebSocket server..."
docker-compose build websocket-server

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
docker-compose ps

# Initialize SSL if needed
if [ ! -d "certbot/conf/live/${SEARXNG_HOSTNAME}" ]; then
    echo "🔐 Initializing SSL certificate..."
    echo "Please make sure your domain is pointing to this server!"
    read -p "Press enter to continue with SSL setup..."
    
    docker-compose run --rm certbot certonly --webroot \
        --webroot-path=/var/www/certbot \
        --email ${SSL_EMAIL:-admin@${SEARXNG_HOSTNAME}} \
        --agree-tos \
        --no-eff-email \
        -d ${SEARXNG_HOSTNAME}
    
    # Restart Nginx with SSL
    docker-compose restart nginx
fi

echo "✅ Searxng Convivial Instance is running!"
echo "🌐 Access at: https://${SEARXNG_HOSTNAME}"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop: docker-compose down"
echo ""
echo "🎉 Happy searching with friends!"