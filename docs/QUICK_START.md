# Multi-Scraper System - Quick Reference

## ✅ System Successfully Refactored!

Your mountain huts scraper is now a **modular multi-source system**. You can easily add scrapers for different websites that all feed into the same database.

## 📁 File Structure

```
lostinthealps/
├── database.py                   # ⚙️ Central database layer
├── base_scraper.py              # 🏗️ Base class for all scrapers
├── scraper_boudy_info.py        # 🇨🇿 boudy.info scraper (WORKING)
├── scraper_template.py          # 📝 Template for new scrapers
├── run_all_scrapers.py          # 🚀 Master runner script
├── query_database.py            # 🔍 Query and export tool
├── mountain_huts.db             # 💾 SQLite database
└── MULTI_SCRAPER_README.md      # 📖 Full documentation
```

## 🚀 Usage

### Run a Single Scraper

```powershell
python scraper_boudy_info.py
```

### Run All Scrapers

```powershell
python run_all_scrapers.py
```

### Query the Database

```powershell
python query_database.py
```

## ➕ Adding a New Website

### 1. Copy the Template

```powershell
Copy-Item scraper_template.py scraper_newsite.py
```

### 2. Edit the New File

Replace these parts:

```python
class NewSiteScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "newsite.com"  # ← Change this

    @property
    def source_url(self) -> str:
        return "https://newsite.com"  # ← Change this

    @property
    def source_description(self) -> str:
        return "Description"  # ← Change this

    def scrape(self) -> List[Dict]:
        """Add your scraping logic here"""
        huts = []

        # Fetch data from website
        # Parse the data
        # Create hut dictionaries

        return huts
```

### 3. Create Hut Dictionaries

Each hut should have at minimum:

```python
hut = {
    'source_id': 'unique_id_from_website',  # Required
    'name': 'Hut Name',                     # Required
    'latitude': 46.5,                       # Recommended
    'longitude': 11.5,                      # Recommended
    'url': 'https://...',                   # Recommended
}
```

Optional fields: `altitude`, `country`, `region`, `description`, `capacity`, `phone`, `email`, `website`, `amenities`, `opening_hours`, `image_url`

### 4. Run Your Scraper

```powershell
python scraper_newsite.py
```

Data automatically goes into the same database!

## 📊 Database Features

- **Unified schema** for all sources
- **Automatic deduplication** by (source, source_id)
- **Updates existing** records on re-scrape
- **Tracks sources** and last scrape times
- **Extended fields** for richer data

## 🔍 Query Examples

### Python API

```python
from query_database import MountainHutsDB

db = MountainHutsDB()

# Get all huts
all_huts = db.get_all_huts()

# Search by name
results = db.search_by_name("Chata")

# Find nearby (lat, lon, radius_km)
nearby = db.get_by_location(46.5, 11.5, 25.0)

# Get statistics
stats = db.get_statistics()
```

### Database API

```python
from database import MountainHutsDatabase

db = MountainHutsDatabase()

# Save a single hut
hut = {'source_id': '123', 'name': 'Test', ...}
db.save_hut(hut, source="mysite.com")

# Save multiple huts
db.save_huts_batch(huts, source="mysite.com")

# Get stats
stats = db.get_statistics()
```

## 🎯 Current Status

✅ **889 huts** from boudy.info

- Czech Republic: ~505
- Italy (Alps): ~231
- Slovakia: ~182
- Austria: ~139
- Switzerland: ~113
- France (Alps): ~35
- Slovenia: ~26
- Germany: ~10

## 🌐 Potential Sources to Add

Here are some mountain hut websites you could scrape:

1. **Swiss Alpine Club (SAC)**: https://www.sac-cas.ch/
2. **Austrian Alpine Club**: https://www.alpenverein.at/
3. **Italian Alpine Club (CAI)**: https://www.cai.it/
4. **French Alpine Club**: https://www.ffcam.fr/
5. **Slovenian Mountain Association**: https://www.pzs.si/
6. **refuges.info**: https://www.refuges.info/
7. **huts.ch**: Various Swiss huts
8. **bergwelten.com**: Mountain information

## 💡 Tips

1. **Start simple**: Get basic data first (name, coordinates, URL)
2. **Add fields gradually**: Enhance with altitude, capacity, etc.
3. **Test individually**: Run each scraper alone first
4. **Be polite**: Add delays between requests
5. **Handle errors**: Use try/except blocks

## 📖 Full Documentation

See `MULTI_SCRAPER_README.md` for complete details.

---

**Need help?** Check the template and boudy.info scraper for examples!
