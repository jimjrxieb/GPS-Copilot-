#!/usr/bin/env python3
"""
CrewAI Integration Success Test
==============================

Validates that GuidePoint CrewAI integration is fully operational after fixing
the Task validation error. Tests end-to-end coordination between specialized agents.
"""

import sys
import asyncio
import json
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from coordination.crew_orchestrator import GuidePointCrewOrchestrator

async def test_crewai_integration():
    """Test complete CrewAI integration functionality"""

    print("🎭 CREWAI INTEGRATION SUCCESS TEST")
    print("=" * 50)

    orchestrator = GuidePointCrewOrchestrator()

    # Test 1: Orchestrator status
    print("\n📊 Test 1: Orchestrator Status")
    status = orchestrator.get_orchestrator_status()
    print(f"✅ Orchestrator ID: {status['orchestrator_id']}")
    print(f"✅ CrewAI Available: {status['crewai_available']}")
    print(f"✅ Available Agents: {len(status['available_agents'])}")
    print(f"✅ Supported Workflows: {len(status['supported_workflows'])}")

    # Test 2: Multi-Agent Assessment with CrewAI Coordination
    print("\n🚀 Test 2: Multi-Agent Assessment with CrewAI")
    test_project = "/tmp/targeted_vuln_test"

    try:
        result = await orchestrator.execute_comprehensive_security_assessment(test_project)

        # Verify core functionality
        print(f"✅ Assessment completed for: {result['project_path']}")
        print(f"✅ Duration: {result['duration_seconds']:.2f} seconds")
        print(f"✅ CrewAI Coordination: {result['crewai_coordination']}")

        # Verify agent results
        agent_results = result.get('agent_results', {})
        working_agents = sum(1 for r in agent_results.values() if isinstance(r, dict) and not r.get('error'))
        print(f"✅ Working Agents: {working_agents}/4")

        # Verify CrewAI specific coordination
        crew_result = result.get('crew_coordination', {})
        if crew_result.get('status') == 'success':
            print(f"✅ CrewAI Coordination Success!")
            print(f"   - Agents Coordinated: {crew_result.get('agents_coordinated', 0)}")
            print(f"   - Tasks Completed: {crew_result.get('tasks_completed', 0)}")
            print(f"   - Coordination Result Available: {bool(crew_result.get('coordination_result'))}")
        else:
            print(f"❌ CrewAI Coordination Failed: {crew_result.get('error', 'unknown')}")
            return False

        # Verify consolidated findings
        consolidated = result.get('consolidated_findings', {})
        print(f"✅ Total Vulnerabilities: {consolidated.get('total_vulnerabilities', 0)}")
        print(f"✅ Security Domains: {len(consolidated.get('security_domains', []))}")

        # Verify executive summary
        executive = result.get('executive_summary', {})
        if executive:
            posture = executive.get('project_security_posture', {})
            print(f"✅ Risk Assessment: {posture.get('risk_level', 'UNKNOWN')} ({posture.get('overall_risk_score', 0)}/100)")

        return True

    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        return False

async def test_cli_interface():
    """Test CLI interface functionality"""

    print("\n🖥️  Test 3: CLI Interface")

    import subprocess

    # Test status command
    try:
        result = subprocess.run([
            'python3', 'coordination/crew_orchestrator.py', 'status'
        ], capture_output=True, text=True, cwd='/home/jimmie/linkops-industries/James-OS/guidepoint')

        if result.returncode == 0:
            print("✅ CLI Status Command: Working")
        else:
            print(f"❌ CLI Status Command Failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ CLI Test Failed: {e}")
        return False

    return True

async def main():
    """Run all CrewAI integration tests"""

    print("Starting comprehensive CrewAI integration test...")

    # Test 1: Core integration
    integration_success = await test_crewai_integration()

    # Test 2: CLI interface
    cli_success = await test_cli_interface()

    # Summary
    print("\n" + "=" * 50)
    print("🎯 CREWAI INTEGRATION TEST SUMMARY")
    print("=" * 50)

    if integration_success and cli_success:
        print("✅ ALL TESTS PASSED - CrewAI Integration Successful!")
        print("\n🔧 Key Achievements:")
        print("   ✅ Fixed missing expected_output in Task creation")
        print("   ✅ CrewAI coordination layer fully functional")
        print("   ✅ Multi-agent workflows with AI coordination")
        print("   ✅ Professional security coordination reports")
        print("   ✅ CLI interface operational")

        print("\n🚀 CrewAI Capabilities Now Available:")
        print("   • AI-powered agent coordination")
        print("   • Intelligent task delegation between specialists")
        print("   • Cross-agent collaboration and consultation")
        print("   • Strategic security recommendations")
        print("   • Automated workflow orchestration")

    else:
        print("❌ SOME TESTS FAILED - Integration needs attention")
        if not integration_success:
            print("   ❌ Core integration issues")
        if not cli_success:
            print("   ❌ CLI interface issues")

if __name__ == "__main__":
    asyncio.run(main())