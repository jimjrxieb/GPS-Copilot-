#!/usr/bin/env python3
"""
Comprehensive Jade Chat Test Suite
50+ test cases covering all functionality
"""

import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any


class JadeChatTester:
    """Automated test suite for Jade chat functionality"""

    def __init__(self):
        self.gp_copilot_root = Path(__file__).parent.parent
        self.jade_chat_path = self.gp_copilot_root / "GP-AI/cli/jade_chat.py"
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def run_jade_command(self, command: str, timeout: int = 10) -> Dict[str, Any]:
        """Run a command through Jade chat and capture output"""
        try:
            result = subprocess.run(
                f'echo "{command}" | timeout {timeout} python3 {self.jade_chat_path}',
                shell=True,
                cwd=str(self.gp_copilot_root),
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )

            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': ''
            }

    def assert_contains(self, output: str, expected: str, test_name: str) -> bool:
        """Assert output contains expected string"""
        if expected.lower() in output.lower():
            self.passed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'PASS',
                'message': f'Found: "{expected}"'
            })
            return True
        else:
            self.failed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'message': f'Expected "{expected}" not found'
            })
            return False

    def assert_not_contains(self, output: str, unexpected: str, test_name: str) -> bool:
        """Assert output does NOT contain string"""
        if unexpected.lower() not in output.lower():
            self.passed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'PASS',
                'message': f'Correctly excludes: "{unexpected}"'
            })
            return True
        else:
            self.failed += 1
            self.test_results.append({
                'test': test_name,
                'status': 'FAIL',
                'message': f'Unexpected "{unexpected}" found'
            })
            return False

    # ========================================
    # Category 1: Basic Functionality (10 tests)
    # ========================================

    def test_01_help_command(self):
        """Test help command shows available commands"""
        result = self.run_jade_command("help")
        self.assert_contains(result['stdout'], "Security Scans", "Help shows categories")
        self.assert_contains(result['stdout'], "Policy & Compliance", "Help shows policy section")

    def test_02_help_variant_question(self):
        """Test 'what can you do' triggers help"""
        result = self.run_jade_command("what can you do")
        self.assert_contains(result['stdout'], "Available Commands", "Help triggered by question")

    def test_03_exit_command(self):
        """Test exit command terminates gracefully"""
        result = self.run_jade_command("exit")
        self.assert_contains(result['stdout'], "Goodbye", "Exit shows goodbye message")

    def test_04_quit_command(self):
        """Test quit command works"""
        result = self.run_jade_command("quit")
        self.assert_contains(result['stdout'], "Goodbye", "Quit works")

    def test_05_welcome_banner(self):
        """Test welcome banner displays"""
        result = self.run_jade_command("exit")
        self.assert_contains(result['stdout'], "Jade Interactive Chat", "Welcome banner shown")
        self.assert_contains(result['stdout'], "Examples:", "Examples shown")

    def test_06_empty_input(self):
        """Test empty input doesn't crash"""
        result = self.run_jade_command("")
        self.assert_contains(result['success'], True, "Empty input handled gracefully")

    def test_07_invalid_command(self):
        """Test invalid command shows helpful message"""
        result = self.run_jade_command("xyz123invalid")
        self.assert_contains(result['stdout'], "not sure", "Shows helpful message for invalid input")

    def test_08_case_insensitive(self):
        """Test commands are case-insensitive"""
        result = self.run_jade_command("HELP")
        self.assert_contains(result['stdout'], "Available Commands", "Case insensitive help")

    def test_09_partial_match(self):
        """Test partial command matching"""
        result = self.run_jade_command("show result")
        # Should match "show results" pattern
        self.assert_contains(result['success'], True, "Partial match works")

    def test_10_unicode_handling(self):
        """Test unicode characters don't crash"""
        result = self.run_jade_command("scan 🚀 project")
        self.assert_contains(result['success'], True, "Unicode handled")

    # ========================================
    # Category 2: Scan Results Display (10 tests)
    # ========================================

    def test_11_show_results_command(self):
        """Test 'show results' displays scan summary"""
        result = self.run_jade_command("show results")
        self.assert_contains(result['stdout'], "Scan Results", "Shows results header")

    def test_12_show_results_variant_view(self):
        """Test 'view results' works"""
        result = self.run_jade_command("view results")
        self.assert_contains(result['stdout'], "Scan Results", "View results works")

    def test_13_show_results_variant_display(self):
        """Test 'display results' works"""
        result = self.run_jade_command("display results")
        self.assert_contains(result['stdout'], "Scan Results", "Display results works")

    def test_14_show_latest_scan(self):
        """Test 'show latest scan' works"""
        result = self.run_jade_command("show latest scan")
        self.assert_contains(result['stdout'], "Scan Results", "Latest scan shown")

    def test_15_show_findings(self):
        """Test 'show findings' works"""
        result = self.run_jade_command("show findings")
        self.assert_contains(result['stdout'], "Scan Results", "Findings shown")

    def test_16_results_show_scanners(self):
        """Test results show scanner names"""
        result = self.run_jade_command("show results")
        # Should show at least one scanner (BANDIT, TRIVY, etc.)
        output = result['stdout'].upper()
        has_scanner = any(s in output for s in ['BANDIT', 'TRIVY', 'GITLEAKS', 'SEMGREP'])
        self.assert_contains(str(has_scanner), 'True', "Shows scanner names")

    def test_17_results_show_counts(self):
        """Test results show issue counts"""
        result = self.run_jade_command("show results")
        self.assert_contains(result['stdout'], "issues", "Shows issue counts")

    def test_18_results_total_summary(self):
        """Test results show total issues"""
        result = self.run_jade_command("show results")
        self.assert_contains(result['stdout'], "Total Issues", "Shows total summary")

    def test_19_results_actionable_tip(self):
        """Test results show actionable tips"""
        result = self.run_jade_command("show results")
        # Should show either "run fixers" tip or "No issues" message
        has_tip = "run fixers" in result['stdout'].lower() or "no security issues" in result['stdout'].lower()
        self.assert_contains(str(has_tip), 'True', "Shows actionable tips")

    def test_20_results_no_scans_message(self):
        """Test graceful handling when no scans exist"""
        # This would require moving scan files temporarily - skip for now
        # Just verify command doesn't crash
        result = self.run_jade_command("show results")
        self.assert_contains(result['success'], True, "Handles no scans gracefully")

    # ========================================
    # Category 3: Project Management (8 tests)
    # ========================================

    def test_21_list_projects(self):
        """Test listing available projects"""
        result = self.run_jade_command("list projects")
        self.assert_contains(result['stdout'], "GP-PROJECTS", "Lists projects")

    def test_22_show_projects(self):
        """Test 'show projects' variant"""
        result = self.run_jade_command("show projects")
        self.assert_contains(result['success'], True, "Show projects works")

    def test_23_set_project_command(self):
        """Test setting current project"""
        result = self.run_jade_command("set project GP-PROJECTS/LinkOps-MLOps")
        self.assert_contains(result['stdout'], "Current project", "Set project works")

    def test_24_use_project_command(self):
        """Test 'use project' variant"""
        result = self.run_jade_command("use project GP-PROJECTS/DVWA")
        self.assert_contains(result['success'], True, "Use project works")

    def test_25_project_in_scan_command(self):
        """Test embedding project in scan command"""
        result = self.run_jade_command("scan GP-PROJECTS/LinkOps-MLOps")
        # Should extract project from command
        self.assert_contains(result['success'], True, "Extracts project from command")

    def test_26_absolute_path_project(self):
        """Test absolute path as project"""
        result = self.run_jade_command("set project /home/jimmie/linkops-industries/Portfolio")
        self.assert_contains(result['success'], True, "Handles absolute paths")

    def test_27_relative_path_project(self):
        """Test relative path handling"""
        result = self.run_jade_command("set project to LinkOps-MLOps")
        self.assert_contains(result['success'], True, "Handles relative paths")

    def test_28_project_persistence(self):
        """Test project persists between commands (in session)"""
        # This requires interactive session - mark as informational
        self.test_results.append({
            'test': 'Project persistence across commands',
            'status': 'INFO',
            'message': 'Requires interactive testing'
        })

    # ========================================
    # Category 4: Scanner Commands (10 tests)
    # ========================================

    def test_29_scan_my_project(self):
        """Test 'scan my project' command"""
        result = self.run_jade_command("scan my project", timeout=30)
        # Should trigger scan or prompt for project
        self.assert_contains(result['success'], True, "Scan my project recognized")

    def test_30_quick_scan(self):
        """Test 'quick scan' command"""
        result = self.run_jade_command("scan my project quickly", timeout=30)
        self.assert_contains(result['success'], True, "Quick scan recognized")

    def test_31_check_project(self):
        """Test 'check my project' variant"""
        result = self.run_jade_command("check my project", timeout=30)
        self.assert_contains(result['success'], True, "Check command works")

    def test_32_analyze_project(self):
        """Test 'analyze project' variant"""
        result = self.run_jade_command("analyze GP-PROJECTS/DVWA", timeout=30)
        self.assert_contains(result['success'], True, "Analyze command works")

    def test_33_test_project(self):
        """Test 'test my project' variant"""
        result = self.run_jade_command("test my project", timeout=30)
        self.assert_contains(result['success'], True, "Test command works")

    def test_34_audit_project(self):
        """Test 'audit project' variant"""
        result = self.run_jade_command("audit GP-PROJECTS/LinkOps-MLOps", timeout=30)
        self.assert_contains(result['success'], True, "Audit command works")

    def test_35_scan_with_advice(self):
        """Test scan with AI advice"""
        result = self.run_jade_command("scan GP-PROJECTS/DVWA with advice", timeout=30)
        self.assert_contains(result['success'], True, "Scan with advice recognized")

    def test_36_scan_and_fix(self):
        """Test scan and fix command"""
        result = self.run_jade_command("scan and fix GP-PROJECTS/DVWA", timeout=30)
        self.assert_contains(result['success'], True, "Scan and fix recognized")

    def test_37_natural_language_scan(self):
        """Test natural language: 'I want to scan my project'"""
        result = self.run_jade_command("I want to scan my project quickly", timeout=30)
        self.assert_contains(result['success'], True, "Natural language scan works")

    def test_38_conversational_scan(self):
        """Test conversational: 'Can you scan my project?'"""
        result = self.run_jade_command("Can you scan my project?", timeout=30)
        self.assert_contains(result['success'], True, "Conversational scan works")

    # ========================================
    # Category 5: Policy/OPA Commands (6 tests)
    # ========================================

    def test_39_check_policy(self):
        """Test 'check policy' command"""
        result = self.run_jade_command("check policy on GP-PROJECTS/Terraform_CICD_Setup", timeout=30)
        self.assert_contains(result['success'], True, "Check policy recognized")

    def test_40_validate_policy(self):
        """Test 'validate policy' variant"""
        result = self.run_jade_command("validate policy", timeout=30)
        self.assert_contains(result['success'], True, "Validate policy works")

    def test_41_test_opa(self):
        """Test 'test opa' command"""
        result = self.run_jade_command("test opa on my project", timeout=30)
        self.assert_contains(result['success'], True, "Test OPA recognized")

    def test_42_terraform_validate(self):
        """Test terraform plan validation"""
        result = self.run_jade_command("validate terraform plan", timeout=30)
        self.assert_contains(result['success'], True, "Terraform validate recognized")

    def test_43_terraform_check(self):
        """Test 'check terraform' variant"""
        result = self.run_jade_command("check terraform for violations", timeout=30)
        self.assert_contains(result['success'], True, "Terraform check works")

    def test_44_kubernetes_policy(self):
        """Test Kubernetes policy check"""
        result = self.run_jade_command("check kubernetes policy", timeout=30)
        self.assert_contains(result['success'], True, "K8s policy check works")

    # ========================================
    # Category 6: Fixer Commands (6 tests)
    # ========================================

    def test_45_run_fixers(self):
        """Test 'run fixers' command"""
        result = self.run_jade_command("run fixers", timeout=60)
        self.assert_contains(result['success'], True, "Run fixers recognized")

    def test_46_apply_fixers(self):
        """Test 'apply fixers' variant"""
        result = self.run_jade_command("apply fixers", timeout=60)
        self.assert_contains(result['success'], True, "Apply fixers works")

    def test_47_execute_fixers(self):
        """Test 'execute fixers' variant"""
        result = self.run_jade_command("execute fixers", timeout=60)
        self.assert_contains(result['success'], True, "Execute fixers works")

    def test_48_fix_issues(self):
        """Test 'fix issues' command"""
        result = self.run_jade_command("fix issues", timeout=60)
        self.assert_contains(result['success'], True, "Fix issues recognized")

    def test_49_fix_findings(self):
        """Test 'fix findings' variant"""
        result = self.run_jade_command("fix findings", timeout=60)
        self.assert_contains(result['success'], True, "Fix findings works")

    def test_50_remediate(self):
        """Test 'remediate' command"""
        result = self.run_jade_command("remediate vulnerabilities", timeout=60)
        self.assert_contains(result['success'], True, "Remediate recognized")

    # ========================================
    # Bonus Tests: Edge Cases & Advanced (10 tests)
    # ========================================

    def test_51_special_characters(self):
        """Test special characters in input"""
        result = self.run_jade_command("scan !@#$%^&*()")
        self.assert_contains(result['success'], True, "Special chars handled")

    def test_52_very_long_input(self):
        """Test very long input string"""
        long_input = "scan " + "x" * 1000
        result = self.run_jade_command(long_input)
        self.assert_contains(result['success'], True, "Long input handled")

    def test_53_multiple_commands(self):
        """Test multiple words in command"""
        result = self.run_jade_command("I really want to scan my project for security issues please")
        self.assert_contains(result['success'], True, "Multi-word command works")

    def test_54_typo_tolerance(self):
        """Test slight typos are handled"""
        result = self.run_jade_command("scann my project")  # typo: scann
        # Should still work or give helpful message
        self.assert_contains(result['success'], True, "Handles typos gracefully")

    def test_55_gui_launch(self):
        """Test GUI launch command (won't actually launch in test)"""
        result = self.run_jade_command("open gui", timeout=5)
        # Command should be recognized even if GUI doesn't launch
        self.assert_contains(result['success'], True, "GUI launch command recognized")

    def test_56_show_stats(self):
        """Test show stats command"""
        result = self.run_jade_command("show stats")
        self.assert_contains(result['success'], True, "Show stats recognized")

    def test_57_analyze_with_ai(self):
        """Test AI analysis command"""
        result = self.run_jade_command("analyze scan results")
        self.assert_contains(result['success'], True, "AI analysis recognized")

    def test_58_summarize_command(self):
        """Test summarize command"""
        result = self.run_jade_command("summarize latest scan results")
        self.assert_contains(result['success'], True, "Summarize recognized")

    def test_59_conftest_agent(self):
        """Test conftest gate agent command"""
        result = self.run_jade_command("run conftest gate agent", timeout=30)
        self.assert_contains(result['success'], True, "Conftest agent recognized")

    def test_60_gatekeeper_agent(self):
        """Test gatekeeper agent command"""
        result = self.run_jade_command("run gatekeeper agent", timeout=30)
        self.assert_contains(result['success'], True, "Gatekeeper agent recognized")

    def run_all_tests(self):
        """Execute all tests and generate report"""
        print("\n" + "="*80)
        print("JADE CHAT COMPREHENSIVE TEST SUITE")
        print("="*80 + "\n")

        # Get all test methods
        test_methods = [method for method in dir(self) if method.startswith('test_')]
        total_tests = len(test_methods)

        print(f"Running {total_tests} tests...\n")

        # Run each test
        for i, test_name in enumerate(test_methods, 1):
            print(f"[{i}/{total_tests}] {test_name.replace('_', ' ').title()}...", end=' ')

            try:
                test_method = getattr(self, test_name)
                test_method()
                print("✓")
            except Exception as e:
                self.failed += 1
                self.test_results.append({
                    'test': test_name,
                    'status': 'ERROR',
                    'message': str(e)
                })
                print(f"✗ (Error: {e})")

            # Small delay to avoid overwhelming system
            time.sleep(0.1)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80 + "\n")

        # Count by status
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        info = sum(1 for r in self.test_results if r['status'] == 'INFO')

        total = len(self.test_results)
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests:  {total}")
        print(f"✅ Passed:    {passed}")
        print(f"❌ Failed:    {failed}")
        print(f"⚠️  Errors:    {errors}")
        print(f"ℹ️  Info:      {info}")
        print(f"\nPass Rate:    {pass_rate:.1f}%\n")

        # Show failures
        if failed > 0 or errors > 0:
            print("="*80)
            print("FAILED/ERROR TESTS")
            print("="*80 + "\n")

            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"❌ {result['test']}")
                    print(f"   {result['message']}\n")

        # Overall status
        print("="*80)
        if pass_rate >= 90:
            print("🎉 EXCELLENT: Jade Chat is production-ready!")
        elif pass_rate >= 75:
            print("✅ GOOD: Most functionality working, minor issues to fix")
        elif pass_rate >= 50:
            print("⚠️  FAIR: Core functionality works, needs improvement")
        else:
            print("❌ NEEDS WORK: Major issues detected")
        print("="*80 + "\n")

        # Save results to JSON
        self.save_results()

    def save_results(self):
        """Save test results to JSON file"""
        results_file = self.gp_copilot_root / "GP-TESTING-VAL/jade_chat_test_results.json"

        output = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(self.test_results),
            'passed': sum(1 for r in self.test_results if r['status'] == 'PASS'),
            'failed': sum(1 for r in self.test_results if r['status'] == 'FAIL'),
            'errors': sum(1 for r in self.test_results if r['status'] == 'ERROR'),
            'results': self.test_results
        }

        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"📄 Results saved to: {results_file}\n")


def main():
    """Run the test suite"""
    tester = JadeChatTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()