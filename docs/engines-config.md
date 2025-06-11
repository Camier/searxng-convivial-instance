# Search Engine Configuration

## 🎓 Academic Research Engines

### Core Scientific
```yaml
priority_1:
  - Google Scholar
  - Semantic Scholar
  - Microsoft Academic
  - CORE (50M+ open access)
  - BASE (300M+ documents)

priority_2:
  - DOAJ (Directory of Open Access Journals)
  - SSRN (Social Sciences)
  - RePEc (Economics)
  - Dimensions (free tier)
  - Unpaywall
```

### Botanical & Ethnopharmacology Focus
```yaml
specialized:
  - PubMed Central
  - PubChem (chemical data)
  - ChEMBL (bioactivity)
  - GBIF (biodiversity)
  - iNaturalist
  - Plants of the World Online (Kew)
  - Tropicos (Missouri Botanical)
  - Native American Ethnobotany Database
  - PROTA (Plant Resources of Tropical Africa)
  - Dr. Duke's Phytochemical Database
```

### 🇫🇷 French Historical Specialization
```yaml
national_archives:
  - Gallica BnF (8M+ documents)
  - Archives Nationales
  - France Archives (meta-search)
  - RetroNews (1631-1950 newspapers)
  - Mémoire des hommes (military)
  - ANOM (colonial archives)

academic_french:
  - Persée (journals)
  - HAL (open archive)
  - OpenEdition
  - Cairn (publications)
  - Theses.fr

regional:
  - All 101 departmental archives
  - Major city archives
  - Diocesan collections

medieval:
  - Biblissima
  - Ménestrel
  - BVMM (manuscripts)
```

### International Historical
```yaml
major_archives:
  - JSTOR (limited free)
  - Internet Archive Scholar
  - HathiTrust
  - Europeana
  - WorldCat
  - DPLA (Digital Public Library of America)

newspapers:
  - Chronicling America (US)
  - British Newspaper Archive
  - Trove (Australia)
  - Papers Past (New Zealand)
```

## 🎵 Music Discovery Engines

### Independent First
```yaml
primary:
  - Bandcamp (artist-friendly)
  - SoundCloud
  - Jamendo (CC music)
  - Free Music Archive
  - ccMixter (remixes)
  - Internet Archive Audio

specialized:
  - Dogmazic (French indie)
  - Ektoplazm (psytrance)
  - Sublime Frequencies
  - Smithsonian Folkways
  - WFMU Free Music Archive
```

### Music Knowledge
```yaml
databases:
  - Discogs (releases & marketplace)
  - MusicBrainz (metadata)
  - Rate Your Music
  - AllMusic (reviews)
  - Genius (lyrics)
  - WhoSampled
  - Setlist.fm

discovery:
  - Music-Map (similar artists)
  - Gnoosic (recommendations)
  - Every Noise at Once
  - Last.fm (stats only, no streaming)
```

### Radio & Streaming
```yaml
radio:
  - Radio Garden (global)
  - SomaFM
  - Radio Paradise
  - NTS Radio
  - Dublab
  - WFMU
  - Resonance FM

dj_mixes:
  - Mixcloud
  - Hearthis.at
  - DJ sets on Archive.org
```

## 🔍 Search Weights & Bangs

### Academic Weight Configuration
```python
ACADEMIC_WEIGHTS = {
    'google_scholar': 1.0,
    'semantic_scholar': 0.9,
    'gallica': 1.2,  # boost French
    'ethnobotany_custom': 1.3,  # boost specialty
    'pubmed': 0.9,
    'core': 0.8,
    'general_search': 0.2  # minimize
}
```

### Music Weight Configuration
```python
MUSIC_WEIGHTS = {
    'bandcamp': 1.3,  # prefer indie
    'soundcloud': 1.0,
    'fma': 1.2,  # boost free
    'discogs': 0.9,
    'spotify': 0.0,  # disabled
    'apple_music': 0.0,  # disabled
}
```

### Bang Shortcuts
```yaml
academic:
  !scholar: Google Scholar
  !gallica: Gallica BnF
  !botanica: Plant databases
  !ethno: Ethnobotany search
  !french: French archives
  !medieval: Medieval sources

music:
  !bc: Bandcamp
  !dig: Deep music search
  !radio: Radio Garden
  !vinyl: Discogs marketplace
  !rare: Obscure music search
  !cc: Creative Commons music
```

## 🔧 Custom Engines

### Ethnobotany Aggregator
```python
custom_engine: "ethnobotany_meta"
sources:
  - Native American Ethnobotany DB
  - Dr. Duke's Database  
  - PROTA
  - Chinese Medicine DB
weight_boost: 1.5
result_merge: "deduplicate"
```

### French Archive Deep Search
```python
custom_engine: "french_historical"
sources:
  - Gallica OCR search
  - RetroNews fulltext
  - Regional archives
paleography_mode: true
date_normalizer: revolutionary_calendar
```

### Underground Music Discovery
```python
custom_engine: "deep_dig"
sources:
  - Bandcamp tags
  - Blog aggregators
  - College radio playlists
  - Netlabels
exclude_mainstream: true
prefer_recent: 6_months
```

---
*Configuration optimized for discovery over efficiency*