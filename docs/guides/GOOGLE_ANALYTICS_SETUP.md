# Google Analytics Setup Guide

This document explains how to set up Google Analytics for Lost in the Alps with GDPR-compliant cookie consent.

---

## 🎯 What's Implemented

✅ **GDPR-Compliant Cookie Consent Banner**
- Shows on first visit to any page
- Stores user preference in localStorage
- Only loads Google Analytics after explicit consent
- Mobile-responsive design
- "Accept All" and "Necessary Only" options

✅ **Privacy Policy Page**
- Complete, professional privacy policy
- Explains all data collection
- Lists user rights under GDPR/CCPA
- Accessible at `/privacy-policy.html`

✅ **Cookie Management**
- "Cookie Settings" button in footer
- Users can revoke consent anytime
- Preference persists across visits

✅ **Google Analytics (Conditional Loading)**
- IP anonymization enabled
- Only loads after user consent
- No advertising features
- Secure cookie flags

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Get Your Google Analytics ID

1. Go to [Google Analytics](https://analytics.google.com/)
2. Create a new property (or use existing)
3. Copy your **Measurement ID** (format: `G-XXXXXXXXXX`)

### Step 2: Update the Cookie Consent Script

Open `website/js/cookie-consent.js` and find these two lines (lines ~20 and ~234):

```javascript
gaTrackingId: config.gaTrackingId || 'G-XXXXXXXXXX', // Replace with your GA ID
```

```javascript
window.cookieConsent = new CookieConsent({
  gaTrackingId: 'G-XXXXXXXXXX' // Replace with your actual Google Analytics ID
});
```

**Replace `'G-XXXXXXXXXX'` with your actual Measurement ID** in both places.

For example, if your ID is `G-ABC123XYZ`:
```javascript
gaTrackingId: 'G-ABC123XYZ',
```

### Step 3: Test It

1. Open your website in a private/incognito window
2. You should see the cookie consent banner at the bottom
3. Click "Accept All"
4. Open browser Developer Tools → Network tab
5. Look for requests to `googletagmanager.com` (confirms GA is loaded)
6. Visit Google Analytics dashboard to see real-time data

---

## 📋 Files Modified

### New Files Created:
- `website/js/cookie-consent.js` - Cookie consent manager
- `website/privacy-policy.html` - Privacy policy page
- `GOOGLE_ANALYTICS_SETUP.md` - This file

### Files Updated:
- `website/index.html` - Added cookie consent script
- `tools/create_ultra_simple_map.py` - Added cookie consent to map
- `mountain_huts_map.html` - Generated with cookie consent

---

## 🔍 How It Works

### First Visit (No Consent Yet)
1. User visits website
2. Cookie consent banner appears at bottom
3. Google Analytics **NOT loaded** yet
4. User can browse freely

### User Accepts Cookies
1. User clicks "Accept All"
2. Consent stored in localStorage
3. Google Analytics script loads dynamically
4. Tracking begins (anonymized IP)
5. Banner disappears

### User Rejects Cookies
1. User clicks "Necessary Only"
2. Consent set to `false` in localStorage
3. Google Analytics **never loads**
4. Only necessary cookies stored (consent preference)
5. Banner disappears

### Returning Visitor
1. Script checks localStorage for consent
2. If accepted: Load Google Analytics silently
3. If rejected: Don't load analytics
4. No banner shown (preference remembered)

---

## 🛠️ Testing the Implementation

### Test 1: First Visit Banner
```bash
1. Open browser private/incognito window
2. Go to http://localhost:8080
3. ✅ Cookie banner should appear at bottom
4. ✅ Banner should be styled with blue/white theme
5. ✅ Two buttons: "Accept All" and "Necessary Only"
```

### Test 2: Accept Cookies
```bash
1. Click "Accept All"
2. ✅ Banner disappears smoothly
3. ✅ Toast message: "Cookie preferences saved..."
4. Open DevTools → Application → Local Storage
5. ✅ Should see: lostinthealps_consent = "true"
6. Open DevTools → Network tab
7. ✅ Should see requests to googletagmanager.com
```

### Test 3: Reject Cookies
```bash
1. Clear localStorage
2. Refresh page
3. Click "Necessary Only"
4. ✅ Banner disappears
5. ✅ Toast message appears
6. Check localStorage
7. ✅ Should see: lostinthealps_consent = "false"
8. Check Network tab
9. ✅ NO requests to googletagmanager.com
```

### Test 4: Cookie Settings Button
```bash
1. Scroll to footer
2. ✅ Should see "🍪 Cookie Settings" button
3. Click it
4. ✅ Banner should reappear
5. ✅ Can change preference
```

### Test 5: Mobile Responsive
```bash
1. Open DevTools → Toggle device toolbar (mobile view)
2. ✅ Banner should stack vertically
3. ✅ Buttons should fill width
4. ✅ Text should be readable
5. ✅ No horizontal scrolling
```

### Test 6: Privacy Policy
```bash
1. Go to /privacy-policy.html
2. ✅ Page should load
3. ✅ Content should be formatted nicely
4. ✅ Links should work
5. ✅ Cookie Settings button in footer
```

---

## 🌍 GDPR Compliance Checklist

✅ **Explicit Consent Required**
- Users must actively click "Accept" (not pre-ticked)
- Analytics only loads AFTER consent

✅ **Clear Information**
- What data is collected (explained in banner & policy)
- Why it's collected (improving the website)
- How long it's stored (26 months)

✅ **Easy Opt-Out**
- "Necessary Only" button prominently displayed
- Cookie Settings accessible from footer
- Can revoke consent anytime

✅ **Privacy Policy**
- Complete, legally-sound policy
- Explains all data practices
- Lists user rights (access, deletion, portability)

✅ **IP Anonymization**
- Google Analytics configured with `anonymize_ip: true`
- Last octet of IP address removed

✅ **Secure Cookies**
- SameSite=Lax flag
- Secure flag (HTTPS only)

✅ **Data Retention**
- Google Analytics: 26 months auto-deletion
- localStorage: Can be cleared by user

---

## 📊 Google Analytics Features Enabled

### Enabled:
- ✅ Page views
- ✅ User flow
- ✅ Geographic data (country/city)
- ✅ Device/browser info
- ✅ Traffic sources
- ✅ Session duration
- ✅ Event tracking (map interactions)

### Disabled for Privacy:
- ❌ Google Advertising features
- ❌ Remarketing
- ❌ Demographics reports
- ❌ Interest reports
- ❌ User ID tracking
- ❌ Cross-device tracking

---

## 🔐 Privacy-First Configuration

The Google Analytics implementation uses these privacy settings:

```javascript
gtag('config', 'G-XXXXXXXXXX', {
  'anonymize_ip': true,                    // Remove last IP octet
  'cookie_flags': 'SameSite=Lax;Secure'   // Secure cookies
});
```

**What this means:**
- IP addresses are anonymized before reaching Google
- Cookies can't be accessed by third-party sites
- Cookies only sent over HTTPS

---

## 🎨 Customization Options

### Change Banner Colors
Edit `website/js/cookie-consent.js`, line ~145:

```javascript
.btn-accept {
  background: #2563eb;  // Change this color
  color: white;
}
```

### Change Banner Position
In `cookie-consent.js`, line ~130:
```javascript
#cookie-consent-banner {
  position: fixed;
  bottom: 0;  // Change to 'top: 0' for top banner
}
```

### Change Text
In `cookie-consent.js`, line ~74-82:
```javascript
<h3>We value your privacy</h3>
<p id="cookie-consent-message">
  We use cookies to improve your experience...
</p>
```

---

## 🐛 Troubleshooting

### Analytics Not Loading
**Problem:** Google Analytics not showing in Network tab after accepting cookies

**Solutions:**
1. Check that you replaced `G-XXXXXXXXXX` with your real ID
2. Ensure you're not using an ad blocker
3. Check browser console for errors
4. Verify GA property is active in Google Analytics dashboard

### Banner Not Showing
**Problem:** Cookie consent banner doesn't appear

**Solutions:**
1. Clear localStorage: DevTools → Application → Local Storage → Delete All
2. Refresh page in incognito/private window
3. Check browser console for JavaScript errors
4. Verify `cookie-consent.js` is loading: DevTools → Network → JS

### Consent Not Persisting
**Problem:** Banner appears every time despite accepting

**Solutions:**
1. Check if browser allows localStorage
2. Check if browser is in private mode (localStorage disabled)
3. Verify no browser extension is blocking localStorage

---

## 📈 Viewing Analytics Data

After setting up:

1. Go to [Google Analytics](https://analytics.google.com/)
2. Select your property
3. Navigate to **Reports** → **Realtime** to see live traffic
4. Navigate to **Reports** → **Engagement** → **Pages and screens** for page views
5. Navigate to **Reports** → **User** → **Overview** for demographic data

**Note:** It may take 24-48 hours for full historical data to appear in dashboards.

---

## 📧 Contact & Support

If you encounter issues or have questions:

- Check browser console for errors
- Review this guide carefully
- Open an issue on [GitHub](https://github.com/barcarolol-bit/Mountain-huts-europe/issues)
- Email: hello@lostinthealps.com

---

## ✅ Post-Setup Checklist

After setup, verify:

- [ ] Google Analytics ID updated in `cookie-consent.js` (2 places)
- [ ] Map regenerated with `python tools/create_ultra_simple_map.py`
- [ ] Banner appears on first visit
- [ ] "Accept All" loads Google Analytics
- [ ] "Necessary Only" doesn't load analytics
- [ ] Cookie Settings button in footer
- [ ] Privacy policy page accessible
- [ ] Mobile responsive (test on phone)
- [ ] Google Analytics dashboard shows data (may take 24h)

---

**Your website is now GDPR-compliant with analytics! 🎉**

