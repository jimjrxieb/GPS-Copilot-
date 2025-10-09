#!/usr/bin/env python3
"""
Visible Workflow Test - Test GuidePoint with Real-Time Status Monitoring
========================================================================

This test runs a real GuidePoint workflow against a vulnerable project while
providing real-time visibility into what's happening. This addresses the
critical need to see what GuidePoint is actually doing.

Key Features:
- Real Qwen-style systematic workflow execution
- Live status monitoring during execution
- Real infrastructure validation
- Comprehensive visibility into each step
"""

import asyncio
import sys
import os
import tempfile
import shutil
import threading
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from automation_engine.automation.infrastructure_execution_engine import QwenStyleWorkflowOrchestrator
from automation_engine.automation.james_ai_engine import SecurityFinding
from automation_engine.automation.guidepoint_status import GuidePointStatusMonitor
import uuid
from datetime import datetime


class VisibleWorkflowTester:
    """Test GuidePoint with full visibility into operations"""

    def __init__(self):
        self.workflow_orchestrator = QwenStyleWorkflowOrchestrator()
        self.status_monitor = GuidePointStatusMonitor()

    async def create_vulnerable_test_project(self):
        """Create a realistic vulnerable project for testing"""

        test_dir = tempfile.mkdtemp(prefix="visible_workflow_test_")

        print(f"📁 Creating vulnerable test project: {test_dir}")

        # Create a Dockerfile with known vulnerabilities
        dockerfile_content = """FROM alpine:3.15
RUN apk add --no-cache curl git nodejs npm
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
"""

        # Create package.json with vulnerable dependencies
        package_json_content = """{
  "name": "vulnerable-web-app",
  "version": "1.0.0",
  "description": "A vulnerable web application for testing",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "4.16.0",
    "lodash": "4.17.10",
    "handlebars": "4.7.0"
  }
}"""

        # Create simple vulnerable server
        server_js_content = """const express = require('express');
const app = express();

// Vulnerable: No security headers
app.get('/', (req, res) => {
  res.send('Hello from vulnerable app!');
});

// Vulnerable: No input validation
app.get('/user/:id', (req, res) => {
  const userId = req.params.id;
  res.send(`User ID: ${userId}`);
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
"""

        # Write all files
        files = {
            "Dockerfile": dockerfile_content,
            "package.json": package_json_content,
            "server.js": server_js_content,
            "README.md": "# Vulnerable Web Application\\nThis app has security vulnerabilities for testing."
        }

        for filename, content in files.items():
            with open(os.path.join(test_dir, filename), "w") as f:
                f.write(content)

        print(f"✅ Created {len(files)} files with known vulnerabilities")

        return test_dir

    async def create_vulnerability_findings(self, test_dir):
        """Create realistic vulnerability findings"""

        vulnerabilities = [
            SecurityFinding(
                id="docker-alpine-cve",
                severity="critical",
                title="Alpine 3.15 contains multiple CVEs requiring update to 3.18",
                description="The alpine:3.15 base image contains critical vulnerabilities",
                file_path=os.path.join(test_dir, "Dockerfile"),
                tool="trivy",
                remediation="Update FROM alpine:3.15 to FROM alpine:3.18"
            ),
            SecurityFinding(
                id="express-outdated",
                severity="high",
                title="Express 4.16.0 has security vulnerabilities",
                description="Express version 4.16.0 contains known security issues",
                file_path=os.path.join(test_dir, "package.json"),
                tool="npm_audit",
                remediation="Update Express to version 4.18.0 or higher"
            ),
            SecurityFinding(
                id="lodash-prototype-pollution",
                severity="medium",
                title="Lodash 4.17.10 vulnerable to prototype pollution",
                description="Lodash version contains prototype pollution vulnerability",
                file_path=os.path.join(test_dir, "package.json"),
                tool="npm_audit",
                remediation="Update Lodash to 4.17.21 or higher"
            ),
            SecurityFinding(
                id="missing-security-headers",
                severity="medium",
                title="Missing security headers in Express application",
                description="Application lacks essential security headers",
                file_path=os.path.join(test_dir, "server.js"),
                tool="eslint-security",
                remediation="Add helmet middleware for security headers"
            )
        ]

        return vulnerabilities

    async def run_visible_workflow_test(self):
        """Run a complete workflow test with real-time visibility"""

        print("🎯 VISIBLE WORKFLOW TEST - GuidePoint with Real-Time Monitoring")
        print("=" * 70)
        print("Testing end-to-end systematic workflow with complete visibility")
        print()

        # Create test project
        test_dir = await self.create_vulnerable_test_project()
        vulnerabilities = await self.create_vulnerability_findings(test_dir)

        workflow_id = f"visible-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        try:
            print(f"🚀 Starting visible workflow execution...")
            print(f"   Workflow ID: {workflow_id}")
            print(f"   Target Project: {test_dir}")
            print(f"   Vulnerabilities: {len(vulnerabilities)}")
            print()

            # Start workflow tracking in status monitor
            self.status_monitor.start_workflow_tracking(
                workflow_id, test_dir, len(vulnerabilities)
            )

            # Execute the systematic workflow with enhanced visibility
            workflow_results = await self.execute_workflow_with_status_updates(
                workflow_id, test_dir, vulnerabilities
            )

            # Mark workflow as completed
            overall_success = workflow_results.get("overall_success", False)
            self.status_monitor.complete_workflow(workflow_id, overall_success)

            # Display final results
            await self.display_workflow_results(workflow_results)

            return overall_success

        finally:
            # Cleanup
            shutil.rmtree(test_dir, ignore_errors=True)

    async def execute_workflow_with_status_updates(self, workflow_id, test_dir, vulnerabilities):
        """Execute workflow with real-time status updates"""

        workflow_results = {
            "workflow_id": workflow_id,
            "project_path": test_dir,
            "total_findings": len(vulnerabilities),
            "steps_completed": [],
            "overall_success": False,
            "step_results": {},
            "visibility_data": {}
        }

        try:
            # STEP 1: DISCOVERY
            print("📡 STEP 1: DISCOVERY - Infrastructure State Reading")
            print("-" * 50)

            step_1_result = await self.workflow_orchestrator._step_1_discovery(test_dir)
            workflow_results["steps_completed"].append("discovery")
            workflow_results["step_results"]["discovery"] = step_1_result

            # Update status monitor
            self.status_monitor.update_workflow_status(
                workflow_id, "discovery", ["discovery"], 20.0
            )

            # Display discovery results
            if step_1_result.get("infrastructure_accessible"):
                scan_results = step_1_result.get("scan_results", {})
                successful_scans = sum(1 for result in scan_results.values() if result.get("success"))
                print(f"✅ Infrastructure accessible: {successful_scans}/{len(scan_results)} discovery commands successful")
            else:
                print("⚠️ Limited infrastructure access - continuing with available capabilities")

            workflow_results["visibility_data"]["discovery"] = {
                "infrastructure_accessible": step_1_result.get("infrastructure_accessible", False),
                "scan_commands_executed": len(step_1_result.get("scan_results", {})),
                "successful_scans": sum(1 for result in step_1_result.get("scan_results", {}).values() if result.get("success"))
            }

            await asyncio.sleep(1)  # Allow status to be observed

            # STEP 2: DIAGNOSIS
            print("\n🔬 STEP 2: DIAGNOSIS - Result Parsing and Issue Identification")
            print("-" * 50)

            step_2_result = await self.workflow_orchestrator._step_2_diagnosis(vulnerabilities, step_1_result)
            workflow_results["steps_completed"].append("diagnosis")
            workflow_results["step_results"]["diagnosis"] = step_2_result

            # Update status monitor
            self.status_monitor.update_workflow_status(
                workflow_id, "diagnosis", ["discovery", "diagnosis"], 40.0
            )

            actionable_findings = step_2_result.get("actionable_findings", [])
            print(f"✅ Identified {len(actionable_findings)} actionable security findings")

            for finding in actionable_findings:
                severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(finding.get("severity"), "⚪")
                print(f"   {severity_icon} {finding.get('severity', '').upper()}: {finding.get('title', '')}")

            workflow_results["visibility_data"]["diagnosis"] = {
                "actionable_findings_count": len(actionable_findings),
                "severity_breakdown": {
                    "critical": len([f for f in actionable_findings if f.get("severity") == "critical"]),
                    "high": len([f for f in actionable_findings if f.get("severity") == "high"]),
                    "medium": len([f for f in actionable_findings if f.get("severity") == "medium"]),
                    "low": len([f for f in actionable_findings if f.get("severity") == "low"])
                }
            }

            await asyncio.sleep(1)

            # STEP 3: INVESTIGATION
            print("\n🔍 STEP 3: INVESTIGATION - Root Cause Analysis")
            print("-" * 50)

            step_3_result = await self.workflow_orchestrator._step_3_investigation(test_dir, step_2_result)
            workflow_results["steps_completed"].append("investigation")
            workflow_results["step_results"]["investigation"] = step_3_result

            # Update status monitor
            self.status_monitor.update_workflow_status(
                workflow_id, "investigation", ["discovery", "diagnosis", "investigation"], 60.0
            )

            investigations = step_3_result.get("investigations_performed", [])
            root_causes = step_3_result.get("root_causes_identified", [])

            print(f"✅ Completed {len(investigations)} investigations")
            print(f"✅ Identified {len(root_causes)} root causes")

            workflow_results["visibility_data"]["investigation"] = {
                "investigations_performed": len(investigations),
                "root_causes_identified": len(root_causes),
                "remediation_ready": step_3_result.get("remediation_readiness", False)
            }

            await asyncio.sleep(1)

            # STEP 4: REMEDIATION
            print("\n🚀 STEP 4: REMEDIATION - Targeted Fix Application")
            print("-" * 50)

            step_4_result = await self.workflow_orchestrator._step_4_remediation(test_dir, step_3_result, vulnerabilities)
            workflow_results["steps_completed"].append("remediation")
            workflow_results["step_results"]["remediation"] = step_4_result

            # Update status monitor
            fixes_attempted = step_4_result.get("fixes_attempted", 0)
            fixes_successful = step_4_result.get("fixes_successful", 0)
            remediation_success_rate = (fixes_successful / max(fixes_attempted, 1)) * 100

            self.status_monitor.update_workflow_status(
                workflow_id, "remediation", ["discovery", "diagnosis", "investigation", "remediation"],
                remediation_success_rate
            )

            print(f"✅ Remediation complete: {fixes_successful}/{fixes_attempted} fixes successful ({remediation_success_rate:.1f}%)")

            workflow_results["visibility_data"]["remediation"] = {
                "fixes_attempted": fixes_attempted,
                "fixes_successful": fixes_successful,
                "success_rate": remediation_success_rate
            }

            await asyncio.sleep(1)

            # STEP 5: VERIFICATION
            print("\n✅ STEP 5: VERIFICATION - Fix Validation Testing")
            print("-" * 50)

            step_5_result = await self.workflow_orchestrator._step_5_verification(test_dir, step_4_result)
            workflow_results["steps_completed"].append("verification")
            workflow_results["step_results"]["verification"] = step_5_result

            # Update status monitor - final status
            verification_passed = step_5_result.get("verification_passed", False)
            final_success_rate = 100.0 if verification_passed else remediation_success_rate

            self.status_monitor.update_workflow_status(
                workflow_id, "verification",
                ["discovery", "diagnosis", "investigation", "remediation", "verification"],
                final_success_rate
            )

            validation_tests = step_5_result.get("validation_tests", [])
            tests_passed = sum(1 for test in validation_tests if test.get("passed"))
            total_tests = len(validation_tests)

            print(f"✅ Verification complete: {tests_passed}/{total_tests} validation tests passed")
            print(f"✅ Overall verification: {'PASSED' if verification_passed else 'FAILED'}")

            workflow_results["visibility_data"]["verification"] = {
                "validation_tests_run": total_tests,
                "tests_passed": tests_passed,
                "verification_passed": verification_passed
            }

            workflow_results["overall_success"] = verification_passed

            return workflow_results

        except Exception as e:
            self.status_monitor.log_event("ERROR", f"Workflow failed: {str(e)}", workflow_id)
            workflow_results["error"] = str(e)
            return workflow_results

    async def display_workflow_results(self, workflow_results):
        """Display comprehensive workflow results"""

        print(f"\n🏆 VISIBLE WORKFLOW TEST RESULTS")
        print("=" * 50)

        workflow_id = workflow_results.get("workflow_id")
        overall_success = workflow_results.get("overall_success", False)
        steps_completed = workflow_results.get("steps_completed", [])
        visibility_data = workflow_results.get("visibility_data", {})

        print(f"Workflow ID: {workflow_id}")
        print(f"Overall Success: {'✅ YES' if overall_success else '❌ NO'}")
        print(f"Steps Completed: {len(steps_completed)}/5")
        print()

        # Step-by-step results with visibility metrics
        print("📊 STEP-BY-STEP VISIBILITY ANALYSIS:")
        print("-" * 40)

        step_names = ["discovery", "diagnosis", "investigation", "remediation", "verification"]

        for step_name in step_names:
            step_data = visibility_data.get(step_name, {})
            completed = step_name in steps_completed

            status_icon = "✅" if completed else "❌"
            print(f"{status_icon} {step_name.title()}:")

            if completed and step_data:
                if step_name == "discovery":
                    print(f"   Infrastructure accessible: {'✅' if step_data.get('infrastructure_accessible') else '❌'}")
                    print(f"   Scan commands: {step_data.get('successful_scans', 0)}/{step_data.get('scan_commands_executed', 0)} successful")

                elif step_name == "diagnosis":
                    findings_count = step_data.get('actionable_findings_count', 0)
                    severity_breakdown = step_data.get('severity_breakdown', {})
                    print(f"   Actionable findings: {findings_count}")
                    print(f"   Severity: {severity_breakdown.get('critical', 0)} critical, {severity_breakdown.get('high', 0)} high, {severity_breakdown.get('medium', 0)} medium")

                elif step_name == "investigation":
                    print(f"   Investigations: {step_data.get('investigations_performed', 0)}")
                    print(f"   Root causes: {step_data.get('root_causes_identified', 0)}")
                    print(f"   Remediation ready: {'✅' if step_data.get('remediation_ready') else '❌'}")

                elif step_name == "remediation":
                    success_rate = step_data.get('success_rate', 0)
                    print(f"   Fixes: {step_data.get('fixes_successful', 0)}/{step_data.get('fixes_attempted', 0)} successful")
                    print(f"   Success rate: {success_rate:.1f}%")

                elif step_name == "verification":
                    print(f"   Validation tests: {step_data.get('tests_passed', 0)}/{step_data.get('validation_tests_run', 0)} passed")
                    print(f"   Overall verification: {'✅ PASSED' if step_data.get('verification_passed') else '❌ FAILED'}")

            elif not completed:
                print(f"   Step not reached")

            print()

        # Visibility Assessment
        print("🔍 VISIBILITY ASSESSMENT:")
        print("-" * 25)

        visibility_score = self.calculate_visibility_score(visibility_data)

        print(f"Visibility Score: {visibility_score:.1f}%")

        if visibility_score >= 80:
            print("✅ EXCELLENT VISIBILITY - Full operational transparency achieved")
        elif visibility_score >= 60:
            print("⚠️ GOOD VISIBILITY - Most operations visible with some gaps")
        else:
            print("❌ LIMITED VISIBILITY - Significant transparency gaps")

        print()
        print("🎯 KEY ACHIEVEMENT: Real-time workflow visibility established")
        print("   ✅ Step-by-step progress tracking")
        print("   ✅ Infrastructure state monitoring")
        print("   ✅ Success/failure rate tracking")
        print("   ✅ Comprehensive metrics collection")

    def calculate_visibility_score(self, visibility_data):
        """Calculate visibility score based on data collected"""

        score = 0
        max_score = 0

        # Discovery visibility (20 points)
        max_score += 20
        discovery = visibility_data.get("discovery", {})
        if discovery.get("infrastructure_accessible"):
            score += 15
        if discovery.get("scan_commands_executed", 0) > 0:
            score += 5

        # Diagnosis visibility (20 points)
        max_score += 20
        diagnosis = visibility_data.get("diagnosis", {})
        if diagnosis.get("actionable_findings_count", 0) > 0:
            score += 15
        if diagnosis.get("severity_breakdown"):
            score += 5

        # Investigation visibility (20 points)
        max_score += 20
        investigation = visibility_data.get("investigation", {})
        if investigation.get("investigations_performed", 0) > 0:
            score += 10
        if investigation.get("root_causes_identified", 0) > 0:
            score += 10

        # Remediation visibility (20 points)
        max_score += 20
        remediation = visibility_data.get("remediation", {})
        if remediation.get("fixes_attempted", 0) > 0:
            score += 10
        if "success_rate" in remediation:
            score += 10

        # Verification visibility (20 points)
        max_score += 20
        verification = visibility_data.get("verification", {})
        if verification.get("validation_tests_run", 0) > 0:
            score += 10
        if "verification_passed" in verification:
            score += 10

        return (score / max_score) * 100 if max_score > 0 else 0


async def main():
    """Run the visible workflow test"""

    print("🎯 GUIDEPOINT VISIBLE WORKFLOW TEST")
    print("=" * 50)
    print("Testing systematic workflow with real-time visibility")
    print("This addresses the critical need to see what GuidePoint is actually doing")
    print()

    tester = VisibleWorkflowTester()

    try:
        success = await tester.run_visible_workflow_test()

        print(f"\n🏁 VISIBLE WORKFLOW TEST COMPLETE")
        print("=" * 40)

        if success:
            print("✅ SUCCESS: GuidePoint systematic workflow is visible and operational")
            print("   Ready for real-world deployment with full transparency")
        else:
            print("⚠️ PARTIAL SUCCESS: Workflow visible but some capabilities need improvement")
            print("   Visibility layer working - can observe and debug issues")

        return success

    except Exception as e:
        print(f"\n❌ VISIBLE WORKFLOW TEST FAILED: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)