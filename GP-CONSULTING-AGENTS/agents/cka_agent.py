#!/usr/bin/env python3
"""
CKA Operations Agent - Kubernetes Task Execution with Confidence Scoring

Executes specific Kubernetes operational tasks under senior engineer guidance.
Focus: Practical problem-solving, not policy generation.

Confidence Levels:
- HIGH: Create pods, services, configmaps, secrets, basic RBAC, check status
- MEDIUM: Security contexts, network policies, deployments, troubleshooting
- LOW: Custom resources, operators, complex networking (escalate to human)
"""

import subprocess
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class CKAOperationsAgent:
    """
    CKA-level Kubernetes operations agent

    Capabilities:
    - Create pods, services, configmaps, secrets
    - Apply basic RBAC policies
    - Check pod status and logs
    - Troubleshoot common issues (CrashLoopBackOff, OOMKilled)
    - Generate deployment manifests
    """

    def __init__(self, kubeconfig: Optional[str] = None):
        self.agent_id = "cka_operations_agent"
        self.kubectl_path = self._find_kubectl()
        self.kubeconfig = kubeconfig or self._get_default_kubeconfig()

        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()

        self.confidence_levels = {
            "high": ["create_pod", "create_service", "create_configmap", "create_secret",
                    "apply_basic_rbac", "check_pod_status", "get_pod_logs"],
            "medium": ["apply_security_context", "create_network_policy", "create_deployment",
                      "troubleshoot_crashloop"],
            "low": ["custom_resources", "operators", "complex_networking"]
        }

        self.secure_defaults = {
            "security_context": {
                "runAsNonRoot": True,
                "runAsUser": 1000,
                "allowPrivilegeEscalation": False,
                "readOnlyRootFilesystem": True,
                "capabilities": {"drop": ["ALL"]}
            },
            "pod_security_standard": "restricted"
        }

    def _find_kubectl(self) -> str:
        kubectl = shutil.which("kubectl")
        if not kubectl:
            raise RuntimeError("kubectl not found in PATH")
        return kubectl

    def _get_default_kubeconfig(self) -> str:
        home = Path.home()
        return str(home / ".kube" / "config")

    def _run_kubectl(self, args: List[str], capture_json: bool = False) -> Tuple[int, str, str]:
        cmd = [self.kubectl_path] + args

        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if capture_json and result.returncode == 0:
            try:
                return result.returncode, json.loads(result.stdout), result.stderr
            except json.JSONDecodeError:
                return result.returncode, result.stdout, result.stderr

        return result.returncode, result.stdout, result.stderr

    def _kubectl_apply(self, manifest: Dict, namespace: str = "default") -> Dict:
        import tempfile
        import yaml

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(manifest, f, default_flow_style=False)
            temp_file = f.name

        try:
            returncode, stdout, stderr = self._run_kubectl([
                "apply", "-f", temp_file, "-n", namespace
            ])

            result = {
                "success": returncode == 0,
                "output": stdout,
                "error": stderr if returncode != 0 else None,
                "manifest_applied": manifest
            }
        finally:
            Path(temp_file).unlink()

        return result

    def create_test_pod(self, name: str, image: str, namespace: str = "default",
                       apply_security_context: bool = True) -> Dict:
        """
        HIGH CONFIDENCE: Create a test pod with secure defaults

        Args:
            name: Pod name
            image: Container image
            namespace: Target namespace
            apply_security_context: Apply secure defaults (recommended)
        """
        print(f"🚀 Creating test pod '{name}' with image '{image}'")

        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": name, "namespace": namespace},
            "spec": {
                "containers": [{
                    "name": name,
                    "image": image,
                    "command": ["sleep", "3600"]
                }]
            }
        }

        if apply_security_context:
            pod_manifest["spec"]["securityContext"] = self.secure_defaults["security_context"]
            pod_manifest["spec"]["containers"][0]["securityContext"] = {
                "allowPrivilegeEscalation": False
            }

        result = self._kubectl_apply(pod_manifest, namespace)

        if result["success"]:
            print(f"   ✅ Pod '{name}' created successfully")
        else:
            print(f"   ❌ Pod creation failed: {result['error']}")

        self._save_operation("create_test_pod", result)
        return result

    def create_basic_service(self, name: str, selector: Dict[str, str],
                            port: int, target_port: int, namespace: str = "default") -> Dict:
        """
        HIGH CONFIDENCE: Create a ClusterIP service

        Args:
            name: Service name
            selector: Pod selector labels
            port: Service port
            target_port: Target container port
            namespace: Target namespace
        """
        print(f"🌐 Creating service '{name}' on port {port}")

        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": name, "namespace": namespace},
            "spec": {
                "type": "ClusterIP",
                "selector": selector,
                "ports": [{
                    "port": port,
                    "targetPort": target_port,
                    "protocol": "TCP"
                }]
            }
        }

        result = self._kubectl_apply(service_manifest, namespace)

        if result["success"]:
            print(f"   ✅ Service '{name}' created")
        else:
            print(f"   ❌ Service creation failed: {result['error']}")

        self._save_operation("create_basic_service", result)
        return result

    def create_configmap(self, name: str, data: Dict[str, str], namespace: str = "default") -> Dict:
        """
        HIGH CONFIDENCE: Create a ConfigMap

        Args:
            name: ConfigMap name
            data: Key-value data
            namespace: Target namespace
        """
        print(f"📋 Creating ConfigMap '{name}'")

        configmap_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": name, "namespace": namespace},
            "data": data
        }

        result = self._kubectl_apply(configmap_manifest, namespace)

        if result["success"]:
            print(f"   ✅ ConfigMap '{name}' created")
        else:
            print(f"   ❌ ConfigMap creation failed: {result['error']}")

        self._save_operation("create_configmap", result)
        return result

    def apply_basic_rbac(self, service_account: str, role_name: str,
                        resources: List[str], verbs: List[str],
                        namespace: str = "default") -> Dict:
        """
        HIGH CONFIDENCE: Apply basic RBAC (Role + RoleBinding)

        Args:
            service_account: ServiceAccount name
            role_name: Role name
            resources: Kubernetes resources (e.g., ["pods", "configmaps"])
            verbs: Allowed verbs (e.g., ["get", "list"])
            namespace: Target namespace
        """
        print(f"🔐 Applying RBAC for ServiceAccount '{service_account}'")

        sa_manifest = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {"name": service_account, "namespace": namespace}
        }

        role_manifest = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {"name": role_name, "namespace": namespace},
            "rules": [{
                "apiGroups": [""],
                "resources": resources,
                "verbs": verbs
            }]
        }

        binding_manifest = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": f"{role_name}-binding", "namespace": namespace},
            "subjects": [{
                "kind": "ServiceAccount",
                "name": service_account,
                "namespace": namespace
            }],
            "roleRef": {
                "kind": "Role",
                "name": role_name,
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }

        sa_result = self._kubectl_apply(sa_manifest, namespace)
        role_result = self._kubectl_apply(role_manifest, namespace)
        binding_result = self._kubectl_apply(binding_manifest, namespace)

        result = {
            "success": all([sa_result["success"], role_result["success"], binding_result["success"]]),
            "service_account": sa_result,
            "role": role_result,
            "role_binding": binding_result
        }

        if result["success"]:
            print(f"   ✅ RBAC configured for '{service_account}'")
        else:
            print(f"   ❌ RBAC configuration failed")

        self._save_operation("apply_basic_rbac", result)
        return result

    def check_pod_status(self, pod_name: str, namespace: str = "default") -> Dict:
        """
        HIGH CONFIDENCE: Check pod status

        Returns pod phase, conditions, and container statuses
        """
        print(f"🔍 Checking pod status: {namespace}/{pod_name}")

        returncode, pod_data, error = self._run_kubectl([
            "get", "pod", pod_name, "-n", namespace, "-o", "json"
        ], capture_json=True)

        if returncode != 0:
            return {
                "success": False,
                "error": error,
                "pod_name": pod_name,
                "namespace": namespace
            }

        status = pod_data.get("status", {})
        result = {
            "success": True,
            "pod_name": pod_name,
            "namespace": namespace,
            "phase": status.get("phase"),
            "conditions": status.get("conditions", []),
            "container_statuses": status.get("containerStatuses", []),
            "start_time": status.get("startTime")
        }

        print(f"   Status: {result['phase']}")
        self._save_operation("check_pod_status", result)
        return result

    def get_pod_logs(self, pod_name: str, namespace: str = "default",
                     tail_lines: int = 100, previous: bool = False) -> Dict:
        """
        HIGH CONFIDENCE: Get pod logs

        Args:
            pod_name: Pod name
            namespace: Namespace
            tail_lines: Number of lines to retrieve
            previous: Get logs from previous container (for crashed pods)
        """
        print(f"📜 Getting logs for {namespace}/{pod_name}")

        args = ["logs", pod_name, "-n", namespace, f"--tail={tail_lines}"]
        if previous:
            args.append("--previous")

        returncode, logs, error = self._run_kubectl(args)

        result = {
            "success": returncode == 0,
            "pod_name": pod_name,
            "namespace": namespace,
            "logs": logs if returncode == 0 else None,
            "error": error if returncode != 0 else None,
            "previous_container": previous
        }

        if result["success"]:
            print(f"   ✅ Retrieved {len(logs.splitlines())} log lines")
        else:
            print(f"   ❌ Failed to get logs: {error}")

        self._save_operation("get_pod_logs", result)
        return result

    def troubleshoot_crashloop(self, pod_name: str, namespace: str = "default") -> Dict:
        """
        MEDIUM CONFIDENCE: Troubleshoot CrashLoopBackOff

        Workflow:
        1. Get pod status
        2. Get previous container logs
        3. Identify crash pattern
        4. Suggest remediation
        """
        print(f"🔧 Troubleshooting CrashLoopBackOff: {namespace}/{pod_name}")

        status_result = self.check_pod_status(pod_name, namespace)

        if not status_result["success"]:
            return {
                "success": False,
                "error": "Could not get pod status",
                "details": status_result
            }

        logs_result = self.get_pod_logs(pod_name, namespace, previous=True)

        crash_patterns = {
            "oomkilled": ["out of memory", "oomkilled", "killed"],
            "panic": ["panic:", "fatal error:", "segmentation fault"],
            "config_error": ["cannot find", "no such file", "invalid configuration"],
            "permission_denied": ["permission denied", "forbidden", "unauthorized"]
        }

        identified_pattern = None
        logs_lower = logs_result.get("logs", "").lower()

        for pattern_name, indicators in crash_patterns.items():
            if any(indicator in logs_lower for indicator in indicators):
                identified_pattern = pattern_name
                break

        remediation = self._suggest_crash_remediation(identified_pattern, status_result)

        result = {
            "success": True,
            "pod_name": pod_name,
            "namespace": namespace,
            "pod_status": status_result,
            "logs_analysis": {
                "crash_pattern": identified_pattern or "unknown",
                "log_snippet": logs_result.get("logs", "")[:500]
            },
            "remediation": remediation
        }

        print(f"   Crash Pattern: {identified_pattern or 'unknown'}")
        print(f"   Remediation: {remediation['action']}")

        self._save_operation("troubleshoot_crashloop", result)
        return result

    def _suggest_crash_remediation(self, pattern: Optional[str], pod_status: Dict) -> Dict:
        """Generate remediation suggestions based on crash pattern"""

        if pattern == "oomkilled":
            return {
                "pattern": "oomkilled",
                "action": "Increase memory limits",
                "details": "Container exceeded memory limits",
                "next_steps": [
                    "Review current memory limits",
                    "Analyze memory usage patterns",
                    "Increase limits by 50-100%",
                    "Consider memory profiling"
                ]
            }

        elif pattern == "panic":
            return {
                "pattern": "panic",
                "action": "Review application error logs",
                "details": "Application panic detected",
                "next_steps": [
                    "Examine full stack trace",
                    "Check for nil pointer dereferences",
                    "Review recent code changes",
                    "Add error handling"
                ]
            }

        elif pattern == "config_error":
            return {
                "pattern": "config_error",
                "action": "Verify ConfigMaps and Secrets",
                "details": "Configuration file or resource missing",
                "next_steps": [
                    "Check ConfigMap/Secret exists",
                    "Verify volume mounts",
                    "Validate file paths",
                    "Review environment variables"
                ]
            }

        else:
            return {
                "pattern": "unknown",
                "action": "Manual investigation required",
                "details": "Unable to automatically identify crash cause",
                "next_steps": [
                    "Review full container logs",
                    "Check application metrics",
                    "Verify dependencies",
                    "Escalate to senior engineer"
                ]
            }

    def create_deployment(self, name: str, image: str, replicas: int = 1,
                         namespace: str = "default", apply_security: bool = True) -> Dict:
        """
        MEDIUM CONFIDENCE: Create deployment with secure defaults

        Args:
            name: Deployment name
            image: Container image
            replicas: Number of replicas
            namespace: Target namespace
            apply_security: Apply security context
        """
        print(f"🚀 Creating deployment '{name}' with {replicas} replicas")

        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": name, "namespace": namespace},
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {"labels": {"app": name}},
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": image,
                            "ports": [{"containerPort": 8080}]
                        }]
                    }
                }
            }
        }

        if apply_security:
            deployment_manifest["spec"]["template"]["spec"]["securityContext"] = \
                self.secure_defaults["security_context"]

        result = self._kubectl_apply(deployment_manifest, namespace)

        if result["success"]:
            print(f"   ✅ Deployment '{name}' created")
        else:
            print(f"   ❌ Deployment creation failed: {result['error']}")

        self._save_operation("create_deployment", result)
        return result

    def _save_operation(self, operation_type: str, result: Dict):
        """Save operation results to GP-DATA"""
        operation_id = f"{operation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        output_file = self.output_dir / f"{operation_id}.json"

        operation_record = {
            "agent": self.agent_id,
            "operation": operation_type,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }

        with open(output_file, 'w') as f:
            json.dump(operation_record, f, indent=2)

    def get_confidence_level(self, operation: str) -> str:
        """Get confidence level for operation"""
        for level, operations in self.confidence_levels.items():
            if operation in operations:
                return level
        return "low"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("CKA Operations Agent - Kubernetes Task Execution")
        print()
        print("HIGH CONFIDENCE Operations:")
        print("  python cka_agent.py create-pod <name> <image> [namespace]")
        print("  python cka_agent.py create-service <name> <port> <target-port> [namespace]")
        print("  python cka_agent.py create-configmap <name> <key=value> [namespace]")
        print("  python cka_agent.py check-pod <pod-name> [namespace]")
        print("  python cka_agent.py get-logs <pod-name> [namespace]")
        print()
        print("MEDIUM CONFIDENCE Operations:")
        print("  python cka_agent.py troubleshoot-crash <pod-name> [namespace]")
        print("  python cka_agent.py create-deployment <name> <image> <replicas> [namespace]")
        print()
        print("Examples:")
        print("  python cka_agent.py create-pod test-pod nginx:alpine default")
        print("  python cka_agent.py troubleshoot-crash my-app-pod-xyz default")
        sys.exit(1)

    agent = CKAOperationsAgent()
    command = sys.argv[1]

    if command == "create-pod" and len(sys.argv) >= 4:
        name = sys.argv[2]
        image = sys.argv[3]
        namespace = sys.argv[4] if len(sys.argv) > 4 else "default"

        result = agent.create_test_pod(name, image, namespace)

        if result["success"]:
            print(f"\n✅ Pod '{name}' created successfully")
            print(f"   Verify: kubectl get pod {name} -n {namespace}")
        else:
            print(f"\n❌ Failed: {result['error']}")

    elif command == "create-service" and len(sys.argv) >= 5:
        name = sys.argv[2]
        port = int(sys.argv[3])
        target_port = int(sys.argv[4])
        namespace = sys.argv[5] if len(sys.argv) > 5 else "default"

        result = agent.create_basic_service(
            name, {"app": name}, port, target_port, namespace
        )

        if result["success"]:
            print(f"\n✅ Service '{name}' created")
            print(f"   Verify: kubectl get svc {name} -n {namespace}")

    elif command == "check-pod" and len(sys.argv) >= 3:
        pod_name = sys.argv[2]
        namespace = sys.argv[3] if len(sys.argv) > 3 else "default"

        result = agent.check_pod_status(pod_name, namespace)

        if result["success"]:
            print(f"\n📊 Pod Status:")
            print(f"   Phase: {result['phase']}")
            print(f"   Containers: {len(result['container_statuses'])}")

    elif command == "get-logs" and len(sys.argv) >= 3:
        pod_name = sys.argv[2]
        namespace = sys.argv[3] if len(sys.argv) > 3 else "default"

        result = agent.get_pod_logs(pod_name, namespace)

        if result["success"]:
            print(f"\n📜 Logs for {pod_name}:")
            print(result["logs"])

    elif command == "troubleshoot-crash" and len(sys.argv) >= 3:
        pod_name = sys.argv[2]
        namespace = sys.argv[3] if len(sys.argv) > 3 else "default"

        result = agent.troubleshoot_crashloop(pod_name, namespace)

        if result["success"]:
            print(f"\n🔧 Troubleshooting Results:")
            print(f"   Crash Pattern: {result['logs_analysis']['crash_pattern']}")
            print(f"   Remediation: {result['remediation']['action']}")
            print(f"\n   Next Steps:")
            for step in result['remediation']['next_steps']:
                print(f"   - {step}")

    elif command == "create-deployment" and len(sys.argv) >= 5:
        name = sys.argv[2]
        image = sys.argv[3]
        replicas = int(sys.argv[4])
        namespace = sys.argv[5] if len(sys.argv) > 5 else "default"

        result = agent.create_deployment(name, image, replicas, namespace)

        if result["success"]:
            print(f"\n✅ Deployment '{name}' created")
            print(f"   Verify: kubectl get deployment {name} -n {namespace}")

    else:
        print("Invalid command or arguments")
        sys.exit(1)