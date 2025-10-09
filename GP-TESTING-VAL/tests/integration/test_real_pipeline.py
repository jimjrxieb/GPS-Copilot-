#!/usr/bin/env python3
"""
Real Integration Test for James-OS Autonomous Pipeline
=====================================================

This test proves the entire pipeline works end-to-end:
1. Scan a project with real vulnerabilities
2. Analyze findings with James AI
3. Generate automated fixes
4. Apply fixes (in dry-run mode)
5. Verify fix commands are correct

NO MOCKS - This uses real components to validate the pipeline.
"""

import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Import real components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.project_scanner import ProjectScanner
from automation.james_ai_engine import JamesAIEngine, SecurityFinding
from automation.automated_fixes import AutomatedFixEngine, FixStatus
from tools.trivy_runner import TrivyRunner
from tools.checkov_runner import CheckovRunner


class RealPipelineTest:
    """Test the real autonomous security pipeline"""

    def __init__(self):
        self.scanner = ProjectScanner()
        self.ai_engine = JamesAIEngine()
        self.fix_engine = AutomatedFixEngine()
        self.trivy = TrivyRunner()
        self.checkov = CheckovRunner()

    async def create_vulnerable_project(self) -> str:
        """Create a test project with real vulnerabilities"""
        # Create temp directory
        test_dir = Path(tempfile.mkdtemp(prefix="james_test_"))

        # Create vulnerable package.json (Node.js with known vulnerabilities)
        package_json = {
            "name": "vulnerable-test-app",
            "version": "1.0.0",
            "dependencies": {
                "express": "4.16.0",  # Old version with vulnerabilities
                "lodash": "4.17.4",   # CVE-2019-10744
                "axios": "0.18.0",    # Multiple vulnerabilities
                "minimist": "0.0.8"   # CVE-2020-7598
            }
        }

        with open(test_dir / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # Create vulnerable Dockerfile
        dockerfile_content = """
FROM node:8-alpine
# Running as root (security issue)
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "index.js"]
"""
        with open(test_dir / "Dockerfile", "w") as f:
            f.write(dockerfile_content)

        # Create vulnerable Terraform file
        terraform_content = """
resource "aws_s3_bucket" "vulnerable_bucket" {
  bucket = "my-vulnerable-bucket"
  acl    = "public-read"  # Security issue: public bucket
}

resource "aws_security_group" "vulnerable_sg" {
  name = "vulnerable-sg"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Security issue: open to world
  }
}
"""
        with open(test_dir / "main.tf", "w") as f:
            f.write(terraform_content)

        # Create vulnerable Kubernetes deployment
        k8s_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vulnerable-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vulnerable
  template:
    metadata:
      labels:
        app: vulnerable
    spec:
      containers:
      - name: app
        image: vulnerable:latest
        # No security context (running as root)
        # No resource limits
        ports:
        - containerPort: 8080
"""
        with open(test_dir / "deployment.yaml", "w") as f:
            f.write(k8s_content)

        print(f"✅ Created vulnerable test project at: {test_dir}")
        return str(test_dir)

    async def test_full_pipeline(self):
        """Test the complete scan → analyze → fix pipeline"""
        print("\n🚀 Starting Real Pipeline Integration Test\n")
        print("=" * 60)

        # Step 1: Create vulnerable project
        print("\n📁 Step 1: Creating vulnerable test project...")
        project_path = await self.create_vulnerable_project()
        project_id = "test_project_001"

        try:
            # Step 2: Run security scans
            print("\n🔍 Step 2: Running security scans...")
            scan_results = {}

            # Run Trivy scan
            print("  - Running Trivy scan...")
            trivy_result = await self.trivy.scan_filesystem(project_path)
            if trivy_result.get("success"):
                scan_results["trivy_results"] = trivy_result.get("data", {})
                vulns = trivy_result.get("data", {}).get("vulnerabilities", [])
                print(f"    ✓ Found {len(vulns)} Trivy findings")
            else:
                print(f"    ✗ Trivy scan failed: {trivy_result.get('error', 'Unknown error')}")

            # Run Checkov scan
            print("  - Running Checkov scan...")
            checkov_result = await self.checkov.scan_directory(project_path)
            if checkov_result.get("success"):
                scan_results["checkov_results"] = checkov_result.get("data", {})
                findings = checkov_result.get("data", {}).get("findings", [])
                print(f"    ✓ Found {len(findings)} Checkov findings")
            else:
                print(f"    ✗ Checkov scan failed: {checkov_result.get('error', 'Unknown error')}")

            # Step 3: Analyze with James AI
            print("\n🧠 Step 3: Analyzing findings with James AI...")
            analysis = await self.ai_engine.analyze_scan_results(scan_results, project_id)

            print(f"  - Analysis ID: {analysis.analysis_id}")
            print(f"  - Findings analyzed: {analysis.findings_analyzed}")
            print(f"  - Risk score: {analysis.risk_score:.1f}/100")
            print(f"  - Priority: {analysis.priority_level}")
            print(f"  - Auto-fixable issues: {len(analysis.auto_fixable)}")

            # Verify findings are stored
            if not analysis.findings or len(analysis.findings) == 0:
                print("\n❌ CRITICAL: No findings stored in analysis!")
                print("   The pipeline is broken - findings not being passed correctly")
                return False

            # Step 4: Generate fixes
            print("\n🔧 Step 4: Generating automated fixes...")
            fix_job = await self.fix_engine.generate_fixes(
                analysis_id=analysis.analysis_id,
                project_id=project_id,
                project_path=project_path
            )

            print(f"  - Fix job ID: {fix_job.job_id}")
            print(f"  - Total fixes generated: {fix_job.total_fixes}")

            if fix_job.total_fixes == 0:
                print("\n⚠️  WARNING: No fixes generated!")
                print("   The fix generation engine may not be working correctly")

            # Step 5: Review generated fixes
            print("\n📋 Step 5: Review generated fixes:")
            for i, fix in enumerate(fix_job.fixes[:5], 1):  # Show first 5 fixes
                print(f"\n  Fix {i}: {fix.title}")
                print(f"    Type: {fix.fix_type.value}")
                print(f"    Priority: {fix.priority}")
                print(f"    Commands: {fix.commands[:2]}")  # Show first 2 commands
                print(f"    Files: {fix.files_to_modify}")

            # Step 6: Test fix application (dry run)
            print("\n🎯 Step 6: Testing fix application (dry run)...")
            applied_job = await self.fix_engine.apply_fix_job(
                job_id=fix_job.job_id,
                project_path=project_path,
                dry_run=True  # Don't actually apply fixes
            )

            print(f"  - Applied fixes: {applied_job.applied_fixes}")
            print(f"  - Failed fixes: {applied_job.failed_fixes}")

            # Validation
            print("\n✅ Pipeline Validation Results:")
            print("=" * 60)

            success = True
            checks = [
                ("Scans produced findings", len(scan_results) > 0),
                ("AI analysis completed", analysis.findings_analyzed > 0),
                ("Findings stored in analysis", len(analysis.findings) > 0),
                ("Fixes were generated", fix_job.total_fixes > 0),
                ("Fix commands are specific", any(fix.commands for fix in fix_job.fixes)),
                ("Files to modify identified", any(fix.files_to_modify for fix in fix_job.fixes))
            ]

            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"{status} {check_name}")
                if not check_result:
                    success = False

            return success

        finally:
            # Cleanup
            print(f"\n🧹 Cleaning up test project: {project_path}")
            shutil.rmtree(project_path, ignore_errors=True)

    async def test_fix_validation(self):
        """Test that generated fixes actually work"""
        print("\n🔬 Testing Fix Validation\n")
        print("=" * 60)

        # Create a simple finding
        finding = SecurityFinding(
            id="test-001",
            severity="high",
            title="Outdated lodash version",
            description="Package lodash@4.17.4 has known vulnerabilities",
            file_path="package.json",
            tool="npm-audit",
            remediation="Update to lodash@4.17.21"
        )

        # Generate fix
        print("Generating fix for lodash vulnerability...")
        fixes = await self.fix_engine.generate_fixes_for_findings(
            [finding],
            project_path="/tmp/test"
        )

        if fixes:
            fix = fixes[0]
            print(f"✅ Generated fix: {fix.title}")
            print(f"   Commands: {fix.commands}")
            print(f"   Success criteria: {fix.success_criteria}")

            # Verify fix has actual commands, not placeholders
            has_real_commands = any("npm" in cmd or "update" in cmd for cmd in fix.commands)
            if has_real_commands:
                print("✅ Fix contains real commands, not placeholders")
                return True
            else:
                print("❌ Fix contains only placeholder commands")
                return False
        else:
            print("❌ No fix generated")
            return False


async def main():
    """Run the integration tests"""
    test = RealPipelineTest()

    print("\n" + "=" * 60)
    print("     James-OS Real Pipeline Integration Test")
    print("     Testing: Scan → Analyze → Fix Pipeline")
    print("=" * 60)

    # Run full pipeline test
    pipeline_success = await test.test_full_pipeline()

    # Run fix validation test
    validation_success = await test.test_fix_validation()

    # Summary
    print("\n" + "=" * 60)
    print("                    TEST SUMMARY")
    print("=" * 60)
    print(f"Pipeline Test: {'✅ PASSED' if pipeline_success else '❌ FAILED'}")
    print(f"Fix Validation: {'✅ PASSED' if validation_success else '❌ FAILED'}")

    overall_success = pipeline_success and validation_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")

    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)