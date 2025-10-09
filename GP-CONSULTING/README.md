# GP-CONSULTING-AGENTS

**Purpose:** Agentic security automation - Jade's autonomous security engineering capabilities
**Part of:** GP-Copilot / Jade AI Security Platform
**Status:** ✅ Agentic Architecture Implemented (Oct 4, 2025)

---

## 🤖 **What Makes This "Agentic"?**

**Before:** Jade was a chatbot that runs tools when you ask
```
You: "scan this project"
Jade: *runs scanner* "Here are the results"
You: "fix the issues"
Jade: *runs fixer* "Fixed"
```

**Now:** Jade is an autonomous Jr Cloud Security Engineer
```
You: "make this terraform secure"
Jade:
  1. 🔍 Scans with OPA (autonomous)
  2. 🧠 Analyzes results (AI reasoning)
  3. 🤔 Decides: "I can auto-fix 18 issues, 7 need approval"
  4. 🔧 Applies fixes (autonomous)
  5. ✓  Verifies with re-scan (autonomous)
  6. 📚 Learns patterns for future (autonomous)
  7. 📊 Reports results
```

**This is like Claude Code, but for security automation.**

---

## 📁 Directory Structure (v2.0 - Agentic)

```
GP-CONSULTING-AGENTS/
│
├── tools/                           # ✨ NEW: Tool Registry (Jade's tools)
│   ├── base_registry.py             # Tool registry framework
│   ├── scanner_tools.py             # 7 scanner tools (Bandit, Trivy, OPA, etc.)
│   ├── fixer_tools.py               # 7 fixer tools (auto-remediation)
│   └── validator_tools.py           # 6 validator tools (verify fixes worked)
│
├── workflows/                       # 🔄 Agentic Workflows (LangGraph)
│   ├── agentic_orchestrator.py      # ✨ NEW: Main autonomous workflow engine
│   ├── opa_enforcement_workflow.py  # ✨ NEW: OPA policy enforcement workflow
│   ├── scan_workflow.py             # Legacy: Manual scan orchestration
│   ├── fix_workflow.py              # Legacy: Manual fix orchestration
│   └── full_workflow.py             # Legacy: Manual full workflow
│
├── agents/                          # 🤖 AI Agents (14 files)
│   ├── cks_agent.py                 # CKS certification expert
│   ├── devsecops_agent.py           # DevSecOps automation
│   ├── secrets_agent.py             # Secrets management
│   ├── sast_agent.py                # SAST analysis
│   ├── kubernetes_fixer.py          # K8s auto-remediation
│   ├── kubernetes_validator.py      # K8s validation
│   └── ... (8 more agents)
│
├── scanners/                        # 🔍 Security Scanners (14 files)
│   ├── bandit_scanner.py            # Python security (Bandit)
│   ├── trivy_scanner.py             # Container/IaC (Trivy)
│   ├── semgrep_scanner.py           # SAST (Semgrep)
│   ├── gitleaks_scanner.py          # Secret detection (Gitleaks)
│   ├── checkov_scanner.py           # IaC security (Checkov)
│   ├── kube_bench_scanner.py        # CIS K8s benchmark
│   ├── kube_hunter_scanner.py       # K8s penetration testing
│   └── ... (7 more scanners)
│
├── fixers/                          # 🔧 Auto-Remediation (12 files)
│   ├── bandit_fixer.py              # Fix Python security issues
│   ├── trivy_fixer.py               # Fix container vulnerabilities
│   ├── gitleaks_fixer.py            # Fix secret leaks
│   ├── terraform_fixer.py           # Fix Terraform issues
│   ├── kubernetes_fixer.py          # Fix K8s misconfigurations
│   ├── apply_all_fixes.py           # Bulk fix application
│   └── ... (6 more fixers)
│
├── remediation/                     # 🩺 Remediation Logic
│   ├── remediation_db.py            # Remediation database
│   └── security_advisor.py          # Security recommendations
│
├── GP-POL-AS-CODE/                  # 📜 Policy-as-Code (OPA/Gatekeeper)
│   ├── 1-POLICIES/                  # OPA policies, Gatekeeper templates
│   ├── 2-AUTOMATION/                # Policy automation (scanners, fixers, generators)
│   │   ├── scanners/                # OPA scanner
│   │   ├── fixers/                  # OPA fixer
│   │   ├── generators/              # Policy generators
│   │   ├── orchestrators/           # OPA manager
│   │   └── agents/                  # Policy enforcement agents
│   ├── 3-STANDARDS/                 # GuidePoint standards
│   └── 4-DOCS/                      # Policy documentation
│
├── GP-devsecops/                    # 🚀 DevSecOps Pipelines
│   ├── pipelines/                   # CI/CD pipeline configs
│   ├── templates/                   # Pipeline templates
│   └── secrets/                     # Secret management
│
├── JADE_AGENTIC_VISION.md           # 📖 Vision document
└── README.md                        # This file

```

---

## 🚀 **Quick Start - Agentic Mode**

### **Autonomous Security Engineering:**

```python
from GP_CONSULTING_AGENTS.workflows.agentic_orchestrator import run_autonomous_workflow

# Jade autonomously: scans → analyzes → decides → fixes → verifies → learns
result = run_autonomous_workflow(
    task="scan and fix terraform security issues",
    target_path="GP-PROJECTS/Terraform_CICD_Setup"
)

print(f"Success: {result['success']}")
print(f"Steps: {' → '.join(result['steps_completed'])}")
print(f"Issues Fixed: {len(result['fixes_applied'])}")
```

### **OPA Policy Enforcement:**

```python
from GP_CONSULTING_AGENTS.workflows.opa_enforcement_workflow import run_opa_workflow

# Autonomous OPA enforcement: scan → fix → validate → deploy
result = run_opa_workflow(
    task="enforce opa terraform policies",
    target_path="GP-PROJECTS/Terraform_CICD_Setup",
    policy_type="terraform"
)
```

### **Traditional Manual Mode (Legacy):**

```bash
# Still works for manual control
python scanners/bandit_scanner.py /path/to/project
python fixers/bandit_fixer.py scan_results.json /path/to/project
```

---

## 🧠 **Agentic Architecture**

### **Tool Registry Pattern**

Jade has access to 20+ tools, organized by category:

```python
from tools.base_registry import ToolRegistry, ToolCategory

# Scanners (SAFE - read-only)
- scan_python_bandit()
- scan_dependencies_trivy()
- scan_secrets_gitleaks()
- scan_code_semgrep()
- scan_iac_checkov()
- scan_iac_opa()

# Fixers (MEDIUM/HIGH - requires approval for high-risk)
- fix_python_bandit()          # MEDIUM severity
- fix_dependencies_trivy()     # HIGH severity
- fix_secrets_gitleaks()       # CRITICAL severity
- fix_terraform_issues()       # HIGH severity
- fix_kubernetes_issues()      # HIGH severity
- generate_opa_policy()        # MEDIUM severity

# Validators (SAFE - verification)
- verify_fix_effectiveness()
- validate_opa_policy()
- validate_gatekeeper_constraint()
- validate_terraform_syntax()
- validate_kubernetes_manifest()
```

### **AI Decision Engine**

Jade uses AI reasoning to decide what to do:

```python
class SecurityEngineerReasoning:
    def analyze_scan_results(self, results):
        """
        Decision tree:
        1. CRITICAL issues? → Fix immediately (with approval)
        2. Compliance violations? → Check requirements
        3. Quick wins? → Apply now
        4. Complex issues? → Create work items for human

        Returns: {
            "decision": "fix_auto" | "fix_with_approval" | "report_only",
            "reasoning": "Explanation",
            "auto_fixable": [...],
            "needs_human": [...]
        }
        """
```

### **Workflow Graph (LangGraph)**

Multi-step autonomous workflow:

```
        ┌─────────┐
        │  SCAN   │ - Scan with appropriate tool
        └────┬────┘
             │
        ┌────▼────┐
        │ ANALYZE │ - AI analyzes results, makes decision
        └────┬────┘
             │
        ┌────▼────┐
        │ DECIDE  │ - Route based on decision
        └─┬───┬─┬─┘
          │   │ │
    ┌─────▼   │ └──────┐
    │  FIX    │  REPORT │
    └────┬────┘         │
         │              │
    ┌────▼────┐         │
    │ VERIFY  │         │
    └────┬────┘         │
         │              │
    ┌────▼────┐         │
    │  LEARN  │         │
    └────┬────┘         │
         │              │
    ┌────▼──────────────▼┐
    │      REPORT        │
    └────────────────────┘
```

---

## 🎯 **Comparison: Manual vs Agentic**

| Task | Manual Mode | Agentic Mode |
|------|-------------|--------------|
| **Scan project** | Run scanner manually | Jade auto-selects scanner based on files |
| **Analyze results** | Human reads results | AI analyzes and makes decisions |
| **Fix issues** | Human decides what to fix | AI decides: auto-fix, approval, or skip |
| **Verify fixes** | Human re-scans manually | Jade automatically re-scans and compares |
| **Learn patterns** | No learning | Jade saves successful patterns to GP-DATA |
| **Approval** | N/A | Jade requests approval for HIGH/CRITICAL changes |

---

## 🛠️ **Tool Capabilities**

### **Scanners (20 tools total)**

| Tool | Language | Capabilities |
|------|----------|-------------|
| **Bandit** | Python | SQL injection, hardcoded secrets, insecure functions |
| **Trivy** | All | Dependencies, containers, IaC, OS packages |
| **Semgrep** | 30+ languages | SAST, OWASP Top 10, custom rules |
| **Gitleaks** | All | Secrets, API keys, passwords, certificates |
| **Checkov** | IaC | Terraform, CloudFormation, Kubernetes, ARM |
| **OPA** | Rego | Custom policies, compliance, governance |
| **Kube-Bench** | K8s | CIS Kubernetes Benchmark |
| **Kube-Hunter** | K8s | Penetration testing, attack vectors |

### **Fixers (30+ patterns)**

**Bandit Fixer:**
- Hardcoded passwords → Environment variables
- Insecure random → secrets.SystemRandom()
- SQL injection → Parameterized queries
- Eval usage → ast.literal_eval()

**Trivy Fixer:**
- Vulnerable packages → Upgraded versions
- Outdated dependencies → Latest patches

**Gitleaks Fixer:**
- Hardcoded secrets → Vault/Secrets Manager
- Exposed keys → Environment variables + rotation

**Terraform Fixer:**
- Unencrypted resources → Add encryption
- Public S3 buckets → Private + bucket policies
- Missing logging → Add CloudWatch/CloudTrail
- Open security groups → Restrict to IPs

**Kubernetes Fixer:**
- Privileged containers → Security context
- Missing resource limits → Add requests/limits
- No network policies → Generate NetworkPolicy
- Root containers → runAsNonRoot

**OPA Policy Generator:**
- Violation pattern → New OPA policy
- OPA policy → Gatekeeper ConstraintTemplate

---

## 📊 **Severity Levels & Approval**

Jade automatically handles approval workflow:

| Severity | Description | Approval Required | Example |
|----------|-------------|-------------------|---------|
| **SAFE** | Read-only, no changes | No | Scanners, validators |
| **LOW** | Minor changes | No | Code formatting, comments |
| **MEDIUM** | Moderate changes | Notify user | Fix Python issues, generate policies |
| **HIGH** | Significant changes | Yes | Fix dependencies, Terraform changes |
| **CRITICAL** | Major changes (secrets, git history) | Explicit approval | Secret rotation, git history rewrite |

---

## 🔄 **Integration with GP-Copilot**

### **GP-AI Integration:**
- **AI Security Engine** - Orchestrates tool calls
- **RAG Engine** - Retrieves similar patterns from past fixes
- **Model Manager** - Runs Qwen2.5-7B-Instruct for reasoning

### **GP-DATA Integration:**
- **Learning Storage** - Saves successful patterns to ChromaDB
- **Scan Results** - Stores all scan results for analysis
- **Reports** - Centralizes all workflow reports

### **GP-RAG Integration:**
- **Dynamic Learning** - "Learn from this fix" → saves to knowledge base
- **Pattern Retrieval** - "Similar issue fixed before?" → retrieves past solutions

### **GP-PLATFORM Integration:**
- **james-config** - Centralized configuration
- **Coordination** - Policy agent coordination
- **Custom Tools** - Tool registry framework

---

## 🎓 **Usage Examples**

### **Example 1: Scan & Fix Python Project**

```python
from workflows.agentic_orchestrator import run_autonomous_workflow

result = run_autonomous_workflow(
    task="scan and fix python security issues",
    target_path="GP-AI/"
)

# Output:
# 🔍 Step 1: Scanning GP-AI/...
# ✅ Scan complete: 12 issues found
#
# 🧠 Step 2: Analyzing scan results...
# ✅ Analysis complete: Decision = fix_auto
#    Reasoning: 8 issues are auto-fixable (hardcoded passwords, insecure random)
#
# 🔧 Step 3: Applying fixes...
# ✅ Fixes applied: 8 fixes
#
# ✓ Step 4: Verifying fixes...
# ✅ Verification complete: 8 issues fixed
#    Effectiveness: 66.7%
#
# 📚 Step 5: Learning from workflow...
# ✅ Learned 8 patterns
#
# 📊 Step 6: Generating report...
# ✅ Report saved: GP-DATA/active/reports/workflow_abc123.json
```

### **Example 2: OPA Policy Enforcement**

```python
from workflows.opa_enforcement_workflow import run_opa_workflow

result = run_opa_workflow(
    task="enforce opa terraform policies",
    target_path="GP-PROJECTS/Terraform_CICD_Setup",
    policy_type="terraform"
)

# Workflow: scan → enforce → validate → deploy → report
```

### **Example 3: Custom Tool Use**

```python
from tools.base_registry import ToolRegistry

# Execute specific tool
result = ToolRegistry.execute_tool(
    "scan_secrets_gitleaks",
    target_path=".",
    scan_mode="detect"
)

print(result['data'])  # Scan results
```

---

## 📈 **Metrics**

**Components:**
- **Tools:** 20 registered (7 scanners, 7 fixers, 6 validators)
- **Workflows:** 2 agentic + 4 legacy
- **Agents:** 14 AI-powered assistants
- **Fix Patterns:** 30+ automated remediations
- **Policy Rules:** 12 OPA policies, 30+ GuidePoint standards

**Capabilities:**
- **Languages:** Python, JavaScript, Go, Java, Terraform, Kubernetes, etc.
- **Frameworks:** CIS, SOC2, PCI-DSS, HIPAA, GDPR, NIST, SLSA
- **Cloud Providers:** AWS, Azure, GCP
- **Automation Level:** 70%+ issues auto-fixable

---

## 🚦 **Status**

**Completed (Oct 4, 2025):**
- ✅ Tool registry framework (base_registry.py)
- ✅ 20 tools registered (scanners, fixers, validators)
- ✅ Agentic orchestrator (LangGraph-based)
- ✅ AI decision engine (SecurityEngineerReasoning)
- ✅ OPA enforcement workflow
- ✅ Approval workflow framework
- ✅ Learning system (saves to GP-DATA)
- ✅ Verification loop (re-scan after fixes)

**Next Steps:**
- ⏳ Test agentic workflows on real projects
- ⏳ Integrate with Jade chat interface
- ⏳ Add more policy generation workflows
- ⏳ Expand to network policy generation
- ⏳ Add rollback capability for failed fixes

---

## 📖 **Documentation**

- [JADE_AGENTIC_VISION.md](JADE_AGENTIC_VISION.md) - Complete vision for agentic Jade
- [GP-POL-AS-CODE/README.md](GP-POL-AS-CODE/README.md) - Policy-as-Code documentation
- [tools/base_registry.py](tools/base_registry.py) - Tool registry framework
- [workflows/agentic_orchestrator.py](workflows/agentic_orchestrator.py) - Main workflow engine

**External:**
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OPA Documentation](https://www.openpolicyagent.org/docs/)
- [Gatekeeper Documentation](https://open-policy-agent.github.io/gatekeeper/)

---

**Version:** 2.0 (Agentic Architecture)
**Last Updated:** October 4, 2025
**Maintained by:** GP-Copilot / Jade AI

---

## 🎬 **Demo Commands**

```bash
# Test tool registry
python -c "from tools.scanner_tools import register_scanner_tools; register_scanner_tools(); from tools.base_registry import ToolRegistry; print(ToolRegistry.list_tools())"

# Run autonomous workflow
python workflows/agentic_orchestrator.py

# Run OPA workflow
python workflows/opa_enforcement_workflow.py

# List available tools
python -c "from tools.base_registry import ToolRegistry; from tools.scanner_tools import *; from tools.fixer_tools import *; from tools.validator_tools import *; register_scanner_tools(); register_fixer_tools(); register_validator_tools(); print(ToolRegistry.list_tools())"
```