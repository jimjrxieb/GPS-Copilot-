#!/usr/bin/env python3
"""
OPA Scanner - Clean, Simple, Working
Single-purpose scanner for Open Policy Agent policy evaluation
"""

import subprocess
import json
import shutil
import yaml
import sys
import time
import requests
import signal
from pathlib import Path
from datetime import datetime
# Import config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig
from typing import Dict, List, Optional

class OpaScanner:
    def __init__(self, output_dir: Optional[Path] = None):
        # Find OPA binary
        if shutil.which("opa"):
            self.tool_path = "opa"
        else:
            # Try common installation paths
            local_paths = [
                Path("/home/jimmie/linkops-industries/GP-copilot/bin/opa"),
                Path("/home/jimmie/linkops-industries/James-OS/guidepoint/bin/opa"),
                Path.home() / ".local/bin/opa"
            ]

            for path in local_paths:
                if path.exists():
                    self.tool_path = str(path)
                    break
            else:
                raise RuntimeError(
                    "OPA not found. Install with:\n"
                    "curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64\n"
                    "chmod +x opa && sudo mv opa /usr/local/bin/"
                )

        # Data persistence directory
        # Use centralized config manager
        if output_dir:
            self.output_dir = output_dir
        else:
            config = GPDataConfig()
            self.output_dir = config.get_scan_directory()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Policy directory
        self.policies_dir = Path(__file__).parent.parent / "policies" / "opa"
        self.policies_dir.mkdir(parents=True, exist_ok=True)

        # OPA server management
        self.opa_process = None
        self.server_port = 8181

        # Severity mapping
        self.severity_mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low"
        }

        # Ensure basic policies exist
        self._ensure_basic_policies()

    def _ensure_basic_policies(self):
        """Create basic security policies if they don't exist"""

        basic_security_policy = '''package security

# Pod Security Violations
violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.privileged == true
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' runs in privileged mode", [container.name])
}

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.allowPrivilegeEscalation == true
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' allows privilege escalation", [container.name])
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "Pod"
    not input.spec.securityContext.runAsNonRoot
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Pod missing runAsNonRoot security context"
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' does not use read-only root filesystem", [container.name])
}

# Deployment Security Violations
violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    container.securityContext.privileged == true
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := sprintf("Container '%s' runs in privileged mode", [container.name])
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "Deployment"
    not input.spec.template.spec.securityContext.runAsNonRoot
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Deployment missing runAsNonRoot security context"
}

# Service Security Violations
violations[{"msg": msg, "severity": "low", "resource": resource}] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Service uses LoadBalancer type - ensure proper ingress controls"
}
'''

        network_policy = '''package network

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "NetworkPolicy"
    count(input.spec.ingress) == 0
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "NetworkPolicy has no ingress rules defined"
}

violations[{"msg": msg, "severity": "medium", "resource": resource}] {
    input.kind == "NetworkPolicy"
    ingress := input.spec.ingress[_]
    from := ingress.from[_]
    from.ipBlock.cidr == "0.0.0.0/0"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "NetworkPolicy allows ingress from all IPs (0.0.0.0/0)"
}
'''

        rbac_policy = '''package rbac

violations[{"msg": msg, "severity": "critical", "resource": resource}] {
    input.kind == "ClusterRoleBinding"
    input.subjects[_].name == "system:anonymous"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "ClusterRoleBinding grants permissions to anonymous users"
}

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "Role"
    rule := input.rules[_]
    rule.verbs[_] == "*"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "Role grants wildcard (*) verb permissions"
}

violations[{"msg": msg, "severity": "high", "resource": resource}] {
    input.kind == "ClusterRole"
    rule := input.rules[_]
    rule.resources[_] == "*"
    rule.verbs[_] == "*"
    resource := sprintf("%s/%s", [input.kind, input.metadata.name])
    msg := "ClusterRole grants wildcard permissions on all resources"
}
'''

        # Write policies
        policies = {
            "security.rego": basic_security_policy,
            "network.rego": network_policy,
            "rbac.rego": rbac_policy
        }

        for filename, content in policies.items():
            policy_file = self.policies_dir / filename
            if not policy_file.exists():
                with open(policy_file, 'w') as f:
                    f.write(content)

    def scan(self, target_path: str, policy_package: str = "security") -> dict:
        """
        Run OPA policy evaluation on Kubernetes manifests and Terraform files

        Args:
            target_path: Directory containing YAML/JSON/TF files to evaluate
            policy_package: OPA package to evaluate (security, network, rbac,
                          secrets-management, image-security, compliance-controls,
                          terraform-security, cicd-security)

        Returns:
            Scan results dictionary with compliance mapping
        """
        target = Path(target_path)
        if not target.exists():
            raise ValueError(f"Target does not exist: {target_path}")

        # Find YAML/JSON files to evaluate
        manifest_files = self._find_manifests(target)

        if not manifest_files:
            empty_result = self._create_empty_result(target_path, policy_package)
            empty_result["note"] = "No YAML/JSON manifests found"
            self._save_results(empty_result)
            return empty_result

        # Evaluate policies
        all_violations = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        files_scanned = 0

        for manifest_file in manifest_files:
            violations = self._evaluate_policy(manifest_file, policy_package)

            for violation in violations:
                severity = violation.get("severity", "low")
                if severity in severity_counts:
                    severity_counts[severity] += 1

                violation["file"] = str(manifest_file.relative_to(target))
                all_violations.append(violation)

            files_scanned += 1

        results = {
            "findings": all_violations,
            "summary": {
                "total": len(all_violations),
                "files_scanned": files_scanned,
                "severity_breakdown": severity_counts,
                "policy_package": policy_package
            },
            "target": target_path,
            "tool": "opa",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "metadata": {
                "policy_directory": str(self.policies_dir),
                "policies_available": [p.stem for p in self.policies_dir.glob("*.rego")]
            }
        }

        self._save_results(results)
        return results

    def _find_manifests(self, target: Path) -> List[Path]:
        """Find YAML, JSON, and Terraform manifest files"""
        manifests = []
        patterns = ['*.yaml', '*.yml', '*.json', '*.tf']

        for pattern in patterns:
            manifests.extend(target.rglob(pattern))

        return manifests

    def _evaluate_policy(self, manifest_file: Path, policy_package: str) -> List[dict]:
        """Evaluate OPA policy against a manifest file"""
        violations = []

        try:
            # Read manifest file
            with open(manifest_file, 'r') as f:
                if manifest_file.suffix in ['.yaml', '.yml']:
                    documents = list(yaml.safe_load_all(f))
                elif manifest_file.suffix == '.tf':
                    # For Terraform files, wrap in document structure
                    documents = [{
                        '_type': 'terraform',
                        '_content': f.read(),
                        'file_path': str(manifest_file)
                    }]
                    f.seek(0)  # Reset for policy evaluation
                else:
                    documents = [json.load(f)]

            # Evaluate each document
            for doc in documents:
                if not doc or not isinstance(doc, dict):
                    continue

                # Run OPA evaluation
                policy_file = self.policies_dir / f"{policy_package}.rego"

                if not policy_file.exists():
                    # Check admission-control subdirectory
                    admission_policy = self.policies_dir / "admission-control" / f"{policy_package}.rego"
                    if admission_policy.exists():
                        policy_file = admission_policy
                    else:
                        continue

                cmd = [
                    self.tool_path,
                    "eval",
                    "--data", str(policy_file),
                    "--input", "-",
                    "--format", "json",
                    f"data.{policy_package}.violations"
                ]

                result = subprocess.run(
                    cmd,
                    input=json.dumps(doc),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0 and result.stdout:
                    output = json.loads(result.stdout)

                    # OPA eval returns: {"result": [{"expressions": [{"value": [...]}]}]}
                    if output.get("result") and len(output["result"]) > 0:
                        expressions = output["result"][0].get("expressions", [])
                        if expressions and len(expressions) > 0:
                            policy_violations = expressions[0].get("value", [])
                            violations.extend(policy_violations)

        except Exception as e:
            # Log error but continue scanning
            pass

        return violations

    def _create_empty_result(self, target_path: str, policy_package: str) -> dict:
        """Create empty result structure"""
        return {
            "findings": [],
            "summary": {
                "total": 0,
                "files_scanned": 0,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0},
                "policy_package": policy_package
            },
            "target": target_path,
            "tool": "opa",
            "timestamp": datetime.now().isoformat(),
            "scan_id": self._generate_scan_id(),
            "metadata": {
                "policy_directory": str(self.policies_dir),
                "policies_available": []
            }
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan identifier"""
        return f"opa_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"

    def _save_results(self, results: dict):
        """Save scan results to persistent storage"""
        scan_id = results.get("scan_id", self._generate_scan_id())
        filename = f"{scan_id}.json"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_file = self.output_dir / filename
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print(f"🔒 OPA results saved to: {output_file}")

            latest_file = self.output_dir / "opa_latest.json"
            with open(latest_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            print(f"⚠️  Failed to save results: {e}")

    def start_opa_server(self, policies_dir: str = None) -> bool:
        """Start OPA server with policies loaded for admission control"""
        if not policies_dir:
            policies_dir = str(self.policies_dir)

        # Create OPA config file for server mode
        config_file = self.policies_dir / "config.yaml"
        config = {
            "services": {
                "authz": {
                    "url": f"http://localhost:{self.server_port}"
                }
            },
            "bundles": {
                "authz": {
                    "resource": "bundle.tar.gz"
                }
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(config, f)

        print(f"🚀 Starting OPA server on port {self.server_port}...")

        cmd = [
            self.tool_path, "run",
            "--server",
            "--addr", f"localhost:{self.server_port}",
            "--config-file", str(config_file),
            policies_dir
        ]

        try:
            self.opa_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=None if sys.platform == "win32" else lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
            )

            # Wait for server to start
            time.sleep(3)

            if self._check_server_health():
                print(f"✅ OPA server started successfully")
                return True
            else:
                print(f"❌ OPA server failed to start properly")
                self.stop_opa_server()
                return False

        except Exception as e:
            print(f"❌ Failed to start OPA server: {e}")
            return False

    def _check_server_health(self) -> bool:
        """Check if OPA server is responding"""
        try:
            response = requests.get(f"http://localhost:{self.server_port}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def stop_opa_server(self):
        """Stop the OPA server"""
        if self.opa_process:
            print("🛑 Stopping OPA server...")
            try:
                self.opa_process.terminate()
                self.opa_process.wait(timeout=10)
                print("✅ OPA server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing OPA server...")
                self.opa_process.kill()
                self.opa_process.wait()
            except Exception as e:
                print(f"❌ Error stopping OPA server: {e}")
            finally:
                self.opa_process = None

    def query_server(self, input_data: dict, policy_path: str = "data.kubernetes.admission") -> dict:
        """Query the running OPA server with input data"""
        if not self._check_server_health():
            return {"error": "OPA server not running"}

        try:
            url = f"http://localhost:{self.server_port}/v1/data/{policy_path.replace('.', '/')}"
            response = requests.post(
                url,
                json={"input": input_data},
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Query failed with status {response.status_code}"}

        except Exception as e:
            return {"error": f"Query failed: {e}"}

    def test_admission_control(self, test_manifest: dict) -> dict:
        """Test a Kubernetes manifest against admission policies"""
        if not self._check_server_health():
            return {"error": "OPA server not running. Start server first."}

        # Format input as Kubernetes AdmissionReview
        admission_review = {
            "kind": "AdmissionReview",
            "apiVersion": "admission.k8s.io/v1",
            "request": {
                "uid": "test-uid",
                "kind": test_manifest.get("kind", {}),
                "object": test_manifest,
                "operation": "CREATE"
            }
        }

        result = self.query_server(admission_review, "data.kubernetes.admission")

        if "result" in result:
            violations = result["result"].get("deny", [])
            return {
                "allowed": len(violations) == 0,
                "violations": violations,
                "admission_review": admission_review
            }
        else:
            return result

    def __del__(self):
        """Cleanup: Stop OPA server when scanner is destroyed"""
        if hasattr(self, 'opa_process') and self.opa_process:
            self.stop_opa_server()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python opa_scanner.py <target_path> [policy_package]")
        print()
        print("Policy packages:")
        print("  Core Security:")
        print("    - security (default)       : Basic container security")
        print("    - kubernetes              : K8s security controls")
        print("    - network                 : Network policy validation")
        print("    - rbac                    : RBAC security checks")
        print()
        print("  Advanced Security:")
        print("    - secrets-management      : Secret handling & rotation")
        print("    - image-security          : Container image supply chain")
        print("    - compliance-controls     : SOC2, PCI-DSS, HIPAA, GDPR")
        print()
        print("  Infrastructure:")
        print("    - terraform-security      : Multi-cloud IaC (AWS, Azure, GCP)")
        print("    - cicd-security          : CI/CD pipeline security (SLSA)")
        print()
        print("  Admission Control (comprehensive):")
        print("    - pod-security           : Advanced pod security standards")
        print("    - network-policies       : Zero-trust networking")
        print()
        print("Example: python opa_scanner.py /path/to/k8s compliance-controls")
        sys.exit(1)

    target_path = sys.argv[1]
    policy_package = sys.argv[2] if len(sys.argv) > 2 else "security"

    scanner = OpaScanner()
    results = scanner.scan(target_path, policy_package)

    print(f"🔒 OPA found {results['summary']['total']} violations")
    print(f"   Files scanned: {results['summary']['files_scanned']}")

    if results['summary']['total'] > 0:
        severity = results['summary']['severity_breakdown']
        print(f"   Critical: {severity['critical']}")
        print(f"   High: {severity['high']}")
        print(f"   Medium: {severity['medium']}")
        print(f"   Low: {severity['low']}")