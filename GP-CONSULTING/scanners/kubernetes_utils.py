#!/usr/bin/env python3
"""
Kubernetes Utilities - Shared logic for K8s security scanners
Provides manifest detection and validation utilities
"""

import yaml
from pathlib import Path
from typing import List, Dict, Optional

class KubernetesDetector:
    """Utility class for Kubernetes manifest detection and analysis"""

    K8S_KINDS = [
        'Deployment', 'Service', 'ConfigMap', 'Secret', 'Pod',
        'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'Ingress',
        'NetworkPolicy', 'ServiceAccount', 'Role', 'RoleBinding',
        'ClusterRole', 'ClusterRoleBinding', 'PersistentVolume',
        'PersistentVolumeClaim', 'StorageClass', 'Namespace',
        'HorizontalPodAutoscaler', 'VerticalPodAutoscaler',
        'PodDisruptionBudget', 'LimitRange', 'ResourceQuota'
    ]

    @staticmethod
    def find_k8s_manifests(target_path: Path) -> List[Path]:
        """
        Find all Kubernetes YAML manifests in target directory

        Args:
            target_path: Directory to search for manifests

        Returns:
            List of Path objects to Kubernetes manifest files
        """
        manifests = []
        patterns = ['*.yaml', '*.yml']

        if not target_path.exists():
            return manifests

        for pattern in patterns:
            for file_path in target_path.rglob(pattern):
                try:
                    if KubernetesDetector.is_k8s_manifest(file_path):
                        manifests.append(file_path)
                except Exception:
                    # Skip files that can't be parsed
                    continue

        return manifests

    @staticmethod
    def is_k8s_manifest(file_path: Path) -> bool:
        """
        Check if file is a Kubernetes manifest

        Args:
            file_path: Path to YAML file to check

        Returns:
            True if file contains Kubernetes resources
        """
        try:
            with open(file_path, 'r') as f:
                # Handle multi-document YAML files
                documents = list(yaml.safe_load_all(f))

                for doc in documents:
                    if doc and isinstance(doc, dict):
                        kind = doc.get('kind')
                        api_version = doc.get('apiVersion')

                        # Must have both kind and apiVersion to be K8s manifest
                        if kind in KubernetesDetector.K8S_KINDS and api_version:
                            return True

        except (yaml.YAMLError, IOError, UnicodeDecodeError):
            # Not a valid YAML file or not readable
            return False
        except Exception:
            # Catch-all for unexpected errors
            return False

        return False

    @staticmethod
    def get_manifest_summary(target_path: Path) -> Dict:
        """
        Get summary of Kubernetes manifests in target

        Args:
            target_path: Directory to analyze

        Returns:
            Dictionary with manifest statistics
        """
        manifests = KubernetesDetector.find_k8s_manifests(target_path)

        # Count by kind
        kind_counts = {}
        total_resources = 0

        for manifest in manifests:
            try:
                with open(manifest, 'r') as f:
                    documents = list(yaml.safe_load_all(f))

                    for doc in documents:
                        if doc and isinstance(doc, dict):
                            kind = doc.get('kind')
                            if kind in KubernetesDetector.K8S_KINDS:
                                total_resources += 1
                                if kind not in kind_counts:
                                    kind_counts[kind] = 0
                                kind_counts[kind] += 1
            except Exception:
                continue

        return {
            "total_manifest_files": len(manifests),
            "total_k8s_resources": total_resources,
            "resource_types": kind_counts,
            "manifest_files": [str(m.relative_to(target_path)) for m in manifests]
        }

    @staticmethod
    def extract_namespaces(target_path: Path) -> List[str]:
        """
        Extract all namespaces referenced in manifests

        Args:
            target_path: Directory containing manifests

        Returns:
            List of unique namespace names
        """
        namespaces = set()
        manifests = KubernetesDetector.find_k8s_manifests(target_path)

        for manifest in manifests:
            try:
                with open(manifest, 'r') as f:
                    documents = list(yaml.safe_load_all(f))

                    for doc in documents:
                        if doc and isinstance(doc, dict):
                            # Check for namespace in metadata
                            metadata = doc.get('metadata', {})
                            if 'namespace' in metadata:
                                namespaces.add(metadata['namespace'])

                            # Check if this IS a Namespace resource
                            if doc.get('kind') == 'Namespace':
                                name = metadata.get('name')
                                if name:
                                    namespaces.add(name)
            except Exception:
                continue

        return sorted(list(namespaces))


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python kubernetes_utils.py <target_path>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if not target.exists():
        print(f"Error: {target} does not exist")
        sys.exit(1)

    # Get summary
    summary = KubernetesDetector.get_manifest_summary(target)
    namespaces = KubernetesDetector.extract_namespaces(target)

    print(f"📋 Kubernetes Manifest Summary for {target}")
    print(f"   Total manifest files: {summary['total_manifest_files']}")
    print(f"   Total K8s resources: {summary['total_k8s_resources']}")
    print(f"\n📦 Resource Types:")
    for kind, count in sorted(summary['resource_types'].items()):
        print(f"   {kind}: {count}")

    if namespaces:
        print(f"\n🏷️  Namespaces found: {', '.join(namespaces)}")