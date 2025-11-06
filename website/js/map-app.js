// Mountain Huts Explorer - Main Application Logic
// This file contains all the JavaScript for the interactive map

let map, markerCluster, markers = [];
let allHuts = [];
let fuse = null;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getHutId(hut) {
    return `${hut.lat}_${hut.lon}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// SIDEBAR VIEW MANAGEMENT
// ============================================================================

function switchSidebarView(view) {
    const filterSidebar = document.getElementById('filter-sidebar');
    const favoritesSidebar = document.getElementById('favorites-sidebar');
    const detailSidebar = document.getElementById('detail-sidebar');
    
    // Close detail sidebar if open
    detailSidebar.classList.remove('open');
    
    if (view === 'filters') {
        filterSidebar.style.display = 'flex';
        favoritesSidebar.style.display = 'none';
        
        // Update nav buttons
        document.getElementById('nav-filters').classList.add('active');
        document.getElementById('nav-favorites').classList.remove('active');
    } else if (view === 'favorites') {
        filterSidebar.style.display = 'none';
        favoritesSidebar.style.display = 'flex';
        
        // Update nav buttons
        document.getElementById('nav-filters-fav').classList.remove('active');
        document.getElementById('nav-favorites-fav').classList.add('active');
        
        // Render favorites list
        renderFavoritesList();
    }
}

function renderFavoritesList() {
    const favoritesList = document.getElementById('favorites-list');
    const favorites = FavoritesManager.getAll();
    
    if (favorites.length === 0) {
        favoritesList.innerHTML = `
            <div style="text-align: center; padding: 40px 20px; color: #64748b;">
                <div style="font-size: 48px; margin-bottom: 16px;">⭐</div>
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 8px;">No favorites yet!</div>
                <div style="font-size: 12px; line-height: 1.6;">Click the ⭐ button on any hut to add it to your favorites.</div>
            </div>
        `;
        return;
    }
    
    // Get favorite huts data
    const favoriteHuts = allHuts.filter(hut => {
        const hutId = getHutId(hut);
        return favorites.includes(hutId);
    });
    
    // Sort by name
    favoriteHuts.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    
    // Render list
    let html = '';
    favoriteHuts.forEach(hut => {
        const hutId = getHutId(hut);
        const safeId = hutId.replace(/\./g, '-');
        
        html += `
            <div class="favorite-item" onclick="showHutDetails(allHuts.find(h => getHutId(h) === '${hutId}'))">
                <div class="favorite-item-header">
                    <div class="favorite-item-name">${escapeHtml(hut.name || 'Unknown')}</div>
                    <button class="favorite-item-remove" onclick="event.stopPropagation(); removeFavoriteAndUpdate('${hutId}')" title="Remove from favorites">
                        ×
                    </button>
                </div>
                <div class="favorite-item-meta">
                    ${hut.country && hut.country !== 'N/A' ? `<span>🌍 ${escapeHtml(hut.country)}</span>` : ''}
                    ${hut.altitude && hut.altitude !== 'N/A' ? `<span>🏔️ ${escapeHtml(String(hut.altitude))}m</span>` : ''}
                    ${hut.type && hut.type !== 'N/A' ? `<span>🏠 ${escapeHtml(hut.type)}</span>` : ''}
                </div>
            </div>
        `;
    });
    
    favoritesList.innerHTML = html;
}

function removeFavoriteAndUpdate(hutId) {
    FavoritesManager.remove(hutId);
    updateAllFavoriteCounts();
    renderFavoritesList();
    showToast('Removed from favorites');
}

function updateAllFavoriteCounts() {
    const count = FavoritesManager.count();
    const badge1 = document.getElementById('fav-badge');
    const badge2 = document.getElementById('fav-badge-2');
    const mainCount = document.getElementById('favorites-count-main');
    
    if (badge1) badge1.textContent = count;
    if (badge2) badge2.textContent = count;
    if (mainCount) mainCount.textContent = count;
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadHutsData();
    updateAllFavoriteCounts();
});

function initializeMap() {
    // Create map centered on Alps
    map = L.map('map', {
        center: [47.0, 13.0],
        zoom: 6,
        zoomControl: true,
        attributionControl: true
    });
    
    // Define map layers
    const layers = {
        'openstreetmap': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }),
        'topo': L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            maxZoom: 17,
            attribution: 'Map data: &copy; OpenStreetMap, SRTM | Style: &copy; OpenTopoMap'
        }),
        'cyclosm': L.tileLayer('https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png', {
            maxZoom: 20,
            attribution: '&copy; OpenStreetMap | Style: CyclOSM'
        }),
        'humanitarian': L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap | Style: Humanitarian OSM'
        }),
        'relief': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 13,
            attribution: 'Tiles &copy; Esri'
        }),
        'light': L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap &copy; CARTO'
        }),
        'satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri'
        })
    };
    
    // Add default layer
    let currentLayer = layers['topo'];
    currentLayer.addTo(map);
    
    // Layer switching
    document.querySelectorAll('input[name="map-layer"]').forEach(radio => {
        radio.addEventListener('change', function(e) {
            if (e.target.checked) {
                map.removeLayer(currentLayer);
                currentLayer = layers[e.target.value];
                currentLayer.addTo(map);
            }
        });
    });
    
    // Initialize marker cluster
    markerCluster = L.markerClusterGroup({
        maxClusterRadius: 60,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        chunkedLoading: true,
        chunkInterval: 200,
        chunkDelay: 50
    });
    
    map.addLayer(markerCluster);
}

// ============================================================================
// DATA LOADING
// ============================================================================

function loadHutsData() {
    fetch('website/huts_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(`✅ Loaded ${data.length} huts`);
            allHuts = data;
            initializeHuts(data);
            initializeSearch(data);
            initializeFavorites();
        })
        .catch(error => {
            console.error('❌ Error loading huts data:', error);
            alert('Error loading map data. Please refresh the page.');
        });
}

// ============================================================================
// HUTS DISPLAY
// ============================================================================

function initializeHuts(huts) {
    console.log(`Initializing ${huts.length} huts...`);
    
    // Build country filters
    const countries = {};
    huts.forEach(hut => {
        if (hut.country && hut.country !== 'N/A') {
            countries[hut.country] = (countries[hut.country] || 0) + 1;
        }
    });
    
    const sortedCountries = Object.keys(countries).sort();
    const filterDiv = document.getElementById('country-filters');
    filterDiv.innerHTML = '';
    
    sortedCountries.forEach(country => {
        const label = document.createElement('label');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = true;
        checkbox.className = 'country-filter';
        checkbox.dataset.country = country;
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(` ${country} (${countries[country]})`));
        filterDiv.appendChild(label);
    });
    
    // Check if mobile
    const isMobile = window.innerWidth <= 768;
    
    // Create markers
    huts.forEach(hut => {
        const baseRadius = isMobile ? 12 : 7;
        const hoverRadius = isMobile ? 15 : 10;
        
        const marker = L.circleMarker([hut.lat, hut.lon], {
            radius: baseRadius,
            fillColor: hut.color,
            color: '#ffffff',
            weight: 2.5,
            opacity: 1,
            fillOpacity: 0.85
        });
        
        marker.hutData = hut;
        marker._baseRadius = baseRadius;
        marker._hoverRadius = hoverRadius;
        
        // Hover effects
        marker.on('mouseover', function() {
            if (!isMobile) {
                this.setRadius(this._hoverRadius);
                this.setStyle({ weight: 3, fillOpacity: 1 });
            }
        });
        
        marker.on('mouseout', function() {
            if (!isMobile) {
                this.setRadius(this._baseRadius);
                this.setStyle({ weight: 2.5, fillOpacity: 0.85 });
            }
        });
        
        // Click to show details
        marker.on('click', function(e) {
            showHutDetails(this.hutData);
            L.DomEvent.stopPropagation(e);
        });
        
        markers.push(marker);
        markerCluster.addLayer(marker);
    });
    
    console.log(`✅ Added ${markers.length} markers to map`);
    
    // Initialize filters
    initializeFilters();
    updateStats();
}

// ============================================================================
// FILTERING
// ============================================================================

function initializeFilters() {
    // Type filters
    document.querySelectorAll('.type-filter').forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });
    
    // Country filters
    document.querySelectorAll('.country-filter').forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });
    
    // Source filters
    document.querySelectorAll('.source-filter').forEach(cb => {
        cb.addEventListener('change', applyFilters);
    });
    
    // All countries checkbox
    document.getElementById('filter-all').addEventListener('change', function(e) {
        document.querySelectorAll('.country-filter').forEach(cb => {
            cb.checked = e.target.checked;
        });
        applyFilters();
    });
    
    // Altitude sliders
    document.getElementById('min-altitude').addEventListener('input', updateAltitudeRange);
    document.getElementById('max-altitude').addEventListener('input', updateAltitudeRange);
    document.getElementById('min-altitude').addEventListener('change', applyFilters);
    document.getElementById('max-altitude').addEventListener('change', applyFilters);
    
    // Capacity inputs
    document.getElementById('min-capacity').addEventListener('change', applyFilters);
    document.getElementById('max-capacity').addEventListener('change', applyFilters);
    
    // Contact info filters
    ['phone', 'email', 'website', 'hours', 'manager', 'owner', 'description'].forEach(type => {
        const el = document.getElementById(`filter-has-${type}`);
        if (el) el.addEventListener('change', applyFilters);
    });
    
    // Reset button
    document.getElementById('reset-filters').addEventListener('click', resetFilters);
    
    // Export button
    document.getElementById('export-kmz').addEventListener('click', exportKML);
}

function applyFilters() {
    const selectedTypes = Array.from(document.querySelectorAll('.type-filter:checked')).map(cb => cb.value);
    const selectedCountries = Array.from(document.querySelectorAll('.country-filter:checked')).map(cb => cb.dataset.country);
    const selectedSources = Array.from(document.querySelectorAll('.source-filter:checked')).map(cb => cb.value);
    
    const minAlt = parseInt(document.getElementById('min-altitude').value) || 0;
    const maxAlt = parseInt(document.getElementById('max-altitude').value) || 4000;
    const minCap = parseInt(document.getElementById('min-capacity').value) || 0;
    const maxCap = parseInt(document.getElementById('max-capacity').value) || 999999;
    
    const allCountriesChecked = document.getElementById('filter-all').checked;
    
    markers.forEach(marker => {
        const hut = marker.hutData;
        let show = true;
        
        // Type filter
        if (!selectedTypes.includes(hut.type)) show = false;
        
        // Country filter
        if (!allCountriesChecked && selectedCountries.length > 0) {
            if (!selectedCountries.includes(hut.country)) show = false;
        }
        
        // Source filter
        if (!selectedSources.includes(hut.source)) show = false;
        
        // Altitude filter
        const alt = parseInt(hut.altitude) || 0;
        if (alt < minAlt || alt > maxAlt) show = false;
        
        // Capacity filter
        const cap = parseInt(hut.capacity) || 0;
        if (cap < minCap || cap > maxCap) show = false;
        
        // Contact info filters
        if (document.getElementById('filter-has-phone')?.checked && (!hut.phone || hut.phone === 'N/A')) show = false;
        if (document.getElementById('filter-has-email')?.checked && (!hut.email || hut.email === 'N/A')) show = false;
        if (document.getElementById('filter-has-website')?.checked && (!hut.website || hut.website === 'N/A')) show = false;
        if (document.getElementById('filter-has-hours')?.checked && (!hut.opening || hut.opening === 'N/A')) show = false;
        if (document.getElementById('filter-has-manager')?.checked && (!hut.manager || hut.manager === 'N/A')) show = false;
        if (document.getElementById('filter-has-owner')?.checked && (!hut.owner || hut.owner === 'N/A')) show = false;
        if (document.getElementById('filter-has-description')?.checked && (!hut.description || hut.description === 'N/A')) show = false;
        
        // Show/hide marker
        if (show) {
            if (!markerCluster.hasLayer(marker)) {
                markerCluster.addLayer(marker);
            }
        } else {
            markerCluster.removeLayer(marker);
        }
    });
    
    updateStats();
}

function updateAltitudeRange() {
    const min = document.getElementById('min-altitude').value;
    const max = document.getElementById('max-altitude').value;
    document.getElementById('altitude-range').textContent = `${min} - ${max} m`;
}

function resetFilters() {
    // Reset all checkboxes
    document.querySelectorAll('.type-filter, .country-filter, .source-filter').forEach(cb => cb.checked = true);
    document.getElementById('filter-all').checked = true;
    
    // Reset sliders
    document.getElementById('min-altitude').value = 0;
    document.getElementById('max-altitude').value = 4000;
    updateAltitudeRange();
    
    // Reset capacity
    document.getElementById('min-capacity').value = '';
    document.getElementById('max-capacity').value = '';
    
    // Reset contact filters
    ['phone', 'email', 'website', 'hours', 'manager', 'owner', 'description'].forEach(type => {
        const el = document.getElementById(`filter-has-${type}`);
        if (el) el.checked = false;
    });
    
    applyFilters();
}

// ============================================================================
// STATISTICS
// ============================================================================

function updateStats() {
    const visibleMarkers = markers.filter(m => markerCluster.hasLayer(m));
    const visibleHuts = visibleMarkers.map(m => m.hutData);
    
    // Count
    document.getElementById('stats-visible').textContent = visibleHuts.length;
    document.getElementById('stats-total-visible').textContent = visibleHuts.length;
    
    // Countries
    const uniqueCountries = new Set(visibleHuts.map(h => h.country).filter(c => c && c !== 'N/A'));
    document.getElementById('stats-countries').textContent = uniqueCountries.size;
    
    // Altitude
    const altitudes = visibleHuts.map(h => parseInt(h.altitude)).filter(a => !isNaN(a) && a > 0);
    if (altitudes.length > 0) {
        const avgAlt = Math.round(altitudes.reduce((a, b) => a + b, 0) / altitudes.length);
        const minAlt = Math.min(...altitudes);
        const maxAlt = Math.max(...altitudes);
        
        document.getElementById('stats-avg-alt').textContent = `${avgAlt}m`;
        document.getElementById('stats-avg-altitude').textContent = `${avgAlt}m`;
        document.getElementById('stats-alt-range').textContent = `${minAlt}m - ${maxAlt}m`;
    } else {
        document.getElementById('stats-avg-alt').textContent = '0m';
        document.getElementById('stats-avg-altitude').textContent = 'N/A';
        document.getElementById('stats-alt-range').textContent = 'N/A';
    }
    
    // Contact info
    const withContact = visibleHuts.filter(h => 
        (h.phone && h.phone !== 'N/A') || 
        (h.email && h.email !== 'N/A') || 
        (h.website && h.website !== 'N/A')
    ).length;
    document.getElementById('stats-with-contact').textContent = withContact;
    
    // Capacity
    const capacities = visibleHuts.map(h => parseInt(h.capacity)).filter(c => !isNaN(c) && c > 0);
    if (capacities.length > 0) {
        const minCap = Math.min(...capacities);
        const maxCap = Math.max(...capacities);
        document.getElementById('stats-capacity-range').textContent = `${minCap} - ${maxCap} beds`;
    } else {
        document.getElementById('stats-capacity-range').textContent = 'N/A';
    }
}

// ============================================================================
// SEARCH
// ============================================================================

function initializeSearch(huts) {
    fuse = new Fuse(huts, {
        keys: ['name', 'country', 'type'],
        threshold: 0.3,
        minMatchCharLength: 2
    });
    
    const searchBox = document.getElementById('search-box');
    const searchClear = document.getElementById('search-clear');
    const searchResults = document.getElementById('search-results');
    
    searchBox.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        if (query.length === 0) {
            searchResults.classList.remove('visible');
            searchClear.classList.remove('visible');
            return;
        }
        
        searchClear.classList.add('visible');
        
        if (query.length < 2) {
            searchResults.innerHTML = '<div class="search-no-results">Type at least 2 characters...</div>';
            searchResults.classList.add('visible');
            return;
        }
        
        const results = fuse.search(query).slice(0, 10);
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
        } else {
            let html = '';
            results.forEach(result => {
                const hut = result.item;
                html += `<div class="search-result-item" data-lat="${hut.lat}" data-lon="${hut.lon}">`;
                html += `<div class="search-result-name">${escapeHtml(hut.name)}</div>`;
                html += `<div class="search-result-meta">`;
                if (hut.country && hut.country !== 'N/A') html += `🌍 ${escapeHtml(hut.country)} • `;
                if (hut.altitude && hut.altitude !== 'N/A') html += `🏔️ ${escapeHtml(String(hut.altitude))}m • `;
                html += escapeHtml(hut.source);
                html += '</div></div>';
            });
            searchResults.innerHTML = html;
            
            // Add click handlers
            document.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', function() {
                    const lat = parseFloat(this.dataset.lat);
                    const lon = parseFloat(this.dataset.lon);
                    const hut = allHuts.find(h => h.lat === lat && h.lon === lon);
                    if (hut) {
                        showHutDetails(hut);
                        searchResults.classList.remove('visible');
                        searchBox.value = '';
                        searchClear.classList.remove('visible');
                    }
                });
            });
        }
        
        searchResults.classList.add('visible');
    });
    
    searchClear.addEventListener('click', function() {
        searchBox.value = '';
        searchResults.classList.remove('visible');
        searchClear.classList.remove('visible');
    });
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchBox.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('visible');
        }
    });
}

// ============================================================================
// DETAIL SIDEBAR
// ============================================================================

function showHutDetails(hut) {
    const detailSidebar = document.getElementById('detail-sidebar');
    const detailTitle = document.getElementById('detail-hut-name');
    const detailContent = document.getElementById('detail-content');
    
    // Set title
    detailTitle.textContent = hut.name;
    
    // Build content
    let content = '<div>';
    
    // Badges
    content += '<div style="margin-bottom: 20px;">';
    if (hut.altitude && hut.altitude !== 'N/A') {
        content += `<span class="detail-badge"><span class="badge-icon">🏔️</span>${escapeHtml(String(hut.altitude))} m</span>`;
    }
    if (hut.country && hut.country !== 'N/A') {
        content += `<span class="detail-badge"><span class="badge-icon">🌍</span>${escapeHtml(hut.country)}</span>`;
    }
    if (hut.type && hut.type !== 'N/A') {
        content += `<span class="detail-badge"><span class="badge-icon">🏠</span>${escapeHtml(hut.type)}</span>`;
    }
    content += '</div>';
    
    // Main Information
    content += '<div class="detail-section"><h3>📋 Main Information</h3>';
    if (hut.capacity && hut.capacity !== 'N/A') {
        content += `<div class="detail-info-box"><div class="info-label">Capacity</div><div class="info-value">${escapeHtml(String(hut.capacity))} beds</div></div>`;
    }
    if (hut.opening && hut.opening !== 'N/A') {
        content += `<div class="detail-info-box"><div class="info-label">Opening Hours</div><div class="info-value">${escapeHtml(hut.opening)}</div></div>`;
    }
    content += '</div>';
    
    // Contact
    if ((hut.phone && hut.phone !== 'N/A') || (hut.email && hut.email !== 'N/A') || (hut.website && hut.website !== 'N/A')) {
        content += '<div class="detail-section"><h3>📞 Contact</h3>';
        if (hut.phone && hut.phone !== 'N/A') {
            content += `<a href="tel:${hut.phone}" class="detail-button primary">📱 Call: ${escapeHtml(hut.phone)}</a>`;
        }
        if (hut.email && hut.email !== 'N/A') {
            content += `<a href="mailto:${hut.email}" class="detail-button secondary">✉️ Email</a>`;
        }
        if (hut.website && hut.website !== 'N/A') {
            content += `<a href="${hut.website}" target="_blank" class="detail-button tertiary">🌐 Website</a>`;
        }
        content += '</div>';
    }
    
    // Description
    if (hut.description && hut.description !== 'N/A') {
        content += `<div class="detail-section"><h3>ℹ️ Description</h3><p style="color: #475569; line-height: 1.6;">${escapeHtml(hut.description)}</p></div>`;
    }
    
    // Favorites button
    const hutId = `${hut.lat}_${hut.lon}`;
    const isFavorite = FavoritesManager.has(hutId);
    content += '<div class="detail-section">';
    content += '<h3>⭐ Save for Later</h3>';
    content += `<button class="favorite-btn ${isFavorite ? 'favorited' : ''}" id="fav-btn-${hutId}" onclick="toggleFavorite('${hutId}')">`;
    content += isFavorite ? '⭐ Saved to Favorites' : '☆ Add to Favorites';
    content += '</button></div>';
    
    content += '<div id="weather-container"></div>';
    content += '<div id="nearby-container"></div>';
    content += '</div>';
    
    detailContent.innerHTML = content;
    detailSidebar.classList.add('open');
    
    // Center map on hut
    map.setView([hut.lat, hut.lon], 13);
    
    // Load weather and nearby huts
    if (hut.lat && hut.lon) {
        loadWeather(hut.lat, hut.lon);
        loadNearbyHuts(hut.lat, hut.lon, hut.name);
    }
}

// Back button
document.getElementById('back-to-filters').addEventListener('click', function() {
    document.getElementById('detail-sidebar').classList.remove('open');
});

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.getElementById('detail-sidebar').classList.remove('open');
    }
});

// ============================================================================
// FAVORITES SYSTEM
// ============================================================================

const FavoritesManager = {
    storageKey: 'mountainhuts_favorites_v1',
    
    getAll() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : [];
        } catch (e) {
            console.error('Error reading favorites:', e);
            return [];
        }
    },
    
    save(favorites) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(favorites));
            return true;
        } catch (e) {
            console.error('Error saving favorites:', e);
            alert('⚠️ Could not save. Browser storage may be full or disabled.');
            return false;
        }
    },
    
    add(hutId) {
        const favorites = this.getAll();
        if (!favorites.includes(hutId)) {
            favorites.push(hutId);
            this.save(favorites);
        }
    },
    
    remove(hutId) {
        const favorites = this.getAll();
        const filtered = favorites.filter(id => id !== hutId);
        this.save(filtered);
    },
    
    toggle(hutId) {
        if (this.has(hutId)) {
            this.remove(hutId);
            return false;
        } else {
            this.add(hutId);
            return true;
        }
    },
    
    has(hutId) {
        return this.getAll().includes(hutId);
    },
    
    count() {
        return this.getAll().length;
    },
    
    exportJSON() {
        const favoriteIds = this.getAll();
        if (favoriteIds.length === 0) {
            alert('❌ No favorites to export!\n\nClick ⭐ on huts to add them to favorites first.');
            return;
        }
        
        const favoriteHuts = allHuts.filter(hut => favoriteIds.includes(`${hut.lat}_${hut.lon}`));
        const exportData = {
            exported: new Date().toISOString(),
            version: '1.0',
            count: favoriteHuts.length,
            favorites: favoriteHuts.map(hut => ({
                id: `${hut.lat}_${hut.lon}`,
                name: hut.name,
                lat: hut.lat,
                lon: hut.lon,
                altitude: hut.altitude,
                country: hut.country
            }))
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `favorite_huts_${favoriteHuts.length}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast(`📥 Exported ${favoriteHuts.length} favorites!`);
    },
    
    importJSON() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/json,.json';
        
        input.onchange = function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    const imported = JSON.parse(e.target.result);
                    if (!imported.favorites || !Array.isArray(imported.favorites)) {
                        alert('❌ Invalid file format!');
                        return;
                    }
                    
                    if (confirm(`Import ${imported.favorites.length} favorites?\n\nCurrent: ${FavoritesManager.count()} favorites\nWill merge (no duplicates)`)) {
                        const currentFavs = FavoritesManager.getAll();
                        const newFavs = imported.favorites.map(fav => fav.id);
                        const merged = Array.from(new Set(currentFavs.concat(newFavs)));
                        
                        FavoritesManager.save(merged);
                        const added = merged.length - FavoritesManager.count();
                        showToast(`✅ Imported! ${added} new favorites`);
                        updateAllFavoriteCounts();
                        renderFavoritesList();
                    }
                } catch (err) {
                    alert(`❌ Error: ${err.message}`);
                }
            };
            reader.readAsText(file);
        };
        
        input.click();
    },
    
    exportGPX() {
        const favoriteIds = this.getAll();
        if (favoriteIds.length === 0) {
            alert('❌ No favorites!');
            return;
        }
        
        const favoriteHuts = allHuts.filter(hut => favoriteIds.includes(`${hut.lat}_${hut.lon}`));
        let gpx = '<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="LostInTheAlps">\n<metadata><name>Favorite Huts</name></metadata>\n';
        
        favoriteHuts.forEach(hut => {
            gpx += `<wpt lat="${hut.lat}" lon="${hut.lon}"><name>${escapeXml(hut.name)}</name>`;
            if (hut.altitude && hut.altitude !== 'N/A') gpx += `<ele>${hut.altitude}</ele>`;
            gpx += '</wpt>\n';
        });
        
        gpx += '</gpx>';
        
        const blob = new Blob([gpx], {type: 'application/gpx+xml'});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'favorite_huts.gpx';
        a.click();
        URL.revokeObjectURL(url);
        showToast('📥 Exported to GPX!');
    }
};

function initializeFavorites() {
    updateAllFavoriteCounts();
    renderFavoritesList();
}

function toggleFavorite(hutId) {
    const nowFavorite = FavoritesManager.toggle(hutId);
    const btn = document.getElementById(`fav-btn-${hutId}`);
    
    if (btn) {
        btn.className = `favorite-btn ${nowFavorite ? 'favorited' : ''}`;
        btn.innerHTML = nowFavorite ? '⭐ Saved to Favorites' : '☆ Add to Favorites';
    }
    
    updateAllFavoriteCounts();
    renderFavoritesList();
    showToast(nowFavorite ? '⭐ Added to favorites!' : 'Removed from favorites');
}

function showFavoritesOnly() {
    const favIds = FavoritesManager.getAll();
    if (favIds.length === 0) {
        showToast('❌ No favorites yet!');
        return;
    }
    
    let count = 0;
    markers.forEach(marker => {
        const id = `${marker.hutData.lat}_${marker.hutData.lon}`;
        if (favIds.includes(id)) {
            if (!markerCluster.hasLayer(marker)) markerCluster.addLayer(marker);
            count++;
        } else {
            markerCluster.removeLayer(marker);
        }
    });
    
    updateStats();
    showToast(`⭐ Showing ${count} favorites`);
}

function showAllHutsReset() {
    markers.forEach(marker => {
        if (!markerCluster.hasLayer(marker)) markerCluster.addLayer(marker);
    });
    updateStats();
}

// ============================================================================
// WEATHER & NEARBY HUTS
// ============================================================================

// OpenWeatherMap API Configuration
// Get your free API key at: https://openweathermap.org/api
const OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE'; // Replace with your actual API key

function loadWeather(lat, lon) {
    const weatherContainer = document.getElementById('weather-container');
    if (!weatherContainer) return;
    
    // Check if API key is configured
    if (!OPENWEATHER_API_KEY || OPENWEATHER_API_KEY === 'YOUR_API_KEY_HERE') {
        weatherContainer.innerHTML = `
            <div class="detail-section">
                <h3>🌤️ Weather</h3>
                <div style="padding: 12px; background: rgba(59, 130, 246, 0.1); border-radius: 8px; border-left: 3px solid #3b82f6;">
                    <p style="font-size: 12px; color: #1e40af; line-height: 1.6; margin-bottom: 8px;">
                        <strong>⚙️ Setup Required:</strong>
                    </p>
                    <p style="font-size: 11px; color: #475569; line-height: 1.6; margin-bottom: 8px;">
                        To enable live weather data, you need a free OpenWeatherMap API key.
                    </p>
                    <ol style="font-size: 11px; color: #475569; line-height: 1.6; margin-left: 20px; margin-bottom: 8px;">
                        <li>Visit <a href="https://openweathermap.org/api" target="_blank" style="color: #3b82f6;">openweathermap.org/api</a></li>
                        <li>Sign up for a free account</li>
                        <li>Get your API key</li>
                        <li>Add it to <code style="background: #f1f5f9; padding: 2px 4px; border-radius: 3px;">website/js/map-app.js</code></li>
                    </ol>
                </div>
            </div>
        `;
        return;
    }
    
    // Show loading state
    weatherContainer.innerHTML = `
        <div class="detail-section">
            <h3>🌤️ Weather</h3>
            <div style="text-align: center; padding: 20px; color: #64748b;">
                <div style="font-size: 24px; margin-bottom: 8px;">⏳</div>
                <div style="font-size: 12px;">Loading weather...</div>
            </div>
        </div>
    `;
    
    // Fetch weather data
    const apiUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${OPENWEATHER_API_KEY}`;
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const temp = Math.round(data.main.temp);
            const feelsLike = Math.round(data.main.feels_like);
            const humidity = data.main.humidity;
            const windSpeed = Math.round(data.wind.speed * 3.6); // Convert m/s to km/h
            const description = data.weather[0].description;
            const icon = data.weather[0].icon;
            
            // Get weather emoji based on condition
            const weatherEmoji = getWeatherEmoji(data.weather[0].main, icon);
            
            weatherContainer.innerHTML = `
                <div class="detail-section">
                    <h3>🌤️ Current Weather</h3>
                    <div style="display: flex; align-items: center; gap: 16px; padding: 12px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 10px; margin-bottom: 12px;">
                        <div style="font-size: 48px; line-height: 1;">${weatherEmoji}</div>
                        <div style="flex: 1;">
                            <div style="font-size: 32px; font-weight: 700; color: #0369a1; line-height: 1;">${temp}°C</div>
                            <div style="font-size: 12px; color: #475569; text-transform: capitalize; margin-top: 4px;">${description}</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px;">
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px;">
                            <div style="color: #64748b; margin-bottom: 2px;">Feels like</div>
                            <div style="font-weight: 600; color: #1e293b;">${feelsLike}°C</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px;">
                            <div style="color: #64748b; margin-bottom: 2px;">Humidity</div>
                            <div style="font-weight: 600; color: #1e293b;">${humidity}%</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px;">
                            <div style="color: #64748b; margin-bottom: 2px;">Wind</div>
                            <div style="font-weight: 600; color: #1e293b;">${windSpeed} km/h</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px;">
                            <div style="color: #64748b; margin-bottom: 2px;">Pressure</div>
                            <div style="font-weight: 600; color: #1e293b;">${data.main.pressure} hPa</div>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 10px; color: #94a3b8; text-align: center;">
                        Data from OpenWeatherMap
                    </div>
                </div>
            `;
        })
        .catch(error => {
            console.error('Weather fetch error:', error);
            weatherContainer.innerHTML = `
                <div class="detail-section">
                    <h3>🌤️ Weather</h3>
                    <div style="padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 3px solid #ef4444;">
                        <p style="font-size: 12px; color: #991b1b; line-height: 1.6;">
                            <strong>⚠️ Error loading weather:</strong><br>
                            ${error.message}
                        </p>
                        <p style="font-size: 11px; color: #64748b; margin-top: 8px; line-height: 1.6;">
                            ${error.message.includes('401') ? 'Invalid API key. Please check your OpenWeatherMap API key.' : 
                              error.message.includes('429') ? 'API rate limit exceeded. Try again later.' :
                              'Could not connect to weather service.'}
                        </p>
                    </div>
                </div>
            `;
        });
}

function getWeatherEmoji(condition, icon) {
    const isNight = icon && icon.endsWith('n');
    
    switch(condition) {
        case 'Clear':
            return isNight ? '🌙' : '☀️';
        case 'Clouds':
            return isNight ? '☁️' : '⛅';
        case 'Rain':
        case 'Drizzle':
            return '🌧️';
        case 'Thunderstorm':
            return '⛈️';
        case 'Snow':
            return '❄️';
        case 'Mist':
        case 'Fog':
            return '🌫️';
        default:
            return '🌤️';
    }
}

function loadNearbyHuts(lat, lon, currentName) {
    const nearby = allHuts
        .filter(h => h.name !== currentName)
        .map(h => ({
            ...h,
            distance: haversineDistance(lat, lon, h.lat, h.lon)
        }))
        .filter(h => h.distance < 20)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 5);
    
    const nearbyContainer = document.getElementById('nearby-container');
    if (nearbyContainer && nearby.length > 0) {
        let html = '<div class="detail-section"><h3>📍 Nearby Huts</h3>';
        nearby.forEach(hut => {
            html += `<div style="padding: 10px; background: #f8fafc; border-radius: 6px; margin-bottom: 8px; cursor: pointer;" onclick='showHutDetails(${JSON.stringify(hut)})'>`;
            html += `<div style="font-weight: 600; color: #1e293b;">${escapeHtml(hut.name)}</div>`;
            html += `<div style="font-size: 12px; color: #64748b;">${hut.distance.toFixed(1)} km away`;
            if (hut.altitude && hut.altitude !== 'N/A') html += ` • ${escapeHtml(String(hut.altitude))}m`;
            html += '</div></div>';
        });
        html += '</div>';
        nearbyContainer.innerHTML = html;
    }
}

// ============================================================================
// UTILITIES
// ============================================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeXml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
}

function haversineDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = 'position: fixed; bottom: 80px; right: 20px; background: #1e293b; color: white; padding: 16px 24px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 10000; font-weight: 600;';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function exportKML() {
    const visibleHuts = markers.filter(m => markerCluster.hasLayer(m)).map(m => m.hutData);
    if (visibleHuts.length === 0) {
        alert('No huts to export! Please adjust your filters.');
        return;
    }
    
    let kml = '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n<name>Mountain Huts</name>\n';
    visibleHuts.forEach(hut => {
        kml += `<Placemark><name>${escapeXml(hut.name)}</name><Point><coordinates>${hut.lon},${hut.lat},${hut.altitude || 0}</coordinates></Point></Placemark>\n`;
    });
    kml += '</Document>\n</kml>';
    
    const blob = new Blob([kml], {type: 'application/vnd.google-earth.kml+xml'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mountain_huts.kml';
    a.click();
    URL.revokeObjectURL(url);
    
    alert(`Exported ${visibleHuts.length} huts to KML file!`);
}

// ============================================================================
// MOBILE SUPPORT
// ============================================================================

// Mobile menu toggle
document.getElementById('mobile-menu-btn')?.addEventListener('click', function() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('open');
    this.querySelector('.menu-text').textContent = sidebar.classList.contains('open') ? 'Close' : 'Filters';
});

// Close sidebar on map tap (mobile)
if (window.innerWidth <= 768) {
    map.on('click', function() {
        document.querySelector('.sidebar')?.classList.remove('open');
        document.getElementById('detail-sidebar')?.classList.remove('open');
    });
}

// ============================================================================
// PRESET FILTERS
// ============================================================================


