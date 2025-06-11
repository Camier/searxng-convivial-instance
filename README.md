# 🌟 Searxng Convivial Instance

A privacy-respecting search engine designed as a **digital salon** for 2-3 close friends, emphasizing shared discovery, intellectual companionship, and the joy of learning together.

## 🚀 One-Click Deploy

Deploy your own instance in minutes:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/github.com/Camier/searxng-convivial-instance)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Camier/searxng-convivial-instance)

[![Deploy on Fly.io](https://img.shields.io/badge/Deploy-on%20Fly.io-6F4CFF?style=for-the-badge)](https://fly.io/launch?repo=https://github.com/Camier/searxng-convivial-instance)

## 🎯 Quick Start

### Prerequisites
- Docker & Docker Compose (or use cloud deployment above)
- Domain name with DNS pointing to your server
- 4-8GB RAM VPS
- Basic Linux knowledge

### Installation

1. **Clone and setup**
```bash
git clone https://github.com/Camier/searxng-convivial-instance.git
cd searxng-convivial-instance
cp .env.example .env
```

2. **Configure environment**
Edit `.env` with your values:
```bash
SEARXNG_HOSTNAME=search.yourdomain.com
SEARXNG_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

3. **Start services**
```bash
./start.sh
```

## 🏛️ Core Features

### Academic Research
- **Scientific databases**: PubMed, Semantic Scholar, CORE
- **Botanical focus**: GBIF, Plants of the World, ethnobotany databases
- **French archives**: Gallica, Archives Nationales, all departmental archives
- **Smart features**: DOI resolver, citation graphs, Zotero integration

### Music Discovery
- **No Spotify**: Bandcamp, SoundCloud, Free Music Archive
- **Deep digging**: Genre filters, BPM detection, label search
- **Radio**: Global stations, synchronized listening
- **Knowledge**: Discogs, MusicBrainz, concert history

### Convivial Features
- ☕ **Morning Coffee**: Daily discovery digest
- 👻 **Presence Bubbles**: See who's searching
- 🎁 **Gift Discoveries**: Share surprises
- ✨ **Collision Moments**: Celebrate coincidences
- 🎤 **Voice Notes**: Audio postcards
- 🌙 **Search Moods**: Context-aware themes

## 📁 Project Structure

```
searxng-convivial-instance/
├── docker-compose.yml      # Service orchestration
├── searxng/               # Searxng configuration
│   └── settings.yml       # Main config
├── plugins/               # Custom Python plugins
│   ├── convivial_presence.py
│   ├── discovery_feed.py
│   └── search_moods.py
├── websocket-server/      # Real-time server
├── themes/                # UI themes
├── nginx/                 # Reverse proxy
└── init-db/              # Database schema
```

## 🔧 Configuration

### Adding Friends
```sql
-- Connect to PostgreSQL
docker-compose exec postgres psql -U searxng searxng_convivial

-- Add a friend
INSERT INTO users (username, display_name) 
VALUES ('friend_username', 'Friend Name');
```

### Customizing Engines
Edit `searxng/settings.yml` to add/remove search engines.

### Theme Settings
Themes auto-switch by season. Override in `themes/convivial-theme.css`.

## 🚀 Advanced Usage

### Morning Coffee Schedule
The morning coffee digest runs daily at 8 AM (configurable). Friends receive yesterday's collective discoveries.

### Search Moods
Click the mood selector to set your vibe:
- 🌙 Late night rabbit hole
- 🌺 Sunday morning botanical
- 🎵 Vinyl digging simulation
- 📚 Serious research mode

### Gift Discoveries
Right-click any result → "Gift to friend" → Add message → They'll receive it in 24 hours!

## 🛡️ Privacy & Security

- **No tracking**: Zero analytics or logs
- **Ghost mode**: Browse invisibly
- **Shared secret**: URL-based authentication
- **Local first**: All data stays on your server

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:3000/health
```

### View Logs
```bash
docker-compose logs -f searxng
docker-compose logs -f websocket-server
```

### Database Backup
```bash
docker-compose exec postgres pg_dump -U searxng searxng_convivial > backup.sql
```

## 🤝 Contributing

This is a personal project for friends, but ideas are welcome! Feel free to:
- Open issues for bugs
- Suggest new engines
- Share theme ideas
- Contribute plugins

## 📚 Documentation

- [Development Setup](DEVELOPMENT_SETUP.md) - Deploy without Docker
- [Features & Goals](FEATURES_AND_GOALS.md) - Complete feature list
- [Task Management](TASK_MANAGEMENT_SYSTEM.md) - Implementation roadmap
- [Plugin Development](docs/PLUGIN_GUIDE.md) - Create custom plugins
- [Theme System](docs/THEME_GUIDE.md) - Customize appearance

## 🌈 Philosophy

This isn't just a search engine—it's a space for:
- Intellectual companionship
- Shared discovery journeys
- Ambient awareness of friends' interests
- Celebrating serendipitous connections
- Creating a warm, digital salon

## 📝 License

MIT License - Share the convivial spirit!

---

*Built with love for friends who search together* 💚