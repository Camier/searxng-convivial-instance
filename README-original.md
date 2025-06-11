# SearXNG Project

SearXNG is a free internet metasearch engine which aggregates results from various search services and databases. It's a privacy-respecting, hackable metasearch engine.

## Project Information

- **Repository**: https://github.com/searxng/searxng
- **Documentation**: https://docs.searxng.org/
- **License**: AGPLv3
- **Language**: Python

## Features

- No tracking, no profiling, no data mining
- Supports 70+ search engines
- Easy integration of search engines
- Highly customizable
- Supports multiple output formats (HTML, JSON, RSS/OpenSearch)
- Docker ready

## Local Setup

```bash
# Clone the repository
git clone https://github.com/searxng/searxng.git
cd searxng

# Install dependencies
pip install -r requirements.txt

# Configure
cp searxng/settings.yml.example searxng/settings.yml

# Run
python searxng/webapp.py
```

## Docker Setup

```bash
docker pull searxng/searxng
docker run -d -p 8080:8080 searxng/searxng
```

## Notes

- Default port: 8888
- Configuration file: searxng/settings.yml
- Custom engines can be added in searxng/engines/