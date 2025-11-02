// Main JavaScript for Lost in the Alps Website

// Smooth scroll behavior for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Add scroll effect to navbar
let lastScroll = 0;
const navbar = document.querySelector(".navbar");

if (navbar) {
  window.addEventListener("scroll", () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
      navbar.style.boxShadow = "0 4px 6px -1px rgba(0, 0, 0, 0.1)";
    } else {
      navbar.style.boxShadow = "0 10px 15px -3px rgba(0, 0, 0, 0.1)";
    }

    lastScroll = currentScroll;
  });
}

// Animate stats on scroll
const animateStats = () => {
  const statNumbers = document.querySelectorAll(".stat-number");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const target = entry.target;
          const text = target.textContent;

          // Only animate numbers
          if (/^\d+/.test(text)) {
            const finalNumber = parseInt(text.replace(/[^\d]/g, ""));
            animateNumber(target, finalNumber, text);
          }

          observer.unobserve(target);
        }
      });
    },
    { threshold: 0.5 }
  );

  statNumbers.forEach((stat) => observer.observe(stat));
};

function animateNumber(element, target, originalText) {
  const duration = 1500;
  const start = 0;
  const increment = target / (duration / 16);
  let current = start;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = originalText;
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current).toLocaleString() + "+";
    }
  }, 16);
}

// Initialize animations when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  animateStats();

  // Add loaded class for fade-in animations
  document.body.classList.add("loaded");
});

// Performance optimization: Lazy load images if any are added
if ("loading" in HTMLImageElement.prototype) {
  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach((img) => {
    img.src = img.dataset.src;
  });
} else {
  // Fallback for older browsers
  const script = document.createElement("script");
  script.src =
    "https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js";
  document.body.appendChild(script);
}

// Console message for developers
console.log(
  "%c🏔️ Lost in the Alps",
  "font-size: 20px; font-weight: bold; color: #2563eb;"
);
console.log(
  "%cExplore mountain huts across the Alps!",
  "font-size: 14px; color: #6b7280;"
);
console.log(
  "%cData sources: mountainhuts.info, refuges.info, boudy.info",
  "font-size: 12px; color: #9ca3af;"
);
