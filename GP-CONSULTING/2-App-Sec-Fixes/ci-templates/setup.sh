#!/bin/bash

# ============================================================================
# CI Template Setup Script
# Quickly add security scanning to your project
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║       Security CI Template Setup                        ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Detect project root (go up until we find .git)
PROJECT_ROOT="$(pwd)"
while [[ ! -d "$PROJECT_ROOT/.git" && "$PROJECT_ROOT" != "/" ]]; do
    PROJECT_ROOT="$(dirname "$PROJECT_ROOT")"
done

if [ "$PROJECT_ROOT" = "/" ]; then
    echo "⚠️  Warning: No git repository found. Using current directory."
    PROJECT_ROOT="$(pwd)"
fi

echo "Project root: $PROJECT_ROOT"
echo ""

# ============================================================================
# Detect CI Platform
# ============================================================================

CI_PLATFORM=""

if [ -d "$PROJECT_ROOT/.github" ]; then
    CI_PLATFORM="github"
    echo "✅ Detected: GitHub Actions"
elif [ -f "$PROJECT_ROOT/.gitlab-ci.yml" ]; then
    CI_PLATFORM="gitlab"
    echo "✅ Detected: GitLab CI"
elif [ -f "$PROJECT_ROOT/Jenkinsfile" ]; then
    CI_PLATFORM="jenkins"
    echo "✅ Detected: Jenkins"
else
    echo "❓ No CI platform detected. Choose one:"
    echo "  1) GitHub Actions"
    echo "  2) GitLab CI"
    echo "  3) Jenkins"
    echo "  4) All (install all templates)"
    echo "  5) Pre-commit hooks only"
    read -p "Enter choice (1-5): " choice

    case $choice in
        1) CI_PLATFORM="github" ;;
        2) CI_PLATFORM="gitlab" ;;
        3) CI_PLATFORM="jenkins" ;;
        4) CI_PLATFORM="all" ;;
        5) CI_PLATFORM="pre-commit" ;;
        *) echo "❌ Invalid choice"; exit 1 ;;
    esac
fi

echo ""

# ============================================================================
# Install Templates
# ============================================================================

install_github() {
    echo "→ Installing GitHub Actions templates..."

    mkdir -p "$PROJECT_ROOT/.github/workflows"

    # Ask which template
    echo ""
    echo "Choose GitHub Actions template:"
    echo "  1) Full pipeline (scan + auto-fix + PR) - Recommended"
    echo "  2) Simple scan (fast feedback)"
    echo "  3) Dependency bot (weekly updates)"
    echo "  4) All templates"
    read -p "Enter choice (1-4): " template_choice

    case $template_choice in
        1)
            cp "$SCRIPT_DIR/github-actions/security-scan-and-fix.yml" "$PROJECT_ROOT/.github/workflows/"
            echo "  ✅ Installed: security-scan-and-fix.yml"
            ;;
        2)
            cp "$SCRIPT_DIR/github-actions/simple-security-scan.yml" "$PROJECT_ROOT/.github/workflows/"
            echo "  ✅ Installed: simple-security-scan.yml"
            ;;
        3)
            cp "$SCRIPT_DIR/github-actions/dependency-update-bot.yml" "$PROJECT_ROOT/.github/workflows/"
            echo "  ✅ Installed: dependency-update-bot.yml"
            ;;
        4)
            cp "$SCRIPT_DIR/github-actions/"*.yml "$PROJECT_ROOT/.github/workflows/"
            echo "  ✅ Installed: All templates"
            ;;
    esac

    echo ""
    echo "✅ GitHub Actions templates installed!"
    echo "   Location: .github/workflows/"
    echo "   Next: git add .github/workflows/ && git commit -m 'ci: Add security scanning'"
}

install_gitlab() {
    echo "→ Installing GitLab CI template..."

    cp "$SCRIPT_DIR/gitlab-ci/.gitlab-ci.yml" "$PROJECT_ROOT/.gitlab-ci.yml"

    echo ""
    echo "✅ GitLab CI template installed!"
    echo "   Location: .gitlab-ci.yml"
    echo "   Next: git add .gitlab-ci.yml && git commit -m 'ci: Add security scanning'"
}

install_jenkins() {
    echo "→ Installing Jenkins template..."

    cp "$SCRIPT_DIR/jenkins/Jenkinsfile" "$PROJECT_ROOT/Jenkinsfile"

    echo ""
    echo "✅ Jenkins template installed!"
    echo "   Location: Jenkinsfile"
    echo "   Next: git add Jenkinsfile && git commit -m 'ci: Add security scanning'"
    echo "   Then: Create Pipeline job in Jenkins pointing to this repo"
}

install_precommit() {
    echo "→ Installing pre-commit hooks..."

    cp "$SCRIPT_DIR/pre-commit/.pre-commit-config.yaml" "$PROJECT_ROOT/.pre-commit-config.yaml"

    # Install pre-commit if available
    if command -v pre-commit &> /dev/null; then
        cd "$PROJECT_ROOT"
        pre-commit install
        echo "  ✅ pre-commit hooks installed and activated"
    else
        echo "  ⚠️  pre-commit not found. Install with: pip install pre-commit"
        echo "  Then run: pre-commit install"
    fi

    echo ""
    echo "✅ Pre-commit hooks installed!"
    echo "   Location: .pre-commit-config.yaml"
    echo "   Hooks will run automatically on 'git commit'"
}

# Run installations based on choice
case $CI_PLATFORM in
    github)
        install_github
        install_precommit
        ;;
    gitlab)
        install_gitlab
        install_precommit
        ;;
    jenkins)
        install_jenkins
        install_precommit
        ;;
    all)
        install_github
        install_gitlab
        install_jenkins
        install_precommit
        ;;
    pre-commit)
        install_precommit
        ;;
esac

# ============================================================================
# Create .gitignore entries
# ============================================================================

echo ""
echo "→ Updating .gitignore..."

GITIGNORE="$PROJECT_ROOT/.gitignore"

if [ -f "$GITIGNORE" ]; then
    # Add security scan results to gitignore
    if ! grep -q "security-results" "$GITIGNORE"; then
        cat >> "$GITIGNORE" << 'EOF'

# Security scan results
security-results/
*-results.json
bandit-results.json
semgrep-results.json
gitleaks-results.json
npm-audit-results.json
pip-audit-results.json
.secrets.baseline
EOF
        echo "  ✅ Updated .gitignore"
    fi
else
    echo "  ⚠️  No .gitignore found (skipping)"
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SETUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What was installed:"

if [ "$CI_PLATFORM" = "github" ] || [ "$CI_PLATFORM" = "all" ]; then
    echo "  ✅ GitHub Actions workflows"
fi

if [ "$CI_PLATFORM" = "gitlab" ] || [ "$CI_PLATFORM" = "all" ]; then
    echo "  ✅ GitLab CI pipeline"
fi

if [ "$CI_PLATFORM" = "jenkins" ] || [ "$CI_PLATFORM" = "all" ]; then
    echo "  ✅ Jenkins pipeline"
fi

echo "  ✅ Pre-commit hooks"
echo "  ✅ .gitignore updates"
echo ""
echo "Next steps:"
echo "  1. Review the installed templates"
echo "  2. Customize thresholds if needed"
echo "  3. Commit and push:"
echo "     git add ."
echo "     git commit -m 'ci: Add security scanning pipeline'"
echo "     git push"
echo ""
echo "  4. (Optional) Set up branch protection in your repo settings"
echo ""
echo "Documentation: $SCRIPT_DIR/README.md"
echo ""
