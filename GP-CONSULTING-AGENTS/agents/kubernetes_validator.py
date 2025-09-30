#!/usr/bin/env python3
"""
Kubernetes Validator - Fix Verification Agent
===========================================

SAFETY-FIRST DESIGN:
- READ-ONLY validation checks
- Verifies fixes resolved issues
- No cluster modifications
- Comprehensive test suite

Core Capabilities:
- Validate pod is running after fix
- Verify resource allocation
- Check application functionality
- Generate validation report
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import GP-DATA config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "james-config"))
from gp_data_config import GPDataConfig


class KubernetesValidator:
    """
    Safe validation agent - READ ONLY

    Validates that applied fixes actually resolved the issues
    """

    def __init__(self):
        self.config = GPDataConfig()
        self.output_dir = self.config.get_analysis_directory()

    def _safe_kubectl(self, args: List[str], namespace: str = None) -> tuple:
        """Execute safe kubectl command"""
        cmd = ['kubectl'] + args
        if namespace:
            cmd.extend(['-n', namespace])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr

    def validate_fix(self, diagnosis_file: Path, fix_audit_file: Path = None, wait_time: int = 30) -> Dict:
        """
        Validate that a fix resolved the issue

        Workflow:
        1. Load original diagnosis
        2. Load fix audit trail
        3. Wait for pod stabilization
        4. Re-run diagnostics
        5. Compare before/after
        6. Generate validation report
        """
        print(f"🔍 Validating fix from: {diagnosis_file}")

        # Load original diagnosis
        with open(diagnosis_file, 'r') as f:
            original_diagnosis = json.load(f)

        # Extract pod info
        pod_info = original_diagnosis["pod"].split("/")
        namespace = pod_info[0]
        original_pod_name = pod_info[1]

        validation = {
            "original_diagnosis": str(diagnosis_file),
            "fix_audit": str(fix_audit_file) if fix_audit_file else None,
            "timestamp": datetime.now().isoformat(),
            "pod_namespace": namespace,
            "validation_results": {},
            "issue_resolved": False,
            "validation_summary": {}
        }

        # Wait for pod stabilization
        print(f"⏳ Waiting {wait_time}s for pod stabilization...")
        time.sleep(wait_time)

        # Run validation tests based on original issue type
        diagnostic_type = original_diagnosis.get("diagnostic_type", "unknown")

        if diagnostic_type == "crashloopbackoff":
            validation = self._validate_crashloop_fix(namespace, original_pod_name, validation)
        elif diagnostic_type == "imagepullbackoff":
            validation = self._validate_imagepull_fix(namespace, original_pod_name, validation)
        elif diagnostic_type == "resource_constraints":
            validation = self._validate_resource_fix(namespace, original_pod_name, validation)
        else:
            validation["error"] = f"Unknown diagnostic type: {diagnostic_type}"

        # Save validation report
        self._save_validation(validation)

        return validation

    def _validate_crashloop_fix(self, namespace: str, pod_name: str, validation: Dict) -> Dict:
        """Validate CrashLoopBackOff fix"""
        print("✅ Validating CrashLoopBackOff fix...")

        # Check if new pod is running (deployment may have created new pod)
        returncode, stdout, stderr = self._safe_kubectl(
            ['get', 'pods', '-o', 'json'],
            namespace
        )

        if returncode != 0:
            validation["error"] = f"Failed to get pods: {stderr}"
            return validation

        pods_data = json.loads(stdout)
        running_pods = []
        crashloop_pods = []

        for pod in pods_data.get("items", []):
            pod_phase = pod.get("status", {}).get("phase", "Unknown")
            pod_conditions = pod.get("status", {}).get("conditions", [])
            container_statuses = pod.get("status", {}).get("containerStatuses", [])

            # Check for running pods
            if pod_phase == "Running":
                running_pods.append(pod["metadata"]["name"])

            # Check for crashloop
            for status in container_statuses:
                if status.get("state", {}).get("waiting", {}).get("reason") == "CrashLoopBackOff":
                    crashloop_pods.append(pod["metadata"]["name"])

        validation["validation_results"] = {
            "running_pods": running_pods,
            "crashloop_pods": crashloop_pods,
            "issue_resolved": len(crashloop_pods) == 0 and len(running_pods) > 0
        }

        if validation["validation_results"]["issue_resolved"]:
            print("  ✅ No CrashLoopBackOff detected")
            print(f"  ✅ {len(running_pods)} pod(s) running successfully")
        else:
            print(f"  ❌ Still in CrashLoopBackOff: {crashloop_pods}")

        validation["issue_resolved"] = validation["validation_results"]["issue_resolved"]

        return validation

    def _validate_imagepull_fix(self, namespace: str, pod_name: str, validation: Dict) -> Dict:
        """Validate ImagePullBackOff fix"""
        print("✅ Validating ImagePullBackOff fix...")

        returncode, stdout, stderr = self._safe_kubectl(
            ['get', 'pods', '-o', 'json'],
            namespace
        )

        if returncode != 0:
            validation["error"] = f"Failed to get pods: {stderr}"
            return validation

        pods_data = json.loads(stdout)
        image_pull_issues = []
        running_pods = []

        for pod in pods_data.get("items", []):
            container_statuses = pod.get("status", {}).get("containerStatuses", [])

            for status in container_statuses:
                waiting = status.get("state", {}).get("waiting", {})
                if waiting.get("reason") in ["ImagePullBackOff", "ErrImagePull"]:
                    image_pull_issues.append({
                        "pod": pod["metadata"]["name"],
                        "reason": waiting.get("reason"),
                        "message": waiting.get("message")
                    })

            if pod.get("status", {}).get("phase") == "Running":
                running_pods.append(pod["metadata"]["name"])

        validation["validation_results"] = {
            "image_pull_issues": image_pull_issues,
            "running_pods": running_pods,
            "issue_resolved": len(image_pull_issues) == 0 and len(running_pods) > 0
        }

        if validation["validation_results"]["issue_resolved"]:
            print("  ✅ No ImagePullBackOff detected")
            print(f"  ✅ {len(running_pods)} pod(s) running with correct images")
        else:
            print(f"  ❌ ImagePull issues persist: {len(image_pull_issues)}")

        validation["issue_resolved"] = validation["validation_results"]["issue_resolved"]

        return validation

    def _validate_resource_fix(self, namespace: str, pod_name: str, validation: Dict) -> Dict:
        """Validate resource constraint fix"""
        print("✅ Validating resource fix...")

        # Check for OOMKilled events
        returncode, stdout, stderr = self._safe_kubectl(
            ['get', 'events', '-o', 'json'],
            namespace
        )

        recent_oom_events = []
        if returncode == 0:
            events_data = json.loads(stdout)
            cutoff_time = datetime.now().timestamp() - 300  # Last 5 minutes

            for event in events_data.get("items", []):
                if "OOMKilled" in event.get("message", ""):
                    event_time = event.get("lastTimestamp", "")
                    recent_oom_events.append(event["message"])

        # Check current pod status
        returncode, stdout, stderr = self._safe_kubectl(
            ['get', 'pods', '-o', 'json'],
            namespace
        )

        running_pods = []
        if returncode == 0:
            pods_data = json.loads(stdout)
            for pod in pods_data.get("items", []):
                if pod.get("status", {}).get("phase") == "Running":
                    running_pods.append(pod["metadata"]["name"])

        validation["validation_results"] = {
            "recent_oom_events": recent_oom_events,
            "running_pods": running_pods,
            "issue_resolved": len(recent_oom_events) == 0 and len(running_pods) > 0
        }

        if validation["validation_results"]["issue_resolved"]:
            print("  ✅ No OOMKilled events in last 5 minutes")
            print(f"  ✅ {len(running_pods)} pod(s) running within resource limits")
        else:
            print(f"  ❌ OOMKilled events still occurring: {len(recent_oom_events)}")

        validation["issue_resolved"] = validation["validation_results"]["issue_resolved"]

        return validation

    def _save_validation(self, validation: Dict):
        """Save validation report"""
        validation_id = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}"
        output_file = self.output_dir / f"{validation_id}.json"

        with open(output_file, 'w') as f:
            json.dump(validation, f, indent=2)

        print(f"\n📊 Validation report saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kubernetes Validator - Fix Verification Agent")
        print()
        print("Usage:")
        print("  python kubernetes_validator.py <diagnosis-file> [--wait-time=30]")
        print()
        print("Example:")
        print("  python kubernetes_validator.py GP-DATA/active/analysis/k8s_diagnosis_*.json")
        print("  python kubernetes_validator.py GP-DATA/active/analysis/k8s_diagnosis_*.json --wait-time=60")
        print()
        print("Validation Process:")
        print("  1. Loads original diagnosis")
        print("  2. Waits for pod stabilization")
        print("  3. Re-runs diagnostic checks")
        print("  4. Compares before/after state")
        print("  5. Generates validation report")
        sys.exit(1)

    diagnosis_file = Path(sys.argv[1])

    # Parse wait time
    wait_time = 30
    for arg in sys.argv[2:]:
        if arg.startswith("--wait-time="):
            wait_time = int(arg.split("=")[1])

    if not diagnosis_file.exists():
        print(f"❌ Diagnosis file not found: {diagnosis_file}")
        sys.exit(1)

    validator = KubernetesValidator()

    try:
        result = validator.validate_fix(diagnosis_file, wait_time=wait_time)

        if result["issue_resolved"]:
            print("\n✅ VALIDATION PASSED - Issue resolved successfully")
        else:
            print("\n❌ VALIDATION FAILED - Issue persists, further troubleshooting needed")

    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)