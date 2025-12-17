# 🔍 Database Inspection - Findings & Solutions

**Date:** November 15, 2025  
**Inspection Size:** 50 random entries  
**Database Size:** 162 entries (down from 7,472)

---

## 🎯 Executive Summary

**Finding:** 100% of inspected entries have critical data missing (altitude, description, website, capacity)

**Root Cause:** The tyrol.com scraper has the code to extract this data BUT IT'S NOT BEING USED

**Impact:** Database quality dropped dramatically - only basic coordinates and names are being stored

---

## 📊 Key Statistics

### Data Completeness (Current Database)

| Field           | Status         | Count          | Issue                   |
| --------------- | -------------- | -------------- | ----------------------- |
| Name            | ✅ Perfect     | 162/162 (100%) | -                       |
| Coordinates     | ✅ Perfect     | 162/162 (100%) | -                       |
| Country         | ✅ Perfect     | 162/162 (100%) | -                       |
| Hut Type        | ✅ Perfect     | 162/162 (100%) | -                       |
| **Altitude**    | ❌ **MISSING** | 0/162 (0%)     | **Critical field**      |
| **Description** | ❌ **MISSING** | 0/162 (0%)     | **Important for users** |
| **Website**     | ❌ **MISSING** | 0/162 (0%)     | **Contact info**        |
| **Capacity**    | ❌ **MISSING** | 0/162 (0%)     | **Planning info**       |
| **Phone**       | ❌ **MISSING** | 0/162 (0%)     | **Contact info**        |
| **Email**       | ❌ **MISSING** | 0/162 (0%)     | **Contact info**        |

---

## 🔎 Root Cause Analysis

### Problem in `src/scrapers/scraper_tyrol_com.py`

The scraper has **THREE methods for parsing hut data:**

1. **`parse_marker_data()`** (CURRENTLY USED ✅)

   - Lines 194-242
   - Only extracts: name, coordinates, country, hut_type
   - Missing: altitude, description, capacity, contact info

2. **`parse_hut_item()`** (NOT USED ❌)

   - Lines 244-332
   - CAN extract: altitude, region, amenities
   - Has regex patterns for altitude: `r'\d+\s*m'`

3. **`fetch_hut_details()`** (NOT USED ❌)
   - Lines 334-389
   - CAN extract: email, phone, website, description
   - Already has all the parsing logic!

### Why It's Happening

The `scrape()` method (line 31) calls `parse_marker_data()` which only extracts basic info from the map JSON:

```python
# Line 78-80
hut = self.parse_marker_data(marker, name_to_url)
if hut:
    all_huts.append(hut)
```

It never calls `fetch_hut_details()` to get the additional data!

---

## ✅ The Fix

### Option 1: Quick Fix (Add detail fetching)

Modify the `scrape()` method to also fetch details for each hut:

```python
# In scrape() method, around line 78
for marker in markers_data:
    try:
        hut = self.parse_marker_data(marker, name_to_url)
        if hut and hut.get('url'):
            # NEW: Fetch additional details from hut page
            details = self.fetch_hut_details(hut['url'])
            hut.update(details)
            all_huts.append(hut)
    except Exception as e:
        self.logger.warning(f"Error parsing marker: {e}")
        continue
```

**Pros:** Simple, uses existing code  
**Cons:** Will be slower (162 extra HTTP requests)

### Option 2: Better Fix (Extract from marker data first)

Check if the marker JSON already contains altitude/description:

```python
def parse_marker_data(self, marker: Dict, name_to_url: Dict[str, str]) -> Dict:
    """Parse a single marker from the map data"""
    hut = {}

    # Extract name
    hut['name'] = marker.get('title', 'Unknown')

    # Extract coordinates
    latlng = marker.get('latlng', [])
    if len(latlng) == 2:
        hut['latitude'] = float(latlng[0])
        hut['longitude'] = float(latlng[1])

    # NEW: Extract altitude if available
    if 'altitude' in marker:
        hut['altitude'] = marker.get('altitude')
    elif 'elevation' in marker:
        hut['altitude'] = marker.get('elevation')
    elif 'height' in marker:
        hut['altitude'] = marker.get('height')

    # NEW: Extract description if available
    if 'description' in marker:
        hut['description'] = marker.get('description')
    elif 'text' in marker:
        hut['description'] = marker.get('text')

    # ... rest of existing code ...

    return self.normalize_hut_data(hut)
```

**Pros:** Fast, no extra requests  
**Cons:** Depends on what's in the marker JSON

### Option 3: Best Fix (Hybrid approach)

1. Extract what's available from marker JSON
2. For critical missing fields (altitude), fetch details page
3. Use rate limiting to be respectful

```python
# In scrape() method
for marker in markers_data:
    try:
        hut = self.parse_marker_data(marker, name_to_url)
        if not hut:
            continue

        # If critical fields are missing, fetch details
        needs_details = (
            not hut.get('altitude') or
            not hut.get('description')
        )

        if needs_details and hut.get('url'):
            self.logger.debug(f"Fetching details for {hut['name']}")
            details = self.fetch_hut_details(hut['url'])
            hut.update(details)

        all_huts.append(hut)

    except Exception as e:
        self.logger.warning(f"Error parsing marker: {e}")
        continue
```

---

## 🚀 Immediate Action Plan

### Step 1: Investigate Marker JSON Structure

First, let's see what data is actually in the markers:

```python
# Add this temporarily to parse_marker_data()
self.logger.debug(f"Marker keys: {marker.keys()}")
self.logger.debug(f"Marker data: {marker}")
```

Run the scraper once and check the logs to see what fields are available.

### Step 2: Implement the Fix

Based on what's in the marker JSON:

- If altitude is there → extract it
- If not → implement Option 1 or 3 above

### Step 3: Re-run the Scraper

```bash
python src/scrapers/scraper_tyrol_com.py
```

### Step 4: Verify the Fix

```bash
python tools/inspect_random_entries.py
```

Should show altitude and description populated.

---

## 🔧 Additional Improvements

### 1. Data Validation in Scraper

Add validation before saving:

```python
def validate_hut_data(self, hut: Dict) -> bool:
    """Validate hut has minimum required data"""
    required = ['name', 'latitude', 'longitude']
    for field in required:
        if not hut.get(field):
            return False

    # Warn if critical fields missing
    if not hut.get('altitude'):
        self.logger.warning(f"Hut {hut['name']} missing altitude")

    return True
```

### 2. Progress Logging

Add better logging to see what's being extracted:

```python
self.logger.info(
    f"Scraped {hut['name']}: "
    f"alt={hut.get('altitude', 'N/A')}, "
    f"desc={'✓' if hut.get('description') else '✗'}, "
    f"web={'✓' if hut.get('website') else '✗'}"
)
```

### 3. Sample Entry Inspection

After scraping, log a sample entry to verify:

```python
if len(all_huts) > 0:
    sample = all_huts[0]
    self.logger.info("Sample hut data:")
    for key, value in sample.items():
        self.logger.info(f"  {key}: {value}")
```

---

## 📋 Other Database Issues

### Issue 1: Missing Previous Data

- **Before:** 7,472 entries from 4 sources
- **Now:** 162 entries from 1 source
- **Missing:** refuges.info (5,250), boudy.info (889), mountainhuts.info (673), mountain-huts.net (660)

**Action:** Re-run all scrapers

```bash
python scripts/run_all_scrapers.py
```

### Issue 2: ID Gap

- Current IDs: 991-1152
- Missing IDs: 1-990

**Likely cause:** Database was cleared/reset but auto-increment wasn't reset

**Action:** Not critical, but could reset if desired:

```sql
-- Reset auto-increment (after backing up!)
DELETE FROM mountain_huts WHERE id >= 991;
DELETE FROM sqlite_sequence WHERE name='mountain_huts';
-- Then re-run scrapers
```

---

## 🎯 Success Metrics

After fixes, expect:

| Metric               | Current | Target | Status  |
| -------------------- | ------- | ------ | ------- |
| Altitude coverage    | 0%      | >95%   | ❌ → ✅ |
| Description coverage | 0%      | >80%   | ❌ → ✅ |
| Website coverage     | 0%      | >50%   | ❌ → ✅ |
| Total entries        | 162     | >7,000 | ❌ → ✅ |
| Data sources         | 1       | 4+     | ❌ → ✅ |

---

## 📝 Test After Fix

```bash
# 1. Fix the scraper (implement Option 1, 2, or 3)
# Edit: src/scrapers/scraper_tyrol_com.py

# 2. Clear test entries
python -c "import sqlite3; conn = sqlite3.connect('data/mountain_huts.db'); conn.execute('DELETE FROM mountain_huts WHERE source=\"tyrol.com\"'); conn.commit()"

# 3. Re-run scraper
python src/scrapers/scraper_tyrol_com.py

# 4. Check one entry manually
python -c "import sqlite3; conn = sqlite3.connect('data/mountain_huts.db'); conn.row_factory = sqlite3.Row; cursor = conn.cursor(); cursor.execute('SELECT * FROM mountain_huts LIMIT 1'); row = dict(cursor.fetchone()); import json; print(json.dumps(row, indent=2))"

# 5. Run full inspection
python tools/inspect_random_entries.py
```

---

## 💡 Key Takeaways

1. ✅ **Database structure is good** - Schema is well-designed
2. ✅ **Coordinates are perfect** - GPS data is accurate
3. ✅ **Scraper has the code** - Just needs to be activated
4. ❌ **Critical method not called** - `fetch_hut_details()` exists but unused
5. ❌ **Other scrapers not run** - Need to restore 7,000+ entries

---

## 🔗 Related Files

- **Scraper to fix:** `src/scrapers/scraper_tyrol_com.py`
- **Inspection tool:** `tools/inspect_random_entries.py`
- **Database:** `data/mountain_huts.db`
- **Run all scrapers:** `scripts/run_all_scrapers.py`

---

_Report generated: November 15, 2025_
