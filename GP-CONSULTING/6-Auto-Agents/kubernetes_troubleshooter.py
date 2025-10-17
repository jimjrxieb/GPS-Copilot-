#!/usr/bin/env python3
"""
Kubernetes Troubleshooting Agent - Junior Engineer Assistant

Automates common Kubernetes troubleshooting workflows:
- CrashLoopBackOff diagnosis and fixes
- ImagePullBackOff resolution
- Resource limit optimization
- OOMKilled recovery

100% focus on practical problem-solving, not policy generation.
"""

import subprocess
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Import GP-DATA config manager
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig

class KubernetesTroubleshootingAgent:
    def __init__(self, kubeconfig: Optional[str] = None):
        self.agent_id = "k8s_troubleshooter"
        self.kubectl_path = self._find_kubectl()
        self.kubeconfig = kubeconfig or self._get_default_kubeconfig()

        # Use GP-DATA config for diagnostic output
        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()

        # Common error patterns we can auto-fix
        self.error_patterns = {
            "oomkilled": {
                "indicators": ["OOMKilled", "out of memory"],
                "confidence": "high",
                "auto_fixable": True
            },
            "imagepullbackoff": {
                "indicators": ["ImagePullBackOff", "ErrImagePull", "manifest unknown"],
                "confidence": "high",
                "auto_fixable": True
            },
            "crashloopbackoff": {
                "indicators": ["CrashLoopBackOff", "Error", "panic"],
                "confidence": "medium",
                "auto_fixable": False  # Needs human analysis
            },
            "configmap_missing": {
                "indicators": ["configmap", "not found", "couldn't find"],
                "confidence": "high",
                "auto_fixable": True
            }
        }

    def _find_kubectl(self) -> str:
        """Find kubectl binary"""
        kubectl = shutil.which("kubectl")
        if not kubectl:
            raise RuntimeError("kubectl not found in PATH")
        return kubectl

    def _get_default_kubeconfig(self) -> str:
        """Get default kubeconfig location"""
        home = Path.home()
        return str(home / ".kube" / "config")

    def _run_kubectl(self, args: List[str], capture_json: bool = False) -> Tuple[int, str, str]:
        """Run kubectl command and return exit code, stdout, stderr"""
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

    def diagnose_crashloopbackoff(self, namespace: str, pod_name: str) -> Dict:
        """
        Full CrashLoopBackOff diagnosis workflow

        Workflow:
        1. Get pod status (kubectl describe)
        2. Get recent logs (kubectl logs --previous)
        3. Get events (kubectl get events)
        4. Identify error patterns
        5. Generate fix recommendations
        """
        print(f"🔍 Diagnosing CrashLoopBackOff: {namespace}/{pod_name}")

        diagnosis = {
            "pod": f"{namespace}/{pod_name}",
            "timestamp": datetime.now().isoformat(),
            "status": {},
            "logs": "",
            "events": [],
            "error_pattern": None,
            "root_cause": None,
            "confidence": "unknown",
            "auto_fixable": False,
            "suggested_fixes": []
        }

        # Step 1: Get pod status
        print("   📋 Getting pod status...")
        returncode, pod_status, error = self._run_kubectl(
            ["get", "pod", pod_name, "-n", namespace, "-o", "json"],
            capture_json=True
        )

        if returncode == 0:
            diagnosis["status"] = pod_status
        else:
            diagnosis["status"] = {"error": error}
            return diagnosis

        # Step 2: Get container logs (from previous crashed container)
        print("   📜 Getting pod logs...")
        returncode, logs, error = self._run_kubectl(
            ["logs", pod_name, "-n", namespace, "--previous", "--tail=100"]
        )

        if returncode == 0:
            diagnosis["logs"] = logs
        else:
            # Try current container if no previous
            returncode, logs, error = self._run_kubectl(
                ["logs", pod_name, "-n", namespace, "--tail=100"]
            )
            diagnosis["logs"] = logs if returncode == 0 else error

        # Step 3: Get pod events
        print("   🔔 Getting pod events...")
        returncode, events_data, error = self._run_kubectl(
            ["get", "events", "-n", namespace,
             "--field-selector", f"involvedObject.name={pod_name}", "-o", "json"],
            capture_json=True
        )

        if returncode == 0 and isinstance(events_data, dict):
            diagnosis["events"] = events_data.get("items", [])

        # Step 4: Analyze error patterns
        print("   🧠 Analyzing error patterns...")
        diagnosis = self._analyze_error_patterns(diagnosis)

        # Step 5: Generate fixes
        print("   💡 Generating fix recommendations...")
        diagnosis = self._generate_fixes(diagnosis)

        return diagnosis

    def _analyze_error_patterns(self, diagnosis: Dict) -> Dict:
        """Identify error patterns from logs and events"""
        logs_lower = diagnosis["logs"].lower()
        events_text = " ".join([e.get("message", "") for e in diagnosis["events"]]).lower()
        combined_text = logs_lower + " " + events_text

        for pattern_name, pattern_config in self.error_patterns.items():
            for indicator in pattern_config["indicators"]:
                if indicator.lower() in combined_text:
                    diagnosis["error_pattern"] = pattern_name
                    diagnosis["confidence"] = pattern_config["confidence"]
                    diagnosis["auto_fixable"] = pattern_config["auto_fixable"]

                    # Set root cause based on pattern
                    if pattern_name == "oomkilled":
                        diagnosis["root_cause"] = "Container exceeded memory limits"
                    elif pattern_name == "imagepullbackoff":
                        diagnosis["root_cause"] = "Cannot pull container image"
                    elif pattern_name == "crashloopbackoff":
                        diagnosis["root_cause"] = "Application error or misconfiguration"
                    elif pattern_name == "configmap_missing":
                        diagnosis["root_cause"] = "Missing ConfigMap or Secret"

                    break

            if diagnosis["error_pattern"]:
                break

        return diagnosis

    def _generate_fixes(self, diagnosis: Dict) -> Dict:
        """Generate specific fix recommendations based on error pattern"""
        pattern = diagnosis.get("error_pattern")

        if pattern == "oomkilled":
            # Calculate new memory limits
            current_limit = self._extract_memory_limit(diagnosis["status"])
            recommended_limit = self._calculate_memory_increase(current_limit)

            diagnosis["suggested_fixes"] = [
                {
                    "type": "increase_memory",
                    "action": "Increase memory limits",
                    "current": current_limit,
                    "recommended": recommended_limit,
                    "command": f"kubectl set resources deployment <deployment-name> -c <container-name> --limits=memory={recommended_limit}"
                }
            ]

        elif pattern == "imagepullbackoff":
            diagnosis["suggested_fixes"] = [
                {
                    "type": "check_image_tag",
                    "action": "Verify image tag exists in registry",
                    "details": "Check if the image tag is correct and exists in the container registry"
                },
                {
                    "type": "check_imagepullsecrets",
                    "action": "Verify ImagePullSecrets",
                    "details": "Ensure the pod has correct ImagePullSecrets for private registries"
                }
            ]

        elif pattern == "configmap_missing":
            diagnosis["suggested_fixes"] = [
                {
                    "type": "create_configmap",
                    "action": "Create missing ConfigMap",
                    "details": "Review pod spec and create the missing ConfigMap or Secret"
                }
            ]

        elif pattern == "crashloopbackoff":
            diagnosis["suggested_fixes"] = [
                {
                    "type": "review_logs",
                    "action": "Manual log review required",
                    "details": "Application error detected - review logs for specific error messages"
                }
            ]

        return diagnosis

    def _extract_memory_limit(self, pod_status: Dict) -> str:
        """Extract current memory limit from pod status"""
        try:
            containers = pod_status.get("spec", {}).get("containers", [])
            if containers:
                limits = containers[0].get("resources", {}).get("limits", {})
                return limits.get("memory", "256Mi")
        except:
            pass
        return "256Mi"

    def _calculate_memory_increase(self, current: str) -> str:
        """Calculate recommended memory increase (2x current)"""
        # Simple 2x increase - could be smarter based on usage patterns
        if current.endswith("Mi"):
            value = int(current[:-2])
            return f"{value * 2}Mi"
        elif current.endswith("Gi"):
            value = int(current[:-2])
            return f"{value * 2}Gi"
        return "512Mi"  # Default fallback

    def fix_oom_killed(self, namespace: str, deployment_name: str,
                       container_name: str, memory_limit: str) -> Dict:
        """
        Auto-fix OOMKilled issue by increasing memory limits

        This is 100% automatable with high confidence
        """
        print(f"🔧 Fixing OOMKilled for {namespace}/{deployment_name}")

        # Build resource patch
        patch = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": container_name,
                            "resources": {
                                "limits": {
                                    "memory": memory_limit
                                },
                                "requests": {
                                    "memory": memory_limit
                                }
                            }
                        }]
                    }
                }
            }
        }

        # Apply patch
        returncode, stdout, stderr = self._run_kubectl([
            "patch", "deployment", deployment_name,
            "-n", namespace,
            "--type", "strategic",
            "--patch", json.dumps(patch)
        ])

        result = {
            "success": returncode == 0,
            "deployment": f"{namespace}/{deployment_name}",
            "memory_limit": memory_limit,
            "output": stdout,
            "error": stderr if returncode != 0 else None
        }

        if result["success"]:
            print(f"   ✅ Memory limit increased to {memory_limit}")
        else:
            print(f"   ❌ Fix failed: {stderr}")

        return result

    def get_failing_pods(self, namespace: str = None) -> List[Dict]:
        """
        Get all pods in non-running states

        Returns list of pods with their issues for batch processing
        """
        args = ["get", "pods", "-o", "json"]
        if namespace:
            args.extend(["-n", namespace])
        else:
            args.append("--all-namespaces")

        returncode, pods_data, error = self._run_kubectl(args, capture_json=True)

        if returncode != 0:
            return []

        failing_pods = []

        for pod in pods_data.get("items", []):
            pod_name = pod["metadata"]["name"]
            pod_namespace = pod["metadata"]["namespace"]

            # Check container statuses
            container_statuses = pod.get("status", {}).get("containerStatuses", [])

            for status in container_statuses:
                state = status.get("state", {})
                waiting = state.get("waiting", {})

                if waiting:
                    reason = waiting.get("reason", "")
                    if reason in ["CrashLoopBackOff", "ImagePullBackOff", "OOMKilled"]:
                        failing_pods.append({
                            "name": pod_name,
                            "namespace": pod_namespace,
                            "reason": reason,
                            "container": status["name"]
                        })

        return failing_pods

    def save_diagnosis(self, diagnosis: Dict) -> Path:
        """Save diagnosis results to GP-DATA"""
        diagnosis_id = f"k8s_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        output_file = self.output_dir / f"{diagnosis_id}.json"

        with open(output_file, 'w') as f:
            json.dump(diagnosis, f, indent=2)

        return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Kubernetes Troubleshooting Agent - Junior Engineer Assistant")
        print()
        print("Usage:")
        print("  python k8s_troubleshooter.py diagnose <namespace> <pod-name>")
        print("  python k8s_troubleshooter.py fix-oom <namespace> <deployment> <container> <memory-limit>")
        print("  python k8s_troubleshooter.py list-failing [namespace]")
        print()
        print("Examples:")
        print("  python k8s_troubleshooter.py diagnose default my-app-pod-xyz")
        print("  python k8s_troubleshooter.py fix-oom default my-app app 512Mi")
        print("  python k8s_troubleshooter.py list-failing default")
        sys.exit(1)

    agent = KubernetesTroubleshootingAgent()
    command = sys.argv[1]

    if command == "diagnose" and len(sys.argv) == 4:
        namespace = sys.argv[2]
        pod_name = sys.argv[3]

        diagnosis = agent.diagnose_crashloopbackoff(namespace, pod_name)

        # Save to GP-DATA
        saved_file = agent.save_diagnosis(diagnosis)

        print()
        print("🔍 DIAGNOSIS RESULTS:")
        print(f"   Pod: {diagnosis['pod']}")
        print(f"   Error Pattern: {diagnosis['error_pattern']}")
        print(f"   Root Cause: {diagnosis['root_cause']}")
        print(f"   Confidence: {diagnosis['confidence']}")
        print(f"   Auto-fixable: {diagnosis['auto_fixable']}")
        print()
        print("💡 SUGGESTED FIXES:")
        for i, fix in enumerate(diagnosis["suggested_fixes"], 1):
            print(f"   {i}. {fix['action']}")
            if "command" in fix:
                print(f"      Command: {fix['command']}")
            if "details" in fix:
                print(f"      Details: {fix['details']}")
        print()
        print(f"📊 Diagnosis saved to GP-DATA: {saved_file}")

    elif command == "fix-oom" and len(sys.argv) == 6:
        namespace = sys.argv[2]
        deployment = sys.argv[3]
        container = sys.argv[4]
        memory_limit = sys.argv[5]

        result = agent.fix_oom_killed(namespace, deployment, container, memory_limit)

        if result["success"]:
            print()
            print(f"✅ Successfully fixed OOMKilled for {result['deployment']}")
            print(f"   New memory limit: {result['memory_limit']}")
        else:
            print()
            print(f"❌ Fix failed: {result['error']}")

    elif command == "list-failing":
        namespace = sys.argv[2] if len(sys.argv) > 2 else None

        failing = agent.get_failing_pods(namespace)

        print()
        print(f"🚨 FAILING PODS ({len(failing)} found):")
        for pod in failing:
            print(f"   {pod['namespace']}/{pod['name']}")
            print(f"      Reason: {pod['reason']}")
            print(f"      Container: {pod['container']}")
            print()

    else:
        print("Invalid command or arguments")
        sys.exit(1)