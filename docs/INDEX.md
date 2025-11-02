# Documentation Index

Welcome to the Lost in the Alps documentation!

## 📚 Documentation Files

### Getting Started

- **[README.md](README.md)** - Project overview (in root folder)
- **[QUICK_START.md](QUICK_START.md)** - Step-by-step getting started guide

### System Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and architecture details
- **[DATABASE_SUMMARY.md](DATABASE_SUMMARY.md)** - Complete database overview and statistics
- **[MULTI_SCRAPER_README.md](MULTI_SCRAPER_README.md)** - Multi-scraper system documentation

### Project History

- **[REFACTORING_SUCCESS.md](REFACTORING_SUCCESS.md)** - Refactoring documentation
- **[SUCCESS_SUMMARY.md](SUCCESS_SUMMARY.md)** - Initial implementation summary

## 🎯 Quick Links

### For Users

- **How do I get started?** → See `QUICK_START.md`
- **What data is available?** → See `DATABASE_SUMMARY.md`
- **How do I query the database?** → Run `python tools/query_database.py`

### For Developers

- **How is the system architected?** → See `ARCHITECTURE.md`
- **How do I add a new scraper?** → See `MULTI_SCRAPER_README.md`
- **Where are the scrapers?** → In the `scrapers/` folder
- **Where is the core code?** → `database.py` and `scrapers/base_scraper.py`

## 📁 Project Structure Overview

```
lostinthealps/
├── scrapers/          # All scraper modules
├── tools/             # Utility scripts
├── data/              # Database files
├── docs/              # Documentation (you are here)
├── debug/             # Debug files and tools
├── database.py        # Core database layer
└── run_all_scrapers.py # Main entry point
```

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
