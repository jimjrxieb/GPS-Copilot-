#!/usr/bin/env python3
"""
🖖 PHASE 3 FIXER: Kubernetes Security Hardening
Hardens Kubernetes deployments by fixing container security contexts,
adding resource limits, and removing dangerous configurations

CIS Kubernetes Benchmark: 5.2.x, 5.7.x
PCI-DSS: 2.2
NIST 800-190: Container Security
"""

import re
import yaml
import argparse
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class KubernetesSecurityHardener:
    """Harden Kubernetes deployments for production security"""

    def __init__(self, target_file: Path, validate: bool = False, namespace: str = "securebank"):
        self.target_file = target_file
        self.backup_file = None
        self.fixes_applied = []
        self.validate = validate
        self.namespace = namespace
        self.validation_results = {}

    def backup(self):
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_file = self.target_file.parent / f"{self.target_file.name}.backup.{timestamp}"
        self.backup_file.write_text(self.target_file.read_text())
        print(f"✅ Backup created: {self.backup_file}")

    def harden_security_context(self, content: str) -> str:
        """Fix container security contexts"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Fix runAsUser: 0 (root)
            if 'runAsUser: 0' in line or 'runAsUser:0' in line:
                self.fixes_applied.append({
                    'line': i + 1,
                    'type': 'Root user removed',
                    'original': line.strip()
                })
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + 'runAsUser: 10000  # ✅ FIXED: Non-root user (Phase 3)')
                fixed_lines.append(' ' * indent + '# ' + line.strip() + ' - REMOVED: Running as root')
                i += 1
                continue

            # Fix privileged: true
            if 'privileged: true' in line:
                self.fixes_applied.append({
                    'line': i + 1,
                    'type': 'Privileged mode disabled',
                    'original': line.strip()
                })
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + 'privileged: false  # ✅ FIXED: Disabled privileged mode (Phase 3)')
                fixed_lines.append(' ' * indent + '# ' + line.strip() + ' - REMOVED: Privileged container')
                i += 1
                continue

            # Fix allowPrivilegeEscalation: true
            if 'allowPrivilegeEscalation: true' in line:
                self.fixes_applied.append({
                    'line': i + 1,
                    'type': 'Privilege escalation blocked',
                    'original': line.strip()
                })
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + 'allowPrivilegeEscalation: false  # ✅ FIXED: Blocked privilege escalation (Phase 3)')
                i += 1
                continue

            # Remove dangerous capabilities
            if 'add:' in line and i + 1 < len(lines):
                # Check if next lines have dangerous capabilities
                j = i + 1
                caps_to_remove = []
                while j < len(lines) and lines[j].strip().startswith('-'):
                    cap_line = lines[j].strip()
                    if any(danger in cap_line for danger in ['NET_ADMIN', 'SYS_ADMIN', 'SYS_PTRACE', 'SYS_MODULE']):
                        caps_to_remove.append(j)
                    j += 1

                if caps_to_remove:
                    self.fixes_applied.append({
                        'line': i + 1,
                        'type': f'Removed {len(caps_to_remove)} dangerous capabilities',
                        'original': 'capabilities.add section'
                    })
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * indent + '# ✅ FIXED: Dangerous capabilities removed (Phase 3)')
                    fixed_lines.append(' ' * indent + '# add:  - REMOVED: NET_ADMIN, SYS_ADMIN, SYS_PTRACE')
                    # Skip the capability lines
                    i = j
                    continue

            # Remove hostPath volumes
            if 'hostPath:' in line:
                self.fixes_applied.append({
                    'line': i + 1,
                    'type': 'hostPath volume removed',
                    'original': line.strip()
                })
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + '# ❌ REMOVED: hostPath volume (Phase 3)')
                fixed_lines.append(' ' * indent + '# ' + line.strip() + ' - Security risk: host filesystem access')

                # Skip next lines until we're out of this volume definition
                j = i + 1
                while j < len(lines) and len(lines[j]) - len(lines[j].lstrip()) > indent:
                    fixed_lines.append(' ' * indent + '# ' + lines[j].strip())
                    j += 1
                i = j
                continue

            fixed_lines.append(line)
            i += 1

        return '\n'.join(fixed_lines)

    def add_security_context(self, content: str) -> str:
        """Add missing securityContext blocks"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # After "containers:" add securityContext if missing
            if 'containers:' in line and i + 1 < len(lines):
                fixed_lines.append(line)

                # Check if next section has securityContext
                j = i + 1
                has_security_context = False
                container_indent = 0

                # Find the container definition
                while j < len(lines) and j < i + 20:  # Look ahead 20 lines
                    if 'securityContext:' in lines[j]:
                        has_security_context = True
                        break
                    if '- name:' in lines[j]:  # Next container
                        container_indent = len(lines[j]) - len(lines[j].lstrip())
                        break
                    j += 1

                if not has_security_context and container_indent > 0:
                    self.fixes_applied.append({
                        'line': i + 1,
                        'type': 'Added secure securityContext',
                        'original': 'Missing securityContext'
                    })

                    # Add secure securityContext
                    indent = ' ' * (container_indent + 2)
                    i += 1  # Move past containers line
                    fixed_lines.append(lines[i])  # Add "- name:" line
                    i += 1

                    # Insert securityContext
                    fixed_lines.append(indent + '# ✅ ADDED: Secure security context (Phase 3)')
                    fixed_lines.append(indent + 'securityContext:')
                    fixed_lines.append(indent + '  runAsNonRoot: true')
                    fixed_lines.append(indent + '  runAsUser: 10000')
                    fixed_lines.append(indent + '  readOnlyRootFilesystem: true')
                    fixed_lines.append(indent + '  allowPrivilegeEscalation: false')
                    fixed_lines.append(indent + '  capabilities:')
                    fixed_lines.append(indent + '    drop:')
                    fixed_lines.append(indent + '    - ALL')
                    continue

            fixed_lines.append(line)
            i += 1

        return '\n'.join(fixed_lines)

    def add_resource_limits(self, content: str) -> str:
        """Add resource limits to containers"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # After container name, check for resources
            if '- name:' in line and 'container' in line.lower():
                fixed_lines.append(line)

                # Check if resources exist
                j = i + 1
                has_resources = False
                container_indent = len(line) - len(line.lstrip())

                while j < len(lines) and j < i + 30:
                    if 'resources:' in lines[j]:
                        has_resources = True
                        break
                    if '- name:' in lines[j]:  # Next container
                        break
                    j += 1

                if not has_resources:
                    self.fixes_applied.append({
                        'line': i + 1,
                        'type': 'Added resource limits',
                        'original': 'Missing resources'
                    })

                    # Add after the next line (usually image or ports)
                    i += 1
                    fixed_lines.append(lines[i])

                    # Insert resources
                    indent = ' ' * (container_indent + 2)
                    fixed_lines.append(indent + '# ✅ ADDED: Resource limits (Phase 3)')
                    fixed_lines.append(indent + 'resources:')
                    fixed_lines.append(indent + '  requests:')
                    fixed_lines.append(indent + '    memory: "128Mi"')
                    fixed_lines.append(indent + '    cpu: "100m"')
                    fixed_lines.append(indent + '  limits:')
                    fixed_lines.append(indent + '    memory: "512Mi"')
                    fixed_lines.append(indent + '    cpu: "500m"')
                    i += 1
                    continue

            fixed_lines.append(line)
            i += 1

        return '\n'.join(fixed_lines)

    def add_network_policy(self) -> Path:
        """Create NetworkPolicy manifest"""
        network_policy = """---
# ============================================================================
# NETWORK POLICY - PHASE 3 HARDENING
# ============================================================================
# Created by kubernetes_security_hardening.py
# Date: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
#
# Compliance:
# - CIS Kubernetes 5.3.2: Network segmentation
# - PCI-DSS 1.2.1: Network traffic restriction
# - Zero Trust: Default deny with explicit allow
# ============================================================================
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: securebank-network-policy
  namespace: securebank
spec:
  podSelector:
    matchLabels:
      app: securebank-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow from frontend
  - from:
    - podSelector:
        matchLabels:
          app: securebank-frontend
    ports:
    - protocol: TCP
      port: 3000
  egress:
  # Allow to PostgreSQL
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  # Allow to Redis
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  # Allow DNS
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53

---
# Frontend NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: securebank-frontend-policy
  namespace: securebank
spec:
  podSelector:
    matchLabels:
      app: securebank-frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow from anywhere (LoadBalancer)
  - from: []
    ports:
    - protocol: TCP
      port: 3000
  egress:
  # Allow to backend
  - to:
    - podSelector:
        matchLabels:
          app: securebank-backend
    ports:
    - protocol: TCP
      port: 3000
  # Allow DNS
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53

---
# Database NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgres-network-policy
  namespace: securebank
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Only allow from backend
  - from:
    - podSelector:
        matchLabels:
          app: securebank-backend
    ports:
    - protocol: TCP
      port: 5432
  egress:
  # Allow DNS only
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
"""

        network_policy_file = self.target_file.parent / "network-policy.yaml"
        network_policy_file.write_text(network_policy)
        print(f"✅ NetworkPolicy created: {network_policy_file}")

        self.fixes_applied.append({
            'line': 0,
            'type': 'NetworkPolicy created',
            'original': 'No NetworkPolicy'
        })

        return network_policy_file

    def run_kubectl(self, command: List[str]) -> Optional[dict]:
        """Run kubectl command and return output"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def validate_deployment(self) -> dict:
        """Validate the hardened deployment by applying and checking pod status"""
        print("\n" + "="*70)
        print("🔍 DEPLOYMENT VALIDATION - Phase 3")
        print("="*70)

        validation_results = {
            "success": False,
            "pods_checked": 0,
            "pods_ready": 0,
            "issues_found": [],
            "recommendations": []
        }

        print(f"\n📦 Applying hardened deployment to namespace: {self.namespace}")

        # Apply the hardened deployment
        result = self.run_kubectl(["kubectl", "apply", "-f", str(self.target_file)])
        if not result["success"]:
            validation_results["issues_found"].append({
                "type": "kubectl_apply_failed",
                "message": f"Failed to apply deployment: {result['stderr']}"
            })
            return validation_results

        print("✅ Deployment applied successfully")

        # Wait for pods to be created
        print("\n⏳ Waiting 15 seconds for pods to initialize...")
        time.sleep(15)

        # Get pod status
        print("\n🔍 Checking pod status...")
        result = self.run_kubectl([
            "kubectl", "get", "pods",
            "-n", self.namespace,
            "-o", "json"
        ])

        if not result["success"]:
            validation_results["issues_found"].append({
                "type": "get_pods_failed",
                "message": "Failed to get pod status"
            })
            return validation_results

        try:
            pods_data = json.loads(result["stdout"])
            pods = pods_data.get("items", [])
            validation_results["pods_checked"] = len(pods)

            for pod in pods:
                pod_name = pod["metadata"]["name"]
                pod_status = pod["status"]["phase"]

                # Check container statuses
                container_statuses = pod["status"].get("containerStatuses", [])

                for container in container_statuses:
                    container_name = container["name"]
                    ready = container["ready"]

                    if ready:
                        validation_results["pods_ready"] += 1
                        print(f"   ✅ {pod_name}/{container_name}: Ready")
                    else:
                        print(f"   ❌ {pod_name}/{container_name}: Not Ready")

                        # Check for specific issues
                        state = container.get("state", {})

                        # CrashLoopBackOff
                        if "waiting" in state:
                            reason = state["waiting"].get("reason", "")
                            message = state["waiting"].get("message", "")

                            if "CrashLoopBackOff" in reason or "Error" in reason:
                                # Get logs
                                log_result = self.run_kubectl([
                                    "kubectl", "logs", pod_name,
                                    "-n", self.namespace,
                                    "-c", container_name,
                                    "--tail=20"
                                ])

                                logs = log_result.get("stdout", "") if log_result else ""

                                issue = {
                                    "type": "CrashLoopBackOff",
                                    "pod": pod_name,
                                    "container": container_name,
                                    "reason": reason,
                                    "message": message,
                                    "logs": logs
                                }

                                # Analyze logs for common issues
                                recommendations = self.analyze_pod_failure(logs, container_name)
                                issue["recommendations"] = recommendations

                                validation_results["issues_found"].append(issue)
                                validation_results["recommendations"].extend(recommendations)

            # Overall success if more than 50% pods are ready
            if validation_results["pods_checked"] > 0:
                ready_percentage = (validation_results["pods_ready"] / validation_results["pods_checked"]) * 100
                validation_results["success"] = ready_percentage >= 50
                validation_results["ready_percentage"] = ready_percentage

        except json.JSONDecodeError as e:
            validation_results["issues_found"].append({
                "type": "json_parse_error",
                "message": f"Failed to parse pod data: {str(e)}"
            })

        return validation_results

    def analyze_pod_failure(self, logs: str, container_name: str) -> List[str]:
        """Analyze pod logs and provide recommendations"""
        recommendations = []

        # PostgreSQL specific issues
        if "postgres" in container_name.lower():
            if "could not change permissions" in logs or "Operation not permitted" in logs:
                recommendations.append({
                    "issue": "PostgreSQL permission errors",
                    "fix": "Add Pod-level securityContext with fsGroup: 999",
                    "example": """
spec:
  securityContext:
    fsGroup: 999
    runAsUser: 999
    runAsNonRoot: false"""
                })
                recommendations.append({
                    "issue": "PostgreSQL data directory permissions",
                    "fix": "Set PGDATA to subdirectory",
                    "example": """
env:
- name: PGDATA
  value: /var/lib/postgresql/data/pgdata"""
                })
                recommendations.append({
                    "issue": "PostgreSQL needs writable volumes",
                    "fix": "Add emptyDir volumes for /var/lib/postgresql/data, /var/run/postgresql, /tmp",
                    "example": """
volumeMounts:
- name: postgres-data
  mountPath: /var/lib/postgresql/data
- name: postgres-run
  mountPath: /var/run/postgresql
- name: postgres-tmp
  mountPath: /tmp
volumes:
- name: postgres-data
  emptyDir: {}
- name: postgres-run
  emptyDir: {}
- name: postgres-tmp
  emptyDir: {}"""
                })

            if "Read-only file system" in logs:
                recommendations.append({
                    "issue": "ReadOnlyRootFilesystem blocks PostgreSQL",
                    "fix": "Set readOnlyRootFilesystem: false for PostgreSQL",
                    "example": """
securityContext:
  readOnlyRootFilesystem: false"""
                })

        # Node.js / Backend issues
        if "backend" in container_name.lower() or "node" in logs:
            if "ECONNREFUSED" in logs:
                recommendations.append({
                    "issue": "Cannot connect to database",
                    "fix": "Ensure database is running and ready before backend starts",
                    "example": "Check database pod logs and status"
                })

            if "Read-only file system" in logs or "EROFS" in logs:
                recommendations.append({
                    "issue": "Node.js needs write access for logs/tmp",
                    "fix": "Either disable readOnlyRootFilesystem or add writable volumes",
                    "example": """
securityContext:
  readOnlyRootFilesystem: false
# OR add volumes:
volumeMounts:
- name: tmp
  mountPath: /tmp
- name: logs
  mountPath: /app/logs
volumes:
- name: tmp
  emptyDir: {}
- name: logs
  emptyDir: {}"""
                })

        # Secret/ConfigMap issues
        if "secret" in logs.lower() and ("not found" in logs or "NotFound" in logs):
            recommendations.append({
                "issue": "Kubernetes Secret not found",
                "fix": "Ensure all required Secrets exist before deploying",
                "example": "kubectl get secrets -n <namespace>"
            })

        # Image pull issues
        if "ImagePullBackOff" in logs or "ErrImagePull" in logs:
            recommendations.append({
                "issue": "Cannot pull container image",
                "fix": "Check image name and registry access",
                "example": "kubectl describe pod <pod-name>"
            })

        return recommendations

    def print_validation_report(self, validation_results: dict):
        """Print detailed validation report"""
        print("\n" + "="*70)
        print("📊 VALIDATION REPORT")
        print("="*70)

        print(f"\n✅ Pods Ready: {validation_results['pods_ready']}/{validation_results['pods_checked']}")
        if validation_results.get("ready_percentage"):
            print(f"📈 Success Rate: {validation_results['ready_percentage']:.1f}%")

        if validation_results["success"]:
            print("\n🎉 Validation PASSED - Majority of pods are running")
        else:
            print("\n⚠️  Validation FAILED - Issues detected")

        if validation_results["issues_found"]:
            print(f"\n❌ Issues Found: {len(validation_results['issues_found'])}")
            for i, issue in enumerate(validation_results["issues_found"], 1):
                print(f"\n   Issue #{i}:")
                print(f"   Type: {issue.get('type', 'Unknown')}")
                if issue.get("pod"):
                    print(f"   Pod: {issue['pod']}/{issue['container']}")
                if issue.get("reason"):
                    print(f"   Reason: {issue['reason']}")

                # Show recommendations
                if issue.get("recommendations"):
                    print(f"\n   💡 Recommendations:")
                    for rec in issue["recommendations"]:
                        print(f"\n      Issue: {rec['issue']}")
                        print(f"      Fix: {rec['fix']}")
                        if rec.get("example"):
                            print(f"      Example:\n{rec['example']}")

        # Show unique recommendations
        if validation_results["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS ({len(validation_results['recommendations'])} total)")
            print("="*70)

            # Deduplicate by issue
            seen_issues = set()
            for rec in validation_results["recommendations"]:
                if rec["issue"] not in seen_issues:
                    seen_issues.add(rec["issue"])
                    print(f"\n✓ {rec['issue']}")
                    print(f"  Fix: {rec['fix']}")

        print("\n" + "="*70)

    def fix(self) -> dict:
        """Execute the hardening"""
        print("🖖 Kubernetes Security Hardening - Phase 3")
        print("="*70)

        # Backup
        self.backup()

        # Read content
        content = self.target_file.read_text()

        # Apply fixes
        print("\n🔧 Applying security hardening...")

        content = self.harden_security_context(content)
        content = self.add_security_context(content)
        content = self.add_resource_limits(content)

        # Add header
        header = """# ============================================================================
# KUBERNETES DEPLOYMENT - HARDENED (PHASE 3)
# ============================================================================
# Security fixes applied: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
#
# Hardening applied:
# - Containers run as non-root (runAsUser: 10000)
# - Privileged mode disabled
# - Dangerous capabilities removed
# - Resource limits added
# - ReadOnlyRootFilesystem enabled
# - Privilege escalation blocked
#
# Compliance:
# - CIS Kubernetes 5.2.x: Container security
# - PCI-DSS 2.2: Configuration standards
# - NIST 800-190: Container security
# ============================================================================

"""
        content = header + content

        # Write fixed content
        self.target_file.write_text(content)

        # Create NetworkPolicy
        network_policy_file = self.add_network_policy()

        print(f"\n✅ Applied {len(self.fixes_applied)} security hardenings")

        if self.fixes_applied:
            print("\n📋 Hardening applied:")
            for fix in self.fixes_applied[:15]:
                print(f"   Line {fix['line']}: {fix['type']}")
            if len(self.fixes_applied) > 15:
                print(f"   ... and {len(self.fixes_applied) - 15} more")

        print(f"\n📊 Summary:")
        print(f"   Backup: {self.backup_file}")
        print(f"   Hardened file: {self.target_file}")
        print(f"   NetworkPolicy: {network_policy_file}")
        print(f"   Total fixes: {len(self.fixes_applied)}")

        # Run validation if requested
        if self.validate:
            validation_results = self.validate_deployment()
            self.print_validation_report(validation_results)

            return {
                "success": validation_results["success"],
                "fixes_applied": len(self.fixes_applied),
                "backup_file": str(self.backup_file),
                "network_policy_file": str(network_policy_file),
                "validation": validation_results
            }
        else:
            print("\n🚀 Next Steps:")
            print(f"   1. Review changes: diff {self.backup_file} {self.target_file}")
            print(f"   2. Apply NetworkPolicy: kubectl apply -f {network_policy_file}")
            print(f"   3. Apply hardened deployment: kubectl apply -f {self.target_file}")
            print(f"   4. Verify pods restart successfully")
            print(f"\n💡 Tip: Use --validate flag to automatically test the deployment")

            return {
                "success": True,
                "fixes_applied": len(self.fixes_applied),
                "backup_file": str(self.backup_file),
                "network_policy_file": str(network_policy_file)
            }

def main():
    parser = argparse.ArgumentParser(
        description="Kubernetes Security Hardening - Phase 3",
        epilog="""
Examples:
  # Basic hardening (no validation)
  python3 kubernetes_security_hardening.py --target deployment.yaml

  # Hardening with deployment validation
  python3 kubernetes_security_hardening.py --target deployment.yaml --validate

  # Specify custom namespace
  python3 kubernetes_security_hardening.py --target deployment.yaml --validate --namespace production
        """
    )
    parser.add_argument("--target", required=True, help="Target YAML file to harden")
    parser.add_argument("--validate", action="store_true",
                       help="Validate deployment after hardening by applying and checking pod status")
    parser.add_argument("--namespace", default="securebank",
                       help="Kubernetes namespace to deploy to (default: securebank)")
    args = parser.parse_args()

    target_file = Path(args.target)
    if not target_file.exists():
        print(f"❌ Target file not found: {target_file}")
        return 1

    hardener = KubernetesSecurityHardener(
        target_file,
        validate=args.validate,
        namespace=args.namespace
    )
    result = hardener.fix()

    if result["success"]:
        print(f"\n{'='*70}")
        if args.validate:
            print("✅ Kubernetes Security Hardening Complete with Validation!")
        else:
            print("✅ Kubernetes Security Hardening Complete!")
        print(f"{'='*70}")
        return 0
    else:
        print(f"\n{'='*70}")
        if args.validate:
            print("⚠️  Hardening complete but validation found issues")
            print("Review recommendations above and apply fixes")
        else:
            print("❌ Hardening failed")
        print(f"{'='*70}")
        return 1

if __name__ == "__main__":
    exit(main())
