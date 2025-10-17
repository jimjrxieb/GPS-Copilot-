# CI/CD Security Templates

**Copy-paste ready CI/CD templates for automated security scanning and remediation**

Perfect for adding security checks to any project in minutes!

---

## 📁 Available Templates

| Platform | Template | Purpose | Setup Time |
|----------|----------|---------|------------|
| **GitHub Actions** | [security-scan-and-fix.yml](github-actions/security-scan-and-fix.yml) | Full scan + auto-fix + PR creation | 5 min |
| **GitHub Actions** | [simple-security-scan.yml](github-actions/simple-security-scan.yml) | Quick security check | 2 min |
| **GitHub Actions** | [dependency-update-bot.yml](github-actions/dependency-update-bot.yml) | Weekly dependency updates | 3 min |
| **GitLab CI** | [.gitlab-ci.yml](gitlab-ci/.gitlab-ci.yml) | Complete security pipeline | 5 min |
| **Jenkins** | [Jenkinsfile](jenkins/Jenkinsfile) | Groovy pipeline with gates | 10 min |

---

## 🚀 Quick Start

### GitHub Actions

**1. Choose your template:**

<details>
<summary><strong>Option A: Full Pipeline (Recommended)</strong></summary>

Includes scanning, auto-fixing, PR creation, and security gates.

```bash
# Copy to your project
cp github-actions/security-scan-and-fix.yml .github/workflows/

# Commit and push
git add .github/workflows/security-scan-and-fix.yml
git commit -m "ci: Add security scanning pipeline"
git push
```

**Features:**
- ✅ Runs Bandit, Semgrep, Gitleaks
- ✅ Auto-fixes vulnerabilities
- ✅ Creates PR with fixes
- ✅ Blocks merge on critical issues
- ✅ Uploads to GitHub Security tab

**When it runs:**
- Every push to main/develop/staging
- Every pull request
- Daily at 2 AM UTC
- Manual trigger

</details>

<details>
<summary><strong>Option B: Simple Scan (Fast)</strong></summary>

Lightweight security check for quick feedback.

```bash
cp github-actions/simple-security-scan.yml .github/workflows/

git add .github/workflows/simple-security-scan.yml
git commit -m "ci: Add simple security scan"
git push
```

**Features:**
- ✅ Fast scanning (< 10 minutes)
- ✅ Bandit, Gitleaks, Semgrep
- ✅ Fails on HIGH+ issues
- ✅ npm/pip audit

**When it runs:**
- Every push
- Every pull request

</details>

<details>
<summary><strong>Option C: Dependency Bot (Weekly)</strong></summary>

Automated weekly dependency security updates.

```bash
cp github-actions/dependency-update-bot.yml .github/workflows/

git add .github/workflows/dependency-update-bot.yml
git commit -m "ci: Add dependency update bot"
git push
```

**Features:**
- ✅ Weekly automated updates
- ✅ npm audit fix + pip-audit --fix
- ✅ Creates PR with changes
- ✅ Security-focused updates only

**When it runs:**
- Every Monday at 9 AM UTC
- Manual trigger

</details>

---

### GitLab CI

```bash
# Copy to project root
cp gitlab-ci/.gitlab-ci.yml .gitlab-ci.yml

# Commit and push
git add .gitlab-ci.yml
git commit -m "ci: Add security scanning pipeline"
git push
```

**Features:**
- ✅ Multi-stage pipeline (scan → fix → gate → report)
- ✅ Parallel scanning for speed
- ✅ Security gate with thresholds
- ✅ HTML report generation
- ✅ SAST report integration

**Pipeline stages:**
1. security-scan (Bandit, Semgrep, Gitleaks, npm, pip)
2. auto-fix (Automated remediation)
3. security-gate (Pass/fail based on thresholds)
4. report (Generate HTML report)

---

### Jenkins

```bash
# Copy to project root
cp jenkins/Jenkinsfile Jenkinsfile

# In Jenkins:
# 1. Create new Pipeline job
# 2. Point to your repository
# 3. Jenkins will auto-detect Jenkinsfile

# Commit
git add Jenkinsfile
git commit -m "ci: Add security scanning pipeline"
git push
```

**Features:**
- ✅ Parameterized builds (auto-fix on/off, scan level)
- ✅ Parallel dependency scanning
- ✅ Email notifications on failure
- ✅ HTML result publishing
- ✅ Configurable security gates

**Parameters:**
- `RUN_AUTO_FIX` - Enable/disable automatic fixes (default: true)
- `FAIL_ON_CRITICAL` - Fail build on critical issues (default: true)
- `SCAN_LEVEL` - full, quick, or critical-only (default: full)

---

## 🔧 Customization Guide

### Adjust Security Thresholds

**GitHub Actions:**
```yaml
# In security-scan-and-fix.yml, edit security-gate job:
- name: Check security threshold
  run: |
    CRITICAL=${{ needs.security-scan.outputs.critical-count }}
    HIGH=${{ needs.security-scan.outputs.high-count }}

    # Fail if critical issues exist
    if [ "$CRITICAL" -gt 0 ]; then  # Change to -gt 5 to allow 5 critical
      exit 1
    fi

    # Fail if too many high issues
    if [ "$HIGH" -gt 5 ]; then  # Change threshold here
      exit 1
    fi
```

**GitLab CI:**
```yaml
# In .gitlab-ci.yml, edit security-gate job:
if [ "$CRITICAL_TOTAL" -gt 0 ]; then  # Change threshold
  exit 1
fi

if [ "$HIGH_TOTAL" -gt 10 ]; then  # Change threshold
  exit 1
fi
```

**Jenkins:**
```groovy
// In Jenkinsfile, edit Security Gate stage:
if (params.FAIL_ON_CRITICAL && critical > 0) {  // Change > 0 to > 5
    error("FAILED")
}

if (high > 10) {  // Change threshold
    unstable("WARNING")
}
```

---

### Add Custom Scanners

**Example: Add Trivy (container scanning)**

**GitHub Actions:**
```yaml
- name: Run Trivy
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: '.'
    format: 'json'
    output: 'trivy-results.json'
```

**GitLab CI:**
```yaml
trivy-scan:
  stage: security-scan
  image: aquasec/trivy:latest
  script:
    - trivy fs --format json --output trivy-results.json .
  artifacts:
    paths:
      - trivy-results.json
```

---

### Exclude Files/Directories

**For Bandit:**
```yaml
# Add to scanner command
bandit -r . -x ./tests,./venv -f json -o bandit-results.json
```

**For Semgrep:**
```yaml
# Create .semgrepignore file
echo "tests/" > .semgrepignore
echo "node_modules/" >> .semgrepignore
```

**For Gitleaks:**
```yaml
# Create .gitleaksignore file
echo "test/" > .gitleaksignore
echo "*.test.js" >> .gitleaksignore
```

---

### Schedule Customization

**GitHub Actions:**
```yaml
on:
  schedule:
    # Daily at 2 AM UTC
    - cron: '0 2 * * *'

    # Every Monday at 9 AM
    - cron: '0 9 * * 1'

    # Every 6 hours
    - cron: '0 */6 * * *'
```

**GitLab CI:**
```yaml
# Use GitLab Pipeline Schedules in UI
# Settings → CI/CD → Schedules → New Schedule
```

---

## 📊 What Each Template Does

### GitHub Actions: security-scan-and-fix.yml

**Complete workflow:**

```
1. Security Scan (Job 1)
   ├─→ Bandit (Python SAST)
   ├─→ Semgrep (Multi-language SAST)
   ├─→ Gitleaks (Secrets)
   ├─→ npm audit (Node.js deps)
   ├─→ pip-audit (Python deps)
   └─→ Generate summary

2. Auto-Fix (Job 2) - Runs if findings > 0
   ├─→ Apply automated fixes
   ├─→ Create new branch
   ├─→ Commit changes
   └─→ Create Pull Request

3. Security Gate (Job 3)
   ├─→ Check thresholds
   ├─→ FAIL if critical > 0
   └─→ WARN if high > 5

4. SARIF Upload (Job 4)
   └─→ Upload to GitHub Security tab
```

**Outputs:**
- PR with automated fixes (if needed)
- Security report comment on PR
- Results in GitHub Security tab
- Artifacts with JSON results

---

### GitHub Actions: simple-security-scan.yml

**Fast security check:**

```
1. Install scanners (Bandit, Semgrep, Gitleaks)
2. Run all scanners in parallel
3. Fail build if HIGH+ issues found
4. Quick feedback (< 10 minutes)
```

**Use when:**
- You want fast CI feedback
- Don't need auto-fix
- Simple pass/fail is enough

---

### GitHub Actions: dependency-update-bot.yml

**Weekly dependency updates:**

```
1. Run npm audit (if package.json exists)
2. Run pip-audit (if requirements.txt exists)
3. Apply automated fixes (npm audit fix, pip-audit --fix)
4. Create PR with:
   - Before/after vulnerability counts
   - List of updated packages
   - Testing checklist
```

**Auto-labels:** `security`, `dependencies`, `automated`

---

### GitLab CI: .gitlab-ci.yml

**4-stage pipeline:**

```
Stage 1: security-scan
├─→ bandit-scan (Python)
├─→ semgrep-scan (Multi-lang)
├─→ gitleaks-scan (Secrets)
├─→ npm-audit (Node deps)
└─→ pip-audit (Python deps)

Stage 2: auto-fix
├─→ auto-fix-secrets
└─→ auto-fix-dependencies

Stage 3: security-gate
└─→ Check thresholds & fail/warn

Stage 4: report
└─→ Generate HTML report
```

**Artifacts:**
- SAST reports (integrated with GitLab Security Dashboard)
- JSON results (30 days retention)
- HTML report (90 days retention)
- Fix patches (7 days retention)

---

### Jenkins: Jenkinsfile

**Parameterized pipeline:**

```
Parameters:
  • RUN_AUTO_FIX (true/false)
  • FAIL_ON_CRITICAL (true/false)
  • SCAN_LEVEL (full/quick/critical-only)

Stages:
1. Setup
2. Security Scan - Python (Bandit)
3. Security Scan - Secrets (Gitleaks)
4. Security Scan - Multi-Language (Semgrep)
5. Security Scan - Dependencies (npm + pip in parallel)
6. Security Analysis (aggregate results)
7. Auto-Fix (if enabled)
8. Security Gate (configurable thresholds)

Post-actions:
  • Archive artifacts
  • Publish HTML report
  • Email on failure
```

---

## 🎯 Best Practices

### 1. Start Simple, Then Enhance

```bash
# Week 1: Add simple scan
cp simple-security-scan.yml .github/workflows/

# Week 2: Add full pipeline
cp security-scan-and-fix.yml .github/workflows/

# Week 3: Add dependency bot
cp dependency-update-bot.yml .github/workflows/
```

### 2. Use Branch Protection

**GitHub:**
```
Settings → Branches → Branch protection rules
✅ Require status checks to pass before merging
✅ Require security-scan job to pass
```

### 3. Configure Notifications

**Slack integration (GitHub Actions):**
```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Security scan failed: ${{ github.repository }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 4. Create Security Policy

Add `SECURITY.md`:
```markdown
# Security Policy

## Automated Security Scanning

We use automated security scanning on:
- Every commit
- Every PR
- Daily schedule

Critical issues block merges.

## Reporting Vulnerabilities

Email: security@example.com
```

### 5. Review Auto-Fix PRs

**Always review** automated security fix PRs:
- Run tests locally
- Check for breaking changes
- Verify fixes don't introduce regressions

---

## 🔍 Troubleshooting

### Scanner Installation Fails

**Problem:** `pip install bandit` fails

**Solution:**
```yaml
# Use specific versions
- pip install bandit==1.7.5 semgrep==1.45.0

# Or use cache
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

---

### Too Many False Positives

**Problem:** Bandit/Semgrep reports false positives

**Solution:**
```bash
# Create ignore files
echo "tests/" > .bandit
echo "**/*.test.js" > .semgrepignore

# Or use inline comments
password = "test123"  # nosec B105 - Test fixture only
```

---

### Pipeline Takes Too Long

**Problem:** Security scan > 30 minutes

**Solution:**
```yaml
# Run scanners in parallel
jobs:
  bandit:
    runs-on: ubuntu-latest
  semgrep:
    runs-on: ubuntu-latest
  gitleaks:
    runs-on: ubuntu-latest

# Or use simple template for faster feedback
cp simple-security-scan.yml .github/workflows/
```

---

### Auto-Fix Creates Breaking Changes

**Problem:** npm audit fix breaks application

**Solution:**
```yaml
# Disable force flag
- npm audit fix  # Remove --force

# Or run in separate job
- npm audit fix --dry-run  # Test first
```

---

## 📚 Additional Resources

### Scanner Documentation

- **Bandit:** https://bandit.readthedocs.io/
- **Semgrep:** https://semgrep.dev/docs/
- **Gitleaks:** https://github.com/gitleaks/gitleaks
- **npm audit:** https://docs.npmjs.com/cli/audit
- **pip-audit:** https://pypi.org/project/pip-audit/

### CI/CD Platform Docs

- **GitHub Actions:** https://docs.github.com/actions
- **GitLab CI:** https://docs.gitlab.com/ee/ci/
- **Jenkins:** https://www.jenkins.io/doc/book/pipeline/

### Security Standards

- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **CWE Top 25:** https://cwe.mitre.org/top25/
- **NIST 800-53:** https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final

---

## 🎉 Quick Copy-Paste

### Minimal GitHub Actions Security Scan

```yaml
name: Security
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install bandit && bandit -r . -ll
      - run: |
          wget -q https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
          tar -xzf gitleaks_8.18.0_linux_x64.tar.gz
          ./gitleaks detect --source . --no-git
```

### Minimal GitLab CI Security Scan

```yaml
security:
  image: python:3.11
  script:
    - pip install bandit
    - bandit -r . -ll
```

### Minimal Jenkins Security Scan

```groovy
pipeline {
    agent any
    stages {
        stage('Security') {
            steps {
                sh 'pip install bandit && bandit -r . -ll'
            }
        }
    }
}
```

---

**Version:** 1.0
**Last Updated:** 2025-10-14
**Tested With:** GitHub Actions, GitLab CI, Jenkins
**License:** MIT
