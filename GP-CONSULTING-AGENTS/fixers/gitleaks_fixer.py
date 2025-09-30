#!/usr/bin/env python3
"""
Gitleaks Secret Fixer - Real Implementation
Automatically remediates secrets and sensitive data detected by Gitleaks
"""

import json
import sys
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class GitleaksFixer:
    """
    Applies automated fixes for Gitleaks secret findings.

    Supports:
    - Removing hardcoded secrets from source code
    - Converting to environment variables
    - Adding secrets to .gitignore patterns
    - Generating secret rotation recommendations
    """

    def __init__(self):
        config = GPDataConfig()
        self.fixes_dir = config.get_fixes_directory()
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        # Define secret remediation patterns
        self.secret_patterns = {
            'aws-access-key': {
                'env_var': 'AWS_ACCESS_KEY_ID',
                'description': 'AWS Access Key'
            },
            'aws-secret-key': {
                'env_var': 'AWS_SECRET_ACCESS_KEY',
                'description': 'AWS Secret Access Key'
            },
            'generic-api-key': {
                'env_var': 'API_KEY',
                'description': 'Generic API Key'
            },
            'password': {
                'env_var': 'PASSWORD',
                'description': 'Password'
            },
            'private-key': {
                'env_var': 'PRIVATE_KEY',
                'description': 'Private Key'
            },
            'slack-token': {
                'env_var': 'SLACK_TOKEN',
                'description': 'Slack Token'
            },
            'github-token': {
                'env_var': 'GITHUB_TOKEN',
                'description': 'GitHub Token'
            },
            'jwt': {
                'env_var': 'JWT_SECRET',
                'description': 'JWT Secret'
            },
            'database-url': {
                'env_var': 'DATABASE_URL',
                'description': 'Database Connection String'
            }
        }

        self.applied_fixes = []
        self.skipped_fixes = []
        self.backup_files = []
        self.secrets_to_rotate = []

    def fix_findings(self, scan_results_path: str, project_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        """
        Main entry point to fix Gitleaks findings.

        Args:
            scan_results_path: Path to Gitleaks scan results JSON
            project_path: Path to the project being fixed
            auto_fix: If True, apply fixes automatically

        Returns:
            Dictionary with fix results
        """
        print(f"🔧 Gitleaks Secret Fixer - Starting fix process")
        print(f"   Scan results: {scan_results_path}")
        print(f"   Target project: {project_path}")
        print(f"   Auto-fix mode: {auto_fix}")
        print()

        # Load scan results
        with open(scan_results_path, 'r') as f:
            scan_data = json.load(f)

        # Extract Gitleaks findings
        secrets = self._extract_secrets(scan_data)

        if not secrets:
            print("✅ No secrets found to fix!")
            return {
                "status": "success",
                "fixes_applied": 0,
                "message": "No secrets detected"
            }

        print(f"📊 Found {len(secrets)} secrets to analyze")
        print()

        # Group secrets by file
        secrets_by_file = {}
        for secret in secrets:
            filepath = secret.get('file', '')

            if not filepath:
                continue

            # Make path absolute if it's relative
            if not Path(filepath).is_absolute():
                filepath = str(Path(project_path) / filepath.lstrip('/'))

            if filepath not in secrets_by_file:
                secrets_by_file[filepath] = []
            secrets_by_file[filepath].append(secret)

        # Process each file
        for filepath, file_secrets in secrets_by_file.items():
            if not Path(filepath).exists():
                print(f"⚠️  Skipping non-existent file: {filepath}")
                continue

            print(f"📝 Processing: {filepath}")
            self._fix_file(filepath, file_secrets, auto_fix)
            print()

        # Create .env.example template
        if self.applied_fixes:
            self._create_env_template(project_path)

        # Generate fix report
        report = self._generate_fix_report(scan_results_path, project_path)

        print("\n📊 Fix Summary:")
        print(f"   ✅ Fixes applied: {len(self.applied_fixes)}")
        print(f"   ⚠️  Secrets requiring rotation: {len(self.secrets_to_rotate)}")
        print(f"   💾 Backup files created: {len(self.backup_files)}")

        if self.secrets_to_rotate:
            print("\n🔐 CRITICAL: These secrets are exposed and must be rotated:")
            for secret in self.secrets_to_rotate:
                print(f"   - {secret['type']}: {secret['file']}:line {secret['line']}")

        return report

    def _extract_secrets(self, scan_data: dict) -> List[Dict]:
        """Extract secret findings from Gitleaks results"""
        secrets = []

        # Handle Gitleaks output format
        if 'results' in scan_data and 'gitleaks' in scan_data['results']:
            gitleaks_data = scan_data['results']['gitleaks']

            # Gitleaks findings
            for finding in gitleaks_data.get('findings', []):
                secrets.append({
                    'type': finding.get('RuleID', 'unknown-secret'),
                    'file': finding.get('File', ''),
                    'line': finding.get('StartLine', 0),
                    'secret': finding.get('Secret', ''),
                    'match': finding.get('Match', ''),
                    'commit': finding.get('Commit', '')
                })

        # Alternative format (direct Gitleaks JSON)
        elif isinstance(scan_data, list):
            for finding in scan_data:
                secrets.append({
                    'type': finding.get('RuleID', 'unknown-secret'),
                    'file': finding.get('File', ''),
                    'line': finding.get('StartLine', 0),
                    'secret': finding.get('Secret', ''),
                    'match': finding.get('Match', ''),
                    'commit': finding.get('Commit', '')
                })

        return secrets

    def _fix_file(self, filepath: str, secrets: List[Dict], auto_fix: bool):
        """Fix secrets in a single file"""

        # Create backup
        backup_path = self._create_backup(filepath)
        if backup_path:
            self.backup_files.append(backup_path)

        # Read file content
        with open(filepath, 'r') as f:
            lines = f.readlines()
            original_content = ''.join(lines)

        modified = False

        # Sort secrets by line number (reverse order to maintain line numbers)
        secrets.sort(key=lambda x: x.get('line', 0), reverse=True)

        # Apply fixes
        for secret in secrets:
            secret_type = secret.get('type', '').lower()
            line_num = secret.get('line', 0)
            secret_value = secret.get('secret', '')

            # Determine environment variable name
            env_var = self._get_env_var_name(secret_type, secret_value)

            print(f"   🔒 Line {line_num}: {secret_type} - Replacing with env var {env_var}")

            # Track for rotation
            self.secrets_to_rotate.append({
                'type': secret_type,
                'file': filepath,
                'line': line_num,
                'env_var': env_var
            })

            if line_num > 0 and line_num <= len(lines):
                line_idx = line_num - 1
                original_line = lines[line_idx]

                # Replace the secret with environment variable reference
                fixed_line = self._replace_secret_with_env(
                    original_line,
                    secret_value,
                    env_var,
                    filepath
                )

                if fixed_line != original_line:
                    lines[line_idx] = fixed_line
                    modified = True

                    self.applied_fixes.append({
                        "file": filepath,
                        "line": line_num,
                        "secret_type": secret_type,
                        "env_var": env_var,
                        "fix_applied": "replaced_with_env_var"
                    })

        # Write fixed content if changes were made
        if modified and auto_fix:
            with open(filepath, 'w') as f:
                f.writelines(lines)
            print(f"   ✅ File updated with {len([f for f in self.applied_fixes if f['file'] == filepath])} fixes")

    def _get_env_var_name(self, secret_type: str, secret_value: str) -> str:
        """Determine appropriate environment variable name for secret"""
        for pattern, config in self.secret_patterns.items():
            if pattern in secret_type:
                return config['env_var']

        # Generic fallback
        if 'api' in secret_type or 'key' in secret_type:
            return 'API_KEY'
        elif 'token' in secret_type:
            return 'AUTH_TOKEN'
        elif 'password' in secret_type:
            return 'PASSWORD'
        else:
            return 'SECRET'

    def _replace_secret_with_env(self, line: str, secret: str, env_var: str, filepath: str) -> str:
        """Replace secret value with environment variable reference"""

        # Determine language/format
        file_ext = Path(filepath).suffix

        # Python
        if file_ext == '.py':
            # Add import if not present (will be added at top of file later)
            if secret in line:
                # Replace the secret value with os.environ.get()
                fixed_line = line.replace(
                    f'"{secret}"',
                    f'os.environ.get("{env_var}", "")'
                ).replace(
                    f"'{secret}'",
                    f'os.environ.get("{env_var}", "")'
                )
                # Add comment
                if fixed_line != line:
                    return f"{fixed_line.rstrip()}  # FIXED: Moved secret to environment variable\n"

        # JavaScript/TypeScript
        elif file_ext in ['.js', '.ts', '.jsx', '.tsx']:
            if secret in line:
                fixed_line = line.replace(
                    f'"{secret}"',
                    f'process.env.{env_var} || ""'
                ).replace(
                    f"'{secret}'",
                    f"process.env.{env_var} || ''"
                )
                if fixed_line != line:
                    return f"{fixed_line.rstrip()}  // FIXED: Moved secret to environment variable\n"

        # YAML (Kubernetes, Docker Compose, etc.)
        elif file_ext in ['.yaml', '.yml']:
            if secret in line:
                # For YAML, use a placeholder that needs manual env var setup
                fixed_line = line.replace(secret, f"${{{env_var}}}")
                if fixed_line != line:
                    return f"{fixed_line.rstrip()}  # FIXED: Use env var {env_var}\n"

        # Shell scripts
        elif file_ext in ['.sh', '.bash']:
            if secret in line:
                fixed_line = line.replace(
                    f'"{secret}"',
                    f'"${{{env_var}}}"'
                ).replace(
                    f"'{secret}'",
                    f'"${{{env_var}}}"'
                )
                if fixed_line != line:
                    return f"{fixed_line.rstrip()}  # FIXED: Moved secret to environment variable\n"

        # Terraform
        elif file_ext == '.tf':
            if secret in line:
                fixed_line = line.replace(
                    f'"{secret}"',
                    f'var.{env_var.lower()}'
                ).replace(
                    f"'{secret}'",
                    f'var.{env_var.lower()}'
                )
                if fixed_line != line:
                    return f"{fixed_line.rstrip()}  # FIXED: Moved to Terraform variable\n"

        # Generic replacement for unknown formats
        else:
            if secret in line:
                fixed_line = line.replace(secret, f"<{env_var}>")
                if fixed_line != line:
                    return f"{fixed_line.rstrip()}  # FIXED: Replace with environment variable {env_var}\n"

        return line

    def _create_env_template(self, project_path: str):
        """Create .env.example template with required environment variables"""
        env_vars = set()

        for fix in self.applied_fixes:
            env_vars.add(fix['env_var'])

        if not env_vars:
            return

        env_example_path = Path(project_path) / '.env.example'

        # Load existing .env.example if it exists
        existing_vars = set()
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        var_name = line.split('=')[0].strip()
                        existing_vars.add(var_name)

        # Add new variables
        new_vars = env_vars - existing_vars

        if new_vars:
            with open(env_example_path, 'a') as f:
                f.write(f"\n# Added by Gitleaks Fixer - {datetime.now().strftime('%Y-%m-%d')}\n")
                for var in sorted(new_vars):
                    f.write(f"{var}=\n")

            print(f"\n   📝 Updated {env_example_path} with {len(new_vars)} new environment variables")

    def _create_backup(self, filepath: str) -> Optional[str]:
        """Create backup of file before fixing"""
        try:
            backup_path = f"{filepath}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(filepath, 'r') as source:
                with open(backup_path, 'w') as backup:
                    backup.write(source.read())
            return backup_path
        except Exception as e:
            print(f"   ⚠️  Could not create backup: {e}")
            return None

    def _generate_fix_report(self, scan_path: str, project_path: str) -> Dict[str, Any]:
        """Generate comprehensive fix report"""

        timestamp = datetime.now().isoformat()
        report = {
            "status": "success",
            "timestamp": timestamp,
            "scan_file": scan_path,
            "project": project_path,
            "statistics": {
                "total_secrets": len(self.applied_fixes),
                "fixes_applied": len(self.applied_fixes),
                "secrets_to_rotate": len(self.secrets_to_rotate),
                "files_modified": len(set(f['file'] for f in self.applied_fixes)),
                "backups_created": len(self.backup_files)
            },
            "applied_fixes": self.applied_fixes,
            "secrets_to_rotate": self.secrets_to_rotate,
            "backup_files": self.backup_files,
            "rotation_instructions": self._generate_rotation_instructions()
        }

        # Save report
        report_file = self.fixes_dir / f"gitleaks_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Fix report saved: {report_file}")

        return report

    def _generate_rotation_instructions(self) -> Dict[str, str]:
        """Generate secret rotation instructions"""
        instructions = {}

        for secret in self.secrets_to_rotate:
            secret_type = secret['type']

            if 'aws' in secret_type:
                instructions[secret_type] = "1. Go to AWS IAM Console\n2. Delete old access key\n3. Create new access key\n4. Update environment variables"
            elif 'github' in secret_type:
                instructions[secret_type] = "1. Go to GitHub Settings > Developer settings > Personal access tokens\n2. Delete old token\n3. Generate new token\n4. Update environment variables"
            elif 'slack' in secret_type:
                instructions[secret_type] = "1. Go to Slack App Settings\n2. Regenerate OAuth token\n3. Update environment variables"
            elif 'database' in secret_type:
                instructions[secret_type] = "1. Connect to database\n2. Change password for user\n3. Update DATABASE_URL environment variable"
            else:
                instructions[secret_type] = "1. Access service admin panel\n2. Regenerate or rotate secret\n3. Update environment variables"

        return instructions


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Gitleaks Secret Fixer - Automatically remediate exposed secrets")
        print()
        print("Usage:")
        print("  gitleaks_fixer.py <scan_results.json> <project_path>")
        print()
        print("Arguments:")
        print("  scan_results.json  - Path to Gitleaks scan results JSON file")
        print("  project_path       - Path to the project to fix")
        print()
        print("Example:")
        print("  gitleaks_fixer.py scan_results.json ./my-project")
        print()
        print("How it works:")
        print("  1. Identifies exposed secrets from Gitleaks scan")
        print("  2. Replaces hardcoded secrets with environment variables")
        print("  3. Creates/updates .env.example template")
        print("  4. Generates secret rotation instructions")
        print("  5. Creates backups and comprehensive report")
        print()
        print("⚠️  IMPORTANT: Exposed secrets MUST be rotated immediately!")
        sys.exit(1)

    scan_results = sys.argv[1]
    project_path = sys.argv[2]

    fixer = GitleaksFixer()
    result = fixer.fix_findings(scan_results, project_path)

    # Exit with appropriate code
    if result.get('status') == 'success':
        if result.get('statistics', {}).get('fixes_applied', 0) > 0:
            print("\n✅ Secrets removed from source code!")
            print("⚠️  CRITICAL: Exposed secrets MUST be rotated NOW!")
            print("⚠️  Review the fix report for rotation instructions")
        sys.exit(0)
    else:
        print("\n❌ Fix process failed")
        sys.exit(1)


if __name__ == "__main__":
    main()