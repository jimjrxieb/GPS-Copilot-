#!/usr/bin/env python3
"""
OPA Cluster Manager for GP-Copilot/Jade
Manages Gatekeeper deployment and validation in live Kubernetes clusters

This is what makes Jade operational - it can deploy and validate
policies in real clusters.
"""

import subprocess
import json
import yaml
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

class OpaClusterManager:
    """Manages Gatekeeper policies in Kubernetes clusters"""

    def __init__(self):
        self.kubectl_available = self._check_kubectl()
        self.gatekeeper_namespace = "gatekeeper-system"

    def _check_kubectl(self) -> bool:
        """Check if kubectl is available and configured"""
        try:
            result = subprocess.run(
                ['kubectl', 'version', '--short'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def install_gatekeeper(self) -> bool:
        """Install Gatekeeper in the cluster"""
        if not self.kubectl_available:
            print("❌ kubectl not configured. Cannot install Gatekeeper.")
            return False

        print("🚀 Installing Gatekeeper v3.14.0...")

        install_url = "https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.14.0/deploy/gatekeeper.yaml"

        try:
            result = subprocess.run(
                ['kubectl', 'apply', '-f', install_url],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("✅ Gatekeeper installed successfully")
                time.sleep(10)  # Wait for pods to start
                return self._verify_gatekeeper_ready()
            else:
                print(f"❌ Failed to install Gatekeeper: {result.stderr}")
                return False

        except subprocess.SubprocessError as e:
            print(f"❌ Error installing Gatekeeper: {e}")
            return False

    def _verify_gatekeeper_ready(self) -> bool:
        """Verify Gatekeeper pods are running"""
        try:
            result = subprocess.run(
                ['kubectl', 'get', 'pods', '-n', self.gatekeeper_namespace],
                capture_output=True,
                text=True
            )

            if "Running" in result.stdout:
                print("✅ Gatekeeper pods are running")
                return True
            else:
                print("⏳ Gatekeeper pods not ready yet")
                return False

        except subprocess.SubprocessError:
            return False

    def deploy_policies(self, policies: List[str]) -> Dict[str, Any]:
        """Deploy generated policies to Gatekeeper"""
        if not self.kubectl_available:
            return {"error": "kubectl not configured"}

        results = {
            "deployed": [],
            "failed": [],
            "total": len(policies)
        }

        for policy_file in policies:
            print(f"📄 Deploying: {policy_file}")

            try:
                result = subprocess.run(
                    ['kubectl', 'apply', '-f', policy_file],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    results["deployed"].append(policy_file)
                    print(f"   ✅ Deployed successfully")
                else:
                    results["failed"].append({
                        "file": policy_file,
                        "error": result.stderr
                    })
                    print(f"   ❌ Failed: {result.stderr}")

            except subprocess.SubprocessError as e:
                results["failed"].append({
                    "file": policy_file,
                    "error": str(e)
                })

        print(f"\n📊 Deployment Summary:")
        print(f"   ✅ Deployed: {len(results['deployed'])}/{results['total']}")
        print(f"   ❌ Failed: {len(results['failed'])}/{results['total']}")

        return results

    def validate_enforcement(self, test_manifest: str = None) -> Dict[str, Any]:
        """Check if policies are actually blocking violations"""
        if not self.kubectl_available:
            return {"error": "kubectl not configured"}

        # Use provided manifest or create a violating one
        if not test_manifest:
            test_manifest = self._create_test_violation()

        print("🧪 Testing policy enforcement...")

        try:
            # Try to create violating resource with dry-run
            result = subprocess.run(
                ['kubectl', 'apply', '-f', test_manifest, '--dry-run=server'],
                capture_output=True,
                text=True
            )

            if "denied" in result.stderr.lower():
                # Policy is working - violation was blocked
                violations = self._parse_violations(result.stderr)
                print("✅ Policies are enforcing correctly!")
                return {
                    "status": "enforcing",
                    "violations_blocked": violations
                }
            else:
                # Policy not blocking - might not be active
                print("⚠️  Policies may not be enforcing")
                return {
                    "status": "not_enforcing",
                    "output": result.stdout
                }

        except subprocess.SubprocessError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _create_test_violation(self) -> str:
        """Create a test manifest with violations"""
        violation_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': 'test-violation',
                'namespace': 'default'
            },
            'spec': {
                'containers': [{
                    'name': 'test',
                    'image': 'nginx',
                    'securityContext': {
                        'privileged': True,  # Violation
                        'runAsUser': 0  # Violation
                    }
                }],
                'hostNetwork': True  # Violation
            }
        }

        test_file = Path("/tmp/test-violation.yaml")
        with open(test_file, 'w') as f:
            yaml.dump(violation_manifest, f)

        return str(test_file)

    def _parse_violations(self, error_output: str) -> List[str]:
        """Parse Gatekeeper violation messages from kubectl output"""
        violations = []
        lines = error_output.split('\n')

        for line in lines:
            if 'denied' in line.lower() or 'violation' in line.lower():
                violations.append(line.strip())

        return violations

    def get_constraints(self) -> List[Dict]:
        """Get all active Gatekeeper constraints"""
        if not self.kubectl_available:
            return []

        try:
            # Get all constraint templates
            result = subprocess.run(
                ['kubectl', 'get', 'constrainttemplates', '-o', 'json'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                templates = json.loads(result.stdout)
                return templates.get('items', [])
            else:
                return []

        except (subprocess.SubprocessError, json.JSONDecodeError):
            return []

    def get_violations(self) -> List[Dict]:
        """Get current policy violations from Gatekeeper"""
        if not self.kubectl_available:
            return []

        try:
            # Get audit logs from Gatekeeper
            result = subprocess.run(
                ['kubectl', 'logs', '-n', self.gatekeeper_namespace,
                 'deployment/gatekeeper-audit', '--tail=100'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Parse violation logs
                violations = []
                for line in result.stdout.split('\n'):
                    if 'violation' in line.lower():
                        violations.append(line)
                return violations
            else:
                return []

        except subprocess.SubprocessError:
            return []

    def test_policy(self, policy_file: str, test_manifests: List[str]) -> Dict[str, Any]:
        """Test a policy against known manifests before deployment"""
        results = {
            "policy": policy_file,
            "tests": []
        }

        # Deploy policy in dry-run mode first
        print(f"🧪 Testing policy: {policy_file}")

        for manifest in test_manifests:
            try:
                # Apply manifest with dry-run to see if it would be blocked
                result = subprocess.run(
                    ['kubectl', 'apply', '-f', manifest, '--dry-run=server'],
                    capture_output=True,
                    text=True
                )

                test_result = {
                    "manifest": manifest,
                    "blocked": "denied" in result.stderr.lower(),
                    "message": result.stderr if result.stderr else result.stdout
                }

                results["tests"].append(test_result)

            except subprocess.SubprocessError as e:
                results["tests"].append({
                    "manifest": manifest,
                    "error": str(e)
                })

        return results


def main():
    """Test the cluster manager"""
    manager = OpaClusterManager()

    print("🛡️  OPA Cluster Manager Test")
    print("=" * 40)

    # Check kubectl
    if manager.kubectl_available:
        print("✅ kubectl is configured")

        # Check Gatekeeper
        if manager._verify_gatekeeper_ready():
            print("✅ Gatekeeper is running")

            # Get active constraints
            constraints = manager.get_constraints()
            print(f"📋 Active constraint templates: {len(constraints)}")

            # Test enforcement
            validation = manager.validate_enforcement()
            print(f"🧪 Enforcement status: {validation.get('status')}")

        else:
            print("❌ Gatekeeper not running")
            print("   Run: manager.install_gatekeeper()")

    else:
        print("❌ kubectl not configured")
        print("   Configure kubectl to connect to a cluster")


if __name__ == "__main__":
    main()