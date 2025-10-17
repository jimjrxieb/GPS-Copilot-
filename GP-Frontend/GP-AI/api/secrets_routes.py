"""
GP-JADE Secrets Management API Routes
======================================

FastAPI routes for managing secrets through the GUI.

Author: GP-JADE Team
Date: October 1, 2025
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Import from GP-AI/core (was GP-PLATFORM, now merged)
from core.secrets_manager import get_config
from core.secrets_manager import JadeSecretsManager
from loguru import logger

router = APIRouter()


class SecretRequest(BaseModel):
    """Request model for setting a secret"""
    key: str
    value: str


class SecretInfo(BaseModel):
    """Response model for secret information (no value)"""
    key: str
    description: str
    configured: bool
    last_modified: Optional[str] = None


class BackupRequest(BaseModel):
    """Request model for creating encrypted backup"""
    password: str


# Define all supported secrets with descriptions
SECRET_DEFINITIONS = {
    "github_token": "GitHub Personal Access Token for API access",
    "huggingface_token": "HuggingFace API token for model access",
    "gitguardian_token": "GitGuardian API token for secret scanning",
    "aws_access_key": "AWS Access Key ID",
    "aws_secret_key": "AWS Secret Access Key",
    "aws_region": "AWS Default Region (e.g., us-east-1)",
    "docker_username": "Docker Hub username",
    "docker_token": "Docker Hub access token",
    "acr_username": "Azure Container Registry username",
    "acr_token": "Azure Container Registry password"
}


@router.get("/api/v1/secrets", response_model=List[SecretInfo])
async def get_secrets_status():
    """
    Get status of all secrets (configured or missing)

    Returns list of secrets with their configuration status.
    Does NOT return actual secret values for security.
    """
    try:
        config = get_config()
        secrets_list = []

        for key, description in SECRET_DEFINITIONS.items():
            value = config.sm.get_secret(key)
            secrets_list.append(
                SecretInfo(
                    key=key,
                    description=description,
                    configured=value is not None
                )
            )

        logger.info(f"Retrieved status for {len(secrets_list)} secrets")
        return secrets_list

    except Exception as e:
        logger.error(f"Failed to get secrets status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve secrets: {str(e)}")


@router.get("/api/v1/secrets/{key}/preview")
async def get_secret_preview(key: str):
    """
    Get a preview of a secret value (first 8 chars + ***)

    Returns masked version for verification without exposing full value.
    """
    try:
        if key not in SECRET_DEFINITIONS:
            raise HTTPException(status_code=404, detail=f"Unknown secret: {key}")

        config = get_config()
        value = config.sm.get_secret(key)

        if not value:
            return {"key": key, "preview": None, "configured": False}

        # Show first 8 characters + ***
        preview = value[:8] + "***" if len(value) > 8 else "***"

        return {
            "key": key,
            "preview": preview,
            "configured": True,
            "length": len(value)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get secret preview for {key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get preview: {str(e)}")


@router.post("/api/v1/secrets")
async def set_secret(request: SecretRequest):
    """
    Set or update a secret value

    Stores the secret in OS keychain with AES-256 encryption.
    """
    try:
        if request.key not in SECRET_DEFINITIONS:
            raise HTTPException(status_code=400, detail=f"Unknown secret: {request.key}")

        if not request.value or not request.value.strip():
            raise HTTPException(status_code=400, detail="Secret value cannot be empty")

        config = get_config()
        success = config.sm.set_secret(request.key, request.value)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store secret")

        logger.info(f"Secret '{request.key}' set successfully")

        return {
            "success": True,
            "message": f"Secret '{request.key}' stored securely",
            "key": request.key
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set secret {request.key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set secret: {str(e)}")


@router.delete("/api/v1/secrets/{key}")
async def delete_secret(key: str):
    """
    Delete a secret from the keychain
    """
    try:
        if key not in SECRET_DEFINITIONS:
            raise HTTPException(status_code=404, detail=f"Unknown secret: {key}")

        config = get_config()
        success = config.sm.delete_secret(key)

        if not success:
            raise HTTPException(status_code=404, detail=f"Secret '{key}' not found or already deleted")

        logger.info(f"Secret '{key}' deleted successfully")

        return {
            "success": True,
            "message": f"Secret '{key}' deleted",
            "key": key
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete secret {key}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete secret: {str(e)}")


@router.get("/api/v1/secrets/validation/status")
async def get_validation_status():
    """
    Get validation status for all integrations

    Checks if required secrets are configured for each integration.
    """
    try:
        config = get_config()
        validation = config.get_validation_status()

        return {
            "success": True,
            "validation": validation,
            "all_valid": all(validation.values())
        }

    except Exception as e:
        logger.error(f"Failed to get validation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate: {str(e)}")


@router.post("/api/v1/secrets/backup")
async def create_encrypted_backup(request: BackupRequest):
    """
    Create an encrypted backup of all secrets

    Requires a master password. Backup is encrypted with PBKDF2 + Fernet.
    """
    try:
        if not request.password or len(request.password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters"
            )

        config = get_config()

        # Create backup in GP-DATA/metadata/
        backup_dir = Path(__file__).parent.parent.parent / "GP-DATA" / "metadata"
        backup_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"secrets_backup_{timestamp}.enc"

        success = config.sm.export_to_encrypted_backup(
            str(backup_path),
            request.password
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to create backup")

        logger.info(f"Created encrypted backup at {backup_path}")

        return {
            "success": True,
            "message": "Encrypted backup created successfully",
            "backup_path": str(backup_path),
            "timestamp": timestamp
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")


@router.get("/api/v1/secrets/health")
async def secrets_health_check():
    """
    Health check for secrets management system
    """
    try:
        config = get_config()

        # Count configured secrets
        configured_count = sum(
            1 for key in SECRET_DEFINITIONS.keys()
            if config.sm.get_secret(key) is not None
        )

        return {
            "status": "healthy",
            "total_secrets": len(SECRET_DEFINITIONS),
            "configured_secrets": configured_count,
            "missing_secrets": len(SECRET_DEFINITIONS) - configured_count,
            "keyring_backend": str(config.sm.keyring.__class__.__name__)
        }

    except Exception as e:
        logger.error(f"Secrets health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
