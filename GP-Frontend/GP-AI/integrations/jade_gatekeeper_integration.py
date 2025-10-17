#!/usr/bin/env python3
"""
Jade Gatekeeper Integration
Makes Jade capable of generating and deploying Gatekeeper policies

This is the intelligence layer that connects Jade to Kubernetes
admission control via Gatekeeper.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add GP-CONSULTING-AGENTS to path
sys.path.insert(0, "/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS")

from generators.opa_policy_generator import OpaPolicyGenerator
from managers.opa_cluster_manager import OpaClusterManager
from scanners.opa_scanner import OpaScanner

class JadeGatekeeperIntegration:
    """Jade's Gatekeeper capabilities for intelligent policy management"""

    def __init__(self):
        self.scanner = OpaScanner()
        self.generator = OpaPolicyGenerator()
        self.manager = OpaClusterManager()
        self.workflow_dir = Path("/home/jimmie/linkops-industries/GP-copilot/GP-CONSULTING-AGENTS/workflows")

    def full_workflow(self, target: str) -> Dict[str, Any]:
        """
        Jade's complete Gatekeeper workflow:
        1. Scan for violations
        2. Generate preventive policies
        3. Test policies
        4. Deploy to cluster
        5. Validate enforcement
        """
        print("🤖 Jade: Starting Gatekeeper workflow")
        print("=" * 50)

        workflow_results = {
            "target": target,
            "steps": {}
        }

        # Step 1: Scan for violations
        print("\n📍 Step 1: Scanning for security violations...")
        scan_results = self.scanner.scan(target)

        if not scan_results:
            print("❌ Scan failed")
            workflow_results["steps"]["scan"] = {"status": "failed"}
            return workflow_results

        violations_found = len(scan_results.get('findings', []))
        print(f"   Found {violations_found} violations")
        workflow_results["steps"]["scan"] = {
            "status": "completed",
            "violations": violations_found
        }

        # Step 2: Generate preventive policies
        print("\n📍 Step 2: Generating Gatekeeper policies...")
        policies = self.generator.generate_from_violations(scan_results)

        if not policies:
            print("   No policies generated (no violations found)")
            workflow_results["steps"]["generate"] = {"status": "skipped"}
        else:
            print(f"   Generated {len(policies)} policies")
            for policy in policies:
                print(f"      📄 {Path(policy).name}")

            workflow_results["steps"]["generate"] = {
                "status": "completed",
                "policies": policies
            }

        # Step 3: Test policies (if kubectl available)
        if self.manager.kubectl_available:
            print("\n📍 Step 3: Testing policies...")

            # Create test manifests
            test_manifests = self._create_test_manifests()
            test_results = []

            for policy in policies:
                result = self.manager.test_policy(policy, test_manifests)
                test_results.append(result)

            workflow_results["steps"]["test"] = {
                "status": "completed",
                "results": test_results
            }

            # Step 4: Deploy to cluster
            print("\n📍 Step 4: Deploying to cluster...")
            deploy_results = self.manager.deploy_policies(policies)

            workflow_results["steps"]["deploy"] = {
                "status": "completed" if deploy_results["deployed"] else "failed",
                "deployed": len(deploy_results["deployed"]),
                "failed": len(deploy_results["failed"])
            }

            # Step 5: Validate enforcement
            print("\n📍 Step 5: Validating enforcement...")
            validation = self.manager.validate_enforcement()

            workflow_results["steps"]["validate"] = {
                "status": validation.get("status"),
                "violations_blocked": validation.get("violations_blocked", [])
            }

        else:
            print("\n⚠️  kubectl not configured - skipping cluster operations")
            workflow_results["steps"]["test"] = {"status": "skipped"}
            workflow_results["steps"]["deploy"] = {"status": "skipped"}
            workflow_results["steps"]["validate"] = {"status": "skipped"}

        # Summary
        print("\n" + "=" * 50)
        print("📊 Workflow Summary:")
        for step, result in workflow_results["steps"].items():
            status = result.get("status", "unknown")
            icon = "✅" if status == "completed" else "⏭️" if status == "skipped" else "❌"
            print(f"   {icon} {step}: {status}")

        return workflow_results

    def _create_test_manifests(self) -> List[str]:
        """Create test manifests for policy validation"""
        test_dir = Path("/tmp/jade-test-manifests")
        test_dir.mkdir(exist_ok=True)

        # Good manifest (should pass)
        good_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': 'compliant-pod',
                'labels': {
                    'owner': 'jade',
                    'cost-center': 'security',
                    'data-classification': 'internal'
                }
            },
            'spec': {
                'securityContext': {
                    'runAsUser': 1000,
                    'runAsNonRoot': True
                },
                'containers': [{
                    'name': 'app',
                    'image': 'nginx:1.24',
                    'securityContext': {
                        'allowPrivilegeEscalation': False,
                        'readOnlyRootFilesystem': True
                    },
                    'resources': {
                        'limits': {
                            'memory': '128Mi',
                            'cpu': '100m'
                        }
                    }
                }]
            }
        }

        # Bad manifest (should fail)
        bad_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': 'violating-pod'
            },
            'spec': {
                'containers': [{
                    'name': 'app',
                    'image': 'nginx',
                    'securityContext': {
                        'privileged': True,
                        'runAsUser': 0
                    }
                }],
                'hostNetwork': True
            }
        }

        import yaml

        good_file = test_dir / "compliant.yaml"
        with open(good_file, 'w') as f:
            yaml.dump(good_manifest, f)

        bad_file = test_dir / "violating.yaml"
        with open(bad_file, 'w') as f:
            yaml.dump(bad_manifest, f)

        return [str(good_file), str(bad_file)]

    def explain_to_jr_engineer(self):
        """Explain the workflow to a Jr Cloud Security Engineer"""
        explanation = """
🎓 JADE'S GATEKEEPER WORKFLOW EXPLAINED

As a Jr Cloud Security Engineer, here's what Jade does for you:

1️⃣ **SCANNING** (What you'd do manually)
   Manual: kubectl get pods -A -o yaml | grep "privileged: true"
   Jade: Automatically scans all manifests for 27+ security violations

2️⃣ **POLICY GENERATION** (What takes hours)
   Manual: Write ConstraintTemplates in Rego for each violation type
   Jade: Generates them automatically based on violations found

3️⃣ **TESTING** (What often gets skipped)
   Manual: kubectl apply --dry-run=server for each test case
   Jade: Tests policies against known good/bad manifests

4️⃣ **DEPLOYMENT** (What's error-prone)
   Manual: kubectl apply -f each-policy.yaml one by one
   Jade: Deploys all policies with rollback capability

5️⃣ **VALIDATION** (What confirms it works)
   Manual: Try to deploy violating pods to see if they're blocked
   Jade: Automatically validates enforcement is active

THE KEY DIFFERENCE:
- Jr Engineer: Manually writes and applies policies
- Jade: Learns from violations and generates preventive policies

YOUR INTERVIEW ANSWER:
"I understand both the manual process of creating ConstraintTemplates
and the automation potential. I can write Rego policies by hand, but
I've also built tooling to generate them from scan results."
        """
        return explanation


def main():
    """Demonstrate Jade's Gatekeeper capabilities"""
    print("🤖 JADE GATEKEEPER INTEGRATION")
    print("=" * 50)

    jade = JadeGatekeeperIntegration()

    # Show explanation for interview
    print(jade.explain_to_jr_engineer())

    # Test with interview demo if requested
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', default='/home/jimmie/linkops-industries/GP-copilot/GP-PROJECTS/INTERVIEW-DEMO')
    parser.add_argument('--run-workflow', action='store_true')
    args = parser.parse_args()

    if args.run_workflow:
        print("\n🚀 Running full workflow...")
        results = jade.full_workflow(args.target)

        # Save results
        results_file = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/workflows/jade_gatekeeper_results.json")
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {results_file}")


if __name__ == "__main__":
    main()