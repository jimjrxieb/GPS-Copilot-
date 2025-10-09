# Kubernetes Threat Model & Attack Vectors

**Purpose**: Understanding threats BEFORE writing policies. If you don't know what you're defending against, your policies are just bureaucracy.

---

## 🎯 Attack Surface Map

```
┌─────────────────────────────────────────────────────┐
│                   External Attackers                 │
└────────────┬────────────────────────────┬───────────┘
             │                            │
     ┌───────▼────────┐           ┌──────▼──────┐
     │   Ingress      │           │  Supply     │
     │   (Network)    │           │  Chain      │
     └───────┬────────┘           └──────┬──────┘
             │                            │
     ┌───────▼────────────────────────────▼──────────┐
     │           Kubernetes Control Plane            │
     │  (API Server, etcd, Controller, Scheduler)    │
     └───────┬────────────────────────────┬──────────┘
             │                            │
     ┌───────▼────────┐           ┌──────▼──────┐
     │   Workload     │           │   Node      │
     │  (Containers)  │           │  (Kubelet)  │
     └───────┬────────┘           └──────┬──────┘
             │                            │
     ┌───────▼────────────────────────────▼──────────┐
     │              Host Operating System            │
     │              (Kernel, Storage, Network)       │
     └────────────────────────────────────────────────┘
```

---

## 🔴 Critical Attack Vectors

### 1. Container Escape → Host Compromise
**Attack Chain**:
```
Vulnerable Container → Kernel Exploit → Root on Host → Cluster Takeover
```

**Real Example**: CVE-2019-5736 (runC container escape)
- Attacker overwrites host runC binary
- Next container execution gives root access
- Complete cluster compromise possible

**Mitigation Policies**:
```rego
# Prevent privileged containers
deny[msg] {
    input.request.object.spec.containers[_].securityContext.privileged == true
    msg := "Privileged containers can escape to host"
}

# Enforce seccomp profiles
deny[msg] {
    not input.request.object.spec.securityContext.seccompProfile
    msg := "Seccomp profile required to limit syscalls"
}
```

### 2. RBAC Abuse → Privilege Escalation
**Attack Chain**:
```
Service Account → Role Binding → Cluster Admin → Game Over
```

**Real Example**: Default service account with excessive permissions
- Pod compromised via application vulnerability
- Service account token accessed
- Token used to create new privileged pods
- Lateral movement across cluster

**Mitigation Policies**:
```rego
# Prevent wildcard permissions
deny[msg] {
    input.request.object.rules[_].verbs[_] == "*"
    msg := "Wildcard verbs are privilege escalation vectors"
}

# Block risky role bindings
deny[msg] {
    input.request.object.roleRef.name == "cluster-admin"
    input.request.object.subjects[_].kind == "ServiceAccount"
    msg := "Service accounts should not have cluster-admin"
}
```

### 3. Supply Chain Attacks → Backdoored Images
**Attack Chain**:
```
Compromised Registry → Malicious Image → Cryptominer/Backdoor → Data Theft
```

**Real Example**: Docker Hub cryptomining images
- Thousands of images with hidden miners
- Legitimate-looking names
- Steal compute resources
- Potential data exfiltration

**Mitigation Policies**:
```rego
# Enforce image signing
deny[msg] {
    image := input.request.object.spec.containers[_].image
    not image_signed(image)
    msg := sprintf("Unsigned image detected: %v", [image])
}

# Require vulnerability scanning
deny[msg] {
    image := input.request.object.spec.containers[_].image
    scan_result := image_scan(image)
    scan_result.critical_vulns > 0
    msg := sprintf("Image has critical vulnerabilities: %v", [image])
}
```

### 4. Network Lateral Movement → Data Exfiltration
**Attack Chain**:
```
Compromised Pod → Network Access → Database → Sensitive Data → External Transfer
```

**Real Example**: Capital One breach pattern
- SSRF vulnerability in application
- Access to metadata service
- Credential theft
- S3 bucket access
- 100 million records stolen

**Mitigation Policies**:
```rego
# Default deny network policies
deny[msg] {
    not input.request.object.spec.podSelector
    msg := "Network policy must specify pod selector"
}

# Block metadata service access
deny[msg] {
    egress := input.request.object.spec.egress[_]
    egress.to[_].ipBlock.cidr == "169.254.169.254/32"
    msg := "Metadata service access blocked"
}
```

### 5. Resource Exhaustion → Denial of Service
**Attack Chain**:
```
No Limits → Resource Consumption → Node Pressure → Cluster Instability
```

**Real Example**: Fork bomb in container
- Single container consumes all CPU/memory
- Node becomes unresponsive
- Scheduler can't place new pods
- Cascading failure across cluster

**Mitigation Policies**:
```rego
# Enforce resource limits
deny[msg] {
    container := input.request.object.spec.containers[_]
    not container.resources.limits.memory
    msg := "Memory limits required to prevent DoS"
}

# Prevent resource ratio abuse
deny[msg] {
    container := input.request.object.spec.containers[_]
    limits := container.resources.limits.cpu
    requests := container.resources.requests.cpu
    to_number(limits) / to_number(requests) > 2
    msg := "CPU limit/request ratio too high"
}
```

---

## 🟡 High-Risk Attack Vectors

### 6. Secret Exposure → Credential Theft
**Attack Path**: Environment variables → Process listing → Secret extraction
**Mitigation**: Never use env vars for secrets, use mounted volumes

### 7. DNS Hijacking → MITM Attacks
**Attack Path**: Compromise CoreDNS → Redirect traffic → Steal credentials
**Mitigation**: DNSSEC, network policies, pod security policies

### 8. Admission Webhook Bypass → Policy Evasion
**Attack Path**: Direct API access → Bypass webhooks → Deploy malicious workloads
**Mitigation**: Multiple enforcement points, audit logging

### 9. etcd Compromise → Complete Cluster Takeover
**Attack Path**: etcd access → Read all secrets → Modify all objects
**Mitigation**: Encryption at rest, strict RBAC, network isolation

### 10. Kubelet Exploitation → Node Compromise
**Attack Path**: Exposed kubelet API → Anonymous access → Container manipulation
**Mitigation**: Disable anonymous auth, use TLS, restrict API access

---

## 🟢 Medium-Risk Attack Vectors

### 11. Log Injection → SIEM Confusion
**Impact**: Hide malicious activity, confuse incident response

### 12. Sidecar Container Abuse → Hidden Processes
**Impact**: Concealed malicious activity, persistence

### 13. Init Container Manipulation → Boot-time Compromise
**Impact**: Privilege escalation, secret theft

### 14. Volume Mount Abuse → Data Access
**Impact**: Access to host filesystem, other container data

### 15. Service Mesh Exploitation → Traffic Interception
**Impact**: MITM attacks, data modification

---

## 🛡️ Defense-in-Depth Strategy

### Layer 1: Admission Control
```
Block bad configurations before deployment
├── Pod Security Standards
├── Resource Requirements
├── Image Validation
└── RBAC Verification
```

### Layer 2: Runtime Protection
```
Detect and prevent malicious behavior
├── Network Policies
├── Seccomp/AppArmor
├── SELinux
└── Falco Rules
```

### Layer 3: Continuous Monitoring
```
Observe and respond to anomalies
├── Audit Logging
├── Metrics Collection
├── Behavior Analysis
└── Incident Response
```

---

## 📊 Risk Matrix

| Attack Vector | Likelihood | Impact | Risk Score | Priority |
|--------------|------------|--------|------------|----------|
| Container Escape | Medium | Critical | 9/10 | P0 |
| RBAC Abuse | High | High | 8/10 | P0 |
| Supply Chain | High | High | 8/10 | P0 |
| Network Lateral Movement | High | Medium | 7/10 | P1 |
| Resource Exhaustion | High | Medium | 6/10 | P1 |
| Secret Exposure | Medium | High | 7/10 | P1 |
| DNS Hijacking | Low | High | 5/10 | P2 |
| Admission Bypass | Low | Critical | 6/10 | P1 |
| etcd Compromise | Low | Critical | 7/10 | P1 |
| Kubelet Exploitation | Medium | High | 7/10 | P1 |

---

## 🎯 Threat Modeling Questions

### For Every Workload, Ask:

1. **What sensitive data does it access?**
   - Databases, APIs, file systems
   - Secrets, tokens, certificates
   - PII, financial data, health records

2. **What's its blast radius if compromised?**
   - Network access scope
   - Permission scope
   - Data access scope

3. **What are its dependencies?**
   - External services
   - Third-party libraries
   - Base images

4. **How is it exposed?**
   - Internet-facing?
   - Internal only?
   - Service mesh participant?

5. **What's its criticality?**
   - Business impact if unavailable
   - Data sensitivity
   - Compliance requirements

---

## 🔍 Detection Strategies

### Indicators of Compromise (IoCs)

**Container Escape Attempts**:
```bash
# Suspicious syscalls
- mount
- ptrace
- kernel module loading
```

**RBAC Abuse**:
```bash
# Unusual API calls
- create privileged pods
- modify RBAC rules
- access secrets outside namespace
```

**Supply Chain Attacks**:
```bash
# Behavioral anomalies
- Unexpected network connections
- Unknown processes
- Modified binaries
```

---

## 📈 Threat Intelligence Sources

### Stay Informed:
- [CISA Kubernetes Hardening Guide](https://www.cisa.gov/kubernetes)
- [MITRE ATT&CK for Containers](https://attack.mitre.org/matrices/enterprise/containers/)
- [NVD Container Vulnerabilities](https://nvd.nist.gov/)
- [Sysdig Threat Research](https://sysdig.com/blog/)
- [Aqua Security Threat Reports](https://www.aquasec.com/research/)

---

## 🚨 Incident Response Playbook

### If Compromise Suspected:

1. **Isolate**
   ```bash
   kubectl cordon <node>
   kubectl label pod <pod> quarantine=true
   ```

2. **Investigate**
   ```bash
   kubectl logs <pod> --previous
   kubectl describe pod <pod>
   kubectl get events --sort-by='.lastTimestamp'
   ```

3. **Collect Evidence**
   ```bash
   kubectl exec <pod> -- ps aux
   kubectl exec <pod> -- netstat -tulpn
   kubectl cp <pod>:/var/log/app.log ./evidence/
   ```

4. **Remediate**
   - Patch vulnerabilities
   - Rotate credentials
   - Update policies
   - Deploy fixes

5. **Learn**
   - Update threat model
   - Improve detection
   - Train team
   - Document lessons

---

## ⚡ Quick Wins

### Implement These First:
1. **Disable privileged containers** - Prevents most container escapes
2. **Enforce non-root users** - Limits privilege escalation
3. **Require resource limits** - Prevents resource exhaustion
4. **Use network policies** - Limits lateral movement
5. **Scan images** - Catches known vulnerabilities

### Measure Success:
- Reduction in security incidents
- Decrease in policy violations
- Faster incident response
- Improved compliance scores
- Developer satisfaction (yes, this matters)

---

**Remember**: Perfect security is impossible. The goal is to make attacks expensive, noisy, and unreliable. Make attackers work harder than defenders.

**Next Step**: Read `COMPLIANCE_MAPPINGS.md` to understand how these threats map to compliance requirements.