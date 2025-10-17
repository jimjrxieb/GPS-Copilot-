#!/usr/bin/env python3
"""
Policy Agent - Autonomous Security Policy Orchestration

Coordinates security policy lifecycle:
1. Scan → Detect violations
2. Generate → Create preventive policies
3. Fix → Auto-remediate issues
4. Approve → Human-in-loop validation
5. Deploy → Apply to cluster/CI

This is an LLM-aware agent that can be called by Jade AI.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add paths for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/scanners"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/fixers"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/generators"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "GP-CONSULTING-AGENTS/GP-POL-AS-CODE/2-AUTOMATION/orchestrators"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "core"))

from opa_scanner import OpaScanner
from opa_fixer import OpaFixer
from opa_policy_generator import OpaPolicyGenerator


class PolicyAgent:
    """
    Autonomous agent for security policy lifecycle management

    This agent coordinates multiple tools to automate security:
    - Scanners (read-only analysis)
    - Generators (create new policies)
    - Fixers (auto-remediate violations)
    - Approval workflow (human-in-loop)

    Example usage:
        agent = PolicyAgent()
        results = agent.auto_remediate("/path/to/project")
    """

    def __init__(self, approval_required: bool = True):
        """
        Initialize policy agent with tools

        Args:
            approval_required: If True, fixes require human approval before applying
        """
        self.scanner = OpaScanner()
        self.fixer = OpaFixer()
        self.generator = OpaPolicyGenerator()
        self.approval_required = approval_required

        # Data directories (use dynamic path from config)
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "config"))
        from platform_config import get_config
        self.gp_data = get_config().get_data_directory()
        self.scan_dir = self.gp_data / "active" / "scans"
        self.fix_dir = self.gp_data / "active" / "fixes"
        self.policy_dir = self.gp_data / "active" / "policies" / "generated"

        # Create directories
        self.scan_dir.mkdir(parents=True, exist_ok=True)
        self.fix_dir.mkdir(parents=True, exist_ok=True)
        self.policy_dir.mkdir(parents=True, exist_ok=True)

    def auto_remediate(self, project_path: str, policy_package: str = "security") -> Dict:
        """
        Autonomous remediation workflow:
        1. Scan project for violations
        2. Generate fixes
        3. (Optional) Submit for approval
        4. Apply fixes
        5. Generate preventive policies

        Args:
            project_path: Path to project to scan/fix
            policy_package: OPA policy package to use

        Returns:
            Workflow results with all steps
        """
        workflow_id = f"remediate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"🤖 Policy Agent Starting: {workflow_id}")
        print(f"   Target: {project_path}")
        print(f"   Policy: {policy_package}")
        print(f"   Approval Required: {self.approval_required}")
        print()

        results = {
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "project_path": project_path,
            "policy_package": policy_package,
            "steps": {}
        }

        # Step 1: Scan
        print("📊 Step 1: Scanning for policy violations...")
        scan_results = self.scanner.scan(project_path, policy_package)

        if not scan_results or scan_results.get('summary', {}).get('total', 0) == 0:
            print("✅ No violations found! Project is compliant.")
            results["steps"]["scan"] = {"status": "clean", "violations": 0}
            return results

        violations_count = scan_results['summary']['total']
        print(f"   Found {violations_count} violations")

        # Save scan results
        scan_file = self.scan_dir / f"{workflow_id}_scan.json"
        with open(scan_file, 'w') as f:
            json.dump(scan_results, f, indent=2)

        results["steps"]["scan"] = {
            "status": "violations_found",
            "violations": violations_count,
            "severity": scan_results['summary']['severity_breakdown'],
            "scan_file": str(scan_file)
        }

        # Step 2: Generate Fixes
        print("\n🔧 Step 2: Generating automated fixes...")
        fix_results = self.fixer.fix_findings(
            str(scan_file),
            project_path,
            auto_fix=False  # Don't apply yet
        )

        fixes_count = len(fix_results.get('applied_fixes', []))
        skipped_count = len(fix_results.get('skipped_fixes', []))

        print(f"   Generated {fixes_count} automated fixes")
        print(f"   Skipped {skipped_count} (manual review needed)")

        results["steps"]["generate_fixes"] = {
            "status": "completed",
            "fixes_generated": fixes_count,
            "fixes_skipped": skipped_count
        }

        # Step 3: Approval (if required)
        if self.approval_required and fixes_count > 0:
            print("\n⏸️  Step 3: Waiting for human approval...")
            print(f"   Review fixes in: {self.fix_dir}")

            # In production, this would integrate with approval workflow
            # For now, we'll simulate approval
            approved = self._request_approval(fix_results)

            results["steps"]["approval"] = {
                "status": "approved" if approved else "rejected",
                "approved": approved
            }

            if not approved:
                print("❌ Fixes rejected. Workflow stopped.")
                return results
        else:
            print("\n⚡ Step 3: Auto-approval enabled, applying fixes...")
            results["steps"]["approval"] = {"status": "auto_approved"}

        # Step 4: Apply Fixes
        print("\n✨ Step 4: Applying fixes to project...")
        fix_results = self.fixer.fix_findings(
            str(scan_file),
            project_path,
            auto_fix=True  # Now apply
        )

        results["steps"]["apply_fixes"] = {
            "status": "completed",
            "files_modified": len(set(f['file'] for f in fix_results.get('applied_fixes', []))),
            "backups_created": len(fix_results.get('backup_files', []))
        }

        print(f"   Modified {results['steps']['apply_fixes']['files_modified']} files")
        print(f"   Created {results['steps']['apply_fixes']['backups_created']} backups")

        # Step 5: Generate Preventive Policies
        print("\n🛡️  Step 5: Generating preventive policies...")
        policies = self.generator.generate_from_violations(scan_results)

        if policies:
            print(f"   Generated {len(policies)} Gatekeeper policies")
            results["steps"]["generate_policies"] = {
                "status": "completed",
                "policies_generated": len(policies),
                "policy_files": policies
            }
        else:
            print("   No preventive policies needed")
            results["steps"]["generate_policies"] = {
                "status": "skipped",
                "reason": "No policy violations matched generator patterns"
            }

        # Save workflow results
        workflow_file = self.gp_data / "active" / "workflows" / f"{workflow_id}_results.json"
        workflow_file.parent.mkdir(parents=True, exist_ok=True)

        with open(workflow_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Workflow Complete!")
        print(f"   Results saved: {workflow_file}")

        return results

    def scan_only(self, project_path: str, policy_package: str = "security") -> Dict:
        """
        Just scan, don't fix (read-only analysis)

        Args:
            project_path: Path to project to scan
            policy_package: OPA policy package

        Returns:
            Scan results
        """
        print(f"🔍 Scanning: {project_path}")
        print(f"   Policy: {policy_package}")

        results = self.scanner.scan(project_path, policy_package)

        if results:
            total = results.get('summary', {}).get('total', 0)
            print(f"\n📊 Found {total} violations")

            severity = results['summary']['severity_breakdown']
            print(f"   Critical: {severity['critical']}")
            print(f"   High: {severity['high']}")
            print(f"   Medium: {severity['medium']}")
            print(f"   Low: {severity['low']}")

        return results

    def generate_gatekeeper_from_rego(self, rego_file: str) -> List[str]:
        """
        Generate Gatekeeper ConstraintTemplates from OPA Rego policies

        This is the HIGHEST VALUE automation for GuidePoint!

        Args:
            rego_file: Path to OPA .rego file

        Returns:
            List of generated ConstraintTemplate files
        """
        print(f"🔄 Converting OPA → Gatekeeper: {rego_file}")
        print("   This feature requires LLM (DeepSeek-Coder)")
        print("   Calling Jade AI engine...")

        # This would integrate with Jade AI's LLM
        # For now, return placeholder
        print("   ⚠️  LLM integration pending")
        return []

    def _request_approval(self, fix_results: Dict) -> bool:
        """
        Request human approval for fixes

        In production, this would:
        1. Create approval proposal in database
        2. Trigger notification (Slack, email)
        3. Wait for human approval via GUI
        4. Return approval status

        For now, we'll auto-approve in demo mode
        """
        print("\n📋 Fix Summary for Approval:")

        applied = fix_results.get('applied_fixes', [])
        skipped = fix_results.get('skipped_fixes', [])

        print(f"\n   Automated Fixes ({len(applied)}):")
        for fix in applied[:5]:  # Show first 5
            print(f"   ✓ {fix['fix_applied']}: {fix['description']}")
            print(f"     File: {fix['file']}")

        if len(applied) > 5:
            print(f"   ... and {len(applied) - 5} more")

        if skipped:
            print(f"\n   Manual Review Required ({len(skipped)}):")
            for skip in skipped[:3]:
                print(f"   ⚠️  {skip['policy']}")
                print(f"     Reason: {skip['reason']}")

        # In demo mode, auto-approve
        print("\n   [Demo Mode: Auto-approving]")
        return True

    def health_check(self) -> Dict:
        """Check agent tool availability"""
        return {
            "scanner": hasattr(self.scanner, 'tool_path') and Path(self.scanner.tool_path).exists(),
            "fixer": self.fixer is not None,
            "generator": self.generator is not None,
            "opa_policies": len(list(Path("1-POLICIES/opa").glob("*.rego"))) if Path("1-POLICIES/opa").exists() else 0,
            "gatekeeper_templates": len(list(Path("1-POLICIES/gatekeeper/templates").glob("*.yaml"))) if Path("1-POLICIES/gatekeeper/templates").exists() else 0
        }


def main():
    """CLI interface for PolicyAgent"""
    import argparse

    parser = argparse.ArgumentParser(description="Policy Agent - Autonomous Security Remediation")
    parser.add_argument("command", choices=["scan", "remediate", "health"])
    parser.add_argument("target", nargs="?", help="Project path to scan/fix")
    parser.add_argument("--policy", default="security", help="Policy package (default: security)")
    parser.add_argument("--no-approval", action="store_true", help="Skip approval step")

    args = parser.parse_args()

    agent = PolicyAgent(approval_required=not args.no_approval)

    if args.command == "scan":
        if not args.target:
            print("Error: target path required for scan")
            return 1
        results = agent.scan_only(args.target, args.policy)
        print(json.dumps(results, indent=2))

    elif args.command == "remediate":
        if not args.target:
            print("Error: target path required for remediate")
            return 1
        results = agent.auto_remediate(args.target, args.policy)
        print(json.dumps(results, indent=2))

    elif args.command == "health":
        status = agent.health_check()
        print(json.dumps(status, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())