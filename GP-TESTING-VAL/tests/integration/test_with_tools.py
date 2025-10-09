#!/usr/bin/env python3
"""
Test GuidePoint Agents After Security Tools Installation
========================================================

Verifies that agents can now utilize installed security tools
for comprehensive vulnerability detection.
"""

import sys
import asyncio
import subprocess
from pathlib import Path

sys.path.insert(0, '/home/jimmie/linkops-industries/James-OS/guidepoint')

from agents.scanner_agent.agent import ScannerAgent
from agents.kubernetes_agent.agent import KubernetesAgent
from agents.iac_policy_agent.agent import IaCPolicyAgent
from agents.devsecops_agent.agent import DevSecOpsAgent
from coordination.crew_orchestrator import GuidePointCrewOrchestrator

def check_tool_availability():
    """Check which security tools are available"""
    tools = {
        'bandit': ['bandit', '--version'],
        'checkov': ['checkov', '--version'],
        'safety': ['safety', '--version'],
        'trivy': ['trivy', '--version'],
        'tfsec': ['tfsec', '--version'],
        'kubescape': ['kubescape', 'version'],
        'gitleaks': ['gitleaks', 'version']
    }

    print("🔍 Security Tools Status:")
    available_count = 0

    for tool, cmd in tools.items():
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"  ✅ {tool}: Available")
                available_count += 1
            else:
                print(f"  ❌ {tool}: Not found")
        except:
            print(f"  ❌ {tool}: Not found")

    print(f"\n📊 Tools available: {available_count}/{len(tools)}")
    return available_count

async def test_enhanced_scanning():
    """Test agents with enhanced tool capabilities"""

    # Use the Portfolio project for real testing
    test_project = "/home/jimmie/linkops-industries/Portfolio"

    if not Path(test_project).exists():
        print(f"⚠️  Portfolio project not found at {test_project}")
        print("Using complex verification test instead...")
        test_project = "/tmp/complex_verification"

    print(f"\n🎯 Testing agents on: {test_project}")

    # Test Scanner Agent with tools
    print("\n🔍 Testing Scanner Agent with enhanced tools...")
    scanner = ScannerAgent()
    scanner_result = await scanner.analyze_project(test_project)
    vulns = scanner_result.get('vulnerabilities', [])
    print(f"  Found {len(vulns)} vulnerabilities")
    if vulns:
        for v in vulns[:3]:
            print(f"    - {v.get('description', 'Unknown')} ({v.get('severity', 'MEDIUM')})")

    # Test IaC Agent with Checkov/TFSec
    print("\n🏗️ Testing IaC/Policy Agent with Checkov/TFSec...")
    iac = IaCPolicyAgent()
    iac_result = await iac.analyze_infrastructure(test_project)
    findings = iac_result.get('security_findings', [])
    print(f"  Found {len(findings)} security findings")
    print(f"  Tools used: {list(iac_result.get('tool_results', {}).keys())}")

    # Test Kubernetes Agent
    print("\n☸️ Testing Kubernetes Agent with Kubescape...")
    k8s = KubernetesAgent()
    k8s_result = await k8s.analyze_cluster_security(
        kubeconfig_path=None,
        manifests_path=test_project
    )
    issues = k8s_result.get('security_issues', [])
    print(f"  Found {len(issues)} Kubernetes security issues")

    # Test full orchestration
    print("\n🎭 Testing Full Orchestration with all tools...")
    orchestrator = GuidePointCrewOrchestrator()
    full_result = await orchestrator.execute_comprehensive_security_assessment(test_project)

    consolidated = full_result.get('consolidated_findings', {})
    print(f"\n📊 COMPREHENSIVE RESULTS WITH TOOLS:")
    print(f"  Total vulnerabilities: {consolidated.get('total_vulnerabilities', 0)}")
    print(f"  Critical findings: {len(consolidated.get('critical_findings', []))}")
    print(f"  High findings: {len(consolidated.get('high_findings', []))}")
    print(f"  Security domains: {consolidated.get('security_domains', [])}")

    executive = full_result.get('executive_summary', {})
    posture = executive.get('project_security_posture', {})
    print(f"  Risk level: {posture.get('risk_level', 'Unknown')}")
    print(f"  Risk score: {posture.get('overall_risk_score', 0)}/100")

    # Check improvement
    improved = consolidated.get('total_vulnerabilities', 0) > 10
    print(f"\n{'✅ SIGNIFICANT IMPROVEMENT' if improved else '⚠️  Limited improvement'}")
    print(f"Tools integration {'successful' if improved else 'needs more work'}")

async def main():
    print("🔧 GUIDEPOINT ENHANCED CAPABILITY TEST")
    print("=" * 50)

    # Check tool availability
    tools_available = check_tool_availability()

    if tools_available < 3:
        print("\n⚠️  Warning: Less than 3 security tools available")
        print("Run: bash /home/jimmie/linkops-industries/James-OS/guidepoint/install_security_tools.sh")
        print("Then try again")

    # Run enhanced tests
    await test_enhanced_scanning()

if __name__ == "__main__":
    asyncio.run(main())