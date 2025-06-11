# SearXNG Documentation Overview

This document provides a comprehensive overview of all documentation available in the SearXNG GitHub repository.

## Main Documentation Categories

### 1. Root Documentation Files
- **README.rst** - Main project readme
- **CHANGELOG.rst** - Version history and changes
- **CONTRIBUTING.md** - Contribution guidelines
- **SECURITY.md** - Security policies and reporting

### 2. User Documentation (`docs/user/`)
- **about.rst** - About SearXNG
- **configured_engines.rst** - List of configured search engines
- **search-syntax.rst** - Search syntax and operators

### 3. Administrator Documentation (`docs/admin/`)

#### Installation Guides
- **installation.rst** - General installation overview
- **installation-searxng.rst** - SearXNG specific installation
- **installation-docker.rst** - Docker deployment
- **installation-nginx.rst** - Nginx configuration
- **installation-apache.rst** - Apache configuration
- **installation-uwsgi.rst** - uWSGI setup
- **installation-scripts.rst** - Installation scripts

#### Configuration & Settings (`docs/admin/settings/`)
- **settings.rst** - Main settings documentation
- **settings_brand.rst** - Branding configuration
- **settings_engines.rst** - Search engine configuration
- **settings_general.rst** - General settings
- **settings_server.rst** - Server configuration
- **settings_ui.rst** - User interface settings
- **settings_search.rst** - Search behavior settings
- **settings_redis.rst** - Redis configuration
- **settings_outgoing.rst** - Outgoing requests settings
- **settings_plugins.rst** - Plugin configuration

#### Administration Topics
- **api.rst** - API documentation
- **architecture.rst** - System architecture
- **plugins.rst** - Plugin system overview
- **update-searxng.rst** - Update procedures
- **answer-captcha.rst** - CAPTCHA handling
- **searx.limiter.rst** - Rate limiting
- **searx.favicons.rst** - Favicon management

### 4. Developer Documentation (`docs/dev/`)

#### Getting Started
- **quickstart.rst** - Quick start guide for developers
- **contribution_guide.rst** - Development contribution guide
- **makefile.rst** - Makefile documentation
- **lxcdev.rst** - LXC development environment

#### Search Engines (`docs/dev/engines/`)
- **engine_overview.rst** - Engine architecture overview
- **engines.rst** - Engine development guide
- **enginelib.rst** - Engine library documentation
- **offline_concept.rst** - Offline engine concepts
- **xpath.rst** - XPath engine documentation
- **json_engine.rst** - JSON engine documentation
- **mediawiki.rst** - MediaWiki engine guide

#### Online Engines (`docs/dev/engines/online/`)
Major engines documented:
- **google.rst** - Google engine
- **duckduckgo.rst** - DuckDuckGo engine
- **bing.rst** - Bing engine
- **brave.rst** - Brave search engine
- **startpage.rst** - Startpage engine
- **qwant.rst** - Qwant engine
- **wikipedia.rst** - Wikipedia engine
- **yahoo.rst** - Yahoo engine
- Plus 40+ more specialized engines

#### Offline Engines (`docs/dev/engines/offline/`)
- **command-line-engines.rst** - CLI-based engines
- **sql-engines.rst** - SQL database engines
- **nosql-engines.rst** - NoSQL database engines
- **search-indexer-engines.rst** - Search indexer engines

#### Plugins (`docs/dev/plugins/`)
- **development.rst** - Plugin development guide
- **builtins.rst** - Built-in plugins
- **calculator.rst** - Calculator plugin
- **hash_plugin.rst** - Hash plugin
- **unit_converter.rst** - Unit converter plugin
- **tor_check.rst** - Tor check plugin

#### Result Types (`docs/dev/result_types/`)
- **base_result.rst** - Base result structure
- **answer.rst** - Answer results
- **infobox.rst** - Infobox results
- **suggestion.rst** - Suggestion results
- **correction.rst** - Spelling corrections

#### Other Development Topics
- **search_api.rst** - Search API documentation
- **templates.rst** - Template system
- **translation.rst** - Translation/i18n guide
- **extended_types.rst** - Extended type system
- **commits.rst** - Commit guidelines

### 5. Source Code Documentation (`docs/src/`)
- **searx.search.rst** - Search module
- **searx.settings.rst** - Settings module
- **searx.utils.rst** - Utility functions
- **searx.favicons.rst** - Favicon handling
- **searx.locales.rst** - Locale management
- **searx.redisdb.rst** - Redis database
- **searx.sqlitedb.rst** - SQLite database
- **searx.exceptions.rst** - Exception handling
- **searx.botdetection.rst** - Bot detection

### 6. Utilities Documentation (`docs/utils/`)
- **searxng.sh.rst** - SearXNG shell utilities
- **lxc.sh.rst** - LXC container utilities

### 7. Instance Setup
- **own-instance.rst** - Setting up your own instance

## Key Features Documented

1. **Privacy & Security**
   - No user tracking or profiling
   - Secure encrypted connections
   - Tor support for anonymity
   - Bot detection and rate limiting

2. **Search Capabilities**
   - 70+ supported search engines
   - Multiple result types (web, images, videos, etc.)
   - Advanced search syntax
   - Plugin system for extensions

3. **Deployment Options**
   - Docker containers
   - Traditional server installation
   - Multiple web server configurations
   - Development environments

4. **Customization**
   - Theming and branding
   - Custom search engines
   - Plugin development
   - Translation support (58 languages)

## Documentation Formats

- **reStructuredText (.rst)** - Primary documentation format
- **Markdown (.md)** - Used for GitHub-specific files
- **Sphinx** - Documentation build system
- **Jinja2** - Template system for dynamic content

## Building Documentation

```bash
cd docs
make html  # Build HTML documentation
make help  # See all available targets
```

The documentation is comprehensive and well-organized, covering everything from basic usage to advanced development topics.