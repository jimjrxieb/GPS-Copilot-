# GuidePoint OPA Policy Suite

## 📋 **Enterprise Security Policies - Production Ready**

This directory contains **production-grade OPA (Open Policy Agent) Rego policies** for comprehensive security governance across Kubernetes, infrastructure, and CI/CD pipelines.

---

## 🗂️ **Policy Structure**

### **Core Security Policies**
```
policies/opa/
├── security.rego                    # Basic container security
├── kubernetes.rego                  # K8s security controls  
├── network.rego                     # Network policy validation
├── rbac.rego                        # RBAC security checks
├── secrets-management.rego          # Secret handling & rotation (NEW)
├── image-security.rego              # Container image supply chain (NEW)
├── compliance-controls.rego         # Multi-framework compliance (NEW)
├── terraform-security.rego          # Multi-cloud IaC security (NEW)
├── cicd-security.rego              # CI/CD pipeline security (NEW)
└── admission-control/
    ├── pod-security.rego           # Advanced pod security (270+ lines)
    └── network-policies.rego       # Zero-trust networking (210+ lines)
```

---

## 🛡️ **Policy Coverage by Domain**

### **1. Kubernetes Pod Security** (`pod-security.rego`, `security.rego`)

**Controls:**
- ✅ Privileged container prevention (CVE-2019-5736)
- ✅ Non-root user enforcement (UID 0 blocking)
- ✅ Privilege escalation prevention
- ✅ Dangerous capabilities dropping (NET_ADMIN, SYS_ADMIN, etc.)
- ✅ Read-only root filesystem enforcement
- ✅ Resource limits (CPU/memory)

**Compliance:** CIS 5.2.x, SOC2 CC6.1, NIST AC-2, PCI-DSS 2.2.2

---

### **2. Secrets Management** (`secrets-management.rego`)

**Controls:**
- ✅ Secrets in env vars → volume mount migration
- ✅ Hardcoded secret detection (AWS keys, API tokens)
- ✅ Secret volume permission enforcement (0400)
- ✅ External secrets operator requirement
- ✅ Service account token auto-mount restriction
- ✅ Secret rotation metadata tracking

**Compliance:** CIS 5.4.x, PCI-DSS 3.4, NIST IA-5, SOC2 CC6.1

**Real Threat Prevention:**
- Process listing exposure
- Crash dump credential leakage
- Version control secret exposure

---

### **3. Container Image Security** (`image-security.rego`)

**Controls:**
- ✅ Trusted registry enforcement (supply chain)
- ✅ Latest tag prohibition (immutable tags required)
- ✅ Image signature verification (Cosign/Notary)
- ✅ Base image restrictions (distroless/minimal)
- ✅ ImagePullPolicy enforcement
- ✅ Vulnerability scan attestation

**Compliance:** CIS 5.1.x, SLSA Level 3, NIST SA-10

**Real Threat Prevention:**
- SolarWinds-style supply chain attacks
- Malicious image injection
- Known CVE deployment

---

### **4. Network Security** (`network-policies.rego`, `network.rego`)

**Controls:**
- ✅ Metadata service blocking (169.254.169.254, GCP metadata)
- ✅ Zero-trust network segmentation
- ✅ Egress policy enforcement
- ✅ Network zone labeling (dmz, internal, restricted, public)
- ✅ Cross-zone communication restrictions
- ✅ NetworkPolicy requirement for sensitive namespaces

**Compliance:** CIS 5.3.2, NIST SC-7, PCI-DSS 1.2.x, SOC2 CC6.6

**Real Threat Prevention:**
- Capital One breach pattern (SSRF to metadata)
- Lateral movement
- Data exfiltration

---

### **5. Compliance Controls** (`compliance-controls.rego`)

**Frameworks Covered:**
- SOC2 Type II
- PCI-DSS v4
- HIPAA
- ISO 27001
- GDPR

**Controls:**
- ✅ Resource labeling for audit trails
- ✅ Data classification enforcement (PII, PHI, cardholder data)
- ✅ Encryption at rest requirements
- ✅ Audit logging enforcement
- ✅ Retention policy compliance
- ✅ Change management documentation
- ✅ Environment segregation
- ✅ Data residency compliance (GDPR Art.44)
- ✅ Backup and disaster recovery
- ✅ Access control review (90-day certification)

---

### **6. Terraform Security** (`terraform-security.rego`)

**Multi-Cloud Coverage: AWS, Azure, GCP**

**AWS Controls:**
- ✅ S3 encryption + public access block
- ✅ RDS encryption + backup retention
- ✅ Security group 0.0.0.0/0 blocking
- ✅ EC2 IMDSv2 enforcement

**Azure Controls:**
- ✅ Storage account HTTPS-only
- ✅ NSG unrestricted access prevention

**GCP Controls:**
- ✅ GCS uniform bucket-level access
- ✅ GCE public IP restrictions

**Cross-Cloud:**
- ✅ Unencrypted volume detection
- ✅ Required tagging (Environment, Owner, CostCenter)
- ✅ State file backend encryption
- ✅ Remote backend requirement

**Compliance:** CIS-AWS, CIS-Azure, CIS-GCP, NIST SC-28, PCI-DSS 3.4

---

### **7. CI/CD Pipeline Security** (`cicd-security.rego`)

**Pipeline Controls:**
- ✅ Branch protection (main/prod requires 2+ approvals)
- ✅ GPG commit signing verification
- ✅ Dependency vulnerability scanning
- ✅ SAST enforcement
- ✅ Secret scanning (pre-commit)

**Container Controls:**
- ✅ Image vulnerability scanning (block on CRITICAL)
- ✅ Image signing requirement (Cosign/Notary)
- ✅ Approved base image enforcement

**Deployment Gates:**
- ✅ Security team review for production
- ✅ Rollback plan requirement
- ✅ Test coverage ≥80%
- ✅ SLSA provenance attestation

**Artifact Security:**
- ✅ Encrypted artifact storage
- ✅ Access logging
- ✅ Secret masking in logs

**Compliance:** SLSA Level 4, NIST SSDF, SOC2 CC7.2, PCI-DSS 10.2

---

## 🔗 **Integration with OPA Fixer**

The `opa_fixer.py` automatically remediates violations detected by these policies:

```python
# Policy violation detected
violation = {
    "msg": "Container 'nginx' running as privileged",
    "severity": "CRITICAL",
    "control": "CIS-5.2.5"
}

# Fixer automatically applies remediation
manifest['spec']['containers'][0]['securityContext']['privileged'] = False
```

**Complete Workflow:**
1. **OPA Scanner** → Evaluates `.rego` policies against resources
2. **Violations Detected** → CIS-5.2.5: Privileged container
3. **OPA Fixer** → Matches violation to fix pattern
4. **Automatic Remediation** → Removes privileged flag, creates backup, generates audit report

---

## 📊 **Compliance Mapping**

| Framework | Coverage | Key Controls |
|-----------|----------|--------------|
| **CIS Kubernetes** | 90%+ | 5.1.x, 5.2.x, 5.3.x, 5.4.x, 5.7.x |
| **SOC2 Type II** | Full | CC6.1, CC6.6, CC7.2, CC8.1, CC9.1 |
| **PCI-DSS v4** | Data Security | 1.2.x, 2.2.2, 3.4, 6.4.1, 10.2 |
| **NIST SP 800-53** | Key Controls | AC-2, AC-3, SC-7, SC-28, SA-10 |
| **SLSA Supply Chain** | Level 3-4 | Build L3, Source L3, Provenance |
| **ISO 27001** | Core | A.8.1, A.9.2.1, A.12.1.2, A.12.3 |
| **GDPR** | Data Protection | Art.30, Art.32, Art.44 |
| **HIPAA** | Security Rule | §164.312(a), §164.312(b) |

---

## 🚀 **Usage Examples**

### **Kubernetes Admission Control**
```bash
# Test policy against manifest
opa eval -i manifest.yaml -d policies/opa/pod-security.rego "data.kubernetes.admission.security.pods.violation"

# Deploy as admission webhook
kubectl apply -f opa-admission-webhook.yaml
```

### **Terraform Pre-Deployment Gate**
```bash
# Run policy check on Terraform plan
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary | opa eval -d policies/opa/terraform-security.rego -I -
```

### **CI/CD Pipeline Integration**
```yaml
# GitHub Actions example
- name: OPA Policy Check
  run: |
    opa eval -d policies/opa/cicd-security.rego \
      --input pipeline-metadata.json \
      --fail-defined "data.cicd.security.deny"
```

---

## 🎯 **Real-World Breach Prevention**

| Breach Pattern | Policy Protection |
|----------------|-------------------|
| **Container Escape** (CVE-2019-5736) | Privileged mode blocking |
| **Capital One** (SSRF to metadata) | Metadata service blocking |
| **SolarWinds** (Supply chain) | Image signature verification |
| **Log4Shell** (Vulnerable deps) | Dependency scanning gates |
| **Codecov** (Secret exposure) | Secret scanning + env var checks |
| **MongoDB Ransomware** | Backup policy enforcement |

---

## 📈 **Policy Metrics**

- **Total Policies:** 9 files
- **Total Rules:** 150+ security controls
- **Lines of Code:** 2,500+ lines
- **Compliance Frameworks:** 8 major frameworks
- **Cloud Coverage:** AWS, Azure, GCP
- **Supply Chain Security:** SLSA Level 4 ready

---

## 🔧 **Policy Testing**

```bash
# Run all policy tests
opa test policies/opa/ -v

# Test specific policy
opa test policies/opa/secrets-management.rego -v

# Generate test coverage report
opa test policies/opa/ --coverage --format=json
```

---

## 📝 **Contributing**

When adding new policies:
1. Include compliance mapping in metadata
2. Reference specific CVEs/breach patterns
3. Use fail-closed defaults (`default allow = false`)
4. Add helper functions for readability
5. Include real-world threat context
6. Write unit tests
7. Update this README

---

## ⚠️ **Production Deployment Notes**

1. **Start with warn mode**, graduate to deny
2. **Create exemption process** for legitimate use cases
3. **Monitor policy violations** before enforcement
4. **Test in staging** before production
5. **Document policy decisions** for audits
6. **Review policies quarterly** for relevance

---

**Last Updated:** 2024-09-24  
**Maintained By:** GuidePoint Security Engineering  
**Review Cycle:** Quarterly + post-incident updates
