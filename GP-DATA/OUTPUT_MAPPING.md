# GP-DATA Output Mapping - Complete Reference

**Standardized output structure for all GP-Copilot operations**

---

## 📁 Directory Structure

```
GP-DATA/
├── active/                         # Current operational data
│   ├── scans/                     # Raw scanner output
│   ├── analysis/                  # Agent analysis and assessments
│   ├── reports/                   # Professional reports and documentation
│   ├── fixes/                     # Remediation tracking and fixes
│   ├── workflows/                 # Workflow orchestration logs
│   └── deliverables/              # Client-ready deliverables
│
├── archive/                        # Historical data (date-based)
│   ├── 2025-09-24/
│   │   ├── scans/
│   │   ├── analysis/
│   │   ├── reports/
│   │   ├── fixes/
│   │   └── workflows/
│   └── [YYYY-MM-DD]/
│
├── templates/                      # Reusable templates
│   ├── reports/                   # Report templates
│   ├── policies/                  # Policy templates
│   └── workflows/                 # Workflow templates
│
└── clients/                        # Multi-client data isolation (future)
    └── [client_name]/
        ├── scans/
        ├── analysis/
        ├── reports/
        └── deliverables/
```

---

## 🏷️ Agent → Output Directory Mapping

| Agent | Primary Output | Secondary Output | Metadata Tags |
|-------|---------------|------------------|---------------|
| **CKA Agent** | `analysis/` | `fixes/` | `domain: kubernetes_security` |
| **IaC Agent** | `fixes/` | `analysis/` | `domain: infrastructure_security` |
| **Secrets Agent** | `analysis/` | - | `domain: secrets_management` |
| **DevSecOps Agent** | `workflows/` | `fixes/` | `domain: cicd_security` |
| **Research Agent** | `reports/` | - | `domain: security_research` |
| **QA Agent** | `analysis/` | - | `domain: quality_assurance` |
| **DFIR Agent** | `reports/` | - | `domain: threat_intelligence` |
| **Client Support Agent** | `deliverables/` | - | `domain: client_engagement` |
| **Container Agent** | `analysis/` | `fixes/` | `domain: container_security` |

---

## 📂 Detailed Output Mapping

### 1. `active/scans/` - Raw Scanner Output

**Source**: All scanners in `GP-CONSULTING-AGENTS/scanners/`

**File Naming**: `{scanner_name}_{project_name}_{timestamp}.json`

**Examples**:
```
kubernetes_scanner_Portfolio_20250924_142530.json
checkov_scanner_Portfolio_20250924_142535.json
trivy_scanner_Portfolio_20250924_142540.json
bandit_scanner_Portfolio_20250924_142545.json
```

**Metadata Structure**:
```json
{
  "scanner": "kubernetes_scanner",
  "project_path": "/path/to/project",
  "scan_timestamp": "2025-09-24T14:25:30.123456",
  "findings_count": 15,
  "severity_breakdown": {
    "critical": 2,
    "high": 5,
    "medium": 6,
    "low": 2
  },
  "findings": [...]
}
```

---

### 2. `active/analysis/` - Agent Analysis & Assessments

**Source**: CKA Agent, Secrets Agent, QA Agent, IaC Agent, Container Agent

**File Naming**: `{agent_id}_{operation}_{timestamp}.json`

**Examples**:
```
cka_agent_assess_cluster_20250924_143000.json
secrets_agent_scan_for_hardcoded_secrets_20250924_143100.json
qa_agent_validate_k8s_manifests_20250924_143200.json
iac_agent_scan_terraform_20250924_143300.json
container_agent_analyze_image_20250924_143400.json
```

**Metadata Structure**:
```json
{
  "metadata": {
    "operation_id": "cka_agent_assess_cluster_20250924_143000",
    "agent": {
      "id": "cka_agent",
      "name": "CKA Kubernetes Agent",
      "domain": "kubernetes_security"
    },
    "operation": {
      "type": "assess_cluster",
      "confidence": "high",
      "timestamp": "2025-09-24T14:30:00.123456"
    },
    "context": {
      "project_path": "/path/to/project",
      "client_name": "TechCorp"
    },
    "tags": {
      "domain": "kubernetes_security",
      "confidence": "high",
      "assessment_type": "comprehensive"
    }
  },
  "result": {
    "success": true,
    "findings": [...],
    "recommendations": [...]
  }
}
```

---

### 3. `active/reports/` - Professional Reports

**Source**: Research Agent, DFIR Agent

**File Naming**: `{report_type}_{subject}_{timestamp}.md`

**Examples**:
```
cve_report_CVE-2024-1234_20250924_143500.md
security_guide_kubernetes_20250924_143600.md
threat_intel_report_APT29_20250924_143700.md
incident_report_INC-2024-001_20250924_143800.md
best_practices_container_security_20250924_143900.md
```

**Report Structure (Markdown)**:
```markdown
# [Report Title]

**Generated**: 2025-09-24 14:35:00
**Agent**: Research Agent
**Domain**: security_research
**Confidence**: high

---

## Executive Summary

[Summary content]

---

## Detailed Findings

[Findings content]

---

## Recommendations

1. Recommendation 1
2. Recommendation 2

---

## References

- [Source 1]
- [Source 2]

---

*Report generated by GP-Copilot Research Agent*
*Metadata: agent_id=research_agent, operation=generate_report, confidence=high*
```

---

### 4. `active/fixes/` - Remediation Tracking

**Source**: IaC Agent, DevSecOps Agent, Container Agent

**File Naming**: `{fix_type}_{project_name}_{timestamp}.json`

**Examples**:
```
terraform_fixes_Portfolio_20250924_144000.json
kubernetes_remediation_Portfolio_20250924_144100.json
container_patches_Portfolio_20250924_144200.json
pipeline_hardening_Portfolio_20250924_144300.json
```

**Fix Metadata Structure**:
```json
{
  "metadata": {
    "operation_id": "iac_agent_fix_terraform_issues_20250924_144000",
    "agent": {
      "id": "iac_agent",
      "name": "Infrastructure as Code Agent",
      "domain": "infrastructure_security"
    },
    "operation": {
      "type": "fix_terraform_issues",
      "confidence": "high",
      "timestamp": "2025-09-24T14:40:00.123456"
    }
  },
  "result": {
    "fixes_applied": 8,
    "fixes": [
      {
        "file": "main.tf",
        "line": 42,
        "issue": "S3 bucket encryption not enabled",
        "fix": "Added encryption configuration",
        "severity": "high",
        "status": "applied"
      }
    ],
    "validation": {
      "terraform_fmt": "passed",
      "terraform_validate": "passed",
      "checkov_rescan": "passed"
    }
  }
}
```

---

### 5. `active/workflows/` - Workflow Orchestration

**Source**: DevSecOps Agent, Workflow Orchestrators

**File Naming**: `{workflow_type}_{pipeline_name}_{timestamp}.json`

**Examples**:
```
github_actions_workflow_ci-pipeline_20250924_144400.json
jenkins_pipeline_deployment_20250924_144500.json
gitlab_ci_workflow_security_scan_20250924_144600.json
```

**Workflow Metadata**:
```json
{
  "metadata": {
    "operation_id": "devsecops_agent_scan_github_actions_20250924_144400",
    "agent": {
      "id": "devsecops_agent",
      "name": "DevSecOps CI/CD Agent",
      "domain": "cicd_security"
    },
    "operation": {
      "type": "scan_github_actions",
      "confidence": "high",
      "timestamp": "2025-09-24T14:44:00.123456"
    }
  },
  "result": {
    "pipeline_file": ".github/workflows/ci.yml",
    "security_gates_added": 4,
    "findings": [
      {
        "type": "missing_secret_scanning",
        "severity": "high",
        "recommendation": "Add Gitleaks scanning step"
      }
    ],
    "enhanced_pipeline": {
      "steps_added": ["Trivy scan", "Gitleaks scan", "SAST with Semgrep"],
      "security_coverage": "95%"
    }
  }
}
```

---

### 6. `active/deliverables/` - Client-Ready Deliverables

**Source**: Client Support Agent

**File Naming**: `{deliverable_type}_{client_name}_{timestamp}.md`

**Examples**:
```
meeting_notes_TechCorp_20250924_144700.md
action_items_TechCorp_20250924_144800.md
technical_checklist_kubernetes_TechCorp_20250924_144900.md
engagement_summary_TechCorp_20250924_145000.md
deliverable_security_assessment_TechCorp_20250924_145100.md
```

**Deliverable Metadata**:
```json
{
  "metadata": {
    "operation_id": "client_support_agent_meeting_notes_template_20250924_144700",
    "agent": {
      "id": "client_support_agent",
      "name": "Client Support Agent",
      "domain": "client_engagement"
    },
    "operation": {
      "type": "meeting_notes_template",
      "confidence": "high",
      "timestamp": "2025-09-24T14:47:00.123456"
    },
    "context": {
      "client_name": "TechCorp",
      "meeting_title": "Security Review",
      "attendees": 8
    }
  },
  "result": {
    "notes_file": "meeting_notes_TechCorp_20250924_144700.md",
    "action_items_count": 5,
    "next_meeting": "2025-10-08"
  }
}
```

---

## 🔄 Data Flow Architecture

### **Scanner → Analysis → Fixes → Reports → Deliverables**

```
1. SCAN PHASE
   Scanners → GP-DATA/active/scans/
   (kubernetes_scanner, checkov_scanner, trivy_scanner, etc.)

2. ANALYSIS PHASE
   Agents → GP-DATA/active/analysis/
   (CKA Agent, QA Agent, Secrets Agent analyze raw scans)

3. REMEDIATION PHASE
   Fixers → GP-DATA/active/fixes/
   (IaC Agent, DevSecOps Agent apply fixes)

4. REPORTING PHASE
   Report Generators → GP-DATA/active/reports/
   (Research Agent, DFIR Agent create professional docs)

5. DELIVERY PHASE
   Client Support → GP-DATA/active/deliverables/
   (Client Support Agent packages for client delivery)
```

---

## 📊 Agent Output Summary Table

| Agent | Operation Example | Output Directory | File Format | Metadata Domain |
|-------|------------------|-----------------|-------------|-----------------|
| CKA Agent | `assess` cluster | `analysis/` | JSON | `kubernetes_security` |
| CKA Agent | `generate` RBAC | `analysis/` | JSON + YAML | `kubernetes_security` |
| IaC Agent | `scan_terraform` | `fixes/` | JSON | `infrastructure_security` |
| IaC Agent | `fix_terraform_issues` | `fixes/` | JSON | `infrastructure_security` |
| Secrets Agent | `scan_for_hardcoded_secrets` | `analysis/` | JSON | `secrets_management` |
| Secrets Agent | `create_k8s_secret` | `analysis/` | JSON + YAML | `secrets_management` |
| DevSecOps Agent | `scan_github_actions` | `workflows/` | JSON | `cicd_security` |
| DevSecOps Agent | `add_security_gates` | `workflows/` | JSON + YAML | `cicd_security` |
| Research Agent | `fetch_cve_data` | `reports/` | Markdown | `security_research` |
| Research Agent | `create_security_guide` | `reports/` | Markdown | `security_research` |
| QA Agent | `validate_k8s_manifests` | `analysis/` | JSON | `quality_assurance` |
| QA Agent | `validate_terraform_syntax` | `analysis/` | JSON | `quality_assurance` |
| DFIR Agent | `hash_lookup` | `reports/` | JSON | `threat_intelligence` |
| DFIR Agent | `incident_documentation` | `reports/` | Markdown | `threat_intelligence` |
| Client Support Agent | `meeting_notes_template` | `deliverables/` | Markdown | `client_engagement` |
| Client Support Agent | `engagement_summary` | `deliverables/` | Markdown | `client_engagement` |

---

## 🔧 Integration with GPDataConfig

### **Usage in Agents**

```python
from gp_data_config import GPDataConfig
from agent_metadata import AgentMetadata

# Initialize configuration
config = GPDataConfig()

# Create agent metadata
metadata = AgentMetadata(
    agent_id="cka_agent",
    operation="assess_cluster",
    confidence="high",
    project_path="/path/to/project",
    client_name="TechCorp"
)

# Save operation with metadata
result = {
    "findings": 5,
    "issues": 2,
    "recommendations": [...]
}

# Agent determines output directory based on its type
output_dir = config.get_analysis_directory()  # For CKA, QA, Secrets agents
# output_dir = config.get_reports_directory()   # For Research, DFIR agents
# output_dir = config.get_fixes_directory()     # For IaC, DevSecOps agents
# output_dir = config.get_workflows_directory() # For DevSecOps workflows
# output_dir = config.get_deliverable_directory() # For Client Support agent

# Save with metadata
output_file = metadata.save(output_dir, result)
print(f"Saved: {output_file}")
```

---

## 📈 Audit Trail

All agent operations are logged to audit trail:

**Location**: `GP-DATA/audit_trail.json`

**Structure**:
```json
{
  "created": "2025-09-24T10:00:00.000000",
  "operations": [
    {
      "operation_id": "cka_agent_assess_cluster_20250924_143000",
      "timestamp": "2025-09-24T14:30:00.123456",
      "agent_id": "cka_agent",
      "operation": "assess_cluster",
      "confidence": "high",
      "client": "TechCorp",
      "success": true,
      "summary": {
        "findings_count": 5,
        "critical_issues": 2
      }
    }
  ]
}
```

**Usage**:
```python
from agent_metadata import AgentAuditTrail
from pathlib import Path

audit = AgentAuditTrail(Path("GP-DATA/audit_trail.json"))

# Log operation
audit.log_operation(metadata, result_summary)

# Query history
history = audit.get_agent_history("cka_agent", limit=10)
recent = audit.get_recent_operations(limit=20)
```

---

## 🎯 Archive Strategy

### **Daily Archive Rotation**

```bash
# Archive script (automated)
GP-DATA/
├── active/              # Current day operations
└── archive/
    ├── 2025-09-24/      # Previous day archived
    │   ├── scans/
    │   ├── analysis/
    │   ├── reports/
    │   ├── fixes/
    │   └── workflows/
    └── 2025-09-23/      # Older archives
```

**Archive Command**:
```python
from gp_data_config import GPDataConfig
from datetime import datetime
import shutil

config = GPDataConfig()
today = datetime.now().strftime("%Y-%m-%d")
archive_dir = config.get_archive_directory(today)

# Move active to archive
shutil.move(config.base_path / "active", archive_dir)
# Recreate active directories
config.get_scan_directory()
config.get_analysis_directory()
# etc...
```

---

## ✅ Validation Checklist

- [x] All agents output to correct directories
- [x] Metadata follows standardized format
- [x] File naming convention is consistent
- [x] Audit trail captures all operations
- [x] Archive strategy is documented
- [x] Multi-client support is prepared
- [x] Integration with GPDataConfig is complete

---

**Status**: ✅ Output Mapping Complete
**Integration**: Ready for production deployment
**Agents**: All 8 agents properly mapped to GP-DATA structure