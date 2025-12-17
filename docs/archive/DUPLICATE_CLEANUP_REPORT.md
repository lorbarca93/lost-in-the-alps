# Duplicate Cleanup Report

**Date:** November 5, 2025  
**Issue:** Duplicate entries from mountainhuts.info in database

## Problem Identified

670 duplicate entries were found in the database from the mountainhuts.info source. Each hut was appearing twice, inflating the total count and cluttering the map.

## Root Cause

The scraper was run multiple times and the database didn't have a unique constraint on `(source, source_id)`, allowing duplicate entries to be inserted despite the deduplication logic in the code.

## Actions Taken

### 1. Detection
- Created `tools/fix_duplicates.py` to detect and analyze duplicates
- Found 670 groups of duplicate entries (670 extra entries)
- All duplicates were from mountainhuts.info

### 2. Cleanup
- Removed 670 duplicate entries from the database
- Kept the first occurrence of each hut (lowest ID)
- **Before:** 1,343 entries from mountainhuts.info
- **After:** 673 entries from mountainhuts.info
- **Total database:** 7,472 huts (down from 8,142)

### 3. Prevention
- Added unique constraint: `CREATE UNIQUE INDEX idx_source_source_id_unique ON mountain_huts(source, source_id)`
- This prevents future duplicate entries at the database level
- Any attempt to insert a duplicate will now fail with an integrity error

### 4. Data Regeneration
- Regenerated `huts_data.json` with clean data
- Regenerated `website/api/stats.json` with updated statistics
- Regenerated `website/api/huts.json` with updated hut list
- Regenerated `mountain_huts_map.html` with clean markers

## Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Huts | 8,142 | 7,472 | -670 |
| mountainhuts.info entries | 1,343 | 673 | -670 |
| Map Markers | 8,142 | 7,472 | -670 |

## Verification

The website now shows:
- **7,472 huts** (accurate count)
- **41 countries**
- **4 data sources**
- No duplicate markers on the map

## Future Prevention

The unique constraint ensures that:
1. Each `(source, source_id)` combination can only appear once
2. If a scraper tries to insert a duplicate, it will fail
3. The `save_hut` method will properly UPDATE existing entries instead of creating duplicates

## Files Modified

- `data/mountain_huts.db` - Removed duplicates, added constraint
- `huts_data.json` - Regenerated with clean data
- `website/api/stats.json` - Updated statistics
- `website/api/huts.json` - Updated hut list
- `mountain_huts_map.html` - Regenerated map

## Tools Created

- `tools/fix_duplicates.py` - Detection and removal tool
- `tools/generate_website_data.py` - Data generation tool
- `tools/add_unique_constraint.py` - Constraint addition tool

## Recommendation

Run the scrapers again to ensure fresh data, knowing that duplicates are now impossible due to the database constraint.

