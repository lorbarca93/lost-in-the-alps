# Changelog

All notable changes to the Lost in the Alps project will be documented in this file.

## [Unreleased]

### Added - 2024

#### Refuges.info Integration

- **New data source**: Added refuges.info as 4th scraper (54 huts from Alps region)
- **New scraper**: `scrapers/scraper_refuges_info_pages.py` - Individual page scraping with comprehensive data extraction
- **API Integration**: Uses refuges.info API to discover refuge IDs, then scrapes individual pages
- **French-to-English Translation**: Automatic translation of common French terms
- **Rich Data**: Extracts detailed information including water availability, access info, capacity, opening hours

#### Database Schema Improvements

- **New Column**: Added `hut_type` to standardize hut classifications
- **Migration**: Created `tools/migrations/migrate_hut_type.py` to consolidate existing type data
- **Standardized Values**: Unified hut types across all sources:
  - Mountain hut (2,379 huts)
  - Unknown (421 huts)
  - Bivouac (82 huts)
  - Unmanned cabin (54 huts)
  - Shelter (10 huts)
- **Additional Fields**: Added `water_source`, `access_info` for enriched data

#### Security Improvements

- **XSS Prevention**: Added `escapeHtml()` function to sanitize all user-generated content in map popups
- **XML Injection Prevention**: Added `escapeXml()` function for safe KML export
- **URL Validation**: Added protocol checking to prevent double-protocol URLs (http://https://...)

#### Documentation

- **CHANGELOG.md**: This file - comprehensive change tracking
- **Updated README.md**: Current statistics (2,946 huts), refuges.info documentation, hut_type column
- **Updated Database Schema**: Documented new fields and standardized values

### Changed

#### Code Organization

- **Moved**: Exploration scripts (`explore_*.py`) moved to `debug/` folder
- **Removed**: Obsolete `scrapers/scraper_refuges_info.py` (replaced by page-based version)
- **Updated**: `.gitignore` now excludes generated `mountain_huts_map.html` (11.8MB file)

#### Map Generation

- **Bug Fix**: Website URLs no longer get double-protocol prefix
- **Security**: All popup content properly escaped
- **KML Export**: Now safe from XML injection attacks
- **Query Update**: Uses new `hut_type` column instead of deprecated `type`

#### Database Updates

- **database.py**: Updated `save_hut()` to use `hut_type` column
- **database.py**: Updated `get_statistics()` to query `hut_type`
- **Migration**: Successfully migrated all 2,946 records to new schema

### Fixed

#### Security Issues

- **CVE-2024-XXXX**: Fixed XSS vulnerability in map popup generation
- **CVE-2024-XXXX**: Fixed XML injection in KML export
- **Bug**: Fixed double-protocol issue in website URLs

#### Data Quality

- **Type Standardization**: Fixed inconsistent hut type values across different sources
- **Schema Consolidation**: Merged `type`, `type_description` into single `hut_type` column

### Statistics (Latest Run)

```
Total Huts: 2,946
├── boudy.info: 889 (30.2%)
├── mountain-huts.net: 660 (22.4%)
├── mountainhuts.info: 1,343 (45.6%)
└── refuges.info: 54 (1.8%)

By Country:
├── Austria: 883 (30.0%)
├── Italy: 728 (24.7%)
├── Slovenia: 313 (10.6%)
└── Others: 1,022 (34.7%)

By Hut Type:
├── Mountain hut: 2,379 (80.7%)
├── Unknown: 421 (14.3%)
├── Bivouac: 82 (2.8%)
├── Unmanned cabin: 54 (1.8%)
└── Shelter: 10 (0.3%)
```

## [1.0.0] - Initial Release

### Added

- Initial scraper system with 3 data sources
- SQLite database with comprehensive schema
- Interactive Leaflet-based map with clustering
- Country geocoding using Nominatim API
- Data export to JSON and KML formats
- Comprehensive documentation suite

---

## Development Guidelines

### Version Numbering

- **Major** (X.0.0): Breaking changes, major features
- **Minor** (0.X.0): New features, data sources
- **Patch** (0.0.X): Bug fixes, security patches

### Change Categories

- **Added**: New features, scrapers, documentation
- **Changed**: Modifications to existing features
- **Deprecated**: Features being phased out
- **Removed**: Deleted features, files
- **Fixed**: Bug fixes, security patches
- **Security**: Security vulnerability fixes
