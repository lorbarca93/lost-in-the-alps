# Security Implementation Guide
**Priority Fixes for Lost in the Alps**

## 🚨 Critical Fix #1: Add Subresource Integrity (SRI) Hashes

### What is SRI?
Subresource Integrity ensures that external resources (scripts, styles) haven't been tampered with. If a CDN is compromised, the browser will block the malicious code.

### How to Generate SRI Hashes

**Method 1: Using Online Tool**
1. Visit https://www.srihash.org/
2. Paste the CDN URL
3. Get the integrity hash

**Method 2: Using Command Line**
```bash
# For Linux/Mac:
curl https://unpkg.com/leaflet@1.9.4/dist/leaflet.js | \
  openssl dgst -sha384 -binary | \
  openssl base64 -A

# For Windows PowerShell:
$response = Invoke-WebRequest -Uri "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" -UseBasicParsing
$bytes = [System.Text.Encoding]::UTF8.GetBytes($response.Content)
$hash = [System.Security.Cryptography.SHA384]::Create().ComputeHash($bytes)
$sri = "sha384-" + [Convert]::ToBase64String($hash)
Write-Output $sri
```

**Method 3: Using Node.js**
```javascript
const crypto = require('crypto');
const https = require('https');

function generateSRI(url) {
  https.get(url, (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
      const hash = crypto.createHash('sha384').update(data).digest('base64');
      console.log(`integrity="sha384-${hash}" crossorigin="anonymous"`);
    });
  });
}

// Generate SRI for all libraries
generateSRI('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js');
generateSRI('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css');
generateSRI('https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js');
generateSRI('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css');
generateSRI('https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css');
generateSRI('https://cdn.jsdelivr.net/npm/fuse.js@6.6.2');
```

### Required Changes

**File**: `tools/create_ultra_simple_map.py`

**Replace lines 1315-1321** with:
```python
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha384-[HASH-HERE]" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"
          integrity="sha384-[HASH-HERE]" crossorigin="anonymous" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"
          integrity="sha384-[HASH-HERE]" crossorigin="anonymous" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha384-[HASH-HERE]" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"
            integrity="sha384-[HASH-HERE]" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/fuse.js@6.6.2"
            integrity="sha384-[HASH-HERE]" crossorigin="anonymous"></script>
```

---

## 🚨 Critical Fix #2: Fix HTTP to HTTPS URLs

### Changes Required

**File**: `tools/create_ultra_simple_map.py`

**Line ~1491, 1648** - Update website URL construction:
```python
# BEFORE:
var websiteUrl = hut.website.startsWith('http') ? hut.website : 'http://' + hut.website;

# AFTER:
var websiteUrl = hut.website.startsWith('http') ? hut.website.replace(/^http:/, 'https:') : 'https://' + hut.website;
```

**Lines ~1472-1474** - Update KML icon URLs:
```python
# BEFORE:
kml += '<Style id="boudy"><IconStyle><Icon><href>http://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon></IconStyle></Style>\\n';

# AFTER:
kml += '<Style id="boudy"><IconStyle><Icon><href>https://maps.google.com/mapfiles/kml/paddle/blu-circle.png</href></Icon></IconStyle></Style>\\n';
```

---

## 🚨 Critical Fix #3: Add Security Headers

### For GitHub Pages (Recommended)

**Create file**: `website/_headers`

```
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()

/mountain_huts_map.html
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://www.googletagmanager.com https://api.openweathermap.org; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: https:; connect-src 'self' https://api.openweathermap.org https://www.googletagmanager.com; font-src 'self' data:; frame-ancestors 'self'

/*.html
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://www.googletagmanager.com
```

**Note**: GitHub Pages may not support custom headers. Alternative: Use Netlify or Cloudflare Pages.

### For Netlify (Current Setup)

**Update file**: `netlify.toml`

Add to the existing file:
```toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    X-Frame-Options = "SAMEORIGIN"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"

[[headers]]
  for = "/mountain_huts_map.html"
  [headers.values]
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://www.googletagmanager.com https://api.openweathermap.org; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: https:; connect-src 'self' https://api.openweathermap.org https://www.googletagmanager.com; font-src 'self' data:"
```

---

## 🚨 Critical Fix #4: Secure API Key Configuration

### OpenWeatherMap API Key

**Current Issue**: Hardcoded placeholder in code

**Solution 1: Environment Variable (Recommended for local development)**

```python
# In tools/create_ultra_simple_map.py
import os

# Get API key from environment variable
openweather_key = os.getenv('OPENWEATHER_API_KEY', 'YOUR_OPENWEATHERMAP_API_KEY')

# Use in template
var apiKey = '{openweather_key}';
```

**Solution 2: Configuration File (Recommended for production)**

Create `config.json`:
```json
{
  "openWeatherApiKey": "your-actual-key-here",
  "googleAnalyticsId": "G-YOUR-ACTUAL-ID"
}
```

**Add to .gitignore**:
```
config.json
.env
```

Update JavaScript to load config:
```javascript
// Load configuration
let config = {{ openWeatherApiKey: '', googleAnalyticsId: '' }};
try {{
    const response = await fetch('/config.json');
    config = await response.json();
}} catch(e) {{
    console.log('Using default configuration');
}}

const apiKey = config.openWeatherApiKey || '';
```

**Solution 3: Build-Time Substitution (Current approach - BEST for GitHub Pages)**

Keep current approach but document clearly:

1. Get free API key from https://openweathermap.org/api
2. Replace `'YOUR_OPENWEATHERMAP_API_KEY'` with actual key in `tools/create_ultra_simple_map.py` line ~1917
3. Run `python tools/create_ultra_simple_map.py`
4. Deploy generated `mountain_huts_map.html`

**Important**: Add `mountain_huts_map.html` to `.gitignore` if it contains the real key, or use GitHub Secrets for deployment.

### Google Analytics ID

**Current Issue**: Placeholder in `website/js/cookie-consent.js`

**Fix**:
1. Get your GA4 property ID from Google Analytics
2. Replace `'G-XXXXXXXXXX'` in lines 9, 415, 420 of `website/js/cookie-consent.js`
3. Commit the change (GA IDs are not sensitive, they're public)

---

## 🚨 Critical Fix #5: Update Python Dependencies

### Check for Vulnerabilities

```bash
# Install pip-audit
pip install pip-audit

# Run audit
pip-audit

# Or use safety
pip install safety
safety check
```

### Update Dependencies

```bash
# Update all to latest versions
pip install --upgrade requests beautifulsoup4 lxml aiohttp reverse_geocoder

# Verify versions
pip freeze | grep -E "requests|beautifulsoup4|lxml|aiohttp|reverse_geocoder"

# Update requirements.txt
pip freeze > requirements.txt
```

### Pin Specific Secure Versions

Edit `requirements.txt`:
```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3          # CVE-2022-2309 fixed in 4.9.1+
aiohttp==3.9.1       # CVE-2024-23334 fixed in 3.9.1+
reverse_geocoder==1.5.1
```

---

## 📋 Implementation Checklist

### Immediate (Do Now)
- [ ] Generate and add SRI hashes to external scripts
- [ ] Replace all HTTP URLs with HTTPS
- [ ] Add security headers to `netlify.toml`
- [ ] Update Python dependencies
- [ ] Test website functionality after changes

### Short Term (This Week)
- [ ] Configure actual OpenWeatherMap API key
- [ ] Configure actual Google Analytics ID
- [ ] Add `config.json` to `.gitignore`
- [ ] Document API key setup in README

### Long Term (Optional)
- [ ] Set up Dependabot for automated dependency updates
- [ ] Implement CSP reporting endpoint
- [ ] Consider self-hosting critical libraries
- [ ] Set up automated security scanning in CI/CD

---

## 🧪 Testing After Implementation

### 1. Test SRI Implementation
- Open browser DevTools (F12)
- Go to Console tab
- Look for any SRI errors
- Verify all external scripts load correctly

### 2. Test HTTPS Links
- Right-click page → Inspect
- Go to Security tab
- Verify "This page is secure"
- No mixed content warnings

### 3. Test Security Headers
- Use https://securityheaders.com/
- Enter your website URL
- Aim for A or A+ rating

### 4. Test Functionality
- Search functionality works
- Map markers display correctly
- Weather widget loads (with API key)
- Filters work properly
- Mobile responsiveness maintained

---

## 📚 Additional Resources

- [MDN: Subresource Integrity](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity)
- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [Content Security Policy Guide](https://content-security-policy.com/)
- [OpenWeatherMap API Documentation](https://openweathermap.org/api)
- [Google Analytics 4 Setup Guide](https://support.google.com/analytics/answer/9304153)

---

## ⚠️ Important Notes

1. **Test Locally First**: Always test changes on localhost before deploying
2. **Backup Database**: Keep backups before making changes
3. **Version Control**: Commit changes in small, logical chunks
4. **Document Changes**: Update this guide if you modify the implementation
5. **Monitor After Deploy**: Watch for errors in production for 24-48 hours

---

## 🆘 Troubleshooting

### SRI Hash Mismatch
- **Error**: "Failed to find a valid digest in the 'integrity' attribute"
- **Fix**: Regenerate the SRI hash using one of the methods above

### CSP Blocking Scripts
- **Error**: "Refused to load the script because it violates CSP"
- **Fix**: Add the script source to `script-src` directive in CSP

### Mixed Content Warnings
- **Error**: "Mixed Content: The page was loaded over HTTPS, but requested an insecure resource"
- **Fix**: Change all `http://` to `https://` in URLs

### API Key Not Working
- **Error**: Weather widget shows fallback message
- **Fix**: 
  1. Verify API key is correct
  2. Check API key is activated (OpenWeather can take 10 minutes)
  3. Verify you haven't exceeded free tier limits

---

**Last Updated**: November 6, 2025  
**Maintainer**: Security Team

