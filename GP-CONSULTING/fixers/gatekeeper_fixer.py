#!/usr/bin/env python3
"""
Gatekeeper Fixer - Automatically fixes violations detected by Gatekeeper
This fixer takes Gatekeeper denial messages and applies fixes to manifests

Workflow:
1. Gatekeeper denies admission → provides specific violation message
2. This fixer parses the violation → determines the fix needed
3. Applies the fix to the manifest → makes it compliant
"""

import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

class GatekeeperFixer:
    """Automatically fixes Kubernetes manifests based on Gatekeeper violations"""

    def __init__(self):
        self.fixes_applied = []
        self.fix_mappings = {
            'runAsNonRoot': self._fix_run_as_non_root,
            'privileged': self._fix_privileged,
            'resource limits': self._fix_resource_limits,
            'required label': self._fix_missing_labels,
            'hostNetwork': self._fix_host_network,
            'allowPrivilegeEscalation': self._fix_privilege_escalation,
            'readOnlyRootFilesystem': self._fix_readonly_filesystem,
            'capabilities': self._fix_capabilities,
            'seccompProfile': self._fix_seccomp_profile,
            'runAsUser': self._fix_run_as_user
        }

    def fix_from_gatekeeper_denial(self, denial_message: str, manifest_path: str) -> Dict[str, Any]:
        """
        Parse Gatekeeper denial and fix the manifest

        Example denial:
        "Container nginx must set runAsNonRoot"
        "Container app cannot run in privileged mode"
        "Resource missing required label: owner"
        """

        # Load the manifest
        with open(manifest_path, 'r') as f:
            manifest = yaml.safe_load(f)

        original_manifest = yaml.dump(manifest)

        # Parse the denial message and apply fixes
        fixes_needed = self._parse_denial_message(denial_message)

        for fix_type, details in fixes_needed.items():
            if fix_type in self.fix_mappings:
                manifest = self.fix_mappings[fix_type](manifest, details)
                self.fixes_applied.append({
                    'type': fix_type,
                    'details': details,
                    'manifest': manifest_path
                })

        # Save fixed manifest
        fixed_path = Path(manifest_path).parent / f"fixed_{Path(manifest_path).name}"
        with open(fixed_path, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)

        return {
            'original_manifest': original_manifest,
            'fixed_manifest': yaml.dump(manifest),
            'fixed_file': str(fixed_path),
            'fixes_applied': self.fixes_applied
        }

    def _parse_denial_message(self, message: str) -> Dict[str, Any]:
        """Parse Gatekeeper denial message to identify needed fixes"""
        fixes = {}

        # Check for common violation patterns
        if 'runAsNonRoot' in message:
            container_match = re.search(r'Container (\S+)', message)
            fixes['runAsNonRoot'] = {
                'container': container_match.group(1) if container_match else None
            }

        if 'privileged' in message:
            container_match = re.search(r'Container (\S+)', message)
            fixes['privileged'] = {
                'container': container_match.group(1) if container_match else None
            }

        if 'resource limits' in message or 'must specify' in message:
            if 'memory' in message or 'cpu' in message:
                container_match = re.search(r'Container (\S+)', message)
                fixes['resource limits'] = {
                    'container': container_match.group(1) if container_match else None,
                    'resource': 'both'  # Fix both CPU and memory
                }

        if 'required label' in message:
            label_match = re.search(r'label: (\S+)', message)
            fixes['required label'] = {
                'label': label_match.group(1) if label_match else 'owner'
            }

        if 'hostNetwork' in message:
            fixes['hostNetwork'] = {}

        if 'allowPrivilegeEscalation' in message:
            container_match = re.search(r'Container (\S+)', message)
            fixes['allowPrivilegeEscalation'] = {
                'container': container_match.group(1) if container_match else None
            }

        if 'readOnlyRootFilesystem' in message:
            container_match = re.search(r'Container (\S+)', message)
            fixes['readOnlyRootFilesystem'] = {
                'container': container_match.group(1) if container_match else None
            }

        if 'runAsUser' in message and 'root' in message:
            fixes['runAsUser'] = {}

        return fixes

    def _fix_run_as_non_root(self, manifest: Dict, details: Dict) -> Dict:
        """Fix runAsNonRoot violation"""
        container_name = details.get('container')

        # Ensure spec exists
        if 'spec' not in manifest:
            manifest['spec'] = {}

        # Add pod-level securityContext if not exists
        if 'securityContext' not in manifest['spec']:
            manifest['spec']['securityContext'] = {}

        # Set runAsNonRoot at pod level
        manifest['spec']['securityContext']['runAsNonRoot'] = True
        manifest['spec']['securityContext']['runAsUser'] = 1000
        manifest['spec']['securityContext']['runAsGroup'] = 3000
        manifest['spec']['securityContext']['fsGroup'] = 2000

        # Also fix specific container if mentioned
        if container_name and 'containers' in manifest['spec']:
            for container in manifest['spec']['containers']:
                if container.get('name') == container_name or container_name is None:
                    if 'securityContext' not in container:
                        container['securityContext'] = {}
                    container['securityContext']['runAsNonRoot'] = True
                    container['securityContext']['runAsUser'] = 1000

        return manifest

    def _fix_privileged(self, manifest: Dict, details: Dict) -> Dict:
        """Fix privileged container violation"""
        container_name = details.get('container')

        if 'containers' in manifest.get('spec', {}):
            for container in manifest['spec']['containers']:
                if container.get('name') == container_name or container_name is None:
                    if 'securityContext' not in container:
                        container['securityContext'] = {}
                    container['securityContext']['privileged'] = False
                    container['securityContext']['allowPrivilegeEscalation'] = False

        return manifest

    def _fix_resource_limits(self, manifest: Dict, details: Dict) -> Dict:
        """Add resource limits to containers"""
        container_name = details.get('container')

        default_limits = {
            'limits': {
                'memory': '256Mi',
                'cpu': '500m'
            },
            'requests': {
                'memory': '128Mi',
                'cpu': '100m'
            }
        }

        if 'containers' in manifest.get('spec', {}):
            for container in manifest['spec']['containers']:
                if container.get('name') == container_name or container_name is None:
                    if 'resources' not in container:
                        container['resources'] = default_limits
                    else:
                        # Merge with existing resources
                        if 'limits' not in container['resources']:
                            container['resources']['limits'] = default_limits['limits']
                        if 'requests' not in container['resources']:
                            container['resources']['requests'] = default_limits['requests']

        return manifest

    def _fix_missing_labels(self, manifest: Dict, details: Dict) -> Dict:
        """Add required compliance labels"""
        label_name = details.get('label', 'owner')

        if 'metadata' not in manifest:
            manifest['metadata'] = {}

        if 'labels' not in manifest['metadata']:
            manifest['metadata']['labels'] = {}

        # Add standard compliance labels
        default_labels = {
            'owner': 'platform-team',
            'cost-center': 'engineering',
            'data-classification': 'internal',
            'environment': 'production',
            'managed-by': 'gatekeeper-fixer'
        }

        if label_name in default_labels:
            manifest['metadata']['labels'][label_name] = default_labels[label_name]

        return manifest

    def _fix_host_network(self, manifest: Dict, details: Dict) -> Dict:
        """Remove host network access"""
        if 'spec' in manifest:
            manifest['spec']['hostNetwork'] = False
            manifest['spec']['hostPID'] = False
            manifest['spec']['hostIPC'] = False

        return manifest

    def _fix_privilege_escalation(self, manifest: Dict, details: Dict) -> Dict:
        """Disable privilege escalation"""
        container_name = details.get('container')

        if 'containers' in manifest.get('spec', {}):
            for container in manifest['spec']['containers']:
                if container.get('name') == container_name or container_name is None:
                    if 'securityContext' not in container:
                        container['securityContext'] = {}
                    container['securityContext']['allowPrivilegeEscalation'] = False

        return manifest

    def _fix_readonly_filesystem(self, manifest: Dict, details: Dict) -> Dict:
        """Set filesystem to read-only"""
        container_name = details.get('container')

        if 'containers' in manifest.get('spec', {}):
            for container in manifest['spec']['containers']:
                if container.get('name') == container_name or container_name is None:
                    if 'securityContext' not in container:
                        container['securityContext'] = {}
                    container['securityContext']['readOnlyRootFilesystem'] = True

                    # Add emptyDir volumes for writable paths
                    if 'volumeMounts' not in container:
                        container['volumeMounts'] = []

                    # Add common writable directories
                    writable_dirs = ['/tmp', '/var/cache', '/var/run']
                    for dir_path in writable_dirs:
                        volume_name = dir_path.replace('/', '-').strip('-')
                        container['volumeMounts'].append({
                            'name': volume_name,
                            'mountPath': dir_path
                        })

                        # Add corresponding volume
                        if 'volumes' not in manifest['spec']:
                            manifest['spec']['volumes'] = []

                        if not any(v.get('name') == volume_name for v in manifest['spec']['volumes']):
                            manifest['spec']['volumes'].append({
                                'name': volume_name,
                                'emptyDir': {}
                            })

        return manifest

    def _fix_capabilities(self, manifest: Dict, details: Dict) -> Dict:
        """Drop dangerous capabilities"""
        container_name = details.get('container')

        if 'containers' in manifest.get('spec', {}):
            for container in manifest['spec']['containers']:
                if container.get('name') == container_name or container_name is None:
                    if 'securityContext' not in container:
                        container['securityContext'] = {}

                    # Drop all capabilities and only add what's needed
                    container['securityContext']['capabilities'] = {
                        'drop': ['ALL'],
                        'add': []  # Add specific capabilities only if needed
                    }

        return manifest

    def _fix_seccomp_profile(self, manifest: Dict, details: Dict) -> Dict:
        """Add seccomp profile"""
        container_name = details.get('container')

        # Add pod-level seccomp
        if 'spec' not in manifest:
            manifest['spec'] = {}
        if 'securityContext' not in manifest['spec']:
            manifest['spec']['securityContext'] = {}

        manifest['spec']['securityContext']['seccompProfile'] = {
            'type': 'RuntimeDefault'
        }

        # Add container-level seccomp
        if 'containers' in manifest['spec']:
            for container in manifest['spec']['containers']:
                if container.get('name') == container_name or container_name is None:
                    if 'securityContext' not in container:
                        container['securityContext'] = {}
                    container['securityContext']['seccompProfile'] = {
                        'type': 'RuntimeDefault'
                    }

        return manifest

    def _fix_run_as_user(self, manifest: Dict, details: Dict) -> Dict:
        """Fix running as root user"""
        # Set non-root user ID
        if 'spec' not in manifest:
            manifest['spec'] = {}
        if 'securityContext' not in manifest['spec']:
            manifest['spec']['securityContext'] = {}

        manifest['spec']['securityContext']['runAsUser'] = 1000
        manifest['spec']['securityContext']['runAsGroup'] = 3000

        return manifest

    def batch_fix(self, violations: List[Dict[str, str]]) -> List[Dict]:
        """Fix multiple violations from Gatekeeper audit"""
        results = []

        for violation in violations:
            denial_message = violation.get('message', '')
            manifest_path = violation.get('manifest', '')

            if denial_message and manifest_path:
                fix_result = self.fix_from_gatekeeper_denial(denial_message, manifest_path)
                results.append(fix_result)

        return results


def main():
    """Test the Gatekeeper fixer"""
    fixer = GatekeeperFixer()

    # Example Gatekeeper denial messages
    test_denials = [
        "Container nginx must set runAsNonRoot",
        "Container app cannot run in privileged mode",
        "Container web must specify memory limits",
        "Resource missing required label: owner",
        "Pod cannot use hostNetwork",
        "Container app must set allowPrivilegeEscalation to false",
        "Container nginx must have readOnlyRootFilesystem"
    ]

    print("🔧 Gatekeeper Fixer - Automatic Violation Resolution")
    print("=" * 50)

    for denial in test_denials:
        print(f"\n📍 Denial: {denial}")
        fixes = fixer._parse_denial_message(denial)
        print(f"   Fixes identified: {list(fixes.keys())}")

    print("\n✅ Fixer ready to automatically resolve Gatekeeper violations!")


if __name__ == "__main__":
    main()