#!/usr/bin/env python3
"""
OPA Manager - Comprehensive Open Policy Agent Integration

Integrates OPA scanner, server management, and automated policy generation
for complete security policy lifecycle management.

Components:
- OPA Scanner: Policy evaluation and compliance checking
- OPA Server: Runtime admission control for Kubernetes
- OPA Fixer: Automated policy generation and remediation
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Import our existing components
import sys
sys.path.append(str(Path(__file__).parent.parent))  # Go up to GP-POL-AS-CODE

from scanners.opa_scanner import OpaScanner
from fixers.opa_fixer import OpaFixer

class OPAManager:
    """Comprehensive OPA management system"""

    def __init__(self, config_dir: str = None):
        """Initialize OPA manager with scanner, server, and fixer"""
        self.config_dir = Path(config_dir) if config_dir else Path("/home/jimmie/linkops-industries/GP-copilot/GP-PLATFORM/config")
        self.data_dir = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DATA/active")
        self.docs_dir = Path("/home/jimmie/linkops-industries/GP-copilot/GP-DOCS")

        # Initialize components
        self.scanner = OpaScanner()
        self.fixer = OpaFixer()

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # OPA server state
        self.server_running = False
        self.policies_dir = self.config_dir / "opa-policies"
        self.policies_dir.mkdir(exist_ok=True)

    def scan_project(self, target: str) -> Dict:
        """Scan project for OPA policy compliance"""
        self.logger.info(f"Scanning project: {target}")

        # Run OPA scanner
        results = self.scanner.scan(target)

        if results:
            # Save scan results
            scan_file = self.data_dir / "scans" / f"opa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            scan_file.parent.mkdir(exist_ok=True)

            with open(scan_file, 'w') as f:
                json.dump(results, f, indent=2)

            self.logger.info(f"Scan results saved to: {scan_file}")

            # Also save formatted report to GP-DOCS
            self._save_formatted_report(results, target)

        return results

    def start_admission_control(self, policies_dir: str = None) -> bool:
        """Start OPA server for Kubernetes admission control"""
        if self.server_running:
            self.logger.info("OPA server already running")
            return True

        policies_path = policies_dir or str(self.policies_dir)

        self.logger.info(f"Starting OPA server with policies from: {policies_path}")
        success = self.scanner.start_opa_server(policies_path)

        if success:
            self.server_running = True
            self.logger.info("OPA admission control server started successfully")

            # Test server health
            time.sleep(2)  # Give server time to start
            if self.scanner._check_server_health():
                self.logger.info("OPA server health check passed")
                return True
            else:
                self.logger.error("OPA server health check failed")
                self.stop_admission_control()
                return False
        else:
            self.logger.error("Failed to start OPA server")
            return False

    def stop_admission_control(self) -> bool:
        """Stop OPA admission control server"""
        if not self.server_running:
            self.logger.info("OPA server not running")
            return True

        self.logger.info("Stopping OPA server")
        success = self.scanner.stop_opa_server()

        if success:
            self.server_running = False
            self.logger.info("OPA server stopped successfully")
        else:
            self.logger.error("Failed to stop OPA server")

        return success

    def test_admission_control(self, manifest_file: str) -> Dict:
        """Test Kubernetes manifest against admission control policies"""
        if not self.server_running:
            self.logger.error("OPA server not running. Start admission control first.")
            return {"error": "OPA server not running"}

        self.logger.info(f"Testing manifest: {manifest_file}")
        return self.scanner.test_admission_control(manifest_file)

    def generate_fixes(self, scan_file: str, target: str) -> Dict:
        """Generate fixes for OPA violations using the fixer"""
        self.logger.info(f"Generating fixes for scan results: {scan_file}")

        # Use the fixer's main method
        results = self.fixer.fix_findings(scan_file, target, auto_fix=False)

        # Save generated fixes
        fix_file = self.data_dir / "fixes" / f"opa_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        fix_file.parent.mkdir(exist_ok=True)

        with open(fix_file, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Generated fixes saved to: {fix_file}")
        return results

    def deploy_policies(self, policies: Dict, target_dir: str = None) -> bool:
        """Deploy generated policies to OPA policies directory"""
        target_path = Path(target_dir) if target_dir else self.policies_dir
        target_path.mkdir(exist_ok=True)

        self.logger.info(f"Deploying policies to: {target_path}")

        deployed_count = 0

        for policy_type, policy_data in policies.items():
            if not policy_data or policy_data.get("error"):
                self.logger.warning(f"Skipping {policy_type}: no valid policy data")
                continue

            # Save policy files
            if policy_type == "admission_control" and "policies" in policy_data:
                for policy_name, policy_content in policy_data["policies"].items():
                    policy_file = target_path / f"{policy_name}.rego"
                    with open(policy_file, 'w') as f:
                        f.write(policy_content)
                    deployed_count += 1
                    self.logger.info(f"Deployed policy: {policy_file}")

            elif "policy" in policy_data:
                policy_file = target_path / f"{policy_type}.rego"
                with open(policy_file, 'w') as f:
                    f.write(policy_data["policy"])
                deployed_count += 1
                self.logger.info(f"Deployed policy: {policy_file}")

        self.logger.info(f"Deployed {deployed_count} policies")
        return deployed_count > 0

    def full_workflow(self, target: str, auto_deploy: bool = False) -> Dict:
        """Execute complete OPA workflow: scan → generate → deploy → test"""
        self.logger.info(f"Starting full OPA workflow for: {target}")

        workflow_results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "steps": {}
        }

        # Step 1: Scan project
        self.logger.info("Step 1: Scanning project")
        scan_results = self.scan_project(target)
        workflow_results["steps"]["scan"] = {
            "status": "completed" if scan_results else "failed",
            "results": scan_results
        }

        # Step 2: Generate fixes
        self.logger.info("Step 2: Generating security fixes")
        latest_scan = self._get_latest_scan_file()
        if latest_scan:
            fixes = self.generate_fixes(latest_scan, target)
            workflow_results["steps"]["generate"] = {
                "status": "completed" if fixes else "failed",
                "fixes_generated": len(fixes.get("fixes", []))
            }
        else:
            workflow_results["steps"]["generate"] = {
                "status": "failed",
                "error": "No scan results found"
            }
            fixes = {}

        # Step 3: Deploy fixes (if auto_deploy or no server running)
        if auto_deploy or not self.server_running:
            self.logger.info("Step 3: Applying fixes")
            apply_success = self._apply_fixes(fixes, target)
            workflow_results["steps"]["deploy"] = {
                "status": "completed" if apply_success else "failed"
            }

            # Step 4: Start admission control
            self.logger.info("Step 4: Starting admission control")
            server_success = self.start_admission_control()
            workflow_results["steps"]["admission_control"] = {
                "status": "running" if server_success else "failed"
            }
        else:
            self.logger.info("Step 3-4: Skipping deploy/start (server already running)")
            workflow_results["steps"]["deploy"] = {"status": "skipped"}
            workflow_results["steps"]["admission_control"] = {"status": "already_running"}

        # Step 5: Test workflow with sample manifest
        if self.server_running:
            self.logger.info("Step 5: Testing admission control")
            # Create a test manifest for validation
            test_manifest = self._create_test_manifest()
            test_results = self.test_admission_control(test_manifest)
            workflow_results["steps"]["test"] = {
                "status": "completed",
                "results": test_results
            }

        # Save workflow results
        workflow_file = self.data_dir / "workflows" / f"opa_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        workflow_file.parent.mkdir(exist_ok=True)

        with open(workflow_file, 'w') as f:
            json.dump(workflow_results, f, indent=2)

        self.logger.info(f"Full workflow completed. Results saved to: {workflow_file}")
        return workflow_results

    def _create_test_manifest(self) -> str:
        """Create a test Kubernetes manifest for admission control testing"""
        test_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "test-pod",
                "namespace": "default"
            },
            "spec": {
                "containers": [
                    {
                        "name": "test-container",
                        "image": "nginx:latest",
                        "securityContext": {
                            "runAsUser": 0,  # Root user - should trigger policy
                            "privileged": True  # Privileged - should trigger policy
                        }
                    }
                ]
            }
        }

        test_file = self.data_dir / "test_manifest.yaml"
        with open(test_file, 'w') as f:
            import yaml
            yaml.dump(test_manifest, f)

        return str(test_file)

    def _save_formatted_report(self, results: Dict, target: str):
        """Save formatted OPA scan report to GP-DOCS/SCAN-RESULTS"""
        docs_scan_dir = self.docs_dir / "SCAN-RESULTS"
        docs_scan_dir.mkdir(exist_ok=True)

        # Generate formatted report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = docs_scan_dir / f"OPA_SCAN_REPORT_{timestamp}.md"

        report_content = f"""# OPA Security Scan Report

**Target Project**: {target}
**Scan Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Scanner**: Open Policy Agent (OPA)
**Scan ID**: {results.get('scan_id', 'N/A')}

## Summary

- **Total Issues Found**: {results.get('summary', {}).get('total', 0)}
- **Files Scanned**: {results.get('summary', {}).get('files_scanned', 0)}
- **Policy Package**: {results.get('summary', {}).get('policy_package', 'N/A')}

### Severity Breakdown
"""

        severity = results.get('summary', {}).get('severity_breakdown', {})
        for level, count in severity.items():
            icon = "🔴" if level == "critical" else "🟠" if level == "high" else "🟡" if level == "medium" else "🟢"
            report_content += f"- {icon} **{level.title()}**: {count}\n"

        report_content += f"""
### Available Policies
The following OPA policies were available for evaluation:
"""

        policies = results.get('metadata', {}).get('policies_available', [])
        for policy in policies:
            report_content += f"- {policy}\n"

        report_content += f"""

## Findings

"""

        findings = results.get('findings', [])
        if findings:
            for i, finding in enumerate(findings, 1):
                report_content += f"""### Finding {i}: {finding.get('policy', 'Unknown Policy')}

**File**: {finding.get('file', 'N/A')}
**Severity**: {finding.get('severity', 'Unknown')}
**Message**: {finding.get('message', 'No message provided')}

"""
        else:
            report_content += "✅ **No policy violations found!**\n\nAll scanned files comply with the configured OPA security policies.\n"

        report_content += f"""

## Technical Details

**Policy Directory**: {results.get('metadata', {}).get('policy_directory', 'N/A')}
**Raw Results**: Available in GP-DATA/active/scans/
**Timestamp**: {results.get('timestamp', 'N/A')}

---
*Generated by GP-Copilot OPA Manager*
"""

        # Save formatted report
        with open(report_file, 'w') as f:
            f.write(report_content)

        self.logger.info(f"Formatted report saved to: {report_file}")

        # Also save a copy of raw JSON to GP-DOCS for reference
        json_file = docs_scan_dir / f"OPA_RAW_RESULTS_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)

    def _get_latest_scan_file(self) -> Optional[str]:
        """Get the latest OPA scan file"""
        scan_dir = self.data_dir / "scans"
        if not scan_dir.exists():
            return None

        opa_files = list(scan_dir.glob("opa_*.json"))
        if not opa_files:
            return None

        # Get the most recent file
        latest_file = max(opa_files, key=lambda f: f.stat().st_mtime)
        return str(latest_file)

    def _apply_fixes(self, fixes: Dict, target: str) -> bool:
        """Apply fixes to target project"""
        if not fixes or not fixes.get("fixes"):
            self.logger.warning("No fixes to apply")
            return True

        self.logger.info(f"Applying {len(fixes['fixes'])} fixes to {target}")

        # The fixer can auto-apply fixes, so we call it with auto_fix=True
        latest_scan = self._get_latest_scan_file()
        if latest_scan:
            self.fixer.fix_findings(latest_scan, target, auto_fix=True)
            return True
        return False

    def get_status(self) -> Dict:
        """Get current OPA manager status"""
        return {
            "server_running": self.server_running,
            "server_port": self.scanner.server_port,
            "policies_dir": str(self.policies_dir),
            "data_dir": str(self.data_dir),
            "scanner_available": hasattr(self.scanner, 'tool_path') and Path(self.scanner.tool_path).exists(),
            "fixer_available": True,  # OPA fixer is always available
            "policies_count": len(list(self.policies_dir.glob("*.rego"))) if self.policies_dir.exists() else 0
        }

    def cleanup(self):
        """Cleanup resources and stop server"""
        if self.server_running:
            self.stop_admission_control()


def main():
    """CLI interface for OPA Manager"""
    import argparse

    parser = argparse.ArgumentParser(description="OPA Manager - Comprehensive Policy Management")
    parser.add_argument("command", choices=[
        "scan", "start-server", "stop-server", "generate", "deploy",
        "test", "workflow", "status"
    ])
    parser.add_argument("target", nargs="?", help="Target directory or manifest file")
    parser.add_argument("--auto-deploy", action="store_true", help="Auto-deploy generated policies")
    parser.add_argument("--policies-dir", help="Custom policies directory")

    args = parser.parse_args()

    manager = OPAManager()

    try:
        if args.command == "scan":
            if not args.target:
                print("Error: target required for scan")
                return 1
            results = manager.scan_project(args.target)
            print(json.dumps(results, indent=2))

        elif args.command == "start-server":
            success = manager.start_admission_control(args.policies_dir)
            print(f"Server start: {'success' if success else 'failed'}")

        elif args.command == "stop-server":
            success = manager.stop_admission_control()
            print(f"Server stop: {'success' if success else 'failed'}")

        elif args.command == "generate":
            if not args.target:
                print("Error: target required for generate")
                return 1
            policies = manager.generate_policies(args.target)
            print(json.dumps(policies, indent=2))

        elif args.command == "deploy":
            print("Error: deploy requires policies from generate command")
            return 1

        elif args.command == "test":
            if not args.target:
                print("Error: manifest file required for test")
                return 1
            results = manager.test_admission_control(args.target)
            print(json.dumps(results, indent=2))

        elif args.command == "workflow":
            if not args.target:
                print("Error: target required for workflow")
                return 1
            results = manager.full_workflow(args.target, args.auto_deploy)
            print(json.dumps(results, indent=2))

        elif args.command == "status":
            status = manager.get_status()
            print(json.dumps(status, indent=2))

        return 0

    except KeyboardInterrupt:
        print("\nInterrupted")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        manager.cleanup()


if __name__ == "__main__":
    exit(main())