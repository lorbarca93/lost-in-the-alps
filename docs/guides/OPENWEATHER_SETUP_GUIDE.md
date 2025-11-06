# OpenWeatherMap API Setup - Quick Guide

**Time Required**: 5 minutes  
**Cost**: Free (1,000 calls/day)  
**Difficulty**: Easy

---

## 🎯 **Why You Need This**

The weather widget shows **real-time weather conditions** in every hut popup:
- Current temperature (°C)
- Weather conditions (sunny, cloudy, rain, snow)
- Weather icon
- Link to 5-day forecast

**Without API key:** Shows fallback link to weather map (still functional)  
**With API key:** Beautiful embedded weather widget in every popup! 🌤️

---

## 🚀 **5-Minute Setup**

### **Step 1: Create Free Account** (2 minutes)

1. Go to: https://openweathermap.org/api
2. Click **"Sign Up"** (top right)
3. Fill in:
   - Email address
   - Username  
   - Password
4. Verify your email (check inbox)
5. Log in to your account

### **Step 2: Get Your API Key** (1 minute)

1. After logging in, you'll be at the dashboard
2. Click **"API keys"** tab
3. You'll see a default API key already created
4. Copy the key (looks like: `abc123def456...`)
5. **Important**: It may take 10 minutes to activate

### **Step 3: Add Key to Your Code** (2 minutes)

**Option A - Quick Update (For Testing):**

1. Open `mountain_huts_map.html` (at root of project)
2. Search for: `YOUR_OPENWEATHERMAP_API_KEY`
3. Replace with your actual key
4. Save file
5. Test locally: Open in browser and click a hut

**Option B - Permanent Update (Recommended):**

1. Open `tools/create_ultra_simple_map.py`
2. Find line ~1421:
   ```python
   var apiKey = 'YOUR_OPENWEATHERMAP_API_KEY';  // REPLACE THIS
   ```
3. Replace with:
   ```python
   var apiKey = 'abc123your-real-key-here';  // Your actual key
   ```
4. Save file
5. Regenerate map:
   ```bash
   python tools/create_ultra_simple_map.py
   ```
6. Commit and push:
   ```bash
   git add tools/create_ultra_simple_map.py mountain_huts_map.html website/huts_data.json
   git commit -m "Add OpenWeatherMap API key for live weather"
   git push origin develop
   ```

---

## ✅ **Test It Works**

1. Open your site (locally or on GitHub Pages)
2. Click any mountain hut on the map
3. Wait 1-2 seconds
4. You should see weather widget appear:
   ```
   ╔════════════════════════╗
   ║ [Icon] 15°C            ║
   ║        Partly Cloudy   ║
   ║                5-Day → ║
   ╚════════════════════════╝
   ```

5. If you see it → **Success!** ✅
6. If you don't → Check troubleshooting below

---

## 🆓 **Free Tier Limits**

**What You Get Free:**
- ✅ 1,000 API calls per day
- ✅ Current weather data
- ✅ 5-day / 3-hour forecast
- ✅ No credit card required
- ✅ Valid forever

**What That Means:**
- 1,000 hut popups opened per day = free
- Most sites get < 100 visitors/day
- Plenty for your needs!
- Resets every 24 hours

**If You Exceed Limit:**
- Fallback link still works
- Just shows "View Forecast →" link
- No errors or broken features

---

## 🔒 **Security Note**

**Is it safe to put API key in code?**

For OpenWeatherMap Current Weather API:
- ✅ **Yes, it's safe** for this use case
- ✅ Free tier, no billing
- ✅ Can't be used maliciously (no cost to you)
- ✅ Rate limited by OpenWeatherMap (1,000/day)
- ✅ Standard practice for free weather APIs

**However:**
- ⚠️ Don't commit paid API keys to public repos
- ⚠️ For paid services, use environment variables
- ✅ This is fine for free tier weather API

---

## 🐛 **Troubleshooting**

### **"Invalid API key" Error:**
- Wait 10-15 minutes after creating account
- API keys take time to activate
- Check you copied the full key (no spaces)
- Verify key in OpenWeatherMap dashboard

### **CORS Error in Browser:**
- This shouldn't happen (OpenWeatherMap allows browser requests)
- If it does, try clearing browser cache
- Check browser console for exact error

### **"Loading weather..." Never Finishes:**
1. Check browser console (F12) for errors
2. Verify internet connection
3. Confirm API key is correct
4. Check if ad blocker is interfering
5. Try in incognito/private window

### **Rate Limit Exceeded:**
- You get 1,000 calls/day
- Check your OpenWeatherMap dashboard for usage
- Upgrade to paid plan if needed ($40/month for 100k calls)
- Or implement weather caching (future enhancement)

---

## 🎨 **Customization**

### **Change Weather Widget Position:**

In `tools/create_ultra_simple_map.py`, find weather widget line (~1327):

**Current:** After description, before nearby huts
```javascript
// Description...
// Weather Widget
// Nearby Huts
```

**Move to top:** Put after header badges
**Move to bottom:** Put before footer

### **Change Weather Display:**

Edit lines ~1438-1445 to customize:
- Temperature unit: `units=metric` → `units=imperial` (°F)
- Icon size: `50px` → `60px` (bigger)
- Colors: Change gradient colors
- Layout: Adjust flexbox

### **Change Forecast Link:**

Current: Links to OpenWeatherMap city page

Change to custom: weatherspark.com, windy.com, etc.

---

## 📊 **API Usage Monitoring**

Track your usage:

1. Log in to OpenWeatherMap
2. Go to **"API keys"** tab
3. Click on your key
4. See usage statistics
5. Monitor daily calls

**Typical usage:**
- 10 visitors/day × 10 huts each = 100 calls/day
- Well under 1,000 limit
- No issues!

---

## 🌍 **Alternative Weather APIs**

If you want to try others:

### **Weather.gov (US Only)**
- Free, no API key
- US huts only
- Very accurate

### **Met.no (Europe)**
- Free, no registration
- Good for European huts
- Requires attribution

### **Weatherstack**
- Free tier: 1,000 calls/month
- Good free tier
- Easy to integrate

### **Visual Crossing**
- Free tier: 1,000 calls/day
- Historical weather
- Nice API

**Recommendation:** Stick with OpenWeatherMap - it's the easiest and most reliable.

---

## ✅ **Post-Setup Checklist**

- [ ] Created OpenWeatherMap account
- [ ] Got API key
- [ ] Waited 10 minutes for activation
- [ ] Added key to code
- [ ] Regenerated map
- [ ] Tested in browser
- [ ] Weather widget appears when clicking huts
- [ ] Committed and pushed to GitHub
- [ ] Verified on live site

---

## 🎉 **You're Done!**

Once you see the weather widget appear in popups, you're all set!

**Your hut explorer now shows:**
- 🔍 Smart search
- 🌤️ **Real-time weather** ← This!
- 📍 Nearby huts
- 📊 Live statistics
- ⚡ Optimized performance

**Professional-grade mountain hut planning tool!** 🏔️

---

**Questions?** Open an issue on GitHub or check NEW_FEATURES_DOCUMENTATION.md

