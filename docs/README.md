# Mountain Huts Scraper - boudy.info

A Python-based web scraper for extracting mountain huts, bivouacs, and shelters data from [boudy.info](https://www.boudy.info/) and storing it in a local SQLite database.

## Features

- **Web Scraping**: Extracts data from boudy.info including:

  - Hut names
  - Types (bivouac, shelter, mountain hut, hotel)
  - Status (new, approved, deleted, secret)
  - GPS coordinates (latitude/longitude)
  - Altitude
  - Descriptions
  - Direct URLs to each hut

- **Local Database**: Stores all data in SQLite database for easy querying

- **Query Tools**: Search and filter huts by:

  - Name
  - Type
  - Location (radius search)
  - Get statistics

- **Export Options**: Export data to JSON or CSV formats

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### 1. Run the Scraper

```bash
python scraper.py
```

This will:

- Create a `mountain_huts.db` SQLite database
- Scrape the boudy.info website
- Store all found mountain huts in the database

### 2. Query the Database

```bash
python query_database.py
```

Interactive commands:

- `stats` - Show database statistics
- `all` - List all huts
- `search` - Search by name
- `type` - Filter by type (0-3)
- `location` - Search by GPS coordinates
- `export-json` - Export to JSON file
- `export-csv` - Export to CSV file

### Programmatic Usage

```python
from query_database import MountainHutsDB

# Initialize database connection
db = MountainHutsDB("mountain_huts.db")

# Get all huts
all_huts = db.get_all_huts()

# Search by name
results = db.search_by_name("Chata")

# Get huts near a location (lat, lon, radius in km)
nearby = db.get_by_location(49.2, 16.6, 25.0)

# Get statistics
stats = db.get_statistics()

# Export to JSON or CSV
db.export_to_json("output.json")
db.export_to_csv("output.csv")
```

## Database Schema

The `mountain_huts` table contains:

| Column             | Type      | Description             |
| ------------------ | --------- | ----------------------- |
| id                 | INTEGER   | Primary key             |
| name               | TEXT      | Name of the hut         |
| type               | INTEGER   | Type code (0-3)         |
| type_description   | TEXT      | Human-readable type     |
| status             | INTEGER   | Status code (0-3)       |
| status_description | TEXT      | Human-readable status   |
| latitude           | REAL      | GPS latitude            |
| longitude          | REAL      | GPS longitude           |
| altitude           | INTEGER   | Elevation in meters     |
| description        | TEXT      | Full description        |
| url                | TEXT      | Direct link to hut page |
| scraped_at         | TIMESTAMP | When data was collected |

## Types

- **0** - Unidentified object
- **1** - Bivouac/camping spot
- **2** - Shelter/hut
- **3** - Mountain hut/hotel

## Status

- **0** - New object
- **1** - Approved object
- **2** - Deleted object
- **3** - Secret object

## Notes

- The scraper includes delays between requests to be respectful to the server
- Some huts may not have complete information (coordinates, altitude, etc.)
- The website is in Czech, so descriptions will be in Czech language

## Legal & Ethical Considerations

- This scraper is designed for personal, educational, or research use
- Please respect the website's terms of service
- Consider the server load and scraping frequency
- The data belongs to boudy.info - give proper attribution if you use it

## Future Enhancements

Potential improvements:

- Add support for photos/images
- Extract more detailed amenity information
- Add support for incremental updates
- Implement better coordinate extraction
- Add map visualization of the huts
- Support for different languages
