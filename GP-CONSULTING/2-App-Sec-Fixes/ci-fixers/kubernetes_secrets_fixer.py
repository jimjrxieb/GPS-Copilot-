#!/usr/bin/env python3
"""
🖖 PHASE 2 FIXER: Kubernetes Secrets Migration
Converts hardcoded secrets in ConfigMaps to proper Kubernetes Secrets

PCI-DSS: 3.4, 8.2.1
CIS Kubernetes: 5.4.1
NIST 800-53: SC-28
"""

import re
import base64
import yaml
import argparse
from pathlib import Path
from datetime import datetime

class KubernetesSecretsFixer:
    """Convert ConfigMap secrets to Kubernetes Secrets"""

    def __init__(self, target_file: Path):
        self.target_file = target_file
        self.backup_file = None
        self.secrets_found = []

    def backup(self):
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_file = self.target_file.parent / f"{self.target_file.name}.backup.{timestamp}"
        self.backup_file.write_text(self.target_file.read_text())
        print(f"✅ Backup created: {self.backup_file}")

    def identify_secrets(self, content: str) -> list:
        """Identify secret patterns in YAML"""
        secrets = []

        # Patterns that indicate secrets
        secret_patterns = [
            r'.*PASSWORD.*',
            r'.*SECRET.*',
            r'.*KEY.*',
            r'.*TOKEN.*',
            r'.*CREDENTIAL.*',
            r'.*AWS_ACCESS.*',
            r'.*AWS_SECRET.*',
            r'.*DB_PASSWORD.*',
            r'.*REDIS_PASSWORD.*',
            r'.*JWT_SECRET.*',
            r'.*API_KEY.*',
        ]

        lines = content.split('\n')
        for i, line in enumerate(lines):
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Extract key-value pair
                    if ':' in line:
                        key_value = line.split(':', 1)
                        if len(key_value) == 2:
                            key = key_value[0].strip()
                            value = key_value[1].strip().strip('"\'')
                            if value and not value.startswith('valueFrom'):
                                secrets.append({
                                    'line': i + 1,
                                    'key': key,
                                    'value': value,
                                    'original_line': line
                                })

        return secrets

    def create_kubernetes_secret(self, secrets: list, name: str = "app-secrets") -> str:
        """Create Kubernetes Secret manifest"""
        secret_data = {}

        for secret in secrets:
            key = secret['key'].replace('-', '_').replace(' ', '_')
            value = secret['value']
            # Base64 encode
            encoded = base64.b64encode(value.encode()).decode()
            secret_data[key] = encoded

        secret_manifest = f"""---
# ============================================================================
# KUBERNETES SECRET - PCI-DSS COMPLIANT
# ============================================================================
# Migrated from ConfigMap by kubernetes_secrets_fixer.py
# Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
#
# Compliance:
# - PCI-DSS 3.4: Secrets encrypted at rest (when encryption enabled)
# - CIS 5.4.1: Secrets not in ConfigMaps
# - NIST SC-28: Protection of information at rest
# ============================================================================
apiVersion: v1
kind: Secret
metadata:
  name: {name}
  namespace: securebank
  labels:
    app: securebank
    security: pci-compliant
type: Opaque
data:
"""

        for key, value in secret_data.items():
            secret_manifest += f"  {key}: {value}\n"

        return secret_manifest

    def fix_configmap_references(self, content: str, secrets: list) -> str:
        """Replace ConfigMap data with Secret references"""
        lines = content.split('\n')
        fixed_lines = []
        in_configmap_data = False
        configmap_indent = 0

        for i, line in enumerate(lines):
            # Check if we're in a ConfigMap data section
            if 'kind: ConfigMap' in line:
                in_configmap_data = False
            elif in_configmap_data and line.strip().startswith('data:'):
                configmap_indent = len(line) - len(line.lstrip())
                fixed_lines.append(line)
                continue
            elif in_configmap_data:
                # Check if this line contains a secret
                if any(s['line'] - 1 == i for s in secrets):
                    # Comment out the line
                    fixed_lines.append('  # ❌ REMOVED: Secret moved to Kubernetes Secret ' + line.lstrip())
                    continue

            # Check for env valueFrom configMapKeyRef
            if 'configMapKeyRef:' in line:
                # Check if the next line references a secret
                secret_key = None
                for s in secrets:
                    key_name = s['key'].replace('-', '_').replace(' ', '_')
                    if i + 2 < len(lines) and key_name in lines[i + 2]:
                        secret_key = key_name
                        break

                if secret_key:
                    # Replace with secretKeyRef
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * indent + 'secretKeyRef:  # ✅ FIXED: Using Secret instead of ConfigMap')
                    continue

            # Replace configmap name references
            if 'name: database-secrets' in line or 'name: app-config' in line:
                if any('SECRET' in s['key'] or 'PASSWORD' in s['key'] for s in secrets):
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * indent + 'name: app-secrets  # ✅ FIXED: Using Kubernetes Secret')
                    continue

            fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def generate_secret_manifest_file(self, secrets: list) -> Path:
        """Generate separate Secret manifest file"""
        secret_content = self.create_kubernetes_secret(secrets, "app-secrets")

        secret_file = self.target_file.parent / "secrets.yaml"
        secret_file.write_text(secret_content)

        print(f"✅ Secret manifest created: {secret_file}")
        return secret_file

    def fix(self) -> dict:
        """Execute the fix"""
        print("🖖 Kubernetes Secrets Fixer - Phase 2")
        print("="*70)

        # Backup
        self.backup()

        # Read content
        content = self.target_file.read_text()

        # Identify secrets
        self.secrets_found = self.identify_secrets(content)
        print(f"\n🔍 Found {len(self.secrets_found)} secrets in {self.target_file.name}")

        if not self.secrets_found:
            print("✅ No secrets found to fix")
            return {"success": True, "secrets_fixed": 0}

        # Show secrets found
        print("\n📋 Secrets to be moved:")
        for secret in self.secrets_found[:10]:  # Show first 10
            print(f"   Line {secret['line']}: {secret['key']}")
        if len(self.secrets_found) > 10:
            print(f"   ... and {len(self.secrets_found) - 10} more")

        # Create Kubernetes Secret manifest
        secret_file = self.generate_secret_manifest_file(self.secrets_found)

        # Fix ConfigMap references
        fixed_content = self.fix_configmap_references(content, self.secrets_found)

        # Write fixed content
        self.target_file.write_text(fixed_content)

        print(f"\n✅ Fixed {len(self.secrets_found)} secrets in {self.target_file.name}")
        print(f"✅ Kubernetes Secret created: {secret_file}")

        print("\n📊 Summary:")
        print(f"   Backup: {self.backup_file}")
        print(f"   Fixed file: {self.target_file}")
        print(f"   Secret manifest: {secret_file}")
        print(f"   Secrets migrated: {len(self.secrets_found)}")

        print("\n🚀 Next Steps:")
        print(f"   1. Review changes: diff {self.backup_file} {self.target_file}")
        print(f"   2. Apply Secret: kubectl apply -f {secret_file}")
        print(f"   3. Apply updated deployment: kubectl apply -f {self.target_file}")
        print(f"   4. Validate: kubectl get secrets -n securebank")

        return {
            "success": True,
            "secrets_fixed": len(self.secrets_found),
            "backup_file": str(self.backup_file),
            "secret_file": str(secret_file)
        }

def main():
    parser = argparse.ArgumentParser(description="Kubernetes Secrets Fixer - Phase 2")
    parser.add_argument("--target", required=True, help="Target YAML file to fix")
    args = parser.parse_args()

    target_file = Path(args.target)
    if not target_file.exists():
        print(f"❌ Target file not found: {target_file}")
        return 1

    fixer = KubernetesSecretsFixer(target_file)
    result = fixer.fix()

    if result["success"]:
        print(f"\n{'='*70}")
        print("✅ Kubernetes Secrets Fix Complete!")
        print(f"{'='*70}")
        return 0
    else:
        print("❌ Fix failed")
        return 1

if __name__ == "__main__":
    exit(main())
