# Development Setup Guide

Since Docker isn't available on this system, here are the steps to deploy the Searxng convivial instance:

## Option 1: Deploy to a VPS (Recommended)

### Prerequisites
- A VPS with 4-8GB RAM (DigitalOcean, Linode, Hetzner, etc.)
- Ubuntu 22.04 or Debian 11
- Domain name pointing to your VPS

### Quick Deploy Script
```bash
# On your VPS, run:
git clone https://github.com/Camier/searxng-convivial-instance.git
cd searxng-convivial-instance

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure and start
cp .env.example .env
nano .env  # Edit your domain and generate keys
./start.sh
```

## Option 2: Local Development Without Docker

### 1. Install PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb searxng_convivial
sudo -u postgres createuser searxng
sudo -u postgres psql -c "ALTER USER searxng WITH PASSWORD 'your_password';"
```

### 2. Install Redis (2 instances)
```bash
sudo apt install redis-server
# Configure second instance for pub/sub
sudo cp /etc/redis/redis.conf /etc/redis/redis-pubsub.conf
sudo sed -i 's/port 6379/port 6380/g' /etc/redis/redis-pubsub.conf
sudo systemctl start redis
```

### 3. Install Searxng
```bash
cd /opt
sudo git clone https://github.com/searxng/searxng.git
cd searxng
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Install Node.js for WebSocket server
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
cd websocket-server
npm install
```

## Option 3: Use GitHub Codespaces

1. Fork the repository
2. Click "Code" → "Codespaces" → "Create codespace"
3. Docker is pre-installed in Codespaces
4. Run `./start.sh` in the terminal

## Recommended: Deploy to Railway.app

For the easiest deployment:

1. Sign up at https://railway.app
2. Create new project from GitHub
3. Add PostgreSQL and Redis services
4. Deploy with one click

## Testing Without Full Deployment

To test the plugins and features locally:

```bash
# Run Searxng standalone
cd /path/to/searxng
python searx/webapp.py

# Test plugins
cp plugins/*.py searx/plugins/
# Edit settings.yml to enable plugins

# Run WebSocket server
cd websocket-server
npm install
node server.js
```

## Next Steps

1. Choose your deployment method
2. Follow the appropriate guide above
3. Configure your domain and SSL
4. Add friends to the database
5. Start searching together!

## Need Help?

- Check the [Task Management System](TASK_MANAGEMENT_SYSTEM.md) for detailed implementation steps
- Review [Features and Goals](FEATURES_AND_GOALS.md) for configuration options
- Open an issue on GitHub for support