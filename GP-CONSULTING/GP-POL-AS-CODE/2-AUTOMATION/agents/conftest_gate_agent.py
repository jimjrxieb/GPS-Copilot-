#!/usr/bin/env python3
"""
Conftest Gate Agent
Step 1: OPA + Gatekeeper Codification - Terraform Plan-Time Validation

Denies bad builds by default using Rego policies at CI time (shift-left).
"""

import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ConftestGateAgent:
    """
    CI/CD gate using Conftest to validate Terraform plans against OPA policies.

    Workflow:
    1. terraform plan -out=plan.tfplan
    2. terraform show -json plan.tfplan > plan.json
    3. conftest test plan.json --policy ./1-POLICIES/opa/
    4. Fail pipeline if violations found
    """

    def __init__(self, policy_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.conftest_path = self._find_conftest()
        self.terraform_path = self._find_terraform()

        # Policy directory
        if policy_dir:
            self.policy_dir = policy_dir
        else:
            self.policy_dir = Path(__file__).resolve().parent.parent.parent / "1-POLICIES" / "opa"

        if not self.policy_dir.exists():
            raise RuntimeError(f"Policy directory not found: {self.policy_dir}")

        # Output directory (GP-DATA/active/scans/)
        if output_dir:
            self.output_dir = output_dir
        else:
            gp_copilot_root = Path(__file__).resolve().parent.parent.parent.parent.parent
            self.output_dir = gp_copilot_root / "GP-DATA" / "active" / "scans" / "conftest"

        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _find_conftest(self) -> str:
        """Locate conftest binary"""
        if shutil.which("conftest"):
            return "conftest"

        # Try installing if not found
        print("Conftest not found. Install with:")
        print("curl -L -o conftest.tar.gz https://github.com/open-policy-agent/conftest/releases/download/v0.49.1/conftest_0.49.1_Linux_x86_64.tar.gz")
        print("tar xzf conftest.tar.gz && sudo mv conftest /usr/local/bin/")
        raise RuntimeError("Conftest not installed")

    def _find_terraform(self) -> str:
        """Locate terraform binary"""
        if shutil.which("terraform"):
            return "terraform"
        raise RuntimeError("Terraform not installed")

    def validate_terraform_plan(self, terraform_dir: Path, workspace: str = "default") -> Dict:
        """
        Run Terraform plan and validate against OPA policies

        Args:
            terraform_dir: Directory containing Terraform configuration
            workspace: Terraform workspace (default, staging, production)

        Returns:
            {
                "passed": bool,
                "violations": [...],
                "warnings": [...],
                "plan_file": "path/to/plan.json",
                "timestamp": "2025-10-03T..."
            }
        """
        print(f"[Conftest Gate] Validating Terraform in {terraform_dir} (workspace: {workspace})")

        # Step 1: terraform init
        init_result = subprocess.run(
            [self.terraform_path, "init", "-input=false"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        if init_result.returncode != 0:
            return {
                "passed": False,
                "error": f"terraform init failed: {init_result.stderr}",
                "timestamp": datetime.now().isoformat()
            }

        # Step 2: terraform plan
        plan_file = terraform_dir / "plan.tfplan"
        plan_result = subprocess.run(
            [self.terraform_path, "plan", "-out", str(plan_file), "-input=false"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        if plan_result.returncode not in [0, 2]:  # 0 = no changes, 2 = changes planned
            return {
                "passed": False,
                "error": f"terraform plan failed: {plan_result.stderr}",
                "timestamp": datetime.now().isoformat()
            }

        # Step 3: terraform show -json
        plan_json_file = terraform_dir / "plan.json"
        show_result = subprocess.run(
            [self.terraform_path, "show", "-json", str(plan_file)],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        if show_result.returncode != 0:
            return {
                "passed": False,
                "error": f"terraform show failed: {show_result.stderr}",
                "timestamp": datetime.now().isoformat()
            }

        plan_json_file.write_text(show_result.stdout)

        # Step 4: conftest test
        conftest_result = subprocess.run(
            [
                self.conftest_path, "test",
                str(plan_json_file),
                "--policy", str(self.policy_dir),
                "--namespace", "terraform",
                "--output", "json"
            ],
            capture_output=True,
            text=True
        )

        # Parse conftest output
        violations = []
        warnings = []

        try:
            results = json.loads(conftest_result.stdout) if conftest_result.stdout else []
            for result in results:
                for failure in result.get("failures", []):
                    violations.append({
                        "policy": failure.get("metadata", {}).get("policy", "unknown"),
                        "msg": failure.get("msg", ""),
                        "file": result.get("filename", "")
                    })
                for warning in result.get("warnings", []):
                    warnings.append({
                        "policy": warning.get("metadata", {}).get("policy", "unknown"),
                        "msg": warning.get("msg", ""),
                        "file": result.get("filename", "")
                    })
        except json.JSONDecodeError:
            # Conftest returned non-JSON (likely empty)
            pass

        passed = conftest_result.returncode == 0 and len(violations) == 0

        result = {
            "passed": passed,
            "violations": violations,
            "warnings": warnings,
            "plan_file": str(plan_json_file),
            "timestamp": datetime.now().isoformat(),
            "terraform_dir": str(terraform_dir),
            "workspace": workspace
        }

        # Save results to GP-DATA
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = terraform_dir.name
        output_file = self.output_dir / f"{project_name}_{timestamp}.json"
        output_file.write_text(json.dumps(result, indent=2))
        print(f"[Conftest Gate] Results saved to {output_file}")

        # Also save a human-readable report
        report_file = self.output_dir / f"{project_name}_{timestamp}_report.txt"
        report_lines = [
            "=" * 80,
            "CONFTEST GATE SCAN REPORT",
            f"Project: {project_name}",
            f"Directory: {terraform_dir}",
            f"Timestamp: {result['timestamp']}",
            "=" * 80,
            "",
            f"Result: {'PASSED ✅' if passed else 'FAILED ❌'}",
            f"Violations: {len(violations)}",
            f"Warnings: {len(warnings)}",
            ""
        ]

        if violations:
            report_lines.append("VIOLATIONS:")
            report_lines.append("-" * 80)
            for v in violations:
                report_lines.append(f"  [{v['policy']}] {v['msg']}")
                report_lines.append(f"  File: {v['file']}")
                report_lines.append("")

        if warnings:
            report_lines.append("WARNINGS:")
            report_lines.append("-" * 80)
            for w in warnings:
                report_lines.append(f"  [{w['policy']}] {w['msg']}")
                report_lines.append(f"  File: {w['file']}")
                report_lines.append("")

        report_lines.append("=" * 80)
        report_file.write_text("\n".join(report_lines))
        print(f"[Conftest Gate] Report saved to {report_file}")

        # Cleanup
        if plan_file.exists():
            plan_file.unlink()

        return result

    def ci_gate(self, terraform_dir: Path, fail_on_violations: bool = True) -> bool:
        """
        CI/CD gate - fail pipeline if violations found

        Returns:
            True if passed, False if violations
        """
        result = self.validate_terraform_plan(terraform_dir)

        if not result.get("passed"):
            print("\n❌ CONFTEST GATE FAILED")
            print(f"Found {len(result.get('violations', []))} violations:")
            for v in result.get("violations", []):
                print(f"  - [{v['policy']}] {v['msg']}")

            if fail_on_violations:
                return False

        if result.get("warnings"):
            print(f"\n⚠️  {len(result['warnings'])} warnings:")
            for w in result.get("warnings", []):
                print(f"  - [{w['policy']}] {w['msg']}")

        print("\n✅ CONFTEST GATE PASSED")
        return True


def main():
    """CLI entrypoint"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: conftest_gate_agent.py <terraform_dir>")
        sys.exit(1)

    terraform_dir = Path(sys.argv[1])
    if not terraform_dir.exists():
        print(f"Error: {terraform_dir} does not exist")
        sys.exit(1)

    agent = ConftestGateAgent()
    passed = agent.ci_gate(terraform_dir)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()