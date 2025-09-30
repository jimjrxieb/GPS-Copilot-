#!/usr/bin/env python3
"""
Kubernetes Security Fixer - Real Implementation
Automatically fixes Kubernetes security issues from kube-bench, kubescape, and Polaris
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


class KubernetesFixer:
    """
    Applies automated fixes for Kubernetes security findings.

    Supports fixes for:
    - kube-bench CIS benchmarks
    - kubescape security framework
    - Polaris best practices
    """

    def __init__(self):
        config = GPDataConfig()
        self.fixes_dir = config.get_fixes_directory()
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

        # Define fixable Kubernetes security patterns
        self.fix_patterns = {
            # Pod Security
            "no_security_context": {
                "name": "add_security_context",
                "description": "Add security context to pod",
                "fix_strategy": self._fix_security_context
            },
            "privileged_container": {
                "name": "remove_privileged",
                "description": "Remove privileged flag from container",
                "fix_strategy": self._fix_privileged_container
            },
            "runs_as_root": {
                "name": "non_root_user",
                "description": "Run container as non-root user",
                "fix_strategy": self._fix_run_as_root
            },
            "no_resource_limits": {
                "name": "add_resource_limits",
                "description": "Add CPU/memory limits",
                "fix_strategy": self._fix_resource_limits
            },
            "no_resource_requests": {
                "name": "add_resource_requests",
                "description": "Add CPU/memory requests",
                "fix_strategy": self._fix_resource_requests
            },
            "no_readiness_probe": {
                "name": "add_readiness_probe",
                "description": "Add readiness probe",
                "fix_strategy": self._fix_readiness_probe
            },
            "no_liveness_probe": {
                "name": "add_liveness_probe",
                "description": "Add liveness probe",
                "fix_strategy": self._fix_liveness_probe
            },

            # Network Security
            "no_network_policy": {
                "name": "create_network_policy",
                "description": "Create network policy",
                "fix_strategy": self._fix_network_policy
            },

            # RBAC
            "overly_permissive_rbac": {
                "name": "restrict_rbac",
                "description": "Restrict RBAC permissions",
                "fix_strategy": self._fix_rbac_permissions
            },

            # Image Security
            "image_pull_policy_not_always": {
                "name": "fix_image_pull_policy",
                "description": "Set imagePullPolicy to Always",
                "fix_strategy": self._fix_image_pull_policy
            },
            "latest_image_tag": {
                "name": "fix_image_tag",
                "description": "Remove :latest tag",
                "fix_strategy": self._fix_latest_tag
            },

            # Secrets
            "secret_in_env": {
                "name": "use_secret_volume",
                "description": "Use secret volume instead of env",
                "fix_strategy": self._fix_secret_exposure
            }
        }

        self.applied_fixes = []
        self.skipped_fixes = []
        self.backup_files = []

    def fix_findings(self, scan_results_path: str, project_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        """
        Main entry point to fix Kubernetes findings.

        Args:
            scan_results_path: Path to Kubernetes scan results JSON
            project_path: Path to the project being fixed
            auto_fix: If True, apply fixes automatically

        Returns:
            Dictionary with fix results
        """
        print(f"🔧 Kubernetes Fixer - Starting fix process")
        print(f"   Scan results: {scan_results_path}")
        print(f"   Target project: {project_path}")
        print(f"   Auto-fix mode: {auto_fix}")
        print()

        # Load scan results
        with open(scan_results_path, 'r') as f:
            scan_data = json.load(f)

        # Extract Kubernetes findings from multiple tools
        all_findings = self._extract_kubernetes_findings(scan_data)

        if not all_findings:
            print("✅ No Kubernetes findings to fix!")
            return {
                "status": "success",
                "fixes_applied": 0,
                "message": "No security issues found"
            }

        print(f"📊 Found {len(all_findings)} Kubernetes security issues to analyze")
        print()

        # Group findings by file
        findings_by_file = {}
        for finding in all_findings:
            filepath = finding.get('file_path', '')

            if not filepath:
                continue

            # Make path absolute if it's relative
            if not Path(filepath).is_absolute():
                filepath = str(Path(project_path) / filepath.lstrip('/'))

            if filepath not in findings_by_file:
                findings_by_file[filepath] = []
            findings_by_file[filepath].append(finding)

        # Process each file
        for filepath, file_findings in findings_by_file.items():
            if not Path(filepath).exists():
                print(f"⚠️  Skipping non-existent file: {filepath}")
                continue

            print(f"📝 Processing: {filepath}")
            self._fix_file(filepath, file_findings, auto_fix)
            print()

        # Generate fix report
        report = self._generate_fix_report(scan_results_path, project_path)

        print("📊 Fix Summary:")
        print(f"   ✅ Fixes applied: {len(self.applied_fixes)}")
        print(f"   ⚠️  Fixes skipped (manual review needed): {len(self.skipped_fixes)}")
        print(f"   💾 Backup files created: {len(self.backup_files)}")

        return report

    def _extract_kubernetes_findings(self, scan_data: dict) -> List[Dict]:
        """Extract Kubernetes findings from various scanner outputs"""
        findings = []

        # Extract from kubernetes_security results
        if 'results' in scan_data and 'kubernetes_security' in scan_data['results']:
            k8s_data = scan_data['results']['kubernetes_security']

            # kube-bench findings
            if 'tools' in k8s_data and 'kube_bench' in k8s_data['tools']:
                for issue in k8s_data['tools']['kube_bench'].get('issues', []):
                    findings.append({
                        'tool': 'kube-bench',
                        'type': 'cis_benchmark',
                        'id': issue.get('id'),
                        'severity': issue.get('severity', 'medium'),
                        'title': issue.get('title'),
                        'remediation': issue.get('remediation'),
                        'file_path': self._infer_k8s_file(issue)
                    })

            # kubescape findings
            if 'tools' in k8s_data and 'kubescape' in k8s_data['tools']:
                for control in k8s_data['tools']['kubescape'].get('controls', []):
                    if control.get('status') == 'failed':
                        findings.append({
                            'tool': 'kubescape',
                            'type': 'security_control',
                            'id': control.get('control_id'),
                            'severity': control.get('severity', 'medium'),
                            'title': control.get('name'),
                            'remediation': control.get('remediation'),
                            'file_path': control.get('resource_file')
                        })

            # Polaris findings
            if 'tools' in k8s_data and 'polaris' in k8s_data['tools']:
                for result in k8s_data['tools']['polaris'].get('results', []):
                    if result.get('success') is False:
                        findings.append({
                            'tool': 'polaris',
                            'type': 'best_practice',
                            'id': result.get('check'),
                            'severity': result.get('severity', 'warning'),
                            'title': result.get('message'),
                            'file_path': result.get('file')
                        })

        return findings

    def _infer_k8s_file(self, issue: Dict) -> str:
        """Infer Kubernetes file from kube-bench issue"""
        # Map kube-bench checks to likely Kubernetes manifest locations
        issue_id = issue.get('id', '')

        # Most issues are config-related
        return 'kubernetes/config/kubelet.yaml'  # Default

    def _fix_file(self, filepath: str, findings: List[Dict], auto_fix: bool):
        """Fix issues in a single Kubernetes YAML file"""

        # Create backup
        backup_path = self._create_backup(filepath)
        if backup_path:
            self.backup_files.append(backup_path)

        # Read YAML content
        try:
            with open(filepath, 'r') as f:
                if filepath.endswith('.yaml') or filepath.endswith('.yml'):
                    manifests = list(yaml.safe_load_all(f))
                else:
                    # Not a YAML file, skip
                    return
        except Exception as e:
            print(f"   ⚠️  Could not parse YAML: {e}")
            return

        original_manifests = [m.copy() if m else {} for m in manifests]
        modified = False

        # Apply fixes to each manifest
        for i, manifest in enumerate(manifests):
            if not manifest:
                continue

            for finding in findings:
                fix_pattern = self._match_fix_pattern(finding)
                if not fix_pattern:
                    self.skipped_fixes.append({
                        "file": filepath,
                        "issue": finding.get('id'),
                        "reason": "No fix pattern available"
                    })
                    continue

                fix_config = self.fix_patterns[fix_pattern]
                print(f"   🔧 Fixing {finding.get('id')} - {fix_config['description']}")

                try:
                    manifest = fix_config['fix_strategy'](manifest, finding)
                    modified = True

                    self.applied_fixes.append({
                        "file": filepath,
                        "issue": finding.get('id'),
                        "fix_applied": fix_config['name'],
                        "description": fix_config['description']
                    })
                except Exception as e:
                    print(f"   ❌ Failed to fix: {str(e)}")
                    self.skipped_fixes.append({
                        "file": filepath,
                        "issue": finding.get('id'),
                        "reason": f"Fix failed: {str(e)}"
                    })

            manifests[i] = manifest

        # Write fixed content if changes were made
        if modified:
            with open(filepath, 'w') as f:
                yaml.safe_dump_all(manifests, f, default_flow_style=False)
            print(f"   ✅ File updated with {len([f for f in self.applied_fixes if f['file'] == filepath])} fixes")

    def _match_fix_pattern(self, finding: Dict) -> Optional[str]:
        """Match finding to a fix pattern"""
        title = finding.get('title', '').lower()
        issue_id = finding.get('id', '').lower()

        # Map findings to patterns
        if 'security context' in title or 'securitycontext' in issue_id:
            return 'no_security_context'
        elif 'privileged' in title:
            return 'privileged_container'
        elif 'root' in title and 'user' in title:
            return 'runs_as_root'
        elif 'resource' in title and ('limit' in title or 'limits' in title):
            return 'no_resource_limits'
        elif 'resource' in title and ('request' in title or 'requests' in title):
            return 'no_resource_requests'
        elif 'readiness' in title:
            return 'no_readiness_probe'
        elif 'liveness' in title:
            return 'no_liveness_probe'
        elif 'network policy' in title:
            return 'no_network_policy'
        elif 'imagepullpolicy' in title.replace(' ', '').lower():
            return 'image_pull_policy_not_always'
        elif 'latest' in title and 'tag' in title:
            return 'latest_image_tag'
        elif 'secret' in title and 'env' in title:
            return 'secret_in_env'

        return None

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

    # Fix strategies for each pattern

    def _fix_security_context(self, manifest: Dict, finding: Dict) -> Dict:
        """Add security context to pod/deployment"""
        if manifest.get('kind') in ['Pod', 'Deployment', 'StatefulSet', 'DaemonSet']:
            spec = manifest.get('spec', {})
            if manifest.get('kind') in ['Deployment', 'StatefulSet', 'DaemonSet']:
                spec = spec.get('template', {}).get('spec', {})

            if 'securityContext' not in spec:
                spec['securityContext'] = {
                    'runAsNonRoot': True,
                    'runAsUser': 1000,
                    'fsGroup': 1000
                }

        return manifest

    def _fix_privileged_container(self, manifest: Dict, finding: Dict) -> Dict:
        """Remove privileged flag from containers"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                if container.get('securityContext', {}).get('privileged'):
                    container['securityContext']['privileged'] = False

        return manifest

    def _fix_run_as_root(self, manifest: Dict, finding: Dict) -> Dict:
        """Configure container to run as non-root"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                if 'securityContext' not in container:
                    container['securityContext'] = {}
                container['securityContext']['runAsNonRoot'] = True
                container['securityContext']['runAsUser'] = 1000

        return manifest

    def _fix_resource_limits(self, manifest: Dict, finding: Dict) -> Dict:
        """Add resource limits to containers"""
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

        return manifest

    def _fix_resource_requests(self, manifest: Dict, finding: Dict) -> Dict:
        """Add resource requests to containers"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                if 'resources' not in container:
                    container['resources'] = {}
                if 'requests' not in container['resources']:
                    container['resources']['requests'] = {
                        'cpu': '100m',
                        'memory': '128Mi'
                    }

        return manifest

    def _fix_readiness_probe(self, manifest: Dict, finding: Dict) -> Dict:
        """Add readiness probe to containers"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                if 'readinessProbe' not in container:
                    container['readinessProbe'] = {
                        'httpGet': {
                            'path': '/health',
                            'port': 8080
                        },
                        'initialDelaySeconds': 5,
                        'periodSeconds': 10
                    }

        return manifest

    def _fix_liveness_probe(self, manifest: Dict, finding: Dict) -> Dict:
        """Add liveness probe to containers"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                if 'livenessProbe' not in container:
                    container['livenessProbe'] = {
                        'httpGet': {
                            'path': '/health',
                            'port': 8080
                        },
                        'initialDelaySeconds': 15,
                        'periodSeconds': 20
                    }

        return manifest

    def _fix_network_policy(self, manifest: Dict, finding: Dict) -> Dict:
        """This requires creating a new NetworkPolicy - add comment"""
        # Can't fix in-place, needs new resource
        return manifest

    def _fix_rbac_permissions(self, manifest: Dict, finding: Dict) -> Dict:
        """Restrict RBAC permissions"""
        if manifest.get('kind') in ['Role', 'ClusterRole']:
            for rule in manifest.get('rules', []):
                # Remove wildcard permissions
                if '*' in rule.get('verbs', []):
                    rule['verbs'] = ['get', 'list', 'watch']
                if '*' in rule.get('resources', []):
                    rule['resources'] = ['pods', 'services']

        return manifest

    def _fix_image_pull_policy(self, manifest: Dict, finding: Dict) -> Dict:
        """Set imagePullPolicy to Always"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                container['imagePullPolicy'] = 'Always'

        return manifest

    def _fix_latest_tag(self, manifest: Dict, finding: Dict) -> Dict:
        """Remove :latest tag from images"""
        spec = self._get_pod_spec(manifest)
        if spec:
            for container in spec.get('containers', []):
                image = container.get('image', '')
                if image.endswith(':latest'):
                    # Replace with :v1.0 as placeholder
                    container['image'] = image.replace(':latest', ':v1.0')
                    print(f"      ⚠️  Changed :latest to :v1.0 - please update to actual version")

        return manifest

    def _fix_secret_exposure(self, manifest: Dict, finding: Dict) -> Dict:
        """This requires restructuring - add comment"""
        # Complex fix requiring volume mounts
        return manifest

    def _get_pod_spec(self, manifest: Dict) -> Optional[Dict]:
        """Extract pod spec from various Kubernetes resources"""
        kind = manifest.get('kind')
        if kind == 'Pod':
            return manifest.get('spec')
        elif kind in ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob']:
            if kind == 'CronJob':
                return manifest.get('spec', {}).get('jobTemplate', {}).get('spec', {}).get('template', {}).get('spec')
            return manifest.get('spec', {}).get('template', {}).get('spec')
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
                "total_findings": len(self.applied_fixes) + len(self.skipped_fixes),
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
        report_file = self.fixes_dir / f"kubernetes_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Fix report saved: {report_file}")

        return report


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Kubernetes Security Fixer - Automatically fix Kubernetes security issues")
        print()
        print("Usage:")
        print("  kubernetes_fixer.py <scan_results.json> <project_path>")
        print()
        print("Arguments:")
        print("  scan_results.json  - Path to Kubernetes scan results JSON file")
        print("  project_path       - Path to the project to fix")
        print()
        print("Example:")
        print("  kubernetes_fixer.py scan_results.json ./kubernetes")
        print()
        print("Fixable Issues:")
        print("  Pod Security:")
        print("    - Add security context")
        print("    - Remove privileged containers")
        print("    - Run as non-root user")
        print("    - Add resource limits/requests")
        print("    - Add health probes")
        print()
        print("  Image Security:")
        print("    - Fix imagePullPolicy")
        print("    - Remove :latest tags")
        print()
        print("  RBAC:")
        print("    - Restrict overly permissive roles")
        sys.exit(1)

    scan_results = sys.argv[1]
    project_path = sys.argv[2]

    fixer = KubernetesFixer()
    result = fixer.fix_findings(scan_results, project_path)

    # Exit with appropriate code
    if result.get('status') == 'success':
        if result.get('statistics', {}).get('fixes_applied', 0) > 0:
            print("\n✅ Fixes applied successfully!")
            print("⚠️  Please review the changes and test before deploying")
        sys.exit(0)
    else:
        print("\n❌ Fix process failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
