# Security Audit Report - Lost in the Alps
**Date**: November 6, 2025  
**Audited by**: AI Security Review  
**Scope**: Complete codebase security assessment

---

## Executive Summary

This security audit has reviewed the entire "Lost in the Alps" codebase, including:
- Python backend (scrapers, database layer, tools)
- Frontend HTML/JavaScript/CSS
- API endpoints
- External dependencies
- Data handling and storage

**Overall Risk Level**: **LOW-MEDIUM** ✅

The codebase demonstrates good security practices in most areas. Critical issues identified are primarily related to configuration (placeholder API keys) and some recommended hardening measures.

---

## 🟢 Security Strengths

### 1. XSS Protection (EXCELLENT) ✅
**Finding**: Robust HTML escaping implementation
- **Location**: `tools/create_ultra_simple_map.py`, lines 1666-1670
- **Implementation**: Dedicated `escapeHtml()` function using DOM-based escaping
- **Usage**: Consistently applied to ALL user-generated content before rendering

```javascript
function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

**Evidence of proper usage**:
- Line 1682: `escapeHtml(hut.name)`
- Line 1902: `escapeHtml(hut.country)`
- Line 1914: `escapeHtml(String(hut.capacity))`
- Line 1946: `escapeHtml(hut.phone)` in href attributes

**Risk**: ✅ **NONE** - All dynamic content is properly escaped

---

### 2. SQL Injection Protection (EXCELLENT) ✅
**Finding**: 100% parameterized queries
- **Location**: `database.py` - all database operations
- **Implementation**: All SQL queries use `?` placeholders with tuple parameters

**Examples**:
```python
# Line 41-43: Search by name
cursor.execute(
    "SELECT * FROM mountain_huts WHERE name LIKE ? ORDER BY name",
    (f"%{name}%",)
)

# Line 148: UPDATE with parameters
cursor.execute("""
    UPDATE mountain_huts 
    SET name = ?, hut_type = ?, ...
    WHERE source = ? AND source_id = ?
""", (hut.get('name'), hut.get('hut_type'), ..., source, hut.get('source_id')))

# Line 195: INSERT with parameters
cursor.execute("""
    INSERT INTO mountain_huts (source, source_id, name, ...)
    VALUES (?, ?, ?, ...)
""", (source, hut.get('source_id'), hut.get('name'), ...))
```

**Risk**: ✅ **NONE** - No string concatenation in SQL queries detected

---

### 3. Input Sanitization (GOOD) ✅
**Finding**: Data cleaning and validation at multiple layers

**Python side** (`tools/create_ultra_simple_map.py`, lines 8-17):
```python
def clean_string(s):
    if not s:
        return "N/A"
    s = str(s)
    s = s.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Remove any control characters except spaces
    s = ''.join(char for char in s if ord(char) >= 32 or char == ' ')
    return s.strip() or "N/A"
```

**Scraper validation** (`scrapers/scraper_mountainhuts_info.py`, lines 262-305):
- Phone number validation
- JavaScript variable filtering
- Quote removal
- String concatenation cleanup

**Risk**: ✅ **LOW** - Multi-layer validation reduces risk

---

### 4. No Code Injection Vectors (EXCELLENT) ✅
**Finding**: No dangerous code execution functions detected

**Checked for**:
- ❌ No `eval()` usage
- ❌ No `exec()` usage
- ❌ No `__import__()` dynamic imports
- ❌ No `compile()` usage
- ❌ No shell command injection (`os.system`, `subprocess` with `shell=True`)

**Risk**: ✅ **NONE**

---

### 5. Database Security (GOOD) ✅
**Finding**: Proper database isolation and constraints

**Strengths**:
- Unique constraint on `(source, source_id)` prevents duplicates (line 57)
- `.gitignore` properly excludes database files (line 13-14)
- Database stored locally, not in version control
- Automatic indexes for performance and security (lines 74-88)

**Risk**: ✅ **LOW**

---

### 6. GDPR Compliance (EXCELLENT) ✅
**Finding**: Robust cookie consent implementation
- **Location**: `website/js/cookie-consent.js`

**Features**:
- 🍪 Explicit consent before loading analytics
- ✅ Clear accept/reject options
- 📝 Privacy policy link
- 🔒 SameSite=Lax cookie flag (line 51)
- 🔐 IP anonymization for GA (line 156)
- 💾 LocalStorage for persistent consent (line 35)
- 🎯 Granular control (Accept All vs Necessary Only)

**Risk**: ✅ **NONE** - Fully GDPR compliant

---

## 🟡 Medium Priority Issues

### 1. Hardcoded Placeholder API Keys ⚠️
**Finding**: Placeholder API keys in code
**Severity**: MEDIUM (Configuration issue, not a vulnerability)

**Locations**:
1. **OpenWeatherMap API**: `mountain_huts_map.html` & `tools/create_ultra_simple_map.py`
   ```javascript
   var apiKey = 'YOUR_OPENWEATHERMAP_API_KEY';
   ```

2. **Google Analytics ID**: `website/js/cookie-consent.js` (lines 9, 415, 420)
   ```javascript
   gaTrackingId: 'G-XXXXXXXXXX'
   ```

**Impact**:
- ✅ Weather widget gracefully falls back to link-based weather
- ✅ Analytics simply doesn't load if not configured
- ❌ Users need to manually configure these

**Recommendation**: 
```javascript
// Option 1: Environment-based configuration
const apiKey = window.OPENWEATHER_API_KEY || '';

// Option 2: Configuration file
fetch('/config.json').then(r => r.json()).then(config => {
    apiKey = config.openWeatherKey;
});

// Option 3: Build-time substitution
// Use a build script to inject keys from environment variables
```

**Risk**: 🟡 **MEDIUM** - Reduces functionality but doesn't expose security issues

---

### 2. No Subresource Integrity (SRI) ⚠️
**Finding**: External CDN resources loaded without integrity checks
**Severity**: MEDIUM

**Vulnerable locations** (`mountain_huts_map.html`, lines 7-13):
```html
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://cdn.jsdelivr.net/npm/fuse.js@6.6.2"></script>
```

**Attack vector**: If CDN is compromised, malicious code could be injected

**Recommendation**: Add SRI hashes
```html
<script 
  src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha384-..."
  crossorigin="anonymous"
></script>
```

**How to generate SRI**:
```bash
curl https://unpkg.com/leaflet@1.9.4/dist/leaflet.js | openssl dgst -sha384 -binary | openssl base64 -A
```

**Risk**: 🟡 **MEDIUM** - Dependency on third-party CDN trustworthiness

---

### 3. Missing Security Headers ⚠️
**Finding**: No security HTTP headers configured
**Severity**: MEDIUM

**Missing headers**:
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://unpkg.com
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

**Implementation** (for GitHub Pages):
Since you're using GitHub Pages, add a `_headers` file in the `website/` directory:
```
/*
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://unpkg.com; img-src 'self' data: https:; connect-src 'self' https://api.openweathermap.org
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
```

**Risk**: 🟡 **MEDIUM** - Increases attack surface for XSS and clickjacking

---

### 4. Mixed Content Potential ⚠️
**Finding**: Some HTTP links detected in output
**Severity**: LOW-MEDIUM

**Locations**:
- `mountain_huts_map.html`, lines 1472-1474: Google Maps icons using HTTP
  ```javascript
  kml += '<Style id="boudy"><IconStyle><Icon><href>http://maps.google.com/...</href></Icon></IconStyle></Style>\n';
  ```

- Line 1491, 1648: Website URL construction
  ```javascript
  var websiteUrl = hut.website.startsWith('http') ? hut.website : 'http://' + hut.website;
  ```

**Impact**: 
- ✅ Modern browsers block HTTP in HTTPS pages
- ❌ Could cause "Mixed Content" warnings

**Recommendation**:
```javascript
// Always use HTTPS
var websiteUrl = hut.website.startsWith('http') 
  ? hut.website.replace('http://', 'https://') 
  : 'https://' + hut.website;

// Or for KML icons
kml += '<Style id="boudy"><IconStyle><Icon><href>https://maps.google.com/...</href></Icon></IconStyle></Style>\n';
```

**Risk**: 🟡 **LOW-MEDIUM** - Browser protections mitigate most risks

---

## 🟢 Low Priority Recommendations

### 1. Rate Limiting for Scrapers ℹ️
**Finding**: Scrapers could benefit from explicit rate limiting
**Severity**: LOW (Good practice)

**Current state**: Basic delays exist
**Recommendation**: Add configurable rate limiting

```python
# In base_scraper.py
import time
from functools import wraps

def rate_limit(calls_per_second=1):
    min_interval = 1.0 / calls_per_second
    last_call = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_call[0] = time.time()
            return result
        return wrapper
    return decorator

# Usage
@rate_limit(calls_per_second=0.5)  # Max 1 call per 2 seconds
def scrape_page(self, url):
    return self.session.get(url)
```

**Risk**: 🟢 **LOW** - More about being a good citizen than security

---

### 2. Coordinate Validation ℹ️
**Finding**: Limited validation of latitude/longitude ranges
**Severity**: LOW

**Current validation**: Type checking only (lines 171-175 in `scraper_mountainhuts_info.py`)
```python
try:
    lat = float(latitude)
    lon = float(longitude)
except (ValueError, TypeError):
    continue
```

**Recommendation**: Add range validation
```python
def validate_coordinates(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        
        # Validate ranges
        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude {lat} out of range")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude {lon} out of range")
        
        # Optional: Validate European bounds for this project
        # Alps region roughly: 43°N-48°N, 5°E-17°E
        # Could add warning for coordinates far outside expected region
        
        return lat, lon
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid coordinates: {e}")
        return None, None
```

**Risk**: 🟢 **LOW** - Data quality issue, not security

---

### 3. Email/Phone Validation ℹ️
**Finding**: Limited validation of contact information
**Severity**: LOW

**Current**: Basic cleaning only (lines 262-278 in `scraper_mountainhuts_info.py`)

**Recommendation**: Add format validation
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    # International format: +XX XXXXXXXXX
    pattern = r'^\+[0-9]{1,3}[\s\-]?[0-9\s\-]{6,}$'
    return re.match(pattern, phone) is not None
```

**Risk**: 🟢 **LOW** - Data quality issue

---

### 4. Dependency Pinning ℹ️
**Finding**: Dependencies use minimum versions, not exact versions
**Severity**: LOW

**Current** (`requirements.txt`):
```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
reverse_geocoder>=1.5.1
aiohttp>=3.9.0
```

**Recommendation**: Use exact versions or ranges
```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
reverse_geocoder==1.5.1
aiohttp==3.9.1
```

**Or use `pip freeze` for production**:
```bash
pip freeze > requirements.lock
```

**Risk**: 🟢 **LOW** - Reproducibility and supply chain concern

---

### 5. User-Agent Consideration ℹ️
**Finding**: Generic User-Agent string
**Severity**: LOW

**Current** (`scrapers/base_scraper.py`, line 26):
```python
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
```

**Recommendation**: Add contact information
```python
'User-Agent': 'LostInTheAlps-Scraper/1.0 (+https://github.com/yourusername/lostinthealps; contact@example.com) Mozilla/5.0'
```

**Why**: 
- Allows website owners to contact you
- Demonstrates good faith
- Helps distinguish from malicious bots

**Risk**: 🟢 **LOW** - Ethical consideration

---

## 🔒 Data Privacy & Storage

### Sensitive Data Handling ✅
**Assessment**: GOOD

**What's NOT stored**:
- ❌ No user passwords
- ❌ No payment information
- ❌ No personal identifiable information (PII)
- ❌ No tracking beyond consented analytics

**What IS stored**:
- ✅ Public hut information (names, locations, contacts)
- ✅ User consent choices (localStorage, reversible)
- ✅ Anonymous analytics (with consent only)

**Privacy compliance**:
- ✅ GDPR-compliant cookie consent
- ✅ Privacy policy provided (`website/privacy-policy.html`)
- ✅ User can revoke consent
- ✅ No data sold or shared

---

## 🔐 Authentication & Authorization

**Assessment**: NOT APPLICABLE ✅

This is a **read-only public website** with no authentication system. This is actually a **security advantage** because:
- ❌ No login vulnerabilities
- ❌ No session hijacking risks
- ❌ No password storage concerns
- ❌ No privilege escalation vectors

---

## 🌐 External Dependencies

### Third-Party Libraries (Frontend)
| Library | Version | Source | Risk Level | Notes |
|---------|---------|--------|------------|-------|
| Leaflet | 1.9.4 | unpkg.com | 🟡 Medium | Add SRI hash |
| Leaflet.markercluster | 1.5.3 | unpkg.com | 🟡 Medium | Add SRI hash |
| Fuse.js | 6.6.2 | jsdelivr.net | 🟡 Medium | Add SRI hash |
| Google Analytics | Latest | googletagmanager.com | 🟢 Low | Loaded with consent |

### Python Dependencies
| Library | Version | Purpose | Known Vulnerabilities |
|---------|---------|---------|----------------------|
| requests | >=2.31.0 | HTTP client | None known (current) |
| beautifulsoup4 | >=4.12.0 | HTML parsing | None known |
| lxml | >=4.9.0 | XML parsing | **CVE-2022-2309** (fixed in 4.9.1+) ✅ |
| reverse_geocoder | >=1.5.1 | Geolocation | None known |
| aiohttp | >=3.9.0 | Async HTTP | **CVE-2024-23334** (fixed in 3.9.1+) ⚠️ |

**Recommendation**: Update to latest patches
```bash
pip install --upgrade requests beautifulsoup4 lxml aiohttp
pip freeze > requirements.txt
```

---

## 🚨 Critical Recommendations (Action Required)

### Priority 1: Add SRI to External Scripts
**Impact**: Prevents CDN compromise attacks  
**Effort**: Low (30 minutes)  
**Action**: Update `tools/create_ultra_simple_map.py` to include SRI hashes

### Priority 2: Configure API Keys Securely
**Impact**: Enables full functionality  
**Effort**: Low (15 minutes)  
**Action**: Create configuration guide for deployment

### Priority 3: Add Security Headers
**Impact**: Hardens against XSS, clickjacking  
**Effort**: Low (15 minutes)  
**Action**: Add `_headers` file for GitHub Pages

### Priority 4: Fix Mixed Content
**Impact**: Prevents browser warnings  
**Effort**: Low (10 minutes)  
**Action**: Replace HTTP URLs with HTTPS

### Priority 5: Update Dependencies
**Impact**: Patches known vulnerabilities  
**Effort**: Low (5 minutes)  
**Action**: Run `pip install --upgrade` and test

---

## 📊 Security Score

| Category | Score | Weight | Notes |
|----------|-------|--------|-------|
| **XSS Protection** | 10/10 | 25% | Excellent escaping |
| **SQL Injection** | 10/10 | 25% | Perfect parameterization |
| **Input Validation** | 8/10 | 15% | Good, could add range checks |
| **Dependency Security** | 7/10 | 15% | Need SRI hashes |
| **Configuration** | 6/10 | 10% | Placeholder API keys |
| **Privacy Compliance** | 10/10 | 10% | GDPR compliant |

**Overall Score**: **8.5/10** ✅

---

## 🎯 Action Plan

### Immediate (This Week)
1. ✅ Add SRI integrity hashes to external scripts
2. ✅ Replace HTTP URLs with HTTPS
3. ✅ Create `_headers` file for security headers
4. ✅ Update Python dependencies

### Short Term (This Month)
5. ⏳ Document API key configuration process
6. ⏳ Add coordinate range validation
7. ⏳ Implement rate limiting in scrapers
8. ⏳ Pin dependency versions

### Long Term (Optional)
9. 📋 Set up automated dependency scanning (Dependabot, Snyk)
10. 📋 Add CSP reporting endpoint
11. 📋 Consider self-hosting critical dependencies
12. 📋 Implement automated security testing in CI/CD

---

## ✅ Conclusion

**The "Lost in the Alps" codebase demonstrates solid security fundamentals**:
- ✅ No critical vulnerabilities detected
- ✅ Strong XSS and SQL injection protection
- ✅ GDPR-compliant privacy implementation
- ✅ No dangerous code execution patterns
- ✅ Appropriate data handling

**The main areas for improvement are**:
- 🔧 Configuration management (API keys)
- 🔧 External dependency hardening (SRI)
- 🔧 HTTP security headers
- 🔧 Dependency updates

**Risk Assessment**: This is a **low-risk, read-only public website** with **no authentication**, **no user-generated content storage**, and **no payment processing**. The attack surface is minimal, and the identified issues are mostly about hardening and best practices rather than exploitable vulnerabilities.

**Recommendation**: ✅ **Safe to deploy** after implementing Priority 1-4 recommendations.

---

**Report Generated**: November 6, 2025  
**Next Review**: Recommend annual security audit or after major feature additions

