# Quick Setup: Jade GHA Explainer for jimjrxieb/CLOUD-project

## Your Workflow Run

**Repository:** `jimjrxieb/CLOUD-project`
**Run ID:** `18300191954`
**Workflow:** Security scan pipeline

## Option 1: Use Jade Explain-GHA (Recommended)

This gives you AI-powered analysis with automatic artifact parsing.

### Setup (One-time)

```bash
# Authenticate GitHub CLI
gh auth login

# Follow prompts:
# - Select: GitHub.com
# - Protocol: HTTPS
# - Authenticate: Login with browser or paste token
```

### Run Analysis

```bash
# Basic analysis
jade explain-gha jimjrxieb/CLOUD-project 18300191954

# Save to file
jade explain-gha jimjrxieb/CLOUD-project 18300191954 --output analysis.json

# Brief mode (AI explanation only)
jade explain-gha jimjrxieb/CLOUD-project 18300191954 --brief
```

### What You'll Get

```
╔══════════════════════════════════════════════════════════════╗
║           SECURITY SCAN RESULTS SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

📡 Fetching workflow run details...
   Status: completed
   Branch: main
   Commit: abc1234...

📥 Downloading security scan artifacts...
   Found 8 artifact(s)

🔬 Parsing scanner results...
   Processed 47 findings from 8 scanner(s)

Total Findings: 47
Risk Score: 245 (weighted by severity)

Severity Breakdown:
  🔴 Critical: 5
  🟠 High:     12
  🟡 Medium:   20
  🟢 Low:      10

Scanners Used: 8
Scanner Types: bandit, trivy, semgrep, gitleaks, checkov, tfsec, safety, npm-audit

======================================================================
AI SECURITY ANALYSIS
======================================================================

[AI-powered explanation of each finding]
[Risk prioritization and remediation guidance]
[Action plan for junior engineers]

Confidence Score: 94.5%
```

## Option 2: Manual Log Analysis

If you can't authenticate `gh` CLI right now:

### Download Logs Manually

1. Go to: https://github.com/jimjrxieb/CLOUD-project/actions/runs/18300191954
2. Click "Summary" in top-right
3. Click "Download log archive"
4. Extract the ZIP file

### Analyze with Script

```bash
# Run analyzer
./analyze-gha-logs.sh

# Choose option 2 (already downloaded)
# Enter path to log file
```

## Option 3: Direct Command (What You Tried)

```bash
# This downloads raw logs to a file
gh run view 18300191954 --repo jimjrxieb/CLOUD-project --log > ~/gha-scan-results.txt

# Then analyze the text file
./analyze-gha-logs.sh
```

**Note:** This gives you raw logs, not parsed artifacts. For AI analysis, use Option 1.

## Troubleshooting

### Error: "gh auth login" needed

**Solution:**
```bash
gh auth login
```

### Error: "No such file or directory: GP-AI/GP-DATA/ai-models"

**Fix:**
```bash
mkdir -p GP-AI/GP-DATA/ai-models
```

### Error: "Not authenticated"

**Check auth status:**
```bash
gh auth status
```

**Refresh token:**
```bash
gh auth refresh -s repo
```

### Can't access repository

Make sure you have read access to `jimjrxieb/CLOUD-project`:
```bash
gh repo view jimjrxieb/CLOUD-project
```

## Quick Commands

### List Recent Runs
```bash
gh run list --repo jimjrxieb/CLOUD-project --limit 10
```

### View Run Details
```bash
gh run view 18300191954 --repo jimjrxieb/CLOUD-project
```

### Download Artifacts
```bash
gh run download 18300191954 --repo jimjrxieb/CLOUD-project
```

### Analyze with Jade
```bash
jade explain-gha jimjrxieb/CLOUD-project 18300191954
```

## What Jade Explain-GHA Does

1. **Fetches workflow metadata** - Run status, branch, commit
2. **Downloads artifacts** - All security scan outputs (JSON files)
3. **Parses results** - Supports 15+ scanner formats
4. **Consolidates findings** - Groups by severity and scanner
5. **Calculates risk** - Weighted scoring (Critical×10 + High×5 + Medium×2 + Low×1)
6. **AI analysis** - Explains vulnerabilities to junior engineers
7. **Logs evidence** - Audit trail in `~/.jade/evidence.jsonl`

## Expected Artifacts from CLOUD-project

Based on the workflow file, you should get artifacts from:

- **Secret scanning:** GitLeaks, TruffleHog
- **SAST:** Semgrep, Bandit, ESLint, Gosec
- **Container:** Trivy, Grype
- **IaC:** Checkov, TFSec, Kubescape, KICS
- **Dependencies:** Safety, npm audit, Snyk

## Next Steps

After analyzing your run:

1. **Review critical findings** - Fix high-priority issues first
2. **Check evidence log** - `grep "explain_gha" ~/.jade/evidence.jsonl | jq`
3. **View dashboard** - `bin/jade-stats`
4. **Compare trends** - Analyze multiple runs to track improvements

## Support

- **Full docs:** [GP-DOCS/guides/JADE_GHA_EXPLAINER.md](GP-DOCS/guides/JADE_GHA_EXPLAINER.md)
- **Help:** `jade explain-gha --help`
- **Demo:** `./DEMO_GHA_EXPLAINER.sh`

---

**TL;DR:**
```bash
# Setup (once)
gh auth login

# Analyze
jade explain-gha jimjrxieb/CLOUD-project 18300191954
```