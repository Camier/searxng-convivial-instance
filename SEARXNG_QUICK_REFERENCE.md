# SearXNG Quick Reference Guide

## Documentation Structure in GitHub

### Documentation Locations
```
/home/mik/GITHUB/searxng/
├── docs/                     # Main documentation
│   ├── admin/               # Administrator guides
│   ├── dev/                 # Developer documentation
│   ├── user/                # User guides
│   └── utils/               # Utility documentation
├── README.rst               # Project overview
├── CONTRIBUTING.md          # How to contribute
├── CHANGELOG.rst            # Version history
└── SECURITY.md              # Security policies
```

### Configuration Files
```
searx/settings.yml                          # Main settings file
utils/templates/etc/searxng/settings.yml    # Settings template
tests/unit/settings/                        # Example settings for testing
```

## Key Documentation Files

### For Users
- `docs/user/about.rst` - What is SearXNG
- `docs/user/search-syntax.rst` - How to search effectively
- `docs/user/configured_engines.rst` - Available search engines

### For Administrators
- `docs/admin/installation.rst` - Installation overview
- `docs/admin/installation-docker.rst` - Docker setup
- `docs/admin/settings/settings.rst` - Configuration guide
- `docs/admin/update-searxng.rst` - Update procedures

### For Developers
- `docs/dev/quickstart.rst` - Getting started
- `docs/dev/engines/engine_overview.rst` - Engine architecture
- `docs/dev/plugins/development.rst` - Plugin development
- `docs/dev/contribution_guide.rst` - Contributing code

## Important Topics Covered

### 1. Search Engines (70+ documented)
- Google, DuckDuckGo, Bing, Brave
- Wikipedia, Wikidata
- YouTube, Peertube, Odysee
- GitHub, GitLab
- And many more specialized engines

### 2. Installation Methods
- Docker (recommended)
- Manual installation
- Script-based installation
- Various web server configurations (Nginx, Apache)

### 3. Configuration Areas
- Branding and UI customization
- Search behavior settings
- Engine configuration
- Redis integration
- Rate limiting
- Plugin system

### 4. Development Topics
- Creating new search engines
- Plugin development
- Translation/localization
- API usage
- Testing framework

## Quick Commands

### View documentation locally
```bash
cd /home/mik/GITHUB/searxng/docs
make html
# Documentation will be in _build/html/
```

### Run SearXNG
```bash
cd /home/mik/GITHUB/searxng
python searx/webapp.py
```

### Run with Docker
```bash
docker pull searxng/searxng
docker run -d -p 8080:8080 searxng/searxng
```

## Documentation Stats
- **Total documentation files**: 150+ .rst files
- **Search engines documented**: 70+
- **Languages supported**: 58
- **Plugin types**: 10+

## Online Resources
- Official site: https://docs.searxng.org/
- Public instances: https://searx.space/
- GitHub: https://github.com/searxng/searxng
- Matrix chat: #searxng:matrix.org