# External Links Feature - Google Maps & Meteoblue Integration

## 🎉 Successfully Implemented!

### New Feature
Added external tool buttons to the hut detail page that open the hut's coordinates in:
1. **Google Maps** - For navigation and route planning
2. **Meteoblue** - For detailed weather forecasts

### What Changed

#### Location in Code
- **File**: `website/js/map-app.js`
- **Function**: `showHutDetails(hut)` (lines 824-838)

#### New Section Added
**"🗺️ External Tools"** section appears in the hut detail sidebar with two buttons:

1. **📍 Open in Google Maps**
   - Opens Google Maps search with exact coordinates
   - URL format: `https://www.google.com/maps/search/?api=1&query=LAT,LON`
   - Opens in new tab with `target="_blank"`
   - Security: Uses `rel="noopener noreferrer"`

2. **🌦️ Detailed Weather (Meteoblue)**
   - Opens Meteoblue weekly forecast for the location
   - URL format: `https://www.meteoblue.com/en/weather/week/HUT_NAME?lat=LAT&lon=LON`
   - Includes hut name in URL (encoded for safety)
   - Opens in new tab with security attributes

### How It Works

When a user clicks on any mountain hut marker:
1. Detail sidebar opens with hut information
2. New "External Tools" section appears after Description
3. User can click either button to:
   - Navigate to the hut using Google Maps
   - View detailed 7-14 day weather forecast on Meteoblue

### Benefits

✅ **Navigation** - Users can easily get directions to the hut
✅ **Weather Planning** - Access professional weather forecasts beyond our 14-day Open-Meteo data
✅ **User Experience** - One-click access to powerful external tools
✅ **Coordinates Preserved** - Exact GPS coordinates passed to external services
✅ **Secure** - Opens in new tabs with proper security attributes

### Button Styling

- **Google Maps**: Primary button (blue background)
- **Meteoblue**: Secondary button (white background with border)
- Both have proper spacing and icons (📍 and 🌦️)
- Consistent with existing button design

### Testing

To test the new feature:
1. Open the map at `http://localhost:8080/mountain_huts_map.html`
2. Click any mountain hut marker
3. Scroll down in the detail sidebar
4. Look for **"🗺️ External Tools"** section
5. Click **"📍 Open in Google Maps"** - Should open Google Maps at that location
6. Click **"🌦️ Detailed Weather (Meteoblue)"** - Should open Meteoblue forecast

### Example URLs Generated

For a hut at coordinates 46.5° N, 10.5° E named "Rifugio Example":

**Google Maps:**
```
https://www.google.com/maps/search/?api=1&query=46.5,10.5
```

**Meteoblue:**
```
https://www.meteoblue.com/en/weather/week/Rifugio%20Example?lat=46.5&lon=10.5
```

### Future Enhancements (Optional)

- Add more external tools (e.g., Windy.com, Mountain-Forecast.com)
- Add GPX download for individual hut
- Add "Share location" button (WhatsApp, Telegram, etc.)
- Add altitude-specific weather forecast services

---

**Implemented**: November 11, 2025
**Feature**: External navigation and weather links
**User Benefit**: Easy access to professional mapping and weather services

