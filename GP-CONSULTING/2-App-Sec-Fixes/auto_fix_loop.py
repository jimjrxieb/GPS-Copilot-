#!/usr/bin/env python3
"""
Automated Fix Loop Agent
Scan → Fix → Re-scan until all fixable issues are resolved
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Project paths
GP_CONSULTING = Path(__file__).parent.parent
PHASE1_CI_SCANNERS = GP_CONSULTING / "1-Security-Assessment" / "ci-scanners"
PHASE2_FIXERS = GP_CONSULTING / "2-App-Sec-Fixes" / "fixers"
GP_DATA = Path.home() / "linkops-industries" / "GP-copilot" / "GP-DATA" / "active"


class AutoFixLoop:
    """Automated security fix loop with scan → fix → rescan"""

    def __init__(self, project_path: str, max_iterations: int = 5):
        self.project_path = Path(project_path).resolve()
        self.max_iterations = max_iterations
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Fixer mapping: Bandit/Semgrep issue → Fixer script
        self.fixer_map = {
            # Hardcoded secrets
            "gitleaks": PHASE2_FIXERS / "fix-hardcoded-secrets.sh",
            "B105": PHASE2_FIXERS / "fix-hardcoded-secrets.sh",  # hardcoded_password
            "B106": PHASE2_FIXERS / "fix-hardcoded-secrets.sh",  # hardcoded_password_funcarg
            "B107": PHASE2_FIXERS / "fix-hardcoded-secrets.sh",  # hardcoded_password_default

            # SQL injection
            "B608": PHASE2_FIXERS / "fix-sql-injection.sh",      # hardcoded_sql_expressions
            "B610": PHASE2_FIXERS / "fix-sql-injection.sh",      # django_extra_used
            "B611": PHASE2_FIXERS / "fix-sql-injection.sh",      # django_rawsql_used

            # Weak cryptography
            "B303": PHASE2_FIXERS / "fix-weak-crypto.sh",        # md5
            "B304": PHASE2_FIXERS / "fix-weak-crypto.sh",        # sha1
            "B305": PHASE2_FIXERS / "fix-weak-crypto.sh",        # des
            "B306": PHASE2_FIXERS / "fix-weak-crypto.sh",        # weak_cipher

            # Insecure requests
            "B113": PHASE2_FIXERS / "fix-insecure-requests.sh",  # request_without_timeout

            # Weak random
            "B311": PHASE2_FIXERS / "fix-weak-random.sh",        # random

            # Command injection
            "B602": PHASE2_FIXERS / "fix-command-injection.sh",  # shell_true
            "B605": PHASE2_FIXERS / "fix-command-injection.sh",  # os_system
            "B607": PHASE2_FIXERS / "fix-command-injection.sh",  # shell_injection

            # Dependencies
            "dependency": PHASE2_FIXERS / "fix-dependency-vulns.sh",
        }

        self.results = {
            "project": str(self.project_path),
            "timestamp": self.timestamp,
            "iterations": [],
            "final_status": "unknown"
        }

    def run_ci_scanners(self, iteration: int) -> Dict:
        """Run Phase 1 CI scanners"""
        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}: Running CI Scanners")
        print(f"{'='*60}")

        scanner_results = {}

        # Bandit (Python SAST)
        print("→ Running Bandit scanner...")
        bandit_cmd = [
            "python3",
            str(PHASE1_CI_SCANNERS / "bandit_scanner.py"),
            "--target", str(self.project_path)
        ]
        try:
            subprocess.run(bandit_cmd, check=False, capture_output=True)
            # Load results
            bandit_file = self._find_latest_scan("1-sec-assessment/ci-findings", "bandit")
            if bandit_file:
                with open(bandit_file) as f:
                    scanner_results["bandit"] = json.load(f)
                print(f"   ✅ Bandit: {self._count_issues(scanner_results['bandit'])} issues")
        except Exception as e:
            print(f"   ⚠️  Bandit failed: {e}")

        # Gitleaks (Secrets)
        print("→ Running Gitleaks scanner...")
        gitleaks_cmd = [
            "python3",
            str(PHASE1_CI_SCANNERS / "gitleaks_scanner.py"),
            "--target", str(self.project_path)
        ]
        try:
            subprocess.run(gitleaks_cmd, check=False, capture_output=True)
            gitleaks_file = self._find_latest_scan("1-sec-assessment/ci-findings", "gitleaks")
            if gitleaks_file:
                with open(gitleaks_file) as f:
                    scanner_results["gitleaks"] = json.load(f)
                print(f"   ✅ Gitleaks: {self._count_issues(scanner_results['gitleaks'])} issues")
        except Exception as e:
            print(f"   ⚠️  Gitleaks failed: {e}")

        # Semgrep (Multi-language SAST)
        print("→ Running Semgrep scanner...")
        semgrep_cmd = [
            "python3",
            str(PHASE1_CI_SCANNERS / "semgrep_scanner.py"),
            "--target", str(self.project_path)
        ]
        try:
            subprocess.run(semgrep_cmd, check=False, capture_output=True)
            semgrep_file = self._find_latest_scan("1-sec-assessment/ci-findings", "semgrep")
            if semgrep_file:
                with open(semgrep_file) as f:
                    scanner_results["semgrep"] = json.load(f)
                print(f"   ✅ Semgrep: {self._count_issues(scanner_results['semgrep'])} issues")
        except Exception as e:
            print(f"   ⚠️  Semgrep failed: {e}")

        return scanner_results

    def analyze_findings(self, scanner_results: Dict) -> List[Tuple[str, Path]]:
        """Analyze findings and determine which fixers to run"""
        fixers_to_run = set()

        # Bandit findings
        if "bandit" in scanner_results:
            for finding in scanner_results["bandit"].get("findings", []):
                issue_id = finding.get("test_id")
                if issue_id in self.fixer_map:
                    fixers_to_run.add(self.fixer_map[issue_id])

        # Gitleaks findings
        if "gitleaks" in scanner_results:
            if scanner_results["gitleaks"].get("findings"):
                fixers_to_run.add(self.fixer_map["gitleaks"])

        # Semgrep findings
        if "semgrep" in scanner_results:
            for finding in scanner_results["semgrep"].get("findings", []):
                check_id = finding.get("check_id", "")
                if "sql" in check_id.lower():
                    fixers_to_run.add(self.fixer_map["B608"])

        # Dependency check
        if (self.project_path / "package.json").exists() or \
           (self.project_path / "requirements.txt").exists():
            fixers_to_run.add(self.fixer_map["dependency"])

        return list(fixers_to_run)

    def apply_fixes(self, fixers: List[Path]) -> int:
        """Apply automated fixes"""
        if not fixers:
            print("\n⚠️  No automated fixers available for these issues")
            return 0

        print(f"\n→ Applying {len(fixers)} automated fixers...")

        fixes_applied = 0
        for fixer in fixers:
            fixer_name = fixer.name
            print(f"\n  🔧 Running {fixer_name}...")

            try:
                result = subprocess.run(
                    [str(fixer), str(self.project_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes
                )

                if result.returncode == 0:
                    print(f"     ✅ {fixer_name} completed successfully")
                    fixes_applied += 1
                else:
                    print(f"     ⚠️  {fixer_name} completed with warnings")
                    if result.stderr:
                        print(f"     {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                print(f"     ❌ {fixer_name} timed out")
            except Exception as e:
                print(f"     ❌ {fixer_name} failed: {e}")

        return fixes_applied

    def count_total_issues(self, scanner_results: Dict) -> int:
        """Count total issues across all scanners"""
        total = 0
        for scanner, results in scanner_results.items():
            total += self._count_issues(results)
        return total

    def _count_issues(self, scan_result: Dict) -> int:
        """Count issues in a single scan result"""
        if "findings" in scan_result:
            return len(scan_result["findings"])
        if "metadata" in scan_result and "issue_count" in scan_result["metadata"]:
            return scan_result["metadata"]["issue_count"]
        return 0

    def _find_latest_scan(self, subfolder: str, scanner: str) -> Path:
        """Find latest scan file for a scanner"""
        scan_dir = GP_DATA / subfolder
        if not scan_dir.exists():
            return None

        pattern = f"{scanner}_*.json"
        files = list(scan_dir.glob(pattern))
        if not files:
            return None

        return max(files, key=lambda f: f.stat().st_mtime)

    def generate_report(self):
        """Generate final fix report"""
        report_path = GP_DATA / "2-app-sec-fixes" / f"auto_fix_report_{self.timestamp}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📝 Full report saved: {report_path}")

    def run(self):
        """Run the complete fix loop"""
        print(f"""
╔══════════════════════════════════════════════════════════╗
║         AUTOMATED FIX LOOP - Phase 2 Remediation        ║
╚══════════════════════════════════════════════════════════╝

Project: {self.project_path}
Max Iterations: {self.max_iterations}
Timestamp: {self.timestamp}
""")

        initial_results = None

        for iteration in range(1, self.max_iterations + 1):
            # Step 1: Run scanners
            scanner_results = self.run_ci_scanners(iteration)

            # Count issues
            total_issues = self.count_total_issues(scanner_results)

            # Store iteration results
            iteration_data = {
                "iteration": iteration,
                "total_issues": total_issues,
                "scanner_results": {
                    scanner: self._count_issues(results)
                    for scanner, results in scanner_results.items()
                }
            }

            if iteration == 1:
                initial_results = scanner_results
                iteration_data["initial_scan"] = True

            print(f"\n📊 Iteration {iteration} Summary:")
            print(f"   Total Issues: {total_issues}")
            for scanner, count in iteration_data["scanner_results"].items():
                print(f"   • {scanner}: {count}")

            # Exit if no issues
            if total_issues == 0:
                print(f"\n✅ SUCCESS: No security issues found!")
                self.results["final_status"] = "clean"
                self.results["iterations"].append(iteration_data)
                break

            # Step 2: Determine which fixers to run
            fixers = self.analyze_findings(scanner_results)

            if not fixers:
                print(f"\n⚠️  No automated fixes available for remaining {total_issues} issues")
                print(f"   Manual review required")
                self.results["final_status"] = "manual_review_needed"
                iteration_data["manual_review_needed"] = True
                self.results["iterations"].append(iteration_data)
                break

            # Step 3: Apply fixes
            fixes_applied = self.apply_fixes(fixers)
            iteration_data["fixes_applied"] = fixes_applied

            if fixes_applied == 0:
                print(f"\n⚠️  No fixes were successfully applied")
                self.results["final_status"] = "fixes_failed"
                self.results["iterations"].append(iteration_data)
                break

            print(f"\n   ✅ Applied {fixes_applied} automated fixes")

            # Store iteration
            self.results["iterations"].append(iteration_data)

            # Loop will re-scan in next iteration

        # Final summary
        print(f"\n{'='*60}")
        print("FINAL SUMMARY")
        print(f"{'='*60}")

        if initial_results:
            initial_count = self.count_total_issues(initial_results)
            final_count = total_issues if iteration > 0 else 0

            print(f"\nBefore:  {initial_count} issues")
            print(f"After:   {final_count} issues")

            if initial_count > 0:
                reduction = ((initial_count - final_count) / initial_count) * 100
                print(f"Reduction: {reduction:.1f}%")

        print(f"\nIterations: {iteration}/{self.max_iterations}")
        print(f"Status: {self.results.get('final_status', 'unknown')}")

        # Generate report
        self.generate_report()

        return self.results


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 auto_fix_loop.py /path/to/project [max_iterations]")
        print("\nExample:")
        print("  python3 auto_fix_loop.py ~/linkops-industries/GP-copilot/GP-PROJECTS/FINANCE-project")
        print("  python3 auto_fix_loop.py ~/project 3")
        sys.exit(1)

    project_path = sys.argv[1]
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    if not Path(project_path).exists():
        print(f"❌ ERROR: Project path does not exist: {project_path}")
        sys.exit(1)

    # Run auto-fix loop
    agent = AutoFixLoop(project_path, max_iterations)
    results = agent.run()

    # Exit code based on status
    if results.get("final_status") == "clean":
        sys.exit(0)
    elif results.get("final_status") == "manual_review_needed":
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
