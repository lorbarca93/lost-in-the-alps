# Repository Structure

```
lostinthealps/
├── .venv/                      # Python virtual environment (auto-generated)
├── data/                       # Database storage
│   └── mountain_huts.db       # SQLite database with all hut data (2,892 huts)
├── debug/                      # Debug and reference files
│   └── mountainhuts_locations.js  # Reference: Raw data from mountainhuts.info
├── docs/                       # Documentation
│   ├── DATA_ENRICHMENT_SUMMARY.md  # Summary of data enhancement work
│   └── REPOSITORY_STRUCTURE.md     # This file
├── scrapers/                   # Web scraping modules
│   ├── base_scraper.py        # Abstract base class for all scrapers
│   ├── scraper_boudy_info.py  # Scraper for boudy.info (889 huts)
│   ├── scraper_mountain_huts_net.py  # Scraper for mountain-huts.net (660 huts)
│   ├── scraper_mountainhuts_info.py  # Scraper for mountainhuts.info (1,343 huts)
│   ├── scraper_refuges_info.py       # Template for refuges.info (not implemented)
│   └── scraper_template.py    # Template for creating new scrapers
├── tools/                      # Utility scripts
│   ├── assign_countries.py    # Assign countries using Nominatim geocoding
│   ├── check_mountainhuts_stats.py  # Statistics for mountainhuts.info data
│   ├── check_samples.py       # View sample records from database
│   ├── check_stats.py         # Overall database statistics
│   ├── create_ultra_simple_map.py   # Generate interactive HTML map
│   ├── export_to_json.py      # Export database to JSON format
│   └── query_database.py      # Interactive database query tool
├── .gitignore                  # Git ignore rules
├── database.py                 # Database interface layer
├── mountain_huts_map.html      # Interactive map (generated, 1.27 MB)
├── README.md                   # Main project documentation
├── requirements.txt            # Python dependencies
└── run_all_scrapers.py        # Main script to run all scrapers

```

## Key Files

### Core Files

- **database.py** - Central database handler with MountainHutsDatabase class
- **run_all_scrapers.py** - Master orchestrator to run all scrapers sequentially
- **requirements.txt** - Python package dependencies

### Scrapers

All scrapers inherit from `base_scraper.py` and implement the standard interface:

- `scrape()` - Main scraping method
- `source_name`, `source_url`, `source_description` - Source metadata

### Tools

Utility scripts for various tasks:

- **assign_countries.py** - Use Nominatim API to geocode coordinates to countries
- **create_ultra_simple_map.py** - Generate the interactive Leaflet map
- **check_stats.py** - View database statistics
- **query_database.py** - Run custom SQL queries

### Generated Files

- **mountain_huts_map.html** - Interactive map with all 2,892 huts
- **data/mountain_huts.db** - SQLite database with complete dataset

## Database Schema

The `mountain_huts` table contains:

- **Identity:** id, source, source_id, name
- **Location:** latitude, longitude, altitude, country, region
- **Type:** type, type_description, status, status_description
- **Contact:** phone, email, website, owner, manager
- **Details:** description, amenities, capacity, opening_hours, image_url
- **Metadata:** url, scraped_at, updated_at

## Workflow

### Adding a New Scraper

1. Copy `scrapers/scraper_template.py`
2. Implement the `scrape()` method
3. Add import to `run_all_scrapers.py`
4. Run with `python run_all_scrapers.py`

### Updating the Map

```bash
python tools/create_ultra_simple_map.py
```

### Viewing Statistics

```bash
python tools/check_stats.py
```

### Assigning Countries (if needed)

```bash
python tools/assign_countries.py
# Or with --force to re-check all huts
python tools/assign_countries.py --force
```

## File Size Reference

- Database: ~5-10 MB (2,892 huts with rich data)
- Map HTML: 1.27 MB (includes embedded JSON)
- Debug locations.js: 378 KB (raw reference data)

## Cleanup Policy

- **Keep:** Working scrapers, useful tools, documentation, generated map
- **Remove:** One-time migration scripts, test files, old debug HTML
- **Gitignore:** .venv, **pycache**, \*.db (except in data/), debug files
