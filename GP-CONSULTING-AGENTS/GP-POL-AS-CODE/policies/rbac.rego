package rbac

violations[{"msg": msg, "severity": "critical", "resource": resource}] {
    input.kind == "ClusterRoleBinding"
    input.subjects[_].name == "system:anonymous"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "ClusterRoleBinding grants permissions to anonymous users"
}

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Role"
    rule := input.rules[_]
    rule.verbs[_] == "*"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Role grants wildcard (*) verb permissions"
}

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "ClusterRole"
    rule := input.rules[_]
    rule.resources[_] == "*"
    rule.verbs[_] == "*"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "ClusterRole grants wildcard permissions on all resources"
}
