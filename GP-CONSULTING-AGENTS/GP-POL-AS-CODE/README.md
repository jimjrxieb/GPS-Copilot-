# 🏛️ GP-POL-AS-CODE: Policy-as-Code Command Center

## 📂 **Centralized Policy Management System**

**Purpose**: Unified management of OPA policies, Gatekeeper integration, and policy automation workflows.

```
GP-POL-AS-CODE/
├── policies/               # 11 Rego policy files
├── generators/            # Policy generation tools
├── managers/              # OPA & cluster management
├── scanners/              # Policy evaluation engines
├── gatekeeper/            # Kubernetes admission control
├── workflows/             # Human & AI automation workflows
└── examples/              # Usage examples & templates
```

## 🎯 **What This Centralizes:**

### **Previously Scattered Components:**
```
OLD STRUCTURE:
├── GP-CONSULTING-AGENTS/policies/opa/        → NOW: policies/
├── GP-CONSULTING-AGENTS/generators/          → NOW: generators/
├── GP-CONSULTING-AGENTS/managers/            → NOW: managers/
├── GP-CONSULTING-AGENTS/opa_manager.py       → NOW: managers/
└── GP-CONSULTING-AGENTS/scanners/opa_*       → NOW: scanners/
```

### **New Unified Structure:**
- **🔐 Policies**: 11 rego files for comprehensive security
- **🏭 Generators**: Automated policy creation from violations
- **⚙️ Managers**: OPA server and cluster management
- **🔍 Scanners**: Policy evaluation and violation detection
- **🚪 Gatekeeper**: Real-time Kubernetes admission control
- **🔄 Workflows**: Both human and AI automation processes

## 🚀 **Quick Start:**

### **Human Workflow:**
```bash
# 1. Evaluate policies against manifests
python scanners/opa_scanner.py /path/to/k8s/manifests

# 2. Generate new policies from violations
python generators/opa_policy_generator.py --violations scan_results.json

# 3. Deploy to cluster (with human confirmation)
python managers/opa_cluster_manager.py --deploy --dry-run
```

### **AI Workflow (Jade):**
```bash
# Jade can now access unified policy system
python ../../GP-AI/jade_enhanced.py \
  --query "Analyze Portfolio security with OPA policies" \
  --policy-engine GP-POL-AS-CODE
```

## 📋 **Policy Inventory:**

| Policy File | Purpose | Lines | Compliance |
|------------|---------|--------|------------|
| `pod-security.rego` | K8s pod security standards | 248 | CIS-5.2, SOC2 |
| `terraform-security.rego` | IaC security validation | 180+ | CIS-1.0 |
| `rbac.rego` | Access control policies | 120+ | NIST-AC |
| `secrets-management.rego` | Secret handling rules | 95+ | PCI-DSS |
| `compliance-controls.rego` | Multi-framework checks | 200+ | SOC2, HIPAA |
| [6 more policies] | Complete security suite | 1000+ | Enterprise |

## 🎯 **Usage Modes:**

### **1. Scanner Mode (Current)**
- CLI-based policy evaluation
- CI/CD integration ready
- Report generation

### **2. Server Mode (Available)**
- HTTP API for policy decisions
- Microservice integration
- Real-time policy queries

### **3. Gatekeeper Mode (Ready to Deploy)**
- Real-time Kubernetes admission control
- Automatic violation blocking
- Policy enforcement at cluster level

---

**Status**: Production-ready Policy-as-Code management system
**Integration**: Jade AI, GP-CONSULTING-AGENTS, CI/CD pipelines
**Next Steps**: Deploy Gatekeeper for real-time enforcement