# GP-DATA/active/findings Directory Structure

**Purpose:** Organized storage for all security scanner results from GP-CONSULTING framework

---

## Directory Structure

```
findings/
├── raw/                      # Raw scanner output (JSON)
│   ├── ci/                   # Phase 1: CI scanners
│   │   ├── bandit_*.json     # Python SAST results
│   │   ├── semgrep_*.json    # Multi-language SAST results
│   │   ├── gitleaks_*.json   # Secrets detection results
│   │   └── *_latest.json     # Latest scan for each tool
│   ├── cd/                   # Phase 1: CD scanners
│   │   ├── checkov_*.json    # IaC security scan results
│   │   ├── trivy_*.json      # Container/IaC vulnerability results
│   │   ├── opa_*.json        # Policy validation results
│   │   ├── tfsec_*.json      # Terraform security results
│   │   └── *_latest.json     # Latest scan for each tool
│   └── runtime/              # Phase 1: Runtime scanners
│       ├── kube_hunter_*.json    # K8s security scan results
│       ├── npm_audit_*.json      # Dependency audit results
│       └── *_latest.json         # Latest scan for each tool
├── processed/                # Enriched/deduplicated findings
│   ├── ci/                   # Processed CI findings
│   ├── cd/                   # Processed CD findings
│   └── runtime/              # Processed runtime findings
└── baseline/                 # Initial baseline for comparison
    ├── ci/                   # Baseline CI findings
    ├── cd/                   # Baseline CD findings
    └── runtime/              # Baseline runtime findings
```

---

## File Naming Convention

All scanner outputs follow this naming pattern:

```
{scanner}_{timestamp}.json
{scanner}_latest.json
```

**Examples:**
- `bandit_20251014_150721.json` - Bandit scan from Oct 14, 2025 at 15:07:21
- `semgrep_latest.json` - Latest Semgrep scan result

---

## Scanner Categories

### CI Scanners (Code-Level)

| Scanner | Purpose | Output Location | Frequency |
|---------|---------|-----------------|-----------|
| **Bandit** | Python SAST | `raw/ci/bandit_*.json` | Every commit, daily |
| **Semgrep** | Multi-language SAST | `raw/ci/semgrep_*.json` | Every commit, daily |
| **Gitleaks** | Secrets detection | `raw/ci/gitleaks_*.json` | Every commit, daily |

**Use case:** Phase 2 (App-Sec-Fixes) uses these findings to auto-remediate code vulnerabilities

---

### CD Scanners (Infrastructure-Level)

| Scanner | Purpose | Output Location | Frequency |
|---------|---------|-----------------|-----------|
| **Checkov** | IaC policy checks | `raw/cd/checkov_*.json` | Pre-deployment |
| **Trivy** | Container/IaC vulns | `raw/cd/trivy_*.json` | Pre-deployment |
| **OPA** | Policy validation | `raw/cd/opa_*.json` | Pre-deployment |
| **TFSec** | Terraform security | `raw/cd/tfsec_*.json` | Pre-deployment |

**Use case:** Phase 3 (Hardening) uses these findings to secure infrastructure

---

### Runtime Scanners

| Scanner | Purpose | Output Location | Frequency |
|---------|---------|-----------------|-----------|
| **Kube-hunter** | K8s cluster security | `raw/runtime/kube_hunter_*.json` | Weekly |
| **npm audit** | Dependency vulnerabilities | `raw/runtime/npm_audit_*.json` | Daily |

**Use case:** Phase 5 (Compliance-Audit) monitors production security posture

---

## Usage Examples

### Access Latest Scan Results

```bash
# Latest CI scans
cat findings/raw/ci/bandit_latest.json
cat findings/raw/ci/semgrep_latest.json
cat findings/raw/ci/gitleaks_latest.json

# Latest CD scans
cat findings/raw/cd/checkov_latest.json
cat findings/raw/cd/trivy_latest.json
cat findings/raw/cd/opa_latest.json
```

---

### Count Findings by Severity

```bash
# Count CRITICAL findings in latest Bandit scan
jq '[.findings[] | select(.severity=="CRITICAL")] | length' findings/raw/ci/bandit_latest.json

# Count HIGH findings in latest Checkov scan
jq '[.findings[] | select(.severity=="HIGH")] | length' findings/raw/cd/checkov_latest.json
```

---

### Compare Before/After

```bash
# Save baseline
cp findings/raw/ci/bandit_latest.json findings/baseline/ci/bandit_baseline.json

# After fixes, compare
diff <(jq '.findings | length' findings/baseline/ci/bandit_baseline.json) \
     <(jq '.findings | length' findings/raw/ci/bandit_latest.json)
```

---

## Current Statistics

**As of latest organization (2025-10-14):**

| Category | File Count | Description |
|----------|------------|-------------|
| CI Scanners | 28 files | Bandit (12), Semgrep (7), Gitleaks (9) |
| CD Scanners | 52 files | Checkov (4), Trivy (13), OPA (29), TFSec (6) |
| Runtime | 4 files | Kube-hunter (2), npm audit (2) |
| **Total** | **84 files** | Historical scan data preserved |

---

## Integration with GP-CONSULTING

### Phase 1: Security Assessment
Scanners write directly to `findings/raw/{ci,cd,runtime}/`

**Example:**
```python
# From 1-Security-Assessment/ci-scanners/bandit_scanner.py
output_dir = Path(__file__).parent.parent.parent / 'GP-DATA' / 'active' / 'findings' / 'raw' / 'ci'
```

---

### Phase 2: App-Sec-Fixes
Reads from `findings/raw/ci/` to determine what to fix

**Example:**
```bash
# From 2-App-Sec-Fixes/fixers/fix-hardcoded-secrets.sh
FINDINGS=$(cat ../../GP-DATA/active/findings/raw/ci/gitleaks_latest.json)
```

---

### Phase 3: Hardening
Reads from `findings/raw/cd/` to determine infrastructure issues

**Example:**
```bash
# From 3-Hardening/fixers/fix-s3-encryption.sh
FINDINGS=$(cat ../../GP-DATA/active/findings/raw/cd/checkov_latest.json)
```

---

### Phase 5: Compliance-Audit
Compares `baseline/` vs `raw/` to measure improvement

**Example:**
```bash
# From 5-Compliance-Audit/validators/compare-results.sh
bash compare-results.sh \
  --before findings/baseline/ \
  --after findings/raw/
```

---

## Retention Policy

- **raw/**: Keep all scans for 90 days, then archive
- **processed/**: Keep deduplicated findings for 1 year
- **baseline/**: Keep indefinitely for compliance audit trail

---

## Migration Notes

**Previous location:** `GP-DATA/active/scans/`
**New location:** `GP-DATA/active/findings/raw/{ci,cd,runtime}/`

**Migration completed:** 2025-10-14
- ✅ Copied all historical scanner results to new structure
- ✅ Organized by scanner type (CI/CD/Runtime)
- ✅ Preserved all timestamps and original files
- ✅ Updated scanner output paths in GP-CONSULTING framework

**Old location preserved:** Original `scans/` directory kept for backward compatibility

---

## Troubleshooting

### Scanner Output Not Appearing

**Issue:** Scanner completes but no JSON file in findings/

**Solution:** Check scanner output_dir configuration:
```python
# Should be:
output_dir = Path(__file__).parent.parent.parent / 'GP-DATA' / 'active' / 'findings' / 'raw' / 'ci'
```

---

### Latest Files Not Updated

**Issue:** `*_latest.json` not reflecting newest scan

**Solution:** Scanners should overwrite `*_latest.json` after each scan, or create symlink:
```bash
ln -sf bandit_$(date +%Y%m%d_%H%M%S).json bandit_latest.json
```

---

## Related Documentation

- [GP-CONSULTING Framework](../../GP-CONSULTING/README.md)
- [Phase 1: Security Assessment](../../GP-CONSULTING/1-Security-Assessment/README.md)
- [Scanner Output Formats](../../GP-CONSULTING/1-Security-Assessment/ci-scanners/README.md)
- [Post-Migration Validation](../../GP-CONSULTING/POST-MIGRATION-VALIDATION.md)

---

**Last updated:** 2025-10-14
**Organization version:** 2.0 (Phase-based)
