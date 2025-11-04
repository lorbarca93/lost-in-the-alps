// Main JavaScript for Lost in the Alps website

// Smooth scroll for in-page navigation
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", (event) => {
    const hash = anchor.getAttribute("href");
    if (!hash || hash === "#") return;

    const target = document.querySelector(hash);
    if (!target) return;

    event.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

// Elevate navbar on scroll
const navbar = document.querySelector(".navbar");
if (navbar) {
  window.addEventListener("scroll", () => {
    const isElevated = window.scrollY > 24;
    navbar.classList.toggle("is-elevated", isElevated);
  });
}

// Reveal-on-scroll animations
const revealElements = document.querySelectorAll(".reveal-on-scroll");
if (revealElements.length) {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.4, rootMargin: "0px 0px -10% 0px" }
  );

  revealElements.forEach((element) => revealObserver.observe(element));
}

// Load real statistics from API
async function loadRealStats() {
  try {
    const response = await fetch('api/stats.json');
    const stats = await response.json();
    
    // Update stat numbers with real data
    const statElements = document.querySelectorAll('.stat-number');
    if (statElements.length >= 4) {
      statElements[0].dataset.value = stats.total_huts;
      statElements[1].dataset.value = stats.countries_count;
      statElements[2].dataset.value = stats.sources_count;
      statElements[3].dataset.value = stats.with_details_percent;
    }
    
    // Create country chart
    if (stats.by_country) {
      createCountryChart(stats.by_country);
    }
    
    return stats;
  } catch (error) {
    console.error('Error loading statistics:', error);
    return null;
  }
}

// Create a simple bar chart for countries
function createCountryChart(countries) {
  const chartContainer = document.getElementById('country-chart');
  if (!chartContainer) return;
  
  // Take top 15 countries
  const topCountries = countries.slice(0, 15);
  if (topCountries.length === 0) {
    chartContainer.innerHTML = '<p style="color: #64748b; text-align: center;">No data available</p>';
    return;
  }
  
  const maxCount = Math.max(...topCountries.map(c => c.count));
  
  chartContainer.innerHTML = topCountries.map(country => {
    const percentage = (country.count / maxCount) * 100;
    const escapedCountry = country.country.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return `
      <div style="margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 14px;">
          <span style="color: #1e293b; font-weight: 500;">${escapedCountry}</span>
          <span style="color: #64748b;">${country.count} huts</span>
        </div>
        <div style="width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
          <div style="width: ${percentage}%; height: 100%; background: #2563eb; transition: width 0.6s ease;"></div>
        </div>
      </div>
    `;
  }).join('');
}

// Stat counter animation
const statNumbers = document.querySelectorAll(".stat-number");
if (statNumbers.length) {
  // Load real stats first
  loadRealStats().then(() => {
    const counterObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          animateNumber(entry.target);
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.6 }
    );

    statNumbers.forEach((element) => counterObserver.observe(element));
  });
}

function animateNumber(element) {
  const targetValue = Number(element.dataset.value || 0);
  const suffix = element.dataset.suffix || "";
  const prefix = element.dataset.prefix || "";
  const duration = Number(element.dataset.duration || 1400);

  if (!Number.isFinite(targetValue) || targetValue <= 0) {
    element.textContent = `${prefix}${targetValue}${suffix}`;
    return;
  }

  const frameDuration = 1000 / 60;
  const totalFrames = Math.round(duration / frameDuration);
  let frame = 0;

  const counter = () => {
    frame += 1;
    const progress = Math.min(frame / totalFrames, 1);
    const easedProgress = easeOutCubic(progress);
    const currentValue = Math.round(targetValue * easedProgress);

    element.textContent = `${prefix}${currentValue.toLocaleString()}${suffix}`;

    if (progress < 1) {
      window.requestAnimationFrame(counter);
    }
  };

  window.requestAnimationFrame(counter);
}

function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

// Map loading indicator
document.addEventListener("DOMContentLoaded", () => {
  const mapFrame = document.querySelector(".map-wrapper iframe");
  const mapLoading = document.getElementById("map-loading");

  if (mapFrame && mapLoading) {
    const hideLoader = () => mapLoading.classList.add("is-hidden");
    const fallbackTimer = window.setTimeout(hideLoader, 4000);

    mapFrame.addEventListener(
      "load",
      () => {
        window.clearTimeout(fallbackTimer);
        hideLoader();
      },
      { once: true }
    );
  }

  document.body.classList.add("loaded");
});

// Graceful lazy-loading support for future images
if ("loading" in HTMLImageElement.prototype) {
  document.querySelectorAll('img[loading="lazy"]').forEach((img) => {
    if (img.dataset.src) {
      img.src = img.dataset.src;
    }
  });
} else {
  const script = document.createElement("script");
  script.src = "https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js";
  script.defer = true;
  document.head.appendChild(script);
}

// Console message for curious developers
console.log("%cLost in the Alps", "font-size:18px;font-weight:600;color:#2563eb;");
console.log("%cOpen data for mountain hut explorers.", "font-size:13px;color:#475569;");
