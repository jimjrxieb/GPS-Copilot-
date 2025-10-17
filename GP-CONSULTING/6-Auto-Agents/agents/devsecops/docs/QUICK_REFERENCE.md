# Quick Reference: Pipeline Debugging

**TL;DR:** Fast commands for when you just need to fix a broken pipeline NOW.

---

## 🚨 Pipeline Failing? Start Here

```bash
# 1. Check what's failing
gh run list --repo <owner/repo> --limit 3

# 2. Get the run ID of the failed run
# Example output: "completed  failure  commit-msg  workflow  branch  trigger  18303577082  1m  timestamp"
#                                                                      ^^^^^^^^^^^
#                                                                      This is the run ID

# 3. Run the automated debugger
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-devsecops
python3 pipeline_debugger.py <owner/repo>
```

---

## ⚡ Most Common Fixes (Copy-Paste Ready)

### Fix 1: "Connection timeout" or "Authentication failed"
**Cause:** Missing API key/secret (SonarQube, GitGuardian, etc.)

**Quick Fix:** Add `continue-on-error: true`

```yaml
# In .github/workflows/<workflow>.yml
- name: SonarQube Scan
  continue-on-error: true  # <-- ADD THIS LINE
  uses: sonarsource/sonarqube-scan-action@master
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

### Fix 2: "Deprecated action version"
**Cause:** Using old GitHub Action version

**Quick Fix:** Update version number

```bash
# Find deprecated actions
grep -r "upload-artifact@v3" .github/workflows/

# Replace in file (example)
sed -i 's/upload-artifact@v3/upload-artifact@v4/g' .github/workflows/gh_actions.yml
```

---

### Fix 3: "X CRITICAL vulnerabilities found"
**Cause:** Real security issues in dependencies

**DO NOT skip the scan!** Fix the vulnerabilities.

```bash
# 1. Check what's vulnerable
trivy fs . --severity CRITICAL

# 2. Upgrade dependencies (example for Maven)
# Edit pom.xml, update Spring Boot version
vim pom.xml

# 3. Test locally
mvn clean package
```

See: [SECURITY_ACHIEVEMENT.md](../../GP-PROJECTS/CLOUD-project/SECURITY_ACHIEVEMENT.md) for full CVE remediation workflow.

---

### Fix 4: "Tests failed"
**Temporary Fix:** Skip tests

```yaml
# In .github/workflows/<workflow>.yml
- name: Build with Maven
  run: mvn package -DskipTests  # <-- ADD -DskipTests
```

**Proper Fix:** Debug and fix the tests

```bash
# Run tests locally
mvn test

# View test reports
cat target/surefire-reports/*.txt
```

---

### Fix 5: Job fails at "Set up job"
**Cause:** Missing required secrets OR job needs disabling

**Option A:** Disable the job temporarily

```yaml
# In .github/workflows/<workflow>.yml
docker_build:
  if: false  # <-- ADD THIS LINE
  name: Build and Push Docker Image
  runs-on: ubuntu-latest
```

**Option B:** Add required secrets

```bash
gh secret set DOCKER_USER --body "your_username" --repo <owner/repo>
gh secret set DOCKER_CRED --body "your_token" --repo <owner/repo>
```

---

### Fix 6: "Download failed" or "404 Not Found"
**Cause:** External dependency unavailable

**Quick Fix:** Make optional

```yaml
- name: Install OWASP Dependency-Check
  continue-on-error: true  # <-- ADD THIS LINE
  run: |
    curl -LO https://example.com/tool.zip
    unzip tool.zip
```

---

## 🔍 Quick Diagnosis Commands

```bash
# Which job failed?
gh run view <run-id> --repo <owner/repo> --json jobs \
  --jq '.jobs[] | select(.conclusion=="failure") | .name'

# Which step in that job failed?
gh run view <run-id> --repo <owner/repo> --json jobs \
  --jq '.jobs[] | select(.name=="build") | .steps[] | select(.conclusion=="failure") | .name'

# Show me the error
gh run view <run-id> --repo <owner/repo> --log-failed | grep -i error
```

---

## 📝 Standard Fix Workflow

```bash
# 1. Make your fix (edit .github/workflows/<workflow>.yml)

# 2. Commit and push
git add .github/workflows/
git commit -m "Fix: Make SonarQube scan optional"
git push

# 3. Wait for workflow to run (~2 minutes)
sleep 120

# 4. Check if it passed
gh run list --repo <owner/repo> --limit 2

# 5. If still failing, repeat
```

---

## 🎯 Decision Tree

```
Pipeline failing?
│
├─ Shows "Connection timeout" or "Auth failed"
│  └─> Add: continue-on-error: true
│
├─ Shows "X CRITICAL vulnerabilities"
│  └─> FIX THE VULNS (don't skip scan!)
│
├─ Shows "cannot find symbol"
│  └─> Fix code (imports, dependencies)
│
├─ Shows "Tests failed"
│  ├─> Temp: Add -DskipTests
│  └─> Proper: Fix tests
│
├─ Shows "deprecated version"
│  └─> Update action version (v3 → v4)
│
├─ Fails at "Set up job"
│  ├─> Add secrets OR
│  └─> Disable job: if: false
│
└─ Shows "Download failed"
   └─> Add: continue-on-error: true
```

---

## 🛠️ The Magic Sleep Command

```bash
# Wait N seconds, then run command
sleep <seconds> && <command>

# Examples:
sleep 60 && gh run list --limit 2         # Wait 1 minute
sleep 120 && gh run list --limit 2        # Wait 2 minutes
sleep 180 && gh run list --limit 2        # Wait 3 minutes

# Why? Workflows take time to run. Sleep waits for completion.
```

---

## 🚀 Full Automation Script

```bash
#!/bin/bash
# auto_fix_pipeline.sh - Automated pipeline debugging

REPO="$1"

if [ -z "$REPO" ]; then
    echo "Usage: ./auto_fix_pipeline.sh owner/repo"
    exit 1
fi

echo "🔍 Checking pipeline status for $REPO..."
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/GP-devsecops

python3 pipeline_debugger.py "$REPO"

if [ $? -eq 0 ]; then
    echo ""
    echo "📚 See recommendations above and apply fixes to .github/workflows/"
    echo ""
    echo "After fixing, monitor with:"
    echo "  sleep 120 && gh run list --repo $REPO --limit 2"
fi
```

**Usage:**
```bash
chmod +x auto_fix_pipeline.sh
./auto_fix_pipeline.sh jimjrxieb/CLOUD-project
```

---

## 📚 Full Documentation

**Detailed guides:**
- [CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md](./CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md) - Complete workflow
- [README.md](./README.md) - Tool documentation
- [SECURITY_ACHIEVEMENT.md](../../GP-PROJECTS/CLOUD-project/SECURITY_ACHIEVEMENT.md) - CVE remediation

**Real examples:**
- [CLOUD-project](../../GP-PROJECTS/CLOUD-project) - Working reference implementation
- [PIPELINE_SUCCESS.md](../../GP-PROJECTS/CLOUD-project/PIPELINE_SUCCESS.md) - Success story

---

## 💡 Pro Tips

1. **Always check locally first:**
   ```bash
   mvn clean package    # Test build
   trivy fs . --severity CRITICAL    # Test security
   ```

2. **One fix at a time:**
   - Don't batch multiple changes
   - Easier to debug which fix worked

3. **Use descriptive commits:**
   ```bash
   git commit -m "Fix: Make SonarQube optional (missing secrets)"
   # NOT: git commit -m "fix stuff"
   ```

4. **Optional ≠ Unimportant:**
   - Keep Trivy CRITICAL scan blocking
   - Make third-party tools optional (SonarQube, GitGuardian)

5. **Document your changes:**
   ```yaml
   # SonarQube Scan (optional - requires SONAR_TOKEN/SONAR_HOST_URL secrets)
   - name: SonarQube Scan
     continue-on-error: true
   ```

---

## ⚙️ File Locations

```
GP-copilot/
├── GP-CONSULTING-AGENTS/
│   └── GP-devsecops/
│       ├── README.md                              # Tool documentation
│       ├── QUICK_REFERENCE.md                     # This file
│       ├── CI_CD_PIPELINE_DEBUGGING_WORKFLOW.md   # Complete guide
│       └── pipeline_debugger.py                   # Automation script
│
└── GP-PROJECTS/
    └── CLOUD-project/
        ├── .github/workflows/
        │   ├── gh_actions.yml                     # Main CI/CD
        │   └── security_scan.yml                  # Security workflow
        ├── PIPELINE_SUCCESS.md                    # Success documentation
        ├── SECURITY_ACHIEVEMENT.md                # CVE remediation guide
        └── SECURITY_SCANNING.md                   # Security tools config
```

---

**Last Updated:** October 2025
**Status:** Production-ready ✅
