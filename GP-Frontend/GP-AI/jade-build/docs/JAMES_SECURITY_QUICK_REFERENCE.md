# James Security Quick Reference Guide

## 🤖 **FOR JAMES AI: When to Use Each Security Component**

### **🎯 DECISION TREE**

```
User Request → Determine Type → Choose Component

📋 "Scan this project for vulnerabilities"
├─ Use: scanners/run_all_scans.py
└─ Follow with: intelligence/analyze_scan_results.py

🔧 "Fix the security issues found"
├─ Use: fixers/apply_all_fixes.py
└─ Input: scan results JSON file

🛡️ "Set up CI/CD security pipeline"
├─ Use: agents/devsecops_agent/agent.py
└─ Command: implement <project_path> github_actions

⚓ "Harden Kubernetes cluster"
├─ Use: agents/kubernetes_agent/agent.py
└─ Commands: analyze + generate security manifests

🧠 "Intelligent security automation"
├─ Use: agents/enhanced_security_agent.py
└─ For: ML-powered fix decisions

📊 "Comprehensive security assessment"
├─ Use: agents/scanner_agent/agent.py
└─ For: Multi-tool analysis + autonomous fixes
```

### **⚡ COMMAND PATTERNS FOR JAMES**

#### **Complete Security Workflow**
```bash
# 1. Scan (always start here)
python scanners/run_all_scans.py /target/project

# 2. Analyze (get intelligence)
python intelligence/analyze_scan_results.py /results/scans/latest_scan.json

# 3. Fix (apply remediation)
python fixers/apply_all_fixes.py /results/scans/latest_scan.json /target/project
```

#### **Specialized Workflows**

**DevSecOps Pipeline Setup:**
```bash
python agents/devsecops_agent/agent.py implement /project/path github_actions
```

**Kubernetes Security Hardening:**
```bash
python agents/kubernetes_agent/agent.py analyze /k8s/manifests
python agents/kubernetes_agent/agent.py generate /output/dir production
```

**Autonomous Vulnerability Remediation:**
```bash
python agents/scanner_agent/agent.py analyze /project/path
python agents/scanner_agent/agent.py remediate /project/path
```

### **🔍 COMPONENT SELECTION LOGIC**

| User Need | Primary Component | Secondary Components | Example |
|-----------|-------------------|---------------------|---------|
| "Scan for vulnerabilities" | `scanners/run_all_scans.py` | `intelligence/analyze_scan_results.py` | Full project security scan |
| "Fix security issues" | `fixers/apply_all_fixes.py` | Requires scan results first | Apply proven remediation patterns |
| "DevSecOps pipeline" | `agents/devsecops_agent/` | `scanners/` for validation | GitHub Actions security workflow |
| "Kubernetes hardening" | `agents/kubernetes_agent/` | `scanners/` + `fixers/` | RBAC, NetworkPolicies, PSS |
| "Comprehensive assessment" | `agents/scanner_agent/` | Uses `scanners/` internally | Executive security reporting |
| "Smart automation" | `agents/enhanced_security_agent.py` | ML-powered decisions | Confidence-based fix execution |

### **📂 FILE LOCATION REFERENCE**

```
/home/jimmie/linkops-industries/James-OS/guidepoint/
├── agents/                          # 🎯 Specialized domain experts
│   ├── devsecops_agent/agent.py     # CI/CD security automation
│   ├── kubernetes_agent/agent.py    # CKA/CKS cluster hardening
│   ├── scanner_agent/agent.py       # Multi-tool vulnerability detection
│   └── enhanced_security_agent.py   # ML-enhanced decision making
├── scanners/                        # 🔧 Unified tool execution
│   ├── run_all_scans.py            # Master orchestrator (6 tools)
│   ├── checkov_scanner.py          # Infrastructure-as-Code
│   ├── trivy_scanner.py            # Container vulnerabilities
│   ├── bandit_scanner.py           # Python SAST
│   ├── gitleaks_scanner.py         # Secrets detection
│   ├── semgrep_scanner.py          # Multi-language SAST
│   └── npm_audit_scanner.py        # Node.js dependencies
├── fixers/                          # 🛠️ Proven remediation
│   ├── apply_all_fixes.py          # Master fix orchestrator
│   ├── production_terraform_fixer.py # KICS-based Terraform fixes
│   ├── python_fixer.py             # Python security fixes
│   └── kics_remediation_patterns.py # Industry-standard patterns
└── intelligence/                    # 🧠 AI-powered analysis
    ├── analyze_scan_results.py     # Master intelligence orchestrator
    ├── rag/knowledge_retriever.py  # Security knowledge with confidence
    └── risk_assessment.py          # Business impact analysis
```

### **🚀 INTEGRATION EXAMPLES**

#### **Example 1: New Project Security Setup**
```python
# James should execute this sequence for new projects
async def setup_new_project_security(project_path):
    # 1. Comprehensive scan
    scan_cmd = f"python scanners/run_all_scans.py {project_path}"

    # 2. Intelligence analysis
    analysis_cmd = f"python intelligence/analyze_scan_results.py /results/scans/latest_scan.json"

    # 3. Implement DevSecOps pipeline
    devsecops_cmd = f"python agents/devsecops_agent/agent.py implement {project_path} github_actions"

    # 4. Apply automated fixes
    fix_cmd = f"python fixers/apply_all_fixes.py /results/scans/latest_scan.json {project_path}"

    return "Complete security setup with pipeline, scanning, and remediation"
```

#### **Example 2: Kubernetes Project Hardening**
```python
# James should use this for K8s security requests
async def harden_kubernetes_project(manifests_path):
    # 1. K8s-specific analysis
    k8s_cmd = f"python agents/kubernetes_agent/agent.py analyze {manifests_path}"

    # 2. Generate security manifests
    generate_cmd = f"python agents/kubernetes_agent/agent.py generate /output production"

    # 3. Comprehensive scanning for validation
    scan_cmd = f"python scanners/run_all_scans.py {manifests_path}"

    # 4. Apply fixes if needed
    fix_cmd = f"python fixers/apply_all_fixes.py /results/scans/latest_scan.json {manifests_path}"

    return "Complete K8s hardening with RBAC, NetworkPolicies, and security validation"
```

#### **Example 3: Autonomous Security Assessment**
```python
# James should use this for hands-off security automation
async def autonomous_security_assessment(project_path):
    # 1. Use scanner agent for comprehensive analysis
    analysis_cmd = f"python agents/scanner_agent/agent.py analyze {project_path}"

    # 2. Execute autonomous remediation
    remediate_cmd = f"python agents/scanner_agent/agent.py remediate {project_path}"

    return "Fully autonomous security assessment with 100% success rate fixes"
```

### **⚠️ IMPORTANT USAGE NOTES**

1. **Always scan first**: Start with `scanners/run_all_scans.py` for comprehensive coverage
2. **Use agents for specialization**: DevSecOps, Kubernetes, or general scanning agents
3. **Apply intelligence**: Use `intelligence/analyze_scan_results.py` for risk assessment
4. **Fix with confidence**: Use `fixers/apply_all_fixes.py` for proven remediation patterns
5. **Validate results**: Re-scan after fixes to verify success

### **🎯 SUCCESS PATTERNS**

**✅ High Success Pattern**:
Scan → Intelligence Analysis → Specialized Agent (if needed) → Apply Fixes → Validate

**❌ Common Mistakes**:
- Skipping initial comprehensive scan
- Applying fixes without intelligence analysis
- Not using specialized agents for domain expertise
- Forgetting to validate fix success

### **📊 EXPECTED OUTCOMES**

| Component | Expected Results |
|-----------|------------------|
| `scanners/run_all_scans.py` | JSON with findings from 6 tools |
| `intelligence/analyze_scan_results.py` | Risk assessment + fix recommendations with confidence scores |
| `agents/devsecops_agent/` | GitHub Actions workflow with 7 security gates |
| `agents/kubernetes_agent/` | RBAC, NetworkPolicies, Pod Security Standards |
| `agents/scanner_agent/` | Executive report + autonomous remediation |
| `fixers/apply_all_fixes.py` | Applied fixes with backup files created |

**🎯 Remember: Specialized agents provide domain expertise, unified orchestration provides execution consistency. Use both for enterprise-grade security automation.**