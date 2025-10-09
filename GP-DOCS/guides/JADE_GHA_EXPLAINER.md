# Jade GHA Explainer - AI-Powered GitHub Actions Analysis

## Overview

The `jade explain-gha` command fetches GitHub Actions security scan results, parses outputs from multiple scanners, and provides AI-powered explanations prioritized by risk for junior engineers.

**Week 2 Intelligence Layer Feature** ✅

## Features

- 📡 **Automated artifact fetching** - Downloads all security-related artifacts from GHA workflow runs
- 🔬 **Multi-scanner parsing** - Supports 15+ security scanners (Bandit, Trivy, Semgrep, GitLeaks, etc.)
- 🤖 **AI-powered explanations** - Uses LLM to explain findings in simple terms
- 📊 **Risk prioritization** - Calculates weighted risk scores and prioritizes by severity
- 💾 **Evidence logging** - All actions logged to `~/.jade/evidence.jsonl` for audit trail
- 🎯 **Exit codes** - Returns error codes for CI/CD integration

## Supported Scanners

The GHA analyzer automatically detects and parses results from:

### SAST (Static Application Security Testing)
- **Bandit** - Python security scanning
- **Semgrep** - Multi-language pattern-based scanning
- **ESLint** - JavaScript/TypeScript security
- **Gosec** - Go security scanning

### Secrets Detection
- **GitLeaks** - Secret scanning
- **TruffleHog** - High-entropy secret detection
- **Detect-Secrets** - Baseline secret scanning

### Container Security
- **Trivy** - Container vulnerability scanning
- **Grype** - Container and dependency scanning

### Infrastructure as Code
- **Checkov** - Multi-IaC security scanning
- **TFSec** - Terraform security
- **Kubescape** - Kubernetes security
- **KICS** - Infrastructure as Code security

### Dependency Scanning
- **Safety** - Python dependency vulnerabilities
- **npm audit** - Node.js dependency scanning
- **Snyk** - Multi-language dependency scanning

## Usage

### Basic Command

```bash
jade explain-gha <owner/repo> <run-id>
```

**Example:**
```bash
jade explain-gha guidepoint/cloud-project 1234567890
```

### With Output File

Save detailed analysis to JSON for later review:

```bash
jade explain-gha owner/repo 1234567890 --output analysis.json
```

### Brief Mode

Show only AI explanation without detailed summary:

```bash
jade explain-gha owner/repo 1234567890 --brief
```

## Finding Workflow Run IDs

### Method 1: GitHub CLI
```bash
# List recent workflow runs
gh run list --repo owner/repo

# Get specific workflow runs
gh run list --repo owner/repo --workflow security_scan.yml
```

### Method 2: GitHub Web UI
1. Navigate to repository → Actions tab
2. Click on a workflow run
3. Run ID is in the URL: `github.com/owner/repo/actions/runs/<RUN_ID>`

### Method 3: GitHub API
```bash
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/actions/runs | jq '.workflow_runs[0].id'
```

## Output Format

### Summary Display

```
╔══════════════════════════════════════════════════════════════╗
║           SECURITY SCAN RESULTS SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

Repository: guidepoint/cloud-project
Run ID: 1234567890
Status: completed

Total Findings: 47
Risk Score: 245

Severity Breakdown:
  🔴 Critical: 5
  🟠 High:     12
  🟡 Medium:   20
  🟢 Low:      10

Scanners Used: 8
Scanner Types: bandit, trivy, semgrep, gitleaks, checkov, tfsec, safety, npm-audit
```

### AI Analysis Output

```
======================================================================
AI SECURITY ANALYSIS
======================================================================

Based on the security scan results, I've identified several critical issues
that require immediate attention:

**TOP PRIORITY ISSUES:**

1. 🔴 SQL Injection Vulnerability (bandit-B608)
   - What: Unsanitized user input in SQL query construction
   - Risk: Attackers can execute arbitrary SQL commands
   - Location: api/users.py:45
   - Fix: Use parameterized queries or ORM methods

   Before:
   query = f"SELECT * FROM users WHERE id = {user_id}"

   After:
   query = "SELECT * FROM users WHERE id = ?"
   cursor.execute(query, (user_id,))

2. 🔴 Hardcoded AWS Credentials (gitleaks)
   - What: AWS access key committed to version control
   - Risk: Full AWS account compromise if leaked
   - Location: config/aws.py:12
   - Fix: Use AWS Secrets Manager or environment variables
   - Immediate action: Rotate the compromised credential

[... additional analysis ...]

**RISK ASSESSMENT:**
- Risk Score: 245 (HIGH)
- Critical issues require immediate remediation
- Recommended timeline: Fix critical within 24 hours

**ACTION PLAN:**
1. Rotate exposed AWS credentials immediately
2. Fix SQL injection in api/users.py
3. Remove hardcoded secrets from codebase
4. Implement pre-commit hooks to prevent future secrets
5. Review and update all Python dependencies with known CVEs

======================================================================

Confidence Score: 94.5%
```

## Exit Codes

The command returns different exit codes for automation:

- **0** - Success, no critical/high findings
- **1** - Critical or high severity findings detected
- **2** - Error fetching workflow data or artifacts
- **3** - Unexpected error during analysis
- **130** - User interrupted (Ctrl+C)

### CI/CD Integration Example

```yaml
# In your GitHub Actions workflow
- name: Analyze security findings with Jade
  run: |
    jade explain-gha ${{ github.repository }} ${{ github.run_id }} \
      --output jade-analysis.json
  continue-on-error: true

- name: Upload Jade analysis
  uses: actions/upload-artifact@v4
  with:
    name: jade-ai-analysis
    path: jade-analysis.json
```

## Architecture

### Components

1. **GHA Analyzer** (`gha_analyzer.py`)
   - Fetches workflow run data via `gh` CLI
   - Downloads security scan artifacts
   - Parses scanner-specific JSON formats
   - Consolidates findings by severity and scanner type

2. **Jade GHA Explainer** (`jade_explain_gha.py`)
   - Orchestrates the analysis workflow
   - Generates LLM-friendly prompts
   - Uses AI Security Engine for explanations
   - Logs all actions for observability

3. **CLI Integration** (`bin/jade`)
   - Provides user-friendly command interface
   - Handles error cases and user interrupts
   - Formats output with rich terminal UI

### Data Flow

```
GitHub Actions Workflow Run
           ↓
    [Fetch Artifacts]
           ↓
    [Parse Results] ← Bandit, Trivy, Semgrep, etc.
           ↓
   [Consolidate Findings]
           ↓
    [Calculate Risk Score]
           ↓
   [Generate LLM Prompt]
           ↓
  [AI Security Analysis]
           ↓
    [Format & Display]
           ↓
   [Log to Evidence File]
```

## Configuration

### Prerequisites

1. **GitHub CLI** - Must be installed and authenticated
   ```bash
   gh --version
   gh auth status
   ```

2. **Repository Access** - Must have read access to repository and workflows
   ```bash
   gh auth refresh -s repo
   ```

3. **Python Dependencies**
   ```bash
   pip install click rich
   ```

### Environment Variables

Optional environment variables for customization:

```bash
# Change evidence log location
export JADE_LOG_PATH=/custom/path/evidence.jsonl

# GitHub token (if not using gh CLI)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
```

## Observability

All `explain-gha` actions are logged to the Jade evidence log for audit trail.

### View Evidence Log

```bash
# Show all GHA analysis actions
grep "explain_gha" ~/.jade/evidence.jsonl | jq

# View recent analyses
tail -20 ~/.jade/evidence.jsonl | jq 'select(.action == "explain_gha")'

# Show LLM confidence scores
jq 'select(.action == "explain_gha") | {target, confidence: .llm_confidence}' \
  ~/.jade/evidence.jsonl
```

### Dashboard Statistics

```bash
# View Jade stats including GHA analyses
bin/jade-stats
```

## Example: CLOUD-project Workflow

The CLOUD-project demonstrates a comprehensive security pipeline:

**Workflow:** `.github/workflows/security_scan.yml`

**Scanners Used:**
- Pre-flight checks (file change detection)
- Secret scanning (TruffleHog, GitLeaks, Detect-Secrets)
- SAST (Semgrep, Bandit, ESLint, Gosec)
- Container security (Trivy, Grype)
- IaC security (Checkov, TFSec, Kubescape, KICS)
- Dependency scanning (Safety, npm audit, Snyk)
- Compliance validation (SOC 2, PCI DSS, GDPR)

**Analysis Example:**
```bash
# Analyze latest security scan
LATEST_RUN=$(gh run list --repo guidepoint/cloud-project --workflow security_scan.yml --limit 1 --json databaseId -q '.[0].databaseId')

jade explain-gha guidepoint/cloud-project $LATEST_RUN --output cloud-analysis.json
```

## Advanced Usage

### Batch Analysis

Analyze multiple workflow runs:

```bash
#!/bin/bash
# analyze-recent-runs.sh

REPO="owner/repo"
RUNS=$(gh run list --repo $REPO --limit 5 --json databaseId -q '.[].databaseId')

for run_id in $RUNS; do
  echo "Analyzing run $run_id..."
  jade explain-gha $REPO $run_id --output "analysis-${run_id}.json"
done
```

### Trend Analysis

Track security improvements over time:

```bash
# Get risk scores from analyses
jq '.summary.risk_score' analysis-*.json

# Compare critical findings over time
jq '.summary.severity_counts.critical' analysis-*.json
```

### Integration with Slack

Send AI analysis to Slack:

```bash
ANALYSIS=$(jade explain-gha owner/repo 1234567890 --brief 2>&1 | \
  sed -n '/AI SECURITY ANALYSIS/,/Confidence Score/p')

curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"$ANALYSIS\"}"
```

## Troubleshooting

### Error: "Failed to fetch workflow run"

**Cause:** Invalid run ID or insufficient permissions

**Solution:**
```bash
# Verify run exists
gh run view <run-id> --repo owner/repo

# Check authentication
gh auth status

# Refresh token with repo scope
gh auth refresh -s repo
```

### Error: "No security-related artifacts found"

**Cause:** Workflow didn't produce security artifacts

**Solution:**
- Check workflow uses `actions/upload-artifact@v4`
- Ensure artifact names contain keywords: "security", "scan", "sast", etc.
- Verify workflow completed successfully

### Error: "Failed to parse scanner results"

**Cause:** Unsupported scanner format or corrupted JSON

**Solution:**
- Check artifact JSON files are valid: `jq . artifact.json`
- Review supported scanners in documentation
- Open issue with sample output for new scanner support

## Future Enhancements

Planned features for Week 3+:

- [ ] **Auto-remediation** - Generate fix PRs directly from GHA analysis
- [ ] **Trend dashboards** - Visualize security posture over time
- [ ] **Custom severity mapping** - Override scanner severity levels
- [ ] **Multi-repo analysis** - Compare findings across repositories
- [ ] **Integration with JIRA** - Auto-create tickets for critical findings
- [ ] **Policy enforcement** - Block merges based on risk score thresholds

## Related Commands

- `jade scan <project>` - Local project scanning
- `jade query <question>` - Query security knowledge base
- `jade agent <question>` - Multi-agent troubleshooting
- `bin/jade-stats` - View Jade observability dashboard

## References

- [GitHub Actions API](https://docs.github.com/en/rest/actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [CLOUD-project Workflow](./../GP-PROJECTS/CLOUD-project/.github/workflows/security_scan.yml)
- [Jade Observability](./JADE_OBSERVABILITY_COMPLETE.md)