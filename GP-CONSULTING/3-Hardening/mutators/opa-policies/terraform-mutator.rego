package terraform.mutate

import future.keywords.in

# Mutating policy for Terraform - Auto-injects security defaults

# RDS: Auto-enable encryption
mutate_rds_encryption[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    not resource.change.after.storage_encrypted

    mutation := {
        "resource_type": "aws_db_instance",
        "resource_name": resource.name,
        "attribute": "storage_encrypted",
        "value": true,
        "reason": "PCI-DSS 3.4 - Enable encryption at rest"
    }
}

# RDS: Auto-make private
mutate_rds_public_access[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    resource.change.after.publicly_accessible == true

    mutation := {
        "resource_type": "aws_db_instance",
        "resource_name": resource.name,
        "attribute": "publicly_accessible",
        "value": false,
        "reason": "PCI-DSS 1.2.1 - Restrict public access to databases"
    }
}

# RDS: Auto-add KMS key
mutate_rds_kms[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_db_instance"
    resource.change.after.storage_encrypted == true
    not resource.change.after.kms_key_id

    mutation := {
        "resource_type": "aws_db_instance",
        "resource_name": resource.name,
        "attribute": "kms_key_id",
        "value": "aws_kms_key.securebank.arn",
        "reason": "Use customer-managed KMS key for encryption"
    }
}

# S3: Auto-enable encryption
mutate_s3_encryption[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_encryption(resource)

    mutation := {
        "resource_type": "aws_s3_bucket",
        "resource_name": resource.name,
        "attribute": "server_side_encryption_configuration",
        "value": {
            "rule": {
                "apply_server_side_encryption_by_default": {
                    "sse_algorithm": "aws:kms",
                    "kms_master_key_id": "aws_kms_key.securebank.arn"
                }
            }
        },
        "reason": "PCI-DSS 3.4 - Encrypt S3 buckets containing payment data"
    }
}

has_encryption(resource) {
    resource.change.after.server_side_encryption_configuration
}

# S3: Auto-block public access
mutate_s3_public_access[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_public_access_block(resource.name)

    mutation := {
        "resource_type": "aws_s3_bucket_public_access_block",
        "resource_name": sprintf("%s_public_access_block", [resource.name]),
        "attributes": {
            "bucket": sprintf("aws_s3_bucket.%s.id", [resource.name]),
            "block_public_acls": true,
            "block_public_policy": true,
            "ignore_public_acls": true,
            "restrict_public_buckets": true
        },
        "reason": "PCI-DSS 1.2.1 - Block all public access to S3 buckets"
    }
}

has_public_access_block(bucket_name) {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket_public_access_block"
    contains(resource.name, bucket_name)
}

# EKS: Auto-enable private endpoint
mutate_eks_private_endpoint[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_eks_cluster"
    vpc_config := resource.change.after.vpc_config[_]
    vpc_config.endpoint_public_access == true

    mutation := {
        "resource_type": "aws_eks_cluster",
        "resource_name": resource.name,
        "attribute": "vpc_config.endpoint_public_access",
        "value": false,
        "reason": "CIS 5.4.1 - Disable EKS public endpoint access"
    }
}

mutate_eks_private_access[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_eks_cluster"
    vpc_config := resource.change.after.vpc_config[_]
    not vpc_config.endpoint_private_access

    mutation := {
        "resource_type": "aws_eks_cluster",
        "resource_name": resource.name,
        "attribute": "vpc_config.endpoint_private_access",
        "value": true,
        "reason": "Enable EKS private endpoint access"
    }
}

# CloudWatch: Auto-enable encryption
mutate_cloudwatch_encryption[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_cloudwatch_log_group"
    not resource.change.after.kms_key_id

    mutation := {
        "resource_type": "aws_cloudwatch_log_group",
        "resource_name": resource.name,
        "attribute": "kms_key_id",
        "value": "aws_kms_key.securebank.arn",
        "reason": "Encrypt CloudWatch logs with KMS"
    }
}

# Security Group: Auto-restrict 0.0.0.0/0
mutate_security_group_open_world[mutation] {
    resource := input.resource_changes[_]
    resource.type == "aws_security_group"
    rule := resource.change.after.ingress[_]
    "0.0.0.0/0" in rule.cidr_blocks

    mutation := {
        "resource_type": "aws_security_group",
        "resource_name": resource.name,
        "attribute": sprintf("ingress[%d].cidr_blocks", [rule.index]),
        "value": ["10.0.0.0/8"],  # Internal VPC only
        "reason": "PCI-DSS 1.2.1 - Restrict ingress to internal networks only",
        "severity": "HIGH"
    }
}

# Aggregate all mutations
mutations := {
    "rds_encryption": mutate_rds_encryption,
    "rds_public_access": mutate_rds_public_access,
    "rds_kms": mutate_rds_kms,
    "s3_encryption": mutate_s3_encryption,
    "s3_public_access": mutate_s3_public_access,
    "eks_private_endpoint": mutate_eks_private_endpoint,
    "eks_private_access": mutate_eks_private_access,
    "cloudwatch_encryption": mutate_cloudwatch_encryption,
    "security_group_open_world": mutate_security_group_open_world
}

# Main mutation decision
mutate := {
    "apply": true,
    "mutations": [mutation | mutation := mutations[_][_]],
    "summary": sprintf("Auto-injected %d security defaults", [count(mutations)])
}
