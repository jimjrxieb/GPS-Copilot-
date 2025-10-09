# Compliance Framework to OPA Policy Mappings

**Purpose**: Connect security policies to compliance requirements. Because auditors don't care about your elegant code - they care about evidence of controls.

---

## 🎯 Quick Reference Matrix

| Compliance Framework | Control ID | OPA Policy | Risk Addressed |
|---------------------|------------|------------|----------------|
| CIS K8s 5.1.1 | RBAC Configuration | `rbac-policies.rego` | Unauthorized Access |
| CIS K8s 5.2.3 | Security Context | `pod-security.rego` | Privilege Escalation |
| CIS K8s 5.3.2 | Network Policies | `network-policies.rego` | Lateral Movement |
| CIS K8s 5.7.3 | Resource Limits | `resource-limits.rego` | Resource Exhaustion |
| SOC2 CC6.1 | Logical Access | `rbac-policies.rego` | Data Breach |
| SOC2 CC6.6 | Data Transmission | `network-policies.rego` | Data Interception |
| SOC2 CC7.1 | System Monitoring | `audit-policies.rego` | Undetected Breach |
| NIST AC-2 | Account Management | `rbac-policies.rego` | Insider Threat |
| NIST SC-7 | Boundary Protection | `network-policies.rego` | External Attack |
| PCI-DSS 2.2.2 | Configuration Standards | `pod-security.rego` | System Compromise |
| PCI-DSS 7.1 | Access Control | `rbac-policies.rego` | Cardholder Data Access |
| HIPAA 164.312(a) | Access Control | `rbac-policies.rego` | PHI Exposure |
| ISO27001 A.9.1 | Access Requirements | `rbac-policies.rego` | Information Disclosure |
| FedRAMP AC-3 | Access Enforcement | `rbac-policies.rego` | Government Data Breach |

---

## 📚 CIS Kubernetes Benchmark v1.7.0

### 5.1 RBAC and Service Accounts

#### 5.1.1 - Ensure RBAC is enabled
**Control**: Role-Based Access Control must be enabled
**Risk**: Without RBAC, any authenticated user has full cluster access
**OPA Policy**:
```rego
package cis.5_1_1

# Verify RBAC is not bypassed
violation[{"msg": msg, "severity": "CRITICAL"}] {
    input.request.object.kind == "ClusterRoleBinding"
    input.request.object.subjects[_].kind == "User"
    input.request.object.subjects[_].name == "system:anonymous"
    input.request.object.roleRef.name == "cluster-admin"
    msg := "CIS 5.1.1: Anonymous users cannot have cluster-admin"
}
```

#### 5.1.3 - Minimize wildcard RBAC
**Control**: Avoid wildcards in Roles and ClusterRoles
**Risk**: Overly permissive roles enable privilege escalation
**OPA Policy**:
```rego
package cis.5_1_3

violation[{"msg": msg, "severity": "HIGH"}] {
    input.request.object.rules[_].apiGroups[_] == "*"
    input.request.object.rules[_].resources[_] == "*"
    input.request.object.rules[_].verbs[_] == "*"
    msg := "CIS 5.1.3: Wildcard permissions violate least privilege"
}
```

### 5.2 Pod Security Standards

#### 5.2.3 - Minimize privilege escalation
**Control**: Set allowPrivilegeEscalation to false
**Risk**: Processes can gain more privileges than parent
**OPA Policy**:
```rego
package cis.5_2_3

violation[{"msg": msg, "severity": "HIGH"}] {
    container := input.request.object.spec.containers[_]
    container.securityContext.allowPrivilegeEscalation == true
    msg := sprintf("CIS 5.2.3: Container allows privilege escalation: %v", [container.name])
}
```

#### 5.2.5 - Do not run privileged containers
**Control**: Containers must not run in privileged mode
**Risk**: Privileged containers can escape to host
**OPA Policy**:
```rego
package cis.5_2_5

violation[{"msg": msg, "severity": "CRITICAL"}] {
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("CIS 5.2.5: Privileged container detected: %v", [container.name])
}
```

### 5.3 Network Policies and CNI

#### 5.3.2 - Apply Security Context to Pods
**Control**: Network segmentation via NetworkPolicies
**Risk**: Unrestricted pod-to-pod communication
**OPA Policy**:
```rego
package cis.5_3_2

# Require NetworkPolicy for production namespaces
violation[{"msg": msg, "severity": "MEDIUM"}] {
    input.request.object.metadata.namespace == "production"
    not has_network_policy(input.request.object.metadata.namespace)
    msg := "CIS 5.3.2: Production namespace requires NetworkPolicy"
}
```

---

## 🏢 SOC2 Type II Controls

### CC6.1 - Logical and Physical Access Controls
**Requirement**: Restrict logical access to information assets
**Evidence Required**:
- RBAC configuration exports
- Access review logs
- Least privilege validation

**OPA Implementation**:
```rego
package soc2.cc6_1

# Track evidence for SOC2 audit
evidence[{"control": "CC6.1", "data": data}] {
    data := {
        "timestamp": time.now_ns(),
        "user": input.request.userInfo.username,
        "action": input.request.operation,
        "resource": input.request.object.kind,
        "result": "allowed/denied"
    }
}

# Enforce least privilege
violation[{"msg": msg, "control": "CC6.1"}] {
    excessive_permissions(input.request.object)
    msg := "SOC2 CC6.1: Excessive permissions violate least privilege"
}
```

### CC6.6 - Data Transmission Security
**Requirement**: Encryption of data in transit
**OPA Implementation**:
```rego
package soc2.cc6_6

violation[{"msg": msg, "control": "CC6.6"}] {
    container := input.request.object.spec.containers[_]
    port := container.ports[_]
    port.protocol == "TCP"
    not is_tls_enabled(container, port)
    msg := sprintf("SOC2 CC6.6: Unencrypted port exposed: %v", [port.containerPort])
}
```

### CC7.1 - System Monitoring
**Requirement**: Monitor system performance and vulnerabilities
**OPA Implementation**:
```rego
package soc2.cc7_1

# Ensure logging is enabled
violation[{"msg": msg, "control": "CC7.1"}] {
    not input.request.object.spec.containers[_].env[_].name == "ENABLE_AUDIT_LOG"
    msg := "SOC2 CC7.1: Audit logging must be enabled"
}
```

---

## 🏛️ NIST Cybersecurity Framework

### AC-2 - Account Management
**Requirement**: Manage information system accounts
**Mapping**: CIS 5.1.1, 5.1.3, 5.1.5
**OPA Policy**:
```rego
package nist.ac_2

# Service account lifecycle management
violation[{"msg": msg, "control": "AC-2"}] {
    sa := input.request.object
    sa.kind == "ServiceAccount"
    not sa.metadata.labels["owner"]
    not sa.metadata.labels["expiry"]
    msg := "NIST AC-2: Service accounts must have owner and expiry labels"
}
```

### AC-3 - Access Enforcement
**Requirement**: Enforce approved authorizations
**OPA Policy**:
```rego
package nist.ac_3

# Enforce separation of duties
violation[{"msg": msg, "control": "AC-3"}] {
    binding := input.request.object
    binding.kind == "RoleBinding"
    count(binding.subjects) > 1
    has_admin_role(binding.roleRef)
    msg := "NIST AC-3: Admin roles cannot have multiple subjects (separation of duties)"
}
```

### SC-7 - Boundary Protection
**Requirement**: Monitor and control communications at external boundaries
**OPA Policy**:
```rego
package nist.sc_7

violation[{"msg": msg, "control": "SC-7"}] {
    service := input.request.object
    service.kind == "Service"
    service.spec.type == "LoadBalancer"
    not has_ingress_controls(service)
    msg := "NIST SC-7: External services require ingress controls"
}
```

---

## 💳 PCI-DSS v4.0

### Requirement 2: Default Passwords and Security Parameters

#### 2.2.2 - Configuration standards for all system components
**OPA Policy**:
```rego
package pci_dss.2_2_2

violation[{"msg": msg, "requirement": "2.2.2"}] {
    container := input.request.object.spec.containers[_]
    has_default_password(container)
    msg := sprintf("PCI-DSS 2.2.2: Default password detected in %v", [container.name])
}
```

### Requirement 7: Restrict Access by Business Need

#### 7.1 - Limit access to system components
**OPA Policy**:
```rego
package pci_dss.7_1

violation[{"msg": msg, "requirement": "7.1"}] {
    namespace := input.request.object.metadata.namespace
    is_cardholder_environment(namespace)
    not has_access_restrictions(input.request.object)
    msg := "PCI-DSS 7.1: Cardholder data environment requires access restrictions"
}
```

### Requirement 8: Identify and Authenticate Access

#### 8.2.1 - Strong cryptography for authentication
**OPA Policy**:
```rego
package pci_dss.8_2_1

violation[{"msg": msg, "requirement": "8.2.1"}] {
    not uses_strong_auth(input.request.userInfo)
    msg := "PCI-DSS 8.2.1: Strong authentication required"
}
```

---

## 🏥 HIPAA Security Rule

### 164.312(a)(1) - Access Control
**Technical Safeguard**: Unique user identification
**OPA Policy**:
```rego
package hipaa.164_312_a_1

violation[{"msg": msg, "section": "164.312(a)(1)"}] {
    pod := input.request.object
    contains_phi(pod)
    not has_unique_identity(pod)
    msg := "HIPAA 164.312(a)(1): PHI access requires unique user identification"
}
```

### 164.312(e)(1) - Transmission Security
**Technical Safeguard**: Integrity controls
**OPA Policy**:
```rego
package hipaa.164_312_e_1

violation[{"msg": msg, "section": "164.312(e)(1)"}] {
    not uses_encryption(input.request.object)
    handles_phi(input.request.object)
    msg := "HIPAA 164.312(e)(1): PHI transmission requires encryption"
}
```

---

## 🌐 ISO 27001:2013

### A.9 - Access Control

#### A.9.1.2 - Access to networks and services
**OPA Policy**:
```rego
package iso27001.a_9_1_2

violation[{"msg": msg, "control": "A.9.1.2"}] {
    not has_network_policy(input.request.object.metadata.namespace)
    msg := "ISO27001 A.9.1.2: Network access must be controlled"
}
```

#### A.9.2.3 - Management of privileged access
**OPA Policy**:
```rego
package iso27001.a_9_2_3

violation[{"msg": msg, "control": "A.9.2.3"}] {
    has_privileged_access(input.request.object)
    not has_time_restriction(input.request.object)
    msg := "ISO27001 A.9.2.3: Privileged access requires time restrictions"
}
```

---

## 🏛️ FedRAMP Controls

### AC-3 - Access Enforcement
**Control Enhancement**: AC-3(4) - Mandatory Access Control
**OPA Policy**:
```rego
package fedramp.ac_3_4

violation[{"msg": msg, "control": "AC-3(4)"}] {
    is_federal_data(input.request.object)
    not has_mandatory_labels(input.request.object)
    msg := "FedRAMP AC-3(4): Federal data requires mandatory access labels"
}
```

---

## 📊 Compliance Automation Script

```python
#!/usr/bin/env python3
"""
Generate compliance evidence from OPA policy evaluations
"""

import json
import subprocess
from datetime import datetime

def generate_compliance_report(framework, policies):
    """
    Map OPA violations to compliance findings
    """
    report = {
        "framework": framework,
        "timestamp": datetime.now().isoformat(),
        "controls": {}
    }

    for control, policy_file in policies.items():
        # Run OPA evaluation
        result = subprocess.run(
            ["opa", "eval", "-d", policy_file, "-i", "input.json", "data.violations"],
            capture_output=True,
            text=True
        )

        violations = json.loads(result.stdout)
        report["controls"][control] = {
            "status": "PASS" if not violations else "FAIL",
            "findings": violations,
            "evidence": f"opa_eval_{control}_{datetime.now().strftime('%Y%m%d')}.json"
        }

    return report

# Usage
cis_policies = {
    "5.1.1": "policies/opa/cis/5_1_1.rego",
    "5.2.3": "policies/opa/cis/5_2_3.rego",
    "5.2.5": "policies/opa/cis/5_2_5.rego"
}

report = generate_compliance_report("CIS Kubernetes Benchmark", cis_policies)
print(json.dumps(report, indent=2))
```

---

## ✅ Compliance Checklist

### For SOC2 Audit:
- [ ] RBAC configuration documentation
- [ ] Network policy coverage > 80%
- [ ] No privileged containers in production
- [ ] Audit logging enabled
- [ ] Quarterly access reviews documented

### For PCI-DSS:
- [ ] Cardholder data environment segmented
- [ ] No default passwords
- [ ] Strong authentication enforced
- [ ] Encryption in transit verified
- [ ] Vulnerability scanning evidence

### For HIPAA:
- [ ] PHI access logging
- [ ] Encryption at rest and transit
- [ ] Unique user identification
- [ ] Automatic logoff configured
- [ ] Audit controls operational

### For FedRAMP:
- [ ] Continuous monitoring active
- [ ] Mandatory access controls
- [ ] FIPS 140-2 encryption
- [ ] Incident response procedures
- [ ] POA&M maintained

---

## 🎯 Key Takeaway

**Compliance is not security, but security enables compliance.**

Your OPA policies should:
1. **Prevent** the vulnerability (security)
2. **Document** the control (compliance)
3. **Evidence** the enforcement (audit)

Remember: Auditors want evidence, not explanations. Every policy should generate an audit trail.

**Next Step**: Implement policies in `opa/admission-control/` with these compliance mappings in mind.