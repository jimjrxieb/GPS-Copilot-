# SecOps Framework - CI/CD/Runtime Architecture

## Overview

This framework implements **shift-left security** by organizing scanners into three stages that mirror the software delivery lifecycle:

```
CI (Code)  →  CD (Deploy)  →  Runtime (Monitor)
  ↓              ↓                ↓
Fast         Medium           Real-time
Seconds      Minutes          24/7
Local        Cloud            Production
```

---

## Three Stages Explained

### CI (Continuous Integration) 🔍

**When:** Code commit, pull request, **before** deployment
**Speed:** Fast (seconds to minutes)
**Purpose:** Find vulnerabilities early when they're cheap to fix
**Tools:**

| Tool | Type | Language | Speed | Focus |
|------|------|----------|-------|-------|
| **Bandit** | SAST | Python | ~5s | Hardcoded secrets, SQL injection, weak crypto |
| **Semgrep** | SAST | Multi-language | ~10s | Code patterns, OWASP Top 10, business logic |
| **Gitleaks** | Secret Scanning | All | ~3s | AWS keys, API tokens, passwords in commits |
| **npm audit** | SCA | JavaScript | ~5s | Vulnerable npm packages, CVEs |
| **pip-audit** | SCA | Python | ~5s | Vulnerable Python packages, CVEs |
| **Trivy** | Container Scanning | Docker | ~15s | OS package vulnerabilities in images |

**Why CI First?**
- Runs on your laptop (no cloud needed)
- Fastest feedback loop
- Cheapest to fix (before production)
- Blocks bad code at source

---

### CD (Continuous Deployment) 🏗️

**When:** Terraform apply, kubectl apply, **during** infrastructure deployment
**Speed:** Medium (minutes)
**Purpose:** Validate infrastructure is secure before production
**Tools:**

| Tool | Type | Language | Speed | Focus |
|------|------|----------|-------|-------|
| **tfsec** | IaC Security | Terraform | ~10s | AWS misconfigurations (S3, RDS, VPC, IAM) |
| **Checkov** | IaC Security | Multi-cloud | ~15s | CIS benchmarks, policy violations |
| **OPA/Conftest** | Policy-as-Code | Terraform, K8s | ~5s | Custom policies (PCI-DSS, company standards) |
| **OPA Gatekeeper** | Admission Control | Kubernetes | ~100ms | Real-time policy enforcement (blocks violations) |
| **Kubescape** | K8s Security | Kubernetes | ~30s | CIS K8s Benchmark, NSA hardening |
| **AWS Config** | Cloud Posture | AWS | Real-time | Resource compliance validation |

**Why CD Second?**
- Validates infrastructure **before** deployment
- Catches misconfigurations early
- Enforces compliance (PCI-DSS, CIS, HIPAA)
- Fail-safe deployment gates

---

### Runtime (Production Monitoring) 🚨

**When:** 24/7 in production
**Speed:** Real-time
**Purpose:** Detect threats and monitor live systems
**Tools:**

| Tool | Type | Platform | Speed | Focus |
|------|------|----------|-------|-------|
| **Prometheus** | Metrics | Kubernetes | Real-time (15s scrape) | CPU, memory, request rates, error rates |
| **Grafana** | Visualization | Prometheus | Real-time | Dashboards, alerts, anomaly detection |
| **AWS GuardDuty** | Threat Detection | AWS | Real-time | Compromised instances, malicious IPs, crypto mining |
| **AWS Security Hub** | Cloud SIEM | AWS | Real-time | Aggregates GuardDuty, Config, Inspector, Macie |
| **CloudWatch Logs** | Logging | AWS | Real-time | Application logs, error tracking |
| **CloudTrail** | Audit Logging | AWS | Real-time | Who did what, when (API audit logs) |

**Why Runtime Last?**
- Requires production environment
- More complex setup (K8s, AWS)
- Continuous monitoring (not one-time scan)
- Incident response and forensics

---

## Usage

### Quick Start (CI only - no cloud needed)

```bash
cd secops/1-scanners

# Run CI scanners only (fast, local)
./run-all-ci-cd-runtime.sh --only-ci

# Output:
# [1/4] SAST (Bandit + Semgrep)...
# [2/4] Secret Scanning (Gitleaks)...
# [3/4] Dependency Scanning (npm + pip)...
# [4/4] Container Scanning (Trivy)...
# ✅ SCANNING COMPLETE (Duration: 45s)
```

### Run All Stages

```bash
# Run everything (CI + CD + Runtime)
./run-all-ci-cd-runtime.sh

# Skip runtime if no AWS/K8s cluster
./run-all-ci-cd-runtime.sh --skip-runtime

# Skip CI and CD (runtime monitoring only)
./run-all-ci-cd-runtime.sh --only-runtime
```

### Individual Stage Scripts

```bash
# CI Stage
cd ci/
./scan-code-sast.sh        # Bandit + Semgrep
./scan-secrets.sh          # Gitleaks
./scan-dependencies.sh     # npm audit + pip-audit
./scan-containers.sh       # Trivy

# CD Stage
cd ../cd/
./scan-iac.sh             # tfsec + Checkov + OPA
./scan-kubernetes.sh      # Kubescape + Gatekeeper
./scan-aws-compliance.sh  # AWS Config

# Runtime Stage
cd ../runtime/
./query-prometheus.sh     # Prometheus metrics
./query-guardduty.sh      # AWS GuardDuty
./query-cloudwatch.sh     # CloudWatch Logs
```

---

## Learning Path

### Week 1-2: Start with CI (Code Security)

**Focus:** Bandit, Gitleaks, Semgrep
**Why:** These run on your laptop, no cloud needed
**Time:** 1-2 weeks to master

**Hands-on:**
```bash
cd secops/1-scanners
./run-all-ci-cd-runtime.sh --only-ci

# Review findings
cd ../2-findings/raw
cat bandit-results.json | jq '.results[] | {severity, issue_text, filename}'
cat gitleaks-results.json | jq '.[] | {Description, File, Match}'
```

**Learn:**
- How to read SAST findings (false positives vs real issues)
- Common code vulnerabilities (SQL injection, XSS, hardcoded secrets)
- Dependency management (npm audit, pip-audit)

---

### Week 3-4: Move to CD (Infrastructure Security)

**Focus:** tfsec, Checkov, OPA
**Why:** Learn Terraform and Kubernetes security
**Time:** 2 weeks to master

**Hands-on:**
```bash
cd secops/1-scanners
./run-all-ci-cd-runtime.sh --only-cd

# Review infrastructure violations
cd ../2-findings/raw
cat tfsec-results.json | jq '.results[] | {severity, rule_id, description}'
cat checkov-results.json | jq '.results.failed_checks[] | {check_id, check_name, resource}'
```

**Learn:**
- Terraform security best practices (S3 encryption, RDS private, IAM least-privilege)
- Kubernetes hardening (CIS Benchmarks, pod security, RBAC)
- Policy-as-code (writing custom OPA policies)

---

### Week 5-8: Add Runtime (Cloud Security)

**Focus:** Prometheus, GuardDuty, CloudWatch
**Why:** Understand cloud monitoring and threat detection
**Time:** 3-4 weeks to master

**Hands-on:**
```bash
# Requires AWS credentials and K8s cluster
export AWS_PROFILE=securebank
export PROMETHEUS_URL=http://localhost:9090

cd secops/1-scanners
./run-all-ci-cd-runtime.sh --only-runtime

# Review runtime findings
cd ../2-findings/raw
cat guardduty-findings.json | jq '.Findings[] | {Type, Severity, Title}'
cat cloudwatch-errors.json | jq '.events[] | {timestamp, message}'
```

**Learn:**
- Prometheus metrics and PromQL queries
- AWS GuardDuty threat detection patterns
- Incident response workflows
- Log analysis with CloudWatch

---

## Integration Examples

### GitHub Actions (CI Pipeline)

```yaml
# .github/workflows/ci-security.yml
name: CI Security Scan

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run CI Security Scanners
        run: |
          cd secops/1-scanners
          ./run-all-ci-cd-runtime.sh --only-ci

      - name: Upload Findings
        uses: actions/upload-artifact@v3
        with:
          name: security-findings
          path: secops/2-findings/raw/
```

### Terraform Plan Hook (CD Pipeline)

```bash
# .git/hooks/pre-commit or CI/CD pipeline
cd secops/1-scanners
./run-all-ci-cd-runtime.sh --only-cd

# Fail if CRITICAL or HIGH issues found
CRITICAL=$(jq '[.results[] | select(.severity == "CRITICAL")] | length' ../2-findings/raw/tfsec-results.json)

if [ "$CRITICAL" -gt 0 ]; then
  echo "❌ CRITICAL issues found in Terraform. Fix before deploying."
  exit 1
fi
```

### Kubernetes Admission Control (CD Enforcement)

```bash
# Install OPA Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Apply constraint templates (from secops/policies/opa/)
kubectl apply -f infrastructure/k8s/opa-gatekeeper.yaml

# Test enforcement
kubectl run test-root --image=nginx --restart=Never
# Result: Denied by K8sRequireNonRoot policy ✅
```

---

## AWS Services by Stage

### CD Stage (Deployment Validation):
- **AWS Secrets Manager** - Store credentials securely
- **AWS Config** - Validate resource compliance
- **VPC & Security Groups** - Network isolation

### Runtime Stage (Production Monitoring):
- **CloudWatch** - Logs and metrics
- **GuardDuty** - Threat detection
- **Security Hub** - Aggregated findings
- **CloudTrail** - API audit logs
- **Prometheus/Grafana** - Kubernetes monitoring

---

## Troubleshooting

### CI scanners fail with "command not found"

Install missing tools:
```bash
# Bandit (Python SAST)
pip install bandit

# Semgrep (Multi-language SAST)
pip install semgrep

# Gitleaks (Secret scanning)
brew install gitleaks  # macOS
# or download from https://github.com/gitleaks/gitleaks/releases

# Trivy (Container scanning)
brew install aquasecurity/trivy/trivy  # macOS
```

### CD scanners fail with "AWS credentials not configured"

Configure AWS CLI:
```bash
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format
```

### Runtime monitors fail with "Prometheus not accessible"

Set Prometheus URL:
```bash
export PROMETHEUS_URL=http://localhost:9090

# Or port-forward from K8s
kubectl port-forward -n monitoring svc/prometheus-server 9090:80
```

---

## File Structure

```
secops/
├── 1-scanners/
│   ├── ci/                          # CI scanners (code-level)
│   │   ├── scan-code-sast.sh       # Bandit + Semgrep
│   │   ├── scan-secrets.sh         # Gitleaks
│   │   ├── scan-dependencies.sh    # npm audit + pip-audit
│   │   └── scan-containers.sh      # Trivy
│   │
│   ├── cd/                          # CD scanners (infrastructure)
│   │   ├── scan-iac.sh             # tfsec + Checkov + OPA
│   │   ├── scan-kubernetes.sh      # Kubescape + Gatekeeper
│   │   └── scan-aws-compliance.sh  # AWS Config
│   │
│   ├── runtime/                     # Runtime monitors
│   │   ├── query-prometheus.sh     # Prometheus metrics
│   │   ├── query-guardduty.sh      # AWS GuardDuty
│   │   └── query-cloudwatch.sh     # CloudWatch Logs
│   │
│   ├── run-all-ci-cd-runtime.sh    # Master orchestrator
│   └── scanners-config.yaml        # Tool configuration
│
├── 2-findings/
│   ├── raw/                         # Raw JSON outputs
│   └── reports/                     # Human-readable reports
│
├── 3-fixers/
│   ├── ci-fixes/                    # Auto-fixers for CI issues
│   ├── cd-fixes/                    # Auto-fixers for CD issues
│   └── runtime-fixes/               # Auto-fixers for runtime issues
│
└── policies/
    └── opa/                         # Custom OPA policies
```

---

## Next Steps

1. **Start with CI:** Run `./run-all-ci-cd-runtime.sh --only-ci` (no setup needed)
2. **Learn tools:** Review findings in `../2-findings/raw/*.json`
3. **Fix issues:** Run auto-fixers in `../3-fixers/`
4. **Move to CD:** Set up Terraform and Kubernetes
5. **Add Runtime:** Deploy to AWS and enable GuardDuty
6. **Integrate CI/CD:** Add to GitHub Actions or Jenkins

---

## Resources

- **CI Scanners:**
  - [Bandit](https://bandit.readthedocs.io/)
  - [Semgrep](https://semgrep.dev/docs/)
  - [Gitleaks](https://github.com/gitleaks/gitleaks)
  - [Trivy](https://github.com/aquasecurity/trivy)

- **CD Scanners:**
  - [tfsec](https://github.com/aquasecurity/tfsec)
  - [Checkov](https://www.checkov.io/)
  - [OPA](https://www.openpolicyagent.org/)
  - [Kubescape](https://github.com/kubescape/kubescape)

- **Runtime Monitors:**
  - [Prometheus](https://prometheus.io/)
  - [Grafana](https://grafana.com/)
  - [AWS GuardDuty](https://aws.amazon.com/guardduty/)

---

## Contact

For questions or issues:
- See `secops-config.yaml` for tool details
- Check `2-findings/reports/` for findings
- Run with `--help` flag for usage information
