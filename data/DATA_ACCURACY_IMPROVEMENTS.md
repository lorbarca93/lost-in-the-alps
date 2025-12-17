# Database Data Accuracy Improvement Recommendations
**Date:** November 15, 2025  
**After:** Activating all 4 data sources and re-inspection

---

## 🎯 Executive Summary

**Status:** ✅ Major improvement achieved!
- **Database size:** 162 → 6,757 entries (+4,078% increase)
- **Active sources:** 1 → 4 sources activated
- **Data quality:** Still room for improvement in specific areas

---

## 📊 Current Database State

### Data Sources (6,757 total entries)

| Source | Entries | Percentage | Status |
|--------|---------|------------|--------|
| **refuges.info** | 5,264 | 77.9% | ✅ Active |
| **mountainhuts.info** | 671 | 9.9% | ✅ Active |
| **mountain-huts.net** | 660 | 9.8% | ⚠️ Active (failed earlier) |
| **tyrol.com** | 162 | 2.4% | ✅ Active |
| **boudy.info** | 0 | 0% | ❌ Failed to run |

---

## 🔍 Inspection Results (50 random entries)

### Overall Quality Metrics

| Metric | Result | Status |
|--------|--------|--------|
| **Entries with issues** | 100% (50/50) | ⚠️ Needs improvement |
| **Average issues per entry** | 1.28 | ✅ Good (down from 2.0) |
| **Critical data missing** | 82.8% of issues | 🔴 Priority 1 |
| **Coordinate problems** | 6.2% of issues | 🟡 Priority 2 |
| **URL issues** | 6.2% of issues | 🟡 Priority 3 |
| **Formatting issues** | 4.7% of issues | 🟢 Low priority |

### Issue Breakdown

1. **Critical Data Missing** (53 issues, 82.8%)
   - Missing country: Mostly mountainhuts.info entries
   - Missing altitude: tyrol.com entries
   - Missing description: Multiple sources

2. **Coordinate Problems** (4 issues, 6.2%)
   - Some entries outside Alps range (may be valid - e.g., Pyrenees, Carpathians)
   - False positives due to strict Alps-only validation

3. **URL Issues** (4 issues, 6.2%)
   - Missing `http://` or `https://` prefix (e.g., `www.example.com`)
   - Should be normalized to `https://www.example.com`

4. **Formatting Issues** (3 issues, 4.7%)
   - Phone numbers with special characters
   - Unicode encoding in names (Czech, Slovak, etc.)

---

## 🎯 Proposed Improvements for Data Accuracy

### Priority 1: Critical Data Completeness

#### 1.1 Fix Missing Country Data (mountainhuts.info)

**Problem:** Many entries from mountainhuts.info are missing country information.

**Solution:**
```python
# In scraper_mountainhuts_info.py
# Extract country from existing data fields:
# - Look for country codes in URLs/paths
# - Use reverse geocoding API for entries with coordinates but no country
# - Cross-reference with country name lists
```

**Implementation Steps:**
1. Add country extraction from URL patterns (e.g., `.sk` → Slovakia, `.cz` → Czech Republic)
2. Use OpenStreetMap Nominatim API for reverse geocoding
3. Create country mapping table for common patterns

**Expected Impact:** +500 entries with country data

---

#### 1.2 Fix Missing Altitude (tyrol.com)

**Problem:** tyrol.com scraper not extracting altitude from detail pages.

**Solution:** Already implemented in recent fix, but needs validation:
```python
# In scraper_tyrol_com.py - fetch_hut_details()
# Already has altitude extraction, but may need refinement
```

**Next Steps:**
1. Test if altitude extraction is working (may need to run scraper again)
2. If not working, use elevation API as fallback:
   - Open-Elevation API (free)
   - Google Elevation API (requires API key)

**Expected Impact:** +162 entries with altitude

---

#### 1.3 Add Missing Descriptions

**Problem:** Many entries lack descriptions (critical for user experience).

**Solution Options:**
1. **AI Enrichment** (Already available):
   ```bash
   python tools/enrich_huts_with_ai.py
   ```
   - Use OpenAI/Claude to generate descriptions from available data
   - Cost-effective for bulk enrichment

2. **Scraper Enhancement:**
   - Improve detail page parsing
   - Extract from multiple HTML elements
   - Combine multiple sources for same hut

3. **External API:**
   - Use Wikipedia API for well-known huts
   - Use OpenStreetMap descriptions

**Expected Impact:** +2,000 entries with descriptions

---

### Priority 2: Data Validation & Normalization

#### 2.1 URL Normalization

**Problem:** Some URLs missing `http://` or `https://` prefix.

**Solution:** Add URL normalization in database layer:
```python
# In src/database.py - normalize_hut_data()
def normalize_url(url: str) -> str:
    """Normalize URL to include protocol"""
    if not url:
        return None
    
    url = url.strip()
    
    # Add https:// if missing protocol
    if not url.startswith(('http://', 'https://')):
        # Check if it looks like a domain
        if '.' in url and not url.startswith('www.'):
            url = f'https://{url}'
        elif url.startswith('www.'):
            url = f'https://{url}'
    
    return url
```

**Expected Impact:** All URLs properly formatted

---

#### 2.2 Phone Number Normalization

**Problem:** Phone numbers have inconsistent formats.

**Solution:** Create phone number parser:
```python
def normalize_phone(phone: str) -> str:
    """Normalize phone number format"""
    if not phone:
        return None
    
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.\/\|]', '', phone)
    
    # Keep only digits and +
    cleaned = re.sub(r'[^\d+]', '', cleaned)
    
    return cleaned
```

**Expected Impact:** Consistent phone number format

---

#### 2.3 Coordinate Validation

**Problem:** Current validation is too strict (Alps-only), flags valid entries.

**Solution:** Expand validation ranges:
```python
# In tools/inspect_random_entries.py - check_coordinates()
# Current: Alps only (lat 43-48, lon 5-17)
# Expand to: All European mountains
# - Pyrenees: lat 42-44, lon -2 to 3
# - Carpathians: lat 45-50, lon 20-27
# - Balkans: lat 40-46, lon 14-23
# - Scandinavia: lat 60-70, lon 5-30

def check_coordinates(self, entry: Dict) -> List[str]:
    """Check if coordinates are valid and reasonable"""
    issues = []
    lat = entry.get('latitude')
    lon = entry.get('longitude')
    
    if lat is None or lon is None:
        issues.append("Missing coordinates")
    else:
        # European mountain ranges
        european_mountains = [
            (43, 48, 5, 17),   # Alps
            (42, 44, -2, 3),   # Pyrenees
            (45, 50, 20, 27),  # Carpathians
            (40, 46, 14, 23),  # Balkans
            (60, 70, 5, 30),   # Scandinavia
        ]
        
        in_valid_range = any(
            min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
            for min_lat, max_lat, min_lon, max_lon in european_mountains
        )
        
        if not in_valid_range:
            issues.append(f"Coordinates ({lat}, {lon}) outside known mountain ranges")
        
        # Check for dummy values
        if lat == 0.0 and lon == 0.0:
            issues.append("Coordinates are (0,0) - likely placeholder")
    
    return issues
```

**Expected Impact:** Fewer false positives in coordinate validation

---

### Priority 3: Data Accuracy Improvements

#### 3.1 Duplicate Detection & Merging

**Problem:** Potential duplicates across sources (e.g., same hut from different sites).

**Solution:** Implement duplicate detection algorithm:
```python
# New tool: tools/detect_duplicates.py

def find_duplicates(threshold=0.8):
    """
    Find potential duplicates using:
    1. Name similarity (Levenshtein distance)
    2. Coordinate proximity (within 100m)
    3. Cross-reference source IDs
    """
    # Fuzzy name matching
    # Coordinate clustering
    # Manual review queue for similar entries
```

**Expected Impact:** Cleaner database, merged best data from multiple sources

---

#### 3.2 Data Cross-Validation

**Problem:** Single source of truth - no validation against other sources.

**Solution:** Cross-validate data across sources:
```python
def cross_validate_hut(hut_id):
    """
    For a given hut, check if it appears in multiple sources:
    1. Compare altitude (should be similar, ±50m tolerance)
    2. Compare coordinates (should be close, ±100m tolerance)
    3. Merge best data from each source
    """
    pass
```

**Expected Impact:** Higher accuracy, more complete entries

---

#### 3.3 Altitude Validation

**Problem:** Some altitudes may be incorrect (0, negative, too high).

**Solution:** Add altitude validation:
```python
def validate_altitude(altitude: int, lat: float, lon: float) -> bool:
    """Validate altitude against elevation API"""
    if altitude is None:
        return False
    
    # Reasonable range for mountain huts
    if altitude < 100 or altitude > 5000:
        return False
    
    # Optional: Cross-check with elevation API
    # (API call only for suspicious values)
    if altitude < 500 or altitude > 4000:
        api_elevation = get_elevation_from_api(lat, lon)
        if abs(altitude - api_elevation) > 200:
            return False  # Flag for review
    
    return True
```

**Expected Impact:** Cleaner altitude data

---

### Priority 4: Scraper Improvements

#### 4.1 Fix boudy.info Scraper

**Problem:** boudy.info scraper failed to run.

**Action Required:**
1. Debug import errors
2. Test individual scraper
3. Fix any breaking changes

**Expected Impact:** +889 entries restored

---

#### 4.2 Improve Error Handling

**Problem:** Some scrapers silently fail or skip entries.

**Solution:**
```python
# In base_scraper_v2.py
# Add comprehensive error tracking:
# - Failed entries logged with reasons
# - Retry mechanism for transient failures
# - Summary report of what failed and why
```

**Expected Impact:** Better visibility into data quality issues

---

#### 4.3 Add Progress Checkpoints

**Problem:** Long-running scrapers lose progress on failure.

**Solution:** Already implemented in base_scraper_v2.py, but verify:
- Checkpoint after every N entries
- Resume capability after interruption
- Progress reporting

---

## 📋 Implementation Priority List

### Immediate (Week 1)

1. ✅ **Fix tyrol.com scraper** - DONE
2. ✅ **Run all scrapers** - DONE
3. **Fix boudy.info scraper** - Priority 1
4. **Add URL normalization** - Quick win
5. **Fix missing country data** - High impact

### Short-term (Week 2-3)

6. **Add altitude extraction/validation**
7. **Expand coordinate validation ranges**
8. **Normalize phone numbers**
9. **Run AI enrichment for descriptions**

### Medium-term (Month 1)

10. **Implement duplicate detection**
11. **Cross-validate data across sources**
12. **Add comprehensive error tracking**
13. **Create data quality dashboard**

---

## 🔧 Quick Wins (Can Implement Today)

### 1. URL Normalization Script
```python
# tools/normalize_urls.py
# Quick script to fix all URLs in database
# Run once, fixes all entries
```

### 2. Country Detection from Coordinates
```python
# tools/add_missing_countries.py
# Use reverse geocoding for entries with coordinates but no country
# Free API: OpenStreetMap Nominatim
```

### 3. Phone Number Cleanup
```python
# tools/normalize_phones.py
# Clean up all phone numbers in database
# Standardize format
```

---

## 📊 Success Metrics

### Target Metrics (After Improvements)

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Total entries** | 6,757 | 7,500+ | 🟡 In progress |
| **Country completeness** | ~90% | >98% | 🔴 Needs work |
| **Altitude completeness** | ~95% | >98% | 🟡 Close |
| **Description completeness** | ~20% | >60% | 🔴 Needs work |
| **URL validity** | ~95% | >99% | 🟢 Good |
| **Phone completeness** | ~5% | >30% | 🔴 Low |
| **Email completeness** | ~10% | >25% | 🔴 Low |

---

## 🚀 Next Steps

1. **Fix boudy.info scraper** - Restore 889 entries
2. **Run URL normalization** - Quick win
3. **Add missing countries** - High impact
4. **Run AI enrichment** - Add descriptions
5. **Re-inspect database** - Verify improvements

---

## 📝 Notes

- **Coordinate validation:** Current strict Alps-only check may flag valid entries outside Alps. Consider expanding to all European mountain ranges.
- **URL formatting:** Many entries have `www.example.com` instead of `https://www.example.com`. Easy fix with normalization script.
- **Data sources:** All 4 main sources now active (except boudy.info). Need to fix boudy.info to restore full dataset.
- **AI enrichment:** Tool already exists (`enrich_huts_with_ai.py`) but may need API key configuration.

---

*Report generated: November 15, 2025*  
*Database size: 6,757 entries (up from 162)*  
*Data sources: 4 active (3 working, 1 needs fixing)*

