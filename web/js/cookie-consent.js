/**
 * Cookie Consent Manager
 * GDPR-compliant cookie consent for Lost in the Alps
 * 
 * Features:
 * - Shows consent banner on first visit
 * - Stores preferences in localStorage
 * - Only loads analytics after consent
 * - Allows changing preferences anytime
 */

(function() {
  'use strict';

  const CONSENT_KEY = 'cookie_consent';
  const CONSENT_VERSION = '1.0';
  
  // Google Analytics ID (replace with your actual ID)
  const GA_ID = 'G-XXXXXXXXXX'; // TODO: Add your Google Analytics ID
  
  /**
   * Get stored consent preferences
   */
  function getConsent() {
    try {
      const stored = localStorage.getItem(CONSENT_KEY);
      if (stored) {
        const consent = JSON.parse(stored);
        // Check if consent version matches
        if (consent.version === CONSENT_VERSION) {
          return consent;
        }
      }
    } catch (e) {
      console.warn('Could not read cookie consent:', e);
    }
    return null;
  }

  /**
   * Save consent preferences
   */
  function saveConsent(analytics) {
    const consent = {
      version: CONSENT_VERSION,
      analytics: analytics,
      timestamp: new Date().toISOString()
    };
    try {
      localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));
    } catch (e) {
      console.warn('Could not save cookie consent:', e);
    }
    return consent;
  }

  /**
   * Load Google Analytics (only if consented)
   */
  function loadAnalytics() {
    if (GA_ID === 'G-XXXXXXXXXX') {
      console.log('📊 Analytics: No GA ID configured');
      return;
    }

    // Check if already loaded
    if (window.gtag) return;

    // Load gtag.js
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
    document.head.appendChild(script);

    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA_ID, {
      'anonymize_ip': true,
      'cookie_flags': 'SameSite=Lax;Secure'
    });

    console.log('📊 Analytics loaded');
  }

  /**
   * Remove analytics cookies
   */
  function removeAnalytics() {
    // Remove Google Analytics cookies
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const name = cookie.split('=')[0].trim();
      if (name.startsWith('_ga') || name.startsWith('_gid') || name.startsWith('_gat')) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${window.location.hostname};`;
      }
    }
    console.log('📊 Analytics cookies removed');
  }

  /**
   * Create and show the cookie consent banner
   */
  function showBanner() {
    // Don't show if banner already exists
    if (document.getElementById('cookie-consent-banner')) return;

    const banner = document.createElement('div');
    banner.id = 'cookie-consent-banner';
    banner.innerHTML = `
      <div class="cookie-consent-content">
        <div class="cookie-consent-text">
          <span class="cookie-icon">🍪</span>
          <p>We use cookies to analyze site usage and improve your experience. 
             <a href="privacy-policy.html" target="_blank">Learn more</a></p>
        </div>
        <div class="cookie-consent-buttons">
          <button id="cookie-reject" class="cookie-btn cookie-btn-secondary">Reject</button>
          <button id="cookie-accept" class="cookie-btn cookie-btn-primary">Accept</button>
        </div>
      </div>
    `;

    document.body.appendChild(banner);

    // Animate in
    requestAnimationFrame(() => {
      banner.classList.add('visible');
    });

    // Event listeners
    document.getElementById('cookie-accept').addEventListener('click', () => {
      acceptCookies();
      hideBanner();
    });

    document.getElementById('cookie-reject').addEventListener('click', () => {
      rejectCookies();
      hideBanner();
    });
  }

  /**
   * Hide the consent banner
   */
  function hideBanner() {
    const banner = document.getElementById('cookie-consent-banner');
    if (banner) {
      banner.classList.remove('visible');
      setTimeout(() => banner.remove(), 300);
    }
  }

  /**
   * Accept cookies and load analytics
   */
  function acceptCookies() {
    saveConsent(true);
    loadAnalytics();
    showToast('✓ Preferences saved');
  }

  /**
   * Reject cookies and remove analytics
   */
  function rejectCookies() {
    saveConsent(false);
    removeAnalytics();
    showToast('✓ Preferences saved');
  }

  /**
   * Show a toast notification
   */
  function showToast(message) {
    // Use existing toast function if available
    if (typeof window.showToast === 'function') {
      window.showToast(message);
      return;
    }

    // Create simple toast
    const toast = document.createElement('div');
    toast.className = 'cookie-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => {
      toast.classList.remove('visible');
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }

  /**
   * Add Cookie Settings button to footer
   */
  function addSettingsButton() {
    const footer = document.querySelector('.footer-bar');
    if (!footer) return;

    // Check if button already exists
    if (document.getElementById('cookie-settings-btn')) return;

    const divider = document.createElement('span');
    divider.className = 'footer-divider';
    divider.textContent = '|';

    const button = document.createElement('a');
    button.id = 'cookie-settings-btn';
    button.href = '#';
    button.textContent = 'Cookie Settings';
    button.addEventListener('click', (e) => {
      e.preventDefault();
      showSettingsModal();
    });

    footer.appendChild(divider);
    footer.appendChild(button);
  }

  /**
   * Show cookie settings modal
   */
  function showSettingsModal() {
    // Remove existing modal
    const existing = document.getElementById('cookie-settings-modal');
    if (existing) existing.remove();

    const consent = getConsent();
    const analyticsEnabled = consent ? consent.analytics : false;

    const modal = document.createElement('div');
    modal.id = 'cookie-settings-modal';
    modal.innerHTML = `
      <div class="cookie-modal-backdrop"></div>
      <div class="cookie-modal-content">
        <div class="cookie-modal-header">
          <h3>🍪 Cookie Settings</h3>
          <button class="cookie-modal-close" aria-label="Close">✕</button>
        </div>
        <div class="cookie-modal-body">
          <div class="cookie-option">
            <div class="cookie-option-info">
              <strong>Essential Cookies</strong>
              <p>Required for the website to function. Cannot be disabled.</p>
            </div>
            <label class="cookie-toggle disabled">
              <input type="checkbox" checked disabled>
              <span class="cookie-toggle-slider"></span>
            </label>
          </div>
          <div class="cookie-option">
            <div class="cookie-option-info">
              <strong>Analytics Cookies</strong>
              <p>Help us understand how visitors use our site (Google Analytics with anonymized IP).</p>
            </div>
            <label class="cookie-toggle">
              <input type="checkbox" id="analytics-toggle" ${analyticsEnabled ? 'checked' : ''}>
              <span class="cookie-toggle-slider"></span>
            </label>
          </div>
        </div>
        <div class="cookie-modal-footer">
          <button id="cookie-save-settings" class="cookie-btn cookie-btn-primary">Save Settings</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Animate in
    requestAnimationFrame(() => modal.classList.add('visible'));

    // Event listeners
    modal.querySelector('.cookie-modal-backdrop').addEventListener('click', closeModal);
    modal.querySelector('.cookie-modal-close').addEventListener('click', closeModal);
    modal.querySelector('#cookie-save-settings').addEventListener('click', () => {
      const analyticsChecked = document.getElementById('analytics-toggle').checked;
      if (analyticsChecked) {
        acceptCookies();
      } else {
        rejectCookies();
      }
      closeModal();
    });

    // Close on Escape
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        closeModal();
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);

    function closeModal() {
      modal.classList.remove('visible');
      setTimeout(() => modal.remove(), 300);
    }
  }

  /**
   * Inject required CSS styles
   */
  function injectStyles() {
    if (document.getElementById('cookie-consent-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'cookie-consent-styles';
    styles.textContent = `
      /* Cookie Consent Banner */
      #cookie-consent-banner {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #1e293b;
        color: white;
        padding: 0;
        z-index: 100000;
        transform: translateY(100%);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
      }

      #cookie-consent-banner.visible {
        transform: translateY(0);
      }

      .cookie-consent-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
      }

      .cookie-consent-text {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
      }

      .cookie-icon {
        font-size: 24px;
        flex-shrink: 0;
      }

      .cookie-consent-text p {
        margin: 0;
        font-size: 14px;
        line-height: 1.5;
        color: #e2e8f0;
      }

      .cookie-consent-text a {
        color: #60a5fa;
        text-decoration: none;
      }

      .cookie-consent-text a:hover {
        text-decoration: underline;
      }

      .cookie-consent-buttons {
        display: flex;
        gap: 10px;
        flex-shrink: 0;
      }

      .cookie-btn {
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: all 0.15s ease;
        font-family: inherit;
      }

      .cookie-btn-primary {
        background: #3b82f6;
        color: white;
      }

      .cookie-btn-primary:hover {
        background: #2563eb;
      }

      .cookie-btn-secondary {
        background: transparent;
        color: #94a3b8;
        border: 1px solid #475569;
      }

      .cookie-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
      }

      /* Cookie Toast */
      .cookie-toast {
        position: fixed;
        bottom: 100px;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        background: #1e293b;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        opacity: 0;
        transition: all 0.3s ease;
        z-index: 100001;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      }

      .cookie-toast.visible {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }

      /* Cookie Settings Modal */
      #cookie-settings-modal {
        position: fixed;
        inset: 0;
        z-index: 100002;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      #cookie-settings-modal.visible {
        opacity: 1;
      }

      .cookie-modal-backdrop {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
      }

      .cookie-modal-content {
        position: relative;
        background: white;
        border-radius: 12px;
        width: 90%;
        max-width: 480px;
        max-height: 90vh;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        transform: scale(0.95);
        transition: transform 0.3s ease;
      }

      #cookie-settings-modal.visible .cookie-modal-content {
        transform: scale(1);
      }

      .cookie-modal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 18px 20px;
        background: #1e293b;
        color: white;
      }

      .cookie-modal-header h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
      }

      .cookie-modal-close {
        background: rgba(255, 255, 255, 0.1);
        border: none;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.15s ease;
      }

      .cookie-modal-close:hover {
        background: rgba(255, 255, 255, 0.2);
      }

      .cookie-modal-body {
        padding: 20px;
      }

      .cookie-option {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 16px;
        padding: 16px 0;
        border-bottom: 1px solid #e5e7eb;
      }

      .cookie-option:last-child {
        border-bottom: none;
      }

      .cookie-option-info {
        flex: 1;
      }

      .cookie-option-info strong {
        display: block;
        font-size: 14px;
        color: #1e293b;
        margin-bottom: 4px;
      }

      .cookie-option-info p {
        margin: 0;
        font-size: 13px;
        color: #6b7280;
        line-height: 1.5;
      }

      /* Toggle Switch */
      .cookie-toggle {
        position: relative;
        display: inline-block;
        width: 48px;
        height: 26px;
        flex-shrink: 0;
      }

      .cookie-toggle input {
        opacity: 0;
        width: 0;
        height: 0;
      }

      .cookie-toggle-slider {
        position: absolute;
        cursor: pointer;
        inset: 0;
        background: #d1d5db;
        border-radius: 26px;
        transition: background 0.2s ease;
      }

      .cookie-toggle-slider::before {
        content: "";
        position: absolute;
        height: 20px;
        width: 20px;
        left: 3px;
        bottom: 3px;
        background: white;
        border-radius: 50%;
        transition: transform 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
      }

      .cookie-toggle input:checked + .cookie-toggle-slider {
        background: #3b82f6;
      }

      .cookie-toggle input:checked + .cookie-toggle-slider::before {
        transform: translateX(22px);
      }

      .cookie-toggle.disabled .cookie-toggle-slider {
        background: #9ca3af;
        cursor: not-allowed;
      }

      .cookie-modal-footer {
        padding: 16px 20px;
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
        display: flex;
        justify-content: flex-end;
      }

      /* Mobile Responsive */
      @media (max-width: 640px) {
        .cookie-consent-content {
          flex-direction: column;
          text-align: center;
          padding: 16px;
          gap: 16px;
        }

        .cookie-consent-text {
          flex-direction: column;
          gap: 8px;
        }

        .cookie-consent-buttons {
          width: 100%;
        }

        .cookie-btn {
          flex: 1;
          padding: 12px 16px;
        }

        .cookie-modal-content {
          width: 95%;
          margin: 20px;
        }
      }
    `;

    document.head.appendChild(styles);
  }

  /**
   * Initialize cookie consent
   */
  function init() {
    // Inject styles
    injectStyles();

    // Add settings button to footer
    addSettingsButton();

    // Check existing consent
    const consent = getConsent();

    if (consent === null) {
      // No consent yet, show banner
      // Delay slightly to let page load
      setTimeout(showBanner, 1000);
    } else if (consent.analytics) {
      // User accepted analytics
      loadAnalytics();
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose functions globally for external use
  window.CookieConsent = {
    showBanner: showBanner,
    showSettings: showSettingsModal,
    accept: acceptCookies,
    reject: rejectCookies,
    getConsent: getConsent
  };

})();
