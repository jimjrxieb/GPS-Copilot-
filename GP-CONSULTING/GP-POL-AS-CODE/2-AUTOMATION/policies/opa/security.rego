package security

# Pod Security Violations
violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.privileged == true
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' runs in privileged mode", [container.name])
}

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.allowPrivilegeEscalation == true
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' allows privilege escalation", [container.name])
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "Pod"
    not input.spec.securityContext.runAsNonRoot
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Pod missing runAsNonRoot security context"
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' does not use read-only root filesystem", [container.name])
}

# Deployment Security Violations
violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    container.securityContext.privileged == true
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' runs in privileged mode", [container.name])
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "Deployment"
    not input.spec.template.spec.securityContext.runAsNonRoot
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Deployment missing runAsNonRoot security context"
}

# Service Security Violations
violations[{"msg": msg, "severity": "low", "resource": resource}] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Service uses LoadBalancer type - ensure proper ingress controls"
}
