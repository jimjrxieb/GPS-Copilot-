# GP-DATA Centralized Storage Architecture v2.0

**Purpose**: Unified data persistence for all GuidePoint security scanning operations

**Status**: ✅ PRODUCTION READY

---

## 🏗️ Directory Structure

```
/home/jimmie/linkops-industries/GP-copilot/GP-DATA/
│
├── active/                              # Current operational data
│   ├── scans/                          # All scanner output (unified)
│   │   ├── {tool}_{timestamp}.json    # Individual scan results
│   │   └── {tool}_latest.json          # Latest scan per tool
│   │
│   ├── analysis/                       # James Brain AI analysis
│   │   ├── insights/                   # AI-generated security insights
│   │   ├── correlations/               # Cross-tool finding correlation
│   │   └── recommendations/            # Remediation strategies
│   │
│   ├── fixes/                          # Remediation tracking
│   │   ├── proposed/                   # AI-generated fix proposals
│   │   ├── applied/                    # Applied fixes with verification
│   │   └── rollback/                   # Rollback snapshots
│   │
│   ├── reports/                        # Current reports
│   │   ├── executive/                  # Executive summaries
│   │   ├── technical/                  # Technical details
│   │   └── compliance/                 # Compliance evidence
│   │
│   └── workflows/                      # Current workflow tracking
│       └── workflow_*.json             # Multi-tool scan coordination
│
├── archive/                            # Historical data
│   ├── 2025-09/                       # Date-based archival
│   │   ├── scans/
│   │   ├── reports/
│   │   └── workflows/
│   └── legacy/                        # Old raw/processed structure
│       ├── raw/                       # Archived raw scans
│       ├── processed/                 # Archived processed scans
│       └── [other legacy dirs]
│
└── templates/                          # Reusable assets
    ├── reports/                       # Report templates
    ├── policies/                      # OPA policy templates
    └── workflows/                     # Process templates
```

---

## 📊 Data Flow Architecture

### 1. Scanner Execution (Unified Pattern)
```
Scanner → Tool Execution → Normalized Output → GP-DATA/active/scans/
```

**Example** (Bandit):
- Location: `GP-DATA/active/scans/bandit_20250924_094349_482.json`
- Content: Standardized format with normalized severity
- Symlink: `GP-DATA/active/scans/bandit_latest.json` → latest scan

### 2. Standardized Result Format
```json
{
  "findings": [
    {
      "file": "app.py",
      "line": 42,
      "severity": "high",              // Normalized: critical/high/medium/low
      "issue": "SQL injection risk",
      "cwe": 89,
      "test_id": "B608"
    }
  ],
  "summary": {
    "total": 26,
    "files_scanned": 1319,
    "severity_breakdown": {
      "critical": 0,
      "high": 1,
      "medium": 0,
      "low": 25
    }
  },
  "target": "/path/to/project",
  "tool": "bandit",
  "timestamp": "2025-09-24T09:43:49.482180",
  "scan_id": "bandit_20250924_094349_482"
}
```

---

## 🔧 Configuration Management

### Centralized Path Configuration
All scanners use the `GPDataConfig` manager for path resolution:

```python
# james-config/gp_data_config.py
class GPDataConfig:
    def get_scan_directory(self) -> Path:
        return self.base_path / "active" / "scans"

    def get_reports_directory(self) -> Path:
        return self.base_path / "active" / "reports"
```

### Scanner Integration Pattern
```python
from pathlib import Path
import sys

# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig

class Scanner:
    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
```

**Benefits:**
- Single point of truth for all data paths
- Easy migration when restructuring GP-DATA
- Multi-client ready (future expansion)
- Environment switching (dev/prod/test)

---

## 🛡️ Implemented Scanners (100% Coverage)

All scanners now use GPDataConfig and write to `/active/scans/`:

✅ **bandit_scanner.py** - Python security analysis
✅ **checkov_scanner.py** - IaC security scanning (9 frameworks)
✅ **gitleaks_scanner.py** - Git secret scanning
✅ **kube_bench_scanner.py** - CIS Kubernetes benchmarks
✅ **kube_hunter_scanner.py** - Kubernetes penetration testing
✅ **npm_audit_scanner.py** - NPM dependency vulnerabilities
✅ **opa_scanner.py** - Policy compliance evaluation
✅ **polaris_scanner.py** - Kubernetes best practices
✅ **semgrep_scanner.py** - Static code analysis (14 languages)
✅ **tfsec_scanner.py** - Terraform security
✅ **trivy_scanner.py** - Container/dependency vulnerabilities

---

## 🧠 James Brain Integration

### Data Access Pattern
```python
from gp_data_config import GPDataConfig

config = GPDataConfig()
scans_dir = config.scans

# Load latest scan results
latest_bandit = scans_dir / "bandit_latest.json"
latest_trivy = scans_dir / "trivy_latest.json"

# Process with AI for insights, recommendations
```

### AI Analysis Pipeline
```
1. Scan Results → GP-DATA/active/scans/
                     ↓
2. James Brain Analysis → GP-DATA/active/analysis/insights/
                     ↓
3. Finding Correlation → GP-DATA/active/analysis/correlations/
                     ↓
4. Remediation Strategy → GP-DATA/active/fixes/proposed/
                     ↓
5. Executive Report → GP-DATA/active/reports/executive/
```

---

## 📈 Historical Tracking & Archival

### Archive Strategy
- **Active scans**: Latest scan per tool + recent historical scans
- **Monthly archival**: Move scans > 30 days to `/archive/YYYY-MM/`
- **Legacy data**: Old raw/processed structure archived to `/archive/legacy/`

### Retention Policy
- **Active scans**: 30 days rolling window
- **Monthly archives**: 1 year
- **Compliance evidence**: Permanent
- **Legacy data**: Archive only (historical reference)

---

## 🚀 Migration Complete

### What Changed (v1.0 → v2.0)
- ❌ **Removed**: Complex raw/processed directory separation
- ✅ **Added**: Centralized `GPDataConfig` manager
- ✅ **Simplified**: Single `/active/scans/` directory
- ✅ **Standardized**: All scanners use identical pattern
- ✅ **Future-proofed**: Easy path changes without touching 10+ scanners

### Migration Summary
```
Old structure:
/GP-DATA/scans/raw/{tool}/
/GP-DATA/scans/processed/{tool}/

New structure:
/GP-DATA/active/scans/{tool}_{timestamp}.json
/GP-DATA/active/scans/{tool}_latest.json
```

**Architectural Benefits:**
- 🎯 **Maintainability**: Change paths in one place
- 📦 **Simplicity**: No raw/processed complexity
- 🔄 **Consistency**: All scanners identical pattern
- 🚀 **Scalability**: Ready for multi-client expansion

---

## 📝 Usage Examples

### Run Scan with Auto-Persistence
```bash
# Any scanner auto-persists to GP-DATA/active/scans/
python3 GP-CONSULTING-AGENTS/scanners/bandit_scanner.py /path/to/project

# Output:
# 🐍 Bandit results saved to: GP-DATA/active/scans/bandit_20250924_094349_482.json
# 🐍 Bandit found 0 security issues
```

### Access Latest Results
```bash
# Latest scan results always available
cat GP-DATA/active/scans/trivy_latest.json
cat GP-DATA/active/scans/checkov_latest.json
```

### Query Historical Scans
```python
from pathlib import Path
import json

scans_dir = Path("GP-DATA/active/scans")

# Get all Trivy scans
trivy_scans = sorted(scans_dir.glob("trivy_*.json"))

# Compare first and last
with open(trivy_scans[0]) as f:
    first_scan = json.load(f)
with open(trivy_scans[-1]) as f:
    latest_scan = json.load(f)

print(f"First scan: {first_scan['summary']['total']} findings")
print(f"Latest scan: {latest_scan['summary']['total']} findings")
```

---

## 🎯 Key Benefits

✅ **Centralized Storage**: All security data in logical structure
✅ **Configuration Management**: Single source of truth for paths
✅ **Historical Tracking**: Compare scans over time
✅ **James Brain Ready**: AI-powered analysis on persistent data
✅ **Audit Compliance**: Timestamped scan results with IDs
✅ **Cross-tool Correlation**: Deduplicate findings across tools
✅ **Easy Migration**: Change structure without touching scanners

---

**Architecture Status**: Production Ready v2.0
**Last Updated**: 2025-09-24
**Owner**: GuidePoint Security Platform
**Major Change**: Simplified architecture with centralized configuration