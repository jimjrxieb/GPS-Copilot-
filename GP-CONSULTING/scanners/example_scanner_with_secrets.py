#!/usr/bin/env python3
"""
Example Scanner with Secrets Management
========================================

This is a template showing how to properly use the SecretsManager
in GP-JADE scanners.

Author: GP-JADE Team
Date: October 1, 2025
"""

import sys
from pathlib import Path

# Add GP-PLATFORM to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-PLATFORM"))

from core.config import get_config
from loguru import logger


class ExampleScanner:
    """
    Example scanner demonstrating secure credential usage
    """

    def __init__(self):
        self.config = get_config()
        logger.info("Example Scanner initialized")

    def scan_with_github(self, repo_url: str):
        """
        Example: Scanning a GitHub repository

        SECURE: Uses SecretsManager for GitHub token
        """
        # Get GitHub token from secrets manager
        github_token = self.config.get_github_token()

        if not github_token:
            logger.error("GitHub token not configured")
            logger.info("Configure with: python3 GP-PLATFORM/core/secrets_manager.py")
            return None

        # Use the token securely
        import requests

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        try:
            response = requests.get(repo_url, headers=headers)
            logger.info(f"GitHub API call successful: {response.status_code}")
            return response.json()
        except Exception as e:
            logger.error(f"GitHub API call failed: {e}")
            return None

    def scan_aws_resources(self):
        """
        Example: Scanning AWS resources

        SECURE: Uses SecretsManager for AWS credentials
        """
        # Get AWS credentials from secrets manager
        aws_creds = self.config.get_aws_credentials()

        if not aws_creds:
            logger.error("AWS credentials not configured")
            logger.info("Configure with: sm.set_secret('aws_access_key', '...')")
            return None

        # Use credentials with boto3
        import boto3

        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=aws_creds['access_key'],
                aws_secret_access_key=aws_creds['secret_key'],
                region_name=aws_creds['region']
            )

            buckets = s3.list_buckets()
            logger.info(f"Found {len(buckets['Buckets'])} S3 buckets")
            return buckets

        except Exception as e:
            logger.error(f"AWS scan failed: {e}")
            return None

    def scan_docker_registry(self):
        """
        Example: Scanning Docker registry

        SECURE: Uses SecretsManager for Docker credentials
        """
        # Get Docker credentials from secrets manager
        docker_creds = self.config.get_docker_credentials()

        if not docker_creds:
            logger.error("Docker credentials not configured")
            return None

        # Use credentials (example with Docker API)
        import base64

        auth_string = f"{docker_creds['username']}:{docker_creds['token']}"
        auth_b64 = base64.b64encode(auth_string.encode()).decode()

        logger.info(f"Docker auth configured for user: {docker_creds['username']}")
        return auth_b64

    def validate_before_scan(self):
        """
        Example: Validating configuration before scanning

        BEST PRACTICE: Always validate credentials before use
        """
        validation = self.config.get_validation_status()

        logger.info("Configuration validation:")
        for integration, is_valid in validation.items():
            status = "✅" if is_valid else "❌"
            logger.info(f"  {status} {integration.upper()}")

        # Check if all required integrations are configured
        required = ["aws", "github"]
        missing = [i for i in required if not validation.get(i, False)]

        if missing:
            logger.warning(f"Missing required credentials: {', '.join(missing)}")
            return False

        logger.info("✅ All required credentials configured")
        return True


def main():
    """Demo the scanner"""
    scanner = ExampleScanner()

    # Validate configuration
    if not scanner.validate_before_scan():
        print("❌ Configuration incomplete. Please configure credentials.")
        return

    # Example: GitHub scan
    print("\n📦 GitHub Scan Example:")
    result = scanner.scan_with_github("https://api.github.com/user")
    if result:
        print(f"✅ Authenticated as: {result.get('login', 'Unknown')}")

    # Example: AWS scan
    print("\n☁️  AWS Scan Example:")
    buckets = scanner.scan_aws_resources()
    if buckets:
        print(f"✅ Found {len(buckets['Buckets'])} S3 buckets")

    # Example: Docker scan
    print("\n🐳 Docker Scan Example:")
    auth = scanner.scan_docker_registry()
    if auth:
        print(f"✅ Docker authentication configured")


if __name__ == "__main__":
    main()
