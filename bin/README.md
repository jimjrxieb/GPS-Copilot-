# BIN - Security Tools & Executables

## Overview

`bin/` is the **centralized directory for security scanning tools and executable binaries** used by the GP-JADE AI Security Platform. This directory provides quick access to all security scanners, policy validators, and custom CLI tools.

---

## Directory Structure

```
bin/
├── bandit           → Symlink to Python code security scanner
├── checkov          → Symlink to Infrastructure-as-Code security scanner
├── conftest         → Binary: Policy testing for Kubernetes/OPA
├── gitleaks         → Symlink to secrets detection tool
├── gp-jade          → Symlink to JADE AI CLI (legacy)
├── jade             → Symlink to JADE AI CLI (primary)
├── jade-stats       → Custom script: JADE observability dashboard
├── kubescape        → Symlink to Kubernetes security scanner
├── opa              → Symlink to Open Policy Agent
├── semgrep          → Symlink to semantic code analysis tool
├── tfsec            → Symlink to Terraform security scanner
└── trivy            → Symlink to vulnerability scanner
```

---

## Tool Categories

### 🐍 Python Code Security

**bandit** (v1.8.6)
- **Type**: Symlink → `/home/jimmie/.pyenv/shims/bandit`
- **Purpose**: Static analysis for Python code security issues
- **Usage**: `bandit -r /path/to/code`
- **Detects**: SQL injection, hardcoded passwords, insecure crypto, shell injection
- **Scanner**: `GP-CONSULTING/scanners/bandit_scanner.py`
- **Fixer**: `GP-CONSULTING/fixers/bandit_fixer.py`

**semgrep** (Latest)
- **Type**: Symlink → `/home/jimmie/.local/bin/semgrep`
- **Purpose**: Semantic pattern matching for security vulnerabilities
- **Usage**: `semgrep --config=auto /path/to/code`
- **Detects**: Security patterns, custom rules, OWASP Top 10
- **Scanner**: `GP-CONSULTING/scanners/semgrep_scanner.py`
- **Fixer**: `GP-CONSULTING/fixers/semgrep_fixer.py`

---

### 🔐 Secrets Detection

**gitleaks** (v8.18.0)
- **Type**: Binary (6.8MB executable)
- **Purpose**: Detect hardcoded secrets, API keys, passwords in code/git history
- **Usage**: `gitleaks detect --source /path/to/repo`
- **Detects**: AWS keys, GitHub tokens, private keys, passwords, JWTs
- **Scanner**: `GP-CONSULTING/scanners/gitleaks_scanner.py`
- **Fixer**: `GP-CONSULTING/fixers/gitleaks_fixer.py`

---

### 🏗️ Infrastructure-as-Code (IaC) Security

**checkov** (v3.2.471)
- **Type**: Symlink → `/home/jimmie/.local/bin/checkov`
- **Purpose**: IaC security scanner (Terraform, CloudFormation, Kubernetes, Docker)
- **Usage**: `checkov -d /path/to/iac`
- **Detects**: Misconfigurations, compliance violations (CIS, PCI-DSS, HIPAA)
- **Scanner**: `GP-CONSULTING/scanners/checkov_scanner.py`
- **Fixer**: `GP-CONSULTING/fixers/checkov_fixer.py`

**tfsec** (v1.28.1)
- **Type**: Binary (38MB executable)
- **Purpose**: Static analysis for Terraform code
- **Usage**: `tfsec /path/to/terraform`
- **Detects**: AWS/Azure/GCP misconfigurations, insecure defaults
- **Scanner**: `GP-CONSULTING/scanners/tfsec_scanner.py`
- **Fixer**: `GP-CONSULTING/fixers/tfsec_fixer.py`

---

### ☸️ Kubernetes Security

**kubescape** (v3.0.3)
- **Type**: Binary (164MB executable)
- **Purpose**: Kubernetes security posture management (KSPM)
- **Usage**: `kubescape scan framework nsa /path/to/manifests`
- **Detects**: NSA/CISA Kubernetes hardening guide violations, RBAC issues
- **Scanner**: `GP-CONSULTING/scanners/kubernetes_scanner.py`
- **Note**: Update available (v3.0.15)

**opa** (v0.57.1)
- **Type**: Symlink → `/usr/local/bin/opa`
- **Purpose**: Open Policy Agent - policy enforcement engine
- **Usage**: `opa test /path/to/policies`
- **Purpose**: Policy-as-Code validation for Kubernetes, Terraform, CI/CD
- **Scanner**: `GP-CONSULTING/GP-POL-AS-CODE/scanners/opa_scanner.py`
- **Policies**: `GP-CONSULTING/GP-POL-AS-CODE/policies/*.rego`

**conftest** (v0.49.1 / OPA v0.61.0)
- **Type**: Binary (40MB executable)
- **Purpose**: Test structured configuration files using OPA policies
- **Usage**: `conftest test deployment.yaml -p policy.rego`
- **Use Cases**: Kubernetes YAML validation, Dockerfile validation, CI/CD gates

---

### 🛡️ Vulnerability Scanning

**trivy** (v0.48.0)
- **Type**: Symlink → `/home/jimmie/bin/trivy`
- **Purpose**: Comprehensive vulnerability scanner (OS, libraries, containers, IaC)
- **Usage**: `trivy fs /path/to/code`
- **Detects**: CVEs in dependencies, container images, filesystems
- **Scanner**: `GP-CONSULTING/scanners/trivy_scanner.py`
- **Fixer**: `GP-CONSULTING/fixers/trivy_fixer.py`

---

### 🤖 JADE AI CLI Tools

**jade** (Primary CLI)
- **Type**: Symlink → `../GP-AI/cli/jade-cli.py`
- **Purpose**: Main JADE AI command-line interface
- **Usage**:
  ```bash
  jade chat                    # Interactive AI security consultant
  jade scan <project>          # Run security scans
  jade explain <workflow_run>  # Explain GitHub Actions failures
  jade fix <project>           # Auto-fix security issues
  jade rag query "question"    # Query knowledge base
  ```
- **Documentation**: [GP-AI/cli/README.md](../GP-AI/cli/README.md)

**gp-jade** (Legacy)
- **Type**: Symlink → `../GP-AI/cli/gp-jade.py`
- **Purpose**: Legacy JADE interface (deprecated)
- **Status**: Use `jade` instead

**jade-stats** (Custom Script)
- **Type**: Python script (executable)
- **Purpose**: JADE observability dashboard - view metrics and audit logs
- **Usage**: `jade-stats`
- **Features**:
  - View total events logged
  - Error rates and LLM confidence scores
  - Security findings and fix success rates
  - Recent scan/fix activities
  - Log integrity verification
- **Data Source**: `GP-DATA/active/audit/jade-evidence.jsonl`

---

## Workflow Integration

```
┌─────────────────────────────────────────────────────┐
│            User Command / API Request               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   jade scan <project> │
         └───────────┬───────────┘
                     │
     ┌───────────────┼───────────────┬───────────┐
     │               │               │           │
     ▼               ▼               ▼           ▼
┌─────────┐    ┌─────────┐    ┌─────────┐  ┌─────────┐
│ bandit  │    │ semgrep │    │ trivy   │  │gitleaks │
│(Python) │    │(SAST)   │    │(Vuln)   │  │(Secrets)│
└────┬────┘    └────┬────┘    └────┬────┘  └────┬────┘
     │              │              │            │
     └──────────────┴──────────────┴────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GP-CONSULTING/       │
         │  scanners/*.py        │
         │  (Parse & Normalize)  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GP-DATA/active/      │
         │  results/<project>/   │
         │  (Store JSON results) │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GP-AI/               │
         │  (AI Analysis &       │
         │   Fix Generation)     │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  GP-CONSULTING/       │
         │  fixers/*.py          │
         │  (Apply Fixes)        │
         └───────────────────────┘
```

---

## Usage Examples

### Run Single Scanner

```bash
# Python code security
bandit -r GP-PROJECTS/my-app

# Secrets detection
gitleaks detect --source GP-PROJECTS/my-app

# Container vulnerabilities
trivy fs GP-PROJECTS/my-app

# Terraform security
tfsec GP-PROJECTS/my-infrastructure

# Kubernetes security
kubescape scan framework nsa GP-PROJECTS/k8s-manifests
```

### Run via JADE CLI

```bash
# Automated multi-scanner workflow
jade scan GP-PROJECTS/my-app

# Interactive chat mode
jade chat

# View results
jade-stats
```

### Policy Testing

```bash
# Test OPA policies
opa test GP-CONSULTING/GP-POL-AS-CODE/policies/

# Validate Kubernetes manifest
conftest test deployment.yaml -p kubernetes.rego

# Evaluate policy
opa eval -d security-policy.rego "data.allow"
```

---

## Tool Comparison Matrix

| Tool | Language | Type | Speed | Coverage | Fix Support |
|------|----------|------|-------|----------|-------------|
| **bandit** | Python | SAST | Fast | Python only | ✅ Yes |
| **semgrep** | Any | SAST | Medium | Multi-language | ✅ Yes |
| **gitleaks** | Any | Secrets | Fast | Git/Files | ✅ Yes |
| **trivy** | Any | Vuln/IaC | Fast | Comprehensive | ✅ Yes |
| **checkov** | IaC | Config | Medium | Multi-cloud | ✅ Yes |
| **tfsec** | Terraform | IaC | Fast | Terraform only | ✅ Yes |
| **kubescape** | K8s | Config | Medium | Kubernetes | ❌ Manual |
| **opa** | Any | Policy | Fast | Custom rules | N/A |
| **conftest** | Any | Policy | Fast | Structured config | N/A |

---

## Environment Variables

```bash
# Add bin/ to PATH
export PATH="/home/jimmie/linkops-industries/GP-copilot/bin:$PATH"

# Trivy cache directory
export TRIVY_CACHE_DIR="$HOME/.cache/trivy"

# Gitleaks config
export GITLEAKS_CONFIG="$HOME/linkops-industries/GP-copilot/GP-CONSULTING/config/gitleaks.toml"

# OPA policy directory
export OPA_POLICY_DIR="$HOME/linkops-industries/GP-copilot/GP-CONSULTING/GP-POL-AS-CODE/policies"
```

---

## Maintenance

### Check for Updates

```bash
# Trivy
trivy --version
# Update: Download from https://github.com/aquasecurity/trivy/releases

# Gitleaks
gitleaks version
# Update: Download from https://github.com/gitleaks/gitleaks/releases

# Kubescape (update available)
kubescape version
kubescape update

# Python-based tools (bandit, semgrep, checkov)
source ai-env/bin/activate
pip install --upgrade bandit semgrep checkov
```

### Verify All Tools

```bash
#!/bin/bash
# Test all scanners
for tool in bandit checkov gitleaks trivy tfsec kubescape opa conftest semgrep; do
    echo -n "Testing $tool: "
    if command -v $tool &> /dev/null; then
        echo "✅ OK"
    else
        echo "❌ Missing"
    fi
done
```

---

## Troubleshooting

### Symlink Broken

```bash
# Check symlink target
ls -la bin/gitleaks

# Binaries are now directly in bin/ (no symlinks needed)
```

### Permission Denied

```bash
# Make executable
chmod +x bin/conftest
chmod +x bin/jade-stats
```

### Tool Not Found

```bash
# Verify PATH includes bin/
echo $PATH

# Add to PATH temporarily
export PATH="/home/jimmie/linkops-industries/GP-copilot/bin:$PATH"

# Add permanently (add to ~/.bashrc)
echo 'export PATH="/home/jimmie/linkops-industries/GP-copilot/bin:$PATH"' >> ~/.bashrc
```

---

## Related Files & Directories

- **bin/download-binaries.sh** - Script to download/update security tool binaries
- **GP-CONSULTING/scanners/** - Python wrapper scripts for all scanners
- **GP-CONSULTING/fixers/** - Automated fix generators
- **GP-CONSULTING/config/** - Scanner configuration files
- **GP-DATA/active/results/** - Scan results storage
- **GP-AI/cli/** - JADE CLI implementations

---

## Security Notes

- All binaries are verified downloads from official GitHub releases
- Symlinks point to system-installed tools or project directories
- Custom scripts (jade-stats) are auditable Python code
- No network access required for most tools (except update checks)
- Scan results are stored locally in GP-DATA/

---

## Version History

| Tool | Current Version | Latest Version | Update Priority |
|------|----------------|----------------|-----------------|
| bandit | 1.8.6 | - | Up to date |
| checkov | 3.2.471 | - | Up to date |
| conftest | 0.49.1 | - | Up to date |
| gitleaks | 8.18.0 | - | Up to date |
| kubescape | 3.0.3 | 3.0.15 | ⚠️ Medium |
| opa | 0.57.1 | - | Low |
| semgrep | Latest | - | Auto-updates |
| tfsec | 1.28.1 | - | Up to date |
| trivy | 0.48.0 | - | Up to date |

---

## Documentation Links

- [START_HERE.md](../START_HERE.md) - Platform quick start
- [GP-CONSULTING/README.md](../GP-CONSULTING/README.md) - Security agents overview
- [GP-AI/cli/README.md](../GP-AI/cli/README.md) - JADE CLI documentation
- [GP-TOOLS/README.md](../GP-TOOLS/README.md) - Additional tools and utilities

---

**Maintained by**: LinkOps Industries - JADE AI Security Platform Team