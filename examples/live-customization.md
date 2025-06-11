# 🔥 Live Customization Examples

## Example 1: Instant Theme Changes

```bash
# Start the convivial instance
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Edit theme in another terminal
nano themes/convivial-theme.css
```

Change this:
```css
:root {
  --convivial-primary: #7fb069;  /* Sage green */
}
```

To this:
```css
:root {
  --convivial-primary: #e91e63;  /* Hot pink */
}
```

**Result**: Refresh browser - instant pink theme!

## Example 2: Add Custom Search Engine

```yaml
# Edit searxng/settings.yml while running
engines:
  - name: my music collection
    engine: json_engine
    shortcut: mymusic
    search_url: http://192.168.1.100:8080/search?q={query}
    disabled: false
```

**Result**: Type `!mymusic jazz` - searches your local collection!

## Example 3: Live Plugin Development

```python
# Create plugins/sound_effects.py
import random

name = "Sound Effects"
description = "Adds fun sounds to searches"
default_on = True

sounds = ["🎵", "🎺", "🎸", "🥁", "🎹"]

def post_search(request, search):
    """Add random music emoji to music searches"""
    if any(word in search.search_query.query.lower() 
           for word in ['music', 'song', 'band', 'album']):
        for result in search.result_container.results:
            result['title'] = f"{random.choice(sounds)} {result['title']}"
    return True
```

**Result**: Save file, search "music" - instant musical emojis!

## Example 4: Dynamic Mood Switching

```javascript
// Add to themes/convivial-theme.css
[data-mood="party"] {
  --convivial-background: linear-gradient(45deg, #ff006e, #8338ec, #3a86ff);
  animation: party-gradient 3s ease infinite;
}

@keyframes party-gradient {
  0%, 100% { filter: hue-rotate(0deg); }
  50% { filter: hue-rotate(180deg); }
}
```

```python
# Add to plugins/party_mode.py
def on_request(request, search):
    if "party" in search.search_query.query.lower():
        request.form['mood'] = 'party'
    return True
```

**Result**: Search "party music" - instant disco mode!

## Example 5: Personal Search Shortcuts

```python
# plugins/personal_shortcuts.py
shortcuts = {
    "morning": "site:gutenberg.org philosophy coffee",
    "lunch": "site:allrecipes.com vegetarian quick",
    "workout": "site:youtube.com 10 minute hiit",
    "relax": "site:bandcamp.com ambient meditation"
}

def on_request(request, search):
    query = search.search_query.query.strip()
    if query in shortcuts:
        search.search_query.query = shortcuts[query]
    return True
```

**Result**: Type "morning" - auto-expands to philosophical readings!

## Example 6: Live Data Dashboard

```python
# plugins/search_stats.py
import json
from datetime import datetime

stats_file = "/etc/searxng/stats.json"

def post_search(request, search):
    # Load stats
    try:
        with open(stats_file, 'r') as f:
            stats = json.load(f)
    except:
        stats = {"searches": [], "top_terms": {}}
    
    # Update stats
    query = search.search_query.query
    stats["searches"].append({
        "query": query,
        "time": datetime.now().isoformat(),
        "results": len(search.result_container.results)
    })
    
    # Update top terms
    for word in query.split():
        stats["top_terms"][word] = stats["top_terms"].get(word, 0) + 1
    
    # Save stats
    with open(stats_file, 'w') as f:
        json.dump(stats, f)
    
    # Keep last 100 searches
    stats["searches"] = stats["searches"][-100:]
    
    return True
```

Then access at `http://localhost:8082/stats.json` - live stats!

## 🚀 Why This is Better Than Traditional Setup

1. **No Restart Needed**: Change files, see results immediately
2. **Multiple Versions**: Run stable + experimental simultaneously  
3. **Clean Rollback**: Break something? Just revert the file
4. **Share Easily**: Send docker-compose.yml to friends
5. **Production Mirror**: Dev matches deployment exactly

## 🎯 Try It Now!

```bash
# 1. Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 2. Open three terminals:
# Terminal 1: Watch logs
docker-compose logs -f searxng

# Terminal 2: Edit files
code .  # or your favorite editor

# Terminal 3: Test changes
curl "http://localhost:8080/search?q=test&format=json"

# 3. Make changes and watch them apply instantly!
```

Docker = More personalization, not less! 🐳✨