# Agent Works (Timeline of Improvements)

Dive-deep log of major improvements, with rationale and outcomes. Changelog stays separate for terse release notes.

---

## 2025-12-07 — Security Hardening & Professional Polish
- **What**: Added strict static-site headers (`_headers`), enforced HTTPS (`_redirects`), documented security posture.
- **Why**: Protect users on static hosting (GitHub Pages/Netlify) with HSTS, CSP, and safer defaults; avoid token leaks.
- **How**:
  - `_headers`: HSTS, CSP (tiles + Mapbox CDNs), X-Frame-Options DENY, Referrer-Policy, Permissions-Policy, X-Content-Type-Options.
  - `_redirects`: Force HTTP→HTTPS 301.
  - `docs/SECURITY.md`: Hosting/CSP allowlist, Mapbox token guidance (set via `localStorage`), SRI and external link notes.
- **Result**: Safer static deployment; clear allowlist for tiles/scripts; Mapbox token not bundled by default.

## 2025-12-07 — Documentation Refresh (Scraper/Data Pipeline)
- **What**: Updated README data counts and added end-to-end pipeline steps.
- **Why**: Keep operators aligned on the current dataset and the exact scrape→clean→export path.
- **How**:
  - README: 6,767 huts; 41 countries; sources listed; quick pipeline: run scrapers → assign countries → reclassify → export JSON → serve.
  - Added security highlights in README (token handling, CSP).
- **Result**: Current numbers and a concise operational path for data refresh.

## 2025-12-07 — Contributor & Operations Experience
- **What**: Added contributor guidelines, code of conduct, release/ops checklist, and issue template.
- **Why**: Standardize collaboration, set expectations, and reduce release friction.
- **How**:
  - `CONTRIBUTING.md`: branching, scraper/data steps, security notes, PR guidance.
  - `CODE_OF_CONDUCT.md`: concise behavioral expectations.
  - `docs/RELEASE_CHECKLIST.md`: run scrapers → country assign → reclassify → export JSON → verify → deploy → post-deploy checks.
  - `.github/ISSUE_TEMPLATE/bug_report.md`: structured bug intake.
- **Result**: Smoother onboarding, repeatable releases, and clearer issue reports.

## 2025-12-07 — Hut Type Reclassification & Data Cleanliness
- **What**: Unified hut taxonomy (Staffed hut, Unstaffed cabin, Bivouac, Shelter, Guesthouse, Unknown) and reclassified all huts.
- **Why**: Improve filter clarity and data integrity across sources with mixed languages.
- **How**:
  - `data_cleaner.py`: expanded alias map (French/German/Italian/Slovenian terms), keyword fallback.
  - `tools/reclassify_hut_types.py`: migrated 5,582 records to the new taxonomy.
  - `web/index.html` / `map-app.js`: updated filter labels and stats to the new categories.
- **Result**: Clearer filtering and consistent types: 4,092 Unstaffed cabins; 1,489 Staffed huts; 779 Guesthouses; 18 Bivouacs; 10 Shelters; 379 Unknown.

## 2025-12-07 — Data Refresh & Export
- **What**: Ran scrapers and regenerated web data.
- **Why**: Bring the dataset to current totals after cleaning and reclassification.
- **How**:
  - Scrapers: refuges.info, mountainhuts.info, mountain-huts.net, tyrol.com.
  - Country assignment: `tools/assign_countries_fast.py`.
  - Export: `tools/generate_huts_json.py`.
- **Result**: 6,767 huts with 100% country coverage; `web/data/huts_data.json` refreshed; filters/statistics reflect new taxonomy.

