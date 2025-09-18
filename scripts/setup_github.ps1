# VSS Integration System - GitHub Repository Setup Script (PowerShell)
# This script prepares the project for GitHub deployment

param(
    [string]$RepositoryUrl = "https://github.com/hoanganh-hue/lalala1.git"
)

Write-Host "🚀 Setting up VSS Integration System for GitHub..." -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Status "Initializing Git repository..."
    git init
}

# Check if remote origin exists
try {
    $origin = git remote get-url origin 2>$null
    if ($origin) {
        Write-Status "Remote origin found: $origin"
    }
} catch {
    Write-Warning "No remote origin found. Please add your GitHub repository:"
    Write-Host "git remote add origin $RepositoryUrl"
    Write-Host "git branch -M main"
    Write-Host "git push -u origin main"
}

# Create necessary directories
Write-Status "Creating necessary directories..."
$directories = @(
    ".github/workflows",
    ".github/ISSUE_TEMPLATE", 
    "scripts",
    "docs"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Status "Created directory: $dir"
    }
}

# Check if pre-commit is available
try {
    pre-commit --version | Out-Null
    Write-Status "Setting up pre-commit hooks..."
    pre-commit install
    Write-Status "Pre-commit hooks installed successfully"
} catch {
    Write-Warning "pre-commit not found. Install with: pip install pre-commit"
}

Write-Status "GitHub repository setup completed successfully!"
Write-Status "Next steps:"
Write-Host "1. Review and customize the generated files"
Write-Host "2. Add your GitHub repository as remote origin"
Write-Host "3. Push your code to GitHub"
Write-Host "4. Enable GitHub Actions and security features"
Write-Host "5. Set up branch protection rules"

Write-Warning "Don't forget to:"
Write-Host "- Update repository description and topics"
Write-Host "- Add appropriate license"
Write-Host "- Configure branch protection rules"
Write-Host "- Set up automated releases"
Write-Host "- Enable security alerts and Dependabot"

Write-Host "🎉 VSS Integration System is ready for GitHub!" -ForegroundColor Blue
