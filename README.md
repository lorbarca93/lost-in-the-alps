# Lost in the Alps - Mountain Huts Database

A comprehensive modular scraper system to collect mountain hut data from multiple sources across Europe, including contact information, management details, and opening hours. Features an interactive web map for exploring over 7,400 mountain huts.

## 📊 Current Status

- **Total Huts**: 6,767 (cleaned, deduplicated)
- **Data Sources**: 4 active sources
  - refuges.info: 5,274 huts
  - mountainhuts.info: 671 huts
  - mountain-huts.net: 664 huts
  - tyrol.com: 162 huts
- **Countries Covered**: 41
- **Coverage**: Alps, Apennines, Carpathians, Balkans, and worldwide
- **Data Quality**: 100% coordinates, 100% countries assigned
- **Last Updated**: December 2025

## 🌳 Branching Strategy

This project uses a **simple two-branch strategy**:

- **`main`** - Production branch, automatically deployed to GitHub Pages, Vercel, and Cloudflare Pages
- **`develop`** - Development branch for risky changes and testing (NOT deployed)

**For detailed branching workflow, see [BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md)**

### Quick Branch Commands

```bash
# Switch to develop for risky changes
git checkout develop

# Switch back to main for deployment
git checkout main

# Merge develop to main (when ready to deploy)
git checkout main
git merge develop
git push origin main
```

## 🚀 Quick Start

### Setup

```bash
# Set up virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # On Windows
source .venv/bin/activate   # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### View the Web Interface

```bash
# Start local web server
cd web
python -m http.server 8080

# Open http://localhost:8080 in your browser
```

The web interface provides:

- Interactive map with 7,472+ mountain huts
- Advanced filtering and search
- Real-time weather information
- Favorites system with export functionality
- Mobile-responsive design

### Run Data Collection

```bash
# Run all scrapers (takes ~2-3 minutes)
python scripts/run_all_scrapers.py

# The script will:
# - Scrape all four sources
# - Save data to data/mountain_huts.db
# - Show statistics summary
```

### Update Web Data

After running scrapers or modifying the database:

```bash
# Generate statistics and data files
python tools/api/stats.py         # Updates web/data/stats.json
python tools/api/export_huts.py   # Updates web/data/huts.json
python tools/generate_huts_json.py  # Updates web/data/huts_data.json

# Regenerate interactive map
python tools/create_ultra_simple_map.py
# Map is automatically generated to web/index.html
```

### Data Pipeline (at a glance)

1. Scrape: `python scripts/run_all_scrapers.py`
2. Clean & classify (auto via data_cleaner + reclassify script)
3. Country assign: `python tools/assign_countries_fast.py`
4. Export JSON for web: `python tools/generate_huts_json.py`
5. Serve web UI: `cd web && python -m http.server 8080`

## 📁 Project Structure

```
lost-in-the-alps/
├── src/                    # Source code
│   ├── scrapers/          # Web scraping modules
│   ├── database.py        # Database interface
│   ├── logger_config.py   # Logging configuration
│   └── debug/             # Debug utilities
│
├── scripts/                # Executable scripts
│   ├── run_all_scrapers.py
│   ├── run_refuges_timed.py
│   └── check_scraper_progress.py
│
├── web/                    # Web interface
│   ├── index.html         # Interactive map (main page)
│   ├── about.html         # About page
│   ├── data/              # Data files (JSON)
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript
│
├── tools/                  # Utility tools
│   ├── api/               # Data export tools
│   ├── maintenance/       # Maintenance scripts
│   └── migrations/        # Database migrations
│
├── docs/                   # Documentation
│   ├── guides/            # How-to guides
│   ├── reports/           # Test reports
│   └── archive/           # Archived docs
│
├── data/                   # Database storage
│   └── mountain_huts.db   # SQLite database
│
├── config/                 # Configuration files
│   └── netlify.toml       # Deployment config
│
└── tests/                  # Test files
```

## 🎯 Features

### Data Collection

- **Multi-source scraping**: Aggregates 8,142+ huts from 4 different websites
- **Comprehensive coverage**: Alps, Apennines, Carpathians, Balkans, and worldwide
- **Rich metadata**: 41 countries, multiple hut types, detailed information
- **Time-limited scraping**: Safe long-running operations with automatic stopping
- **Automatic backups**: Database backups before modifications

### Interactive Web Map

- **7,472+ mountain huts** with cluster markers
- **⭐ Favorites system**: Save huts, export/import JSON, export to GPX
- **🔍 Smart search**: Fuzzy search with autocomplete
- **🌤️ Weather widget**: Real-time weather information
- **📍 Nearby huts**: Shows nearest huts within 20km
- **📊 Statistics dashboard**: Live stats with altitude averages
- **7 map layers**: Topographic, Outdoor, Humanitarian, Relief, Light, Satellite, OSM
- **Advanced filters**: Hut type, altitude, capacity, contact info, 41 countries
- **Mobile-responsive**: Touch-optimized design
- **Export functionality**: Download filtered results as KML/KMZ

### Technical

- **Clean database**: Optimized schema with proper indexing
- **Modular design**: Easy to add new scrapers following the base class
- **SQLite database**: Portable, no server required
- **External JSON loading**: Efficient map data handling

### Trust & Safety / Security Highlights

- Mapbox token is **not bundled**; users set it in `localStorage` for Mapbox layers.
- External links use `rel="noopener noreferrer"`; CSP/HSTS headers provided in `_headers` for static hosting.
- See `docs/SECURITY.md` for CSP domains and hosting notes.

## 📖 Usage

### Viewing the Web Interface

```bash
# Serve with Python HTTP server (recommended)
cd web
python -m http.server 8080
# Then open http://localhost:8080 in your browser
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

### Database Maintenance

```bash
# Assign countries to huts based on coordinates
python tools/assign_countries.py

# Force re-check all huts
python tools/assign_countries.py --force

# Clean and optimize database
python tools/clean_database.py

# Improve database quality
python tools/improve_database.py --analyze
```

## 🔧 Adding New Scrapers

1. Copy the template:

   ```bash
   cp src/scrapers/scraper_template.py src/scrapers/scraper_yoursite.py
   ```

2. Implement the `scrape()` method and required properties

3. Test it:

   ```bash
   python src/scrapers/scraper_yoursite.py
   ```

4. It will be auto-discovered by `scripts/run_all_scrapers.py`

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
- **Data**: Rich data including owner, manager, phone, email, website, opening hours, capacity

### 4. refuges.info

- **Coverage**: French Alps, Swiss Alps, Italian Alps
- **Huts**: 5,250
- **Method**: Comprehensive API-based scraping
- **Data**: Detailed descriptions, water availability, capacity, opening hours, contact info

## 📊 Database Schema

Key fields in the `mountain_huts` table:

- **Identity**: id, source, source_id, name
- **Location**: latitude, longitude, altitude, country, region
- **Type**: hut_type (Mountain hut, Bivouac, Unmanned cabin, Shelter, Unknown)
- **Contact**: phone, email, website, owner, manager
- **Details**: description, amenities, capacity, opening_hours, water_source, access_info
- **Metadata**: scraped_at, updated_at

## 🧭 Version Control

### Quick Setup

```bash
# Initialize Git repository
git init

# Configure Git (if not already done)
git config user.name "Your Name"
git config user.email "your@email.com"

# Initial commit
git add .
git commit -m "Initial commit"
```

### Daily Workflow

```bash
# Check what changed
git status

# Stage and commit changes
git add .
git commit -m "Brief description of changes"

# View history
git log --oneline
```

For detailed Git documentation, see:

- `docs/GIT_SETUP_GUIDE.md` - Complete Git setup instructions
- `docs/GIT_QUICK_REFERENCE.md` - Git command reference
- `.gitmessage` - Commit message template

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **Guides**: Step-by-step guides for common tasks
- **Reports**: Test reports and analysis
- **Archive**: Historical documentation

Key documents:

- `docs/DATA_ENRICHMENT_SUMMARY.md` - Data enhancement details
- `docs/REPOSITORY_STRUCTURE.md` - Complete file structure guide
- `docs/QUICK_START.md` - Quick start guide

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
2. Regenerate data files: `python tools/generate_huts_json.py`
3. Refresh browser (Ctrl+F5 to clear cache)

### Database Not Found

The database is created automatically on first run. If missing, run any scraper to recreate it:

```bash
python scripts/run_all_scrapers.py
```

### Scraper Fails

Check `src/debug/` folder for cached responses and debug utilities.

## 📝 License

This project is for personal/educational use. Please respect the terms of service of scraped websites.

## 🌐 Deployment

This repository is structured so that **only the web interface** is deployed to GitHub, while all source code, scrapers, and tools remain local.

### Structure

- **Local Only**: Source code (`src/`), scripts (`scripts/`), tools (`tools/`), database (`data/`), documentation (`docs/`)
- **Deployed**: Web interface (`web/`) - has its own Git repository

### Deploying the Website

The `web/` folder contains a separate Git repository:

```bash
cd web
git add .
git commit -m "Update website"
git push
```

See `DEPLOYMENT_SETUP.md` for detailed deployment instructions.

## 📧 Support

Check the documentation in `docs/` folder or review the code comments for detailed information.
