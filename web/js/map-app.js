// Mountain Huts Explorer - Main Application Logic
// This file contains all the JavaScript for the interactive map

let map,
  markerCluster,
  markers = [];
let allHuts = [];
let fuse = null;

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getHutId(hut) {
  return `${hut.lat}_${hut.lon}`;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ============================================================================
// SIDEBAR VIEW MANAGEMENT
// ============================================================================

function switchSidebarView(view) {
  const filterSidebar = document.getElementById("filter-sidebar");
  const favoritesSidebar = document.getElementById("favorites-sidebar");
  const detailSidebar = document.getElementById("detail-sidebar");

  // Close detail sidebar if open
  detailSidebar.classList.remove("open");

  if (view === "filters") {
    filterSidebar.style.display = "flex";
    favoritesSidebar.style.display = "none";

    // Update nav buttons
    document.getElementById("nav-filters").classList.add("active");
    document.getElementById("nav-favorites").classList.remove("active");
  } else if (view === "favorites") {
    filterSidebar.style.display = "none";
    favoritesSidebar.style.display = "flex";

    // Update nav buttons
    document.getElementById("nav-filters-fav").classList.remove("active");
    document.getElementById("nav-favorites-fav").classList.add("active");

    // Render favorites list
    renderFavoritesList();
  }
}

function renderFavoritesList() {
  const favoritesList = document.getElementById("favorites-list");
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
  const favoriteHuts = allHuts.filter((hut) => {
    const hutId = getHutId(hut);
    return favorites.includes(hutId);
  });

  // Sort by name
  favoriteHuts.sort((a, b) => (a.name || "").localeCompare(b.name || ""));

  // Render all favorites (no virtual scrolling)
  let html = "";
  favoriteHuts.forEach((hut) => {
    const hutId = getHutId(hut);
    html += `
        <div class="favorite-item" onclick="showHutDetails(allHuts.find(h => getHutId(h) === '${hutId}'))">
            <div class="favorite-item-header">
                <div class="favorite-item-name">${escapeHtml(
                  hut.name || "Unknown"
                )}</div>
                <button class="favorite-item-remove" onclick="event.stopPropagation(); removeFavoriteAndUpdate('${hutId}')" title="Remove from favorites">
                    ×
                </button>
            </div>
            <div class="favorite-item-meta">
                ${
                  hut.country && hut.country !== "N/A"
                    ? `<span>🌍 ${escapeHtml(hut.country)}</span>`
                    : ""
                }
                ${
                  hut.altitude && hut.altitude !== "N/A"
                    ? `<span>🏔️ ${escapeHtml(String(hut.altitude))}m</span>`
                    : ""
                }
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
  showToast("Removed from favorites");
}

function updateAllFavoriteCounts() {
  const count = FavoritesManager.count();
  const badge1 = document.getElementById("fav-badge");
  const badge2 = document.getElementById("fav-badge-2");
  const mainCount = document.getElementById("favorites-count-main");

  if (badge1) badge1.textContent = count;
  if (badge2) badge2.textContent = count;
  if (mainCount) mainCount.textContent = count;
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// Initialize on page load
document.addEventListener("DOMContentLoaded", function () {
  try {
    initializeMap();
    loadHutsData();
    updateAllFavoriteCounts();
    initializeSidebarToggle();
  } catch (error) {
    console.error("Error during initialization:", error);
    if (typeof Toast !== "undefined" && Toast.error) {
      Toast.error(
        "Error initializing application. Please refresh the page.",
        5000
      );
    } else {
      alert("Error initializing application. Please refresh the page.");
    }
  }
});

// ============================================================================
// SIDEBAR TOGGLE
// ============================================================================

function initializeSidebarToggle() {
  const toggleBtn = document.getElementById("sidebar-toggle-btn");
  const filterSidebar = document.getElementById("filter-sidebar");
  const favoritesSidebar = document.getElementById("favorites-sidebar");
  const mapElement = document.getElementById("map");
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");

  if (!toggleBtn) return;

  // Desktop toggle
  toggleBtn.addEventListener("click", function () {
    toggleSidebar();
  });

  // Mobile hamburger menu button
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener("click", function () {
      // Toggle sidebar visibility
      const currentSidebar =
        filterSidebar.style.display !== "none"
          ? filterSidebar
          : favoritesSidebar;
      const isOpen = currentSidebar.classList.contains("open");

      if (isOpen) {
        currentSidebar.classList.remove("open");
        mobileMenuBtn.classList.remove("active");
      } else {
        currentSidebar.classList.add("open");
        mobileMenuBtn.classList.add("active");
      }
    });
  }

  // Mobile touch gestures for sidebar
  if (window.innerWidth <= 768) {
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;

    document.addEventListener(
      "touchstart",
      function (e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
      },
      { passive: true }
    );

    document.addEventListener(
      "touchend",
      function (e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        handleSwipe();
      },
      { passive: true }
    );

    function handleSwipe() {
      const deltaX = touchEndX - touchStartX;
      const deltaY = touchEndY - touchStartY;
      const minSwipeDistance = 50;
      const maxVerticalSwipe = 30;

      // Only handle horizontal swipes (ignore vertical scrolling)
      if (Math.abs(deltaY) > maxVerticalSwipe) return;

      // Swipe right to open sidebar (from left edge)
      if (
        deltaX > minSwipeDistance &&
        touchStartX < 50 &&
        filterSidebar.classList.contains("hidden")
      ) {
        filterSidebar.classList.remove("hidden");
      }
      // Swipe left to close sidebar
      else if (
        deltaX < -minSwipeDistance &&
        !filterSidebar.classList.contains("hidden") &&
        touchStartX < 200
      ) {
        filterSidebar.classList.add("hidden");
      }
    }
  }

  function toggleSidebar() {
    // Check if the currently visible sidebar is hidden
    const isFilterVisible = filterSidebar.style.display !== "none";
    const isFavoritesVisible = favoritesSidebar.style.display !== "none";
    const currentSidebar = isFilterVisible ? filterSidebar : favoritesSidebar;
    const isHidden = currentSidebar.classList.contains("hidden");

    if (isHidden) {
      // Show sidebar
      currentSidebar.classList.remove("hidden");
      mapElement.classList.remove("sidebar-hidden");
      toggleBtn.classList.remove("sidebar-hidden");
    } else {
      // Hide sidebar
      currentSidebar.classList.add("hidden");
      mapElement.classList.add("sidebar-hidden");
      toggleBtn.classList.add("sidebar-hidden");
    }

    // Invalidate map size after transition
    setTimeout(function () {
      if (map) map.invalidateSize();
    }, 350);
  }
}

function initializeMap() {
  // Create map centered on Alps
  map = L.map("map", {
    center: [47.0, 13.0],
    zoom: 6,
    zoomControl: true,
    attributionControl: true,
  });

  // Define map layers
  const layers = {
    openstreetmap: L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        maxZoom: 19,
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }
    ),
    topo: L.tileLayer("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png", {
      maxZoom: 17,
      attribution:
        "Map data: &copy; OpenStreetMap, SRTM | Style: &copy; OpenTopoMap",
    }),
    cyclosm: L.tileLayer(
      "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
      {
        maxZoom: 20,
        attribution: "&copy; OpenStreetMap | Style: CyclOSM",
      }
    ),
    humanitarian: L.tileLayer(
      "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
      {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap | Style: Humanitarian OSM",
      }
    ),
    relief: L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}",
      {
        maxZoom: 13,
        attribution: "Tiles &copy; Esri",
      }
    ),
    light: L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
      {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap &copy; CARTO",
      }
    ),
    satellite: L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      {
        maxZoom: 19,
        attribution: "Tiles &copy; Esri",
      }
    ),
  };

  // Add default layer
  let currentLayer = layers["topo"];
  currentLayer.addTo(map);

  // Layer switching (dropdown)
  const mapLayerSelect = document.getElementById("map-layer-select");
  if (mapLayerSelect) {
    mapLayerSelect.addEventListener("change", function (e) {
      map.removeLayer(currentLayer);
      currentLayer = layers[e.target.value];
      currentLayer.addTo(map);
    });
  }

  // Initialize marker cluster
  markerCluster = L.markerClusterGroup({
    maxClusterRadius: 60,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    zoomToBoundsOnClick: true,
    chunkedLoading: true,
    chunkInterval: 200,
    chunkDelay: 50,
  });

  map.addLayer(markerCluster);

  // Update stats when map moves or zooms
  map.on("moveend zoomend", updateStatsForViewport);
}

// Update statistics based on markers visible in current viewport
function updateStatsForViewport() {
  if (!map || markers.length === 0) return;

  const bounds = map.getBounds();
  const visibleInViewport = markers.filter((marker) => {
    const markerLatLng = marker.getLatLng();
    return bounds.contains(markerLatLng) && markerCluster.hasLayer(marker);
  });

  if (visibleInViewport.length === 0) {
    // No markers in viewport, keep showing total filtered stats
    return;
  }

  const visibleHuts = visibleInViewport.map((m) => m.hutData);

  // Count by type
  const typeCount = {
    mountain_hut: 0,
    bivouac: 0,
    shelter: 0,
  };

  visibleHuts.forEach((h) => {
    const type = (h.type || "unknown").toLowerCase();
    if (type.includes("bivouac") || type.includes("bivvy")) {
      typeCount.bivouac++;
    } else if (type.includes("shelter")) {
      typeCount.shelter++;
    } else if (
      type.includes("hut") ||
      type.includes("refuge") ||
      type.includes("hütte") ||
      type.includes("rifugio")
    ) {
      typeCount.mountain_hut++;
    } else {
      // Unknown types counted as huts
      typeCount.mountain_hut++;
    }
  });

  // Update visible count
  document.getElementById("stats-visible").textContent =
    visibleInViewport.length;
  document.getElementById("stats-total-visible").textContent =
    visibleInViewport.length;

  // Update type breakdown
  document.getElementById("stats-huts").textContent = typeCount.mountain_hut;
  document.getElementById("stats-bivouacs").textContent = typeCount.bivouac;
  document.getElementById("stats-shelters").textContent = typeCount.shelter;

  // Update countries count
  const uniqueCountries = new Set(
    visibleHuts.map((h) => h.country).filter((c) => c && c !== "N/A")
  );
  document.getElementById("stats-countries").textContent = uniqueCountries.size;
  document.getElementById("stats-countries-count").textContent =
    uniqueCountries.size;

  // Update average altitude
  const altitudes = visibleHuts
    .map((h) => parseInt(h.altitude))
    .filter((a) => !isNaN(a) && a > 0);

  if (altitudes.length > 0) {
    const avgAlt = Math.round(
      altitudes.reduce((a, b) => a + b, 0) / altitudes.length
    );
    document.getElementById("stats-avg-alt").textContent = `${avgAlt}m`;
    document.getElementById("stats-avg-altitude").textContent = `${avgAlt}m`;

    // Update min/max altitude
    const minAlt = Math.min(...altitudes);
    const maxAlt = Math.max(...altitudes);
    document.getElementById("stats-min-alt").textContent = `${minAlt}m`;
    document.getElementById("stats-max-alt").textContent = `${maxAlt}m`;
  }

  // Update contact stats
  const withContact = visibleHuts.filter(
    (h) =>
      (h.phone && h.phone !== "N/A") ||
      (h.email && h.email !== "N/A") ||
      (h.website && h.website !== "N/A")
  ).length;
  document.getElementById("stats-with-contact").textContent = withContact;

  // Update total capacity
  const capacities = visibleHuts
    .map((h) => parseInt(h.capacity))
    .filter((c) => !isNaN(c) && c > 0);
  const totalCapacity =
    capacities.length > 0 ? capacities.reduce((a, b) => a + b, 0) : 0;
  document.getElementById("stats-total-capacity").textContent =
    totalCapacity > 0 ? totalCapacity : "N/A";

  // Update with website count
  const withWebsite = visibleHuts.filter(
    (h) => h.website && h.website !== "N/A"
  ).length;
  document.getElementById("stats-with-website").textContent = withWebsite;

  // Update "open now" (simplified - just a placeholder for now)
  document.getElementById("stats-open-now").textContent = "N/A";

  // Update type distribution chart
  updateTypeDistributionChart(typeCount, visibleInViewport.length);
}

// Update the type distribution bar chart
function updateTypeDistributionChart(typeCount, total) {
  const chart = document.getElementById("type-distribution-chart");
  if (!chart) return;

  const maxCount = Math.max(
    typeCount.mountain_hut,
    typeCount.bivouac,
    typeCount.shelter,
    1
  );

  // Calculate percentages
  const hutPct =
    total > 0 ? Math.round((typeCount.mountain_hut / total) * 100) : 0;
  const bivouacPct =
    total > 0 ? Math.round((typeCount.bivouac / total) * 100) : 0;
  const shelterPct =
    total > 0 ? Math.round((typeCount.shelter / total) * 100) : 0;

  // Update percentage labels
  document.getElementById("chart-huts-pct").textContent = hutPct + "%";
  document.getElementById("chart-bivouacs-pct").textContent = bivouacPct + "%";
  document.getElementById("chart-shelters-pct").textContent = shelterPct + "%";

  // Create bar chart
  const hutHeight = (typeCount.mountain_hut / maxCount) * 100;
  const bivouacHeight = (typeCount.bivouac / maxCount) * 100;
  const shelterHeight = (typeCount.shelter / maxCount) * 100;

  chart.innerHTML = `
    <div style="flex: 1; background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%); height: ${hutHeight}%; border-radius: 4px; transition: all 0.3s ease; min-height: 4px;"></div>
    <div style="flex: 1; background: linear-gradient(180deg, #f97316 0%, #ea580c 100%); height: ${bivouacHeight}%; border-radius: 4px; transition: all 0.3s ease; min-height: 4px;"></div>
    <div style="flex: 1; background: linear-gradient(180deg, #10b981 0%, #059669 100%); height: ${shelterHeight}%; border-radius: 4px; transition: all 0.3s ease; min-height: 4px;"></div>
  `;
}

// ============================================================================
// DATA LOADING
// ============================================================================

function loadHutsData() {
  const progressBar = document.getElementById("loading-progress-bar");
  const skeleton = document.getElementById("loading-skeleton");

  // Show loading state
  if (progressBar) progressBar.style.width = "10%";

  fetch("data/huts_data.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Update progress
      if (progressBar) progressBar.style.width = "50%";

      // Simple approach - just parse JSON directly
      // Progress tracking with reader is complex and can cause issues
      return response.json();
    })
    .then((data) => {
      // Validate data
      if (!data || !Array.isArray(data)) {
        throw new Error("Invalid data format: expected an array");
      }

      console.log(`✅ Loaded ${data.length} huts`);

      // Update progress
      if (progressBar) progressBar.style.width = "95%";

      allHuts = data;

      // Initialize immediately
      console.log("About to initialize huts, search, and favorites...");
      try {
        if (typeof initializeHuts === "function") {
          console.log("Calling initializeHuts...");
          initializeHuts(data);
        } else {
          console.error(
            "initializeHuts is not a function!",
            typeof initializeHuts
          );
        }

        if (typeof initializeSearch === "function") {
          console.log("Calling initializeSearch...");
          initializeSearch(data);
        } else {
          console.error(
            "initializeSearch is not a function!",
            typeof initializeSearch
          );
        }

        if (typeof initializeFavorites === "function") {
          console.log("Calling initializeFavorites...");
          initializeFavorites();
        } else {
          console.error(
            "initializeFavorites is not a function!",
            typeof initializeFavorites
          );
        }

        // Complete loading
        if (progressBar) progressBar.style.width = "100%";
        console.log("✅ Initialization complete");
      } catch (error) {
        console.error("❌ Error during initialization:", error);
        console.error("Stack:", error.stack);
        // Try to hide skeleton even on error
        const skeleton = document.getElementById("loading-skeleton");
        const progress = document.getElementById("loading-progress");
        if (skeleton) {
          skeleton.classList.add("hidden");
          setTimeout(() => (skeleton.style.display = "none"), 300);
        }
        if (progress) {
          progress.style.display = "none";
        }

        if (typeof Toast !== "undefined" && Toast.error) {
          Toast.error("Error initializing map. Please refresh.", 5000);
        } else {
          alert(
            "Error initializing map. Please refresh. Error: " + error.message
          );
        }
      }
    })
    .catch((error) => {
      console.error("❌ Error loading huts data:", error);

      // Hide loading UI
      if (skeleton) {
        skeleton.classList.add("hidden");
        setTimeout(() => (skeleton.style.display = "none"), 300);
      }
      if (progressBar) {
        progressBar.style.display = "none";
      }

      if (typeof Toast !== "undefined" && Toast.error) {
        Toast.error("Error loading map data. Please refresh the page.", 5000);
      } else {
        alert("Error loading map data. Please refresh the page.");
      }
    });
}

// ============================================================================
// HUTS DISPLAY
// ============================================================================

function initializeHuts(huts) {
  console.log(`Initializing ${huts.length} huts...`);

  // Define custom hut marker icon (inspired by mountain-huts.net)
  const hutIcon = L.icon({
    iconUrl: "images/hut-marker.png",
    iconSize: [32, 37], // Size of the icon
    iconAnchor: [16, 37], // Point of the icon which will correspond to marker's location
    popupAnchor: [0, -37], // Point from which the popup should open relative to the iconAnchor
  });

  // Build country filters
  const countries = {};
  huts.forEach((hut) => {
    if (hut.country && hut.country !== "N/A") {
      countries[hut.country] = (countries[hut.country] || 0) + 1;
    }
  });

  const sortedCountries = Object.keys(countries).sort();
  const filterDiv = document.getElementById("country-filters");
  filterDiv.innerHTML = "";

  sortedCountries.forEach((country) => {
    const label = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    checkbox.className = "country-filter";
    checkbox.dataset.country = country;
    label.appendChild(checkbox);
    label.appendChild(
      document.createTextNode(` ${country} (${countries[country]})`)
    );
    filterDiv.appendChild(label);
  });

  // Create markers with custom icon
  huts.forEach((hut) => {
    const marker = L.marker([hut.lat, hut.lon], {
      icon: hutIcon,
    });

    marker.hutData = hut;

    // Click to show details
    marker.on("click", function (e) {
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

  // Hide loading skeleton after markers are added
  const skeleton = document.getElementById("loading-skeleton");
  const progressBar = document.getElementById("loading-progress");
  if (skeleton) {
    skeleton.classList.add("hidden");
    setTimeout(() => {
      if (skeleton) skeleton.style.display = "none";
      if (progressBar) {
        progressBar.style.display = "none";
      }
    }, 300);
  }
}

// ============================================================================
// FILTERING
// ============================================================================

function initializeFilters() {
  // Type filters
  document.querySelectorAll(".type-filter").forEach((cb) => {
    cb.addEventListener("change", applyFilters);
  });

  // Country filters
  document.querySelectorAll(".country-filter").forEach((cb) => {
    cb.addEventListener("change", applyFilters);
  });

  // All countries checkbox
  document
    .getElementById("filter-all")
    .addEventListener("change", function (e) {
      document.querySelectorAll(".country-filter").forEach((cb) => {
        cb.checked = e.target.checked;
      });
      applyFilters();
    });

  // Altitude sliders
  document
    .getElementById("min-altitude")
    .addEventListener("input", updateAltitudeRange);
  document
    .getElementById("max-altitude")
    .addEventListener("input", updateAltitudeRange);
  document
    .getElementById("min-altitude")
    .addEventListener("change", applyFilters);
  document
    .getElementById("max-altitude")
    .addEventListener("change", applyFilters);

  // Reset button
  document
    .getElementById("reset-filters")
    .addEventListener("click", resetFilters);
}

function applyFilters() {
  const selectedTypes = Array.from(
    document.querySelectorAll(".type-filter:checked")
  ).map((cb) => cb.value);
  const selectedCountries = Array.from(
    document.querySelectorAll(".country-filter:checked")
  ).map((cb) => cb.dataset.country);

  const minAlt = parseInt(document.getElementById("min-altitude").value) || 0;
  const maxAlt =
    parseInt(document.getElementById("max-altitude").value) || 4000;
  const allCountriesChecked = document.getElementById("filter-all").checked;

  markers.forEach((marker) => {
    const hut = marker.hutData;
    let show = true;

    // Type filter
    if (!selectedTypes.includes(hut.type)) show = false;

    // Country filter
    if (!allCountriesChecked && selectedCountries.length > 0) {
      if (!selectedCountries.includes(hut.country)) show = false;
    }

    // Altitude filter
    const alt = parseInt(hut.altitude) || 0;
    if (alt < minAlt || alt > maxAlt) show = false;

    // Contact info filters
    if (
      document.getElementById("filter-has-phone")?.checked &&
      (!hut.phone || hut.phone === "N/A")
    )
      show = false;
    if (
      document.getElementById("filter-has-email")?.checked &&
      (!hut.email || hut.email === "N/A")
    )
      show = false;
    if (
      document.getElementById("filter-has-website")?.checked &&
      (!hut.website || hut.website === "N/A")
    )
      show = false;
    if (
      document.getElementById("filter-has-hours")?.checked &&
      (!hut.opening || hut.opening === "N/A")
    )
      show = false;
    if (
      document.getElementById("filter-has-manager")?.checked &&
      (!hut.manager || hut.manager === "N/A")
    )
      show = false;
    if (
      document.getElementById("filter-has-owner")?.checked &&
      (!hut.owner || hut.owner === "N/A")
    )
      show = false;
    if (
      document.getElementById("filter-has-description")?.checked &&
      (!hut.description || hut.description === "N/A")
    )
      show = false;

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
  const min = document.getElementById("min-altitude").value;
  const max = document.getElementById("max-altitude").value;
  document.getElementById("altitude-range").textContent = `${min} - ${max} m`;
}

function resetFilters() {
  // Reset all checkboxes
  document
    .querySelectorAll(".type-filter, .country-filter")
    .forEach((cb) => (cb.checked = true));
  document.getElementById("filter-all").checked = true;

  // Reset sliders
  document.getElementById("min-altitude").value = 0;
  document.getElementById("max-altitude").value = 4000;
  updateAltitudeRange();

  // Reset capacity
  document.getElementById("min-capacity").value = "";
  document.getElementById("max-capacity").value = "";

  // Reset contact filters
  [
    "phone",
    "email",
    "website",
    "hours",
    "manager",
    "owner",
    "description",
  ].forEach((type) => {
    const el = document.getElementById(`filter-has-${type}`);
    if (el) el.checked = false;
  });

  applyFilters();
}

// Filter presets
function applyFilterPreset(preset) {
  const showMessage = (msg) => {
    if (typeof Toast !== "undefined" && Toast.info) {
      Toast.info(msg, 2000);
    } else {
      showToast(msg);
    }
  };

  switch (preset) {
    case "alps":
      // Alps countries: France, Italy, Switzerland, Austria, Germany, Slovenia
      const alpsCountries = [
        "France",
        "Italy",
        "Switzerland",
        "Austria",
        "Germany",
        "Slovenia",
      ];
      document.querySelectorAll(".country-filter").forEach((cb) => {
        cb.checked = alpsCountries.includes(cb.dataset.country);
      });
      document.getElementById("filter-all").checked = false;
      showMessage("Applied Alps filter");
      break;

    case "with-contact":
      document.getElementById("filter-has-phone").checked = true;
      document.getElementById("filter-has-email").checked = true;
      document.getElementById("filter-has-website").checked = true;
      showMessage("Filtered to huts with contact info");
      break;

    case "high-altitude":
      document.getElementById("min-altitude").value = 2000;
      document.getElementById("max-altitude").value = 4000;
      updateAltitudeRange();
      showMessage("Filtered to high altitude huts (2000m+)");
      break;

    case "reset":
      resetFilters();
      showMessage("Reset all filters");
      return;
  }

  // Apply filters after preset
  applyFilters();
}

// Toggle collapsible filter sections
function toggleFilterSection(header) {
  const section = header.closest(".filter-section");
  const content = section.querySelector(".filter-section-content");
  const icon = header.querySelector(".collapse-icon");

  if (content.style.display === "none") {
    content.style.display = "";
    icon.textContent = "▼";
    section.classList.remove("collapsed");
  } else {
    content.style.display = "none";
    icon.textContent = "▶";
    section.classList.add("collapsed");
  }
}

// ============================================================================
// STATISTICS
// ============================================================================

function updateStats() {
  const visibleMarkers = markers.filter((m) => markerCluster.hasLayer(m));
  const visibleHuts = visibleMarkers.map((m) => m.hutData);

  // Count by type
  const typeCount = {
    mountain_hut: 0,
    bivouac: 0,
    shelter: 0,
  };

  visibleHuts.forEach((h) => {
    const type = (h.type || "unknown").toLowerCase();
    if (type.includes("bivouac") || type.includes("bivvy")) {
      typeCount.bivouac++;
    } else if (type.includes("shelter")) {
      typeCount.shelter++;
    } else if (
      type.includes("hut") ||
      type.includes("refuge") ||
      type.includes("hütte") ||
      type.includes("rifugio")
    ) {
      typeCount.mountain_hut++;
    } else {
      // Unknown types counted as huts
      typeCount.mountain_hut++;
    }
  });

  // Update visible count
  document.getElementById("stats-visible").textContent = visibleHuts.length;
  document.getElementById("stats-total-visible").textContent =
    visibleHuts.length;

  // Update type breakdown
  document.getElementById("stats-huts").textContent = typeCount.mountain_hut;
  document.getElementById("stats-bivouacs").textContent = typeCount.bivouac;
  document.getElementById("stats-shelters").textContent = typeCount.shelter;

  // Countries
  const uniqueCountries = new Set(
    visibleHuts.map((h) => h.country).filter((c) => c && c !== "N/A")
  );
  document.getElementById("stats-countries").textContent = uniqueCountries.size;
  document.getElementById("stats-countries-count").textContent =
    uniqueCountries.size;

  // Altitude
  const altitudes = visibleHuts
    .map((h) => parseInt(h.altitude))
    .filter((a) => !isNaN(a) && a > 0);
  if (altitudes.length > 0) {
    const avgAlt = Math.round(
      altitudes.reduce((a, b) => a + b, 0) / altitudes.length
    );
    const minAlt = Math.min(...altitudes);
    const maxAlt = Math.max(...altitudes);

    document.getElementById("stats-avg-alt").textContent = `${avgAlt}m`;
    document.getElementById("stats-avg-altitude").textContent = `${avgAlt}m`;
    document.getElementById("stats-min-alt").textContent = `${minAlt}m`;
    document.getElementById("stats-max-alt").textContent = `${maxAlt}m`;
  } else {
    document.getElementById("stats-avg-alt").textContent = "0m";
    document.getElementById("stats-avg-altitude").textContent = "N/A";
    document.getElementById("stats-min-alt").textContent = "0m";
    document.getElementById("stats-max-alt").textContent = "0m";
  }

  // Contact info
  const withContact = visibleHuts.filter(
    (h) =>
      (h.phone && h.phone !== "N/A") ||
      (h.email && h.email !== "N/A") ||
      (h.website && h.website !== "N/A")
  ).length;
  document.getElementById("stats-with-contact").textContent = withContact;

  // Total capacity
  const capacities = visibleHuts
    .map((h) => parseInt(h.capacity))
    .filter((c) => !isNaN(c) && c > 0);
  const totalCapacity =
    capacities.length > 0 ? capacities.reduce((a, b) => a + b, 0) : 0;
  document.getElementById("stats-total-capacity").textContent =
    totalCapacity > 0 ? totalCapacity : "N/A";

  // With website
  const withWebsite = visibleHuts.filter(
    (h) => h.website && h.website !== "N/A"
  ).length;
  document.getElementById("stats-with-website").textContent = withWebsite;

  // Open now (placeholder)
  document.getElementById("stats-open-now").textContent = "N/A";

  // Update type distribution chart
  updateTypeDistributionChart(typeCount, visibleHuts.length);
}

// ============================================================================
// SEARCH
// ============================================================================

function initializeSearch(huts) {
  fuse = new Fuse(huts, {
    keys: ["name", "country", "type"],
    threshold: 0.3,
    minMatchCharLength: 2,
  });

  const searchBox = document.getElementById("search-box");
  const searchClear = document.getElementById("search-clear");
  const searchResults = document.getElementById("search-results");

  // Search function (no debouncing)
  const performSearch = function (query) {
    if (query.length === 0) {
      searchResults.classList.remove("visible");
      searchClear.classList.remove("visible");
      return;
    }

    searchClear.classList.add("visible");

    if (query.length < 2) {
      searchResults.innerHTML =
        '<div class="search-no-results">Type at least 2 characters...</div>';
      searchResults.classList.add("visible");
      return;
    }

    const results = fuse.search(query).slice(0, 10);

    if (results.length === 0) {
      searchResults.innerHTML =
        '<div class="search-no-results">No results found</div>';
    } else {
      let html = "";
      results.forEach((result) => {
        const hut = result.item;
        html += `<div class="search-result-item" data-lat="${hut.lat}" data-lon="${hut.lon}">`;
        html += `<div class="search-result-name">${escapeHtml(hut.name)}</div>`;
        html += `<div class="search-result-meta">`;
        if (hut.country && hut.country !== "N/A")
          html += `🌍 ${escapeHtml(hut.country)} • `;
        if (hut.altitude && hut.altitude !== "N/A")
          html += `🏔️ ${escapeHtml(String(hut.altitude))}m • `;
        html += escapeHtml(hut.source);
        html += "</div></div>";
      });
      searchResults.innerHTML = html;

      // Add click handlers
      document.querySelectorAll(".search-result-item").forEach((item) => {
        item.addEventListener("click", function () {
          const lat = parseFloat(this.dataset.lat);
          const lon = parseFloat(this.dataset.lon);
          const hut = allHuts.find((h) => h.lat === lat && h.lon === lon);
          if (hut) {
            showHutDetails(hut);
            searchResults.classList.remove("visible");
            searchBox.value = "";
            searchClear.classList.remove("visible");
          }
        });
      });
    }

    searchResults.classList.add("visible");
  };

  searchBox.addEventListener("input", function (e) {
    const query = e.target.value.trim();
    performSearch(query);
  });

  searchClear.addEventListener("click", function () {
    searchBox.value = "";
    searchResults.classList.remove("visible");
    searchClear.classList.remove("visible");
  });

  // Close search results when clicking outside
  document.addEventListener("click", function (e) {
    if (!searchBox.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.classList.remove("visible");
    }
  });
}

// ============================================================================
// DETAIL SIDEBAR
// ============================================================================

function showHutDetails(hut) {
  const detailSidebar = document.getElementById("detail-sidebar");
  const detailTitle = document.getElementById("detail-hut-name");
  const detailContent = document.getElementById("detail-content");

  // Set title
  detailTitle.textContent = hut.name;

  // Build content
  let content = "<div>";

  // Badges
  content += '<div style="margin-bottom: 20px;">';
  if (hut.altitude && hut.altitude !== "N/A") {
    content += `<span class="detail-badge"><span class="badge-icon">🏔️</span>${escapeHtml(
      String(hut.altitude)
    )} m</span>`;
  }
  if (hut.country && hut.country !== "N/A") {
    content += `<span class="detail-badge"><span class="badge-icon">🌍</span>${escapeHtml(
      hut.country
    )}</span>`;
  }
  if (hut.type && hut.type !== "N/A") {
    content += `<span class="detail-badge"><span class="badge-icon">🏠</span>${escapeHtml(
      hut.type
    )}</span>`;
  }
  content += "</div>";

  // Main Information
  content += '<div class="detail-section"><h3>📋 Main Information</h3>';
  if (hut.capacity && hut.capacity !== "N/A") {
    content += `<div class="detail-info-box"><div class="info-label">Capacity</div><div class="info-value">${escapeHtml(
      String(hut.capacity)
    )} beds</div></div>`;
  }
  if (hut.opening && hut.opening !== "N/A") {
    content += `<div class="detail-info-box"><div class="info-label">Opening Hours</div><div class="info-value">${escapeHtml(
      hut.opening
    )}</div></div>`;
  }
  content += "</div>";

  // Contact
  if (
    (hut.phone && hut.phone !== "N/A") ||
    (hut.email && hut.email !== "N/A") ||
    (hut.website && hut.website !== "N/A")
  ) {
    content += '<div class="detail-section"><h3>📞 Contact</h3>';
    if (hut.phone && hut.phone !== "N/A") {
      content += `<a href="tel:${
        hut.phone
      }" class="detail-button primary">📱 Call: ${escapeHtml(hut.phone)}</a>`;
    }
    if (hut.email && hut.email !== "N/A") {
      content += `<a href="mailto:${hut.email}" class="detail-button secondary">✉️ Email</a>`;
    }
    if (hut.website && hut.website !== "N/A") {
      content += `<a href="${hut.website}" target="_blank" class="detail-button tertiary">🌐 Website</a>`;
    }
    content += "</div>";
  }

  // AI-Generated History (if available)
  if (
    hut.ai_history &&
    hut.ai_history !== "N/A" &&
    hut.ai_history.length > 50
  ) {
    content +=
      '<div class="detail-section" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); padding: 16px; border-radius: 10px; border-left: 4px solid #0ea5e9;">';
    content +=
      '<h3 style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">📖 History & Background</h3>';
    content += `<p style="color: #475569; line-height: 1.7; white-space: pre-wrap;">${escapeHtml(
      hut.ai_history
    )}</p>`;
    content +=
      '<div style="margin-top: 8px; font-size: 10px; color: #64748b; font-style: italic;">✨ AI-generated historical context</div>';
    content += "</div>";
  }

  // Description
  if (
    hut.description &&
    hut.description !== "N/A" &&
    hut.description.length > 10
  ) {
    content += `<div class="detail-section"><h3>ℹ️ Description</h3><p style="color: #475569; line-height: 1.6;">${escapeHtml(
      hut.description
    )}</p></div>`;
  }

  // More Information Link (Original Source) - EXCLUDE mountainhuts.info as it's not working
  if (hut.url && hut.url !== "N/A" && hut.source !== "mountainhuts.info") {
    content += '<div class="detail-section">';
    content += `<a href="${escapeHtml(
      hut.url
    )}" target="_blank" rel="noopener noreferrer" class="detail-button primary" style="font-size: 16px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px;">
      <span>ℹ️</span> More Information <span style="opacity: 0.7;">↗</span>
    </a>`;
    content += "</div>";
  }

  // External Links (Google Maps & Meteoblue)
  content += '<div class="detail-section">';
  content += "<h3>🗺️ External Tools</h3>";

  // Google Maps button - Fixed format for better compatibility
  const googleMapsUrl = `https://www.google.com/maps?q=${hut.lat},${hut.lon}`;
  content += `<a href="${googleMapsUrl}" target="_blank" rel="noopener noreferrer" class="detail-button primary" style="margin-bottom: 8px;">`;
  content += "📍 Open in Google Maps</a>";

  // Meteoblue button - Correct URL format with coordinates (LAT_N/S_LON_E/W format)
  const latDir = hut.lat >= 0 ? "N" : "S";
  const lonDir = hut.lon >= 0 ? "E" : "W";
  const meteoblueUrl = `https://www.meteoblue.com/en/weather/week/${Math.abs(
    hut.lat
  )}${latDir}${Math.abs(hut.lon)}${lonDir}`;
  content += `<a href="${meteoblueUrl}" target="_blank" rel="noopener noreferrer" class="detail-button secondary" style="margin-bottom: 8px;">`;
  content += "🌦️ Detailed Weather (Meteoblue)</a>";

  content += "</div>";

  // Favorites button
  const hutId = `${hut.lat}_${hut.lon}`;
  const isFavorite = FavoritesManager.has(hutId);
  content += '<div class="detail-section">';
  content += "<h3>⭐ Save for Later</h3>";
  content += `<button class="favorite-btn ${
    isFavorite ? "favorited" : ""
  }" id="fav-btn-${hutId}" onclick="toggleFavorite('${hutId}')">`;
  content += isFavorite ? "⭐ Saved to Favorites" : "☆ Add to Favorites";
  content += "</button></div>";

  content += '<div id="weather-container"></div>';
  content += '<div id="nearby-container"></div>';
  content += "</div>";

  detailContent.innerHTML = content;
  detailSidebar.classList.add("open");

  // Center map on hut
  map.setView([hut.lat, hut.lon], 13);

  // Load weather and nearby huts
  if (hut.lat && hut.lon) {
    loadWeather(hut.lat, hut.lon);
    loadNearbyHuts(hut.lat, hut.lon, hut.name);
  }
}

// Back button
document
  .getElementById("back-to-filters")
  .addEventListener("click", function () {
    document.getElementById("detail-sidebar").classList.remove("open");
  });

// Close on Escape key
// Keyboard shortcuts and accessibility
document.addEventListener("keydown", function (e) {
  // Don't trigger shortcuts when typing in inputs
  if (
    e.target.tagName === "INPUT" ||
    e.target.tagName === "TEXTAREA" ||
    e.target.isContentEditable
  ) {
    // Allow Escape to close modals even when typing
    if (e.key === "Escape") {
      const detailSidebar = document.getElementById("detail-sidebar");
      if (detailSidebar && detailSidebar.classList.contains("open")) {
        detailSidebar.classList.remove("open");
        e.preventDefault();
        return;
      }
      const searchResults = document.getElementById("search-results");
      if (searchResults && searchResults.classList.contains("visible")) {
        searchResults.classList.remove("visible");
        const searchBox = document.getElementById("search-box");
        if (searchBox) searchBox.value = "";
        e.preventDefault();
        return;
      }
    }
    return;
  }

  // Focus search box with '/' key
  if (e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey) {
    const searchBox = document.getElementById("search-box");
    if (searchBox) {
      searchBox.focus();
      searchBox.select();
      e.preventDefault();
      return;
    }
  }

  // Escape key - close modals/sidebars
  if (e.key === "Escape") {
    const detailSidebar = document.getElementById("detail-sidebar");
    if (detailSidebar && detailSidebar.classList.contains("open")) {
      detailSidebar.classList.remove("open");
      e.preventDefault();
      return;
    }
    const searchResults = document.getElementById("search-results");
    if (searchResults && searchResults.classList.contains("visible")) {
      searchResults.classList.remove("visible");
      const searchBox = document.getElementById("search-box");
      if (searchBox) searchBox.value = "";
      e.preventDefault();
      return;
    }
    const filterSidebar = document.getElementById("filter-sidebar");
    if (
      filterSidebar &&
      window.innerWidth <= 768 &&
      !filterSidebar.classList.contains("hidden")
    ) {
      filterSidebar.classList.add("hidden");
      e.preventDefault();
      return;
    }
  }

  // Toggle sidebar with 'B' key (for "bar")
  if (
    e.key === "b" &&
    !e.ctrlKey &&
    !e.metaKey &&
    !e.altKey &&
    window.innerWidth > 768
  ) {
    const toggleBtn = document.getElementById("sidebar-toggle-btn");
    if (toggleBtn) {
      toggleBtn.click();
      e.preventDefault();
      return;
    }
  }

  // Switch to filters view with 'F' key
  if (e.key === "f" && !e.ctrlKey && !e.metaKey && !e.altKey) {
    switchSidebarView("filters");
    e.preventDefault();
    return;
  }

  // Switch to favorites view with 'S' key (for "stars")
  if (e.key === "s" && !e.ctrlKey && !e.metaKey && !e.altKey) {
    switchSidebarView("favorites");
    e.preventDefault();
    return;
  }
});

// ============================================================================
// FAVORITES SYSTEM
// ============================================================================

const FavoritesManager = {
  storageKey: "mountainhuts_favorites_v1",

  getAll() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      console.error("Error reading favorites:", e);
      return [];
    }
  },

  save(favorites) {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(favorites));
      return true;
    } catch (e) {
      console.error("Error saving favorites:", e);
      alert("⚠️ Could not save. Browser storage may be full or disabled.");
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
    const filtered = favorites.filter((id) => id !== hutId);
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
      alert(
        "❌ No favorites to export!\n\nClick ⭐ on huts to add them to favorites first."
      );
      return;
    }

    const favoriteHuts = allHuts.filter((hut) =>
      favoriteIds.includes(`${hut.lat}_${hut.lon}`)
    );
    const exportData = {
      exported: new Date().toISOString(),
      version: "1.0",
      count: favoriteHuts.length,
      favorites: favoriteHuts.map((hut) => ({
        id: `${hut.lat}_${hut.lon}`,
        name: hut.name,
        lat: hut.lat,
        lon: hut.lon,
        altitude: hut.altitude,
        country: hut.country,
      })),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `favorite_huts_${favoriteHuts.length}_${
      new Date().toISOString().split("T")[0]
    }.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`📥 Exported ${favoriteHuts.length} favorites!`);
  },

  importJSON() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/json,.json";

    input.onchange = function (e) {
      const file = e.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = function (e) {
        try {
          const imported = JSON.parse(e.target.result);
          if (!imported.favorites || !Array.isArray(imported.favorites)) {
            alert("❌ Invalid file format!");
            return;
          }

          if (
            confirm(
              `Import ${
                imported.favorites.length
              } favorites?\n\nCurrent: ${FavoritesManager.count()} favorites\nWill merge (no duplicates)`
            )
          ) {
            const currentFavs = FavoritesManager.getAll();
            const newFavs = imported.favorites.map((fav) => fav.id);
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
      alert("❌ No favorites!");
      return;
    }

    const favoriteHuts = allHuts.filter((hut) =>
      favoriteIds.includes(`${hut.lat}_${hut.lon}`)
    );
    let gpx =
      '<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.1" creator="LostInTheAlps">\n<metadata><name>Favorite Huts</name></metadata>\n';

    favoriteHuts.forEach((hut) => {
      gpx += `<wpt lat="${hut.lat}" lon="${hut.lon}"><name>${escapeXml(
        hut.name
      )}</name>`;
      if (hut.altitude && hut.altitude !== "N/A")
        gpx += `<ele>${hut.altitude}</ele>`;
      gpx += "</wpt>\n";
    });

    gpx += "</gpx>";

    const blob = new Blob([gpx], { type: "application/gpx+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "favorite_huts.gpx";
    a.click();
    URL.revokeObjectURL(url);
    showToast("📥 Exported to GPX!");
  },
};

function initializeFavorites() {
  updateAllFavoriteCounts();
  renderFavoritesList();
}

function toggleFavorite(hutId) {
  const nowFavorite = FavoritesManager.toggle(hutId);
  const btn = document.getElementById(`fav-btn-${hutId}`);

  if (btn) {
    btn.className = `favorite-btn ${nowFavorite ? "favorited" : ""}`;
    btn.innerHTML = nowFavorite
      ? "⭐ Saved to Favorites"
      : "☆ Add to Favorites";
  }

  updateAllFavoriteCounts();
  renderFavoritesList();
  showToast(nowFavorite ? "⭐ Added to favorites!" : "Removed from favorites");
}

function showFavoritesOnly() {
  const favIds = FavoritesManager.getAll();
  if (favIds.length === 0) {
    showToast("❌ No favorites yet!");
    return;
  }

  let count = 0;
  markers.forEach((marker) => {
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
  markers.forEach((marker) => {
    if (!markerCluster.hasLayer(marker)) markerCluster.addLayer(marker);
  });
  updateStats();
}

// ============================================================================
// WEATHER & NEARBY HUTS
// ============================================================================

// Open-Meteo API - Free, no API key required!
// Documentation: https://open-meteo.com/

function loadWeather(lat, lon) {
  const weatherContainer = document.getElementById("weather-container");
  if (!weatherContainer) return;

  // No caching - always fetch fresh data

  // Show loading state
  weatherContainer.innerHTML = `
        <div class="detail-section">
            <h3>🌤️ Weather Forecast</h3>
            <div style="text-align: center; padding: 20px; color: #64748b;">
                <div style="font-size: 24px; margin-bottom: 8px;">⏳</div>
                <div style="font-size: 12px;">Loading 14-day forecast...</div>
            </div>
        </div>
    `;

  // Open-Meteo API URL with 14-day forecast
  // Includes: temperature, precipitation, wind, weather code
  const apiUrl =
    `https://api.open-meteo.com/v1/forecast?` +
    `latitude=${lat}&longitude=${lon}` +
    `&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m` +
    `&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max` +
    `&timezone=auto` +
    `&forecast_days=14`;

  fetch(apiUrl)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      // Display weather data
      displayWeather(data, weatherContainer, false);
    })
    .catch((error) => {
      console.error("Weather fetch error:", error);

      weatherContainer.innerHTML = `
                <div class="detail-section">
                    <h3>🌤️ Weather</h3>
                    <div style="padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; border-left: 3px solid #ef4444;">
                        <p style="font-size: 12px; color: #991b1b; line-height: 1.6;">
                            <strong>⚠️ Error loading weather:</strong><br>
                            ${escapeHtml(error.message)}
                        </p>
                        <p style="font-size: 11px; color: #64748b; margin-top: 8px; line-height: 1.6;">
                            Could not connect to weather service. Please check your internet connection.
                        </p>
                    </div>
                </div>
            `;
    });
}

// Display weather data
function displayWeather(data, container) {
  const current = data.current;
  const daily = data.daily;

  // Current weather
  const temp = Math.round(current.temperature_2m);
  const feelsLike = Math.round(current.apparent_temperature);
  const humidity = current.relative_humidity_2m;
  const windSpeed = Math.round(current.wind_speed_10m);
  const windDir = getWindDirection(current.wind_direction_10m);
  const weatherCode = current.weather_code;
  const precipitation = current.precipitation || 0;

  // Get weather description and emoji
  const weatherInfo = getWeatherInfo(weatherCode);

  // Build current weather section
  let html = `
                <div class="detail-section">
                    <h3>🌤️ Current Weather</h3>
                    <div style="display: flex; align-items: center; gap: 16px; padding: 12px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 10px; margin-bottom: 12px;">
                        <div style="font-size: 48px; line-height: 1;">${weatherInfo.emoji}</div>
                        <div style="flex: 1;">
                            <div style="font-size: 32px; font-weight: 700; color: #0369a1; line-height: 1;">${temp}°C</div>
                            <div style="font-size: 12px; color: #475569; margin-top: 4px;">${weatherInfo.description}</div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 11px; margin-bottom: 16px;">
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
                            <div style="font-weight: 600; color: #1e293b;">${windSpeed} km/h ${windDir}</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px;">
                            <div style="color: #64748b; margin-bottom: 2px;">Precip.</div>
                            <div style="font-weight: 600; color: #1e293b;">${precipitation} mm</div>
                        </div>
                    </div>
                    
                    <h4 style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 10px;">📅 14-Day Forecast</h4>
                    <div style="display: flex; flex-direction: column; gap: 6px; max-height: 300px; overflow-y: auto;">
            `;

  // Add 14 days of forecast
  for (let i = 0; i < 14; i++) {
    const date = new Date(daily.time[i]);
    const dayName =
      i === 0
        ? "Today"
        : i === 1
        ? "Tomorrow"
        : date.toLocaleDateString("en-US", { weekday: "short" });
    const dateStr = date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });

    const maxTemp = Math.round(daily.temperature_2m_max[i]);
    const minTemp = Math.round(daily.temperature_2m_min[i]);
    const precipSum = daily.precipitation_sum[i] || 0;
    const precipProb = daily.precipitation_probability_max[i] || 0;
    const windMax = Math.round(daily.wind_speed_10m_max[i]);
    const dayWeatherInfo = getWeatherInfo(daily.weather_code[i]);

    // Color code based on conditions
    const isGoodWeather = precipProb < 30 && maxTemp > 10;
    const borderColor = isGoodWeather
      ? "#10b981"
      : precipProb > 70
      ? "#ef4444"
      : "#64748b";

    html += `
                    <div style="display: flex; align-items: center; gap: 10px; padding: 8px; background: #f8fafc; border-radius: 6px; border-left: 3px solid ${borderColor}; font-size: 11px;">
                        <div style="flex: 0 0 70px;">
                            <div style="font-weight: 600; color: #1e293b;">${dayName}</div>
                            <div style="color: #64748b; font-size: 10px;">${dateStr}</div>
                        </div>
                        <div style="font-size: 24px; flex: 0 0 32px; text-align: center;">${
                          dayWeatherInfo.emoji
                        }</div>
                        <div style="flex: 1;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="font-weight: 700; color: #dc2626;">${maxTemp}°</span>
                                    <span style="color: #64748b;"> / </span>
                                    <span style="font-weight: 600; color: #0369a1;">${minTemp}°</span>
                                </div>
                                <div style="color: #64748b;">
                                    ${
                                      precipSum > 0
                                        ? `💧 ${precipSum.toFixed(1)}mm`
                                        : ""
                                    }
                                    ${
                                      precipProb > 30 ? ` (${precipProb}%)` : ""
                                    }
                                </div>
                            </div>
                            <div style="color: #64748b; font-size: 10px; margin-top: 2px;">
                                ${
                                  dayWeatherInfo.description
                                } • 💨 ${windMax} km/h
                            </div>
                        </div>
                    </div>
                `;
  }

  html += `
                    </div>
                    <div style="margin-top: 12px; font-size: 10px; color: #94a3b8; text-align: center;">
                        Data from <a href="https://open-meteo.com/" target="_blank" style="color: #3b82f6;">Open-Meteo.com</a>
                    </div>
                </div>
            `;

  container.innerHTML = html;
}

// Get weather info from WMO weather code
// Full list: https://open-meteo.com/en/docs
function getWeatherInfo(code) {
  const weatherCodes = {
    0: { description: "Clear sky", emoji: "☀️" },
    1: { description: "Mainly clear", emoji: "🌤️" },
    2: { description: "Partly cloudy", emoji: "⛅" },
    3: { description: "Overcast", emoji: "☁️" },
    45: { description: "Foggy", emoji: "🌫️" },
    48: { description: "Depositing rime fog", emoji: "🌫️" },
    51: { description: "Light drizzle", emoji: "🌦️" },
    53: { description: "Moderate drizzle", emoji: "🌦️" },
    55: { description: "Dense drizzle", emoji: "🌧️" },
    56: { description: "Light freezing drizzle", emoji: "🌧️" },
    57: { description: "Dense freezing drizzle", emoji: "🌧️" },
    61: { description: "Slight rain", emoji: "🌧️" },
    63: { description: "Moderate rain", emoji: "🌧️" },
    65: { description: "Heavy rain", emoji: "⛈️" },
    66: { description: "Light freezing rain", emoji: "🌧️" },
    67: { description: "Heavy freezing rain", emoji: "🌧️" },
    71: { description: "Slight snow", emoji: "🌨️" },
    73: { description: "Moderate snow", emoji: "❄️" },
    75: { description: "Heavy snow", emoji: "❄️" },
    77: { description: "Snow grains", emoji: "🌨️" },
    80: { description: "Slight rain showers", emoji: "🌦️" },
    81: { description: "Moderate rain showers", emoji: "🌧️" },
    82: { description: "Violent rain showers", emoji: "⛈️" },
    85: { description: "Slight snow showers", emoji: "🌨️" },
    86: { description: "Heavy snow showers", emoji: "❄️" },
    95: { description: "Thunderstorm", emoji: "⛈️" },
    96: { description: "Thunderstorm with slight hail", emoji: "⛈️" },
    99: { description: "Thunderstorm with heavy hail", emoji: "⛈️" },
  };

  return weatherCodes[code] || { description: "Unknown", emoji: "🌡️" };
}

// Convert wind direction degrees to compass direction
function getWindDirection(degrees) {
  const directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
  const index = Math.round((degrees % 360) / 45) % 8;
  return directions[index];
}

function loadNearbyHuts(lat, lon, currentName) {
  const nearby = allHuts
    .filter((h) => h.name !== currentName)
    .map((h) => ({
      ...h,
      distance: haversineDistance(lat, lon, h.lat, h.lon),
    }))
    .filter((h) => h.distance < 20)
    .sort((a, b) => a.distance - b.distance)
    .slice(0, 5);

  const nearbyContainer = document.getElementById("nearby-container");
  if (nearbyContainer && nearby.length > 0) {
    let html = '<div class="detail-section"><h3>📍 Nearby Huts</h3>';
    nearby.forEach((hut) => {
      html += `<div style="padding: 10px; background: #f8fafc; border-radius: 6px; margin-bottom: 8px; cursor: pointer;" onclick='showHutDetails(${JSON.stringify(
        hut
      )})'>`;
      html += `<div style="font-weight: 600; color: #1e293b;">${escapeHtml(
        hut.name
      )}</div>`;
      html += `<div style="font-size: 12px; color: #64748b;">${hut.distance.toFixed(
        1
      )} km away`;
      if (hut.altitude && hut.altitude !== "N/A")
        html += ` • ${escapeHtml(String(hut.altitude))}m`;
      html += "</div></div>";
    });
    html += "</div>";
    nearbyContainer.innerHTML = html;
  }
}

// ============================================================================
// UTILITIES
// ============================================================================

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function escapeXml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.style.cssText =
    "position: fixed; bottom: 80px; right: 20px; background: #1e293b; color: white; padding: 16px 24px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); z-index: 10000; font-weight: 600;";
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

function exportKML() {
  const visibleHuts = markers
    .filter((m) => markerCluster.hasLayer(m))
    .map((m) => m.hutData);
  if (visibleHuts.length === 0) {
    alert("No huts to export! Please adjust your filters.");
    return;
  }

  let kml =
    '<?xml version="1.0" encoding="UTF-8"?>\n<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n<name>Mountain Huts</name>\n';
  visibleHuts.forEach((hut) => {
    kml += `<Placemark><name>${escapeXml(hut.name)}</name><Point><coordinates>${
      hut.lon
    },${hut.lat},${hut.altitude || 0}</coordinates></Point></Placemark>\n`;
  });
  kml += "</Document>\n</kml>";

  const blob = new Blob([kml], {
    type: "application/vnd.google-earth.kml+xml",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "mountain_huts.kml";
  a.click();
  URL.revokeObjectURL(url);

  alert(`Exported ${visibleHuts.length} huts to KML file!`);
}

// ============================================================================
// MOBILE SUPPORT
// ============================================================================

// Mobile menu toggle
document
  .getElementById("mobile-menu-btn")
  ?.addEventListener("click", function () {
    const sidebar = document.querySelector(".sidebar");
    sidebar.classList.toggle("open");
    this.querySelector(".menu-text").textContent = sidebar.classList.contains(
      "open"
    )
      ? "Close"
      : "Filters";
  });

// Close sidebar on map tap (mobile)
if (window.innerWidth <= 768) {
  map.on("click", function () {
    document.querySelector(".sidebar")?.classList.remove("open");
    document.getElementById("detail-sidebar")?.classList.remove("open");
  });
}

// ============================================================================
// PRESET FILTERS
// ============================================================================
