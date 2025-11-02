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
│   ├── scraper_refuges_info_pages.py # Refuges.info (54 huts)
│   └── scraper_template.py       # Template for new scrapers
│
├── tools/                         # Utility scripts
│   ├── create_ultra_simple_map.py # Generate interactive map
│   ├── check_stats.py            # View statistics
│   ├── query_database.py         # Query tool
│   ├── assign_countries.py       # Geocoding
│   └── migrations/               # Database migrations
│
├── data/                          # Database storage
│   └── mountain_huts.db          # SQLite database (2,946 huts)
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
├── mountain_huts_map.html        # Generated interactive map
├── requirements.txt              # Python dependencies
├── CHANGELOG.md                  # Change history
└── README.md                     # Main README (START HERE)
```

## 📝 Documentation Updates

Last updated: 2024 (after refuges.info integration, security fixes, hut_type migration)

### Recent Changes
- ✅ Added SCRAPERS.md with comprehensive scraper documentation
- ✅ Created CHANGELOG.md for change tracking
- ✅ Updated README with latest statistics (2,946 huts, 4 sources)
- ✅ Consolidated duplicate documentation

### Deprecated Files
The following files are kept for historical reference but are superseded by newer docs:
- `QUICK_START.md` → See main README.md instead
- `MULTI_SCRAPER_README.md` → See SCRAPERS.md instead
- `README.md` (in docs/) → Outdated, see main README.md

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

Open `mountain_huts_map.html` in your browser

## 📊 Current Status

- **Total Huts**: 1,549
- **Data Sources**: 2
- **Countries**: 8+
- **Last Updated**: November 2025

For detailed statistics, see [DATABASE_SUMMARY.md](DATABASE_SUMMARY.md)
