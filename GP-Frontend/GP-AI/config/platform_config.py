"""
GP-JADE Configuration Management
=================================

Centralized configuration for all GP-JADE components.
Uses SecretsManager for sensitive credentials and environment variables for non-sensitive config.

Author: GP-JADE Team
Date: October 1, 2025
"""

import os
from typing import Optional
from pathlib import Path
import sys

# Add to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from secrets_manager import get_secrets_manager


class JadeConfig:
    """
    Centralized configuration management for GP-JADE.

    Priority order:
    1. Environment variables (for non-sensitive config)
    2. Secrets Manager (for credentials)
    3. Default values
    """

    def __init__(self):
        self.sm = get_secrets_manager()

    # ==================== AWS Configuration ====================

    def get_aws_access_key(self) -> Optional[str]:
        """Get AWS access key from secrets manager"""
        return self.sm.get_secret("aws_access_key")

    def get_aws_secret_key(self) -> Optional[str]:
        """Get AWS secret key from secrets manager"""
        return self.sm.get_secret("aws_secret_key")

    def get_aws_region(self) -> str:
        """Get AWS region (secrets manager or default)"""
        return self.sm.get_secret("aws_region") or os.getenv("AWS_REGION", "us-east-1")

    def get_aws_credentials(self) -> Optional[dict]:
        """Get complete AWS credentials"""
        return self.sm.get_aws_credentials()

    # ==================== Container Registry Configuration ====================

    def get_docker_username(self) -> Optional[str]:
        """Get Docker Hub username from secrets manager"""
        return self.sm.get_secret("docker_username")

    def get_docker_token(self) -> Optional[str]:
        """Get Docker Hub token from secrets manager"""
        return self.sm.get_secret("docker_token")

    def get_docker_credentials(self) -> Optional[dict]:
        """Get complete Docker credentials"""
        return self.sm.get_docker_credentials()

    def get_acr_username(self) -> Optional[str]:
        """Get Azure Container Registry username"""
        return self.sm.get_secret("acr_username")

    def get_acr_password(self) -> Optional[str]:
        """Get Azure Container Registry password"""
        return self.sm.get_secret("acr_password")

    # ==================== Git Configuration ====================

    def get_github_token(self) -> Optional[str]:
        """Get GitHub Personal Access Token from secrets manager"""
        return self.sm.get_secret("github_token")

    def get_gitlab_token(self) -> Optional[str]:
        """Get GitLab token from secrets manager"""
        return self.sm.get_secret("gitlab_token")

    # ==================== AI/ML Configuration ====================

    def get_huggingface_token(self) -> Optional[str]:
        """Get HuggingFace API token from secrets manager"""
        return self.sm.get_secret("huggingface_token")

    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from secrets manager"""
        return self.sm.get_secret("openai_api_key")

    # ==================== Security Tools Configuration ====================

    def get_gitguardian_token(self) -> Optional[str]:
        """Get GitGuardian API token from secrets manager"""
        return self.sm.get_secret("gitguardian_token")

    def get_snyk_token(self) -> Optional[str]:
        """Get Snyk token from secrets manager"""
        return self.sm.get_secret("snyk_token")

    # ==================== Jade Internal Configuration ====================

    def get_jade_api_secret(self) -> Optional[str]:
        """Get Jade API secret key"""
        return self.sm.get_secret("jade_api_secret")

    def get_jade_encryption_key(self) -> Optional[str]:
        """Get Jade master encryption key"""
        return self.sm.get_secret("jade_encryption_key")

    # ==================== Non-Sensitive Configuration ====================

    def get_opa_url(self) -> str:
        """Get OPA server URL (non-sensitive)"""
        return os.getenv("OPA_URL", "http://opa:8181")

    def get_jade_api_url(self) -> str:
        """Get Jade API URL (non-sensitive)"""
        return os.getenv("JADE_API_URL", "http://localhost:8000")

    def get_environment(self) -> str:
        """Get environment (development, staging, production)"""
        return os.getenv("JADE_ENV", "development")

    def get_log_level(self) -> str:
        """Get logging level"""
        return os.getenv("LOG_LEVEL", "INFO")

    def get_data_directory(self) -> Path:
        """Get data storage directory"""
        # Use absolute path to ensure GP-DATA is always at GP-copilot root
        gp_copilot_root = Path(__file__).parent.parent.parent.parent  # GP-Frontend/GP-AI/config -> GP-copilot
        default_path = gp_copilot_root / "GP-DATA"
        return Path(os.getenv("JADE_DATA_DIR", str(default_path)))

    def get_workspace_directory(self) -> Path:
        """Get workspace directory"""
        return Path(os.getenv("JADE_WORKSPACE", "~/jade-workspace")).expanduser()

    # ==================== Validation ====================

    def validate_aws_config(self) -> bool:
        """Check if AWS is properly configured"""
        return self.sm.validate_aws_credentials()

    def validate_github_config(self) -> bool:
        """Check if GitHub is properly configured"""
        return self.sm.validate_github_credentials()

    def validate_docker_config(self) -> bool:
        """Check if Docker is properly configured"""
        creds = self.get_docker_credentials()
        return creds is not None

    def get_validation_status(self) -> dict:
        """Get validation status for all integrations"""
        return {
            "aws": self.validate_aws_config(),
            "github": self.validate_github_config(),
            "docker": self.validate_docker_config(),
            "huggingface": self.get_huggingface_token() is not None,
            "gitguardian": self.get_gitguardian_token() is not None,
        }


# Singleton instance
_config = None

def get_config() -> JadeConfig:
    """Get singleton config instance"""
    global _config
    if _config is None:
        _config = JadeConfig()
    return _config


# Convenience functions for common use cases
def get_aws_credentials() -> Optional[dict]:
    """Quick access to AWS credentials"""
    return get_config().get_aws_credentials()

def get_github_token() -> Optional[str]:
    """Quick access to GitHub token"""
    return get_config().get_github_token()

def get_docker_credentials() -> Optional[dict]:
    """Quick access to Docker credentials"""
    return get_config().get_docker_credentials()


if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table

    console = Console()
    config = get_config()

    console.print("[cyan]GP-JADE Configuration Status[/cyan]\n")

    # Validation status
    table = Table(title="Integration Status")
    table.add_column("Integration", style="cyan")
    table.add_column("Status", style="green")

    status = config.get_validation_status()
    for integration, is_valid in status.items():
        status_text = "✅ Configured" if is_valid else "❌ Not Configured"
        table.add_row(integration.upper(), status_text)

    console.print(table)

    # Non-sensitive config
    console.print("\n[cyan]Non-Sensitive Configuration:[/cyan]")
    console.print(f"  OPA URL: {config.get_opa_url()}")
    console.print(f"  Jade API URL: {config.get_jade_api_url()}")
    console.print(f"  Environment: {config.get_environment()}")
    console.print(f"  Log Level: {config.get_log_level()}")
    console.print(f"  Data Directory: {config.get_data_directory()}")
    console.print(f"  Workspace: {config.get_workspace_directory()}")
