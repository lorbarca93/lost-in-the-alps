# Mountain Huts Multi-Scraper System

A modular scraping framework for collecting mountain hut data from multiple websites into a unified database.

## 🏗️ Architecture

The system is designed with a modular architecture:

```
├── database.py              # Central database layer
├── base_scraper.py         # Abstract base class for all scrapers
├── scraper_boudy_info.py   # boudy.info scraper
├── scraper_*.py            # Add more scrapers here
├── run_all_scrapers.py     # Master script to run all scrapers
├── query_database.py       # Database query tool
└── mountain_huts.db        # SQLite database (created automatically)
```

## 🚀 Quick Start

### 1. Run a Single Scraper

```powershell
# Run the boudy.info scraper
python scraper_boudy_info.py
```

### 2. Run All Scrapers

```powershell
# Run all available scrapers
python run_all_scrapers.py

# Run specific scrapers
python run_all_scrapers.py boudy_info another_site
```

### 3. Query the Database

```powershell
# Interactive query tool
python query_database.py
```

## 📦 Database Schema

The unified database stores huts from all sources:

### Main Table: `mountain_huts`

| Column             | Type      | Description                         |
| ------------------ | --------- | ----------------------------------- |
| id                 | INTEGER   | Primary key (auto-increment)        |
| **source**         | TEXT      | Website source (e.g., "boudy.info") |
| **source_id**      | TEXT      | Original ID from source website     |
| name               | TEXT      | Hut name                            |
| type               | INTEGER   | Type code                           |
| type_description   | TEXT      | Human-readable type                 |
| status             | INTEGER   | Status code                         |
| status_description | TEXT      | Human-readable status               |
| latitude           | REAL      | GPS latitude                        |
| longitude          | REAL      | GPS longitude                       |
| altitude           | INTEGER   | Elevation (meters)                  |
| description        | TEXT      | Full description                    |
| url                | TEXT      | Direct link to hut page             |
| **country**        | TEXT      | Country name/code                   |
| **region**         | TEXT      | Region/area name                    |
| **amenities**      | TEXT      | Available amenities                 |
| **capacity**       | INTEGER   | Number of beds/people               |
| **phone**          | TEXT      | Contact phone                       |
| **email**          | TEXT      | Contact email                       |
| **website**        | TEXT      | Official website                    |
| **opening_hours**  | TEXT      | Opening hours/season                |
| **image_url**      | TEXT      | Main image URL                      |
| scraped_at         | TIMESTAMP | First scrape time                   |
| updated_at         | TIMESTAMP | Last update time                    |

**Unique constraint**: (source, source_id)

### Sources Table: `scraper_sources`

Tracks all registered scraper sources:

| Column       | Type      | Description            |
| ------------ | --------- | ---------------------- |
| id           | INTEGER   | Primary key            |
| name         | TEXT      | Source name (unique)   |
| url          | TEXT      | Base URL               |
| description  | TEXT      | Source description     |
| last_scraped | TIMESTAMP | Last scrape time       |
| total_huts   | INTEGER   | Total huts from source |

## ✨ Creating a New Scraper

### Step 1: Copy the Template

```powershell
Copy-Item scraper_template.py scraper_yoursite.py
```

### Step 2: Implement Your Scraper

```python
from base_scraper import BaseScraper
from typing import List, Dict

class YourSiteScraper(BaseScraper):

    @property
    def source_name(self) -> str:
        return "yoursite.com"

    @property
    def source_url(self) -> str:
        return "https://yoursite.com"

    @property
    def source_description(self) -> str:
        return "Description of the website"

    def scrape(self) -> List[Dict]:
        """Main scraping logic"""
        huts = []

        # 1. Fetch data from website
        response = self.session.get(f"{self.source_url}/api/huts")
        data = response.json()

        # 2. Parse and convert to standard format
        for item in data:
            hut = {
                'source_id': str(item['id']),
                'name': item['name'],
                'latitude': item['lat'],
                'longitude': item['lon'],
                'altitude': item.get('elevation'),
                'country': item.get('country'),
                'url': f"{self.source_url}/hut/{item['id']}"
            }

            # 3. Normalize and add to list
            normalized = self.normalize_hut_data(hut)
            huts.append(normalized)

        return huts

if __name__ == "__main__":
    scraper = YourSiteScraper()
    scraper.run()
```

### Step 3: Run Your Scraper

```powershell
# Run standalone
python scraper_yoursite.py

# Or run with all scrapers
python run_all_scrapers.py
```

## 🔍 Available Fields

When creating a hut dictionary, you can include:

**Required:**

- `source_id`: Unique ID from source (string)
- `name`: Hut name (string)

**Optional but Recommended:**

- `latitude`: GPS latitude (float)
- `longitude`: GPS longitude (float)
- `url`: Direct link to hut page (string)
- `country`: Country name or code (string)

**Additional Fields:**

- `altitude`: Elevation in meters (int)
- `description`: Full text description (string)
- `region`: Region/area name (string)
- `type`: Numeric type code (int)
- `type_description`: Human-readable type (string)
- `status`: Status code (int)
- `status_description`: Human-readable status (string)
- `amenities`: Comma-separated amenities (string)
- `capacity`: Number of beds (int)
- `phone`: Contact phone (string)
- `email`: Contact email (string)
- `website`: Official website (string)
- `opening_hours`: Opening hours/season (string)
- `image_url`: Main image URL (string)

## 📊 Querying Data

### Using the Interactive Tool

```powershell
python query_database.py
```

Commands:

- `stats` - Show comprehensive statistics
- `all` - List all huts
- `search` - Search by name
- `type` - Filter by type
- `location` - Search by GPS coordinates
- `export-json` - Export to JSON
- `export-csv` - Export to CSV

### Using Python API

```python
from query_database import MountainHutsDB

db = MountainHutsDB()

# Get all huts
huts = db.get_all_huts()

# Search by name
results = db.search_by_name("Chata")

# Find nearby huts (lat, lon, radius_km)
nearby = db.get_by_location(46.5, 11.5, 25.0)

# Get statistics
stats = db.get_statistics()
print(f"Total huts: {stats['total_huts']}")
print(f"Sources: {[s['source'] for s in stats['by_source']]}")
```

## 🌐 Current Scrapers

### boudy.info

- **Coverage**: Czech Republic, Slovakia, Austria, Switzerland, Italy, France, Germany, Slovenia
- **Huts**: ~889 huts
- **Types**: Bivouacs, shelters, mountain huts, hotels
- **Features**: GPS coordinates, types, status

## 🎯 Example Use Cases

### Add a New Website

1. Create `scraper_newsite.py` based on the template
2. Implement the `scrape()` method
3. Run it: `python scraper_newsite.py`
4. Data automatically merges into the same database

### Update Existing Data

Simply run the scraper again:

```powershell
python scraper_boudy_info.py
```

The system uses `(source, source_id)` to avoid duplicates and updates existing records.

### Combine Multiple Sources

```powershell
# Run all scrapers
python run_all_scrapers.py

# Query combined data
python query_database.py
```

### Export Combined Data

```python
from query_database import MountainHutsDB

db = MountainHutsDB()
db.export_to_json("all_huts.json")
db.export_to_csv("all_huts.csv")
```

## 🛠️ Advanced Usage

### Database Layer

Direct database access:

```python
from database import MountainHutsDatabase

db = MountainHutsDatabase("custom_db.db")
db.init_database()

# Register a source
db.register_source("mysite.com", "https://mysite.com", "My site description")

# Save a hut
hut = {
    'source_id': '123',
    'name': 'Test Hut',
    'latitude': 46.5,
    'longitude': 11.5
}
db.save_hut(hut, source="mysite.com")

# Save multiple huts
huts = [...]
db.save_huts_batch(huts, source="mysite.com")
```

### Custom Base Scraper

Extend `BaseScraper` for special needs:

```python
from base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.session.headers['Authorization'] = f'Bearer {api_key}'

    def scrape(self):
        # Your custom logic
        pass
```

## 📝 Notes

- All scrapers share the same database
- Duplicate detection by `(source, source_id)`
- Updates existing records on re-scrape
- Polite scraping with delays built-in
- Extensible for any mountain hut website

## 🤝 Contributing

To add a new scraper:

1. Copy `scraper_template.py`
2. Implement the required methods
3. Test with `python scraper_yourname.py`
4. Submit a pull request!

## 📄 License

Respect the terms of service of each source website.
Give proper attribution when using the data.
