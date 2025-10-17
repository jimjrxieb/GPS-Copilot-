package network

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "NetworkPolicy"
    count(input.spec.ingress) == 0
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "NetworkPolicy has no ingress rules defined"
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "NetworkPolicy"
    ingress := input.spec.ingress[_]
    from := ingress.from[_]
    from.ipBlock.cidr == "0.0.0.0/0"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "NetworkPolicy allows ingress from all IPs (0.0.0.0/0)"
}
