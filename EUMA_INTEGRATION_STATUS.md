# EUMA Integration Status

**Date**: November 5, 2025  
**Website**: https://www.european-mountaineers.eu/map  
**Status**: ⏸️ Awaiting API Access

---

## 🎯 About EUMA

The **European Mountaineering Association (EUMA)** maintains a comprehensive database of:
- **2,500+ mountain huts** across Europe
- Hiking trails
- Rock climbing areas

**Source**: [EUMA Blog - Over 2,500 Huts on One Map](https://www.european-mountaineers.eu/blog/post/over-2500-huts-on-one-map)

---

## 🔍 Technical Investigation

### Website Architecture
- **Platform**: Webmapp (Angular/Ionic SPA)
- **App ID**: 30
- **Layer ID**: 467 (Mountain Huts)
- **Taxonomy**: euma-pois-huts
- **Base URL**: https://30.app.webmapp.it

### API Endpoints Discovered

**✅ Working Endpoints:**
```
https://geohub.webmapp.it/api/app/elbrus/30/config.json
- Returns: Full app configuration (458 MB)
- Contains: Layer definitions, settings, taxonomy
- Huts layer: ID 467, taxonomy "euma-pois-huts"
```

**❌ Restricted Endpoints:**
```
https://geohub.webmapp.it/api/ec/poi/download/467.geojson - 401 Unauthorized
https://geohub.webmapp.it/api/ec/layer/download_pois/467.geojson - 200 but invalid JSON
https://geohub.webmapp.it/api/ec/poi/30/geojson - 401 Unauthorized
```

### Findings

1. **Data is not embedded** in the config file
2. **API requires authentication** for POI downloads
3. **Dynamic loading** - data fetched on-demand as users browse
4. **No public bulk export** found

---

## 🚫 Challenges

### Technical Barriers
- ❌ API endpoints return 401 Unauthorized
- ❌ No public GeoJSON export available
- ❌ Data loaded dynamically through authenticated requests
- ❌ CORS restrictions on direct API access

### Ethical Considerations
- ⚠️ Data belongs to EUMA and their member organizations
- ⚠️ May require permission to scrape and redistribute
- ⚠️ Respecting terms of service

---

## 💡 Recommended Next Steps

### Option 1: Official API Access (Recommended)
**Contact EUMA for API access:**
- Email: info@european-mountaineers.eu
- Phone: +49 89 14003-56
- Explain your project and request API access
- They may provide authentication credentials or bulk export

**Benefits:**
- ✅ Legal and ethical
- ✅ Official support
- ✅ Potential collaboration
- ✅ Ongoing updates

### Option 2: Browser Automation
**Use Selenium/Playwright to:**
- Load the map in a real browser
- Intercept network requests
- Extract POI data as it loads

**Drawbacks:**
- ⚠️ Slower and more complex
- ⚠️ May violate terms of service
- ⚠️ Requires maintenance

### Option 3: Manual Network Inspection
**Steps:**
1. Open https://www.european-mountaineers.eu/map in Chrome
2. Open DevTools (F12) > Network tab
3. Filter by "fetch/XHR"
4. Browse the map and identify POI requests
5. Extract authentication headers/tokens
6. Replicate requests programmatically

**Drawbacks:**
- ⚠️ Tokens may expire
- ⚠️ May require user authentication
- ⚠️ Terms of service concerns

---

## 📊 Potential Value

Adding EUMA data would:
- ✅ Add 2,500+ additional huts
- ✅ Improve European coverage
- ✅ Add official data from Alpine Clubs
- ✅ Enhance credibility

**Current database**: 8,142 huts  
**With EUMA**: ~10,600+ huts (30% increase!)

---

## 🎓 What We Learned

### Webmapp Architecture
- Uses GeoHub backend
- Layer-based structure
- Taxonomy-based organization
- Authentication-protected APIs

### EUMA Structure
```
App ID: 30
Layer 467: Mountain Huts
  - Taxonomy: euma-pois-huts
  - ~2,500 POIs
  - Includes: name, location, descriptions, contact
```

---

## ✅ Immediate Actions

**For now, I recommend:**

1. ✉️ **Contact EUMA** - Explain your open-source project
2. 📋 **Document this attempt** - Show professional approach
3. 🤝 **Propose collaboration** - Mutual benefit
4. ⏰ **Continue with current data** - 8,142 huts is already excellent

**Your current 4 sources already provide excellent coverage:**
- refuges.info: 5,250 huts (64.5%)
- mountainhuts.info: 1,343 huts (16.5%)  
- boudy.info: 889 huts (10.9%)
- mountain-huts.net: 660 huts (8.1%)

---

## 📝 Files Created During Investigation

- `tools/investigate_euma.py` - Initial website investigation
- `tools/investigate_euma_api.py` - API endpoint search
- `tools/find_euma_api.py` - Systematic API testing
- `tools/extract_euma_layers.py` - Layer extraction
- `tools/parse_euma_huts.py` - Huts layer parsing
- `tools/fetch_euma_huts.py` - Data fetching attempts
- `tools/download_euma_huts.py` - Download attempts
- `tools/extract_huts_from_config.py` - Config analysis
- `debug/euma_page.html` - Saved EUMA main page
- `debug/euma_webmapp.html` - Saved Webmapp app HTML
- `debug/euma_huts_layer.json` - Layer configuration

**These can be cleaned up if you decide not to pursue EUMA integration.**

---

**Status**: Investigation complete. Awaiting decision on how to proceed.

