# OPA Policy Framework - Engineering Principles

**⚠️ READ THIS FIRST: Templates are starting points, not solutions.**

This framework doesn't just provide policies - it teaches you WHY they exist and WHEN to use them.

---

## 🎯 Core Engineering Principles

### 1. **Understand Before Implementing**
- Every policy addresses specific threat vectors
- Know the attack surface you're protecting
- Understand the business impact of blocking vs. allowing

### 2. **Context Over Copy-Paste**
- Client risk profiles differ
- Compliance requirements vary (SOC2 vs. FedRAMP vs. PCI-DSS)
- Infrastructure patterns are unique

### 3. **Policy Lifecycle Management**
```
Design → Test → Deploy → Monitor → Update
   ↑                                    ↓
   └────────── Feedback Loop ───────────┘
```

---

## 🏗️ Policy Framework Architecture

```
policies/
├── README.md                           # This file - Engineering principles
├── THREAT_MODEL.md                     # Attack vectors and mitigation strategies
├── COMPLIANCE_MAPPINGS.md              # CIS, NIST, SOC2 control mappings
│
├── opa/                                # Core OPA policies
│   ├── admission-control/              # Kubernetes admission policies
│   │   ├── pod-security.rego           # Pod security standards
│   │   ├── container-security.rego     # Container hardening
│   │   └── image-security.rego         # Image validation
│   │
│   ├── runtime-security/               # Runtime protection policies
│   │   ├── network-policies.rego       # Network segmentation
│   │   ├── rbac-policies.rego          # RBAC enforcement
│   │   └── resource-limits.rego        # Resource constraints
│   │
│   ├── compliance/                     # Compliance-specific policies
│   │   ├── cis-benchmarks.rego         # CIS Kubernetes benchmarks
│   │   ├── nist-controls.rego          # NIST cybersecurity framework
│   │   └── pci-dss.rego                # PCI-DSS requirements
│   │
│   └── custom-client/                  # Client-specific policies
│       └── template.rego                # Customizable template
│
├── testing/                            # Policy testing framework
│   ├── unit-tests/                     # Individual policy tests
│   ├── integration-tests/              # Multi-policy interaction tests
│   └── test-runner.sh                  # Test automation
│
├── generators/                         # Policy generation tools
│   ├── policy-generator.py             # Context-aware policy generator
│   └── templates/                      # Base templates with parameters
│
└── observability/                      # Policy monitoring
    ├── metrics.yaml                    # What to measure
    ├── alerts.yaml                     # When to alert
    └── dashboards/                     # Visualization configs
```

---

## 🔍 Critical Questions You Must Answer

### Before Writing Any Policy:

1. **What Attack Vector Does This Prevent?**
   - Privilege escalation?
   - Data exfiltration?
   - Resource exhaustion?
   - Supply chain attacks?

2. **What's The Business Impact?**
   - Will this block legitimate workloads?
   - What's the false positive rate?
   - How does this affect developer velocity?

3. **How Do You Validate It Works?**
   - Unit tests for policy logic
   - Integration tests for policy interactions
   - Chaos engineering for edge cases

4. **What's Your Rollback Strategy?**
   - Version control for policies
   - Gradual rollout mechanisms
   - Emergency bypass procedures

---

## 📚 Policy Categories & Their Purpose

### 1. **Pod Security Standards**
**Threat Mitigation**: Container breakout, privilege escalation
**Risk Level**: CRITICAL
**Compliance**: CIS 5.1, NIST AC-6

```rego
# Example: Enforce non-root containers
package kubernetes.admission.security

violation[{"msg": msg}] {
    input.review.object.spec.securityContext.runAsUser == 0
    msg := "Containers must not run as root (UID 0)"
}
```

**Key Understanding**: Running as root inside a container can lead to host compromise if combined with container escape vulnerabilities.

### 2. **Network Segmentation**
**Threat Mitigation**: Lateral movement, data exfiltration
**Risk Level**: HIGH
**Compliance**: CIS 5.3, NIST SC-7

### 3. **RBAC Enforcement**
**Threat Mitigation**: Unauthorized access, privilege abuse
**Risk Level**: HIGH
**Compliance**: CIS 5.1.1, NIST AC-2

### 4. **Resource Limits**
**Threat Mitigation**: DoS attacks, resource exhaustion
**Risk Level**: MEDIUM
**Compliance**: CIS 5.7, NIST SC-5

### 5. **Image Security**
**Threat Mitigation**: Supply chain attacks, vulnerable dependencies
**Risk Level**: HIGH
**Compliance**: CIS 5.4, NIST SA-12

---

## 🧪 Testing Your Understanding

### Scenario 1: Pod Security Violation
**Question**: A developer's pod is blocked by your security policy. It needs to run as root to bind to port 80. What's your solution?

**Wrong Answer**: Disable the policy
**Right Answer**:
1. Use capabilities instead of root (CAP_NET_BIND_SERVICE)
2. Use port > 1024 and configure service/ingress
3. Document the exception with compensating controls

### Scenario 2: Policy Conflicts
**Question**: Your network policy blocks legitimate traffic between services. How do you debug?

**Process**:
1. Check policy evaluation order
2. Verify label selectors
3. Test with `opa test` command
4. Monitor with policy decision logs

---

## 🛠️ Policy Development Workflow

### 1. **Threat Modeling**
```bash
# Document the threat
cat > threats/new-threat.md << EOF
THREAT: Cryptomining via compromised containers
VECTOR: Public image with embedded miners
IMPACT: Resource theft, performance degradation
MITIGATION: Image scanning, resource limits, behavioral monitoring
EOF
```

### 2. **Policy Design**
```rego
# Design with clear intent
package kubernetes.admission.images

# THREAT: Untrusted image sources
# COMPLIANCE: CIS 5.4.1
# RISK: HIGH
violation[{"msg": msg}] {
    image := input.review.object.spec.containers[_].image
    not starts_with(image, "registry.company.com/")
    msg := sprintf("Image must be from approved registry: %v", [image])
}
```

### 3. **Testing**
```bash
# Test with real scenarios
opa test policies/opa/admission-control/ -v
```

### 4. **Gradual Rollout**
```yaml
# Start in dry-run mode
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: opa-policies
webhooks:
  - name: validation.opa.security
    failurePolicy: Ignore  # Start permissive
    namespaceSelector:
      matchLabels:
        opa-enforcement: "testing"  # Limited scope
```

---

## 📊 Metrics & Observability

### What To Measure:
- **Policy evaluation time** (latency impact)
- **Violation frequency** (is it too restrictive?)
- **Policy coverage** (what's not protected?)
- **False positive rate** (developer friction)

### Alert On:
- Policy evaluation failures
- Sudden spike in violations
- Policy bypasses
- Performance degradation

---

## 🎓 Learning Resources

### Must-Understand Concepts:
1. **Admission Controllers vs. Runtime Security**
   - Admission: Prevent bad configs from deploying
   - Runtime: Detect/prevent bad behavior during execution

2. **Zero-Trust Architecture**
   - Never trust, always verify
   - Least privilege by default
   - Defense in depth

3. **Policy as Code Benefits**
   - Version control
   - Automated testing
   - Consistent enforcement
   - Audit trails

### Recommended Reading:
- [OPA Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## 🚀 Getting Started

### Step 1: Understand Your Environment
```bash
# Inventory current state
kubectl get pods --all-namespaces -o json | \
  jq '[.items[].spec.securityContext] | map(select(. != null))'
```

### Step 2: Start With High-Impact Policies
1. Prevent privileged containers
2. Enforce resource limits
3. Block untrusted images
4. Require security contexts

### Step 3: Measure Before Enforcing
Deploy in dry-run mode and monitor for 1-2 weeks before enforcement.

---

## ⚠️ Common Pitfalls

### 1. **Over-Restrictive Policies**
- Start permissive, tighten gradually
- Always have override mechanisms
- Document exceptions

### 2. **Ignoring Developer Experience**
- Provide clear error messages
- Offer remediation guidance
- Automate fixes where possible

### 3. **Policy Sprawl**
- Consolidate related policies
- Use policy libraries
- Maintain single source of truth

### 4. **Lack of Testing**
- Test policies before production
- Include negative test cases
- Validate policy interactions

---

## 🎯 Success Criteria

You know you've succeeded when:
1. **Policies are self-documenting** - Anyone can understand WHY
2. **Violations decrease over time** - Teams learn secure patterns
3. **Incidents are prevented** - Not just detected
4. **Compliance is automated** - Not manual checklists
5. **Developers embrace policies** - Not fight them

---

**Remember**: Security policies are about risk management, not perfection. Every policy is a trade-off between security and usability. Make informed decisions, not copy-paste choices.

**Your Next Step**: Read `THREAT_MODEL.md` to understand what you're protecting against.