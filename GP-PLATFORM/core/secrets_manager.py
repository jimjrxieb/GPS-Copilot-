"""
GP-JADE Secrets Manager
=======================

Secure secrets management using OS-native keychain (Windows Credential Manager,
macOS Keychain, Linux Secret Service).

NO CLOUD REQUIRED - All secrets stored locally with OS-level encryption.

Author: GP-JADE Team
Date: October 1, 2025
"""

import keyring
from typing import Optional, Dict, List
from loguru import logger
import json
from pathlib import Path


class JadeSecretsManager:
    """
    Secure secrets management using OS keychain.

    All secrets are stored in the OS-native credential store:
    - Windows: Credential Manager
    - macOS: Keychain
    - Linux: Secret Service (gnome-keyring, kwallet)

    NO PLAIN TEXT FILES. NO CLOUD DEPENDENCIES.
    """

    SERVICE_NAME = "jade-ai"

    # Defined secret keys
    SECRET_KEYS = {
        # Cloud Providers
        "aws_access_key": "AWS Access Key ID",
        "aws_secret_key": "AWS Secret Access Key",
        "aws_region": "AWS Default Region",
        "azure_client_id": "Azure Client ID",
        "azure_client_secret": "Azure Client Secret",
        "azure_tenant_id": "Azure Tenant ID",
        "gcp_project_id": "GCP Project ID",
        "gcp_credentials_json": "GCP Credentials JSON",

        # Container Registries
        "docker_username": "Docker Hub Username",
        "docker_token": "Docker Hub Personal Access Token",
        "acr_username": "Azure Container Registry Username",
        "acr_password": "Azure Container Registry Password",
        "gcr_token": "Google Container Registry Token",

        # Version Control
        "github_token": "GitHub Personal Access Token",
        "gitlab_token": "GitLab Personal Access Token",
        "bitbucket_token": "Bitbucket App Password",

        # AI/ML Services
        "huggingface_token": "HuggingFace API Token",
        "openai_api_key": "OpenAI API Key",

        # Security Tools
        "gitguardian_token": "GitGuardian API Token",
        "snyk_token": "Snyk API Token",

        # Jade Specific
        "jade_encryption_key": "Jade Master Encryption Key",
        "jade_api_secret": "Jade API Secret Key",
    }

    def __init__(self):
        """Initialize secrets manager"""
        logger.info("Jade Secrets Manager initialized (using OS keychain)")

    def set_secret(self, key: str, value: str) -> bool:
        """
        Store a secret in OS keychain

        Args:
            key: Secret key name (e.g., "aws_access_key")
            value: Secret value

        Returns:
            True if successful, False otherwise
        """
        try:
            keyring.set_password(self.SERVICE_NAME, key, value)
            logger.info(f"Secret stored: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store secret {key}: {e}")
            return False

    def get_secret(self, key: str) -> Optional[str]:
        """
        Retrieve a secret from OS keychain

        Args:
            key: Secret key name

        Returns:
            Secret value or None if not found
        """
        try:
            value = keyring.get_password(self.SERVICE_NAME, key)
            if value:
                logger.debug(f"Secret retrieved: {key}")
            else:
                logger.warning(f"Secret not found: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to retrieve secret {key}: {e}")
            return None

    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret from OS keychain

        Args:
            key: Secret key name

        Returns:
            True if successful, False otherwise
        """
        try:
            keyring.delete_password(self.SERVICE_NAME, key)
            logger.info(f"Secret deleted: {key}")
            return True
        except keyring.errors.PasswordDeleteError:
            logger.warning(f"Secret not found for deletion: {key}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete secret {key}: {e}")
            return False

    def list_configured_secrets(self) -> List[Dict[str, str]]:
        """
        List all configured secrets (without values)

        Returns:
            List of dicts with key, description, and status
        """
        secrets_status = []

        for key, description in self.SECRET_KEYS.items():
            value = self.get_secret(key)
            secrets_status.append({
                "key": key,
                "description": description,
                "configured": value is not None,
                "value_preview": f"{value[:8]}..." if value else None
            })

        return secrets_status

    def export_to_encrypted_backup(self, backup_path: str, master_password: str) -> bool:
        """
        Export all secrets to encrypted backup file

        Args:
            backup_path: Path to save encrypted backup
            master_password: Password to encrypt the backup

        Returns:
            True if successful
        """
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
            import base64
            import os

            # Collect all secrets
            secrets = {}
            for key in self.SECRET_KEYS.keys():
                value = self.get_secret(key)
                if value:
                    secrets[key] = value

            # Derive encryption key from password
            salt = os.urandom(16)
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

            # Encrypt secrets
            cipher = Fernet(key)
            encrypted_data = cipher.encrypt(json.dumps(secrets).encode())

            # Save with salt prepended
            backup_data = salt + encrypted_data
            Path(backup_path).write_bytes(backup_data)

            logger.info(f"Secrets backed up to: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export secrets: {e}")
            return False

    def import_from_encrypted_backup(self, backup_path: str, master_password: str) -> bool:
        """
        Import secrets from encrypted backup file

        Args:
            backup_path: Path to encrypted backup
            master_password: Password to decrypt the backup

        Returns:
            True if successful
        """
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
            import base64

            # Read backup file
            backup_data = Path(backup_path).read_bytes()

            # Extract salt and encrypted data
            salt = backup_data[:16]
            encrypted_data = backup_data[16:]

            # Derive decryption key from password
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

            # Decrypt secrets
            cipher = Fernet(key)
            decrypted_data = cipher.decrypt(encrypted_data)
            secrets = json.loads(decrypted_data.decode())

            # Store all secrets in keychain
            for key, value in secrets.items():
                self.set_secret(key, value)

            logger.info(f"Secrets imported from: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import secrets: {e}")
            return False

    def validate_aws_credentials(self) -> bool:
        """
        Validate AWS credentials are configured

        Returns:
            True if AWS credentials are available
        """
        access_key = self.get_secret("aws_access_key")
        secret_key = self.get_secret("aws_secret_key")
        return access_key is not None and secret_key is not None

    def validate_github_credentials(self) -> bool:
        """
        Validate GitHub credentials are configured

        Returns:
            True if GitHub token is available
        """
        return self.get_secret("github_token") is not None

    def get_aws_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get AWS credentials as dict

        Returns:
            Dict with access_key, secret_key, region or None
        """
        access_key = self.get_secret("aws_access_key")
        secret_key = self.get_secret("aws_secret_key")
        region = self.get_secret("aws_region") or "us-east-1"

        if access_key and secret_key:
            return {
                "access_key": access_key,
                "secret_key": secret_key,
                "region": region
            }
        return None

    def get_docker_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get Docker Hub credentials as dict

        Returns:
            Dict with username, token or None
        """
        username = self.get_secret("docker_username")
        token = self.get_secret("docker_token")

        if username and token:
            return {
                "username": username,
                "token": token
            }
        return None

    def clear_all_secrets(self, confirm: str = None) -> bool:
        """
        DELETE ALL SECRETS (use with caution!)

        Args:
            confirm: Must be "DELETE_ALL_SECRETS" to proceed

        Returns:
            True if successful
        """
        if confirm != "DELETE_ALL_SECRETS":
            logger.warning("Clear all secrets requires confirmation: confirm='DELETE_ALL_SECRETS'")
            return False

        try:
            for key in self.SECRET_KEYS.keys():
                try:
                    self.delete_secret(key)
                except:
                    pass

            logger.warning("ALL SECRETS DELETED")
            return True
        except Exception as e:
            logger.error(f"Failed to clear secrets: {e}")
            return False


# Singleton instance
_secrets_manager = None

def get_secrets_manager() -> JadeSecretsManager:
    """Get singleton secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = JadeSecretsManager()
    return _secrets_manager


def main():
    """Test secrets manager"""
    from rich.console import Console
    from rich.table import Table

    console = Console()
    sm = get_secrets_manager()

    console.print("[cyan]GP-JADE Secrets Manager[/cyan]\n")

    # Show all configured secrets status
    table = Table(title="Secrets Configuration Status")
    table.add_column("Key", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    table.add_column("Preview", style="yellow")

    for secret in sm.list_configured_secrets():
        status = "✅ Configured" if secret["configured"] else "❌ Not Set"
        preview = secret["value_preview"] or "-"
        table.add_row(
            secret["key"],
            secret["description"],
            status,
            preview
        )

    console.print(table)

    # Show validation status
    console.print("\n[cyan]Validation:[/cyan]")
    console.print(f"  AWS Credentials: {'✅' if sm.validate_aws_credentials() else '❌'}")
    console.print(f"  GitHub Token: {'✅' if sm.validate_github_credentials() else '❌'}")


if __name__ == "__main__":
    main()
