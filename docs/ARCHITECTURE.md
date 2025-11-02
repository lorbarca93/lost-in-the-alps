# Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOUNTAIN HUTS SCRAPER SYSTEM                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        SCRAPER LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ scraper_       │  │ scraper_       │  │ scraper_       │   │
│  │ boudy_info.py  │  │ yoursite.py    │  │ another.py     │   │
│  │                │  │                │  │                │   │
│  │ • boudy.info   │  │ • Your website │  │ • Another site │   │
│  │ • 889 huts     │  │ • Your logic   │  │ • Your data    │   │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘   │
│          │                   │                    │            │
│          └───────────────────┼────────────────────┘            │
│                              │                                 │
└──────────────────────────────┼─────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │ base_scraper.py  │
                    │                  │
                    │ • Common logic   │
                    │ • Normalization  │
                    │ • Error handling │
                    └────────┬─────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌──────────────────┐                         │
│                    │   database.py    │                         │
│                    │                  │                         │
│                    │ • save_hut()     │                         │
│                    │ • save_batch()   │                         │
│                    │ • get_stats()    │                         │
│                    │ • deduplication  │                         │
│                    └────────┬─────────┘                         │
│                             │                                   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ mountain_huts.db  │
                    │    (SQLite)       │
                    ├───────────────────┤
                    │ • mountain_huts   │
                    │   - 889 records   │
                    │   - All sources   │
                    │                   │
                    │ • scraper_sources │
                    │   - Metadata      │
                    └─────────┬─────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       QUERY LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ query_database.py│         │ Your Python Code │             │
│  │                  │         │                  │             │
│  │ • Interactive UI │         │ • Direct API     │             │
│  │ • Search         │         │ • Custom queries │             │
│  │ • Export         │         │ • Analysis       │             │
│  │ • Statistics     │         │                  │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘


DATA FLOW EXAMPLE:
══════════════════

1. Run Scraper
   $ python scraper_boudy_info.py

2. Scraper fetches data from website
   boudy.info API → 889 huts

3. Data normalized by base_scraper
   {source_id, name, lat, lon, ...}

4. Database layer saves/updates
   Check (source, source_id) → Insert or Update

5. Database stores all sources together
   mountain_huts table: 889 records

6. Query data from any tool
   query_database.py or custom scripts


ADDING A NEW SCRAPER:
═══════════════════════

1. Copy template
   scraper_template.py → scraper_newsite.py

2. Implement scrape() method
   Fetch from website
   Parse data
   Return list of huts

3. Run it
   $ python scraper_newsite.py

4. Data automatically added to same database!
   No changes needed elsewhere


BENEFITS:
═════════

✅ Single unified database
✅ Multiple data sources
✅ Automatic deduplication
✅ Easy to extend
✅ Consistent data format
✅ Update tracking
✅ Source attribution
```
