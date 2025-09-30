package kubernetes.admission.security.images

# UNDERSTANDING: Container images are the attack surface entry point
# Untrusted registries = supply chain attacks (SolarWinds pattern)
# Unsigned images = tampering, backdoors
# Outdated images = known CVEs

import future.keywords.contains
import future.keywords.if
import future.keywords.in

metadata := {
    "policy": "container-image-security",
    "version": "1.0.0",
    "compliance": ["CIS-5.1.1", "NIST-SA-10", "SLSA-Level-3"],
    "supply_chain": "software-supply-chain-security",
    "last_review": "2024-09-24"
}

default allow = false

allow {
    count(violation) == 0
}

# CRITICAL: Trusted registry enforcement
# THREAT: Supply chain attacks, malicious images
# COMPLIANCE: CIS 5.1.1, SLSA Level 3
violation[{"msg": msg, "severity": "CRITICAL", "control": "CIS-5.1.1"}] {
    container := input.request.object.spec.containers[_]
    not is_trusted_registry(container.image)
    msg := sprintf("Container '%v' uses untrusted registry: %v - use approved registries only",
                   [container.name, container.image])
}

trusted_registries := [
    "gcr.io/company",
    "company.azurecr.io",
    "123456789.dkr.ecr.us-east-1.amazonaws.com",
    "registry.company.com",
    "quay.io/company"
]

is_trusted_registry(image) {
    startswith(image, trusted_registries[_])
}

# CRITICAL: Latest tag prohibition
# THREAT: Unpredictable deployments, rollback issues
# COMPLIANCE: CIS 5.1.2, NIST CM-2
violation[{"msg": msg, "severity": "HIGH", "control": "CIS-5.1.2"}] {
    container := input.request.object.spec.containers[_]
    image_uses_latest_tag(container.image)
    msg := sprintf("Container '%v' uses ':latest' tag - use immutable tags (SHA256 digest preferred)",
                   [container.name])
}

image_uses_latest_tag(image) {
    endswith(image, ":latest")
}

image_uses_latest_tag(image) {
    not contains(image, ":")
}

# HIGH: Image signature verification
# THREAT: Tampered images, man-in-the-middle attacks
# COMPLIANCE: SLSA Level 3, NIST SA-10
violation[{"msg": msg, "severity": "HIGH", "control": "SLSA-3"}] {
    is_production
    container := input.request.object.spec.containers[_]
    not has_image_signature(container.image)
    msg := sprintf("Production container '%v' requires signed image with Cosign/Notary",
                   [container.name])
}

has_image_signature(image) {
    # Check if image has signature annotation
    input.request.object.metadata.annotations["images.guidepoint.io/signature-verified"] == "true"
}

has_image_signature(image) {
    # Check if image has digest (implies verification)
    contains(image, "@sha256:")
}

# HIGH: Base image restrictions
# THREAT: Vulnerable base images, unnecessary attack surface
# COMPLIANCE: CIS 4.1, NIST SI-2
violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-4.1"}] {
    container := input.request.object.spec.containers[_]
    uses_prohibited_base_image(container.image)
    msg := sprintf("Container '%v' uses prohibited base image - use approved distroless/minimal images",
                   [container.name])
}

prohibited_base_patterns := [
    "ubuntu:latest",
    "debian:latest",
    "centos:latest",
    "alpine:latest",
    ".*:latest"
]

uses_prohibited_base_image(image) {
    regex.match(prohibited_base_patterns[_], image)
}

# MEDIUM: Image pull policy enforcement
# THREAT: Stale local images, missing security updates
# COMPLIANCE: CIS 5.1.3
violation[{"msg": msg, "severity": "MEDIUM", "control": "CIS-5.1.3"}] {
    container := input.request.object.spec.containers[_]
    not container.imagePullPolicy == "Always"
    not container.imagePullPolicy == "IfNotPresent"  # Allow if using digest
    msg := sprintf("Container '%v' must set imagePullPolicy to 'Always' or use immutable digest",
                   [container.name])
}

# MEDIUM: Image scanning requirements
# THREAT: Known CVEs, vulnerable dependencies
# COMPLIANCE: NIST RA-5, PCI-DSS 6.2
violation[{"msg": msg, "severity": "HIGH", "control": "CVE-SCAN"}] {
    is_production
    not has_scan_annotation
    msg := "Production pods require image vulnerability scan attestation"
}

has_scan_annotation {
    input.request.object.metadata.annotations["images.guidepoint.io/scan-date"]
    input.request.object.metadata.annotations["images.guidepoint.io/scan-status"] == "passed"
}

# LOW: Distroless/minimal image recommendation
# THREAT: Unnecessary tools enable privilege escalation
# COMPLIANCE: CIS 4.2, NIST CM-7
violation[{"msg": msg, "severity": "LOW", "control": "MINIMAL-IMAGE"}] {
    container := input.request.object.spec.containers[_]
    not is_minimal_image(container.image)
    not is_exempted(container.name)
    msg := sprintf("Container '%v' should use distroless/minimal base image for reduced attack surface",
                   [container.name])
}

is_minimal_image(image) {
    contains(image, "distroless")
}

is_minimal_image(image) {
    contains(image, "scratch")
}

is_minimal_image(image) {
    regex.match(`.*alpine:\d+\.\d+`, image)  # Versioned alpine
}

is_production {
    input.request.object.metadata.namespace in ["production", "prod", "live"]
}

is_exempted(name) {
    input.request.object.metadata.annotations["security.guidepoint.io/image-exemption"] == "true"
}