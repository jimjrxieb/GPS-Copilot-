package kubernetes.admission.security.network

# UNDERSTANDING: Network segmentation isn't about blocking everything.
# It's about creating deliberate, auditable communication paths.
# Zero-trust means verify everything, trust nothing.

import future.keywords.contains
import future.keywords.if
import future.keywords.in

metadata := {
    "policy": "network-segmentation-enforcement",
    "version": "1.0.0",
    "compliance": ["CIS-5.3.2", "SOC2-CC6.6", "NIST-SC-7", "PCI-DSS-1.2"],
    "principle": "zero-trust-networking",
    "last_review": "2024-09-24"
}

default allow = false

allow {
    count(violation) == 0
}

# HELPER FUNCTIONS (defined early for use in violations)

is_production {
    input.request.object.metadata.namespace in ["production", "prod", "live"]
}

# CRITICAL: Enforce network policies in sensitive namespaces
# THREAT: Lateral movement, data exfiltration
# COMPLIANCE: CIS 5.3.2, PCI-DSS 1.2.1
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.3.2"}] {
    is_sensitive_namespace(input.request.object.metadata.namespace)
    not has_network_policy(input.request.object.metadata.namespace)
    msg := sprintf("Namespace '%v' requires NetworkPolicy for zero-trust",
                   [input.request.object.metadata.namespace])
}

# HIGH: Block access to cloud metadata services
# THREAT: SSRF to metadata service = credential theft (Capital One breach pattern)
# COMPLIANCE: NIST SC-7, SOC2 CC6.6
violation[{"msg": msg, "severity": "CRITICAL", "control": "CLOUD-SECURITY"}] {
    container := input.request.object.spec.containers[_]
    env := container.env[_]
    contains(env.value, "169.254.169.254")
    msg := "Container references metadata service - potential credential theft vector"
}

violation[{"msg": msg, "severity": "CRITICAL", "control": "CLOUD-SECURITY"}] {
    container := input.request.object.spec.containers[_]
    env := container.env[_]
    contains(env.value, "metadata.google.internal")
    msg := "Container references GCP metadata service - credential theft risk"
}

# HIGH: Enforce egress restrictions
# THREAT: Data exfiltration, C2 communication
# COMPLIANCE: PCI-DSS 1.3.4, SOC2 CC6.6
violation[{"msg": msg, "severity": "HIGH", "control": "EGRESS-CONTROL"}] {
    is_production
    pod_needs_internet(input.request.object)
    not has_egress_policy(input.request.object)
    msg := "Internet-facing pod requires explicit egress policy"
}

# MEDIUM: Require network segmentation labels
# THREAT: Misconfigured network policies, policy bypass
# COMPLIANCE: NIST SC-7(5)
violation[{"msg": msg, "severity": "MEDIUM", "control": "SEGMENTATION"}] {
    not input.request.object.metadata.labels["network-zone"]
    is_production
    msg := "Pod missing 'network-zone' label for network segmentation"
}

violation[{"msg": msg, "severity": "MEDIUM", "control": "SEGMENTATION"}] {
    zone := input.request.object.metadata.labels["network-zone"]
    not zone in ["dmz", "internal", "restricted", "public"]
    msg := sprintf("Invalid network zone '%v' - use: dmz, internal, restricted, public", [zone])
}

# MEDIUM: Cross-zone communication restrictions
# THREAT: Lateral movement between security zones
# COMPLIANCE: PCI-DSS 1.3.1
violation[{"msg": msg, "severity": "HIGH", "control": "ZONE-ISOLATION"}] {
    from_zone := input.request.object.metadata.labels["network-zone"]
    to_zone := input.request.object.metadata.labels["communicates-with"]
    violates_zone_rules(from_zone, to_zone)
    msg := sprintf("Forbidden cross-zone communication: %v -> %v", [from_zone, to_zone])
}

violates_zone_rules(from, to) {
    # DMZ cannot reach internal
    from == "dmz"
    to == "restricted"
}

violates_zone_rules(from, to) {
    # Public cannot reach anything except DMZ
    from == "public"
    to in ["internal", "restricted"]
}

# MEDIUM: Service mesh security
# THREAT: Unencrypted service-to-service communication
# COMPLIANCE: SOC2 CC6.6, HIPAA 164.312(e)
violation[{"msg": msg, "severity": "MEDIUM", "control": "MESH-SECURITY"}] {
    has_service_mesh_annotation(input.request.object)
    not has_mtls_enabled(input.request.object)
    msg := "Service mesh pod requires mTLS for zero-trust communication"
}

# LOW: DNS policy enforcement
# THREAT: DNS hijacking, cache poisoning
# COMPLIANCE: NIST SC-20
violation[{"msg": msg, "severity": "LOW", "control": "DNS-SECURITY"}] {
    policy := input.request.object.spec.dnsPolicy
    policy == "Default"
    is_production
    msg := "Use 'ClusterFirst' DNS policy for internal resolution security"
}

# HELPER FUNCTIONS

sensitive_namespaces := ["production", "payment", "database", "secrets", "kube-system"]

is_sensitive_namespace(ns) {
    ns in sensitive_namespaces
}

is_sensitive_namespace(ns) {
    contains(ns, "prod")
}

is_sensitive_namespace(ns) {
    contains(ns, "pci")
}

# Check if namespace has NetworkPolicy
has_network_policy(namespace) {
    # This would typically query the K8s API
    # For now, check for annotation indicating policy exists
    input.request.object.metadata.annotations["network-policy-enforced"] == "true"
}

pod_needs_internet(pod) {
    container := pod.spec.containers[_]
    env := container.env[_]
    contains(lower(env.name), "api_endpoint")
}

pod_needs_internet(pod) {
    container := pod.spec.containers[_]
    env := container.env[_]
    contains(lower(env.value), "https://")
}

has_egress_policy(pod) {
    pod.metadata.annotations["egress-policy"] == "defined"
}

has_service_mesh_annotation(pod) {
    pod.metadata.annotations["sidecar.istio.io/inject"] == "true"
}

has_service_mesh_annotation(pod) {
    pod.metadata.annotations["linkerd.io/inject"] == "enabled"
}

has_mtls_enabled(pod) {
    pod.metadata.annotations["security.istio.io/tlsMode"] == "STRICT"
}

# AUDIT: Network flow tracking for compliance
audit[audit_entry] {
    audit_entry := {
        "type": "network_flow",
        "data": {
            "timestamp": time.now_ns(),
            "pod": input.request.object.metadata.name,
            "namespace": input.request.object.metadata.namespace,
            "network_zone": input.request.object.metadata.labels["network-zone"],
            "decision": allow
        }
    }
}

# RECOMMENDATIONS: Suggest network policies based on pod characteristics
recommendation[{"type": "network_policy", "suggestion": suggestion}] {
    is_database_pod(input.request.object)
    suggestion := {
        "policy_type": "ingress",
        "allow_from": ["app-tier"],
        "deny_all_else": true,
        "reason": "Database should only accept connections from application tier"
    }
}

recommendation[{"type": "network_policy", "suggestion": suggestion}] {
    is_frontend_pod(input.request.object)
    suggestion := {
        "policy_type": "egress",
        "allow_to": ["api-tier", "cdn"],
        "deny_all_else": true,
        "reason": "Frontend should only connect to API and CDN"
    }
}

is_database_pod(pod) {
    contains(lower(pod.metadata.name), "db")
}

is_database_pod(pod) {
    contains(lower(pod.metadata.name), "postgres")
}

is_database_pod(pod) {
    contains(lower(pod.metadata.name), "mysql")
}

is_database_pod(pod) {
    contains(lower(pod.metadata.name), "mongo")
}

is_frontend_pod(pod) {
    contains(lower(pod.metadata.name), "frontend")
}

is_frontend_pod(pod) {
    contains(lower(pod.metadata.name), "ui")
}

is_frontend_pod(pod) {
    pod.metadata.labels["tier"] == "frontend"
}

# TESTING: Verify network policy logic
test_production_requires_network_policy {
    violation[_] with input as {
        "request": {
            "object": {
                "metadata": {
                    "namespace": "production"
                }
            }
        }
    }
}

test_metadata_service_blocked {
    violation[_] with input as {
        "request": {
            "object": {
                "spec": {
                    "containers": [{
                        "env": [{
                            "name": "API_ENDPOINT",
                            "value": "http://169.254.169.254/latest/meta-data/"
                        }]
                    }]
                }
            }
        }
    }
}

test_network_zones_enforced {
    count(violation) == 0 with input as {
        "request": {
            "object": {
                "metadata": {
                    "namespace": "production",
                    "labels": {
                        "network-zone": "internal"
                    },
                    "annotations": {
                        "network-policy-enforced": "true"
                    }
                }
            }
        }
    }
}