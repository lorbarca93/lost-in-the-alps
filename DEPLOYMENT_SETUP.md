# Deployment Setup Guide

This repository is structured so that **only the web interface** is pushed to GitHub, while all source code, scrapers, and tools remain local.

## 📁 Repository Structure

```
lost-in-the-alps/
├── web/                    # ← Separate Git repository (pushed to GitHub)
│   ├── .git/              # Git repository for web folder only
│   ├── index.html
│   ├── map.html
│   ├── data/
│   └── ...
│
├── src/                    # ← Local only (not in git)
├── scripts/                # ← Local only
├── tools/                  # ← Local only
├── docs/                   # ← Local only
├── data/                   # ← Local only (database)
└── .gitignore              # Root gitignore (excludes everything)
```

## 🔧 Setup Instructions

### 1. Root Repository (Local Only)

The root folder should **NOT** have a Git repository, or if it does, it should ignore everything:

```bash
# Root .gitignore already configured to exclude everything except web/
# This ensures nothing from root gets committed
```

### 2. Web Folder Repository (GitHub)

The `web/` folder has its own Git repository:

```bash
cd web

# Initialize git (if not already done)
git init

# Add remote repository
git remote add origin https://github.com/yourusername/your-repo-name.git

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Web interface"

# Push to GitHub
git push -u origin main
```

## 🔄 Workflow

### Updating the Website

1. **Generate new data** (from project root):
   ```bash
   python tools/api/stats.py
   python tools/api/export_huts.py
   python tools/generate_huts_json.py
   python tools/create_ultra_simple_map.py
   ```

2. **Commit and push web changes**:
   ```bash
   cd web
   git add .
   git commit -m "Update data and map"
   git push
   ```

### Making Code Changes

- All source code changes stay local
- Only web interface changes need to be committed to `web/` repository
- Data files in `web/data/` are tracked (they're needed for the website)

## 📝 What Gets Pushed to GitHub

**Included:**
- ✅ All HTML files (`index.html`, `map.html`, `about.html`, etc.)
- ✅ CSS files (`css/styles.css`)
- ✅ JavaScript files (`js/*.js`)
- ✅ Data files (`data/*.json`) - needed for the website
- ✅ Configuration files (`_redirects`, etc.)

**Excluded (stays local):**
- ❌ Source code (`src/`)
- ❌ Scripts (`scripts/`)
- ❌ Tools (`tools/`)
- ❌ Documentation (`docs/`)
- ❌ Database (`data/mountain_huts.db`)
- ❌ Configuration (`config/`)

## 🎯 Benefits

1. **Privacy**: Source code and scrapers stay local
2. **Security**: Database and sensitive tools not exposed
3. **Clean Deployment**: Only website files on GitHub
4. **Easy Updates**: Simple workflow to update website
5. **Separation**: Clear separation between development and deployment

## 🔍 Verifying Setup

### Check Root Git Status

```bash
# From root directory
git status
# Should show nothing or only web/ folder (if root has git)
```

### Check Web Git Status

```bash
# From web directory
cd web
git status
# Should show web files only
```

### Verify .gitignore

```bash
# Root .gitignore should exclude everything except web/
cat .gitignore | grep -v "^#" | head -20

# Web .gitignore should only exclude temp files
cat web/.gitignore
```

## 🚨 Important Notes

1. **Never commit from root**: Always commit from `web/` folder
2. **Data files are tracked**: `web/data/*.json` files are needed for the website
3. **Keep database local**: Never commit `data/mountain_huts.db`
4. **Update data before pushing**: Always regenerate data files before committing

## 📚 Related Documentation

- `web/README.md` - Web interface documentation
- `README.md` - Main project documentation (local only)

