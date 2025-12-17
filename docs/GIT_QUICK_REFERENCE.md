# Git Quick Reference for Lost in the Alps

## Daily Workflow

```bash
# Check what changed
git status

# Stage all changes
git add .

# Commit with message
git commit -m "Brief description of changes"

# Push to remote (if connected to GitHub)
git push
```

## Viewing Changes

```bash
# See uncommitted changes
git diff

# See what's staged
git diff --staged

# See commit history
git log --oneline

# See last 5 commits
git log -5

# See detailed commit
git show <commit-hash>
```

## Branching

```bash
# Create and switch to new branch
git checkout -b feature/my-feature

# Switch branches
git checkout main

# List all branches
git branch

# Merge branch into current
git merge feature/my-feature

# Delete branch
git branch -d feature/my-feature
```

## Undo Things

```bash
# Discard changes in file
git restore <file>              # Git 2.23+
git checkout -- <file>          # Older Git

# Unstage file
git restore --staged <file>     # Git 2.23+
git reset HEAD <file>           # Older Git

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes - CAREFUL!)
git reset --hard HEAD~1

# Create new commit that undoes a previous commit
git revert <commit-hash>
```

## Stashing (Temporary Storage)

```bash
# Save current changes temporarily
git stash

# Save with a description
git stash save "WIP: working on new scraper"

# List stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{0}

# Delete stash
git stash drop stash@{0}
```

## Project-Specific Workflows

### Adding a New Scraper

```bash
# Create feature branch
git checkout -b scraper/newsite

# Work on scraper...
# Test it...

# Commit when working
git add scrapers/scraper_newsite.py
git commit -m "scraper: Add initial scraper for newsite.com"

# More commits as you improve it...
git add scrapers/scraper_newsite.py
git commit -m "scraper: Add contact info extraction"

# When done and tested
git checkout main
git merge scraper/newsite
git branch -d scraper/newsite
```

### Updating the Map

```bash
# Make changes to map generation
git add tools/create_ultra_simple_map.py
git commit -m "feat: Add amenities to map popups"

# Regenerate map
python tools/create_ultra_simple_map.py

# Commit the updated map
git add mountain_huts_map.html
git commit -m "data: Regenerate map with amenities"
```

### Fixing a Bug

```bash
# Create bugfix branch
git checkout -b bugfix/coordinate-swap

# Fix the bug...
git add scrapers/scraper_boudy_info.py
git commit -m "fix: Correct lat/lon swap in boudy.info scraper"

# Merge fix
git checkout main
git merge bugfix/coordinate-swap
git branch -d bugfix/coordinate-swap
```

### Database Updates

```bash
# After running scrapers and updating database
# Note: .db files are in .gitignore, so they won't be committed

# Commit the scraper changes that led to new data
git add run_all_scrapers.py
git commit -m "data: Update scraper to get 500 more huts"

# Update documentation if stats changed
git add README.md
git commit -m "doc: Update statistics to reflect 3,392 total huts"
```

## GitHub Integration

```bash
# Connect to GitHub (first time)
git remote add origin https://github.com/username/lostinthealps.git

# View remote
git remote -v

# Push to GitHub
git push -u origin main         # First time
git push                        # After that

# Pull from GitHub
git pull

# Clone repository (on another machine)
git clone https://github.com/username/lostinthealps.git
```

## Common Scenarios

### "I forgot to commit before starting new work"

```bash
# Stash current changes
git stash

# Commit previous work
git add <previous-files>
git commit -m "Previous work"

# Get your current work back
git stash pop
```

### "I committed to wrong branch"

```bash
# Note the commit hash
git log --oneline -1

# Undo the commit on current branch
git reset --hard HEAD~1

# Switch to correct branch
git checkout correct-branch

# Cherry-pick the commit
git cherry-pick <commit-hash>
```

### "I want to see old version"

```bash
# View commit history
git log --oneline

# Checkout old version (read-only)
git checkout <commit-hash>

# Look around...

# Go back to current
git checkout main
```

### "I made a typo in last commit message"

```bash
# Fix the last commit message
git commit --amend -m "Corrected message"
```

## Useful Aliases

Add these to your `~/.gitconfig` or run:

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.lg "log --oneline --graph --all --decorate"
git config --global alias.undo 'reset --soft HEAD~1'
```

Then use: `git st`, `git co main`, `git lg`, etc.

## Files in This Project

### Always Commit

- `*.py` - All Python source files
- `*.md` - Documentation
- `.gitignore`, `.gitattributes` - Git configuration
- `requirements.txt` - Dependencies

### Sometimes Commit

- `mountain_huts_map.html` - Generated but trackable
- `debug/mountainhuts_locations.js` - Reference data

### Never Commit (in .gitignore)

- `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `data/*.db` - Database files
- `huts_data.json` - Exports

## Emergency Commands

```bash
# See what Git will ignore
git status --ignored

# Remove file from Git but keep locally
git rm --cached <file>

# Completely reset to last commit (CAREFUL!)
git reset --hard HEAD

# Clean untracked files (CAREFUL!)
git clean -fd

# Get out of weird state
git reset --hard origin/main
```

## Get Help

```bash
git help <command>
git <command> --help
```

## Resources

- Full guide: `docs/GIT_SETUP_GUIDE.md`
- Commit template: `.gitmessage`
- Online tutorial: https://learngitbranching.js.org/
