# 🚀 Quick Start - Security CI Templates

**Get security scanning in your project in under 5 minutes!**

---

## 📋 What You Get

✅ **7 Ready-to-use CI templates** - Copy, paste, commit!
✅ **3 GitHub Actions workflows** - Full pipeline, simple scan, dependency bot
✅ **1 GitLab CI pipeline** - Complete 4-stage security workflow
✅ **1 Jenkins pipeline** - Parameterized with security gates
✅ **1 Pre-commit config** - Catch issues before committing
✅ **1-command setup script** - Automated installation

---

## ⚡ Fastest Setup (GitHub Actions)

**30 seconds to security scanning:**

```bash
# 1. Go to your project
cd your-project/

# 2. Copy the simple scan template
mkdir -p .github/workflows
curl -o .github/workflows/security.yml https://raw.githubusercontent.com/.../simple-security-scan.yml

# 3. Commit and push
git add .github/workflows/security.yml
git commit -m "ci: Add security scanning"
git push
```

**Done!** Security scan runs on every push/PR.

---

## 🎯 Automated Setup (All Platforms)

**Use the setup script:**

```bash
# 1. Navigate to ci-templates
cd GP-CONSULTING/2-App-Sec-Fixes/ci-templates/

# 2. Run setup (interactive)
./setup.sh

# Follow prompts to:
#   - Detect your CI platform (or choose one)
#   - Select template type
#   - Auto-install pre-commit hooks
#   - Update .gitignore

# 3. Review and commit
git add .
git commit -m "ci: Add security scanning pipeline"
git push
```

---

## 📦 Manual Setup (Platform Specific)

### GitHub Actions

**Option 1: Full Pipeline (Recommended)**

```bash
cd your-project/
mkdir -p .github/workflows

# Copy template
cp /path/to/ci-templates/github-actions/security-scan-and-fix.yml .github/workflows/

# Commit
git add .github/workflows/
git commit -m "ci: Add comprehensive security pipeline"
git push
```

**Features:**
- Scans: Bandit, Semgrep, Gitleaks, npm audit, pip-audit
- Auto-fixes vulnerabilities
- Creates PR with fixes
- Blocks merge on critical issues

**Option 2: Simple Scan (Fast)**

```bash
cp /path/to/ci-templates/github-actions/simple-security-scan.yml .github/workflows/

git add .github/workflows/
git commit -m "ci: Add simple security scan"
git push
```

**Features:**
- Quick feedback (< 10 min)
- Essential scanners only
- Fails on HIGH+ issues

**Option 3: Dependency Bot (Weekly)**

```bash
cp /path/to/ci-templates/github-actions/dependency-update-bot.yml .github/workflows/

git add .github/workflows/
git commit -m "ci: Add dependency update bot"
git push
```

**Features:**
- Weekly automated updates
- npm + pip vulnerability fixes
- Creates PR with changes

---

### GitLab CI

```bash
cd your-project/

# Copy template to project root
cp /path/to/ci-templates/gitlab-ci/.gitlab-ci.yml .

# Commit
git add .gitlab-ci.yml
git commit -m "ci: Add security scanning pipeline"
git push
```

**Features:**
- 4-stage pipeline (scan → fix → gate → report)
- Parallel scanning for speed
- SAST report integration
- HTML report generation

---

### Jenkins

```bash
cd your-project/

# Copy Jenkinsfile
cp /path/to/ci-templates/jenkins/Jenkinsfile .

# Commit
git add Jenkinsfile
git commit -m "ci: Add security scanning pipeline"
git push

# Then in Jenkins:
# 1. Create new Pipeline job
# 2. Point to your repository
# 3. Jenkins auto-detects Jenkinsfile
```

**Features:**
- Parameterized builds (auto-fix on/off)
- Configurable security gates
- Email notifications
- HTML result publishing

---

### Pre-commit Hooks (Local Development)

```bash
cd your-project/

# Copy config
cp /path/to/ci-templates/pre-commit/.pre-commit-config.yaml .

# Install pre-commit (if not installed)
pip install pre-commit

# Activate hooks
pre-commit install

# Test
pre-commit run --all-files
```

**Features:**
- Runs automatically on `git commit`
- Catches secrets before they're committed
- Python/SQL/Terraform security checks
- Fast local feedback

---

## 🔧 Customization (Common)

### Change Security Thresholds

**GitHub Actions:**
```yaml
# In .github/workflows/security-scan-and-fix.yml
# Find the "Security Gate" job and edit:

if [ "$CRITICAL" -gt 0 ]; then  # Change 0 to allow some critical
  exit 1
fi

if [ "$HIGH" -gt 5 ]; then  # Change 5 to adjust threshold
  exit 1
fi
```

**GitLab CI:**
```yaml
# In .gitlab-ci.yml
# Find security-gate job and edit:

if [ "$CRITICAL_TOTAL" -gt 0 ]; then  # Change threshold
  exit 1
fi
```

**Jenkins:**
```groovy
// In Jenkinsfile
// Find Security Gate stage:

if (critical > 0) {  // Change 0 to allow some
    error("FAILED")
}
```

---

### Exclude Files/Directories

**For all scanners:**

```bash
# Create ignore files
echo "tests/" > .bandit
echo "node_modules/" >> .bandit

echo "tests/" > .semgrepignore
echo "**/*.test.js" >> .semgrepignore

echo "test/" > .gitleaksignore
```

---

### Add More Scanners

**Example: Add Trivy (container scanning)**

**GitHub Actions:**
```yaml
# Add to .github/workflows/security-scan-and-fix.yml
# In the security-scan job:

- name: Run Trivy
  run: |
    wget https://github.com/aquasecurity/trivy/releases/download/v0.48.0/trivy_0.48.0_Linux-64bit.tar.gz
    tar -xzf trivy_0.48.0_Linux-64bit.tar.gz
    ./trivy fs --format json --output trivy-results.json .
```

---

## 🎯 Platform-Specific Features

### GitHub Actions Only

**Enable GitHub Security Tab:**
- Results appear in repo → Security → Code scanning alerts
- Template includes SARIF upload
- Integration with Dependabot

**Enable Branch Protection:**
```
Settings → Branches → Add rule
✅ Require status checks: security-scan
```

---

### GitLab CI Only

**View Security Dashboard:**
- Navigate to: Project → Security & Compliance → Security Dashboard
- SAST findings appear automatically
- Merge request security widget

---

### Jenkins Only

**Parameterized Builds:**
```
Build with Parameters:
- RUN_AUTO_FIX: true/false
- FAIL_ON_CRITICAL: true/false
- SCAN_LEVEL: full/quick/critical-only
```

---

## 📊 What Happens After Setup

### First Run

**GitHub Actions:**
1. Workflow triggers on push
2. Scans your code (5-15 min)
3. Results appear in Actions tab
4. If issues found:
   - Auto-fix runs
   - PR created with fixes
5. Security gate passes/fails

**GitLab CI:**
1. Pipeline starts on commit
2. Parallel scanning (faster)
3. Results in pipeline view
4. Security dashboard updated
5. Merge request widget shows results

**Jenkins:**
1. Build triggered
2. Scanners run sequentially
3. Results archived
4. HTML report published
5. Email sent if failed

---

## 🐛 Troubleshooting

### "Scanner not found"

**Solution:**
```yaml
# Templates install scanners automatically
# If manual install needed:
pip install bandit semgrep pip-audit
```

### "Too many false positives"

**Solution:**
```bash
# Add to code:
password = "test"  # nosec B105 - Test fixture

# Or create ignore file:
echo "tests/" > .bandit
```

### "Pipeline takes too long"

**Solution:**
```bash
# Use simple template for faster feedback
cp simple-security-scan.yml .github/workflows/

# Or run scanners in parallel (already done in templates)
```

---

## 📚 Examples

### GitHub Actions - View Results

```bash
# In your repo on GitHub:
1. Go to "Actions" tab
2. Click on latest workflow run
3. Expand "Security Scan" job
4. See detailed results

# Or check Security tab:
1. Go to "Security" tab
2. Click "Code scanning alerts"
3. View all findings
```

### GitLab CI - View Results

```bash
# In your repo on GitLab:
1. Go to CI/CD → Pipelines
2. Click on latest pipeline
3. View each stage (scan, fix, gate, report)

# Or Security Dashboard:
1. Security & Compliance → Security Dashboard
2. View all vulnerabilities
```

### Jenkins - View Results

```bash
# In Jenkins:
1. Click on your job
2. Click on latest build number
3. View "Console Output"
4. Click "Security Scan Results" for HTML report
```

---

## 🎉 Success Checklist

After setup, verify:

- [ ] Template copied to correct location
- [ ] Committed and pushed to git
- [ ] CI pipeline ran successfully (or check errors)
- [ ] Results visible in CI platform
- [ ] Security gate working (try committing a test secret)
- [ ] (Optional) Branch protection enabled
- [ ] (Optional) Pre-commit hooks working locally

---

## 🔗 Next Steps

1. **Review the first scan results**
   - Check what was found
   - Review auto-fix PRs (if created)

2. **Adjust thresholds if needed**
   - Too strict? Increase thresholds
   - Too permissive? Decrease thresholds

3. **Enable branch protection**
   - Require security scans to pass
   - Block merges on critical issues

4. **Add team notifications**
   - Slack integration
   - Email alerts
   - MS Teams webhooks

5. **Customize for your stack**
   - Add language-specific scanners
   - Add framework-specific rules

---

## 📖 Full Documentation

- **[Complete README](README.md)** - All templates explained
- **[GitHub Actions Template](github-actions/security-scan-and-fix.yml)** - Full pipeline
- **[GitLab CI Template](gitlab-ci/.gitlab-ci.yml)** - Complete pipeline
- **[Jenkins Template](jenkins/Jenkinsfile)** - Parameterized pipeline
- **[Pre-commit Config](pre-commit/.pre-commit-config.yaml)** - Local hooks

---

**Version:** 1.0
**Platform Support:** GitHub Actions, GitLab CI, Jenkins
**Setup Time:** 2-10 minutes
**Maintained:** Yes
