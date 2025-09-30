# GP-Copilot Consulting Agents - Complete Documentation

**8 AI-Powered Security Consulting Agents Aligned with GuidePoint Job Responsibilities**

---

## 🎯 Overview

GP-Copilot agents are specialized AI consultants that execute security tasks with confidence-based decision making. Each agent maps directly to GuidePoint Security junior consultant job responsibilities.

### **Confidence-Based Execution Model**

All agents follow a three-tier confidence model:

- **HIGH Confidence**: Execute autonomously, save to GP-DATA
- **MEDIUM Confidence**: Execute with human validation requirement
- **LOW Confidence**: Escalate to senior consultant, provide guidance only

---

## 📊 Agent Portfolio

| Agent | Job Responsibility | High Confidence Operations | Output Location |
|-------|-------------------|---------------------------|-----------------|
| **CKA Agent** | Kubernetes Operations & CKA Exam Prep | RBAC, NetworkPolicies, Secrets, Pod Security | `GP-DATA/active/analysis/` |
| **IaC Agent** | Infrastructure as Code Security | Terraform/CloudFormation scanning & fixing | `GP-DATA/active/fixes/` |
| **Secrets Agent** | Secrets Management Solutions | K8s secrets, hardcoded secret scanning, templates | `GP-DATA/active/analysis/` |
| **DevSecOps Agent** | CI/CD Pipeline Security | GitHub Actions, Jenkins, GitLab pipeline hardening | `GP-DATA/active/workflows/` |
| **Research Agent** | Cloud Security Research | CVE data, documentation, security guides | `GP-DATA/active/reports/` |
| **QA Agent** | Quality Assurance & Testing | K8s/Terraform validation, YAML testing | `GP-DATA/active/analysis/` |
| **DFIR Agent** | DFIR & Threat Intelligence | IOC lookup, MITRE mapping, incident docs | `GP-DATA/active/reports/` |
| **Client Support Agent** | Client Engagement Support | Meeting notes, action tracking, deliverables | `GP-DATA/active/deliverables/` |

---

## 🔧 Agent Details

### 1. CKA Agent (Kubernetes Operations)
**Location**: `GP-CONSULTING-AGENTS/agents/kubernetes_agent/agent.py`

**Job Responsibility**: *"Support Kubernetes security implementations, including RBAC, network policies, and pod security policies"*

**High Confidence Operations**:
- `assess`: Comprehensive cluster security assessment
- `analyze`: RBAC, NetworkPolicy, PodSecurity analysis
- `generate`: Security manifests (RBAC, NetworkPolicies, Secrets)
- `deploy`: Apply configurations to cluster
- `validate`: Test deployed configurations

**CLI Usage**:
```bash
PYTHONPATH=/home/jimmie/linkops-industries/GP-copilot \
  python3 GP-CONSULTING-AGENTS/agents/kubernetes_agent/agent.py assess GP-Projects/Portfolio
```

**Output Tags**:
- `agent: cka_agent`
- `domain: kubernetes_security`
- `confidence: high|medium|low`

---

### 2. IaC Agent (Infrastructure as Code)
**Location**: `GP-CONSULTING-AGENTS/agents/iac_agent.py`

**Job Responsibility**: *"Assist in securing Infrastructure as Code (IaC) using tools like Terraform, CloudFormation, and ARM templates"*

**High Confidence Operations**:
- `scan_terraform`: Terraform security scanning
- `scan_cloudformation`: CloudFormation template analysis
- `generate_secure_terraform`: Create secure IaC templates
- `fix_terraform_issues`: Automated remediation

**CLI Usage**:
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/iac_agent.py \
  scan-terraform --path GP-Projects/Portfolio/terraform
```

**Output Tags**:
- `agent: iac_agent`
- `domain: infrastructure_security`
- `iac_type: terraform|cloudformation|arm`

---

### 3. Secrets Agent (Secrets Management)
**Location**: `GP-CONSULTING-AGENTS/agents/secrets_agent.py`

**Job Responsibility**: *"Assist in configuring and implementing secrets management solutions like HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets"*

**High Confidence Operations**:
- `create_k8s_secret`: Create Kubernetes secrets with base64 encoding
- `create_configmap`: Generate ConfigMaps for non-sensitive data
- `scan_for_hardcoded_secrets`: Detect secrets in source code
- `generate_secret_templates`: K8s, Docker, Terraform templates
- `validate_secret_references`: Verify secret usage in manifests

**CLI Usage**:
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/secrets_agent.py \
  scan-secrets --path GP-Projects/Portfolio --output-format json
```

**Output Tags**:
- `agent: secrets_agent`
- `domain: secrets_management`
- `secret_type: kubernetes|docker|terraform|hardcoded`

---

### 4. DevSecOps Agent (CI/CD Security)
**Location**: `GP-CONSULTING-AGENTS/agents/devsecops_agent.py`

**Job Responsibility**: *"Contribute to DevSecOps practices by integrating security tools and processes into CI/CD pipelines"*

**High Confidence Operations**:
- `scan_github_actions`: Analyze GitHub Actions workflows
- `scan_jenkins_pipeline`: Jenkins pipeline security audit
- `scan_gitlab_ci`: GitLab CI/CD configuration review
- `generate_secure_pipeline`: Create hardened pipeline configs
- `add_security_gates`: Inject security scanning steps

**CLI Usage**:
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/devsecops_agent.py \
  scan-pipeline --type github-actions --path .github/workflows
```

**Output Tags**:
- `agent: devsecops_agent`
- `domain: cicd_security`
- `pipeline_type: github_actions|jenkins|gitlab_ci`

---

### 5. Research & Documentation Agent
**Location**: `GP-CONSULTING-AGENTS/agents/research_agent.py`

**Job Responsibility**: *"Research and document cloud security best practices, tools, and emerging threats"*

**High Confidence Operations**:
- `fetch_cve_data`: Retrieve CVE data from NVD API
- `generate_documentation`: Create professional security docs
- `create_security_guide`: Generate domain-specific guides
- `compile_best_practices`: Industry best practices with citations
- `threat_intelligence_report`: Emerging threats analysis

**CLI Usage**:
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/research_agent.py \
  fetch-cve --cve-id CVE-2024-1234
```

**Security Guides Available**:
- Kubernetes Security Best Practices
- Container Security Hardening
- Infrastructure as Code Security
- CI/CD Pipeline Security

**Output Tags**:
- `agent: research_agent`
- `domain: security_research`
- `doc_type: cve_report|best_practices|security_guide|threat_intel`

---

### 6. QA Agent (Quality Assurance)
**Location**: `GP-CONSULTING-AGENTS/agents/qa_agent.py`

**Job Responsibility**: *"Perform testing and validation of security configurations and automation scripts before client delivery"*

**High Confidence Operations**:
- `validate_k8s_manifests`: Kubernetes manifest validation (kubectl dry-run)
- `validate_terraform_syntax`: Terraform fmt + validate checks
- `test_yaml_syntax`: YAML syntax validation
- `validate_security_configs`: Security policy compliance
- `generate_qa_report`: Professional QA documentation

**CLI Usage**:
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/qa_agent.py \
  validate-k8s --path GP-Projects/Portfolio/k8s --namespace prod
```

**Output Tags**:
- `agent: qa_agent`
- `domain: quality_assurance`
- `validation_type: k8s|terraform|yaml|security_config`

---

### 7. DFIR Support Agent (Threat Intelligence)
**Location**: `GP-CONSULTING-AGENTS/agents/dfir_agent.py`

**Job Responsibility**: *"Support GuidePoint's DFIR practice, providing Threat Intelligence support to active intrusion investigations"*

**High Confidence Operations**:
- `hash_lookup`: IOC hash reputation (MD5, SHA1, SHA256)
- `ip_reputation_check`: IP address threat intelligence
- `domain_lookup`: Domain reputation analysis
- `timeline_generation`: Incident timeline creation
- `mitre_attack_mapping`: Observables → MITRE ATT&CK techniques
- `incident_documentation`: DFIR report with chain of custody

**CLI Usage**:
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/dfir_agent.py \
  hash-lookup --hash <hash_value> --type sha256
```

**MITRE ATT&CK Detection Patterns**:
- PowerShell/cmd execution → T1059 (Command Scripting)
- Registry modification → T1112 (Modify Registry)
- Scheduled tasks → T1053 (Scheduled Task/Job)
- Process injection → T1055 (Process Injection)

**Output Tags**:
- `agent: dfir_agent`
- `domain: threat_intelligence`
- `ioc_type: hash|ip|domain|timeline|mitre_mapping`

---

### 8. Client Support Agent (Engagement Management)
**Location**: `GP-CONSULTING-AGENTS/agents/client_support_agent.py`

**Job Responsibility**: *"Assist senior consultants in client engagements, participating in meetings, taking notes, and supporting technical assessments"*

**High Confidence Operations**:
- `meeting_notes_template`: Professional meeting notes with action items
- `action_item_tracking`: Track tasks, owners, due dates, status
- `technical_checklist`: Assessment checklists (K8s, cloud, network, app)
- `deliverable_formatting`: Format client deliverables professionally
- `followup_scheduling`: Generate follow-up schedules and reminders
- `engagement_summary`: Executive engagement summaries

**CLI Usage**:
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/client_support_agent.py \
  meeting-notes --title="Security Review" --client="Acme Corp"
```

**Assessment Checklists Available**:
- Kubernetes Security Assessment
- Cloud Security Assessment (IAM, Data, Network, Monitoring)
- Network Security Assessment
- Application Security Assessment (SAST/DAST)

**Output Tags**:
- `agent: client_support_agent`
- `domain: client_engagement`
- `deliverable_type: meeting_notes|action_tracker|checklist|summary`

---

## 📁 GP-DATA Output Structure

### **Agent Output Mapping**

```
GP-DATA/
├── active/
│   ├── scans/              # Scanner raw output
│   ├── analysis/           # Agent analysis (CKA, Secrets, QA, IaC)
│   ├── reports/            # Professional reports (Research, DFIR)
│   ├── fixes/              # Remediation tracking (IaC, DevSecOps)
│   ├── workflows/          # Workflow orchestration (DevSecOps)
│   └── deliverables/       # Client deliverables (Client Support)
│
├── archive/                # Historical data
│   ├── 2025-09-24/
│   └── [date]/
│
├── templates/              # Document templates
│   ├── reports/
│   ├── policies/
│   └── workflows/
│
└── clients/                # Multi-client support (future)
    └── [client_name]/
```

### **Output File Naming Convention**

All agent outputs follow this pattern:
```
{operation_type}_{timestamp}.{format}
{operation_type}_{client_name}_{timestamp}.{format}
```

**Examples**:
- `kubernetes_assessment_20250924_142530.json` (CKA Agent)
- `meeting_notes_Acme_Corp_20250924_143000.md` (Client Support)
- `cve_report_CVE-2024-1234_20250924_143500.md` (Research)
- `incident_report_INC-2024-001_20250924_144000.md` (DFIR)

---

## 🏷️ Agent Tagging System

### **Metadata Tags in All Outputs**

Every agent operation saves metadata with these tags:

```json
{
  "agent": "agent_id",
  "operation": "operation_type",
  "domain": "security_domain",
  "confidence": "high|medium|low",
  "timestamp": "2025-09-24T14:25:30.123456",
  "project_path": "/path/to/project",
  "client": "client_name",
  "result": { /* operation-specific data */ }
}
```

### **Domain Tags**

- `kubernetes_security` - CKA Agent
- `infrastructure_security` - IaC Agent
- `secrets_management` - Secrets Agent
- `cicd_security` - DevSecOps Agent
- `security_research` - Research Agent
- `quality_assurance` - QA Agent
- `threat_intelligence` - DFIR Agent
- `client_engagement` - Client Support Agent

---

## 🔗 Integration with GP-DATA Config

All agents use `GPDataConfig` for path management:

```python
from gp_data_config import GPDataConfig

config = GPDataConfig()

# Get appropriate output directory
output_dir = config.get_analysis_directory()  # CKA, Secrets, QA, IaC
output_dir = config.get_reports_directory()   # Research, DFIR
output_dir = config.get_workflows_directory() # DevSecOps
output_dir = config.get_deliverable_directory() # Client Support (NEW)
```

---

## 🚀 Quick Start Examples

### **Run CKA Assessment**
```bash
cd /home/jimmie/linkops-industries/GP-copilot
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/kubernetes_agent/agent.py \
  assess GP-Projects/Portfolio
```

### **Generate Security Guide**
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/research_agent.py \
  security-guide --domain kubernetes --output GP-DATA/active/reports/
```

### **Create Meeting Notes**
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/client_support_agent.py \
  meeting-notes --title="Security Review" --client="TechCorp" \
  --attendees="Alice (GP),Bob (Client)"
```

### **Validate Kubernetes Configs**
```bash
PYTHONPATH=$(pwd) python3 GP-CONSULTING-AGENTS/agents/qa_agent.py \
  validate-k8s --path GP-Projects/Portfolio/k8s --namespace production
```

---

## 📊 Agent Status Dashboard

### **Current Coverage: 100% of GuidePoint Job Responsibilities**

| Job Responsibility | Agent | Status | Confidence Model |
|-------------------|-------|--------|-----------------|
| ✅ Kubernetes Operations | CKA Agent | Complete | HIGH/MEDIUM/LOW |
| ✅ Infrastructure as Code | IaC Agent | Complete | HIGH/MEDIUM/LOW |
| ✅ Secrets Management | Secrets Agent | Complete | HIGH/MEDIUM/LOW |
| ✅ DevSecOps CI/CD | DevSecOps Agent | Complete | HIGH/MEDIUM/LOW |
| ✅ Security Research | Research Agent | Complete | HIGH/MEDIUM/LOW |
| ✅ Quality Assurance | QA Agent | Complete | HIGH/MEDIUM/LOW |
| ✅ DFIR Threat Intel | DFIR Agent | Complete | HIGH/MEDIUM/LOW |
| ✅ Client Support | Client Support Agent | Complete | HIGH/MEDIUM/LOW |

---

## 🎯 Next Steps

### **Enhanced GP-DATA Integration**
- [ ] Add `get_deliverable_directory()` to `gp_data_config.py`
- [ ] Implement agent execution audit trail
- [ ] Create agent performance metrics dashboard

### **Multi-Client Support**
- [ ] Client-specific agent configurations
- [ ] Per-client output isolation
- [ ] Client branding for deliverables

### **API Integration**
- [ ] james-brain API endpoints for all agents
- [ ] Web UI integration via james-ui
- [ ] Voice command support via james-voice

---

**Status**: ✅ All 8 Agents Complete | GP-DATA Integration Ready
**Documentation**: Complete with tagging system and output mapping
**Ready For**: Production deployment and Thursday demo! 🚀