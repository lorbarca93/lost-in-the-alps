# Performance Audit & Optimization Plan
**Date**: November 6, 2025  
**Current Status**: 7,472 huts loaded

---

## 🔍 Current Performance Analysis

### File Sizes
- `mountain_huts_map.html`: **119.2 KB** (with embedded data)
- `website/huts_data.json`: Data duplicated
- All 7,472 huts loaded at page load

### Performance Bottlenecks Identified

#### 1. **Critical: Large Initial Payload** 🔴
**Issue**: All 7,472 huts embedded in HTML at once
```javascript
var huts = [/* 7472 objects */]; // ~60KB of JSON data
```
**Impact**: 
- Long initial parse time
- Slow page load
- Poor mobile performance
- Wasted memory for huts outside viewport

**Solution**: 
- External JSON file with lazy loading
- Load only visible viewport data initially
- Progressive enhancement

---

#### 2. **Critical: No Debouncing** 🔴
**Issue**: Search and filter functions trigger on every keystroke/click
```javascript
searchBox.addEventListener('input', function() {
    // Runs immediately on every character typed
    applyFilters(); // Expensive operation
});
```
**Impact**:
- UI freezes during typing
- Excessive DOM manipulation
- Battery drain on mobile

**Solution**: Add 300ms debounce

---

#### 3. **High: Inefficient Filtering** 🟠
**Issue**: Multiple forEach loops over all 7,472 huts
```javascript
huts.forEach(function(hut) { /* check each hut */ });
markers.forEach(function(marker) { /* check each marker */ });
```
**Impact**: O(n) operations run frequently

**Solution**: 
- Use Map/Set for O(1) lookups
- Early exits
- Batch updates

---

#### 4. **High: No Request Caching** 🟠
**Issue**: Weather API called every time detail opens
```javascript
fetch('https://api.openweathermap.org/data/2.5/weather...')
  .then(/* no caching */);
```
**Impact**: Unnecessary network requests

**Solution**: Cache API responses (5-minute TTL)

---

#### 5. **Medium: Nearby Huts Calculation** 🟡
**Issue**: Haversine distance calculated for all 7,472 huts on every click
```javascript
huts.forEach(function(hut) {
    var d = getDistance(lat, lon, hut.lat, hut.lon); // Expensive
});
```
**Impact**: ~10-50ms delay per click

**Solution**: 
- Pre-compute spatial index
- Use quadtree for fast nearest-neighbor search

---

#### 6. **Medium: Fuse.js Rebuild** 🟡
**Issue**: Search index rebuilt on every search
```javascript
var fuse = new Fuse(huts, options); // Rebuilds index
```
**Impact**: Wasted CPU cycles

**Solution**: Build index once, reuse

---

#### 7. **Low: Animation on Mobile** 🟢
**Issue**: Marker animations enabled on mobile
```javascript
animate: !isMobileDevice
```
**Current**: Already optimized ✅

---

## 📊 Performance Metrics (Estimated)

### Before Optimization
| Metric | Value | Rating |
|--------|-------|--------|
| **Initial Load** | 2-4s | 🟠 Fair |
| **Time to Interactive** | 3-5s | 🟠 Fair |
| **Search Response** | 100-500ms | 🟡 OK |
| **Filter Response** | 50-200ms | 🟡 OK |
| **Memory Usage** | 80-120MB | 🟠 High |
| **Mobile FPS** | 30-45 | 🟡 OK |

### After Optimization (Target)
| Metric | Target | Improvement |
|--------|--------|-------------|
| **Initial Load** | <1s | 2-4x faster |
| **Time to Interactive** | <1.5s | 2-3x faster |
| **Search Response** | <50ms | 2-10x faster |
| **Filter Response** | <30ms | 2-7x faster |
| **Memory Usage** | 40-60MB | 40% reduction |
| **Mobile FPS** | 55-60 | 20% improvement |

---

## 🚀 Optimization Strategy

### Phase 1: Critical Fixes (Immediate Impact)

#### 1.1 External JSON Loading
```javascript
// Instead of embedded data
var huts = [];
fetch('/website/huts_data.json')
  .then(r => r.json())
  .then(data => {
    huts = data;
    initializeMap();
  });
```
**Benefit**: 
- Reduces HTML from 119KB to ~60KB
- Enables caching
- Parallel download

---

#### 1.2 Debounce Search & Filters
```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

searchBox.addEventListener('input', debounce(function() {
    applyFilters();
}, 300));
```
**Benefit**: 
- 10x fewer filter operations
- Smoother typing
- Better mobile performance

---

#### 1.3 Lazy Weather Loading
```javascript
var weatherCache = new Map();

function loadWeather(lat, lon) {
    const key = `${lat},${lon}`;
    if (weatherCache.has(key)) {
        return Promise.resolve(weatherCache.get(key));
    }
    return fetch(/* ... */).then(data => {
        weatherCache.set(key, data);
        setTimeout(() => weatherCache.delete(key), 300000); // 5min TTL
        return data;
    });
}
```
**Benefit**: 
- Eliminates duplicate API calls
- Faster detail sidebar opening
- Reduced API usage

---

### Phase 2: Algorithmic Improvements

#### 2.1 Spatial Index for Nearby Huts
```javascript
// Build once on load
var spatialIndex = new Map();
huts.forEach(hut => {
    const gridKey = Math.floor(hut.lat * 10) + ',' + Math.floor(hut.lon * 10);
    if (!spatialIndex.has(gridKey)) spatialIndex.set(gridKey, []);
    spatialIndex.get(gridKey).push(hut);
});

// Fast lookup - only checks ~50 huts instead of 7472
function getNearbyHuts(lat, lon, radius) {
    const gridKey = Math.floor(lat * 10) + ',' + Math.floor(lon * 10);
    const candidates = spatialIndex.get(gridKey) || [];
    // Also check adjacent cells
    // ... then calculate distance only for candidates
}
```
**Benefit**: 
- 100x faster nearby search (50ms → 0.5ms)
- Instant detail sidebar

---

#### 2.2 Efficient Filtering with Sets
```javascript
// Instead of arrays
var selectedCountries = new Set();
var selectedTypes = new Set();
var selectedSources = new Set();

// O(1) lookup instead of O(n)
function hutMatchesFilters(hut) {
    if (selectedCountries.size > 0 && !selectedCountries.has(hut.country)) {
        return false;
    }
    // ... fast Set.has() checks
}
```
**Benefit**: 
- 3-5x faster filtering
- Scales better with more filters

---

#### 2.3 Cached Fuse.js Index
```javascript
var fuseInstance = null;

function initializeSearch() {
    if (!fuseInstance) {
        fuseInstance = new Fuse(huts, {
            keys: ['name', 'country', 'type'],
            threshold: 0.3
        });
    }
    return fuseInstance;
}
```
**Benefit**: 
- No repeated index building
- Instant search after first load

---

### Phase 3: Advanced Optimizations

#### 3.1 Virtual Scrolling for Search Results
```javascript
// Only render visible search results (10-20 at a time)
function renderSearchResults(results) {
    const visible = results.slice(0, 20);
    // Render only these, add "Show more" button
}
```
**Benefit**: 
- Faster rendering with many results
- Less DOM manipulation

---

#### 3.2 Web Worker for Heavy Calculations
```javascript
// Offload filtering to background thread
const filterWorker = new Worker('filter-worker.js');
filterWorker.postMessage({ huts, filters });
filterWorker.onmessage = (e) => {
    updateMap(e.data.filtered);
};
```
**Benefit**: 
- Non-blocking UI
- Smooth animations during filtering

---

#### 3.3 Progressive Image Loading
```javascript
// Lazy load images in detail sidebar
<img loading="lazy" src="..." />
```
**Benefit**: 
- Faster initial page load
- Reduced bandwidth

---

#### 3.4 Service Worker Caching
```javascript
// Cache static assets and JSON data
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
```
**Benefit**: 
- Instant repeat visits
- Offline capability
- Reduced server load

---

## 📋 Implementation Priority

### 🔴 **Must Have** (Immediate - 2-3 hours)
1. ✅ Debounce search/filter inputs (30 min)
2. ✅ Lazy weather API loading with cache (30 min)
3. ✅ Optimize filtering with Sets (45 min)
4. ✅ Cache Fuse.js instance (15 min)
5. ✅ Virtual scrolling for search (45 min)

**Expected Impact**: 40-60% performance improvement

---

### 🟠 **Should Have** (Short term - 3-4 hours)
6. ⏳ External JSON loading (1 hour)
7. ⏳ Spatial index for nearby huts (1.5 hours)
8. ⏳ Request Animation Frame for smooth updates (1 hour)
9. ⏳ Lazy load detail content (30 min)

**Expected Impact**: Additional 20-30% improvement

---

### 🟡 **Nice to Have** (Long term - 1-2 days)
10. 📋 Web Worker for filtering (3 hours)
11. 📋 Service Worker for offline (4 hours)
12. 📋 Code splitting & lazy modules (2 hours)
13. 📋 Viewport-based marker loading (3 hours)
14. 📋 WebGL rendering for 10K+ markers (4 hours)

**Expected Impact**: Additional 10-20% improvement + offline capability

---

## 🧪 Performance Testing Plan

### Metrics to Track
1. **Lighthouse Score**
   - Performance: Target 90+
   - Accessibility: Target 100
   - Best Practices: Target 100
   - SEO: Target 100

2. **Core Web Vitals**
   - LCP (Largest Contentful Paint): <2.5s
   - FID (First Input Delay): <100ms
   - CLS (Cumulative Layout Shift): <0.1

3. **Custom Metrics**
   - Time to first marker: <1s
   - Search response time: <50ms
   - Filter application time: <30ms
   - Detail sidebar open time: <100ms

### Testing Tools
- Chrome DevTools Performance tab
- Lighthouse CI
- WebPageTest.org
- Real device testing (iOS/Android)

---

## 🎯 Quick Wins (30-Minute Implementation)

### 1. Add Debounce (5 lines of code)
```javascript
function debounce(fn, ms) {
    let t;
    return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), ms);
    };
}
searchBox.addEventListener('input', debounce(applyFilters, 300));
```

### 2. Cache Weather (10 lines of code)
```javascript
const cache = new Map();
function getWeather(lat, lon) {
    const k = `${lat},${lon}`;
    if (cache.has(k)) return Promise.resolve(cache.get(k));
    return fetch(url).then(d => (cache.set(k, d), d));
}
```

### 3. Use Sets for Filters (15 lines of code)
```javascript
const selectedCountries = new Set();
countryCheckbox.addEventListener('change', (e) => {
    e.target.checked ? selectedCountries.add(e.target.value) 
                     : selectedCountries.delete(e.target.value);
});
// Then: if (selectedCountries.size && !selectedCountries.has(hut.country)) return false;
```

**Total time**: 30 minutes  
**Performance gain**: 30-40%  
**Worth it**: YES! ✅

---

## 📚 Resources

### Performance Best Practices
- [Web.dev Performance](https://web.dev/performance/)
- [MDN Performance Guide](https://developer.mozilla.org/en-US/docs/Web/Performance)
- [Lighthouse Performance Scoring](https://web.dev/performance-scoring/)

### Specific Techniques
- [Debouncing & Throttling](https://css-tricks.com/debouncing-throttling-explained-examples/)
- [Leaflet Performance Tips](https://leafletjs.com/examples/performance/)
- [Web Workers Guide](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)

---

## ✅ Success Criteria

### Performance
- ✅ Lighthouse score 90+
- ✅ Load time <1.5s on 4G
- ✅ Search response <50ms
- ✅ Smooth 60fps scrolling

### User Experience
- ✅ No UI freezing during search
- ✅ Instant filter updates
- ✅ Fast detail sidebar opening
- ✅ Smooth map panning

### Mobile
- ✅ Works well on iPhone 6/Android 5+
- ✅ No lag on map interaction
- ✅ Battery-efficient

---

**Next Steps**: Implement Phase 1 optimizations (2-3 hours work)

