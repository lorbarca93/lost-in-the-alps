# Documentation Index

Welcome to the Lost in the Alps documentation!

## 📚 Essential Documentation

### Getting Started (Start Here!)

- **[../README.md](../README.md)** - Main project README with quick start guide
  - Overview and current statistics
  - Quick start commands
  - Data sources overview
  - Database schema
  - Git setup guide

### Core Documentation

- **[SCRAPERS.md](SCRAPERS.md)** - Comprehensive scraper documentation

  - How each scraper works
  - Data formats and limitations
  - Adding new scrapers
  - Best practices

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture

  - Component overview
  - Design patterns
  - Extension points

- **[DATABASE_SUMMARY.md](DATABASE_SUMMARY.md)** - Database schema and statistics
  - Table structures
  - Field descriptions
  - Current statistics

### Git & Version Control

- **[GIT_SETUP_GUIDE.md](GIT_SETUP_GUIDE.md)** - Complete Git setup instructions
- **[GIT_QUICK_REFERENCE.md](GIT_QUICK_REFERENCE.md)** - Common Git commands

### Project History

- **[CHANGELOG.md](../CHANGELOG.md)** - Complete change history and releases
- **[DATA_ENRICHMENT_SUMMARY.md](DATA_ENRICHMENT_SUMMARY.md)** - Data enhancement details
- **[REFUGES_INFO_INTEGRATION.md](REFUGES_INFO_INTEGRATION.md)** - refuges.info integration docs
- **[WEBSITE_ENHANCEMENT_SUMMARY.md](WEBSITE_ENHANCEMENT_SUMMARY.md)** - Map website improvements

## 🎯 Quick Navigation

### I Want To...

#### Use the System

- **Get started quickly** → See main [README.md](../README.md) Quick Start section
- **View statistics** → Run `python tools/check_stats.py`
- **Query the database** → Run `python tools/query_database.py`
- **Generate the map** → Run `python tools/create_ultra_simple_map.py`

#### Develop

- **Add a new scraper** → See [SCRAPERS.md](SCRAPERS.md) "Adding a New Scraper" section
- **Understand the architecture** → See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Modify the database** → See [DATABASE_SUMMARY.md](DATABASE_SUMMARY.md)
- **Use Git** → See [GIT_SETUP_GUIDE.md](GIT_SETUP_GUIDE.md)

#### Understand the Data

- **Data sources** → See main [README.md](../README.md) "Data Sources" section
- **Database schema** → See [DATABASE_SUMMARY.md](DATABASE_SUMMARY.md)
- **Scraper details** → See [SCRAPERS.md](SCRAPERS.md)

## 📁 Project Structure

```
lostinthealps/
├── scrapers/                      # Scraper modules
│   ├── base_scraper.py           # Abstract base class
│   ├── scraper_boudy_info.py     # Boudy.info (889 huts)
│   ├── scraper_mountain_huts_net.py # Mountain-huts.net (660 huts)
│   ├── scraper_mountainhuts_info.py # Mountainhuts.info (1,343 huts)
│   ├── scraper_refuges_info_pages.py # Refuges.info (5,274 huts)
│   └── scraper_template.py       # Template for new scrapers
│
├── tools/                         # Utility scripts
│   ├── create_ultra_simple_map.py # Generate interactive map
│   ├── clean_database.py         # Database maintenance
│   ├── harmonize_country_names.py # Country standardization
│   ├── check_stats.py            # View statistics
│   ├── query_database.py         # Query tool
│   ├── assign_countries.py       # Geocoding
│   └── migrations/               # Database migrations
│
├── data/                          # Database storage
│   ├── mountain_huts.db          # SQLite database (8,166 huts)
│   └── mountain_huts_backup_*.db # Automatic backups
│
├── website/                       # Web application
│   ├── index.html                # Main homepage
│   ├── map.html                  # Full-screen map
│   ├── mountain_huts_map.html    # Embedded map
│   ├── huts_data.json            # Map data (8,166 huts)
│   ├── js/main.js                # UI logic
│   └── api/                      # API endpoints
│       ├── stats.json            # Statistics
│       └── huts.json             # All huts data
│
├── docs/                          # Documentation (you are here)
│   ├── INDEX.md                  # This file
│   ├── SCRAPERS.md               # Scraper documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── DATABASE_SUMMARY.md       # Database docs
│   └── GIT_SETUP_GUIDE.md        # Git guide
│
├── database.py                    # Database abstraction layer
├── logger_config.py              # Logging configuration
├── run_all_scrapers.py           # Master scraper runner
├── run_refuges_timed.py          # Time-limited scraper
├── check_scraper_progress.py     # Progress monitoring
├── mountain_huts_map.html        # Generated interactive map (backup)
├── requirements.txt              # Python dependencies
├── netlify.toml                  # Deployment config
├── CHANGELOG.md                  # Comprehensive changelog
├── PROJECT_STATUS.md             # Current project status
└── README.md                     # Main README (START HERE)
```

## 📝 Documentation Updates

Last updated: November 4, 2025

### Recent Changes

- ✅ **Refuges.info comprehensive scraping**: 5,274 huts added
- ✅ **Updated SCRAPERS.md**: Current statistics and time-limited scraping
- ✅ **Created CHANGELOG.md**: Comprehensive changelog with v0.2.0
- ✅ **Created PROJECT_STATUS.md**: Current project overview
- ✅ **Updated README.md**: 8,166 huts, 19 countries, 4 sources
- ✅ **Consolidated documentation**: Removed redundant improvement reports

### Active Documentation

All documentation is current and actively maintained:

- `README.md` - Main project overview ⭐
- `CHANGELOG.md` - Version history and changes ⭐
- `PROJECT_STATUS.md` - Current status snapshot ⭐
- `docs/SCRAPERS.md` - Scraper technical details
- `docs/INDEX.md` - This file

## 🔧 Common Tasks

### View Statistics

```bash
python tools/check_stats.py
```

### Run All Scrapers

```bash
python run_all_scrapers.py
```

### Query Database

```bash
python tools/query_database.py
```

### View Map

```bash
# Serve website locally
cd website
python -m http.server 8080
# Open http://localhost:8080/map.html
```

## 📊 Current Status

- **Total Huts**: 8,166 🎉
- **Data Sources**: 4 (refuges.info, mountainhuts.info, boudy.info, mountain-huts.net)
- **Countries**: 19 (Austria, Italy, Slovenia, Croatia, Bulgaria, Poland, Romania, and more)
- **Last Major Update**: November 4, 2025
- **Version**: 0.2.0

For detailed statistics and breakdown, see:
- `PROJECT_STATUS.md` - Comprehensive project overview
- `CHANGELOG.md` - Latest changes and improvements
- [DATABASE_SUMMARY.md](DATABASE_SUMMARY.md) - Database schema details
