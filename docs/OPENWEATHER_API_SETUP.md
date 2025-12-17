# 🌤️ Weather Widget Setup Guide

## Overview
The weather widget displays real-time weather data for mountain huts using the OpenWeatherMap API.

---

## 🔑 Getting Your Free API Key

### Step 1: Sign Up
1. Visit https://openweathermap.org/api
2. Click "Sign Up" in the top right
3. Create a free account
4. Verify your email address

### Step 2: Get API Key
1. Log in to your account
2. Go to "API keys" section
3. Your default API key will be shown
4. Copy the API key (it looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

### Step 3: Activate API Key
⚠️ **Important**: New API keys take **~2 hours** to activate!
- You'll get a 401 error if you try to use it immediately
- Wait 2 hours after creation before testing

---

## 🔧 Adding the API Key to Your Website

### Option 1: Direct Edit (Recommended for Local Development)
1. Open `website/js/map-app.js`
2. Find this line (around line 896):
   ```javascript
   const OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE';
   ```
3. Replace `YOUR_API_KEY_HERE` with your actual API key:
   ```javascript
   const OPENWEATHER_API_KEY = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6';
   ```
4. Save the file

### Option 2: Environment Variable (Recommended for Production)
If you're deploying to a server, use environment variables:

**For Netlify:**
1. Go to your site settings
2. Navigate to "Environment variables"
3. Add: `OPENWEATHER_API_KEY` = `your_api_key_here`
4. Update your build process to inject it

**For other hosts:**
- Follow your hosting provider's documentation for setting environment variables

---

## ✅ Testing the Weather Widget

1. **Start local server:**
   ```bash
   python -m http.server 8000
   ```

2. **Open the website:**
   - Navigate to http://localhost:8000/mountain_huts_map.html

3. **Click on any mountain hut marker**
   - The detail sidebar should open
   - Scroll down to see the weather widget

4. **What you should see:**
   - ✅ **With API key**: Current temperature, weather description, humidity, wind speed
   - ⚠️ **Without API key**: Setup instructions
   - ❌ **With invalid key**: Error message with troubleshooting tips

---

## 🌤️ Weather Data Displayed

The widget shows:
- **Current Temperature** (°C)
- **"Feels Like" Temperature**
- **Weather Condition** (with emoji: ☀️🌧️❄️⛈️)
- **Humidity** (%)
- **Wind Speed** (km/h)
- **Atmospheric Pressure** (hPa)

---

## 🚨 Common Issues & Solutions

### Issue 1: "401 Unauthorized" Error
**Cause**: API key is invalid or not activated yet

**Solution**:
- Wait 2 hours after creating the API key
- Double-check you copied the key correctly (no extra spaces)
- Verify the key is active in your OpenWeatherMap dashboard

### Issue 2: "429 Too Many Requests" Error
**Cause**: You've exceeded the free tier rate limit (60 calls/minute, 1,000,000 calls/month)

**Solution**:
- Wait a minute and try again
- The free tier is usually sufficient for normal use
- Consider caching weather data if needed

### Issue 3: Weather not loading
**Cause**: Network issues or CORS problems

**Solution**:
- Check browser console for errors (F12)
- Ensure you're accessing the site via http:// or https:// (not file://)
- Test the API directly: https://api.openweathermap.org/data/2.5/weather?lat=46.5&lon=8.0&units=metric&appid=YOUR_KEY

### Issue 4: "Setup Required" message still showing
**Cause**: API key not added correctly

**Solution**:
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh the page (Ctrl+F5)
- Check that you saved the `map-app.js` file
- Restart your local server

---

## 📊 API Rate Limits (Free Tier)

| Limit Type | Free Tier |
|------------|-----------|
| Calls per minute | 60 |
| Calls per month | 1,000,000 |
| Data update frequency | 10 minutes |
| Historical data | No |
| Forecasts | No (Current weather only) |

---

## 🔐 Security Best Practices

### For Public Repositories (GitHub):
⚠️ **DO NOT** commit your API key to public repositories!

**Safe approach:**
1. Add `website/js/map-app.js` to `.gitignore` if it contains the key
2. Create a separate config file that's gitignored
3. Use environment variables for production

**Example `.gitignore` entry:**
```
# API keys - do not commit
website/js/config.js
.env
```

### For Production Deployment:
- Use environment variables
- Implement server-side API calls to hide the key
- Consider implementing caching to reduce API calls
- Monitor your API usage in the OpenWeatherMap dashboard

---

## 🎨 Customizing the Weather Widget

### Change Temperature Units
In `map-app.js`, modify the API URL:
```javascript
// For Fahrenheit:
const apiUrl = `...&units=imperial&appid=...`;

// For Kelvin (default):
const apiUrl = `...&appid=...`; // Remove &units parameter
```

### Modify Widget Styling
The weather widget uses inline styles. You can:
1. Extract styles to `styles.css`
2. Create a `.weather-widget` class
3. Customize colors, sizes, layout

### Add More Weather Data
OpenWeatherMap provides additional data:
- Visibility
- Cloudiness percentage
- Rain/snow volume
- Sunrise/sunset times

Check the API documentation at: https://openweathermap.org/current

---

## 📚 Additional Resources

- **OpenWeatherMap API Docs**: https://openweathermap.org/api
- **Current Weather Data**: https://openweathermap.org/current
- **API Dashboard**: https://home.openweathermap.org/api_keys
- **Support**: https://openweathermap.org/faq

---

## ✅ Verification Checklist

Before marking setup as complete:

- [ ] Created OpenWeatherMap account
- [ ] Obtained API key
- [ ] Waited 2 hours for activation
- [ ] Added key to `map-app.js`
- [ ] Tested on localhost
- [ ] Weather widget shows data correctly
- [ ] No console errors
- [ ] Committed changes (without exposing API key if public repo)

---

**Need Help?**
- Check the browser console (F12) for detailed error messages
- Verify your API key status at https://home.openweathermap.org/api_keys
- Review OpenWeatherMap FAQ: https://openweathermap.org/faq

