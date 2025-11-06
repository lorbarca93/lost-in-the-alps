# Database Improvement Tool - User Guide
**Script**: `tools/improve_database.py`  
**Date**: November 6, 2025

---

## 🎯 Purpose

Comprehensive database maintenance and optimization tool that:
- ✅ Analyzes database health
- ✅ Detects data quality issues
- ✅ Fixes common problems
- ✅ Optimizes performance
- ✅ Generates detailed reports

---

## 🚀 Quick Start

### 1. Analyze Database (Safe - No Changes)
```bash
python tools/improve_database.py --analyze
```

**What it does**:
- Analyzes database health
- Detects issues (duplicates, invalid data, etc.)
- Generates report
- **Makes NO changes** - completely safe

**Output**:
```
================================================================================
  DATABASE ANALYSIS
================================================================================
...
   Total issues found: 5
   1. 45 huts missing coordinates
   2. 120 potential name duplicates
   3. 12 huts with invalid coordinates
...
```

---

### 2. Optimize Database (Safe - Performance Only)
```bash
python tools/improve_database.py --optimize
```

**What it does**:
- Creates backup automatically
- Optimizes indexes
- Runs VACUUM (reclaims space)
- Updates statistics (improves queries)
- **Does NOT modify data** - only structure

---

### 3. Fix Data Issues (Modifies Data)
```bash
python tools/improve_database.py --fix
```

**What it does**:
- Creates backup automatically
- Fixes invalid coordinates
- Normalizes empty values
- Trims whitespace
- Updates timestamps

---

### 4. Full Optimization (Everything)
```bash
python tools/improve_database.py --all
```

**What it does**:
- All of the above
- Creates backup
- Fixes data issues
- Optimizes indexes
- VACUUM and ANALYZE
- Generates report

---

## 📋 Options

| Option | Description | Safe? | Changes Data? |
|--------|-------------|-------|---------------|
| `--analyze` | Analyze only | ✅ Yes | ❌ No |
| `--optimize` | Optimize structure | ✅ Yes | ❌ No |
| `--fix` | Fix data issues | ⚠️ Backup | ✅ Yes |
| `--all` | Full optimization | ⚠️ Backup | ✅ Yes |
| `--no-backup` | Skip backup | ⚠️ **Not recommended** | - |
| `--db PATH` | Custom database path | - | - |

---

## 📊 What Gets Analyzed

### 1. Database Statistics
- File size
- Total huts
- Huts with coordinates
- Data completeness percentages

### 2. Data Quality
- ✅ Duplicate detection (names, coordinates)
- ✅ Invalid coordinates (out of range)
- ✅ Suspicious altitudes (<-500m or >9000m)
- ✅ Missing required fields
- ✅ Empty/null values

### 3. Index Optimization
- Existing indexes
- Missing recommended indexes
- Index effectiveness

### 4. Source Distribution
- Huts per source
- Percentages
- Balance analysis

### 5. Geographic Coverage
- Huts per country
- Geographic distribution
- Missing country data

---

## 🔧 What Gets Fixed

### Data Normalization
**Before**:
```
country: "", "N/A", "Unknown", "null"
```
**After**:
```
country: NULL (properly null)
```

### Whitespace Trimming
**Before**:
```
name: " Refuge du Lac  "
```
**After**:
```
name: "Refuge du Lac"
```

### Invalid Coordinates
**Before**:
```
latitude: 99.5 (invalid!)
```
**After**:
```
latitude: NULL
```

### Missing Timestamps
**Before**:
```
updated_at: NULL
```
**After**:
```
updated_at: CURRENT_TIMESTAMP
```

---

## 💾 Backup System

### Automatic Backups

Every time you run `--fix`, `--optimize`, or `--all`, a backup is created:

```
data/backups/mountain_huts_backup_20251106_143052.db
```

**Format**: `mountain_huts_backup_YYYYMMDD_HHMMSS.db`

### Restore from Backup

If something goes wrong:
```bash
# List backups
ls -lh data/backups/

# Restore (copy backup over current database)
cp data/backups/mountain_huts_backup_20251106_143052.db data/mountain_huts.db
```

### Skip Backup (Faster, Not Recommended)
```bash
python tools/improve_database.py --all --no-backup
```

---

## 📄 Generated Reports

After analysis, a JSON report is created:

**File**: `data/database_report.json`

**Contents**:
```json
{
  "timestamp": "2025-11-06T14:30:52",
  "database_path": "data/mountain_huts.db",
  "statistics": {
    "db_size_mb": 12.5,
    "total_huts": 8142,
    "huts_with_coords": 7472,
    "completeness": {
      "name": {"count": 8142, "percentage": 100.0},
      "country": {"count": 8142, "percentage": 100.0},
      "phone": {"count": 1250, "percentage": 15.4}
    }
  },
  "issues": [
    "45 huts missing coordinates",
    "12 huts with invalid coordinates"
  ],
  "fixes": [
    "Fixed 57 data quality issues",
    "Created 2 new indexes"
  ]
}
```

---

## 🎯 Common Use Cases

### Monthly Maintenance
```bash
# Run full optimization once a month
python tools/improve_database.py --all

# This keeps database healthy and fast
```

### Before Major Release
```bash
# Analyze first
python tools/improve_database.py --analyze

# Review report
cat data/database_report.json

# If issues found, fix them
python tools/improve_database.py --fix
```

### After Scraping New Data
```bash
# After running scrapers, optimize
python tools/improve_database.py --optimize

# This rebuilds indexes and updates statistics
```

### Database Feels Slow
```bash
# Quick optimization (no data changes)
python tools/improve_database.py --optimize

# Should improve query performance
```

### Found Data Issues
```bash
# Analyze to see what's wrong
python tools/improve_database.py --analyze

# Fix the issues
python tools/improve_database.py --fix
```

---

## ⚠️ Important Notes

### Safety

1. **Always backs up before changes** (unless `--no-backup`)
2. **Read-only analysis** with `--analyze` is 100% safe
3. **Test on copy first** if unsure
4. **Restore easily** from `data/backups/` if needed

### Performance

- **VACUUM** can take 30-60 seconds
- **Large databases** (>100MB) may take longer
- **Safe to interrupt** with Ctrl+C (changes rolled back)

### Data Loss Prevention

The script will **NEVER**:
- ❌ Delete entire huts
- ❌ Remove source data
- ❌ Drop tables
- ❌ Modify valid data

It will **ONLY**:
- ✅ Fix invalid/malformed data
- ✅ Normalize formatting
- ✅ Set invalid values to NULL
- ✅ Update indexes and statistics

---

## 🐛 Troubleshooting

### "Database is locked"
```bash
# Close any program using the database
# Then try again
python tools/improve_database.py --analyze
```

### "Permission denied"
```bash
# Make sure you have write permissions
chmod +w data/mountain_huts.db

# Or run with appropriate permissions
```

### "Backup failed"
```bash
# Create backup directory manually
mkdir -p data/backups

# Try again
python tools/improve_database.py --fix
```

### Want to see what would be fixed
```python
# Edit the script and set dry_run=True in fix_data_issues()
# Or just run --analyze to see issues without fixing
python tools/improve_database.py --analyze
```

---

## 📈 Performance Impact

### Expected Improvements

| Operation | Time | Benefit |
|-----------|------|---------|
| VACUUM | 30-60s | 5-20% size reduction |
| New Indexes | 10-20s | 2-10x faster queries |
| ANALYZE | 5-10s | Better query plans |
| Data Fixes | Variable | Better data quality |

### Before/After Example

**Before**:
```
Database size: 15.2 MB
Query time: 250ms
Issues: 157
```

**After `--all`**:
```
Database size: 12.8 MB (16% smaller)
Query time: 45ms (5.5x faster)
Issues: 0
```

---

## 🎓 Advanced Usage

### Custom Database Path
```bash
python tools/improve_database.py --analyze --db /path/to/custom.db
```

### Scheduled Maintenance (Cron)
```bash
# Add to crontab for monthly maintenance
0 2 1 * * cd /path/to/project && python tools/improve_database.py --all
```

### Integration with Scrapers
```bash
# After scraping, optimize
python run_all_scrapers.py
python tools/improve_database.py --optimize
```

### Generate Reports Only
```bash
# Analyze without changes, save report
python tools/improve_database.py --analyze > database_analysis.txt
```

---

## ✅ Best Practices

1. **Run `--analyze` monthly** to monitor health
2. **Run `--optimize` after scraping** new data
3. **Run `--fix` when issues detected**
4. **Run `--all` quarterly** for full maintenance
5. **Keep backups** of backups (backup the backup folder)
6. **Review reports** to track database health over time
7. **Test first** on development database if unsure

---

## 📚 See Also

- `COMPLETE_OPTIMIZATION_SUMMARY.md` - Full optimization guide
- `SCRAPER_AUDIT_REPORT.md` - Scraper improvements
- `PERFORMANCE_AUDIT_REPORT.md` - Performance tips
- `database.py` - Database interface code

---

**Questions?** Run with `--help` for quick reference:
```bash
python tools/improve_database.py --help
```

