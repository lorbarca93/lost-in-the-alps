/**
 * GDPR-Compliant Cookie Consent Manager
 * Handles user consent for analytics cookies and manages Google Analytics
 */

class CookieConsent {
  constructor(config = {}) {
    this.config = {
      gaTrackingId: config.gaTrackingId || 'G-XXXXXXXXXX', // Replace with your GA ID
      cookieName: 'lostinthealps_consent',
      cookieExpireDays: 365,
      privacyPolicyUrl: config.privacyPolicyUrl || 'privacy-policy.html',
      ...config
    };
    
    this.consent = this.loadConsent();
    this.init();
  }
  
  init() {
    // If user hasn't made a choice yet, show banner
    if (this.consent === null) {
      this.showBanner();
    } else if (this.consent === true) {
      // User has consented, load analytics
      this.loadAnalytics();
    }
    
    // Add cookie settings button to footer if it doesn't exist
    this.addCookieSettingsLink();
  }
  
  loadConsent() {
    try {
      const consent = localStorage.getItem(this.config.cookieName);
      if (consent === null) return null;
      return consent === 'true';
    } catch (e) {
      console.warn('Could not access localStorage:', e);
      return null;
    }
  }
  
  saveConsent(accepted) {
    try {
      localStorage.setItem(this.config.cookieName, accepted.toString());
      
      // Also set a cookie for server-side detection if needed
      const expiry = new Date();
      expiry.setDate(expiry.getDate() + this.config.cookieExpireDays);
      document.cookie = `${this.config.cookieName}=${accepted}; expires=${expiry.toUTCString()}; path=/; SameSite=Lax`;
      
      this.consent = accepted;
    } catch (e) {
      console.error('Could not save consent:', e);
    }
  }
  
  showBanner() {
    // Create banner HTML
    const banner = document.createElement('div');
    banner.id = 'cookie-consent-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Cookie Consent');
    banner.setAttribute('aria-describedby', 'cookie-consent-message');
    
    banner.innerHTML = `
      <div class="cookie-consent-container">
        <div class="cookie-consent-content">
          <div class="cookie-consent-icon" aria-hidden="true">🍪</div>
          <div class="cookie-consent-text">
            <h3>We value your privacy</h3>
            <p id="cookie-consent-message">
              We use cookies to improve your experience and analyze site traffic. 
              By clicking "Accept", you consent to our use of analytics cookies.
              <a href="${this.config.privacyPolicyUrl}" target="_blank" rel="noopener">Learn more</a>
            </p>
          </div>
        </div>
        <div class="cookie-consent-actions">
          <button id="cookie-consent-accept" class="btn-consent btn-accept" type="button">
            Accept All
          </button>
          <button id="cookie-consent-necessary" class="btn-consent btn-necessary" type="button">
            Necessary Only
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(banner);
    
    // Add styles
    this.injectStyles();
    
    // Add event listeners
    document.getElementById('cookie-consent-accept').addEventListener('click', () => {
      this.acceptCookies();
    });
    
    document.getElementById('cookie-consent-necessary').addEventListener('click', () => {
      this.rejectCookies();
    });
    
    // Animate in
    setTimeout(() => {
      banner.classList.add('cookie-consent-visible');
    }, 100);
  }
  
  hideBanner() {
    const banner = document.getElementById('cookie-consent-banner');
    if (banner) {
      banner.classList.remove('cookie-consent-visible');
      setTimeout(() => {
        banner.remove();
      }, 300);
    }
  }
  
  acceptCookies() {
    this.saveConsent(true);
    this.hideBanner();
    this.loadAnalytics();
    
    // Show confirmation
    this.showToast('Cookie preferences saved. Analytics enabled.');
  }
  
  rejectCookies() {
    this.saveConsent(false);
    this.hideBanner();
    
    // Show confirmation
    this.showToast('Cookie preferences saved. Only necessary cookies enabled.');
  }
  
  loadAnalytics() {
    // Only load if consent is true and GA ID is set
    if (this.consent !== true || this.config.gaTrackingId === 'G-XXXXXXXXXX') {
      return;
    }
    
    // Load Google Analytics
    const script1 = document.createElement('script');
    script1.async = true;
    script1.src = `https://www.googletagmanager.com/gtag/js?id=${this.config.gaTrackingId}`;
    document.head.appendChild(script1);
    
    const script2 = document.createElement('script');
    script2.textContent = `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '${this.config.gaTrackingId}', {
        'anonymize_ip': true,
        'cookie_flags': 'SameSite=Lax;Secure'
      });
    `;
    document.head.appendChild(script2);
    
    console.log('Google Analytics loaded');
  }
  
  showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'cookie-toast';
    toast.textContent = message;
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.classList.add('cookie-toast-visible');
    }, 10);
    
    setTimeout(() => {
      toast.classList.remove('cookie-toast-visible');
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
  
  addCookieSettingsLink() {
    // Add a "Cookie Settings" link to the footer
    const footer = document.querySelector('footer');
    if (footer && !document.getElementById('cookie-settings-link')) {
      const settingsLink = document.createElement('button');
      settingsLink.id = 'cookie-settings-link';
      settingsLink.className = 'cookie-settings-link';
      settingsLink.textContent = '🍪 Cookie Settings';
      settingsLink.type = 'button';
      settingsLink.addEventListener('click', () => {
        this.showBanner();
      });
      
      // Insert before last element in footer (usually "Back to top")
      const footerInner = footer.querySelector('.footer-inner, .container');
      if (footerInner) {
        footerInner.insertBefore(settingsLink, footerInner.lastElementChild);
      } else {
        footer.appendChild(settingsLink);
      }
    }
  }
  
  injectStyles() {
    if (document.getElementById('cookie-consent-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'cookie-consent-styles';
    style.textContent = `
      #cookie-consent-banner {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(12px);
        border-top: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow: 0 -4px 20px rgba(15, 23, 42, 0.1);
        transform: translateY(100%);
        transition: transform 0.3s ease;
        padding: 20px;
      }
      
      #cookie-consent-banner.cookie-consent-visible {
        transform: translateY(0);
      }
      
      .cookie-consent-container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        flex-wrap: wrap;
      }
      
      .cookie-consent-content {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        flex: 1;
        min-width: 300px;
      }
      
      .cookie-consent-icon {
        font-size: 32px;
        line-height: 1;
        flex-shrink: 0;
      }
      
      .cookie-consent-text h3 {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 600;
        color: #1e293b;
      }
      
      .cookie-consent-text p {
        margin: 0;
        font-size: 14px;
        line-height: 1.5;
        color: #475569;
      }
      
      .cookie-consent-text a {
        color: #2563eb;
        text-decoration: underline;
        transition: color 0.2s;
      }
      
      .cookie-consent-text a:hover {
        color: #1d4ed8;
      }
      
      .cookie-consent-actions {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
      }
      
      .btn-consent {
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
        white-space: nowrap;
      }
      
      .btn-accept {
        background: #2563eb;
        color: white;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
      }
      
      .btn-accept:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
      }
      
      .btn-necessary {
        background: white;
        color: #475569;
        border: 2px solid #cbd5e1;
      }
      
      .btn-necessary:hover {
        background: #f8fafc;
        border-color: #94a3b8;
      }
      
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
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        opacity: 0;
        transition: all 0.3s;
        z-index: 1000000;
        max-width: 90%;
      }
      
      .cookie-toast-visible {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }
      
      .cookie-settings-link {
        background: none;
        border: none;
        color: #64748b;
        font-size: 14px;
        cursor: pointer;
        padding: 4px 8px;
        transition: color 0.2s;
        text-decoration: none;
      }
      
      .cookie-settings-link:hover {
        color: #2563eb;
      }
      
      /* Mobile responsive */
      @media (max-width: 768px) {
        #cookie-consent-banner {
          padding: 16px;
        }
        
        .cookie-consent-container {
          flex-direction: column;
          align-items: stretch;
        }
        
        .cookie-consent-content {
          min-width: 100%;
        }
        
        .cookie-consent-actions {
          width: 100%;
        }
        
        .btn-consent {
          flex: 1;
          justify-content: center;
        }
        
        .cookie-consent-text h3 {
          font-size: 16px;
        }
        
        .cookie-consent-text p {
          font-size: 13px;
        }
      }
    `;
    
    document.head.appendChild(style);
  }
  
  // Public API for managing consent
  revokeConsent() {
    this.saveConsent(false);
    this.showToast('Analytics disabled. Please refresh the page.');
  }
  
  hasConsent() {
    return this.consent === true;
  }
  
  getConsentStatus() {
    if (this.consent === null) return 'pending';
    return this.consent ? 'accepted' : 'rejected';
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.cookieConsent = new CookieConsent({
      gaTrackingId: 'G-XXXXXXXXXX' // Replace with your actual Google Analytics ID
    });
  });
} else {
  window.cookieConsent = new CookieConsent({
    gaTrackingId: 'G-XXXXXXXXXX' // Replace with your actual Google Analytics ID
  });
}

