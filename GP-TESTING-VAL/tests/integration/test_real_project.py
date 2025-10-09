#!/usr/bin/env python3
"""
Reality Test: GuidePoint Against Real Project
===========================================

This is the honest test - let's see what GuidePoint actually does
against a real project with real vulnerabilities.

No test projects, no cleanup - this runs against actual infrastructure.
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from automation_engine.automation.infrastructure_execution_engine import QwenStyleWorkflowOrchestrator
from automation_engine.automation.james_ai_engine import SecurityFinding
from automation_engine.automation.guidepoint_status import GuidePointStatusMonitor


async def test_real_project():
    """Test GuidePoint against the actual ms-008-desktop-ui project"""

    real_project_path = "/home/jimmie/linkops-industries/James-OS/ms-008-desktop-ui"

    print("🔍 REALITY TEST: GuidePoint vs Real Project")
    print("=" * 50)
    print(f"Target: {real_project_path}")
    print()

    # Check if project exists
    if not Path(real_project_path).exists():
        print("❌ Project doesn't exist")
        return False

    # Initialize components
    monitor = GuidePointStatusMonitor()
    orchestrator = QwenStyleWorkflowOrchestrator()

    # Create real vulnerability findings based on what we might find
    real_vulnerabilities = [
        SecurityFinding(
            id="real-node-deps",
            severity="high",
            title="Node.js dependencies may have vulnerabilities",
            description="package.json dependencies should be audited",
            file_path=os.path.join(real_project_path, "package.json"),
            tool="npm_audit",
            remediation="Run npm audit fix"
        )
    ]

    workflow_id = "reality-test-001"

    print("🚀 Starting workflow against real project...")
    monitor.start_workflow_tracking(workflow_id, real_project_path, len(real_vulnerabilities))

    try:
        # Run the actual workflow
        results = await orchestrator.execute_systematic_remediation(
            real_project_path,
            real_vulnerabilities
        )

        # Check what actually happened
        print("\n📊 REALITY CHECK RESULTS:")
        print(f"Workflow completed: {'✅' if results.get('overall_success') else '❌'}")
        print(f"Steps completed: {len(results.get('steps_completed', []))}/5")

        # Look for actual file changes
        if results.get('step_results', {}).get('remediation', {}).get('fixes_successful', 0) > 0:
            print("🔍 Checking for actual file modifications...")

            # Check if package.json was modified
            package_json_path = Path(real_project_path) / "package.json"
            if package_json_path.exists():
                # Look for backup files
                backup_files = list(Path(real_project_path).glob("package.json.backup.*"))
                print(f"   Backup files created: {len(backup_files)}")

                if backup_files:
                    print("   ✅ Real backup files found - changes were actually made")
                    for backup in backup_files:
                        print(f"      {backup}")
                else:
                    print("   ⚠️ No backup files - changes may not have been made")

        monitor.complete_workflow(workflow_id, results.get('overall_success', False))

        return results.get('overall_success', False)

    except Exception as e:
        print(f"❌ Reality test failed: {e}")
        monitor.complete_workflow(workflow_id, False)
        return False


async def check_current_status():
    """Check current GuidePoint status after real test"""

    monitor = GuidePointStatusMonitor()
    status = await monitor.get_current_status()

    print("\n📊 POST-TEST STATUS:")
    print(f"Total workflows: {status['execution_metrics']['total_workflows']}")
    print(f"Active workflows: {len(status['active_workflows'])}")

    if status['active_workflows']:
        for workflow in status['active_workflows']:
            print(f"   {workflow['workflow_id']}: {workflow['status']}")


async def main():
    print("🎯 GUIDEPOINT REALITY TEST")
    print("Testing against real infrastructure with real consequences")
    print()

    # Run real test
    success = await test_real_project()

    # Check status
    await check_current_status()

    print(f"\n🏁 REALITY TEST RESULT: {'✅ SUCCESS' if success else '❌ FAILED'}")

    if success:
        print("GuidePoint successfully executed against real project")
    else:
        print("GuidePoint failed against real project - needs more work")

    return success


if __name__ == "__main__":
    asyncio.run(main())