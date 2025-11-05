# Lost in the Alps - Mountain Huts Database

A modular scraper system to collect comprehensive mountain hut data from multiple sources across Europe, including contact information, management details, and opening hours.

## 📊 Current Status

- **Total Huts**: 8,142 🎉
- **Data Sources**: 4 active sources
  - refuges.info: 5,250 huts (64.5%) - French Alpine refuges
  - mountainhuts.info: 1,343 huts (16.5%) - Europe-wide
  - boudy.info: 889 huts (10.9%) - Czech/Slovak Alps
  - mountain-huts.net: 660 huts (8.1%) - Balkans
- **Countries Covered**: 41 (France, Italy, Switzerland, Czech Republic, Austria, Spain, Slovenia, Poland, Slovakia, Croatia, Bulgaria, Germany, Romania, Andorra, Greece, Bosnia & Herz., Serbia, Hungary, Montenegro, North Macedonia, and 21 others worldwide)
- **Coverage**: Alps, Apennines, Carpathians, Balkans, and worldwide
- **Last Updated**: November 5, 2025

## 🚀 Quick Start

```bash
# Set up virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # On Windows
source .venv/bin/activate   # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# View the website (recommended)
# Open website/index.html in your browser
# Or open website/search.html to search all huts

# Generate website data (if database updated)
python website/api/stats.py
python website/api/export_huts.py

# Run all scrapers (updates database)
python run_all_scrapers.py

# View statistics
python tools/check_stats.py

# Query the database
python tools/query_database.py
```

## 📁 Project Structure

```
lostinthealps/
├── data/                           # Database storage
│   ├── mountain_huts.db           # SQLite database (8,142 huts)
│   └── mountain_huts_backup_*.db  # Automatic backups
│
├── scrapers/                       # Web scraping modules
│   ├── base_scraper.py            # Abstract base class
│   ├── scraper_boudy_info.py      # Boudy.info scraper (889 huts, Alps)
│   ├── scraper_mountain_huts_net.py # Mountain-huts.net scraper (660 huts, Balkans)
│   ├── scraper_mountainhuts_info.py # Mountainhuts.info scraper (1,343 huts, Europe-wide)
│   ├── scraper_refuges_info_fast.py  # Refuges.info scraper (5,250 huts, Alpine refuges)
│   └── scraper_template.py        # Template for new scrapers
│
├── website/                        # Web interface
│   ├── index.html                 # Main landing page with real-time stats
│   ├── map.html                   # Full-screen interactive map
│   ├── mountain_huts_map.html     # Embedded map with all features
│   ├── huts_data.json             # Map data source (8,142 huts)
│   ├── js/main.js                 # Real-time data loading
│   └── api/                       # Data export scripts
│       ├── stats.py               # Export statistics to JSON
│       ├── export_huts.py         # Export all huts to JSON
│       ├── stats.json             # Generated statistics
│       └── huts.json              # Generated huts data
│
├── tools/                          # Utility scripts
│   ├── clean_database.py          # Database cleanup and migration
│   ├── create_ultra_simple_map.py # Generate interactive HTML map
│   ├── harmonize_country_names.py # Standardize country names
│   ├── assign_countries.py        # Geocode coordinates to countries
│   ├── check_stats.py             # View database statistics
│   ├── check_samples.py           # View sample records
│   ├── export_to_json.py          # Export database to JSON
│   ├── query_database.py          # Interactive SQL query tool
│   ├── maintenance/               # Diagnostics utilities
│   └── migrations/                # Schema migration helpers
│
├── docs/                           # Documentation
│   ├── DATA_ENRICHMENT_SUMMARY.md # Data enhancement details
│   ├── REPOSITORY_STRUCTURE.md    # Detailed structure guide
│   ├── GIT_SETUP_GUIDE.md         # Complete Git setup instructions
│   └── GIT_QUICK_REFERENCE.md     # Git command reference
│
├── database.py                     # Core database interface layer
├── run_all_scrapers.py            # Master scraper orchestrator
├── run_refuges_timed.py           # Time-limited scraper for long operations
├── check_scraper_progress.py      # Quick progress checker
├── mountain_huts_map.html         # Generated map (for backup/reference)
├── init_git.ps1                   # Git initialization script
├── requirements.txt               # Python dependencies
├── netlify.toml                   # Netlify deployment config
├── CHANGELOG.md                   # Comprehensive changelog
├── .gitignore                     # Git ignore rules
├── .gitattributes                 # Git file handling rules
├── .gitmessage                    # Commit message template
└── README.md                      # This file
```

## 🎯 Features

### Data Collection
- **Multi-source scraping**: Aggregates 8,142 huts from 4 different websites
- **Comprehensive coverage**: Alps, Apennines, Carpathians, Balkans, and worldwide
- **Rich metadata**: 41 countries, multiple hut types, detailed information
- **Time-limited scraping**: Safe long-running operations with automatic stopping

### Interactive Map
- **8,142 mountain huts** with cluster markers
- **Advanced filters**: Quick presets, search by 41 countries, type, altitude, capacity
- **Beautiful design**: Minimal 4px markers, smooth hover effects
- **Detailed popups**: Full hut information with clickable contact links
- **Export functionality**: Download filtered results as KMZ
- **Full-screen mode**: Dedicated map page for immersive experience

### Website
- **Modern light theme**: Professional, clean UI
- **Real-time statistics**: Dynamic data loading from database
- **Responsive design**: Works on mobile, tablet, and desktop
- **Fast filtering**: Sub-second filtering of 8,142 records
- **Country distribution**: Animated visualizations

### Technical
- **Clean database**: Optimized schema with proper indexing
- **Automatic backups**: Before any database modifications
- **Modular design**: Easy to add new scrapers following the base class
- **SQLite database**: Portable, no server required
- **External JSON loading**: Efficient map data handling

## 📖 Usage

### Viewing the Website

```bash
# Open the main website
start website/index.html  # Windows
open website/index.html   # Mac
xdg-open website/index.html  # Linux

# Or serve with Python HTTP server for full functionality
cd website
python -m http.server 8080
# Then open http://localhost:8080 in your browser
```

The website features:
- **Real-time statistics** from the database (8,142 huts)
- **Interactive charts** showing hut distribution by country
- **Full-screen interactive map** with 15+ advanced filters
- **Beautiful light theme** with modern UI
- **Responsive design** for all devices

### Updating Website Data

```bash
# After running scrapers, regenerate website data
python website/api/stats.py         # Updates statistics
python website/api/export_huts.py   # Updates searchable huts

# Regenerate map with updated data
python tools/create_ultra_simple_map.py
Copy-Item mountain_huts_map.html website/mountain_huts_map.html -Force
```

### Running Scrapers

```bash
# Run all scrapers (takes ~2-3 minutes)
python run_all_scrapers.py

# The script will:
# - Scrape all four sources
# - Save data to data/mountain_huts.db
# - Show statistics summary
```

### Querying Data

```bash
# View overall statistics
python tools/check_stats.py

# View detailed mountainhuts.info stats
python tools/check_mountainhuts_stats.py

# View sample records
python tools/check_samples.py

# Interactive SQL query tool
python tools/query_database.py

# Export to JSON
python tools/export_to_json.py
```

### Updating Country Data

```bash
# Assign countries to huts based on coordinates
python tools/assign_countries.py

# Force re-check all huts
python tools/assign_countries.py --force
```

## 🔧 Adding New Scrapers

1. Copy the template:

   ```bash
   cp scrapers/scraper_template.py scrapers/scraper_yoursite.py
   ```

2. Implement the `scrape()` method and properties

3. Test it:

   ```bash
   python scrapers/scraper_yoursite.py
   ```

4. It will be auto-discovered by `run_all_scrapers.py`

## 📚 Documentation

See the `docs/` folder for detailed documentation:

- **DATA_ENRICHMENT_SUMMARY.md** - Details on enhanced data extraction
- **REPOSITORY_STRUCTURE.md** - Complete file structure guide

## 🗺️ Data Sources

### 1. boudy.info

- **Coverage**: Alps region (France, Italy, Switzerland, Austria, Germany, Slovenia)
- **Huts**: 889
- **Method**: AJAX API calls with grid-based search
- **Data**: Basic info (name, location, altitude)

### 2. mountain-huts.net

- **Coverage**: Balkans (Slovenia, Croatia, Bulgaria, Greece, Bosnia, Serbia, North Macedonia, Montenegro)
- **Huts**: 660
- **Method**: JavaScript marker array parsing
- **Data**: Basic info with country codes

### 3. mountainhuts.info

- **Coverage**: Europe-wide (19 countries)
- **Huts**: 1,343
- **Method**: JavaScript locations array parsing (50+ fields per hut)
- **Data**: **Rich data including:**
  - Owner organization (471 huts)
  - Manager name (539 huts)
  - Phone numbers (663 huts)
  - Email addresses (620 huts)
  - Websites (1,272 huts)
  - Opening hours/months (643 huts)
  - Capacity information
  - Last update dates

### 4. refuges.info

- **Coverage**: French Alps, Swiss Alps, Italian Alps
- **Huts**: 5,250 🎉
- **Method**: Comprehensive API-based scraping of:
  - Cabanes non gardées (unmanned huts) - ~3,700
  - Refuges gardés (staffed refuges) - ~400
  - Bivouacs (bivouac shelters) - ~1,100+
- **Data**: **Comprehensive refuge data including:**
  - Detailed descriptions and remarks
  - Water availability and access information
  - Capacity and shelter type
  - Opening hours and contact info
  - Altitude and precise coordinates
  - Owner and manager details
  - Individual page URLs

## 📊 Database Schema

Key fields in the `mountain_huts` table:

- **Identity**: id, source, source_id, name
- **Location**: latitude, longitude, altitude, country, region
- **Type**: hut_type (Mountain hut, Bivouac, Unmanned cabin, Shelter, Unknown)
- **Contact**: phone, email, website, owner, manager
- **Details**: description, amenities, capacity, opening_hours, water_source, access_info
- **Metadata**: scraped_at, updated_at

## 🧭 Version Control with Git

### Quick Setup

1. **Install Git**: Download from https://git-scm.com/download/win

2. **Run the initialization script**:

   ```bash
   .\init_git.ps1
   ```

   This will guide you through Git setup interactively.

3. **Manual setup** (alternative):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your@email.com"
   git init
   git add .
   git commit -m "Initial commit"
   ```

### Daily Git Workflow

```bash
# Check what changed
git status

# Stage and commit changes
git add .
git commit -m "Brief description of changes"

# View history
git log --oneline
```

### Connect to GitHub

```bash
# Create repository on GitHub first, then:
git remote add origin https://github.com/username/lostinthealps.git
git push -u origin main
```

### Documentation

- **Complete guide**: `docs/GIT_SETUP_GUIDE.md`
- **Quick reference**: `docs/GIT_QUICK_REFERENCE.md`
- **Commit template**: `.gitmessage`

## �📝 License

This project is for personal/educational use. Please respect the terms of service of scraped websites.

## 🐛 Troubleshooting

### Import Errors

Make sure you're in the project root directory and have activated the virtual environment:

```bash
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac
```

### Database Locked

Close any programs that might have the database open (DB Browser, etc.)

### Map Not Showing Huts

1. Regenerate the map: `python tools/create_ultra_simple_map.py`
2. Copy to website: `Copy-Item mountain_huts_map.html website/ -Force`
3. Refresh browser (Ctrl+F5 to clear cache)

### Database Not Found

The database is created automatically on first run. If missing, run any scraper to recreate it.

### Scraper Fails

Check `debug/` folder for cached responses and debug utilities.

## 📧 Support

Check the documentation in `docs/` folder or review the code comments for detailed information.
