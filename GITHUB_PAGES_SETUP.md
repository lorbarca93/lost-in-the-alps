# GitHub Pages Setup Guide

## ✅ Automated Deployment

A GitHub Actions workflow has been configured to automatically deploy your website to GitHub Pages.

### Workflow File

The workflow is located at: `.github/workflows/deploy-pages.yml`

It will automatically deploy when you push to:
- `main` branch
- `master` branch  
- `develop` branch

## 🔧 Manual Setup (One-Time)

You need to enable GitHub Pages in your repository settings:

### Steps:

1. **Go to Repository Settings**
   - Navigate to: https://github.com/lorbarca93/lost-in-the-alps/settings
   - Click on **"Pages"** in the left sidebar

2. **Configure Source**
   - Under **"Source"**, select: **"GitHub Actions"**
   - This will use the workflow we just created

3. **Save Settings**
   - The page will automatically save

### Alternative: Deploy from Branch

If you prefer to deploy directly from a branch:

1. Go to **Settings** → **Pages**
2. Under **"Source"**, select: **"Deploy from a branch"**
3. Select branch: **`main`** (or `develop` if that's your default)
4. Select folder: **`/ (root)`**
5. Click **Save**

## 🌐 Your Website URL

Once enabled, your website will be available at:

**https://lorbarca93.github.io/lost-in-the-alps/**

Or if using a custom domain:
**https://yourdomain.com**

## 🔄 Automatic Deployment

After enabling GitHub Pages:

1. **Push changes** to `main`, `master`, or `develop` branch
2. **GitHub Actions** will automatically build and deploy
3. **Check Actions tab** to see deployment progress:
   - https://github.com/lorbarca93/lost-in-the-alps/actions

## 📝 Files Included

The following files are configured for GitHub Pages:

- ✅ `.nojekyll` - Disables Jekyll processing (needed for static sites)
- ✅ `_redirects` - Netlify redirects (also works for GitHub Pages)
- ✅ All HTML, CSS, JavaScript files
- ✅ Data files in `data/` folder

## 🐛 Troubleshooting

### Website Not Loading

1. **Check Actions**: Go to Actions tab and verify deployment succeeded
2. **Check Settings**: Ensure GitHub Pages is enabled in Settings → Pages
3. **Wait**: It may take a few minutes for the site to be available
4. **Clear Cache**: Try accessing in incognito mode

### 404 Errors

- Ensure `index.html` exists in the root
- Check that file paths are relative (not absolute)
- Verify `.nojekyll` file exists

### Data Files Not Loading

- Ensure `data/*.json` files are committed
- Check browser console for CORS errors
- Verify file paths in JavaScript are relative

## 🔍 Verify Deployment

1. Go to: https://github.com/lorbarca93/lost-in-the-alps/actions
2. Look for "Deploy to GitHub Pages" workflow
3. Click on the latest run to see details
4. Once green, your site should be live!

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

