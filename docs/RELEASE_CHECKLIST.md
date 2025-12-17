# Release / Ops Checklist

Use this when updating data or deploying the static site.

## Data Refresh
1) Run scrapers (or selected ones):
```
python scripts/run_all_scrapers.py
```
2) Assign countries (fast offline):
```
python tools/assign_countries_fast.py
```
3) Reclassify hut types (ensures new taxonomy):
```
python tools/reclassify_hut_types.py
```
4) Export JSON for web:
```
python tools/generate_huts_json.py
```

## Verification
- Open `web/index.html` locally (`cd web && python -m http.server 8080`).
- Check totals, filters, and map layer loading.
- Spot-check a few hut detail panels and external links.

## Security & Hosting
- Keep `_headers` and `_redirects` in place (HSTS, CSP, HTTPS).
- Confirm no tokens or secrets are committed; Mapbox token stays in `localStorage`.
- Ensure CDN assets use SRI; external links have `rel="noopener noreferrer"`.

## Deploy
- Commit and push to `main` (or merge from `develop`).
- For GitHub Pages: ensure “Enforce HTTPS” is enabled.
- For Netlify: headers/redirects are auto-applied.

## Post-Deploy
- Smoke test the live site (map load, filters, detail sidebar).
- If GA is enabled, verify consent gating works.

