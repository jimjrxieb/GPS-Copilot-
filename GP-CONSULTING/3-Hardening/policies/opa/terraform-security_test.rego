package terraform.security

# OPA Policy Tests for Terraform Security
# Run with: opa test . --verbose

# Test: S3 bucket WITHOUT encryption (should DENY)
test_s3_bucket_without_encryption {
    deny["S3 bucket 'aws_s3_bucket.test_bucket' must have server-side encryption enabled"] with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.test_bucket",
            "change": {
                "after": {
                    "bucket": "test-bucket"
                }
            }
        }]
    }
}

# Test: S3 bucket WITH encryption (should ALLOW)
test_s3_bucket_with_encryption {
    count(deny) == 0 with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.test_bucket",
            "change": {
                "after": {
                    "bucket": "test-bucket",
                    "server_side_encryption_configuration": [{
                        "rule": [{
                            "apply_server_side_encryption_by_default": {
                                "sse_algorithm": "AES256"
                            }
                        }]
                    }]
                }
            }
        }]
    }
}

# Test: S3 bucket WITHOUT public access block (should DENY)
test_s3_bucket_without_public_access_block {
    deny["S3 bucket 'aws_s3_bucket.test_bucket' must have public access block enabled"] with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.test_bucket",
            "change": {
                "after": {
                    "bucket": "test-bucket",
                    "block_public_acls": false
                }
            }
        }]
    }
}

# Test: S3 bucket WITH public access block (should ALLOW)
test_s3_bucket_with_public_access_block {
    count(deny) == 0 with input as {
        "resource_changes": [{
            "type": "aws_s3_bucket",
            "address": "aws_s3_bucket.test_bucket",
            "change": {
                "after": {
                    "bucket": "test-bucket",
                    "block_public_acls": true,
                    "block_public_policy": true,
                    "ignore_public_acls": true,
                    "restrict_public_buckets": true,
                    "server_side_encryption_configuration": [{
                        "rule": [{
                            "apply_server_side_encryption_by_default": {
                                "sse_algorithm": "AES256"
                            }
                        }]
                    }]
                }
            }
        }]
    }
}

# Test: RDS instance WITHOUT encryption (should DENY if policy exists)
test_rds_instance_without_encryption {
    # This test assumes there's a deny rule for unencrypted RDS
    # Add the actual test based on your terraform-security.rego policy
    true  # Placeholder - replace with actual test
}

# Test: Security group with 0.0.0.0/0 ingress on SSH (should DENY if policy exists)
test_security_group_open_ssh {
    # This test assumes there's a deny rule for open SSH
    # Add the actual test based on your terraform-security.rego policy
    true  # Placeholder - replace with actual test
}
