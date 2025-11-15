# Branching Strategy

This project uses a **simple two-branch strategy** for clean development and deployment.

## 🌳 Branches

### `main` Branch (Production)
- **Purpose**: Production-ready code that gets deployed
- **Status**: ✅ Stable and tested
- **Deployment**: Automatically deployed to:
  - **GitHub Pages** (via GitHub Actions)
  - **Vercel** (if configured)
  - **Cloudflare Pages** (if configured)
- **Usage**: Only merge stable, tested code from `develop`
- **Protection**: Should be protected to prevent direct pushes

### `develop` Branch (Development)
- **Purpose**: Development and testing of new features
- **Status**: 🔧 Experimental and risky changes
- **Deployment**: ❌ **NOT deployed anywhere** - development only
- **Usage**: All new features, bug fixes, and risky changes go here first
- **Workflow**: Merge to `main` only when stable and tested

## 🔄 Workflow

### For New Features / Risky Changes

```bash
# 1. Switch to develop branch
git checkout develop

# 2. Pull latest changes
git pull origin develop

# 3. Create feature branch (optional)
git checkout -b feature/your-feature-name

# 4. Make your changes and commit
git add .
git commit -m "Add feature: description"

# 5. Push to develop
git push origin develop
# or if using feature branch:
git checkout develop
git merge feature/your-feature-name
git push origin develop
```

### For Deploying to Production

```bash
# 1. Ensure develop is stable and tested
git checkout develop

# 2. Switch to main
git checkout main

# 3. Pull latest main
git pull origin main

# 4. Merge develop into main
git merge develop

# 5. Push to main (triggers deployment)
git push origin main
```

### For Quick Hotfixes (Direct to Main)

```bash
# Only for critical production fixes
git checkout main
git pull origin main
# Make minimal fix
git add .
git commit -m "Hotfix: description"
git push origin main
# Then merge back to develop
git checkout develop
git merge main
git push origin develop
```

## 🚀 Deployment Configuration

### GitHub Pages
- **Trigger**: Automatic on push to `main` branch
- **Workflow**: `.github/workflows/deploy-pages.yml`
- **Configuration**: Only deploys from `main` branch

### Vercel / Cloudflare Pages
- **Configuration**: Set to deploy from `main` branch only
- **Manual Setup**: Configure in Vercel/Cloudflare dashboard to watch `main` branch

## 📋 Branch Rules

### ✅ DO:
- ✅ Develop new features on `develop`
- ✅ Test thoroughly before merging to `main`
- ✅ Keep `main` always deployable
- ✅ Use descriptive commit messages
- ✅ Merge `main` back to `develop` after hotfixes

### ❌ DON'T:
- ❌ Push directly to `main` (except hotfixes)
- ❌ Deploy `develop` branch to production
- ❌ Merge untested code to `main`
- ❌ Leave `develop` and `main` out of sync for long

## 🔍 Branch Status

### Check Current Branch
```bash
git branch
```

### See All Branches
```bash
git branch -a
```

### Switch Branches
```bash
git checkout main       # Switch to main
git checkout develop    # Switch to develop
```

### Update Branch
```bash
git pull origin main      # Update main
git pull origin develop   # Update develop
```

## 📝 Example Workflow

**Scenario**: Adding a new mobile feature

1. **Development Phase**:
   ```bash
   git checkout develop
   git pull origin develop
   # Make changes to mobile menu
   git add web/css/styles.css web/js/map-app.js
   git commit -m "feat: improve mobile menu positioning"
   git push origin develop
   ```

2. **Testing Phase**:
   - Test locally on `develop` branch
   - Verify mobile functionality
   - Fix any issues on `develop`

3. **Deployment Phase**:
   ```bash
   git checkout main
   git pull origin main
   git merge develop
   git push origin main
   # GitHub Actions automatically deploys to GitHub Pages
   ```

## 🎯 Benefits

1. **Clear Separation**: Development and production clearly separated
2. **Safe Testing**: Test risky changes without affecting production
3. **Automatic Deployment**: `main` automatically deploys when updated
4. **Simple Workflow**: Easy to understand and follow
5. **Rollback Safety**: Can easily revert if something breaks

## 🔗 Related Files

- `.github/workflows/deploy-pages.yml` - GitHub Pages deployment (main only)
- `README.md` - Main project documentation
- `DEPLOYMENT_SETUP.md` - Deployment configuration guide

