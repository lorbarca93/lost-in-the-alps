// Simple Utility Functions for Lost in the Alps Map
// Simplified version without complex optimizations

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

/**
 * Toast notification system
 */
const Toast = {
  /**
   * Show a toast notification
   * @param {string} message - Message to display
   * @param {string} type - Type: 'success', 'error', 'info', 'warning'
   * @param {number} duration - Duration in milliseconds
   */
  show(message, type = "info", duration = 3000) {
    // Remove existing toasts
    const existing = document.querySelectorAll(".toast");
    existing.forEach((toast) => toast.remove());

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "polite");

    const icon =
      {
        success: "✅",
        error: "❌",
        warning: "⚠️",
        info: "ℹ️",
      }[type] || "ℹ️";

    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-message">${escapeHtml(message)}</span>
      <button class="toast-close" aria-label="Close">×</button>
    `;

    // Add styles if not already added
    if (!document.getElementById("toast-styles")) {
      const style = document.createElement("style");
      style.id = "toast-styles";
      style.textContent = `
        .toast {
          position: fixed;
          top: 20px;
          right: 20px;
          background: white;
          color: #1e293b;
          padding: 16px 20px;
          border-radius: 8px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
          z-index: 10000;
          display: flex;
          align-items: center;
          gap: 12px;
          min-width: 300px;
          max-width: 500px;
          animation: toastSlideIn 0.3s ease-out;
          border-left: 4px solid;
        }
        .toast-success { border-left-color: #10b981; }
        .toast-error { border-left-color: #ef4444; }
        .toast-warning { border-left-color: #f59e0b; }
        .toast-info { border-left-color: #3b82f6; }
        .toast-icon { font-size: 20px; }
        .toast-message { flex: 1; font-size: 14px; line-height: 1.5; }
        .toast-close {
          background: none;
          border: none;
          font-size: 24px;
          color: #64748b;
          cursor: pointer;
          padding: 0;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          line-height: 1;
        }
        .toast-close:hover { color: #1e293b; }
        @keyframes toastSlideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        @keyframes toastSlideOut {
          from {
            transform: translateX(0);
            opacity: 1;
          }
          to {
            transform: translateX(100%);
            opacity: 0;
          }
        }
        .toast-removing {
          animation: toastSlideOut 0.3s ease-out forwards;
        }
      `;
      document.head.appendChild(style);
    }

    document.body.appendChild(toast);

    // Close button
    toast.querySelector(".toast-close").addEventListener("click", () => {
      this.remove(toast);
    });

    // Auto remove
    if (duration > 0) {
      setTimeout(() => this.remove(toast), duration);
    }

    return toast;
  },

  /**
   * Remove toast
   * @param {HTMLElement} toast - Toast element to remove
   */
  remove(toast) {
    if (toast && toast.parentNode) {
      toast.classList.add("toast-removing");
      setTimeout(() => {
        if (toast.parentNode) {
          toast.remove();
        }
      }, 300);
    }
  },

  success(message, duration) {
    return this.show(message, "success", duration);
  },

  error(message, duration) {
    return this.show(message, "error", duration || 5000);
  },

  warning(message, duration) {
    return this.show(message, "warning", duration);
  },

  info(message, duration) {
    return this.show(message, "info", duration);
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Format number with thousand separators
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Check if device is mobile
 * @returns {boolean} True if mobile device
 */
function isMobile() {
  return (
    window.innerWidth <= 768 ||
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    )
  );
}
