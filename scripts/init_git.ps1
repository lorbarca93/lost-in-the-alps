# Git Initialization Script for Lost in the Alps
# Run this AFTER installing Git

Write-Host "`n=== Git Repository Initialization ===" -ForegroundColor Cyan
Write-Host "This script will set up Git for your project`n"

# Check if Git is installed
try {
    $gitVersion = git --version
    Write-Host "✓ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed!" -ForegroundColor Red
    Write-Host "`nPlease install Git first:"
    Write-Host "  Download from: https://git-scm.com/download/win"
    Write-Host "  Then run this script again.`n"
    exit 1
}

# Check if already initialized
if (Test-Path .git) {
    Write-Host "`n⚠ Git repository already initialized!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to continue anyway? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Cancelled." -ForegroundColor Yellow
        exit 0
    }
} else {
    Write-Host "`n✓ No existing Git repository found" -ForegroundColor Green
}

# Get user info
Write-Host "`n--- Git Configuration ---" -ForegroundColor Cyan
$userName = Read-Host "Enter your name for Git commits"
$userEmail = Read-Host "Enter your email for Git commits"

# Configure Git
Write-Host "`nConfiguring Git..." -ForegroundColor Cyan
git config --global user.name "$userName"
git config --global user.email "$userEmail"
git config --global init.defaultBranch main
Write-Host "✓ Git configured with your information" -ForegroundColor Green

# Initialize repository (if not already done)
if (-not (Test-Path .git)) {
    Write-Host "`nInitializing Git repository..." -ForegroundColor Cyan
    git init
    Write-Host "✓ Repository initialized" -ForegroundColor Green
}

# Check what will be committed
Write-Host "`n--- Files to be committed ---" -ForegroundColor Cyan
git status

Write-Host "`n--- Summary of files ---" -ForegroundColor Cyan
$filesToCommit = git ls-files --others --exclude-standard | Measure-Object
$trackedFiles = git ls-files | Measure-Object
Write-Host "New files to add: $($filesToCommit.Count)"
Write-Host "Already tracked: $($trackedFiles.Count)"

# Ask for confirmation
Write-Host "`n--- Ready to create first commit ---" -ForegroundColor Cyan
Write-Host "This will add all project files except those in .gitignore"
$confirm = Read-Host "Create initial commit? (y/n)"

if ($confirm -eq 'y') {
    Write-Host "`nAdding files..." -ForegroundColor Cyan
    git add .
    
    Write-Host "Creating commit..." -ForegroundColor Cyan
    git commit -m "Initial commit: Mountain huts scraper system

- Implemented scrapers for 3 sources (boudy.info, mountain-huts.net, mountainhuts.info)
- Database with 2,892 huts across 19 European countries
- Comprehensive data: owner, manager, contact info, opening hours
- Interactive Leaflet map with country filters
- Clean, organized repository structure
- Full documentation"
    
    Write-Host "`n✓ Initial commit created!" -ForegroundColor Green
    
    # Show the commit
    Write-Host "`n--- Commit Details ---" -ForegroundColor Cyan
    git log -1 --stat
    
} else {
    Write-Host "`nSkipped commit creation." -ForegroundColor Yellow
    Write-Host "You can commit later with:" -ForegroundColor Cyan
    Write-Host "  git add ."
    Write-Host "  git commit -m 'Your commit message'"
}

# Show next steps
Write-Host "`n=== Git Setup Complete! ===" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "  1. Check status:           git status"
Write-Host "  2. View history:           git log --oneline"
Write-Host "  3. Create a branch:        git checkout -b feature/your-feature"
Write-Host "  4. Connect to GitHub:      git remote add origin <your-repo-url>"
Write-Host "  5. Push to GitHub:         git push -u origin main"
Write-Host "`nFor more help, see: docs/GIT_SETUP_GUIDE.md`n"

# Offer to create a GitHub connection
$github = Read-Host "`nDo you want to connect to a GitHub repository now? (y/n)"
if ($github -eq 'y') {
    $repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/repo.git)"
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "`n✓ Remote 'origin' added: $repoUrl" -ForegroundColor Green
        Write-Host "`nTo push your code to GitHub, run:" -ForegroundColor Cyan
        Write-Host "  git push -u origin main`n"
    }
}

Write-Host "All done! Happy coding! 🎉`n" -ForegroundColor Green
