# 🎨 Searxng Convivial Personalization Guide

## Docker vs Traditional Setup Comparison

### With Docker (Recommended)
✅ **Hot-reload everything** - No service restarts needed
✅ **Multiple instances** - Run different configs simultaneously  
✅ **Easy rollback** - Just change docker image tag
✅ **Clean dependencies** - No system pollution
✅ **Production-identical** - Dev matches deployment exactly

### Without Docker
❌ System Python conflicts
❌ Manual dependency management
❌ Harder to test multiple configs
❌ Service restarts for changes
❌ Dev != Production differences

## 🔧 Live Personalization Options

### 1. Real-Time Theme Changes
```bash
# Edit theme while running
nano themes/convivial-theme.css
# Changes appear immediately on refresh!
```

### 2. Hot-Reload Plugins
```python
# plugins/my_custom_plugin.py
name = "My Plugin"
description = "Custom functionality"

def on_request(request, search):
    # Your code here
    pass
```
Just save the file - Searxng detects and loads it!

### 3. Dynamic Settings
```yaml
# searxng/settings.yml
# Edit while running - some changes need container restart
convivial:
  morning_coffee_hour: 9  # Changed from 8
  max_friends: 5          # Increased from 3
```

### 4. Custom Search Engines
```yaml
# searxng/engines/my_archive.yml
- name: my local archive
  engine: json_engine
  shortcut: local
  search_url: http://my-server/search?q={query}
  # Add without rebuilding!
```

## 🎭 Advanced Personalization

### Multiple Personalities
```bash
# docker-compose.botanical.yml
version: '3.8'
services:
  searxng:
    environment:
      - THEME_MODE=botanical
    volumes:
      - ./themes/botanical:/theme

# Run botanical version
docker-compose -f docker-compose.yml -f docker-compose.botanical.yml up
```

### A/B Testing
```nginx
# nginx/conf.d/ab-test.conf
upstream searxng_a {
    server searxng-a:8080;
}
upstream searxng_b {
    server searxng-b:8080;
}

server {
    location / {
        # 50/50 split
        proxy_pass http://searxng_$cookie_variant;
    }
}
```

### Development Workflow
```bash
# 1. Make changes to any file
vim plugins/new_feature.py

# 2. Test immediately (no restart!)
curl http://localhost:8080/search?q=test

# 3. See logs live
docker-compose logs -f searxng

# 4. Debug interactively
docker-compose exec searxng python
>>> import searx
>>> searx.settings['convivial']
```

## 🔌 Plugin Development with Docker

### Live Development Mount
```yaml
# docker-compose.override.yml
services:
  searxng:
    volumes:
      # Mount entire development directory
      - ./dev/searx:/usr/local/searxng/searx:rw
    environment:
      - SEARXNG_DEBUG=1
      - FLASK_ENV=development
```

### Interactive Testing
```bash
# Enter container
docker-compose exec searxng bash

# Install dev tools
pip install ipython pytest

# Run tests
pytest plugins/test_convivial.py

# Interactive debugging
ipython
In [1]: from searx.plugins import convivial_presence
In [2]: convivial_presence.get_active_friends()
```

## 🎨 Theme Development

### Live CSS Editing
```css
/* themes/convivial-theme.css */
/* Edit this file - changes appear on refresh! */
:root {
  --convivial-primary: #custom-color;
}

/* Add DevTools-like experience */
.debug-mode {
  border: 2px solid red !important;
}
```

### Template Overrides
```html
<!-- templates/custom/index.html -->
{% extends "index.html" %}
{% block content %}
  <!-- Your custom homepage -->
  <div class="morning-coffee">
    {{ morning_coffee_content }}
  </div>
  {{ super() }}
{% endblock %}
```

## 🚀 Performance Tuning

### Resource Limits
```yaml
# docker-compose.yml
services:
  searxng:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
    # Easy to adjust and test impact
```

### Caching Strategies
```yaml
redis-cache:
  command: >
    redis-server
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
    --save ""  # Disable persistence for speed
```

## 📝 Configuration Management

### Environment-Based Config
```bash
# .env.development
SEARXNG_DEBUG=true
THEME=development
CACHE_TIMEOUT=10

# .env.production  
SEARXNG_DEBUG=false
THEME=convivial
CACHE_TIMEOUT=3600

# Switch easily
docker-compose --env-file .env.development up
```

### Git-Friendly Setup
```gitignore
# Track your personalizations
!themes/my-theme/
!plugins/my-plugins/
!searxng/settings.yml

# Ignore generated files
searxng/settings.yml.bak
*.pyc
```

## 🔄 Update Without Breaking

### Safe Updates
```bash
# 1. Test new version
docker pull searxng/searxng:new-version
docker-compose run --rm searxng-test

# 2. Backup current state
docker-compose exec postgres pg_dump -U searxng > backup.sql

# 3. Update safely
docker-compose down
docker-compose up -d
```

### Rollback in Seconds
```bash
# Something broke? Roll back!
docker-compose down
sed -i 's/searxng:latest/searxng:previous/' docker-compose.yml
docker-compose up -d
# Fixed in 30 seconds!
```

## 💡 Pro Tips

1. **Use Volume Mounts**: All personalizations in host folders
2. **Layer Configs**: Base + environment-specific overrides
3. **Version Control**: Track your personal configs in git
4. **Test Locally**: Identical setup to production
5. **Debug Easily**: Full access to container internals

## 🎯 Best Practices

### Development Loop
```bash
# Terminal 1: Run services
docker-compose up

# Terminal 2: Watch logs
docker-compose logs -f searxng

# Terminal 3: Edit files
code .  # Your changes appear live!

# Terminal 4: Test changes
./test-search.sh "botanical query"
```

### Production Deployment
```bash
# Same personalization, production-ready
docker-compose -f docker-compose.yml \
               -f docker-compose.prod.yml \
               up -d
```

## Summary

Docker provides **more** personalization because:
- 🔥 Hot-reload everything
- 🧪 Safe experimentation
- 🎭 Multiple configurations
- 🚀 Instant rollback
- 📦 Clean isolation
- 🔧 Full development access

The containerization adds flexibility, not restrictions!