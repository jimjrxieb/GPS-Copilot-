#!/usr/bin/env python3
"""
Gatekeeper Audit Agent
Step 2: Daily Kubernetes Audit - Surface Live Violations

Scans live cluster for policy violations using Gatekeeper audit mode.
Runs daily to find resources that violate policies but were created before enforcement.
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class GatekeeperAuditAgent:
    """
    Daily audit runner for Gatekeeper - surfaces violations in live clusters.

    Workflow:
    1. Query Gatekeeper audit results (kubectl get constraints)
    2. Parse violations from all ConstraintTemplates
    3. Group by severity and resource type
    4. Generate audit report
    5. Trigger PR bot for auto-remediation
    """

    def __init__(self, kubeconfig: Optional[str] = None):
        self.kubectl_path = self._find_kubectl()
        self.kubeconfig = kubeconfig  # Optional: use specific kubeconfig

    def _find_kubectl(self) -> str:
        """Locate kubectl binary"""
        if shutil.which("kubectl"):
            return "kubectl"
        raise RuntimeError("kubectl not installed")

    def _kubectl(self, args: List[str], namespace: Optional[str] = None) -> subprocess.CompletedProcess:
        """Run kubectl command"""
        cmd = [self.kubectl_path]
        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        if namespace:
            cmd.extend(["-n", namespace])
        cmd.extend(args)

        return subprocess.run(cmd, capture_output=True, text=True)

    def check_gatekeeper_installed(self) -> bool:
        """Verify Gatekeeper is installed in cluster"""
        result = self._kubectl(["get", "ns", "gatekeeper-system"])
        return result.returncode == 0

    def get_all_constraints(self) -> List[Dict]:
        """Get all Constraint resources (instances of ConstraintTemplates)"""
        # Common Gatekeeper constraint kinds
        constraint_kinds = [
            "K8sDenyPrivileged",
            "K8sRequireNonRoot",
            "K8sRequireResourceLimits",
            "K8sRequireLabels",
            "K8sBlockHostNamespace",
            "K8sNoHostPath"
        ]

        all_constraints = []

        for kind in constraint_kinds:
            result = self._kubectl(["get", kind, "-o", "json", "--all-namespaces"])
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    items = data.get("items", [])
                    all_constraints.extend(items)
                except json.JSONDecodeError:
                    continue

        return all_constraints

    def audit_violations(self) -> Dict:
        """
        Run audit on live cluster - find all Gatekeeper violations

        Returns:
            {
                "total_violations": int,
                "violations_by_severity": {"critical": [...], "high": [...], ...},
                "violations_by_namespace": {"default": [...], ...},
                "violations_by_constraint": {"K8sDenyPrivileged": [...], ...},
                "timestamp": "2025-10-03T..."
            }
        """
        print("[Gatekeeper Audit] Scanning cluster for policy violations...")

        if not self.check_gatekeeper_installed():
            return {
                "error": "Gatekeeper not installed. Install with: kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.15/deploy/gatekeeper.yaml",
                "timestamp": datetime.now().isoformat()
            }

        constraints = self.get_all_constraints()

        violations = []
        violations_by_severity = {"critical": [], "high": [], "medium": [], "low": []}
        violations_by_namespace = {}
        violations_by_constraint = {}

        for constraint in constraints:
            kind = constraint.get("kind", "")
            name = constraint.get("metadata", {}).get("name", "")
            status = constraint.get("status", {})

            # Parse violations from status
            audit_violations = status.get("violations", [])
            total_violations = status.get("totalViolations", 0)

            if total_violations > 0:
                for violation in audit_violations:
                    enforcement_action = violation.get("enforcementAction", "deny")
                    message = violation.get("message", "")
                    resource_name = violation.get("name", "")
                    resource_namespace = violation.get("namespace", "")
                    resource_kind = violation.get("kind", "")

                    # Determine severity based on constraint type
                    severity = self._get_severity(kind)

                    violation_entry = {
                        "constraint_kind": kind,
                        "constraint_name": name,
                        "severity": severity,
                        "enforcement_action": enforcement_action,
                        "message": message,
                        "resource": {
                            "kind": resource_kind,
                            "name": resource_name,
                            "namespace": resource_namespace
                        }
                    }

                    violations.append(violation_entry)
                    violations_by_severity[severity].append(violation_entry)

                    # Group by namespace
                    if resource_namespace not in violations_by_namespace:
                        violations_by_namespace[resource_namespace] = []
                    violations_by_namespace[resource_namespace].append(violation_entry)

                    # Group by constraint
                    if kind not in violations_by_constraint:
                        violations_by_constraint[kind] = []
                    violations_by_constraint[kind].append(violation_entry)

        result = {
            "total_violations": len(violations),
            "violations": violations,
            "violations_by_severity": violations_by_severity,
            "violations_by_namespace": violations_by_namespace,
            "violations_by_constraint": violations_by_constraint,
            "timestamp": datetime.now().isoformat()
        }

        return result

    def _get_severity(self, constraint_kind: str) -> str:
        """Map constraint kind to severity level"""
        critical_constraints = ["K8sDenyPrivileged", "K8sRequireNonRoot", "K8sBlockHostNamespace"]
        high_constraints = ["K8sRequireResourceLimits", "K8sNoHostPath"]

        if constraint_kind in critical_constraints:
            return "critical"
        elif constraint_kind in high_constraints:
            return "high"
        else:
            return "medium"

    def generate_audit_report(self, output_file: Optional[Path] = None) -> str:
        """Generate human-readable audit report"""
        audit_result = self.audit_violations()

        report_lines = [
            "=" * 80,
            "GATEKEEPER DAILY AUDIT REPORT",
            f"Generated: {audit_result['timestamp']}",
            "=" * 80,
            "",
            f"Total Violations: {audit_result['total_violations']}",
            ""
        ]

        # Summary by severity
        report_lines.append("Violations by Severity:")
        for severity, violations in audit_result["violations_by_severity"].items():
            if violations:
                report_lines.append(f"  {severity.upper()}: {len(violations)}")

        report_lines.append("")

        # Detailed violations
        if audit_result["total_violations"] > 0:
            report_lines.append("Detailed Violations:")
            report_lines.append("-" * 80)

            for violation in audit_result["violations"]:
                report_lines.append(f"\n[{violation['severity'].upper()}] {violation['constraint_kind']}")
                report_lines.append(f"  Resource: {violation['resource']['kind']}/{violation['resource']['name']}")
                report_lines.append(f"  Namespace: {violation['resource']['namespace']}")
                report_lines.append(f"  Message: {violation['message']}")
                report_lines.append(f"  Enforcement: {violation['enforcement_action']}")

        else:
            report_lines.append("✅ No violations found!")

        report_lines.append("")
        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_file:
            output_file.write_text(report)
            print(f"[Gatekeeper Audit] Report saved to {output_file}")

        return report


def main():
    """CLI entrypoint - run daily audit"""
    import sys

    agent = GatekeeperAuditAgent()

    # Generate report
    output_dir = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active/audit")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = output_dir / f"gatekeeper_audit_{timestamp}.txt"

    report = agent.generate_audit_report(output_file)
    print(report)

    # Get violations for triggering PR bot
    audit_result = agent.audit_violations()

    if audit_result.get("total_violations", 0) > 0:
        print(f"\n⚠️  Found {audit_result['total_violations']} violations!")
        print("Run pr_bot_agent.py to generate automated fixes")
        sys.exit(1)
    else:
        print("\n✅ Cluster is compliant!")
        sys.exit(0)


if __name__ == "__main__":
    main()