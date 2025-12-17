# Contributing

Thanks for helping improve Lost in the Alps! Quick guidelines:

## Getting Started
1. Fork and clone the repo.
2. Create a virtualenv, `pip install -r requirements.txt`.
3. Run scrapers/tests in isolation (no external services required).

## Branching
- Use `main` for releases, `develop` for risky changes.
- PRs should target `main` unless coordinated otherwise.

## Data / Scrapers
- Prefer incremental runs: `python scripts/run_all_scrapers.py <scraper_name>`.
- Reclassify/countries/export JSON before submitting data changes:
  ```
  python tools/assign_countries_fast.py
  python tools/generate_huts_json.py
  ```

## Code Style
- Python: keep it simple; add docstrings for public functions.
- Frontend: avoid inline scripts; keep CSP/SRI intact.

## Security
- Do not commit tokens or secrets. Mapbox token stays in `localStorage`.
- Keep `_headers` and `_redirects` intact for static hosting security.

## Pull Requests
- Describe the change, testing steps, and any data updates performed.
- Attach before/after screenshots for UI changes when possible.

