# Git Repository Structure

## Overview

This project uses a **dual-repository structure**:

1. **Root folder**: Local development only (no Git repository, or Git ignores everything)
2. **web/ folder**: Separate Git repository for deployment to GitHub

## 📁 Structure

```
lost-in-the-alps/                    # Local development (no git or git ignores all)
├── .gitignore                       # Excludes everything except web/
│
├── src/                             # ← Local only
├── scripts/                         # ← Local only
├── tools/                           # ← Local only
├── docs/                            # ← Local only
├── data/                            # ← Local only (database)
├── config/                          # ← Local only
│
└── web/                             # ← Separate Git repository
    ├── .git/                        # Git repository for web only
    ├── .gitignore                   # Web-specific ignores
    ├── index.html
    ├── map.html
    ├── data/                        # Data files (tracked - needed for site)
    ├── css/
    └── js/
```

## 🔧 Setup

### Root Folder (Local Only)

The root `.gitignore` excludes everything:

```gitignore
# Ignore everything except web/ folder
/web/

# Source code (keep local only)
src/
scripts/
tools/
docs/
data/
config/
```

**Note**: If you want to initialize Git in the root for local version control:

```bash
# Optional: Initialize git in root for local version control
git init
git add .gitignore
git commit -m "Initial commit: Local development repository"
```

This will track only `.gitignore` and ignore everything else.

### Web Folder (GitHub Deployment)

The `web/` folder has its own Git repository:

```bash
cd web

# Already initialized
git status

# Add remote (when ready)
git remote add origin https://github.com/yourusername/your-repo-name.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: Web interface"

# Push to GitHub
git push -u origin main
```

## 🔄 Workflow

### Daily Development

1. **Work on source code** (local only, not tracked)
2. **Generate data files**:
   ```bash
   python tools/api/stats.py
   python tools/api/export_huts.py
   python tools/generate_huts_json.py
   ```
3. **Test locally**:
   ```bash
   cd web
   python -m http.server 8080
   ```

### Deploying Updates

1. **Regenerate data** (if needed):
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
   git commit -m "Update: [description of changes]"
   git push
   ```

## ✅ What Gets Pushed

### Included in `web/` Repository

- ✅ All HTML files
- ✅ CSS files
- ✅ JavaScript files
- ✅ Data files (`data/*.json`) - needed for website
- ✅ Configuration files (`_redirects`, etc.)

### Excluded (Stays Local)

- ❌ Source code (`src/`)
- ❌ Scripts (`scripts/`)
- ❌ Tools (`tools/`)
- ❌ Documentation (`docs/`)
- ❌ Database (`data/mountain_huts.db`)
- ❌ Configuration (`config/`)
- ❌ Virtual environments (`.venv/`)

## 🎯 Benefits

1. **Privacy**: Source code and scrapers stay local
2. **Security**: Database and tools not exposed publicly
3. **Clean Deployment**: Only website files on GitHub
4. **Simple Workflow**: Easy to update website
5. **Separation**: Clear separation between dev and deployment

## 🔍 Verification

### Check Root (Should be empty or ignore everything)

```bash
# From root
git status
# Should show nothing or only .gitignore
```

### Check Web (Should show web files)

```bash
# From web/
cd web
git status
# Should show web files only
```

## 📚 Related Files

- `DEPLOYMENT_SETUP.md` - Detailed deployment guide
- `web/README.md` - Web interface documentation
- `.gitignore` - Root gitignore configuration
- `web/.gitignore` - Web gitignore configuration

