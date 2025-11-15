# Lost in the Alps - Web Interface

This folder contains the static web interface for the Lost in the Alps mountain hut explorer.

**Note:** This folder has its own Git repository for deployment. The main project repository (parent folder) is kept local only.

## 🚀 Quick Start

### Local Development

```bash
# Start local server
python -m http.server 8080

# Open http://localhost:8080 in your browser
```

### Updating Data

Data files are generated from the main project database. From the project root:

```bash
# Generate statistics and data files
python tools/api/stats.py           # Updates web/data/stats.json
python tools/api/export_huts.py     # Updates web/data/huts.json
python tools/generate_huts_json.py  # Updates web/data/huts_data.json

# Regenerate interactive map
python tools/create_ultra_simple_map.py
```

## 📁 Structure

```
web/
├── index.html                # Landing page (auto-redirects to map)
├── map.html                  # Main interactive map application
├── about.html                # About page
├── privacy-policy.html       # Privacy policy
├── _redirects                # Redirect rules
├── data/                     # Data files (generated)
│   ├── huts_data.json       # Map data (~4.4 MB, 7,472 huts)
│   ├── huts.json            # Searchable huts data
│   └── stats.json           # Statistics
├── css/
│   └── styles.css           # Main stylesheet
└── js/
    ├── map-app.js           # Interactive map logic
    ├── main.js              # Landing page logic
    └── cookie-consent.js    # GDPR cookie consent
```

## 📝 File Descriptions

### HTML Pages

- **index.html**: Landing page with project overview, statistics, and quick links. Auto-redirects to map.
- **map.html**: Full-screen interactive map with filtering, search, favorites, and detailed hut information.
- **about.html**: Project philosophy and detailed information.
- **privacy-policy.html**: GDPR-compliant privacy policy.

### Data Files (data/)

- **huts_data.json**: Complete hut data for map markers (~4.4 MB)
- **huts.json**: Searchable hut data for autocomplete
- **stats.json**: Real-time statistics for the landing page

### JavaScript (js/)

- **map-app.js**: Core map functionality (Leaflet, clustering, filtering, search, favorites)
- **main.js**: Landing page animations and statistics loading
- **cookie-consent.js**: GDPR cookie consent banner

### CSS (css/)

- **styles.css**: Complete styling for the map interface

## 🔧 Build Scripts

Build scripts are located in the parent project's `tools/api/`:

- **stats.py**: Generates `web/data/stats.json` from database
- **export_huts.py**: Generates `web/data/huts.json` from database
- **generate_huts_json.py**: Generates `web/data/huts_data.json` from database

## 📊 Data Flow

```
Parent Project (local only)
    │
    ├──> tools/api/stats.py ──> web/data/stats.json
    ├──> tools/api/export_huts.py ──> web/data/huts.json
    └──> tools/generate_huts_json.py ──> web/data/huts_data.json
```

## 🌐 Deployment

This folder is designed for static hosting:

1. All assets are self-contained
2. External CDN dependencies: Leaflet, Fuse.js (with SRI hashes)
3. No server-side processing required
4. CORS-safe (all data files are served from same origin)

### Git Setup for Deployment

This folder has its own Git repository:

```bash
# Initialize (already done)
git init

# Add remote repository
git remote add origin <your-github-repo-url>

# Add and commit files
git add .
git commit -m "Initial commit"

# Push to GitHub
git push -u origin main
```

## 🔒 Security

- SRI (Subresource Integrity) hashes on all CDN resources
- GDPR-compliant cookie consent
- No tracking without user consent
- Client-side only processing (no data sent to servers)

## 📱 Mobile Support

- Responsive design for all screen sizes
- Touch-optimized map controls
- Collapsible sidebars for mobile devices
- Larger tap targets on small screens
