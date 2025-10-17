#!/usr/bin/env python3
"""
GuidePoint Status Command - Simple CLI to monitor GuidePoint operations
======================================================================

Usage:
    python gp_status.py               # Live dashboard
    python gp_status.py --once        # Single status check
    python gp_status.py --health      # Health check only
    python gp_status.py --workflows   # Show active workflows only

This provides essential visibility into what GuidePoint is actually doing.
"""

import asyncio
import sys
import argparse
import json
from pathlib import Path

# Add GuidePoint to path
sys.path.insert(0, str(Path(__file__).parent))

from automation_engine.automation.guidepoint_status import GuidePointStatusMonitor


async def show_single_status():
    """Show status once and exit"""

    print("🎯 GUIDEPOINT STATUS CHECK")
    print("=" * 40)

    monitor = GuidePointStatusMonitor()
    status = await monitor.get_current_status()

    # System Health
    health = status['system_health']
    print("🏥 System Health:")
    print(f"   CPU: {health['cpu_usage']:.1f}% | Memory: {health['memory_usage']:.1f}% | Disk: {health['disk_usage']:.1f}%")
    print(f"   Kubernetes: {'✅' if health['kubernetes_accessible'] else '❌'} | Docker: {'✅' if health['docker_available'] else '❌'}")
    print(f"   Uptime: {health['uptime']}")
    print()

    # Active Workflows
    workflows = status['active_workflows']
    print(f"🔄 Active Workflows: {len(workflows)}")

    if workflows:
        for workflow in workflows:
            print(f"   • {workflow['workflow_id'][:12]}... ({workflow['status']}) - {workflow['current_step']}")
    else:
        print("   No active workflows")
    print()

    # Execution Metrics
    metrics = status['execution_metrics']
    success_rate = (metrics['successful_workflows'] / max(metrics['total_workflows'], 1)) * 100
    print(f"📊 Metrics: {metrics['total_workflows']} total | {success_rate:.1f}% success rate")

    # Infrastructure
    infra = status['infrastructure_state']
    print(f"🏗️ Infrastructure: {infra.get('cluster_context', 'No cluster')} | Accessible: {'✅' if infra.get('cluster_accessible') else '❌'}")


async def show_health_only():
    """Show health status only"""

    monitor = GuidePointStatusMonitor()
    status = await monitor.get_current_status()
    health = status['system_health']

    print("🏥 GUIDEPOINT HEALTH CHECK")
    print("=" * 30)

    # Simple pass/fail health indicators
    health_checks = [
        ("CPU Usage", health['cpu_usage'] < 80, f"{health['cpu_usage']:.1f}%"),
        ("Memory Usage", health['memory_usage'] < 80, f"{health['memory_usage']:.1f}%"),
        ("Disk Usage", health['disk_usage'] < 90, f"{health['disk_usage']:.1f}%"),
        ("Kubernetes", health['kubernetes_accessible'], "Available" if health['kubernetes_accessible'] else "Unavailable"),
        ("Docker", health['docker_available'], "Available" if health['docker_available'] else "Unavailable")
    ]

    all_healthy = True
    for check_name, is_healthy, value in health_checks:
        status_icon = "✅" if is_healthy else "❌"
        print(f"{status_icon} {check_name}: {value}")
        if not is_healthy:
            all_healthy = False

    print()
    print(f"Overall Health: {'✅ HEALTHY' if all_healthy else '❌ ISSUES DETECTED'}")

    return all_healthy


async def show_workflows_only():
    """Show workflow status only"""

    monitor = GuidePointStatusMonitor()
    status = await monitor.get_current_status()
    workflows = status['active_workflows']

    print("🔄 GUIDEPOINT ACTIVE WORKFLOWS")
    print("=" * 35)

    if workflows:
        for workflow in workflows:
            status_icons = {
                'running': '🟡',
                'completed': '✅',
                'failed': '❌',
                'paused': '⏸️'
            }

            icon = status_icons.get(workflow['status'], '❓')

            print(f"{icon} {workflow['workflow_id']}")
            print(f"   Status: {workflow['status']}")
            print(f"   Current Step: {workflow['current_step']}")
            print(f"   Progress: {len(workflow['steps_completed'])}/5 steps completed")
            print(f"   Runtime: {workflow['elapsed_time']}")
            print(f"   Project: {workflow['project_path']}")
            print(f"   Findings: {workflow['findings_count']}")
            print(f"   Success Rate: {workflow['success_rate']:.1f}%")
            print()
    else:
        print("No active workflows")
        print()

        # Show recent metrics
        metrics = status['execution_metrics']
        if metrics['total_workflows'] > 0:
            print("📊 Recent Activity:")
            success_rate = (metrics['successful_workflows'] / metrics['total_workflows']) * 100
            print(f"   Total Workflows Run: {metrics['total_workflows']}")
            print(f"   Success Rate: {success_rate:.1f}%")
            print(f"   Average Execution Time: {metrics['average_execution_time']:.1f}s")


async def run_live_dashboard():
    """Run the live status dashboard"""

    print("🎯 Starting GuidePoint Live Status Dashboard...")
    print("Press Ctrl+C to exit")
    print()

    monitor = GuidePointStatusMonitor()

    try:
        await monitor.display_status_dashboard()
    except KeyboardInterrupt:
        print("\n\n👋 GuidePoint Status Monitor stopped")


async def test_with_sample_workflow():
    """Create a sample workflow for testing the status monitor"""

    print("🧪 TESTING STATUS MONITOR WITH SAMPLE WORKFLOW")
    print("=" * 50)

    monitor = GuidePointStatusMonitor()

    # Simulate a workflow
    workflow_id = "test-workflow-12345"

    print("Starting sample workflow...")
    monitor.start_workflow_tracking(workflow_id, "/tmp/test-project", 3)

    # Simulate workflow progression
    steps = ["discovery", "diagnosis", "investigation", "remediation", "verification"]
    completed_steps = []

    for i, step in enumerate(steps):
        print(f"Simulating step: {step}")
        completed_steps.append(step)

        success_rate = (len(completed_steps) / len(steps)) * 100
        monitor.update_workflow_status(workflow_id, step, completed_steps, success_rate)

        # Show current status
        status = await monitor.get_current_status()
        active_workflow = status['active_workflows'][0] if status['active_workflows'] else None

        if active_workflow:
            print(f"   Status: {active_workflow['status']} | Step: {active_workflow['current_step']}")
            print(f"   Progress: {len(active_workflow['steps_completed'])}/5")

        await asyncio.sleep(1)  # Simulate processing time

    # Complete workflow
    monitor.complete_workflow(workflow_id, True)
    print("\nWorkflow completed!")

    # Show final status
    await show_single_status()


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(description="GuidePoint Status Monitor")
    parser.add_argument('--once', action='store_true', help='Show status once and exit')
    parser.add_argument('--health', action='store_true', help='Show health check only')
    parser.add_argument('--workflows', action='store_true', help='Show active workflows only')
    parser.add_argument('--test', action='store_true', help='Run with sample workflow for testing')

    args = parser.parse_args()

    try:
        if args.test:
            asyncio.run(test_with_sample_workflow())
        elif args.once:
            asyncio.run(show_single_status())
        elif args.health:
            healthy = asyncio.run(show_health_only())
            sys.exit(0 if healthy else 1)
        elif args.workflows:
            asyncio.run(show_workflows_only())
        else:
            asyncio.run(run_live_dashboard())

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()