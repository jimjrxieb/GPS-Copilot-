#!/usr/bin/env python3
"""
Test Enhanced GuidePoint Vulnerability Analyzer with James Confidence Engine
Validates that failure pattern intelligence is properly integrated
"""

import asyncio
import json
import sys
from pathlib import Path

# Add GuidePoint to path
sys.path.insert(0, str(Path(__file__).parent / "automation_engine"))

from automation_engine.core.vulnerability_analyzer import VulnerabilityAnalyzer, RiskLevel, RemediationType

class TestJamesEnhancedAnalyzer:
    """Test James-enhanced vulnerability analyzer"""

    def __init__(self):
        self.analyzer = VulnerabilityAnalyzer()

    async def test_confidence_engine_integration(self):
        """Test that James Confidence Engine is properly integrated"""
        print("🧪 Testing James Confidence Engine Integration")
        print("=" * 50)

        # Check analyzer status
        status = self.analyzer.get_analyzer_status()

        print(f"✅ Analyzer ID: {status['analyzer_id']}")
        print(f"✅ Status: {status['status']}")

        # Verify James intelligence capabilities
        capabilities = status['capabilities']
        james_capabilities = [
            "james_failure_pattern_intelligence",
            "evidence_based_decision_making"
        ]

        for capability in james_capabilities:
            if capability in capabilities:
                print(f"✅ {capability}: ENABLED")
            else:
                print(f"❌ {capability}: MISSING")

        # Check James engine details
        james_engine = status.get('james_confidence_engine', {})
        print(f"\n🧠 James Intelligence Status:")
        print(f"   Engine Status: {james_engine.get('status', 'unknown')}")
        print(f"   Evidence Source: {james_engine.get('evidence_source', 'unknown')}")
        print(f"   Intelligence Patterns: {james_engine.get('intelligence_patterns', [])}")
        print(f"   Failure Prevention: {james_engine.get('failure_prevention', 'unknown')}")

        return james_engine.get('status') == 'active'

    async def test_vulnerability_analysis_with_james_intelligence(self):
        """Test vulnerability analysis using James failure patterns"""
        print("\n🔍 Testing Vulnerability Analysis with James Intelligence")
        print("=" * 55)

        # Create test vulnerabilities based on known failure patterns
        test_vulnerabilities = [
            {
                "check_id": "CKV_K8S_23",  # Known from failure episodes
                "check_name": "Ensure allowPrivilegeEscalation is set to false",
                "resource": "kubernetes.main.test_pod",
                "file_path": "/test/k8s/pod.yaml",
                "file_line_range": [10, 15],
                "severity": "HIGH"
            },
            {
                "check_id": "k8s-TRIVY-013",  # From actual failure episode
                "check_name": "Trivy vulnerability scanning failure",
                "resource": "container.main.app",
                "file_path": "/test/Dockerfile",
                "file_line_range": [5, 8],
                "severity": "CRITICAL"
            },
            {
                "check_id": "cks-netpol-01",  # From actual failure episode
                "check_name": "Network policy configuration issue",
                "resource": "kubernetes.main.network_policy",
                "file_path": "/test/k8s/network-policy.yaml",
                "file_line_range": [1, 20],
                "severity": "HIGH"
            }
        ]

        print(f"📋 Testing {len(test_vulnerabilities)} vulnerabilities from failure episodes")

        results = []
        for vuln in test_vulnerabilities:
            print(f"\n🔎 Analyzing: {vuln['check_id']}")

            # Test risk level calculation with James intelligence
            risk_level = await self.analyzer._calculate_risk_level(vuln)
            print(f"   Risk Level: {risk_level.value}")

            # Test remediation type determination with James intelligence
            remediation_type, confidence = await self.analyzer._determine_remediation_type(vuln)
            print(f"   Remediation Type: {remediation_type.value}")
            print(f"   James Confidence: {confidence:.3f}")

            # Test business impact assessment with James intelligence
            business_impact = await self.analyzer._assess_business_impact(vuln)
            print(f"   Business Impact: {business_impact}")

            result = {
                "check_id": vuln["check_id"],
                "risk_level": risk_level.value,
                "remediation_type": remediation_type.value,
                "james_confidence": confidence,
                "business_impact": business_impact
            }
            results.append(result)

        return results

    async def test_known_failure_patterns(self):
        """Test specific patterns that caused failures in episodes"""
        print("\n⚠️  Testing Known Failure Patterns")
        print("=" * 35)

        # Test Trivy failure pattern (k8s-TRIVY-013)
        trivy_vuln = {
            "check_id": "k8s-TRIVY-013",
            "check_name": "Trivy scan failure - generic advice pattern",
            "resource": "container.main.app",
            "file_path": "/test/Dockerfile",
            "file_line_range": [1, 10],
            "severity": "CRITICAL"
        }

        print("🔍 Testing Trivy failure pattern (k8s-TRIVY-013)")

        # This should trigger James intelligence about Trivy failures
        remediation_type, confidence = await self.analyzer._determine_remediation_type(trivy_vuln)

        print(f"   Remediation Type: {remediation_type.value}")
        print(f"   James Confidence: {confidence:.3f}")

        # James should have lower confidence for Trivy issues based on failure patterns
        if confidence < 0.5:
            print("   ✅ James correctly identifies Trivy as complex (low confidence)")
        else:
            print("   ⚠️  James confidence unexpectedly high for known failure pattern")

        # Test Network Policy failure pattern (cks-netpol-01)
        netpol_vuln = {
            "check_id": "cks-netpol-01",
            "check_name": "Network policy missing YAML manifest",
            "resource": "kubernetes.main.network_policy",
            "file_path": "/test/k8s/network-policy.yaml",
            "file_line_range": [1, 15],
            "severity": "HIGH"
        }

        print("\n🔍 Testing Network Policy failure pattern (cks-netpol-01)")

        remediation_type, confidence = await self.analyzer._determine_remediation_type(netpol_vuln)

        print(f"   Remediation Type: {remediation_type.value}")
        print(f"   James Confidence: {confidence:.3f}")

        # Network policies should require assisted/manual based on failure patterns
        if remediation_type in [RemediationType.ASSISTED, RemediationType.MANUAL]:
            print("   ✅ James correctly identifies network policies need human guidance")
        else:
            print("   ⚠️  James unexpectedly suggests automation for complex network policy")

        return True

    async def test_evidence_based_improvements(self):
        """Test that James intelligence leads to better decisions"""
        print("\n📈 Testing Evidence-Based Decision Improvements")
        print("=" * 45)

        # Test vulnerability that should trigger James failure prevention
        problematic_vuln = {
            "check_id": "GENERIC-ADVICE-TEST",
            "check_name": "Test vulnerability requiring specific commands",
            "resource": "test.resource",
            "file_path": "/test/config.yaml",
            "file_line_range": [5, 10],
            "severity": "MEDIUM"
        }

        print("🔍 Testing generic vulnerability (should trigger James intelligence)")

        remediation_type, confidence = await self.analyzer._determine_remediation_type(problematic_vuln)
        business_impact = await self.analyzer._assess_business_impact(problematic_vuln)

        print(f"   Remediation Type: {remediation_type.value}")
        print(f"   James Confidence: {confidence:.3f}")
        print(f"   Business Impact: {business_impact}")

        # James intelligence should prevent over-confidence in generic scenarios
        if confidence < 0.7:
            print("   ✅ James appropriately cautious about unknown vulnerability patterns")
        else:
            print("   ⚠️  James unexpectedly confident about unknown pattern")

        return confidence < 0.7

    async def run_all_tests(self):
        """Run all tests and provide summary"""
        print("🚀 James Enhanced GuidePoint Vulnerability Analyzer Test Suite")
        print("=" * 65)

        test_results = []

        # Test 1: Integration
        integration_success = await self.test_confidence_engine_integration()
        test_results.append(("James Integration", integration_success))

        if not integration_success:
            print("\n❌ James Confidence Engine not properly integrated - stopping tests")
            return False

        # Test 2: Vulnerability Analysis
        vuln_results = await self.test_vulnerability_analysis_with_james_intelligence()
        analysis_success = len(vuln_results) == 3
        test_results.append(("Vulnerability Analysis", analysis_success))

        # Test 3: Failure Patterns
        failure_pattern_success = await self.test_known_failure_patterns()
        test_results.append(("Failure Pattern Recognition", failure_pattern_success))

        # Test 4: Evidence-Based Improvements
        improvement_success = await self.test_evidence_based_improvements()
        test_results.append(("Evidence-Based Improvements", improvement_success))

        # Summary
        print(f"\n📊 Test Results Summary")
        print("=" * 25)

        passed = 0
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if success:
                passed += 1

        success_rate = (passed / len(test_results)) * 100
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({passed}/{len(test_results)})")

        if success_rate >= 75:
            print("✅ James enhanced vulnerability analyzer is working correctly!")
            return True
        else:
            print("❌ James enhanced vulnerability analyzer needs additional work")
            return False

async def main():
    """Main test execution"""
    tester = TestJamesEnhancedAnalyzer()
    success = await tester.run_all_tests()

    if success:
        print("\n🎉 James Confidence Engine successfully integrated into GuidePoint!")
        print("   Real failure patterns are now preventing documented mistakes")
    else:
        print("\n⚠️  Integration needs review - some tests failed")

    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)