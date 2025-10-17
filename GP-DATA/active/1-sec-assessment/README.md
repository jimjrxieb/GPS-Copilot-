# Phase 1: Security Assessment - Output Directory

**Purpose:** Store all Phase 1 security assessment findings from GP-CONSULTING scanners

**Corresponds to:** [GP-CONSULTING/1-Security-Assessment](../../../GP-CONSULTING/1-Security-Assessment/)

---

## Directory Structure

```
1-sec-assessment/
├── ci-findings/          # CI scanner results (code-level)
│   ├── bandit_*.json     # Python SAST findings
│   ├── semgrep_*.json    # Multi-language SAST findings
│   ├── gitleaks_*.json   # Secrets detection findings
│   └── *_latest.json     # Latest scan results
├── cd-findings/          # CD scanner results (infrastructure-level)
│   ├── checkov_*.json    # IaC policy check findings
│   ├── trivy_*.json      # Container/IaC vulnerability findings
│   ├── opa_*.json        # OPA policy validation findings
│   ├── tfsec_*.json      # Terraform security findings
│   └── *_latest.json     # Latest scan results
├── runtime-findings/     # Runtime scanner results (production)
│   ├── kube_hunter_*.json    # K8s cluster security findings
│   ├── npm_audit_*.json      # Dependency vulnerability findings
│   └── *_latest.json         # Latest scan results
└── reports/              # Assessment reports and summaries
```

---

## Scanner Types

### CI Scanners (Code-Level Security)

| Scanner | Source | Output Location | Purpose |
|---------|--------|-----------------|---------|
| **Bandit** | [ci-scanners/bandit_scanner.py](../../../GP-CONSULTING/1-Security-Assessment/ci-scanners/bandit_scanner.py) | `ci-findings/bandit_*.json` | Python SAST |
| **Semgrep** | [ci-scanners/semgrep_scanner.py](../../../GP-CONSULTING/1-Security-Assessment/ci-scanners/semgrep_scanner.py) | `ci-findings/semgrep_*.json` | Multi-language SAST |
| **Gitleaks** | [ci-scanners/gitleaks_scanner.py](../../../GP-CONSULTING/1-Security-Assessment/ci-scanners/gitleaks_scanner.py) | `ci-findings/gitleaks_*.json` | Secrets detection |

---

### CD Scanners (Infrastructure-Level Security)

| Scanner | Source | Output Location | Purpose |
|---------|--------|-----------------|---------|
| **Checkov** | [cd-scanners/checkov_scanner.py](../../../GP-CONSULTING/1-Security-Assessment/cd-scanners/checkov_scanner.py) | `cd-findings/checkov_*.json` | IaC policy checks |
| **Trivy** | [cd-scanners/trivy_scanner.py](../../../GP-CONSULTING/1-Security-Assessment/cd-scanners/trivy_scanner.py) | `cd-findings/trivy_*.json` | Container/IaC vulnerabilities |
| **OPA** | [cd-scanners/opa-policies/](../../../GP-CONSULTING/1-Security-Assessment/cd-scanners/opa-policies/) | `cd-findings/opa_*.json` | Policy validation |
| **TFSec** | [cd-scanners/scan-iac.sh](../../../GP-CONSULTING/1-Security-Assessment/cd-scanners/scan-iac.sh) | `cd-findings/tfsec_*.json` | Terraform security |

---

### Runtime Scanners (Production Security)

| Scanner | Source | Output Location | Purpose |
|---------|--------|-----------------|---------|
| **Kube-hunter** | [runtime-scanners/](../../../GP-CONSULTING/1-Security-Assessment/runtime-scanners/) | `runtime-findings/kube_hunter_*.json` | K8s cluster security |
| **npm audit** | Built-in | `runtime-findings/npm_audit_*.json` | Dependency vulnerabilities |

---

## Usage

### Run All CI Scanners

```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/1-Security-Assessment/ci-scanners/

# Bandit (Python SAST)
python3 bandit_scanner.py /path/to/project/backend

# Semgrep (Multi-language SAST)
python3 semgrep_scanner.py --target /path/to/project

# Gitleaks (Secrets)
python3 gitleaks_scanner.py --target /path/to/project --no-git
```

**Output:** All results saved to `GP-DATA/active/1-sec-assessment/ci-findings/`

---

### Run All CD Scanners

```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/1-Security-Assessment/cd-scanners/

# Checkov (IaC)
python3 checkov_scanner.py --target /path/to/project/infrastructure/terraform

# Trivy (Container/IaC)
python3 trivy_scanner.py --mode config --target /path/to/project/infrastructure
```

**Output:** All results saved to `GP-DATA/active/1-sec-assessment/cd-findings/`

---

## View Latest Findings

### CI Findings

```bash
# View latest Bandit findings
jq '.findings | length' ci-findings/bandit_latest.json
jq '.findings[] | select(.severity=="CRITICAL")' ci-findings/bandit_latest.json

# View latest Semgrep findings
jq '.findings | length' ci-findings/semgrep_latest.json

# View latest Gitleaks findings (secrets)
jq '.findings | length' ci-findings/gitleaks_latest.json
```

---

### CD Findings

```bash
# View latest Checkov findings
jq '.findings | length' cd-findings/checkov_latest.json

# View latest Trivy findings
jq '.findings | length' cd-findings/trivy_latest.json
```

---

## Current Statistics

**As of 2025-10-14:**

| Category | File Count | Latest Scan Date |
|----------|------------|------------------|
| CI findings | 28 files | Oct 14, 2025 |
| CD findings | 52 files | Oct 14, 2025 |
| Runtime findings | 4 files | Sep 24, 2025 |
| **Total** | **84 files** | - |

---

## Integration with Other Phases

### Phase 2: App-Sec-Fixes
Reads from `ci-findings/` to determine which code vulnerabilities to fix

**Example:**
```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/2-App-Sec-Fixes/fixers/

# Fix hardcoded secrets found by Gitleaks
GITLEAKS_FINDINGS=$(cat ../../GP-DATA/active/1-sec-assessment/ci-findings/gitleaks_latest.json)
bash fix-hardcoded-secrets.sh /path/to/project
```

---

### Phase 3: Hardening
Reads from `cd-findings/` to determine which infrastructure issues to fix

**Example:**
```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/3-Hardening/fixers/

# Fix S3 encryption issues found by Checkov
CHECKOV_FINDINGS=$(cat ../../GP-DATA/active/1-sec-assessment/cd-findings/checkov_latest.json)
bash fix-s3-encryption.sh /path/to/project/infrastructure/terraform
```

---

### Phase 5: Compliance-Audit
Compares initial assessment with post-fix assessment to measure improvement

**Example:**
```bash
cd /home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING/5-Compliance-Audit/validators/

# Save baseline
mkdir -p baseline/
cp ../../GP-DATA/active/1-sec-assessment/ci-findings/*_latest.json baseline/

# After fixes, compare
bash compare-results.sh \
  --before baseline/ \
  --after ../../GP-DATA/active/1-sec-assessment/ci-findings/
```

---

## File Naming Convention

All scanner outputs follow this pattern:

```
{scanner}_{timestamp}.json
{scanner}_latest.json
```

**Examples:**
- `bandit_20251014_152845.json` - Bandit scan from Oct 14, 2025 at 15:28:45
- `semgrep_latest.json` - Latest Semgrep scan result (symlink or copy)

---

## Retention

- **Historical scans**: Keep all scans for 90 days
- **Latest scans**: Always preserve `*_latest.json` files
- **Baseline scans**: Save initial assessment separately for comparison

---

## Troubleshooting

### Scanner Output Not Appearing

**Issue:** Scanner runs but no JSON file created

**Solution:** Check scanner configuration - output_dir should be:
```python
gp_root = Path(__file__).parent.parent.parent.parent
output_dir = gp_root / 'GP-DATA' / 'active' / '1-sec-assessment' / 'ci-findings'
```

---

### Permission Denied

**Issue:** Cannot write to findings directory

**Solution:**
```bash
chmod -R 755 /home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/1-sec-assessment/
```

---

## Related Documentation

- [GP-CONSULTING Framework](../../../GP-CONSULTING/README.md)
- [Phase 1: Security Assessment](../../../GP-CONSULTING/1-Security-Assessment/README.md)
- [Scanner Configuration](../../../GP-CONSULTING/1-Security-Assessment/ci-scanners/README.md)
- [Findings Migration Report](../FINDINGS-MIGRATION-COMPLETE.md)

---

**Last updated:** 2025-10-14
**Organization version:** 2.0 (Phase-aligned with GP-CONSULTING)
