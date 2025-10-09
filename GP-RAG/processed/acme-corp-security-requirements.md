# ACME Corporation - Security Assessment Requirements

**Client:** ACME Corporation
**Engagement:** Cloud Infrastructure Security Assessment
**Date:** 2025-10-03
**Consultant:** Jade AI Security Team

---

## Client Background

ACME Corporation is a mid-sized SaaS company providing financial management tools to 5,000+ customers. They are preparing for SOC 2 Type II certification and need a comprehensive security assessment.

## Infrastructure Overview

- **Cloud Platform:** AWS (us-east-1, us-west-2)
- **Kubernetes:** EKS clusters (production, staging, dev)
- **IaC:** Terraform for infrastructure provisioning
- **CI/CD:** GitHub Actions → ECR → EKS
- **Databases:** RDS PostgreSQL, DynamoDB
- **Monitoring:** CloudWatch, Datadog

## Compliance Requirements

### SOC 2 Type II Certification
- **Timeline:** Audit in 90 days
- **Focus Areas:**
  - Access controls (MFA, RBAC)
  - Data encryption (at-rest and in-transit)
  - Network segmentation
  - Audit logging and monitoring
  - Incident response procedures
  - Backup and disaster recovery

### Additional Compliance
- **GDPR:** EU customer data handling
- **PCI-DSS:** Payment card data (Stripe integration)
- **HIPAA:** Health data for 3 healthcare clients

## Security Assessment Scope

### 1. Kubernetes Security (Critical)
**Current Issues (from last pen test):**
- CrashLoopBackOff errors in production (app-payment pod)
- Pods running as root
- No network policies implemented
- Privileged containers in staging
- Missing resource limits (OOMKilled events)

**Requirements:**
- Implement Pod Security Standards (Restricted profile)
- Configure network policies (zero-trust micro-segmentation)
- Remediate all CrashLoopBackOff and OOMKilled issues
- RBAC audit (principle of least privilege)
- Secret rotation implementation

### 2. Terraform/IaC Security
**Current Issues:**
- Hardcoded secrets in terraform files
- S3 buckets without encryption
- Overly permissive security groups (0.0.0.0/0)
- No terraform state locking (DynamoDB)
- Terraform state stored in S3 without versioning

**Requirements:**
- Secrets management (AWS Secrets Manager integration)
- Terraform state security (encryption, locking, versioning)
- OPA policy enforcement for terraform plans
- Automated compliance scanning (Checkov, tfsec)

### 3. Application Security
**Stack:**
- Frontend: React (TypeScript)
- Backend: Python (FastAPI, Flask)
- Background jobs: Celery

**Current Issues:**
- SQL injection vulnerability (reported by Bandit)
- Hardcoded API keys in code
- Outdated dependencies (57 CVEs from Trivy)
- Missing CSRF tokens

**Requirements:**
- SAST scanning (Bandit, Semgrep)
- Dependency scanning (Trivy, Snyk)
- Secret scanning (Gitleaks)
- Code review and remediation

### 4. CI/CD Pipeline Security
**Requirements:**
- Container image scanning before deployment
- OPA/Gatekeeper admission control
- Signed container images
- SBOM generation
- Automated security gates (fail on CRITICAL/HIGH)

## Critical Findings to Address

### Priority 1: Immediate (< 1 week)
1. **CrashLoopBackOff in production payment pod**
   - Impact: Payment processing intermittent failures
   - Root cause: OOMKilled (256Mi limit, needs 512Mi)

2. **Hardcoded AWS credentials in `deploy/terraform/main.tf`**
   - Impact: Exposed in Git history
   - Action: Rotate credentials, implement Secrets Manager

3. **SQL Injection in user search endpoint**
   - CVE: CWE-89
   - Impact: Database access vulnerability
   - Fix: Parameterized queries

### Priority 2: Within 30 days
- Implement network policies (deny-all default)
- Remove privileged containers
- Configure pod security admission
- OPA policy enforcement
- Terraform state security

### Priority 3: Before SOC 2 audit (90 days)
- Full RBAC review
- Incident response runbooks
- Disaster recovery testing
- Security training for developers
- Compliance documentation

## Deliverables Required

1. **Security Assessment Report**
   - Executive summary
   - Detailed findings with CVSS scores
   - Remediation roadmap
   - Compliance gap analysis

2. **Remediation Implementation**
   - Fix all CRITICAL and HIGH findings
   - Provide terraform modules (compliant templates)
   - OPA policies for ongoing enforcement
   - CI/CD security pipeline

3. **Documentation**
   - Security runbooks
   - Incident response procedures
   - Compliance evidence for auditors
   - Developer security guidelines

## Success Criteria

- ✅ Zero CRITICAL vulnerabilities
- ✅ <5 HIGH vulnerabilities (documented exceptions)
- ✅ All Kubernetes pods passing Pod Security Standards
- ✅ 100% OPA policy compliance for Terraform
- ✅ Secrets rotation implemented
- ✅ Network policies enforced
- ✅ SOC 2 Type II certification achieved

## Timeline

- **Week 1-2:** Assessment and scanning
- **Week 3-4:** Critical fixes implementation
- **Week 5-8:** Medium/High fixes and policy enforcement
- **Week 9-12:** Documentation and compliance prep

## Contact Information

- **Primary Contact:** Jane Smith (CISO)
- **Email:** jane.smith@acmecorp.com
- **Technical Lead:** Bob Johnson (VP Engineering)
- **Email:** bob.johnson@acmecorp.com

---

**Notes for Jade:**
- Priority: CrashLoopBackOff in payment pod (business critical)
- Focus: Kubernetes security and OPA policy implementation
- Constraint: Must not disrupt production (zero-downtime deployments)
- Client has 2 DevOps engineers (limited capacity - need automation)
