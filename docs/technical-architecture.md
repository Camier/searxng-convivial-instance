# Technical Architecture

## 🏗️ Infrastructure Overview

### Hardware Requirements
```yaml
minimal_setup:
  vps:
    ram: 4GB
    cpu: 2 cores
    storage: 50GB SSD
    bandwidth: unlimited
    cost: ~$20/month

recommended_setup:
  vps:
    ram: 8GB
    cpu: 4 cores
    storage: 100GB SSD
    bandwidth: unlimited
    cost: ~$40/month
    
split_cost: $5-10 per friend
```

### Software Stack
```yaml
core:
  - Ubuntu 22.04 LTS
  - Docker & Docker Compose
  - Nginx (reverse proxy)
  - Let's Encrypt SSL

searxng:
  - SearXNG (latest)
  - Custom theme
  - Plugin extensions

persistence:
  - PostgreSQL 14 (user data)
  - Redis 7 (cache & realtime)

realtime:
  - Node.js (WebSocket server)
  - Socket.io
  - Redis pub/sub
```

## 🔌 Plugin Architecture

### Core Plugins
```python
# convivial_presence.py
class ConvivialPresence(Plugin):
    """Real-time friend awareness"""
    features = [
        "active_searches",
        "reading_status", 
        "mood_indicator",
        "avatar_fade"
    ]

# discovery_feed.py  
class DiscoveryFeed(Plugin):
    """Shared findings stream"""
    features = [
        "morning_digest",
        "live_updates",
        "gift_discoveries",
        "coincidence_detection"
    ]

# voice_notes.py
class VoiceNotes(Plugin):
    """Audio annotations everywhere"""
    features = [
        "result_comments",
        "voice_postcards",
        "audio_reactions",
        "transcription"
    ]

# search_moods.py
class SearchMoods(Plugin):
    """Vibe-based search modes"""
    moods = {
        "late_night": "deep_dive_mode",
        "morning": "gentle_discovery",
        "chaos": "anything_goes"
    }

# time_capsule.py
class TimeCapsule(Plugin):
    """Scheduled discoveries"""
    features = [
        "future_surprises",
        "anniversary_returns",
        "seasonal_collections"
    ]
```

### WebSocket Architecture
```javascript
// Real-time presence system
const presenceServer = {
  namespace: '/presence',
  
  events: {
    'search:start': broadcastToFriends,
    'search:results': showSharedInterest,
    'annotation:add': syncAnnotation,
    'mood:change': updateAwareness,
    'gift:send': notifyRecipient
  },
  
  redis: {
    pub: 'searxng:presence:out',
    sub: 'searxng:presence:in'
  }
}
```

### Database Schema
```sql
-- PostgreSQL schema
CREATE TABLE users (
  id UUID PRIMARY KEY,
  username VARCHAR(50) UNIQUE,
  avatar_url TEXT,
  current_mood VARCHAR(50),
  created_at TIMESTAMP
);

CREATE TABLE collections (
  id UUID PRIMARY KEY,
  name VARCHAR(100),
  type VARCHAR(50), -- 'curiosity', 'musical', 'botanical', etc
  owner_id UUID REFERENCES users(id),
  is_public BOOLEAN DEFAULT true,
  metadata JSONB
);

CREATE TABLE discoveries (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  query TEXT,
  result_url TEXT,
  result_data JSONB,
  annotations JSONB,
  gifted_to UUID REFERENCES users(id),
  discovered_at TIMESTAMP
);

CREATE TABLE voice_notes (
  id UUID PRIMARY KEY,
  discovery_id UUID REFERENCES discoveries(id),
  user_id UUID REFERENCES users(id),
  audio_url TEXT,
  transcript TEXT,
  duration INTEGER
);
```

## 🔐 Security & Privacy

### Authentication Flow
```yaml
options:
  simple:
    - Shared secret URL
    - No individual accounts
    - Trust-based access
    
  oauth:
    - GitHub/GitLab OAuth
    - Individual accounts
    - Granular permissions
    
  federated:
    - Each friend hosts instance
    - Cross-instance auth
    - Decentralized model
```

### Privacy Features
```python
privacy_config = {
    "ghost_mode": {
        "trigger_keywords": ["medical", "personal", "private"],
        "auto_enable": True,
        "no_history": True,
        "no_sharing": True
    },
    
    "data_retention": {
        "search_history": "30_days",
        "voice_notes": "forever",
        "gift_discoveries": "forever",
        "ghost_searches": "never"
    },
    
    "sharing_defaults": {
        "searches": "friends_only",
        "collections": "public",
        "annotations": "friends_only",
        "voice_notes": "opt_in"
    }
}
```

## 🚀 Deployment Guide

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/friends/searxng-convivial
cd searxng-convivial

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Launch services
docker-compose up -d

# 4. Initialize database
docker-compose exec app python manage.py init_db

# 5. Install plugins
docker-compose exec app python manage.py install_plugins
```

### Configuration Files
```yaml
# docker-compose.yml
version: '3.8'
services:
  searxng:
    image: searxng/searxng:latest
    volumes:
      - ./searxng:/etc/searxng
      - ./plugins:/usr/local/searxng/plugins
    depends_on:
      - redis
      - postgres
      
  redis:
    image: redis:7-alpine
    
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: convivial
      
  websocket:
    build: ./websocket
    depends_on:
      - redis
```

## 🔄 Integration Points

### External Services
```yaml
optional_integrations:
  - Hypothesis (web annotations)
  - IPFS (decentralized storage)
  - ActivityPub (future federation)
  - Mopidy (background music)
  
avoid:
  - Google Analytics
  - Facebook anything
  - Commercial APIs
  - Tracking services
```

### Performance Optimization
```yaml
caching:
  - Redis for hot data
  - PostgreSQL materialized views
  - CDN for static assets
  - Service worker for offline

scaling:
  - Horizontal WebSocket scaling
  - Read replicas for search
  - Async job processing
  - Rate limiting per user
```

---
*Architecture designed for joy, not scale*