# Git Setup Guide for Lost in the Alps

## 1. Install Git

### Windows

Download and install Git from: https://git-scm.com/download/win

**Recommended settings during installation:**

- Use Git from Git Bash and also from Windows Command Prompt
- Use the default text editor (or choose VS Code if you have it)
- Override the default branch name: `main`
- Git Credential Manager: Enabled
- Enable file system caching

After installation, restart your terminal/VS Code.

### Verify Installation

```bash
git --version
```

## 2. Initial Git Configuration

Run these commands once (replace with your info):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

## 3. Initialize Repository

```bash
# Initialize git repository
git init

# Add all files to staging
git add .

# Create first commit
git commit -m "Initial commit: Mountain huts scraper system with 2,892 huts"
```

## 4. Check the .gitignore File

The `.gitignore` file is already configured to exclude:

- `.venv/` - Virtual environment (large, reproducible)
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files
- `*.db` - Database files (except in data/)
- `debug/*.html` - Debug HTML files
- `debug/*.js` - Debug JavaScript files (except reference)

## 5. Basic Git Workflow

### Check Status

```bash
git status
```

### Add Changes

```bash
# Add specific file
git add filename.py

# Add all changes
git add .

# Add files in a folder
git add scrapers/
```

### Commit Changes

```bash
git commit -m "Brief description of what changed"
```

### View History

```bash
# See commit history
git log

# See compact history
git log --oneline

# See last 5 commits
git log -5
```

### View Changes

```bash
# See uncommitted changes
git diff

# See changes in a specific file
git diff filename.py

# See staged changes
git diff --staged
```

### Undo Changes

```bash
# Discard changes in a file (careful!)
git checkout -- filename.py

# Unstage a file
git reset HEAD filename.py

# Undo last commit (keeps changes)
git reset --soft HEAD~1

# Undo last commit (discards changes - careful!)
git reset --hard HEAD~1
```

## 6. Branching (Optional but Recommended)

### Create and Switch to a New Branch

```bash
git checkout -b feature/new-scraper
```

### Switch Between Branches

```bash
git checkout main
git checkout feature/new-scraper
```

### Merge Branch into Main

```bash
git checkout main
git merge feature/new-scraper
```

### Delete Branch

```bash
git branch -d feature/new-scraper
```

## 7. Remote Repository (GitHub/GitLab)

### Create Repository on GitHub

1. Go to https://github.com/new
2. Create a new repository (don't initialize with README)
3. Copy the repository URL

### Link Local to Remote

```bash
git remote add origin https://github.com/yourusername/lostinthealps.git
git branch -M main
git push -u origin main
```

### Push Changes

```bash
git push
```

### Pull Changes

```bash
git pull
```

## 8. Recommended Commit Messages

Use clear, descriptive commit messages:

```bash
# Good examples:
git commit -m "Add new scraper for refuges.info"
git commit -m "Fix coordinate swap bug in boudy.info scraper"
git commit -m "Update map to show owner and manager information"
git commit -m "Add country geocoding using Nominatim API"
git commit -m "Clean up debug files and organize repository"

# Less helpful:
git commit -m "Update"
git commit -m "Fix bug"
git commit -m "Changes"
```

## 9. Suggested Branching Strategy

```bash
main                    # Stable, working code
├── develop             # Integration branch
│   ├── feature/new-scraper
│   ├── feature/improved-map
│   └── bugfix/coordinate-issue
```

### Workflow:

1. Create feature branch from `develop`
2. Work on feature
3. Merge back to `develop`
4. Test thoroughly
5. Merge `develop` to `main`

## 10. Common Scenarios

### Scenario: Started Working Without Committing

```bash
# Stash current changes
git stash

# Create a branch for your work
git checkout -b feature/my-changes

# Apply stashed changes
git stash pop

# Commit
git add .
git commit -m "Describe your changes"
```

### Scenario: Want to Try Something Without Losing Current Code

```bash
# Commit current work
git add .
git commit -m "WIP: Current progress"

# Create experimental branch
git checkout -b experiment

# Try things...
# If it works:
git checkout main
git merge experiment

# If it doesn't work:
git checkout main
git branch -d experiment
```

### Scenario: Need to Go Back to Working Version

```bash
# See commit history
git log --oneline

# Go back to specific commit (creates detached HEAD)
git checkout <commit-hash>

# Create branch from there
git checkout -b recovered-version

# Or just look and go back
git checkout main
```

## 11. Files to Commit vs. Ignore

### ✅ Commit These:

- All `.py` source files
- `README.md` and documentation
- `requirements.txt`
- `.gitignore`
- `mountain_huts_map.html` (it's generated but useful to track)
- Reference data in `debug/` (like `mountainhuts_locations.js`)

### ❌ Don't Commit These:

- `.venv/` folder
- `__pycache__/` folders
- `*.pyc` files
- `data/*.db` files (large, contain scraped data)
- Temporary debug files
- IDE-specific files (`.vscode/`, `.idea/`)

## 12. Quick Reference Commands

```bash
# Daily workflow
git status                          # Check what changed
git add .                          # Stage all changes
git commit -m "Description"        # Commit with message
git push                           # Push to remote (if configured)

# View changes
git log --oneline                  # See history
git diff                           # See uncommitted changes
git show <commit-hash>             # See specific commit

# Undo things
git restore <file>                 # Discard changes (Git 2.23+)
git restore --staged <file>        # Unstage file (Git 2.23+)
git revert <commit-hash>           # Undo commit with new commit

# Branching
git branch                         # List branches
git checkout -b <branch-name>      # Create and switch to branch
git merge <branch-name>            # Merge branch into current
```

## 13. First Steps After Installing Git

```bash
# 1. Configure Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 2. Initialize repository
cd C:\Users\loren\Downloads\lostinthealps
git init

# 3. Review what will be committed
git status

# 4. Create first commit
git add .
git commit -m "Initial commit: Mountain huts scraper with 2,892 huts from 3 sources

- Implemented scrapers for boudy.info, mountain-huts.net, mountainhuts.info
- Database with comprehensive data (owner, manager, contact info)
- Interactive map with 19 countries
- Clean, organized repository structure"

# 5. View your commit
git log
```

## 14. Useful Aliases (Optional)

Add to your git config for shortcuts:

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all --decorate"
```

Then use: `git st` instead of `git status`, etc.

## Need Help?

- Git documentation: https://git-scm.com/doc
- Interactive tutorial: https://learngitbranching.js.org/
- GitHub guides: https://guides.github.com/

---

**Pro tip:** Commit often! It's better to have many small commits than one giant commit. Each commit should represent a logical unit of change.
