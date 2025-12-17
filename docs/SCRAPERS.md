# Scraper Documentation

This document provides detailed information about each scraper in the Lost in the Alps project.

## Overview

The project uses a modular scraper system where each data source has its own dedicated scraper class that inherits from `BaseScraper`. All scrapers follow a common pattern and save data to a centralized SQLite database.

## Architecture

### Base Scraper Class

**File**: `scrapers/base_scraper.py`

All scrapers inherit from `BaseScraper` which provides:

- Database connection management
- HTTP session with proper User-Agent headers
- Logging infrastructure
- Common execution workflow
- Data normalization methods

**Required Methods**:

- `source_name`: Property returning the source website name
- `source_url`: Property returning the base URL
- `source_description`: Property describing the data source
- `scrape()`: Main scraping logic that returns list of hut dictionaries

## Active Scrapers

### 1. Boudy.info Scraper

**File**: `scrapers/scraper_boudy_info.py`  
**Class**: `BoudyInfoScraper`  
**Coverage**: Alps region (France, Italy, Switzerland, Austria, Germany, Slovenia)  
**Total Huts**: 889 (10.9% of database)

#### Method

- **Type**: AJAX API Grid-based Search
- **Technique**: Divides map area into grid cells, makes API requests for each cell
- **Grid Size**: 0.5° × 0.5° latitude/longitude cells
- **Bounding Box**: lat 42-49°N, lon 4-18°E

#### Data Extracted

- Basic information: name, coordinates, altitude
- Hut type (coded as integer)
- Source URL for each hut

#### Known Limitations

- Basic data only (no contact info, opening hours)
- Grid-based approach may have coverage gaps
- Type codes need mapping to readable names

#### Example Output

```python
{
    'source_id': '12345',
    'name': 'Rifugio Example',
    'latitude': 46.5,
    'longitude': 11.5,
    'altitude': 2450,
    'type': 'Mountain hut',
    'country': 'Italy',
    'url': 'https://www.boudy.info/...'
}
```

---

### 2. Mountain-huts.net Scraper

**File**: `scrapers/scraper_mountain_huts_net.py`  
**Class**: `MountainHutsNetScraper`  
**Coverage**: Balkans (Slovenia, Croatia, Bulgaria, Greece, Bosnia, Serbia, North Macedonia, Montenegro)  
**Total Huts**: 660 (8.1% of database)

#### Method

- **Type**: JavaScript Array Parsing
- **Technique**: Parses embedded JavaScript marker array from webpage
- **URL**: `https://www.mountain-huts.net/`

#### Data Extracted

- Name, coordinates, altitude
- Country code (2-letter ISO)
- Website URL

#### Known Limitations

- Data embedded in JavaScript, fragile to website changes
- Limited additional information
- Country codes need conversion to full names

#### Example Output

```python
{
    'source_id': 'SI-123',
    'name': 'Planinski dom',
    'latitude': 46.3,
    'longitude': 14.5,
    'altitude': 1800,
    'country': 'Slovenia',
    'url': 'https://www.mountain-huts.net/...'
}
```

---

### 3. Mountainhuts.info Scraper

**File**: `scrapers/scraper_mountainhuts_info.py`  
**Class**: `MountainhustsInfoScraper`  
**Coverage**: Europe-wide (19 countries)  
**Total Huts**: 1,343 (16.4% of database)

#### Method

- **Type**: JavaScript Array Parsing
- **Technique**: Parses `locations` array from embedded JavaScript
- **URL**: `https://www.mountainhuts.info/`
- **Fields per Hut**: 50+ fields

#### Data Extracted

- **Identity**: name, type, status
- **Location**: coordinates, altitude, country, region
- **Contact**: phone (663 huts), email (620 huts), website (1,272 huts)
- **Management**: owner (471 huts), manager (539 huts)
- **Scheduling**: opening hours/months (643 huts)
- **Capacity**: beds, places
- **Metadata**: last update date, posted by, posted date

#### Known Limitations

- JavaScript parsing fragile to format changes
- Not all huts have complete data
- Date formats vary

#### Example Output

```python
{
    'source_id': '123',
    'name': 'Berghütte Example',
    'latitude': 47.2,
    'longitude': 12.8,
    'altitude': 2100,
    'country': 'Austria',
    'type': 'Mountain hut',
    'status': 'Open',
    'phone': '+43 123 456789',
    'email': 'info@example.at',
    'website': 'https://example.at',
    'owner': 'Alpine Club Austria',
    'manager': 'John Doe',
    'opening_hours': 'June-September',
    'capacity': 40,
    'url': 'https://www.mountainhuts.info/...'
}
```

---

### 4. Refuges.info Scraper

**File**: `scrapers/scraper_refuges_info_pages.py`  
**Class**: `RefugesInfoPageScraper`  
**Coverage**: French Alps, Swiss Alps, Italian Alps  
**Total Huts**: 5,274 (64.6% of database) 🎉

#### Method

- **Type**: Comprehensive API + Page Scraping
- **Technique**:
  1. Uses API to get ALL refuge IDs by type (cabane, refuge, bivouac)
  2. Scrapes individual refuge pages for detailed data
  3. Supports time-limited scraping for large datasets
- **API**: `https://www.refuges.info/api/bbox` and `https://www.refuges.info/api/point`
- **Types Scraped**:
  - Cabanes non gardées (unmanned huts): ~3,700
  - Refuges gardés (staffed refuges): ~400
  - Bivouacs (bivouac shelters): ~1,100+
- **Scraping Options**:
  - `--all`: Scrape all 8,000+ refuges (3-4 hours)
  - `--sample`: Scrape 200 random refuges
  - Default: 100 random refuges
  - Time-limited: Use `run_refuges_timed.py` for controlled duration

#### Data Extracted

- **Basic**: name, type, coordinates, altitude
- **Contact**: phone, website, email
- **Details**: description, remarks, capacity
- **Access**: access information, best time to visit
- **Facilities**: water availability, shelter type
- **French-to-English**: Automatic translation of common terms

#### Features

- **Comprehensive coverage**: Scrapes all 8,000+ available refuges
- **Time-limited mode**: Safe scraping with automatic stopping
- **Translation**: French terms automatically translated to English
- **Rate limiting**: Polite 1-second delay between requests
- **Progress tracking**: Regular database commits (every 50 huts)
- **Graceful interruption**: Can resume scraping later

#### Notes

- Full scraping takes 3-4 hours for all 8,000+ refuges
- Use `run_refuges_timed.py` for controlled duration (e.g., 90 minutes)
- Progress is saved regularly, safe to interrupt
- Excludes caves (grottes) and water points (not mountain huts)

#### Example Output

```python
{
    'source_id': '10030',
    'name': 'Rifugio Enrico Rossi',
    'latitude': 45.95,
    'longitude': 7.82,
    'altitude': 2820,
    'type': 'Staffed refuge',
    'country': 'Italy',
    'phone': '+39 123 456789',
    'website': 'https://example.com',
    'description': 'Beautiful mountain refuge...',
    'capacity': 45,
    'water_source': 'Spring nearby',
    'access': 'On foot from valley',
    'opening_hours': 'June to September',
    'url': 'https://www.refuges.info/...'
}
```

---

## Adding a New Scraper

### 1. Create Scraper File

Copy the template:

```bash
cp scrapers/scraper_template.py scrapers/scraper_yoursite.py
```

### 2. Implement Required Methods

```python
from scrapers.base_scraper import BaseScraper

class YourSiteScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "yoursite.com"

    @property
    def source_url(self) -> str:
        return "https://yoursite.com"

    @property
    def source_description(self) -> str:
        return "Description of the data source"

    def scrape(self) -> List[Dict]:
        # Your scraping logic here
        huts = []
        # ... scrape data ...
        return huts
```

### 3. Test the Scraper

```bash
python scrapers/scraper_yoursite.py
```

### 4. Auto-Discovery

The scraper will be automatically discovered by `run_all_scrapers.py` if:

- File name starts with `scraper_`
- Class name ends with `Scraper`
- Inherits from `BaseScraper`

## Data Format

All scrapers should return a list of dictionaries with these fields:

### Required Fields

- `source_id`: Unique ID from the source website (string)
- `name`: Hut name (string)
- `latitude`: Latitude in decimal degrees (float)
- `longitude`: Longitude in decimal degrees (float)

### Optional Fields

- `altitude`: Altitude in meters (int)
- `type`: Hut type - standardized values: 'Mountain hut', 'Bivouac', 'Unmanned cabin', 'Shelter', 'Unknown' (string)
- `country`: Country name (string)
- `region`: Region/province (string)
- `phone`: Phone number (string)
- `email`: Email address (string)
- `website`: Website URL (string)
- `url`: Source page URL (string)
- `description`: Description text (string)
- `owner`: Owner organization (string)
- `manager`: Manager name (string)
- `opening_hours`: Opening hours/dates (string)
- `capacity`: Number of beds/places (int)
- `water_source`: Water availability info (string)
- `access`: Access information (string)
- `amenities`: Available amenities (string)

## Best Practices

### 1. Respectful Scraping

- Add delays between requests (`time.sleep()`)
- Use proper User-Agent headers (handled by `BaseScraper`)
- Respect robots.txt
- Don't overload servers

### 2. Error Handling

```python
try:
    response = self.session.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    self.logger.error(f"Error fetching {url}: {e}")
    return []
```

### 3. Data Validation

- Validate coordinates are within expected ranges
- Check for required fields before saving
- Normalize country names
- Standardize hut types

### 4. Logging

Use the logger provided by `BaseScraper`:

```python
self.logger.info("Starting scrape...")
self.logger.warning("Missing data for hut X")
self.logger.error("Failed to parse response", exc_info=True)
```

### 5. Testing

- Test with small datasets first
- Verify data in database after scraping
- Check for duplicates
- Validate coordinates on map

## Troubleshooting

### No Huts Found

1. Check if website structure changed
2. Verify API endpoints still work
3. Check for JavaScript changes
4. Look for rate limiting or blocking

### Duplicate Entries

- Ensure `source_id` is unique for each source
- Check UNIQUE constraint in database
- Verify scraper isn't running multiple times

### Missing Data

- Check if fields are optional on source website
- Verify parsing logic for optional fields
- Add null/empty checks

### Encoding Issues

- Use UTF-8 encoding for all text
- Handle special characters properly
- Test with non-ASCII names

## Maintenance

### Regular Checks

- [ ] Verify scrapers still work monthly
- [ ] Update for website changes
- [ ] Check data quality
- [ ] Remove duplicate entries
- [ ] Update documentation

### Performance Monitoring

- Track scraping duration
- Monitor success/failure rates
- Check database size growth
- Review error logs

---

For more information, see:

- `README.md` - Project overview
- `docs/DATABASE_SUMMARY.md` - Database schema details
- `docs/DATA_ENRICHMENT_SUMMARY.md` - Data enhancement info
