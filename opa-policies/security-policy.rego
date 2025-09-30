package gp.security

# GP-JADE Security Policy
# OPA policies for security validation

# Default deny
default allow = false

# Allow if no security violations found
allow {
    count(violations) == 0
}

# Check for hardcoded secrets
violations[msg] {
    input.code
    contains(lower(input.code), "password")
    contains(lower(input.code), "=")
    not contains(lower(input.code), "var.")
    not contains(lower(input.code), "secret.")
    msg := "Potential hardcoded password detected"
}

violations[msg] {
    input.code
    regex.match(`[A-Za-z0-9+/]{40,}`, input.code)
    msg := "Potential hardcoded secret or token detected"
}

# Check for overly permissive access
violations[msg] {
    input.code
    contains(input.code, "0.0.0.0/0")
    msg := "Overly permissive network access (0.0.0.0/0) detected"
}

violations[msg] {
    input.terraform_resource
    input.terraform_resource.type == "aws_security_group_rule"
    input.terraform_resource.cidr_blocks[_] == "0.0.0.0/0"
    msg := sprintf("Security group '%s' allows unrestricted access", [input.terraform_resource.name])
}

# Check for public S3 buckets
violations[msg] {
    input.terraform_resource
    input.terraform_resource.type == "aws_s3_bucket"
    input.terraform_resource.acl == "public-read"
    msg := sprintf("S3 bucket '%s' has public read access", [input.terraform_resource.name])
}

# Check for missing encryption
violations[msg] {
    input.terraform_resource
    input.terraform_resource.type == "aws_s3_bucket"
    not input.terraform_resource.server_side_encryption_configuration
    msg := sprintf("S3 bucket '%s' missing encryption configuration", [input.terraform_resource.name])
}

violations[msg] {
    input.terraform_resource
    input.terraform_resource.type == "aws_db_instance"
    input.terraform_resource.storage_encrypted == false
    msg := sprintf("RDS instance '%s' does not have encryption enabled", [input.terraform_resource.name])
}

# Kubernetes security checks
violations[msg] {
    input.kubernetes_pod
    input.kubernetes_pod.spec.containers[_].securityContext.privileged == true
    msg := "Privileged container detected - violates Pod Security Standards"
}

violations[msg] {
    input.kubernetes_pod
    not input.kubernetes_pod.spec.securityContext
    msg := "Missing pod security context"
}

violations[msg] {
    input.kubernetes_pod
    container := input.kubernetes_pod.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container '%s' may run as root", [container.name])
}

# Compliance framework checks
cis_compliant {
    not violations[_]
}

soc2_compliant {
    not violations[_]
    input.encryption_at_rest == true
    input.encryption_in_transit == true
}

# Policy decision
decision = {
    "allow": allow,
    "violations": violations,
    "compliance": {
        "cis": cis_compliant,
        "soc2": soc2_compliant
    }
}