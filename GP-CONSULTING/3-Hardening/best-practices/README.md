# Infrastructure Hardening Best Practices

**Purpose:** Production-ready best practices for IaC, Kubernetes, and OPA policy enforcement

---

## Overview

This directory contains **battle-tested best practices** for:
- Infrastructure as Code (Terraform, CloudFormation)
- Kubernetes security and reliability
- OPA policy design and enforcement
- Container hardening
- Secrets management

**When to use:** Before deploying any infrastructure or Kubernetes resources

---

## Directory Structure

```
best-practices/
├── README.md                          # This file
├── iac-best-practices.md              # Terraform/CloudFormation guidelines
├── kubernetes-best-practices.md       # K8s security and reliability
├── opa-best-practices.md              # Policy design patterns
├── container-hardening.md             # Docker/container security
├── secrets-management.md              # Vault/Secrets Manager patterns
└── checklists/
    ├── pre-deployment-checklist.md    # Before deploy
    ├── post-deployment-checklist.md   # After deploy
    └── production-readiness.md        # Production gate
```

---

## Quick Reference

### IaC Best Practices
See: [iac-best-practices.md](iac-best-practices.md)

**Critical rules:**
1. ✅ Always use remote state (S3 + DynamoDB)
2. ✅ Enable state encryption
3. ✅ Use workspaces for environments
4. ✅ Implement `terraform plan` before `apply`
5. ✅ Never commit secrets to version control

### Kubernetes Best Practices
See: [kubernetes-best-practices.md](kubernetes-best-practices.md)

**Critical rules:**
1. ✅ Always set resource limits/requests
2. ✅ Run containers as non-root
3. ✅ Use readiness/liveness probes
4. ✅ Enable network policies
5. ✅ Use Pod Security Standards (restricted)

### OPA Best Practices
See: [opa-best-practices.md](opa-best-practices.md)

**Critical rules:**
1. ✅ Test policies with `opa test`
2. ✅ Use deny-by-default approach
3. ✅ Separate policy from data
4. ✅ Version policies in Git
5. ✅ Monitor policy violations

---

## Pre-Deployment Checklist

See: [checklists/pre-deployment-checklist.md](checklists/pre-deployment-checklist.md)

```bash
# Run before ANY deployment
cd ../monitoring-alerting/
./pre-deployment-health-check.sh /path/to/project
```

**Must verify:**
- [ ] All secrets in Vault/Secrets Manager (not hardcoded)
- [ ] Resource limits set on all pods
- [ ] Network policies defined
- [ ] OPA policies passing
- [ ] Monitoring/alerting configured
- [ ] Rollback plan documented

---

## When Deployment Fails

See: [../rollback-mitigation/](../rollback-mitigation/)

**Immediate actions:**
1. **Stop deployment:** `kubectl rollout undo deployment/app` or `terraform destroy`
2. **Check health:** `cd ../monitoring-alerting/ && ./deployment-health-check.sh`
3. **Run mitigation:** `cd ../rollback-mitigation/ && ./auto-rollback.sh`
4. **Escalate:** `cd ../escalation/ && ./escalate-incident.sh`

---

## Integration with Other Phases

### ← Phase 1: Security Assessment
**Use:** Run Phase 1 scanners to verify best practices compliance

```bash
cd ../../1-Security-Assessment/cd-scanners/
./scan-iac.py /path/to/terraform  # Verify IaC best practices
./scan-kubernetes.py /path/to/k8s  # Verify K8s best practices
```

### ← Phase 2: App-Sec-Fixes
**Use:** Ensure application security before infrastructure deployment

```bash
cd ../../2-App-Sec-Fixes/fixers/
./fix-hardcoded-secrets.sh /path/to/project  # Remove hardcoded secrets
```

### → Phase 4: Cloud Migration
**Use:** Apply best practices during AWS migration

```bash
# Phase 4 references Phase 3 best practices
cd ../../4-Cloud-Migration/terraform-modules/
# Follow: ../../3-Hardening/best-practices/iac-best-practices.md
```

---

## Documentation

1. **[IaC Best Practices](iac-best-practices.md)** - Terraform/CloudFormation
2. **[Kubernetes Best Practices](kubernetes-best-practices.md)** - K8s security
3. **[OPA Best Practices](opa-best-practices.md)** - Policy design
4. **[Container Hardening](container-hardening.md)** - Docker security
5. **[Secrets Management](secrets-management.md)** - Vault patterns

---

**Status:** ✅ Production-Ready
**Last Updated:** 2025-10-14
