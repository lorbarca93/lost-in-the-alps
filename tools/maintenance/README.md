# Maintenance Utilities

Quick scripts that helped diagnose or fix one-off data issues. They are
kept for historical reference and ad-hoc checks; none of them run as part
of the normal scraping pipeline.

## Diagnostics

- `check_boudy_coords.py`
- `check_boudy_data.py`
- `check_coords.py`
- `examine_boudy_coords.py`
- `examine_boudy_page.py`
- `test_boudy_scraper.py`

## Legacy Fixes

- `fix_boudy_coords.py`
- `fix_coords_again.py`

> **Heads-up:** The legacy fix scripts modify the production database in
> place. Only re-run them if you intentionally need to roll back to the
> pre-fix coordinate state.
