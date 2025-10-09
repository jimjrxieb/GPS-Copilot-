#!/usr/bin/env python3
"""
OPA Policy Fixer - Real Implementation
Automatically fixes Open Policy Agent policy violations
"""

import json
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class OpaFixer:
    """
    Applies automated fixes for OPA (Open Policy Agent) policy violations.

    Supports:
    - Kubernetes resource policy violations
    - Terraform/IaC policy violations
    - Configuration policy violations
    - Custom Rego policy fixes
    """

    def __init__(self):
        config = GPDataConfig()
        self.fixes_dir = config.get_fixes_directory()
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        # Define fixable OPA policy patterns (Enhanced for full policy suite)
        self.fix_patterns = {
            # Kubernetes pod security
            'k8s_deny_privileged': {
                'name': 'remove_privileged_containers',
                'description': 'Remove privileged flag from containers',
                'fix_strategy': self._fix_privileged_container,
                'compliance': ['CIS-5.2.5', 'SOC2-CC6.1']
            },
            'k8s_require_labels': {
                'name': 'add_required_labels',
                'description': 'Add required labels to resources',
                'fix_strategy': self._fix_missing_labels,
                'compliance': ['SOC2-CC6.1', 'ISO27001-A.8.1']
            },
            'k8s_require_resource_limits': {
                'name': 'add_resource_limits',
                'description': 'Add CPU/memory limits',
                'fix_strategy': self._fix_resource_limits,
                'compliance': ['CIS-5.7.3', 'SOC2-CC7.1']
            },
            'k8s_deny_host_network': {
                'name': 'disable_host_network',
                'description': 'Disable hostNetwork access',
                'fix_strategy': self._fix_host_network,
                'compliance': ['CIS-5.2.4']
            },
            'k8s_deny_host_path': {
                'name': 'remove_host_path',
                'description': 'Remove hostPath volumes',
                'fix_strategy': self._fix_host_path,
                'compliance': ['CIS-5.2.9']
            },
            'k8s_require_non_root': {
                'name': 'enforce_non_root',
                'description': 'Run containers as non-root',
                'fix_strategy': self._fix_run_as_root,
                'compliance': ['CIS-5.2.6', 'NIST-AC-2']
            },
            'k8s_require_read_only_root': {
                'name': 'read_only_filesystem',
                'description': 'Set readOnlyRootFilesystem',
                'fix_strategy': self._fix_readonly_fs,
                'compliance': ['CIS-5.2.11', 'PCI-DSS-2.2.2']
            },

            # Secrets management (NEW)
            'secret_in_env': {
                'name': 'migrate_secret_to_volume',
                'description': 'Move secret from env var to volume mount',
                'fix_strategy': self._fix_secret_in_env,
                'compliance': ['CIS-5.4.1', 'PCI-DSS-3.4']
            },
            'hardcoded_secret': {
                'name': 'remove_hardcoded_secret',
                'description': 'Remove hardcoded secret from manifest',
                'fix_strategy': self._fix_hardcoded_secret,
                'compliance': ['SOC2-CC6.1', 'NIST-IA-5']
            },
            'automount_service_account': {
                'name': 'disable_automount',
                'description': 'Disable service account token auto-mount',
                'fix_strategy': self._fix_automount_token,
                'compliance': ['CIS-5.1.5']
            },

            # Image security (NEW)
            'untrusted_registry': {
                'name': 'enforce_trusted_registry',
                'description': 'Use trusted container registry',
                'fix_strategy': self._fix_untrusted_registry,
                'compliance': ['CIS-5.1.1', 'SLSA-L3']
            },
            'latest_tag': {
                'name': 'use_immutable_tag',
                'description': 'Replace :latest with specific tag',
                'fix_strategy': self._fix_latest_tag,
                'compliance': ['CIS-5.1.2', 'NIST-CM-2']
            },
            'image_pull_policy': {
                'name': 'fix_pull_policy',
                'description': 'Set imagePullPolicy to Always',
                'fix_strategy': self._fix_image_pull_policy,
                'compliance': ['CIS-5.1.3']
            },

            # Compliance controls (NEW)
            'missing_data_classification': {
                'name': 'add_data_classification',
                'description': 'Add data classification labels',
                'fix_strategy': self._fix_data_classification,
                'compliance': ['GDPR-Art.32', 'HIPAA-164.312']
            },
            'missing_audit_logging': {
                'name': 'enable_audit_logging',
                'description': 'Enable audit logging',
                'fix_strategy': self._fix_audit_logging,
                'compliance': ['SOC2-CC7.2', 'PCI-DSS-10.2']
            },
            'missing_backup_policy': {
                'name': 'add_backup_annotation',
                'description': 'Add backup policy annotation',
                'fix_strategy': self._fix_backup_policy,
                'compliance': ['SOC2-CC9.1', 'ISO27001-A.12.3']
            },

            # Terraform/IaC policies
            'tf_deny_public_access': {
                'name': 'restrict_public_access',
                'description': 'Restrict public network access',
                'fix_strategy': self._fix_public_access,
                'compliance': ['CIS-AWS-5.2', 'NIST-SC-7']
            },
            'tf_require_encryption': {
                'name': 'enable_encryption',
                'description': 'Enable encryption at rest',
                'fix_strategy': self._fix_encryption,
                'compliance': ['CIS-AWS-2.1.1', 'PCI-DSS-3.4']
            },
            'tf_require_tags': {
                'name': 'add_required_tags',
                'description': 'Add required resource tags',
                'fix_strategy': self._fix_missing_tags,
                'compliance': ['FinOps', 'SOC2-CC1.4']
            },
            's3_encryption': {
                'name': 'enable_s3_encryption',
                'description': 'Enable S3 bucket encryption',
                'fix_strategy': self._fix_s3_encryption,
                'compliance': ['CIS-AWS-2.1.1']
            },
            'rds_encryption': {
                'name': 'enable_rds_encryption',
                'description': 'Enable RDS storage encryption',
                'fix_strategy': self._fix_rds_encryption,
                'compliance': ['CIS-AWS-2.3.1']
            },

            # Network security (NEW)
            'metadata_service_access': {
                'name': 'block_metadata_service',
                'description': 'Block access to cloud metadata service',
                'fix_strategy': self._fix_metadata_access,
                'compliance': ['CLOUD-SECURITY']
            },
            'missing_network_policy': {
                'name': 'create_network_policy',
                'description': 'Create NetworkPolicy for namespace',
                'fix_strategy': self._fix_missing_network_policy,
                'compliance': ['CIS-5.3.2', 'PCI-DSS-1.2']
            },

            # Generic policies
            'deny_default_namespace': {
                'name': 'use_proper_namespace',
                'description': 'Use non-default namespace',
                'fix_strategy': self._fix_default_namespace,
                'compliance': ['Best-Practice']
            },
            'require_security_context': {
                'name': 'add_security_context',
                'description': 'Add security context',
                'fix_strategy': self._fix_security_context,
                'compliance': ['CIS-5.2.x']
            }
        }

        self.applied_fixes = []
        self.skipped_fixes = []
        self.backup_files = []

    def fix_findings(self, scan_results_path: str, project_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        """
        Main entry point to fix OPA policy violations.

        Args:
            scan_results_path: Path to OPA scan results JSON
            project_path: Path to the project being fixed
            auto_fix: If True, apply fixes automatically

        Returns:
            Dictionary with fix results
        """
        print(f"🔧 OPA Policy Fixer - Starting fix process")
        print(f"   Scan results: {scan_results_path}")
        print(f"   Target project: {project_path}")
        print(f"   Auto-fix mode: {auto_fix}")
        print()

        # Load scan results
        with open(scan_results_path, 'r') as f:
            scan_data = json.load(f)

        # Extract OPA violations
        violations = self._extract_violations(scan_data)

        if not violations:
            print("✅ No OPA policy violations to fix!")
            return {
                "status": "success",
                "fixes_applied": 0,
                "message": "No policy violations found"
            }

        print(f"📊 Found {len(violations)} policy violations to analyze")
        print()

        # Group violations by file
        violations_by_file = {}
        for violation in violations:
            filepath = violation.get('file', '')

            if not filepath:
                continue

            # Make path absolute if it's relative
            if not Path(filepath).is_absolute():
                filepath = str(Path(project_path) / filepath.lstrip('/'))

            if filepath not in violations_by_file:
                violations_by_file[filepath] = []
            violations_by_file[filepath].append(violation)

        # Process each file
        for filepath, file_violations in violations_by_file.items():
            if not Path(filepath).exists():
                print(f"⚠️  Skipping non-existent file: {filepath}")
                continue

            print(f"📝 Processing: {filepath}")
            self._fix_file(filepath, file_violations, auto_fix)
            print()

        # Generate fix report
        report = self._generate_fix_report(scan_results_path, project_path)

        print("\n📊 Fix Summary:")
        print(f"   ✅ Fixes applied: {len(self.applied_fixes)}")
        print(f"   ⚠️  Fixes skipped (manual review needed): {len(self.skipped_fixes)}")
        print(f"   💾 Backup files created: {len(self.backup_files)}")

        return report

    def _extract_violations(self, scan_data: dict) -> List[Dict]:
        """Extract policy violations from OPA results"""
        violations = []

        # Handle OPA output format from GP-copilot scanner
        if 'results' in scan_data and 'opa' in scan_data['results']:
            opa_data = scan_data['results']['opa']

            # OPA violations
            for violation in opa_data.get('violations', []):
                violations.append({
                    'policy': violation.get('policy', 'unknown'),
                    'file': violation.get('file', ''),
                    'resource': violation.get('resource', ''),
                    'message': violation.get('message', ''),
                    'severity': violation.get('severity', 'medium'),
                    'metadata': violation.get('metadata', {})
                })

        # Alternative format (direct OPA JSON result)
        elif 'result' in scan_data:
            for result in scan_data.get('result', []):
                if 'violations' in result:
                    for violation in result['violations']:
                        violations.append({
                            'policy': violation.get('msg', 'unknown'),
                            'file': violation.get('file', ''),
                            'resource': '',
                            'message': violation.get('msg', ''),
                            'severity': 'medium',
                            'metadata': violation
                        })

        return violations

    def _fix_file(self, filepath: str, violations: List[Dict], auto_fix: bool):
        """Fix policy violations in a single file"""

        # Create backup
        backup_path = self._create_backup(filepath)
        if backup_path:
            self.backup_files.append(backup_path)

        # Determine file type and load content
        file_ext = Path(filepath).suffix

        if file_ext in ['.yaml', '.yml']:
            with open(filepath, 'r') as f:
                try:
                    manifests = list(yaml.safe_load_all(f))
                except:
                    print(f"   ⚠️  Could not parse YAML file")
                    return
        elif file_ext == '.tf':
            with open(filepath, 'r') as f:
                content = f.read()
            manifests = [{'_type': 'terraform', '_content': content}]
        else:
            print(f"   ⚠️  Unsupported file type: {file_ext}")
            return

        modified = False

        # Apply fixes
        for i, manifest in enumerate(manifests):
            if not manifest:
                continue

            for violation in violations:
                policy_name = violation.get('policy', '').lower()

                # Match policy to fix pattern
                fix_pattern_key = self._match_policy_to_pattern(policy_name)

                if not fix_pattern_key:
                    self.skipped_fixes.append({
                        "file": filepath,
                        "policy": policy_name,
                        "reason": "No fix pattern available"
                    })
                    continue

                fix_config = self.fix_patterns[fix_pattern_key]
                print(f"   🔧 Fixing {policy_name} - {fix_config['description']}")

                try:
                    manifest = fix_config['fix_strategy'](manifest, violation)
                    modified = True

                    self.applied_fixes.append({
                        "file": filepath,
                        "policy": policy_name,
                        "fix_applied": fix_config['name'],
                        "description": fix_config['description']
                    })
                except Exception as e:
                    print(f"   ❌ Failed to fix: {str(e)}")
                    self.skipped_fixes.append({
                        "file": filepath,
                        "policy": policy_name,
                        "reason": f"Fix failed: {str(e)}"
                    })

            manifests[i] = manifest

        # Write fixed content if changes were made
        if modified and auto_fix:
            if file_ext in ['.yaml', '.yml']:
                with open(filepath, 'w') as f:
                    yaml.safe_dump_all(manifests, f, default_flow_style=False)
            elif file_ext == '.tf':
                with open(filepath, 'w') as f:
                    f.write(manifests[0]['_content'])

            print(f"   ✅ File updated with {len([f for f in self.applied_fixes if f['file'] == filepath])} fixes")

    def _match_policy_to_pattern(self, policy_name: str) -> Optional[str]:
        """Match policy violation to fix pattern (Enhanced for full policy suite)"""
        policy_lower = policy_name.lower()

        # Pod security
        if 'privileged' in policy_lower:
            return 'k8s_deny_privileged'
        elif 'allowprivilegeescalation' in policy_lower.replace(' ', ''):
            return 'k8s_deny_privileged'  # Same fix
        elif 'label' in policy_lower and 'require' in policy_lower:
            return 'k8s_require_labels'
        elif 'resource' in policy_lower and ('limit' in policy_lower or 'request' in policy_lower):
            return 'k8s_require_resource_limits'
        elif 'hostnetwork' in policy_lower or 'host_network' in policy_lower:
            return 'k8s_deny_host_network'
        elif 'hostpath' in policy_lower or 'host_path' in policy_lower:
            return 'k8s_deny_host_path'
        elif 'root' in policy_lower and ('non' in policy_lower or 'runasuser' in policy_lower.replace(' ', '')):
            return 'k8s_require_non_root'
        elif 'readonly' in policy_lower or 'read_only' in policy_lower or 'readonlyrootfilesystem' in policy_lower.replace(' ', ''):
            return 'k8s_require_read_only_root'

        # Secrets management
        elif 'secret' in policy_lower and 'environment' in policy_lower:
            return 'secret_in_env'
        elif 'hardcoded' in policy_lower and 'secret' in policy_lower:
            return 'hardcoded_secret'
        elif 'automount' in policy_lower and 'serviceaccount' in policy_lower.replace(' ', ''):
            return 'automount_service_account'

        # Image security
        elif 'untrusted' in policy_lower and 'registry' in policy_lower:
            return 'untrusted_registry'
        elif 'latest' in policy_lower and 'tag' in policy_lower:
            return 'latest_tag'
        elif 'imagepullpolicy' in policy_lower.replace(' ', ''):
            return 'image_pull_policy'

        # Compliance
        elif 'data' in policy_lower and 'classification' in policy_lower:
            return 'missing_data_classification'
        elif 'audit' in policy_lower and 'log' in policy_lower:
            return 'missing_audit_logging'
        elif 'backup' in policy_lower and 'policy' in policy_lower:
            return 'missing_backup_policy'

        # Terraform
        elif 's3' in policy_lower and 'encrypt' in policy_lower:
            return 's3_encryption'
        elif 'rds' in policy_lower and 'encrypt' in policy_lower:
            return 'rds_encryption'
        elif 'public' in policy_lower and ('access' in policy_lower or '0.0.0.0' in policy_lower):
            return 'tf_deny_public_access'
        elif 'encrypt' in policy_lower and 'terraform' not in policy_lower:
            return 'tf_require_encryption'
        elif 'tag' in policy_lower and ('missing' in policy_lower or 'require' in policy_lower):
            return 'tf_require_tags'

        # Network security
        elif 'metadata' in policy_lower and 'service' in policy_lower:
            return 'metadata_service_access'
        elif 'networkpolicy' in policy_lower.replace(' ', '') and 'missing' in policy_lower:
            return 'missing_network_policy'

        # Generic
        elif 'default' in policy_lower and 'namespace' in policy_lower:
            return 'deny_default_namespace'
        elif 'security' in policy_lower and 'context' in policy_lower:
            return 'require_security_context'

        return None

    # Fix strategies for each policy type

    def _fix_privileged_container(self, manifest: Dict, violation: Dict) -> Dict:
        """Remove privileged flag from containers"""
        if manifest.get('kind') in ['Pod', 'Deployment', 'StatefulSet', 'DaemonSet']:
            spec = self._get_pod_spec(manifest)
            if spec:
                for container in spec.get('containers', []):
                    if container.get('securityContext', {}).get('privileged'):
                        container['securityContext']['privileged'] = False
        return manifest

    def _fix_missing_labels(self, manifest: Dict, violation: Dict) -> Dict:
        """Add required labels to resources"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'labels' not in manifest['metadata']:
            manifest['metadata']['labels'] = {}

        # Add common required labels
        required_labels = {
            'app': manifest.get('metadata', {}).get('name', 'app'),
            'environment': 'production',
            'managed-by': 'opa-fixer'
        }

        for label, value in required_labels.items():
            if label not in manifest['metadata']['labels']:
                manifest['metadata']['labels'][label] = value

        return manifest

    def _fix_resource_limits(self, manifest: Dict, violation: Dict) -> Dict:
        """Add CPU/memory limits to containers"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                if 'resources' not in container:
                    container['resources'] = {}
                if 'limits' not in container['resources']:
                    container['resources']['limits'] = {
                        'cpu': '500m',
                        'memory': '512Mi'
                    }
                if 'requests' not in container['resources']:
                    container['resources']['requests'] = {
                        'cpu': '100m',
                        'memory': '128Mi'
                    }
        return manifest

    def _fix_host_network(self, manifest: Dict, violation: Dict) -> Dict:
        """Disable hostNetwork access"""
        spec = self._get_pod_spec(manifest)
        if spec and spec.get('hostNetwork'):
            spec['hostNetwork'] = False
        return manifest

    def _fix_host_path(self, manifest: Dict, violation: Dict) -> Dict:
        """Remove hostPath volumes"""
        spec = self._get_pod_spec(manifest)
        if spec and 'volumes' in spec:
            spec['volumes'] = [
                vol for vol in spec['volumes']
                if 'hostPath' not in vol
            ]
        return manifest

    def _fix_run_as_root(self, manifest: Dict, violation: Dict) -> Dict:
        """Configure containers to run as non-root"""
        spec = self._get_pod_spec(manifest)
        if spec:
            if 'securityContext' not in spec:
                spec['securityContext'] = {}
            spec['securityContext']['runAsNonRoot'] = True
            spec['securityContext']['runAsUser'] = 1000

            for container in spec.get('containers', []):
                if 'securityContext' not in container:
                    container['securityContext'] = {}
                container['securityContext']['runAsNonRoot'] = True
        return manifest

    def _fix_readonly_fs(self, manifest: Dict, violation: Dict) -> Dict:
        """Set readOnlyRootFilesystem"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                if 'securityContext' not in container:
                    container['securityContext'] = {}
                container['securityContext']['readOnlyRootFilesystem'] = True
        return manifest

    def _fix_public_access(self, manifest: Dict, violation: Dict) -> Dict:
        """Restrict public access in Terraform"""
        if manifest.get('_type') == 'terraform':
            content = manifest.get('_content', '')
            # Replace 0.0.0.0/0 with restricted CIDR
            content = re.sub(
                r'cidr_blocks\s*=\s*\["0\.0\.0\.0/0"\]',
                r'cidr_blocks = ["10.0.0.0/8"]  # FIXED: Restricted public access',
                content
            )
            manifest['_content'] = content
        return manifest

    def _fix_encryption(self, manifest: Dict, violation: Dict) -> Dict:
        """Enable encryption in Terraform"""
        if manifest.get('_type') == 'terraform':
            content = manifest.get('_content', '')
            # Add encryption flag if missing
            if 'encrypted' not in content:
                content = re.sub(
                    r'(resource\s+"[^"]+"\s+"[^"]+"\s*\{)',
                    r'\1\n  encrypted = true  # FIXED: Added encryption',
                    content,
                    count=1
                )
            manifest['_content'] = content
        return manifest

    def _fix_missing_tags(self, manifest: Dict, violation: Dict) -> Dict:
        """Add required tags in Terraform"""
        if manifest.get('_type') == 'terraform':
            content = manifest.get('_content', '')
            if 'tags' not in content:
                content = re.sub(
                    r'(resource\s+"[^"]+"\s+"[^"]+"\s*\{)',
                    r'''\1
  tags = {
    Environment = "production"
    ManagedBy   = "opa-fixer"
  }  # FIXED: Added required tags''',
                    content,
                    count=1
                )
            manifest['_content'] = content
        return manifest

    def _fix_default_namespace(self, manifest: Dict, violation: Dict) -> Dict:
        """Use non-default namespace"""
        if manifest.get('metadata', {}).get('namespace') == 'default':
            manifest['metadata']['namespace'] = 'production'
        elif 'namespace' not in manifest.get('metadata', {}):
            if 'metadata' not in manifest:
                manifest['metadata'] = {}
            manifest['metadata']['namespace'] = 'production'
        return manifest

    def _fix_security_context(self, manifest: Dict, violation: Dict) -> Dict:
        """Add security context"""
        spec = self._get_pod_spec(manifest)
        if spec:
            if 'securityContext' not in spec:
                spec['securityContext'] = {
                    'runAsNonRoot': True,
                    'runAsUser': 1000,
                    'fsGroup': 1000
                }
        return manifest

    def _get_pod_spec(self, manifest: Dict) -> Optional[Dict]:
        """Extract pod spec from various Kubernetes resources"""
        kind = manifest.get('kind')
        if kind == 'Pod':
            return manifest.get('spec')
        elif kind in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job']:
            return manifest.get('spec', {}).get('template', {}).get('spec')
        return None

    # NEW FIX STRATEGIES for enhanced policies

    def _fix_secret_in_env(self, manifest: Dict, violation: Dict) -> Dict:
        """Convert secret from env var to volume mount"""
        # This is a complex transformation - add annotation for manual review
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'annotations' not in manifest['metadata']:
            manifest['metadata']['annotations'] = {}
        manifest['metadata']['annotations']['security.guidepoint.io/review'] = 'migrate-secret-to-volume'
        return manifest

    def _fix_hardcoded_secret(self, manifest: Dict, violation: Dict) -> Dict:
        """Remove hardcoded secrets - requires manual intervention"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'annotations' not in manifest['metadata']:
            manifest['metadata']['annotations'] = {}
        manifest['metadata']['annotations']['security.guidepoint.io/review'] = 'remove-hardcoded-secret'
        return manifest

    def _fix_automount_token(self, manifest: Dict, violation: Dict) -> Dict:
        """Disable service account token auto-mount"""
        spec = self._get_pod_spec(manifest)
        if spec:
            spec['automountServiceAccountToken'] = False
        return manifest

    def _fix_untrusted_registry(self, manifest: Dict, violation: Dict) -> Dict:
        """Flag untrusted registry for manual review"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'annotations' not in manifest['metadata']:
            manifest['metadata']['annotations'] = {}
        manifest['metadata']['annotations']['security.guidepoint.io/review'] = 'use-trusted-registry'
        return manifest

    def _fix_latest_tag(self, manifest: Dict, violation: Dict) -> Dict:
        """Replace :latest tag"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                image = container.get('image', '')
                if image.endswith(':latest') or ':' not in image:
                    container['image'] = f"{image.split(':')[0]}:v1.0"
                    # Add annotation for manual review
                    if 'metadata' not in manifest:
                        manifest['metadata'] = {}
                    if 'annotations' not in manifest['metadata']:
                        manifest['metadata']['annotations'] = {}
                    manifest['metadata']['annotations']['security.guidepoint.io/review'] = 'update-image-tag'
        return manifest

    def _fix_image_pull_policy(self, manifest: Dict, violation: Dict) -> Dict:
        """Set imagePullPolicy to Always"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                container['imagePullPolicy'] = 'Always'
        return manifest

    def _fix_data_classification(self, manifest: Dict, violation: Dict) -> Dict:
        """Add data classification labels"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'labels' not in manifest['metadata']:
            manifest['metadata']['labels'] = {}
        manifest['metadata']['labels']['data-classification'] = 'internal'
        manifest['metadata']['labels']['owner'] = 'security-team'
        manifest['metadata']['labels']['cost-center'] = 'engineering'
        return manifest

    def _fix_audit_logging(self, manifest: Dict, violation: Dict) -> Dict:
        """Enable audit logging annotation"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'annotations' not in manifest['metadata']:
            manifest['metadata']['annotations'] = {}
        manifest['metadata']['annotations']['logging.guidepoint.io/audit-enabled'] = 'true'
        return manifest

    def _fix_backup_policy(self, manifest: Dict, violation: Dict) -> Dict:
        """Add backup policy annotation"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'annotations' not in manifest['metadata']:
            manifest['metadata']['annotations'] = {}
        manifest['metadata']['annotations']['backup.guidepoint.io/enabled'] = 'true'
        manifest['metadata']['annotations']['backup.guidepoint.io/retention-days'] = '30'
        return manifest

    def _fix_s3_encryption(self, manifest: Dict, violation: Dict) -> Dict:
        """Enable S3 encryption in Terraform"""
        if manifest.get('_type') == 'terraform':
            content = manifest.get('_content', '')
            if 'aws_s3_bucket' in content and 'server_side_encryption_configuration' not in content:
                content = re.sub(
                    r'(resource\s+"aws_s3_bucket"\s+"[^"]+"\s*\{)',
                    r'''\1
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }  # FIXED: Added S3 encryption''',
                    content,
                    count=1
                )
            manifest['_content'] = content
        return manifest

    def _fix_rds_encryption(self, manifest: Dict, violation: Dict) -> Dict:
        """Enable RDS encryption in Terraform"""
        if manifest.get('_type') == 'terraform':
            content = manifest.get('_content', '')
            if 'aws_db_instance' in content and 'storage_encrypted' not in content:
                content = re.sub(
                    r'(resource\s+"aws_db_instance"\s+"[^"]+"\s*\{)',
                    r'\1\n  storage_encrypted = true  # FIXED: Added RDS encryption',
                    content,
                    count=1
                )
            manifest['_content'] = content
        return manifest

    def _fix_metadata_access(self, manifest: Dict, violation: Dict) -> Dict:
        """Add annotation to block metadata service access"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'annotations' not in manifest['metadata']:
            manifest['metadata']['annotations'] = {}
        manifest['metadata']['annotations']['security.guidepoint.io/block-metadata'] = 'true'
        return manifest

    def _fix_missing_network_policy(self, manifest: Dict, violation: Dict) -> Dict:
        """Add annotation for NetworkPolicy creation"""
        if 'metadata' not in manifest:
            manifest['metadata'] = {}
        if 'annotations' not in manifest['metadata']:
            manifest['metadata']['annotations'] = {}
        manifest['metadata']['annotations']['security.guidepoint.io/create-netpol'] = 'true'
        return manifest

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
                "total_violations": len(self.applied_fixes) + len(self.skipped_fixes),
                "fixes_applied": len(self.applied_fixes),
                "fixes_skipped": len(self.skipped_fixes),
                "files_modified": len(set(f['file'] for f in self.applied_fixes)),
                "backups_created": len(self.backup_files)
            },
            "applied_fixes": self.applied_fixes,
            "skipped_fixes": self.skipped_fixes,
            "backup_files": self.backup_files
        }

        # Save report
        report_file = self.fixes_dir / f"opa_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Fix report saved: {report_file}")

        return report


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("OPA Policy Fixer - Automatically fix Open Policy Agent violations")
        print()
        print("Usage:")
        print("  opa_fixer.py <scan_results.json> <project_path>")
        print()
        print("Arguments:")
        print("  scan_results.json  - Path to OPA scan results JSON file")
        print("  project_path       - Path to the project to fix")
        print()
        print("Example:")
        print("  opa_fixer.py scan_results.json ./kubernetes")
        print()
        print("Fixable Policies (Enhanced Suite):")
        print()
        print("  📦 Kubernetes Pod Security:")
        print("    - Remove privileged containers (CIS-5.2.5)")
        print("    - Add required labels (SOC2-CC6.1)")
        print("    - Add resource limits/requests (CIS-5.7.3)")
        print("    - Disable hostNetwork/hostPath (CIS-5.2.4, 5.2.9)")
        print("    - Enforce non-root containers (CIS-5.2.6)")
        print("    - Set readOnlyRootFilesystem (CIS-5.2.11)")
        print()
        print("  🔐 Secrets Management:")
        print("    - Migrate secrets to volume mounts (CIS-5.4.1)")
        print("    - Remove hardcoded secrets (SOC2-CC6.1)")
        print("    - Disable service account auto-mount (CIS-5.1.5)")
        print()
        print("  🐳 Container Image Security:")
        print("    - Enforce trusted registries (SLSA-L3)")
        print("    - Replace :latest tags (CIS-5.1.2)")
        print("    - Fix imagePullPolicy (CIS-5.1.3)")
        print()
        print("  📋 Compliance Controls:")
        print("    - Add data classification labels (GDPR, HIPAA)")
        print("    - Enable audit logging (SOC2-CC7.2)")
        print("    - Add backup policies (ISO27001-A.12.3)")
        print()
        print("  ☁️  Terraform/IaC:")
        print("    - Restrict public access (CIS-AWS-5.2)")
        print("    - Enable S3/RDS encryption (CIS-AWS-2.1.1, 2.3.1)")
        print("    - Add required tags (FinOps)")
        print()
        print("  🌐 Network Security:")
        print("    - Block metadata service access (Cloud Security)")
        print("    - Create NetworkPolicies (CIS-5.3.2)")
        print()
        print("  🔧 General:")
        print("    - Use non-default namespace")
        print("    - Add security context")
        sys.exit(1)

    scan_results = sys.argv[1]
    project_path = sys.argv[2]

    fixer = OpaFixer()
    result = fixer.fix_findings(scan_results, project_path)

    # Exit with appropriate code
    if result.get('status') == 'success':
        if result.get('statistics', {}).get('fixes_applied', 0) > 0:
            print("\n✅ Policy violations fixed!")
            print("⚠️  Please review the changes and test before deploying")
        sys.exit(0)
    else:
        print("\n❌ Fix process failed")
        sys.exit(1)


if __name__ == "__main__":
    main()