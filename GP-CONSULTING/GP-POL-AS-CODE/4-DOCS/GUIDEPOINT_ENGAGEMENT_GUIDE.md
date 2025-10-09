# GuidePoint Client Engagement - OPA Policy Implementation

**Purpose**: Practical guide for security consultants deploying OPA policies at client sites.

This isn't theory. This is how you actually use the framework in the field.

---

## 📋 Pre-Engagement Checklist

### Information Gathering (Week -1)

**Client Discovery Questions**:
```yaml
business_context:
  - What industry? (Healthcare → HIPAA, Finance → PCI-DSS)
  - What's the data sensitivity? (PII, PHI, Financial, IP)
  - What's the regulatory environment? (SOC2, ISO27001, FedRAMP)
  - What's the risk tolerance? (Startup vs. Enterprise)

technical_environment:
  - Kubernetes version?
  - Cloud provider? (AWS, Azure, GCP, On-prem)
  - Existing security tools? (Service mesh, admission controllers)
  - CI/CD pipeline? (Jenkins, GitLab, GitHub Actions)

operational_constraints:
  - Developer team size and skill level?
  - Change management process?
  - Testing environment availability?
  - Deployment windows?
```

**Critical Early Wins**:
1. Map existing violations (baseline scan)
2. Identify quick wins (low-hanging fruit)
3. Build business case with metrics
4. Get executive buy-in early

---

## 🎯 Week 1: Assessment & Planning

### Day 1-2: Baseline Security Scan

```bash
# Step 1: Audit current state
kubectl get pods --all-namespaces -o json | jq '
  .items[] | select(
    .spec.securityContext.privileged == true or
    .spec.containers[].securityContext.privileged == true
  ) | {
    namespace: .metadata.namespace,
    pod: .metadata.name,
    issue: "privileged container"
  }
'

# Step 2: Network policy coverage
kubectl get networkpolicies --all-namespaces -o json | jq '
  .items | length
' # Compare to namespace count

# Step 3: RBAC audit
kubectl get clusterrolebindings -o json | jq '
  .items[] | select(
    .roleRef.name == "cluster-admin" and
    .subjects[].kind == "ServiceAccount"
  ) | {
    binding: .metadata.name,
    issue: "service account with cluster-admin"
  }
'
```

**Deliverable**: Security posture report
- Current violation count
- Risk prioritization matrix
- Estimated remediation effort

### Day 3-4: Threat Modeling Workshop

**Facilitate with client team**:
```
1. Asset Identification
   - What data/systems are critical?
   - What's the impact of compromise?

2. Attack Vector Analysis
   - External attackers (internet-facing)
   - Insider threats (compromised accounts)
   - Supply chain (vulnerable dependencies)

3. Control Mapping
   - Existing controls
   - Control gaps
   - Remediation priorities
```

**Deliverable**: Threat model document
- Attack trees for top 5 risks
- Control recommendations
- Policy implementation roadmap

### Day 5: Policy Selection & Customization

**NOT copy-paste. Context-aware selection:**

```python
# Example: Client context analysis
client_profile = {
    "industry": "Healthcare",
    "compliance": ["HIPAA", "SOC2"],
    "risk_level": "HIGH",
    "maturity": "Medium"
}

recommended_policies = {
    # CRITICAL - Deploy first
    "privileged-containers": "DENY",  # Container escape prevention
    "host-namespaces": "DENY",        # Isolation enforcement
    "rbac-wildcards": "DENY",         # Privilege escalation prevention

    # HIGH - Deploy week 2
    "resource-limits": "ENFORCE",     # DoS prevention
    "network-policies": "ENFORCE",    # Lateral movement prevention
    "image-scanning": "ENFORCE",      # Supply chain security

    # MEDIUM - Deploy week 3
    "security-contexts": "ENFORCE",   # Defense in depth
    "pod-security-standards": "ENFORCE",

    # Compliance-specific
    "hipaa-encryption": "ENFORCE" if "HIPAA" in client_profile["compliance"] else "OPTIONAL",
    "pci-segmentation": "ENFORCE" if "PCI-DSS" in client_profile["compliance"] else "OPTIONAL"
}
```

---

## 🚀 Week 2: Pilot Deployment

### Phase 1: Non-Production Testing (Day 1-3)

```bash
# Deploy in dry-run mode
cat > opa-deployment-pilot.yaml << EOF
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: opa-validation-pilot
webhooks:
  - name: validation.opa.security
    failurePolicy: Ignore  # Non-blocking initially
    namespaceSelector:
      matchLabels:
        opa-pilot: "true"  # Only test namespaces
    clientConfig:
      service:
        name: opa
        namespace: opa-system
        path: "/v1/admit"
    rules:
      - operations: ["CREATE", "UPDATE"]
        apiGroups: [""]
        apiVersions: ["v1"]
        resources: ["pods"]
EOF

# Label test namespace
kubectl label namespace dev opa-pilot=true

# Monitor policy evaluations
kubectl logs -n opa-system -l app=opa -f | grep -i violation
```

**Observe for 48 hours**:
- Violation frequency
- False positive rate
- Performance impact (<100ms latency target)

### Phase 2: Production Dry-Run (Day 4-5)

```bash
# Expand to production namespaces (still dry-run)
kubectl label namespace production opa-pilot=true

# Collect metrics
curl http://opa-service:8181/metrics | grep policy_evaluation
```

**Key metrics**:
- Violations per hour by policy
- Top violated policies
- Most affected namespaces
- Policy evaluation latency

---

## 🛡️ Week 3: Production Enforcement

### Gradual Rollout Strategy

```bash
# Phase 1: Enforce critical policies only
cat > opa-enforcement-phase1.yaml << EOF
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: opa-enforcement
webhooks:
  - name: critical-policies.opa.security
    failurePolicy: Fail  # Block violations
    namespaceSelector:
      matchExpressions:
      - key: opa-enforcement
        operator: In
        values: ["critical-only"]
    # ... rest of config
EOF

# Enable per namespace
kubectl label namespace production opa-enforcement=critical-only
```

**Day 1-2: Critical policies**:
- Privileged containers (container escape)
- Host namespaces (isolation)
- Cluster-admin bindings (privilege escalation)

**Day 3-4: High-priority policies**:
- Network policies (lateral movement)
- Resource limits (DoS prevention)
- Image validation (supply chain)

**Day 5: Full enforcement**:
- All policies active
- Monitor for issues
- Emergency bypass procedure ready

---

## 📊 Week 4: Validation & Documentation

### Compliance Evidence Generation

```bash
# Generate SOC2 evidence
opa eval -d policies/opa/compliance/ -i audit-log.json \
  'data.soc2.cc6_1.evidence' > soc2-cc6.1-evidence.json

# CIS Benchmark scoring
opa test policies/opa/cis/ --coverage --format=json > cis-benchmark-score.json

# HIPAA controls validation
opa eval -d policies/opa/hipaa/ -i workload-inventory.json \
  'data.hipaa.controls' > hipaa-controls-report.json
```

### Client Deliverables

**1. Executive Summary** (for C-suite):
```markdown
# Security Posture Improvement Report

**Engagement Period**: [dates]
**Consultant**: GuidePoint Security

## Key Achievements
- Reduced attack surface by 85% (privileged containers eliminated)
- Achieved 92% CIS Kubernetes Benchmark compliance (up from 45%)
- Implemented zero-trust networking for all production workloads
- Generated SOC2 Type II control evidence (CC6.1, CC6.6, CC7.1)

## Business Impact
- Security incidents prevented: 3 (estimated)
- Compliance readiness: SOC2 audit-ready
- Risk reduction: HIGH → LOW for container escape
- Developer productivity: Minimal impact (2% latency increase)

## ROI Calculation
- Security tool cost: $0 (OPA is open source)
- Implementation effort: 4 weeks
- Prevented breach value: $4.2M (industry average)
- ROI: 10,500%
```

**2. Technical Documentation** (for engineering team):
```markdown
# OPA Policy Implementation Guide

## Policy Catalog
[Table of all deployed policies with threat/compliance mapping]

## Operational Procedures
- Policy update process
- Emergency bypass procedure
- Troubleshooting guide
- Monitoring and alerting

## Testing Framework
- Unit test examples
- Integration test scenarios
- Chaos engineering tests

## Maintenance
- Quarterly policy review checklist
- Threat model update process
- Compliance mapping refresh
```

**3. Compliance Artifacts** (for auditors):
- Policy-to-control mapping matrix
- Audit log retention configuration
- Evidence collection automation
- Exception documentation (with business justification)

---

## 🔧 Common Client Scenarios

### Scenario 1: Developer Pushback

**Symptom**: "Policies are blocking our deployments!"

**Root Cause Analysis**:
```bash
# Check violation patterns
opa eval -d policies/opa/ -i rejected-pods.json 'data.violations' | \
  jq '.[] | group_by(.policy) | .[] | {
    policy: .[0].policy,
    count: length,
    examples: [.[0:3]]
  }'
```

**Resolution**:
1. Provide clear error messages with remediation steps
2. Document legitimate exceptions with business justification
3. Create policy exemption process with approval workflow
4. Offer automated fixes where possible

### Scenario 2: Performance Concerns

**Symptom**: API server latency increased

**Investigation**:
```bash
# Measure policy evaluation time
kubectl logs -n opa-system -l app=opa | grep -E "evaluation|latency" | \
  awk '{sum+=$NF; count++} END {print "Average:", sum/count, "ms"}'
```

**Optimization**:
- Cache policy decisions for identical requests
- Optimize Rego rules (avoid unnecessary iterations)
- Scale OPA pods horizontally
- Consider policy pre-compilation

### Scenario 3: Emergency Policy Bypass

**Symptom**: Critical production deployment blocked by policy

**Emergency Procedure**:
```bash
# Temporary bypass (use sparingly!)
kubectl annotate namespace production opa-bypass=true --overwrite

# Deploy critical fix

# Re-enable enforcement
kubectl annotate namespace production opa-bypass- --overwrite

# Document in incident report
echo "Emergency bypass used: [reason] [approver] [duration]" >> bypass-log.md
```

---

## 📈 Success Metrics Dashboard

**Track these KPIs weekly**:

```yaml
security_metrics:
  violation_trend:
    week_1: 450  # Baseline
    week_2: 320  # Remediation starts
    week_3: 85   # Enforcement begins
    week_4: 12   # Legitimate exceptions only
    target: <20

  coverage_metrics:
    pods_protected: 95%
    namespaces_enforced: 100%
    policies_active: 15
    compliance_score: 92%

operational_metrics:
  policy_evaluation_latency: "45ms (p95)"
  false_positive_rate: "3%"
  developer_satisfaction: "8/10"
  deployment_success_rate: "97%"
```

---

## 🎓 Knowledge Transfer

### Train the Client Team

**Week 4 Workshop Agenda**:

1. **Policy Engineering Fundamentals** (2 hours)
   - Threat modeling basics
   - OPA Rego syntax
   - Testing methodologies

2. **Operational Procedures** (2 hours)
   - Policy update workflow
   - Incident response
   - Troubleshooting guide

3. **Hands-On Lab** (3 hours)
   - Write custom policy
   - Test with opa test
   - Deploy to cluster
   - Monitor violations

4. **Compliance Integration** (1 hour)
   - Evidence generation
   - Audit preparation
   - Documentation maintenance

**Deliverable**: Certified internal policy administrators

---

## ⚠️ Red Flags to Watch For

**Warning signs of implementation issues**:
- Violation count increasing over time (policy drift)
- High false positive rate (>10%) (overly restrictive)
- Frequent emergency bypasses (poor exception handling)
- Developer circumvention attempts (lack of buy-in)
- No policy updates in 3+ months (stale threat model)

**Immediate actions**:
- Review threat model relevance
- Gather developer feedback
- Audit policy effectiveness
- Refresh compliance mappings

---

## 🎯 Final Client Handoff

### Transition Checklist

- [ ] All policies documented with WHY
- [ ] Runbooks for common scenarios
- [ ] Emergency procedures tested
- [ ] Team trained and certified
- [ ] Compliance evidence automated
- [ ] Monitoring/alerting configured
- [ ] Quarterly review scheduled
- [ ] Escalation contacts defined

### Ongoing Support Options

**Tier 1: Self-Service** (Included)
- Documentation portal
- Community Slack channel
- Quarterly threat model reviews

**Tier 2: Managed Service** (Paid)
- Policy updates for new threats
- Compliance mapping maintenance
- Quarterly security assessments
- 24/7 incident response

**Tier 3: Strategic Advisory** (Retainer)
- Executive security briefings
- Board-level reporting
- M&A security due diligence
- Regulatory change management

---

## 💼 Business Development

**Success = New Opportunities**:

1. **Expand within account**:
   - Additional clusters/regions
   - Related projects (service mesh, secrets management)
   - Advanced security (runtime protection, SIEM integration)

2. **Case study development**:
   - Before/after metrics
   - ROI calculations
   - Client testimonial

3. **Reference architecture**:
   - Industry-specific packages (Healthcare, Finance)
   - Reusable for similar engagements
   - Marketing collateral

---

**Remember**: You're not selling OPA policies. You're selling security expertise, compliance confidence, and risk reduction.

**The policies are just the vehicle. Understanding is the value.**

Now go make your client more secure than they've ever been. 🛡️