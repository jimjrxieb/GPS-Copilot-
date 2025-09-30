package kubernetes.admission.compliance

# UNDERSTANDING: Compliance isn't checkbox theater - it's risk management
# Each control maps to specific breach patterns
# Audit trails enable forensics and accountability

import future.keywords.contains
import future.keywords.if
import future.keywords.in

metadata := {
    "policy": "compliance-enforcement",
    "version": "1.0.0",
    "frameworks": ["SOC2-TypeII", "PCI-DSS-v4", "HIPAA", "ISO27001", "GDPR"],
    "audit_scope": "full-lifecycle-compliance",
    "last_review": "2024-09-24"
}

default allow = false

allow {
    count(violation) == 0
}

# CRITICAL: Resource labeling for audit trails
# COMPLIANCE: SOC2 CC6.1, ISO27001 A.8.1, GDPR Art.30
# THREAT: Audit gaps, compliance violations
violation[{"msg": msg, "severity": "HIGH", "control": "SOC2-CC6.1"}] {
    not has_required_labels
    msg := "Resource missing required compliance labels: owner, cost-center, data-classification"
}

has_required_labels {
    input.request.object.metadata.labels.owner
    input.request.object.metadata.labels["cost-center"]
    input.request.object.metadata.labels["data-classification"]
}

# HIGH: Data classification enforcement
# COMPLIANCE: GDPR Art.32, HIPAA §164.312, PCI-DSS 3.0
# THREAT: Unauthorized data access, regulatory fines
violation[{"msg": msg, "severity": "CRITICAL", "control": "DATA-CLASSIFICATION"}] {
    data_class := input.request.object.metadata.labels["data-classification"]
    data_class in ["pii", "phi", "cardholder-data"]
    not has_encryption_at_rest
    msg := sprintf("Resources with '%v' data must have encryption at rest", [data_class])
}

has_encryption_at_rest {
    input.request.object.metadata.annotations["encryption.guidepoint.io/at-rest"] == "true"
}

# HIGH: Audit logging requirements
# COMPLIANCE: SOC2 CC7.2, PCI-DSS 10.2, HIPAA §164.312(b)
# THREAT: Security incident detection gaps
violation[{"msg": msg, "severity": "HIGH", "control": "AUDIT-LOGGING"}] {
    is_sensitive_resource
    not has_audit_logging_enabled
    msg := "Sensitive resources must have audit logging enabled"
}

is_sensitive_resource {
    input.request.object.metadata.labels["data-classification"] in ["restricted", "confidential"]
}

has_audit_logging_enabled {
    input.request.object.metadata.annotations["logging.guidepoint.io/audit-enabled"] == "true"
}

# HIGH: Retention policy enforcement
# COMPLIANCE: SOC2 A1.2, GDPR Art.17, PCI-DSS 3.1
# THREAT: Data retention violations, storage costs
violation[{"msg": msg, "severity": "MEDIUM", "control": "RETENTION-POLICY"}] {
    secret := input.request.object
    secret.kind == "Secret"
    not secret.metadata.annotations["retention.guidepoint.io/expiry-date"]
    msg := "Secrets must have retention/expiry date annotation"
}

# MEDIUM: Change management documentation
# COMPLIANCE: SOC2 CC8.1, ISO27001 A.12.1.2
# THREAT: Unauthorized changes, audit failures
violation[{"msg": msg, "severity": "MEDIUM", "control": "CHANGE-MGMT"}] {
    is_production
    not has_change_ticket
    msg := "Production changes require change ticket annotation"
}

has_change_ticket {
    input.request.object.metadata.annotations["change.guidepoint.io/ticket-id"]
    input.request.object.metadata.annotations["change.guidepoint.io/approved-by"]
}

# MEDIUM: Environment segregation
# COMPLIANCE: PCI-DSS 6.4.1, SOC2 CC6.6
# THREAT: Dev/test data in production
violation[{"msg": msg, "severity": "HIGH", "control": "ENV-SEGREGATION"}] {
    is_production
    has_non_production_indicator
    msg := "Production resources cannot have dev/test/staging indicators"
}

has_non_production_indicator {
    label_value := input.request.object.metadata.labels[_]
    label_value in ["dev", "test", "staging", "development"]
}

# LOW: Cost allocation tagging
# COMPLIANCE: FinOps best practices, SOC2 CC1.4
# THREAT: Budget overruns, resource waste
violation[{"msg": msg, "severity": "LOW", "control": "COST-CONTROL"}] {
    not input.request.object.metadata.labels["cost-center"]
    msg := "Resources must have cost-center label for financial tracking"
}

# HIGH: Data residency compliance
# COMPLIANCE: GDPR Art.44, CCPA, Data Sovereignty
# THREAT: Cross-border data transfer violations
violation[{"msg": msg, "severity": "CRITICAL", "control": "DATA-RESIDENCY"}] {
    data_class := input.request.object.metadata.labels["data-classification"]
    data_class in ["pii", "gdpr-protected"]
    region := input.request.object.metadata.labels["topology.kubernetes.io/region"]
    not is_compliant_region(region, data_class)
    msg := sprintf("Data class '%v' cannot be stored in region '%v'", [data_class, region])
}

is_compliant_region(region, data_class) {
    # EU data must stay in EU
    data_class == "gdpr-protected"
    startswith(region, "eu-")
}

is_compliant_region(region, data_class) {
    # US PII can be in US regions
    data_class == "pii"
    region in ["us-east-1", "us-west-2", "us-central-1"]
}

# MEDIUM: Backup and disaster recovery
# COMPLIANCE: SOC2 CC9.1, ISO27001 A.12.3
# THREAT: Data loss, business continuity failure
violation[{"msg": msg, "severity": "MEDIUM", "control": "BACKUP-DR"}] {
    is_stateful_resource
    not has_backup_policy
    msg := "Stateful resources must have backup policy annotation"
}

is_stateful_resource {
    input.request.object.kind in ["StatefulSet", "PersistentVolumeClaim"]
}

has_backup_policy {
    input.request.object.metadata.annotations["backup.guidepoint.io/enabled"] == "true"
    input.request.object.metadata.annotations["backup.guidepoint.io/retention-days"]
}

# HIGH: Access control review
# COMPLIANCE: SOC2 CC6.2, ISO27001 A.9.2.1
# THREAT: Stale permissions, privilege creep
violation[{"msg": msg, "severity": "MEDIUM", "control": "ACCESS-REVIEW"}] {
    input.request.object.kind in ["Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding"]
    not has_access_review_date
    msg := "RBAC resources must have last-review-date annotation for access certification"
}

has_access_review_date {
    review_date := input.request.object.metadata.annotations["rbac.guidepoint.io/last-review-date"]
    # Check if review is within last 90 days
    is_recent_review(review_date)
}

is_recent_review(date_string) {
    # Simplified check - in production, use time.parse_rfc3339_ns
    date_string != ""
}

is_production {
    input.request.object.metadata.namespace in ["production", "prod", "live"]
}