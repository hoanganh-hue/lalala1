#!/bin/bash

# VSS Integration System - GitHub Repository Setup Script
# This script prepares the project for GitHub deployment

set -e

echo "🚀 Setting up VSS Integration System for GitHub..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_status "Initializing Git repository..."
    git init
fi

# Check if remote origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    print_warning "No remote origin found. Please add your GitHub repository:"
    echo "git remote add origin https://github.com/hoanganh-hue/lalala1.git"
    echo "git branch -M main"
    echo "git push -u origin main"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p .github/workflows
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p scripts
mkdir -p docs

# Set up pre-commit hooks
print_status "Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_status "Pre-commit hooks installed successfully"
else
    print_warning "pre-commit not found. Install with: pip install pre-commit"
fi

# Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=127, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
EOF

# Create GitHub repository configuration
print_status "Creating GitHub repository configuration..."

# Create CODEOWNERS file
cat > .github/CODEOWNERS << 'EOF'
# Global code owners
* @hoanganh-hue

# Core system files
/src/ @hoanganh-hue
/main.py @hoanganh-hue
/requirements_v3.txt @hoanganh-hue

# Documentation
/docs/ @hoanganh-hue
*.md @hoanganh-hue

# Configuration
/.github/ @hoanganh-hue
/docker-compose.yml @hoanganh-hue
/Dockerfile @hoanganh-hue
EOF

# Create PULL_REQUEST_TEMPLATE.md
cat > .github/pull_request_template.md << 'EOF'
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or clearly documented)
- [ ] Tests added/updated for new functionality

## Related Issues
Closes #(issue number)
EOF

# Create FUNDING.yml for GitHub Sponsors
cat > .github/FUNDING.yml << 'EOF'
# These are supported funding model platforms

github: [hoanganh-hue]
patreon: # Replace with a single Patreon username
open_collective: # Replace with a single Open Collective name
ko_fi: # Replace with a single Ko-fi username
tidelift: # Replace with a single Tidelift platform-name/package-name e.g., npm/babel
community_bridge: # Replace with a single Community Bridge project-name e.g., cloud-foundry
liberapay: # Replace with a single Liberapay username
issuehunt: # Replace with a single IssueHunt username
otechie: # Replace with a single Otechie username
custom: # Replace with up to 4 custom sponsorship URLs
EOF

# Create SECURITY.md
cat > SECURITY.md << 'EOF'
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 3.1.x   | :white_check_mark: |
| 3.0.x   | :white_check_mark: |
| 2.0.x   | :x:                |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

Please report security vulnerabilities privately to maintainers.

### How to Report
1. Email: security@vss-integration.com
2. Include detailed description
3. Provide steps to reproduce
4. Include affected versions

### Response Timeline
- Initial response: 24 hours
- Status update: 72 hours
- Resolution: 7 days

## Security Measures

- All data encrypted in transit and at rest
- Regular security audits
- Dependency vulnerability scanning
- Secure coding practices
- Access control and authentication
EOF

print_status "GitHub repository setup completed successfully!"
print_status "Next steps:"
echo "1. Review and customize the generated files"
echo "2. Add your GitHub repository as remote origin"
echo "3. Push your code to GitHub"
echo "4. Enable GitHub Actions and security features"
echo "5. Set up branch protection rules"

print_warning "Don't forget to:"
echo "- Update repository description and topics"
echo "- Add appropriate license"
echo "- Configure branch protection rules"
echo "- Set up automated releases"
echo "- Enable security alerts and Dependabot"

echo -e "${BLUE}🎉 VSS Integration System is ready for GitHub!${NC}"
