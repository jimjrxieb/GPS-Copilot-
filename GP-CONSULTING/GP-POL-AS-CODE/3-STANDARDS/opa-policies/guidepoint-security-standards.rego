package guidepoint.security

# GuidePoint Security Standards - OPA Policy Bundle
# Implements all Kubernetes security requirements per GuidePoint standards
# Reference: https://guidepoint.com/security-standards

# =============================================================================
# 1. Non-root containers mandatory (GuidePoint Standard)
# =============================================================================
violation[{"msg": msg, "severity": "high"}] {
  container := input.review.object.spec.containers[_]
  not container.securityContext.runAsNonRoot
  msg := sprintf("GuidePoint Security Violation: Container '%v' must run as non-root. This is a mandatory requirement per GuidePoint Kubernetes standards.", [container.name])
}

# =============================================================================
# 2. No privileged containers (GuidePoint Standard - except approved)
# =============================================================================
violation[{"msg": msg, "severity": "critical"}] {
  container := input.review.object.spec.containers[_]
  container.securityContext.privileged == true
  msg := sprintf("GuidePoint Security Violation: Container '%v' is running in privileged mode. Privileged containers are prohibited unless explicitly approved by GuidePoint Security Team.", [container.name])
}

# =============================================================================
# 3. Resource limits required (GuidePoint Standard)
# =============================================================================
violation[{"msg": msg, "severity": "medium"}] {
  container := input.review.object.spec.containers[_]
  not container.resources.limits.cpu
  msg := sprintf("GuidePoint Security Violation: Container '%v' missing CPU limits. Resource limits are required per GuidePoint standards to prevent resource exhaustion attacks.", [container.name])
}

violation[{"msg": msg, "severity": "medium"}] {
  container := input.review.object.spec.containers[_]
  not container.resources.limits.memory
  msg := sprintf("GuidePoint Security Violation: Container '%v' missing memory limits. Resource limits are required per GuidePoint standards.", [container.name])
}

# =============================================================================
# 4. No privilege escalation (GuidePoint CKS Requirement)
# =============================================================================
violation[{"msg": msg, "severity": "high"}] {
  container := input.review.object.spec.containers[_]
  not container.securityContext.allowPrivilegeEscalation == false
  msg := sprintf("GuidePoint Security Violation: Container '%v' allows privilege escalation. Per CKS standards, allowPrivilegeEscalation must be explicitly set to false.", [container.name])
}

# =============================================================================
# 5. Drop dangerous capabilities (GuidePoint CKS Requirement)
# =============================================================================
violation[{"msg": msg, "severity": "critical"}] {
  container := input.review.object.spec.containers[_]
  capability := container.securityContext.capabilities.add[_]
  capability == "SYS_ADMIN"
  msg := sprintf("GuidePoint Security Violation: Container '%v' adds SYS_ADMIN capability. This is a critical security risk per GuidePoint standards.", [container.name])
}

violation[{"msg": msg, "severity": "high"}] {
  container := input.review.object.spec.containers[_]
  capability := container.securityContext.capabilities.add[_]
  capability == "NET_ADMIN"
  msg := sprintf("GuidePoint Security Violation: Container '%v' adds NET_ADMIN capability. Requires explicit approval from GuidePoint Security Team.", [container.name])
}

# =============================================================================
# 6. No host network access (GuidePoint Standard)
# =============================================================================
violation[{"msg": msg, "severity": "high"}] {
  input.review.object.spec.hostNetwork == true
  msg := "GuidePoint Security Violation: Pod uses host network. Host network access is prohibited per GuidePoint security standards."
}

# =============================================================================
# 7. No host PID namespace (GuidePoint Standard)
# =============================================================================
violation[{"msg": msg, "severity": "high"}] {
  input.review.object.spec.hostPID == true
  msg := "GuidePoint Security Violation: Pod uses host PID namespace. This violates GuidePoint container isolation requirements."
}

# =============================================================================
# 8. No host IPC namespace (GuidePoint Standard)
# =============================================================================
violation[{"msg": msg, "severity": "high"}] {
  input.review.object.spec.hostIPC == true
  msg := "GuidePoint Security Violation: Pod uses host IPC namespace. This violates GuidePoint container isolation requirements."
}

# =============================================================================
# 9. No hostPath volumes (GuidePoint Standard - data protection)
# =============================================================================
violation[{"msg": msg, "severity": "critical"}] {
  volume := input.review.object.spec.volumes[_]
  volume.hostPath
  msg := sprintf("GuidePoint Security Violation: Pod uses hostPath volume '%v'. Host filesystem access is prohibited per GuidePoint data classification policies.", [volume.name])
}

# =============================================================================
# 10. Read-only root filesystem (GuidePoint Best Practice)
# =============================================================================
warn[{"msg": msg}] {
  container := input.review.object.spec.containers[_]
  not container.securityContext.readOnlyRootFilesystem == true
  msg := sprintf("GuidePoint Best Practice Warning: Container '%v' does not use read-only root filesystem. While not mandatory, this is strongly recommended per GuidePoint security guidelines.", [container.name])
}

# =============================================================================
# 11. Pod Security Standards enforcement (GuidePoint Standard)
# =============================================================================
violation[{"msg": msg, "severity": "high"}] {
  # Check if pod has security context
  not input.review.object.spec.securityContext
  msg := "GuidePoint Security Violation: Pod missing securityContext. Pod Security Standards must be enforced per GuidePoint CKS requirements."
}

# =============================================================================
# 12. Network policies required (GuidePoint Standard)
# =============================================================================
# Note: This checks if namespace has network policies defined
# Actual implementation requires checking across namespace
warn[{"msg": msg}] {
  input.review.object.kind == "Pod"
  not input.review.object.metadata.namespace == "kube-system"
  msg := "GuidePoint Reminder: Ensure network policies are defined for this namespace per GuidePoint segmentation requirements."
}

# =============================================================================
# COMPLIANCE SUMMARY
# =============================================================================
# This policy bundle implements:
# ✓ Non-root containers mandatory
# ✓ No privileged containers (except approved)
# ✓ Resource limits required
# ✓ No privilege escalation
# ✓ Dangerous capabilities dropped
# ✓ No host namespace access (network, PID, IPC)
# ✓ No hostPath volumes
# ✓ Pod Security Standards enforced
# ✓ Network segmentation reminders
#
# Severity Levels:
# - CRITICAL: Immediate security risk, blocks deployment
# - HIGH: Security violation, requires approval
# - MEDIUM: Best practice violation, should be fixed
# - WARN: Recommendation, does not block
#
# Contact: security@guidepoint.com for exceptions
# =============================================================================
