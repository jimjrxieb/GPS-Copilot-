#!/usr/bin/env python3
"""
Migrate secrets from .env file to OS keychain
==============================================

This script safely migrates all secrets from the .env file to the OS-native
keychain (Windows Credential Manager, macOS Keychain, Linux Secret Service).

After migration, the .env file should be deleted manually.

Usage:
    python3 migrate_secrets.py

Author: GP-JADE Team
Date: October 1, 2025
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from core.secrets_manager import get_secrets_manager
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

console = Console()


def find_env_file():
    """Find .env file in project root"""
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        return env_file
    else:
        console.print("[yellow]⚠️  No .env file found in project root[/yellow]")
        return None


def load_env_secrets(env_file: Path):
    """Load secrets from .env file"""
    load_dotenv(env_file)

    # Map .env variable names to secrets manager keys
    env_mapping = {
        "AWS_ACCESS_KEY": "aws_access_key",
        "AWS_SECRET_ACCESS_KEY": "aws_secret_key",
        "AWS_REGION": "aws_region",

        "AZURE_CLIENT_ID": "azure_client_id",
        "AZURE_CLIENT_SECRET": "azure_client_secret",
        "AZURE_TENANT_ID": "azure_tenant_id",

        "DOCKER_USER": "docker_username",
        "DOCKER_CRED": "docker_token",

        "ACR_USERNAME": "acr_username",
        "ACR_PASSWORD": "acr_password",

        "GH_TOKEN": "github_token",
        "GH_USER": "github_username",

        "GITLAB_TOKEN": "gitlab_token",

        "HF_TOKEN": "huggingface_token",

        "GITGUARDIAN": "gitguardian_token",

        "OPENAI_API_KEY": "openai_api_key",
        "SNYK_TOKEN": "snyk_token",
    }

    secrets = {}
    for env_key, secret_key in env_mapping.items():
        value = os.getenv(env_key)
        if value:
            secrets[secret_key] = value

    return secrets


def migrate_secrets():
    """Main migration function"""
    console.print("[bold cyan]🔐 GP-JADE Secrets Migration Tool[/bold cyan]\n")

    # Find .env file
    env_file = find_env_file()
    if not env_file:
        console.print("[red]❌ Cannot migrate: .env file not found[/red]")
        return False

    console.print(f"[green]✓[/green] Found .env file: {env_file}\n")

    # Load secrets
    secrets = load_env_secrets(env_file)

    if not secrets:
        console.print("[yellow]⚠️  No secrets found in .env file[/yellow]")
        return False

    # Show what will be migrated
    table = Table(title="Secrets to Migrate")
    table.add_column("Key", style="cyan")
    table.add_column("Value Preview", style="yellow")
    table.add_column("Destination", style="green")

    for key, value in secrets.items():
        preview = f"{value[:8]}..." if len(value) > 8 else value
        table.add_row(key, preview, "OS Keychain")

    console.print(table)
    console.print()

    # Confirm migration (auto-confirm if running non-interactively)
    try:
        if not Confirm.ask(f"[yellow]Migrate {len(secrets)} secrets to OS keychain?[/yellow]"):
            console.print("[red]❌ Migration cancelled[/red]")
            return False
    except (EOFError, KeyboardInterrupt):
        console.print("\n[yellow]⚠️  Non-interactive mode detected - proceeding with migration...[/yellow]\n")

    # Perform migration
    console.print("\n[cyan]Migrating secrets...[/cyan]\n")
    sm = get_secrets_manager()

    migrated = 0
    failed = 0

    for key, value in secrets.items():
        if sm.set_secret(key, value):
            console.print(f"  [green]✓[/green] Migrated: {key}")
            migrated += 1
        else:
            console.print(f"  [red]✗[/red] Failed: {key}")
            failed += 1

    console.print()

    # Summary
    if failed == 0:
        console.print(f"[bold green]✅ Migration successful![/bold green]")
        console.print(f"   {migrated} secrets migrated to OS keychain\n")

        # Create backup
        backup_path = env_file.parent / ".env.backup"
        console.print(f"[cyan]Creating backup...[/cyan]")
        env_file.rename(backup_path)
        console.print(f"   [green]✓[/green] Original .env backed up to: {backup_path}\n")

        # Create .env.example
        example_path = env_file.parent / ".env.example"
        console.print(f"[cyan]Creating .env.example template...[/cyan]")
        with open(example_path, "w") as f:
            f.write("# GP-JADE Environment Variables\n")
            f.write("# All secrets are now stored in OS keychain (keyring)\n")
            f.write("# Use GP-PLATFORM/core/secrets_manager.py to manage secrets\n\n")
            for key in secrets.keys():
                f.write(f"# {key.upper()}=\n")
        console.print(f"   [green]✓[/green] Created: {example_path}\n")

        # Instructions
        console.print("[bold yellow]⚠️  NEXT STEPS:[/bold yellow]")
        console.print("   1. Verify secrets: python3 GP-PLATFORM/core/secrets_manager.py")
        console.print("   2. Test application with new secrets")
        console.print(f"   3. Delete backup: rm {backup_path}")
        console.print(f"   4. Add to .gitignore: echo '.env' >> .gitignore")
        console.print(f"   5. Remove from git: git rm --cached .env\n")

        return True
    else:
        console.print(f"[bold red]❌ Migration failed[/bold red]")
        console.print(f"   {migrated} migrated, {failed} failed\n")
        return False


def verify_migration():
    """Verify migrated secrets"""
    console.print("[cyan]Verifying migration...[/cyan]\n")

    sm = get_secrets_manager()

    table = Table(title="Migrated Secrets Verification")
    table.add_column("Key", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Preview", style="yellow")

    for secret in sm.list_configured_secrets():
        if secret["configured"]:
            status = "✅ OK"
            preview = secret["value_preview"]
            table.add_row(secret["key"], status, preview)

    console.print(table)


if __name__ == "__main__":
    success = migrate_secrets()

    if success:
        console.print("\n" + "="*60)
        verify_migration()
        console.print("="*60 + "\n")

        console.print("[bold green]🎉 Secrets successfully migrated to OS keychain![/bold green]")
        console.print("[dim]All secrets are now encrypted by your operating system.[/dim]\n")
