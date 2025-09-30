package kubernetes.admission.security.pods

# UNDERSTANDING: This isn't just a policy file - it's codified security engineering.
# Each rule prevents specific attack vectors identified in our threat model.
# Each violation maps to compliance requirements (CIS, SOC2, NIST).

import future.keywords.contains
import future.keywords.if
import future.keywords.in

# Policy metadata for observability and compliance
metadata := {
    "policy": "pod-security-standards",
    "version": "1.0.0",
    "compliance": ["CIS-5.2", "SOC2-CC6.1", "NIST-AC-3", "PCI-DSS-2.2.2"],
    "risk_level": "CRITICAL",
    "author": "GuidePoint Security Engineering",
    "last_review": "2024-09-24"
}

# DEFAULT: Fail-closed - deny by default unless explicitly allowed
default allow = false

# ALLOW: Requests that pass all security checks
allow {
    count(violation) == 0
}

# CRITICAL: Prevent container escape via privileged mode
# THREAT: CVE-2019-5736 and similar container escape vulnerabilities
# COMPLIANCE: CIS 5.2.5, SOC2 CC6.1
violation[{"msg": msg, "severity": "CRITICAL", "control": "CIS-5.2.5"}] {
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("Container '%v' running as privileged - enables container escape to host", [container.name])
}

# CRITICAL: Enforce non-root containers
# THREAT: Privilege escalation, kernel exploitation
# COMPLIANCE: CIS 5.2.6, NIST AC-2
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.2.6"}] {
    container := input.request.object.spec.containers[_]
    has_root_user(container)
    msg := sprintf("Container '%v' runs as root (UID 0) - use non-root user", [container.name])
}

has_root_user(container) {
    container.securityContext.runAsUser == 0
}

has_root_user(container) {
    not container.securityContext.runAsUser
    not input.request.object.spec.securityContext.runAsUser
}

# HIGH: Prevent privilege escalation
# THREAT: Process can gain more privileges than parent
# COMPLIANCE: CIS 5.2.3, SOC2 CC6.1
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.2.3"}] {
    container := input.request.object.spec.containers[_]
    container.securityContext.allowPrivilegeEscalation == true
    msg := sprintf("Container '%v' allows privilege escalation - set to false", [container.name])
}

# HIGH: Drop dangerous capabilities
# THREAT: Kernel manipulation, network stack access
# COMPLIANCE: CIS 5.2.7, 5.2.8, 5.2.9
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.2.7"}] {
    container := input.request.object.spec.containers[_]
    has_dangerous_capability(container)
    msg := sprintf("Container '%v' has dangerous capabilities - drop ALL or specific caps", [container.name])
}

dangerous_capabilities := ["NET_ADMIN", "SYS_ADMIN", "SYS_MODULE", "SYS_TIME", "KERNEL_MODULE", "SYS_BOOT"]

has_dangerous_capability(container) {
    capability := container.securityContext.capabilities.add[_]
    capability in dangerous_capabilities
}

# HIGH: Require read-only root filesystem
# THREAT: Malware persistence, binary replacement
# COMPLIANCE: CIS 5.2.11, PCI-DSS 2.2.2
violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.2.11"}] {
    container := input.request.object.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem == true
    not is_exempted(container.name)
    msg := sprintf("Container '%v' has writable root filesystem - set readOnlyRootFilesystem: true", [container.name])
}

# MEDIUM: Enforce resource limits
# THREAT: Resource exhaustion, DoS attacks
# COMPLIANCE: CIS 5.7.3, SOC2 CC7.1
violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.7.3"}] {
    container := input.request.object.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Container '%v' missing memory limits - prevents resource exhaustion", [container.name])
}

violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.7.3"}] {
    container := input.request.object.spec.containers[_]
    not container.resources.limits.cpu
    msg := sprintf("Container '%v' missing CPU limits - prevents resource exhaustion", [container.name])
}

# MEDIUM: Prevent host namespace sharing
# THREAT: Container-to-host escalation, process manipulation
# COMPLIANCE: CIS 5.2.2, 5.2.3, 5.2.4
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.2.2"}] {
    input.request.object.spec.hostNetwork == true
    msg := "Pod uses host network - enables network sniffing and spoofing"
}

violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.2.3"}] {
    input.request.object.spec.hostPID == true
    msg := "Pod uses host PID namespace - enables process manipulation"
}

violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.2.4"}] {
    input.request.object.spec.hostIPC == true
    msg := "Pod uses host IPC namespace - enables shared memory access"
}

# MEDIUM: Control volume mounts
# THREAT: Host filesystem access, data exfiltration
# COMPLIANCE: CIS 5.2.12, HIPAA 164.312(a)
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.2.12"}] {
    volume := input.request.object.spec.volumes[_]
    volume.hostPath
    not is_allowed_hostpath(volume.hostPath.path)
    msg := sprintf("Pod mounts restricted host path: %v", [volume.hostPath.path])
}

allowed_hostpaths := ["/var/log", "/tmp"]

is_allowed_hostpath(path) {
    startswith(path, allowed_hostpaths[_])
}

# MEDIUM: Enforce security profiles
# THREAT: Syscall abuse, kernel exploitation
# COMPLIANCE: CIS 5.2.13, FedRAMP AC-3
violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.2.13"}] {
    not input.request.object.spec.securityContext.seccompProfile
    msg := "Pod missing seccomp profile - add runtime/default or custom profile"
}

violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.2.13"}] {
    profile := input.request.object.spec.securityContext.seccompProfile.type
    profile == "Unconfined"
    msg := "Pod uses unconfined seccomp - highly insecure"
}

# HELPER FUNCTIONS

is_production {
    input.request.object.metadata.namespace in ["production", "prod", "live"]
}

# LOW: Best practices and hygiene
# THREAT: Information disclosure, debugging abuse
# COMPLIANCE: SOC2 CC7.1
violation[{"msg": msg, "severity": "LOW", "control": "BEST-PRACTICE"}] {
    container := input.request.object.spec.containers[_]
    container.env[_].name == "DEBUG"
    container.env[_].value == "true"
    is_production
    msg := sprintf("Container '%v' has DEBUG enabled in production", [container.name])
}

is_exempted(container_name) {
    # Some containers legitimately need writable filesystems
    # Document WHY each exemption exists
    exempted := {
        "fluentd": "needs to write logs",
        "prometheus": "needs to write metrics",
        "elasticsearch": "needs to write indices"
    }
    container_name in exempted
}

# AUDIT: Generate evidence for compliance
audit[audit_entry] {
    audit_entry := {
        "timestamp": time.now_ns(),
        "evidence": {
            "request_user": input.request.userInfo.username,
            "namespace": input.request.object.metadata.namespace,
            "pod": input.request.object.metadata.name,
            "violations": count(violation),
            "decision": allow,
            "metadata": metadata
        }
    }
}

# METRICS: Observability hooks for monitoring
metrics[{"metric": metric_name, "value": value}] {
    metric_name := "pod_security_violations_total"
    value := count(violation)
}

metrics[{"metric": metric_name, "labels": labels}] {
    metric_name := "pod_security_evaluation_duration_seconds"
    labels := {"namespace": input.request.object.metadata.namespace}
}

# TESTING: Example test cases
test_privileged_container_denied {
    violation[_] with input as {
        "request": {
            "object": {
                "spec": {
                    "containers": [{
                        "name": "test",
                        "securityContext": {"privileged": true}
                    }]
                }
            }
        }
    }
}

test_non_root_container_allowed {
    count(violation) == 0 with input as {
        "request": {
            "object": {
                "spec": {
                    "securityContext": {"runAsUser": 1000},
                    "containers": [{
                        "name": "test",
                        "securityContext": {
                            "runAsUser": 1000,
                            "readOnlyRootFilesystem": true,
                            "allowPrivilegeEscalation": false
                        },
                        "resources": {
                            "limits": {
                                "cpu": "100m",
                                "memory": "128Mi"
                            }
                        }
                    }]
                }
            }
        }
    }
}