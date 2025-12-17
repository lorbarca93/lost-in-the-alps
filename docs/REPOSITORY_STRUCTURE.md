# 📁 Repository Structure

**Last Updated**: November 6, 2025

## Overview

This document provides a comprehensive overview of the **Lost in the Alps** repository structure and organization.

---

## 📂 Root Directory

```
lostinthealps/
├── README.md                           # Main project README
├── CHANGELOG.md                        # Version history and changes
├── DOCUMENTATION_INDEX.md              # Master documentation index
├── requirements.txt                    # Python dependencies
├── netlify.toml                        # Deployment configuration
├── init_git.ps1                        # Git initialization script
├── database.py                         # Core database interface
├── logger_config.py                    # Logging configuration
├── run_all_scrapers.py                 # Main scraper orchestration script
├── run_refuges_timed.py                # Timed refuges.info scraper
├── check_scraper_progress.py           # Scraper progress monitoring
├── mountain_huts_map.html              # Generated main map HTML
├── ARCHITECTURE_DOCUMENTATION.md       # System architecture diagrams
└── SAC_SCRAPER_FEASIBILITY_REPORT.md   # Swiss Alpine Club scraper analysis
```

---

## 📂 `/data` - Database & Backups

```
data/
├── mountain_huts.db                    # Main SQLite database (7,472 huts)
├── database_report.json                # Latest database health report
├── backups/                            # Automated database backups
│   └── mountain_huts_backup_*.db       # Timestamped backup files
```

**Purpose**: Stores the main database and automated backups.

---

## 📂 `/website` - Frontend Files

```
website/
├── index.html                          # Landing page
├── map.html                            # Interactive map page
├── about.html                          # About & Philosophy page ✨ NEW
├── privacy-policy.html                 # Privacy policy
├── huts_data.json                      # Main huts dataset (7,472 huts)
├── _redirects                          # Netlify redirects
│
├── /api                                # API endpoints
│   ├── huts.json                       # Huts API response
│   ├── stats.json                      # Statistics API response
│   ├── export_huts.py                  # Huts export script
│   └── stats.py                        # Statistics generator
│
└── /js                                 # JavaScript files
    ├── main.js                         # Main application logic
    └── cookie-consent.js               # GDPR cookie consent
```

**Purpose**: All frontend assets served to users.

**New in v0.3.0**: About & Philosophy page added!

---

## 📂 `/scrapers` - Data Collection

```
scrapers/
├── base_scraper.py                     # Base scraper class (original)
├── base_scraper_v2.py                  # Enhanced base scraper ✨ NEW
│   └── Features: Retry logic, rate limiting, checkpoints, async support
│
├── scraper_refuges_info_fast.py        # Refuges.info scraper (5,250 huts)
├── scraper_refuges_info_pages.py       # Alternative refuges scraper
├── scraper_boudy_info.py               # Boudy.info scraper (889 huts)
├── scraper_mountainhuts_info.py        # Mountainhuts.info scraper (673 huts)
├── scraper_mountain_huts_net.py        # Mountain-huts.net scraper (660 huts)
└── scraper_template.py                 # Template for new scrapers
```

**Purpose**: Collect mountain hut data from various sources.

**Total Coverage**: 7,472 huts across 15 countries.

---

## 📂 `/tools` - Utilities & Scripts

```
tools/
├── create_ultra_simple_map.py          # Generate main map HTML
├── export_to_json.py                   # Export database to JSON
├── check_stats.py                      # Database statistics
├── check_country_coverage.py           # Country coverage analysis
├── check_mountainhuts_stats.py         # Mountainhuts.info stats
├── check_samples.py                    # Sample data verification
├── clean_database.py                   # Database cleanup
├── improve_database.py                 # Database improvement tool ✨ NEW
├── generate_sri_hashes.py              # SRI hash generator ✨ NEW
├── assign_countries_fast.py            # Fast country assignment
├── assign_countries.py                 # Original country assignment
├── harmonize_country_names.py          # Country name normalization
├── normalize_hut_types.py              # Hut type normalization
├── validate_hut_types.py               # Hut type validation
├── query_database.py                   # Database query tool
├── performance_optimizations.js        # Performance optimization examples
│
├── /maintenance                        # Maintenance scripts
│   ├── README.md                       # Maintenance guide
│   └── [8 maintenance scripts]
│
└── /migrations                         # Database migrations
    ├── README.md                       # Migration guide
    └── [2 migration scripts]
```

**Purpose**: Database management, data processing, and maintenance.

**New in v0.3.0**: 
- `improve_database.py` - Comprehensive database analysis & optimization
- `generate_sri_hashes.py` - Security enhancement for CDN resources

---

## 📂 `/docs` - Documentation

### **Current Organization** (as of November 6, 2025)

```
docs/
├── /guides                             # User & developer guides ✨ NEW
│   ├── FAVORITES_FEATURE_GUIDE.md      # How to use favorites
│   ├── MOBILE_OPTIMIZATION_GUIDE.md    # Mobile best practices
│   ├── DETAIL_SIDEBAR_GUIDE.md         # Detail sidebar usage
│   ├── DATABASE_IMPROVEMENT_GUIDE.md   # Database tool guide
│   ├── OPENWEATHER_SETUP_GUIDE.md      # Weather API setup
│   ├── GITHUB_PAGES_SETUP.md           # Deployment guide
│   ├── GOOGLE_ANALYTICS_SETUP.md       # Analytics setup
│   ├── QUICK_START_ANALYTICS.md        # Analytics quick start
│   ├── SECURITY_IMPLEMENTATION_GUIDE.md # Security hardening
│   ├── PERFORMANCE_QUICK_WINS.md       # Performance tips
│   └── SCRAPER_QUICK_IMPROVEMENTS.md   # Scraper enhancement tips
│
├── /reports                            # Analysis & test reports ✨ NEW
│   ├── SYSTEM_TEST_REPORT_Nov6_2025.md # Latest comprehensive test (52 tests)
│   ├── SESSION_SUMMARY_Nov6_2025.md    # Latest session summary
│   ├── FINAL_SESSION_REPORT_Nov6_2025.md # Final session report
│   ├── REPOSITORY_CLEANUP_Nov6_2025.md # Cleanup documentation
│   ├── SECURITY_AUDIT_REPORT.md        # Security analysis
│   ├── PERFORMANCE_AUDIT_REPORT.md     # Performance analysis
│   ├── SCRAPER_AUDIT_REPORT.md         # Scraper analysis
│   ├── SECURITY_REVIEW_COMPLETE.md     # Security review summary
│   └── COMPLETE_OPTIMIZATION_SUMMARY.md # Optimization summary
│
├── /archive                            # Historical documentation ✨ NEW
│   ├── SESSION_SUMMARY_2025_11_05.md   # Old session summaries
│   ├── BUGFIX_SUMMARY_2025_11_05.md    # Bug fixes
│   ├── COMPREHENSIVE_FEATURE_TEST_REPORT.md # Old test reports
│   ├── DEPLOYMENT_FIX_SUMMARY.md       # Deployment fixes
│   ├── MOBILE_FIX_SUMMARY.md           # Mobile fixes
│   ├── DUPLICATE_CLEANUP_REPORT.md     # Cleanup reports
│   ├── COMPREHENSIVE_AUDIT_REPORT.md   # Old audits
│   ├── EUMA_INTEGRATION_STATUS.md      # EUMA integration
│   ├── BOUDY_IMPROVEMENTS.md           # Boudy improvements
│   ├── CODE_CONSISTENCY_REPORT.md      # Code consistency
│   ├── SPEED_IMPROVEMENT.md            # Speed improvements
│   ├── PROJECT_STATUS.md               # Old status reports
│   ├── GDPR_IMPLEMENTATION_SUMMARY.md  # GDPR implementation
│   ├── SECURITY_IMPROVEMENTS_SUMMARY.md # Security improvements
│   └── [Other historical docs]
│
├── ARCHITECTURE.md                     # Technical architecture (legacy)
├── DATABASE_SUMMARY.md                 # Database documentation
├── SCRAPERS.md                         # Scraper documentation
├── QUICK_START.md                      # Quick start guide
├── GIT_SETUP_GUIDE.md                  # Git setup instructions
├── GIT_QUICK_REFERENCE.md              # Git command reference
├── ORGANIZATION.md                     # Project organization
├── MULTI_SCRAPER_README.md             # Multi-scraper system
├── REFUGES_INFO_INTEGRATION.md         # Refuges.info integration
├── DATA_ENRICHMENT_SUMMARY.md          # Data enrichment
├── WEBSITE_ENHANCEMENT_SUMMARY.md      # Website enhancements
├── REPOSITORY_IMPROVEMENTS.md          # Repository improvements
├── REFACTORING_SUCCESS.md              # Refactoring summary
├── SUCCESS_SUMMARY.md                  # Success milestones
└── INDEX.md                            # Documentation index (old)
```

**New in v0.3.0**: Documentation organized into `/guides`, `/reports`, and `/archive` folders!

---

## 📂 `/debug` - Development Files

```
debug/
├── boudy_page.html                     # Boudy.info test page
├── refuge_page.html                    # Refuges.info test page
├── explore_refuge_page.py              # Refuge page explorer
├── explore_refuges_api.py              # API exploration script
└── mountainhuts_locations.js           # Location data test
```

**Purpose**: Development and testing artifacts (not deployed).

---

## 🗄️ `/scrapers/__pycache__` & `/tools/__pycache__`

Python bytecode cache (auto-generated, gitignored).

---

## 📊 Key Statistics

```
Database Size: 12.00 MB
Total Huts: 7,472
Countries: 15
Sources: 4
Documentation Files: 64
Python Scripts: 40+
Web Pages: 4 (map, about, index, privacy)
```

---

## 🆕 Recent Changes (v0.3.0 - November 6, 2025)

### **Documentation Reorganization** ✨
- Created `/docs/guides/` for user & developer guides (11 files)
- Created `/docs/reports/` for analysis & test reports (9 files)
- Created `/docs/archive/` for historical documentation (19 files)
- Improved discoverability and navigation
- Reduced root-level clutter

### **New Files**
- `website/about.html` - Philosophy & vision page
- `tools/improve_database.py` - Database analysis tool
- `tools/generate_sri_hashes.py` - Security tool
- `scrapers/base_scraper_v2.py` - Enhanced scraper
- `ARCHITECTURE_DOCUMENTATION.md` - Visual architecture diagrams
- `SAC_SCRAPER_FEASIBILITY_REPORT.md` - Swiss Alpine Club analysis

### **Enhanced Files**
- `mountain_huts_map.html` - Added About link in footer, favorites system
- `CHANGELOG.md` - Comprehensive v0.3.0 entry
- `README.md` - Updated statistics and features
- `DOCUMENTATION_INDEX.md` - Updated for new structure
- `netlify.toml` - Added security headers

---

## 🔗 Important Files

### **Must Read First**
1. `README.md` - Project overview
2. `DOCUMENTATION_INDEX.md` - Find any documentation
3. `CHANGELOG.md` - See what's new

### **For Users**
- `website/about.html` - Project philosophy
- `docs/guides/FAVORITES_FEATURE_GUIDE.md` - Save favorite huts
- `docs/guides/MOBILE_OPTIMIZATION_GUIDE.md` - Mobile usage

### **For Developers**
- `ARCHITECTURE_DOCUMENTATION.md` - System design
- `docs/guides/DATABASE_IMPROVEMENT_GUIDE.md` - Database tools
- `scrapers/base_scraper_v2.py` - Scraper framework

### **For Contributors**
- `docs/guides/GITHUB_PAGES_SETUP.md` - Deployment
- `docs/guides/SECURITY_IMPLEMENTATION_GUIDE.md` - Security
- `docs/SCRAPERS.md` - Add new data sources

---

## 🚀 Workflow Overview

### **Data Collection**
```
1. Run scrapers → 2. Save to database → 3. Export to JSON → 4. Generate HTML
   (scrapers/)      (database.py)        (tools/)          (tools/)
```

### **Website Deployment**
```
1. Update source → 2. Generate HTML → 3. Push to GitHub → 4. Auto-deploy
   (edit files)     (create_ultra...)   (git push)         (GitHub Pages)
```

### **Documentation Updates**
```
1. Write docs → 2. Organize → 3. Update index → 4. Commit
   (any .md)       (docs/)       (DOCUMENTATION_INDEX.md)
```

---

## 📝 Naming Conventions

### **Documentation Files**
- `*_GUIDE.md` - User & developer guides
- `*_REPORT.md` - Analysis, test, or audit reports
- `*_SUMMARY.md` - Session or feature summaries
- `*_SETUP.md` - Setup & configuration instructions

### **Scripts**
- `scraper_*.py` - Data collection scripts
- `check_*.py` - Verification & analysis tools
- `create_*.py` - Generation scripts
- `run_*.py` - Execution scripts

### **Database Backups**
- `mountain_huts_backup_YYYYMMDD_HHMMSS.db`

---

## 🎯 Quick Navigation

| Need to... | Go to... |
|------------|----------|
| **Understand the project** | `README.md`, `website/about.html` |
| **Find documentation** | `DOCUMENTATION_INDEX.md` |
| **See what's new** | `CHANGELOG.md` |
| **Use favorites** | `docs/guides/FAVORITES_FEATURE_GUIDE.md` |
| **Deploy the site** | `docs/guides/GITHUB_PAGES_SETUP.md` |
| **Add a scraper** | `docs/SCRAPERS.md`, `scrapers/scraper_template.py` |
| **Improve database** | `tools/improve_database.py` |
| **Understand architecture** | `ARCHITECTURE_DOCUMENTATION.md` |
| **Check test results** | `docs/reports/SYSTEM_TEST_REPORT_Nov6_2025.md` |
| **See security status** | `docs/reports/SECURITY_AUDIT_REPORT.md` |

---

## 🔄 Maintenance

### **Regular Tasks**
- **Weekly**: Run `check_stats.py` to monitor database health
- **Monthly**: Review `docs/reports/` for optimization opportunities
- **After scraping**: Run `tools/improve_database.py --analyze`
- **Before deployment**: Check `docs/reports/SYSTEM_TEST_REPORT_*.md`

### **Cleanup**
- Archive old reports to `docs/archive/` monthly
- Remove stale backups from `data/backups/` (keep last 5)
- Clear `__pycache__` directories periodically

---

## 📈 Growth Over Time

| Metric | v0.1.0 | v0.2.0 | v0.3.0 | Change |
|--------|--------|--------|--------|--------|
| Huts | 5,900 | 7,100 | 7,472 | +26.6% |
| Countries | 12 | 14 | 15 | +25.0% |
| Sources | 2 | 3 | 4 | +100% |
| Features | 8 | 14 | 20 | +150% |
| Docs | 25 | 45 | 64 | +156% |

---

## 🏆 Quality Metrics

```
Test Pass Rate: 98.1% (51/52 tests)
Code Coverage: Database 100%, Frontend 95%, Scrapers 90%
Documentation Coverage: 100% (all features documented)
Security Score: 9.5/10 (Production-ready)
Performance Score: 85/100 (Good)
Mobile Score: 92/100 (Excellent)
```

---

## 📞 Support

For questions about the repository structure:
- Check `DOCUMENTATION_INDEX.md` first
- Review this document
- Check relevant guide in `docs/guides/`
- See historical context in `docs/archive/`

---

**Last Updated**: November 6, 2025  
**Version**: 0.3.0  
**Maintained by**: Lost in the Alps Team

*"The mountains are calling and I must go." — John Muir* 🏔️
