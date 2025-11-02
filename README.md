# Lost in the Alps - Mountain Huts Database

A modular scraper system to collect comprehensive mountain hut data from multiple sources across Europe, including contact information, management details, and opening hours.

## 📊 Current Status

- **Total Huts**: 2,892
- **Data Sources**: 3 active (boudy.info, mountain-huts.net, mountainhuts.info)
- **Countries Covered**: 19+ (Austria, Italy, Slovenia, Croatia, Bulgaria, Poland, Romania, Slovakia, Greece, Bosnia, Serbia, North Macedonia, Montenegro, Germany, Czech Republic, Switzerland, France, Hungary, Liechtenstein)
- **Enriched Data**: 471 with owner info, 539 with manager info, 663 with phone, 620 with email

## 🚀 Quick Start

```bash
# Set up virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # On Windows
source .venv/bin/activate   # On Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up Git (optional but recommended)
# See docs/GIT_SETUP_GUIDE.md for detailed instructions
git init
git add .
git commit -m "Initial commit"

# Run all scrapers
python run_all_scrapers.py

# Generate interactive map
python tools/create_ultra_simple_map.py

# View statistics
python tools/check_stats.py

# Query the database
python tools/query_database.py

# Open the map
# Just open mountain_huts_map.html in your browser
```

## 📁 Project Structure

```
lostinthealps/
├── data/                           # Database storage
│   └── mountain_huts.db           # SQLite database (2,892 huts)
│
├── scrapers/                       # Web scraping modules
│   ├── base_scraper.py            # Abstract base class
│   ├── scraper_boudy_info.py      # Boudy.info scraper (889 huts, Alps)
│   ├── scraper_mountain_huts_net.py # Mountain-huts.net scraper (660 huts, Balkans)
│   ├── scraper_mountainhuts_info.py # Mountainhuts.info scraper (1,343 huts, Europe-wide)
│   ├── scraper_refuges_info.py    # Template for future implementation
│   └── scraper_template.py        # Template for new scrapers
│
├── tools/                          # Utility scripts
│   ├── create_ultra_simple_map.py # Generate interactive HTML map
│   ├── assign_countries.py        # Geocode coordinates to countries (Nominatim)
│   ├── check_stats.py             # View database statistics
│   ├── check_samples.py           # View sample records
│   ├── check_mountainhuts_stats.py # Detailed mountainhuts.info statistics
│   ├── export_to_json.py          # Export database to JSON
│   └── query_database.py          # Interactive SQL query tool
│
├── docs/                           # Documentation
│   ├── DATA_ENRICHMENT_SUMMARY.md # Data enhancement details
│   ├── REPOSITORY_STRUCTURE.md    # Detailed structure guide
│   ├── GIT_SETUP_GUIDE.md         # Complete Git setup instructions
│   └── GIT_QUICK_REFERENCE.md     # Git command reference
│
├── database.py                     # Core database interface layer
├── run_all_scrapers.py            # Master scraper orchestrator
├── mountain_huts_map.html         # Interactive map (1.27 MB, generated)
├── init_git.ps1                   # Git initialization script
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── .gitattributes                 # Git file handling rules
├── .gitmessage                    # Commit message template
└── README.md                      # This file
```

## 🎯 Features

- **Multi-source scraping**: Aggregates data from 3 different websites
- **Rich data**: Owner, manager, contact info, opening hours for many huts
- **Interactive map**: Leaflet-based map with detailed popups and country filters
- **Modular design**: Easy to add new scrapers following the base class
- **Geocoding**: Automatic country assignment using Nominatim API
- **SQLite database**: Portable, no server required

## 📖 Usage

### Running Scrapers

```bash
# Run all scrapers (takes ~2-3 minutes)
python run_all_scrapers.py

# The script will:
# - Scrape all three sources
# - Save data to data/mountain_huts.db
# - Show statistics summary
```

### Viewing the Map

```bash
# Generate/update the interactive map
python tools/create_ultra_simple_map.py

# Open in browser
start mountain_huts_map.html  # Windows
open mountain_huts_map.html   # Mac
xdg-open mountain_huts_map.html  # Linux
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

## 📊 Database Schema

Key fields in the `mountain_huts` table:

- **Identity**: id, source, source_id, name
- **Location**: latitude, longitude, altitude, country, region
- **Contact**: phone, email, website, owner, manager
- **Details**: description, amenities, capacity, opening_hours
- **Metadata**: scraped_at, updated_at

## � Version Control with Git

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

Regenerate the map: `python tools/create_ultra_simple_map.py`

### Database Not Found

The database is created automatically on first run. If missing, run any scraper to recreate it.

### Scraper Fails

Check `debug/` folder for cached responses and debug utilities.

## 📧 Support

Check the documentation in `docs/` folder or review the code comments for detailed information.
