package kubernetes.admission.security.secrets

# UNDERSTANDING: Secrets in environment variables = plaintext in process listings
# Volume-mounted secrets = files in memory, less exposure surface
# External secrets managers = best practice, but enforce fallback security

import future.keywords.contains
import future.keywords.if
import future.keywords.in

metadata := {
    "policy": "secrets-management-enforcement",
    "version": "1.0.0",
    "compliance": ["CIS-5.4.1", "SOC2-CC6.1", "NIST-SC-28", "PCI-DSS-3.4"],
    "principle": "defense-in-depth-secrets",
    "last_review": "2024-09-24"
}

default allow = false

allow {
    count(violation) == 0
}

# CRITICAL: Secrets in environment variables
# THREAT: Process listing exposure, log leakage, crash dumps
# COMPLIANCE: CIS 5.4.1, PCI-DSS 3.4
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.4.1"}] {
    container := input.request.object.spec.containers[_]
    env := container.env[_]
    env.valueFrom.secretKeyRef
    msg := sprintf("Container '%v' uses secret '%v' as environment variable - use volume mount",
                   [container.name, env.valueFrom.secretKeyRef.name])
}

# HIGH: Hardcoded secrets detection
# THREAT: Credential exposure in version control, image layers
# COMPLIANCE: SOC2 CC6.1, NIST IA-5
violation[{"msg": msg, "severity": "CRITICAL", "control": "SECRET-HARDCODED"}] {
    container := input.request.object.spec.containers[_]
    env := container.env[_]
    env.value
    is_hardcoded_secret(env.name, env.value)
    msg := sprintf("Container '%v' has hardcoded secret in env '%v'", [container.name, env.name])
}

is_hardcoded_secret(name, value) {
    lower(name) in ["password", "api_key", "secret", "token", "access_key"]
    not value == ""
}

is_hardcoded_secret(name, value) {
    # Pattern matching for common secret formats
    regex.match(`^[A-Za-z0-9+/]{40,}={0,2}$`, value)  # Base64-like
}

is_hardcoded_secret(name, value) {
    regex.match(`^[A-Z0-9]{20,}$`, value)  # AWS access key pattern
}

# HIGH: Secret volume permissions
# THREAT: World-readable secrets, privilege escalation
# COMPLIANCE: CIS 5.4.2
violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.4.2"}] {
    volume := input.request.object.spec.volumes[_]
    volume.secret
    not volume.secret.defaultMode == 256  # 0400 octal
    msg := sprintf("Secret volume '%v' must have mode 0400 (read-only owner)", [volume.name])
}

# MEDIUM: Enforce external secrets operator
# THREAT: Secrets stored in etcd, backup exposure
# COMPLIANCE: SOC2 CC6.1
violation[{"msg": msg, "severity": "LOW", "control": "EXTERNAL-SECRETS"}] {
    is_production
    volume := input.request.object.spec.volumes[_]
    volume.secret
    not has_external_secrets_annotation
    msg := "Production pods should use external secrets manager (AWS Secrets Manager, Vault)"
}

has_external_secrets_annotation {
    input.request.object.metadata.annotations["external-secrets.io/backend"]
}

is_production {
    input.request.object.metadata.namespace in ["production", "prod"]
}

# HIGH: Service account token auto-mount
# THREAT: Unnecessary API access, token theft
# COMPLIANCE: CIS 5.1.5
violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.1.5"}] {
    not input.request.object.spec.automountServiceAccountToken == false
    not needs_api_access
    msg := "Pod should set automountServiceAccountToken: false unless API access required"
}

needs_api_access {
    # Allow if explicitly annotated
    input.request.object.metadata.annotations["security.guidepoint.io/needs-api-access"] == "true"
}

# MEDIUM: Secret rotation metadata
# THREAT: Stale credentials, extended exposure window
# COMPLIANCE: NIST IA-5(1), PCI-DSS 8.2.4
violation[{"msg": msg, "severity": "LOW", "control": "SECRET-ROTATION"}] {
    secret := input.request.object
    secret.kind == "Secret"
    secret.type in ["Opaque", "kubernetes.io/basic-auth", "kubernetes.io/tls"]
    not secret.metadata.annotations["secret.guidepoint.io/rotation-date"]
    msg := sprintf("Secret '%v' missing rotation date annotation", [secret.metadata.name])
}