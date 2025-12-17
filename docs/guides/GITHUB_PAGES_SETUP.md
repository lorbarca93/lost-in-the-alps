# 🚀 GitHub Pages Deployment Guide

**Status**: Automated deployment configured ✅  
**URL**: Will be at `https://barcarolol-bit.github.io/Mountain-huts-europe/`

---

## ✅ What's Configured

I've set up **automatic deployment** to GitHub Pages using GitHub Actions. Every time you push to `develop`, `master`, or `main` branch, your website will automatically rebuild and deploy!

### Files Created:
- `.github/workflows/deploy-gh-pages.yml` - GitHub Actions workflow
- `website/.nojekyll` - Prevents Jekyll processing
- `GITHUB_PAGES_SETUP.md` - This guide

---

## 🎯 3-Step Activation (On GitHub Website)

You need to enable GitHub Pages in your repository settings. I can't do this directly, but here's how:

### **Step 1: Go to Repository Settings**
1. Go to https://github.com/barcarolol-bit/Mountain-huts-europe
2. Click **"Settings"** (top right, near Star button)

### **Step 2: Enable GitHub Pages**
1. In the left sidebar, click **"Pages"** (under "Code and automation")
2. Under **"Build and deployment"**, set:
   - **Source**: Select `GitHub Actions` (not "Deploy from a branch")
3. Click **"Save"** if needed

### **Step 3: Wait for Deployment**
1. Go to **"Actions"** tab in your repo
2. You should see a workflow running called "Deploy to GitHub Pages"
3. Wait 2-3 minutes for it to complete
4. Your site will be live at: `https://barcarolol-bit.github.io/Mountain-huts-europe/`

---

## 🔄 How It Works

### Automatic Deployment:
```
Push to develop/main → GitHub Actions triggers
                    ↓
Install Python & dependencies
                    ↓
Generate stats.json and huts.json
                    ↓
Generate mountain_huts_map.html
                    ↓
Copy website files to deployment folder
                    ↓
Deploy to GitHub Pages
                    ↓
Live at: https://barcarolol-bit.github.io/Mountain-huts-europe/
```

### What Gets Deployed:
- ✅ `index.html` - Main landing page (redirects to map)
- ✅ `mountain_huts_map.html` - Full interactive map
- ✅ `map.html` - Also points to the map
- ✅ `privacy-policy.html` - Privacy policy
- ✅ `js/cookie-consent.js` - Cookie consent system
- ✅ `api/stats.json` - Statistics data
- ✅ `api/huts.json` - Huts data
- ✅ All CSS, JS, and other assets

---

## 📋 First-Time Setup Checklist

After I commit and push the workflow:

- [ ] Go to GitHub.com → Your repository
- [ ] Click "Settings" → "Pages"
- [ ] Set Source to "GitHub Actions"
- [ ] Go to "Actions" tab
- [ ] Watch the deployment workflow run
- [ ] Visit your site: `https://barcarolol-bit.github.io/Mountain-huts-europe/`
- [ ] Test the map loads correctly
- [ ] Test cookie consent appears
- [ ] Test mobile responsiveness

---

## 🌐 Your Website URLs

Once enabled, your site will be accessible at:

**Main URLs:**
- `https://barcarolol-bit.github.io/Mountain-huts-europe/` → Redirects to map
- `https://barcarolol-bit.github.io/Mountain-huts-europe/map.html` → Direct to map
- `https://barcarolol-bit.github.io/Mountain-huts-europe/mountain_huts_map.html` → Map
- `https://barcarolol-bit.github.io/Mountain-huts-europe/privacy-policy.html` → Privacy

**API Endpoints:**
- `https://barcarolol-bit.github.io/Mountain-huts-europe/api/stats.json`
- `https://barcarolol-bit.github.io/Mountain-huts-europe/api/huts.json`

---

## 🔧 Troubleshooting

### "Pages tab not visible in Settings"
**Solution:** 
- Repo must be public (or you need GitHub Pro for private repos)
- You must be the repo owner or have admin access

### "Workflow not running"
**Solution:**
1. Check "Actions" tab → Make sure Actions are enabled
2. If disabled, click "Enable Actions"
3. Push a new commit to trigger deployment

### "404 Not Found after deployment"
**Solution:**
1. Wait 5 minutes (DNS propagation)
2. Check the deployment URL in Actions log
3. Try clearing browser cache
4. Make sure you selected "GitHub Actions" as source (not "branch")

### "Map not loading"
**Solution:**
1. Check browser console for errors (F12)
2. Verify `huts_data.json` exists in deployment
3. Check file paths are correct (relative, not absolute)
4. Test locally first: `cd website && python -m http.server 8080`

---

## 🎨 Custom Domain (Optional)

Want to use your own domain like `lostinthealps.com`?

### Steps:
1. Go to Settings → Pages
2. Under "Custom domain", enter your domain
3. Add DNS records at your domain registrar:
   ```
   Type: CNAME
   Name: @ (or www)
   Value: barcarolol-bit.github.io
   ```
4. Wait for DNS to propagate (24-48 hours)
5. Enable "Enforce HTTPS" in Settings → Pages

---

## 🔒 HTTPS / SSL

GitHub Pages automatically provides HTTPS for:
- ✅ `.github.io` domains
- ✅ Custom domains (after DNS verification)

No configuration needed! 🎉

---

## 📊 View Deployment Status

### Real-time:
1. Go to "Actions" tab
2. See latest workflow runs
3. Green checkmark ✅ = deployed successfully
4. Red X ❌ = deployment failed (click for logs)

### Deployment History:
1. Go to "Deployments" (right sidebar on repo homepage)
2. See all past deployments
3. View active deployment URL

---

## 🚀 Deployment Frequency

**Automatically deploys when you push to:**
- `develop` branch (your current branch)
- `main` branch
- `master` branch

**Manual deployment:**
1. Go to "Actions" tab
2. Click "Deploy to GitHub Pages" workflow
3. Click "Run workflow" button
4. Select branch → "Run workflow"

---

## 🧪 Test Before Going Live

Before activating GitHub Pages:

```bash
# Local testing
cd website
python -m http.server 8080

# Open browser to http://localhost:8080
# Test all features:
# - Map loads
# - Filters work
# - Cookie consent appears
# - Privacy policy accessible
# - Mobile responsive
```

---

## 📈 Performance on GitHub Pages

Expected performance:
- ⚡ **Fast**: GitHub's CDN is worldwide
- 📦 **Small files**: 59 KB for map HTML
- 🔄 **JSON loading**: ~1 second for 8,142 huts
- 🌍 **Global**: Low latency everywhere

---

## 🛠️ Workflow Configuration

The workflow (`.github/workflows/deploy-gh-pages.yml`) does:

1. **Checkout code** - Gets latest from your branch
2. **Setup Python** - Installs Python 3.11
3. **Install dependencies** - From `requirements.txt`
4. **Generate data** - Runs `stats.py` and `export_huts.py`
5. **Generate map** - Runs `create_ultra_simple_map.py`
6. **Prepare site** - Copies website files to `_site/`
7. **Upload artifact** - Packages for deployment
8. **Deploy** - Publishes to GitHub Pages

**Runs in ~3-5 minutes** on GitHub's servers.

---

## 🔄 Updating Your Site

After setup, updating is easy:

```bash
# Make changes to your code
# ... edit files ...

# Generate new data (if database changed)
python website/api/stats.py
python website/api/export_huts.py
python tools/create_ultra_simple_map.py

# Commit and push
git add -A
git commit -m "Update website"
git push origin develop

# GitHub Actions automatically deploys!
# Check "Actions" tab to watch progress
# Live in 3-5 minutes
```

---

## 📱 Mobile Testing

After deployment, test on real devices:

- [ ] iPhone/iOS
- [ ] Android phone
- [ ] iPad/tablet
- [ ] Different browsers (Safari, Chrome, Firefox)
- [ ] Cookie consent works
- [ ] Map is responsive
- [ ] Filters usable on mobile

---

## ✅ Post-Deployment Checklist

After site goes live:

- [ ] Visit your GitHub Pages URL
- [ ] Verify map loads and displays 8,142 huts
- [ ] Test cookie consent banner appears
- [ ] Click "Accept All" and verify it works
- [ ] Test "Cookie Settings" button in footer
- [ ] Check privacy policy loads
- [ ] Test on mobile device
- [ ] Test all map layers work
- [ ] Test filters function correctly
- [ ] Check browser console for errors
- [ ] Update Google Analytics ID (if not done yet)
- [ ] Share the URL! 🎉

---

## 🎯 Next Steps After This Commit

1. **I'll commit and push the workflow** → Done automatically
2. **You go to GitHub** → Settings → Pages
3. **Select "GitHub Actions"** as source
4. **Watch it deploy** → Actions tab
5. **Visit your live site!** 🚀

---

## 🌟 Your Live Website!

Once enabled:

**Main URL:**
```
https://barcarolol-bit.github.io/Mountain-huts-europe/
```

**Share it:**
- Tweet about it 🐦
- Post on Reddit (r/hiking, r/alpinism)
- Share with hiking communities
- Add to your portfolio
- Tell your friends! 🏔️

---

## 📧 Need Help?

If something doesn't work:

1. Check "Actions" tab for error logs
2. Read the workflow log file (click on failed step)
3. Verify GitHub Pages is enabled in Settings
4. Make sure repo is public
5. Check that Actions are enabled
6. Open an issue on GitHub with error details

---

**You're ready to go live! 🎉**

Just enable GitHub Pages in Settings → Pages, and your beautiful mountain hut explorer will be live for the world to see! 🏔️🗺️

