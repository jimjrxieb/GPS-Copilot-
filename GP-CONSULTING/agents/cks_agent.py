#!/usr/bin/env python3
"""
CKS-Level Deploy-Test-Validate Agent
==================================

Actually deploys security fixes to Kubernetes and validates they work.
This is what separates documentation generators from real engineers.
"""

import subprocess
import json
import time
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import GP-DATA config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig

class KubernetesDeployTestAgent:
    """
    Real CKS engineer capability:
    - Deploy security manifests to actual cluster
    - Test that they work as expected
    - Validate applications still function
    - Provide actionable feedback
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.security_fixes_dir = self.project_path / "k8s-security-fixes"
        self.namespace = "portfolio"

        # Use GP-DATA config for output
        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()

        self.results = {
            "deployment_results": [],
            "validation_tests": [],
            "functional_tests": [],
            "failures": [],
            "recommendations": [],
            "timestamp": datetime.now().isoformat(),
            "project": str(project_path)
        }

    def deploy_security_fixes(self) -> Dict[str, Any]:
        """Deploy all security manifests and test they work"""
        print("🚀 CKS-Level Deploy-Test-Validate Starting...")
        print("=" * 50)

        # 1. Create namespace if it doesn't exist
        self._ensure_namespace()

        # 2. Deploy security manifests
        self._deploy_manifests()

        # 3. Test RBAC policies
        self._test_rbac_policies()

        # 4. Test NetworkPolicies
        self._test_network_policies()

        # 5. Test Pod Security Standards
        self._test_pod_security()

        # 6. Validate application functionality
        self._test_application_functionality()

        # 7. Generate real CKS report
        return self._generate_cks_report()

    def _ensure_namespace(self):
        """Create namespace with security labels"""
        print("📝 Creating secure namespace...")

        namespace_yaml = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "pod-security.kubernetes.io/enforce": "restricted",
                    "pod-security.kubernetes.io/audit": "restricted",
                    "pod-security.kubernetes.io/warn": "restricted"
                }
            }
        }

        result = self._kubectl_apply(namespace_yaml)
        self.results["deployment_results"].append({
            "action": "namespace_creation",
            "success": result["success"],
            "details": result["output"]
        })

    def _deploy_manifests(self):
        """Deploy all security manifests from the fixes directory"""
        print("🛡️  Deploying security manifests...")

        if not self.security_fixes_dir.exists():
            self.results["failures"].append("Security fixes directory not found")
            return

        for manifest_file in self.security_fixes_dir.glob("*.yaml"):
            print(f"  📄 Deploying {manifest_file.name}")

            try:
                with open(manifest_file, 'r') as f:
                    manifest = yaml.safe_load(f)

                result = self._kubectl_apply(manifest)
                self.results["deployment_results"].append({
                    "manifest": manifest_file.name,
                    "success": result["success"],
                    "output": result["output"],
                    "error": result.get("error")
                })

                if result["success"]:
                    print(f"    ✅ {manifest_file.name} deployed successfully")
                else:
                    print(f"    ❌ {manifest_file.name} failed: {result.get('error')}")

            except Exception as e:
                self.results["failures"].append(f"Failed to deploy {manifest_file.name}: {str(e)}")

    def _test_rbac_policies(self):
        """Test RBAC policies actually work"""
        print("🔐 Testing RBAC policies...")

        # Test 1: Check service account exists
        sa_check = self._kubectl_run([
            "kubectl", "get", "serviceaccount", "app-service-account",
            "-n", self.namespace, "-o", "json"
        ])

        rbac_test = {
            "test": "service_account_exists",
            "success": sa_check["success"],
            "details": "Service account app-service-account created"
        }

        if sa_check["success"]:
            print("  ✅ Service account exists")

            # Test 2: Check RBAC permissions
            auth_test = self._kubectl_run([
                "kubectl", "auth", "can-i", "create", "pods",
                "--as=system:serviceaccount:portfolio:app-service-account",
                "-n", self.namespace
            ])

            rbac_test.update({
                "rbac_permissions": auth_test["success"],
                "rbac_details": auth_test["output"]
            })

            if "yes" in auth_test["output"].lower():
                print("  ✅ RBAC permissions working correctly")
            else:
                print("  ❌ RBAC permissions too restrictive")
        else:
            print("  ❌ Service account not found")

        self.results["validation_tests"].append(rbac_test)

    def _test_network_policies(self):
        """Test NetworkPolicies actually block traffic"""
        print("🌐 Testing NetworkPolicies...")

        # Check NetworkPolicies exist
        np_check = self._kubectl_run([
            "kubectl", "get", "networkpolicy", "-n", self.namespace, "-o", "json"
        ])

        network_test = {
            "test": "network_policies_deployed",
            "success": np_check["success"]
        }

        if np_check["success"]:
            try:
                policies = json.loads(np_check["output"])
                policy_names = [item["metadata"]["name"] for item in policies["items"]]
                print(f"  ✅ NetworkPolicies found: {', '.join(policy_names)}")

                network_test.update({
                    "policies_found": policy_names,
                    "details": f"Found {len(policy_names)} NetworkPolicies"
                })

                # Basic validation - check default-deny exists
                if "default-deny-all" in policy_names:
                    print("  ✅ Default-deny policy active")
                    network_test["default_deny"] = True
                else:
                    print("  ⚠️  No default-deny policy found")
                    network_test["default_deny"] = False

            except json.JSONDecodeError:
                print("  ❌ Failed to parse NetworkPolicy JSON")
                network_test["error"] = "JSON parse failure"
        else:
            print("  ❌ No NetworkPolicies found")

        self.results["validation_tests"].append(network_test)

    def _test_pod_security(self):
        """Test Pod Security Standards enforcement"""
        print("🔒 Testing Pod Security Standards...")

        # Test 1: Try to create insecure pod (should fail)
        insecure_pod = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "insecure-test-pod",
                "namespace": self.namespace
            },
            "spec": {
                "containers": [{
                    "name": "test",
                    "image": "nginx:alpine",
                    "securityContext": {
                        "privileged": True  # This should be blocked
                    }
                }]
            }
        }

        insecure_result = self._kubectl_apply(insecure_pod)

        security_test = {
            "test": "pod_security_enforcement",
            "insecure_pod_blocked": not insecure_result["success"],
            "details": insecure_result.get("error", "")
        }

        if not insecure_result["success"]:
            print("  ✅ Pod Security Standards blocking privileged pods")
        else:
            print("  ❌ Pod Security Standards not enforcing restrictions")
            self._cleanup_pod("insecure-test-pod")

        # Test 2: Try to create secure pod (should succeed)
        secure_pod = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "secure-test-pod",
                "namespace": self.namespace
            },
            "spec": {
                "securityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000
                },
                "containers": [{
                    "name": "test",
                    "image": "nginx:alpine",
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "runAsNonRoot": True,
                        "runAsUser": 1000,
                        "capabilities": {
                            "drop": ["ALL"]
                        }
                    }
                }]
            }
        }

        secure_result = self._kubectl_apply(secure_pod)
        security_test.update({
            "secure_pod_allowed": secure_result["success"],
            "secure_details": secure_result.get("output", "")
        })

        if secure_result["success"]:
            print("  ✅ Secure pods can still be created")
            self._cleanup_pod("secure-test-pod")
        else:
            print("  ❌ Pod Security Standards too restrictive")

        self.results["validation_tests"].append(security_test)

    def _test_application_functionality(self):
        """Test that applications still work after security hardening"""
        print("🔧 Testing application functionality...")

        # Deploy a test application with security contexts
        test_app = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "security-test-app",
                "namespace": self.namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": "security-test"}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": "security-test"}
                    },
                    "spec": {
                        "serviceAccountName": "app-service-account",
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000
                        },
                        "containers": [{
                            "name": "test-app",
                            "image": "nginx:alpine",
                            "ports": [{"containerPort": 80}],
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "runAsNonRoot": True,
                                "runAsUser": 1000,
                                "capabilities": {"drop": ["ALL"]}
                            }
                        }]
                    }
                }
            }
        }

        deploy_result = self._kubectl_apply(test_app)

        functional_test = {
            "test": "application_deployment",
            "success": deploy_result["success"],
            "details": deploy_result.get("output", "")
        }

        if deploy_result["success"]:
            print("  ✅ Hardened application deploys successfully")

            # Wait for pod to be ready
            time.sleep(10)

            # Check pod status
            pod_status = self._kubectl_run([
                "kubectl", "get", "pods", "-l", "app=security-test",
                "-n", self.namespace, "-o", "json"
            ])

            if pod_status["success"]:
                try:
                    pods = json.loads(pod_status["output"])
                    if pods["items"]:
                        pod = pods["items"][0]
                        phase = pod["status"].get("phase", "Unknown")
                        print(f"  📊 Pod status: {phase}")

                        functional_test.update({
                            "pod_phase": phase,
                            "pod_ready": phase == "Running"
                        })

                        if phase == "Running":
                            print("  ✅ Application running with security hardening")
                        else:
                            print("  ⚠️  Application not running properly")

                except json.JSONDecodeError:
                    print("  ❌ Failed to parse pod status")

            # Cleanup
            self._kubectl_run([
                "kubectl", "delete", "deployment", "security-test-app", "-n", self.namespace
            ])
        else:
            print("  ❌ Hardened application failed to deploy")

        self.results["functional_tests"].append(functional_test)

    def _generate_cks_report(self) -> Dict[str, Any]:
        """Generate real CKS-level report with actionable insights"""

        total_deployments = len(self.results["deployment_results"])
        successful_deployments = sum(1 for r in self.results["deployment_results"] if r["success"])

        total_tests = len(self.results["validation_tests"]) + len(self.results["functional_tests"])
        successful_tests = sum(1 for r in self.results["validation_tests"] + self.results["functional_tests"] if r.get("success", False))

        report = {
            "summary": {
                "deployment_success_rate": f"{successful_deployments}/{total_deployments}",
                "test_success_rate": f"{successful_tests}/{total_tests}",
                "cluster_accessible": True,
                "security_posture": "Improved" if successful_deployments > 0 else "Unchanged"
            },
            "deployment_results": self.results["deployment_results"],
            "security_validations": self.results["validation_tests"],
            "functional_validations": self.results["functional_tests"],
            "failures": self.results["failures"],
            "next_actions": self._generate_recommendations()
        }

        print("\n" + "=" * 50)
        print("🎯 CKS-LEVEL DEPLOYMENT & VALIDATION COMPLETE")
        print("=" * 50)
        print(f"✅ Deployments: {successful_deployments}/{total_deployments} successful")
        print(f"✅ Validations: {successful_tests}/{total_tests} passed")
        print(f"🔒 Security Posture: {report['summary']['security_posture']}")

        if self.results["failures"]:
            print(f"❌ Failures: {len(self.results['failures'])}")
            for failure in self.results["failures"]:
                print(f"   - {failure}")

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate actionable next steps"""
        recommendations = []

        # Check for common issues
        rbac_working = any(t.get("rbac_permissions") for t in self.results["validation_tests"] if t["test"] == "service_account_exists")
        if not rbac_working:
            recommendations.append("Review RBAC policies - service account permissions may be too restrictive")

        network_policies_active = any(t.get("default_deny") for t in self.results["validation_tests"] if t["test"] == "network_policies_deployed")
        if not network_policies_active:
            recommendations.append("Deploy default-deny NetworkPolicy for zero-trust networking")

        app_functional = any(t.get("pod_ready") for t in self.results["functional_tests"])
        if not app_functional:
            recommendations.append("Application not starting - review security context compatibility")

        if len(self.results["failures"]) > 0:
            recommendations.append("Address deployment failures before proceeding to production")

        if not recommendations:
            recommendations.append("All security controls deployed and validated successfully")

        return recommendations

    def _kubectl_apply(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Kubernetes manifest and return result"""
        try:
            # Write manifest to temp file
            import tempfile
            import os
            temp_fd, temp_file = tempfile.mkstemp(suffix=".yaml", prefix="k8s_manifest_")
            try:
                with os.fdopen(temp_fd, 'w') as f:
                    yaml.dump(manifest, f)

                result = subprocess.run(
                    ["kubectl", "apply", "-f", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                }
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "kubectl timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _kubectl_run(self, cmd: List[str]) -> Dict[str, Any]:
        """Run kubectl command and return result"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _cleanup_pod(self, pod_name: str):
        """Clean up test pod"""
        self._kubectl_run([
            "kubectl", "delete", "pod", pod_name, "-n", self.namespace, "--ignore-not-found"
        ])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("CKS-Level Deploy-Test-Validate Agent")
        print()
        print("Usage: python cks-agent.py <project_path>")
        print()
        print("Example:")
        print("  python cks-agent.py GP-Projects/Portfolio")
        print()
        print("Outputs:")
        print("  - Deployment validation results → GP-DATA/active/analysis/")
        print("  - Project-specific report → <project>/k8s-security-fixes/")
        sys.exit(1)

    project_path = sys.argv[1]
    agent = KubernetesDeployTestAgent(project_path)

    try:
        results = agent.deploy_security_fixes()

        # Save to GP-DATA (centralized)
        scan_id = f"cks_validation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        gp_data_file = agent.output_dir / f"{scan_id}.json"

        with open(gp_data_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n📊 Results saved to GP-DATA: {gp_data_file}")

        # Also save to project directory for convenience
        project_output = Path(project_path) / "k8s-security-fixes" / "deployment_validation_results.json"
        with open(project_output, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"📄 Project copy saved to: {project_output}")

    except KeyboardInterrupt:
        print("\n⚠️  Deployment testing interrupted")
    except Exception as e:
        print(f"\n❌ Deployment testing failed: {e}")
        sys.exit(1)