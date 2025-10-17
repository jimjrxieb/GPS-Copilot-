# Fix Reports Directory

This directory stores reports from auto-fixer executions, organized by layer.

## Structure

```
fixing/
├── ci-fixes/              # CI fixer execution reports
│   ├── fix-hardcoded-secrets-TIMESTAMP.log
│   └── fix-sql-injection-TIMESTAMP.log
│
├── cd-fixes/              # CD fixer execution reports
│   ├── fix-security-groups-TIMESTAMP.log
│   ├── fix-s3-encryption-TIMESTAMP.log
│   ├── fix-iam-wildcards-TIMESTAMP.log
│   └── fix-kubernetes-security-TIMESTAMP.log
│
├── runtime-fixes/         # Runtime fixer execution reports
│   └── fix-cloudwatch-security-TIMESTAMP.log
│
├── summary-TIMESTAMP.json # Overall fix summary (all layers)
└── README.md              # This file
```

## Report Format

### Individual Fixer Logs
```
TIMESTAMP: 2025-10-09 15:31:23
FIXER: fix-security-groups.sh
LAYER: CD (Infrastructure)

BEFORE:
  Violations: 4 instances of 0.0.0.0/0

CHANGES MADE:
  ✅ Created backup: terraform.backup.20251009-153123
  ✅ Fixed security group: rds-sg (0.0.0.0/0 → 10.0.0.0/16)
  ✅ Fixed security group: backend-sg (scoped to ALB)

AFTER:
  Violations: 0 instances of 0.0.0.0/0

STATUS: Success
```

### Summary JSON
```json
{
  "timestamp": "2025-10-09T15:31:23Z",
  "ci_fixes": {
    "executed": 2,
    "successful": 2,
    "failed": 0,
    "violations_fixed": 0
  },
  "cd_fixes": {
    "executed": 4,
    "successful": 4,
    "failed": 0,
    "violations_fixed": 60
  },
  "runtime_fixes": {
    "executed": 1,
    "successful": 1,
    "failed": 0,
    "violations_fixed": 5
  },
  "total_violations_fixed": 65,
  "duration_seconds": 12
}
```

## Usage

Fixers automatically save reports here when run with the master orchestrator:

```bash
cd secops/3-fixers
./run-all-fixes.sh --only-cd

# Reports saved to:
# secops/6-reports/fixing/cd-fixes/fix-security-groups-TIMESTAMP.log
# secops/6-reports/fixing/summary-TIMESTAMP.json
```

## Integration with Validators

The validator script compares:
- **Before:** `secops/2-findings/baseline-counts.txt`
- **Fixes:** `secops/6-reports/fixing/summary-TIMESTAMP.json`
- **After:** `secops/2-findings/diff-report.txt`

Full workflow:
```bash
# 1. Baseline scan
cd secops/1-scanners
./run-all-ci-cd-runtime.sh
cd ../5-validators
./compare-results.sh  # Saves baseline

# 2. Apply fixes
cd ../3-fixers
./run-all-fixes.sh  # Saves to 6-reports/fixing/

# 3. Validation scan
cd ../1-scanners
./run-all-ci-cd-runtime.sh
cd ../5-validators
./compare-results.sh  # Shows improvement

# 4. Review fix reports
ls ../6-reports/fixing/
```

## Retention Policy

- **Fix logs:** Keep for 30 days (audit trail)
- **Summary JSONs:** Keep for 1 year (compliance reporting)
- **Backups:** Keep for 7 days (rollback capability)

## Compliance Mapping

Fix reports include compliance framework mappings:

- **PCI-DSS:** Requirement number (e.g., 8.2.1, 3.4)
- **CIS Benchmarks:** Control ID (e.g., CIS AWS 1.16, CIS K8s 5.2.1)
- **OWASP:** Category (e.g., A02:2021 Cryptographic Failures)

Example:
```
COMPLIANCE:
  ✅ PCI-DSS 1.3.1: Network segmentation (RDS isolated)
  ✅ CIS AWS 4.1: Restrict default security group
```

## Audit Trail

All fix reports include:
- Timestamp (ISO 8601 format)
- Fixer name and version
- Git commit hash (if applicable)
- Backup location
- Before/after state
- Compliance mapping

This provides evidence for auditors that violations were:
1. Detected (scanner logs in `2-findings/`)
2. Fixed (fixer logs in `6-reports/fixing/`)
3. Validated (validator logs in `2-findings/diff-report.txt`)

---

**Last Updated:** 2025-10-09
**Owner:** SecOps Framework
**Purpose:** Track all automated remediation activities
