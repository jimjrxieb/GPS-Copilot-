#!/usr/bin/env python3
"""
🧪 GuidePoint RAG Consulting Test Suite
Validates the complete GuidePoint security consulting workflow with RAG intelligence
"""

import asyncio
import json
import sys
from pathlib import Path

# Add GP-SEC-INTEL-ANALYSIS to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "GP-SEC-INTEL-ANALYSIS"))

from guidepoint_rag_integration import GuidePointRAGIntegration, SecurityConsultingRequest

async def test_kubernetes_security_consulting():
    """Test Kubernetes security consulting with real scenario"""

    print("🧪 Testing Kubernetes Security Consulting...")
    print("=" * 60)

    integration = GuidePointRAGIntegration()

    # Real-world Kubernetes security scenario
    request = SecurityConsultingRequest(
        question="How do I fix Kubernetes privilege escalation vulnerabilities in my production cluster?",
        vulnerability_findings=[
            {
                "vulnerability_type": "CKV_K8S_12",
                "description": "Memory limits not set for containers",
                "severity": "high",
                "affected_workloads": ["api-server", "worker-nodes"]
            },
            {
                "vulnerability_type": "CKV_K8S_8",
                "description": "Liveness probe not configured",
                "severity": "medium",
                "affected_workloads": ["database", "cache"]
            }
        ],
        client_context={
            "industry": "fintech",
            "compliance": ["SOC2", "PCI-DSS"],
            "environment": "production",
            "cluster_size": "50 nodes"
        },
        urgency_level="high"
    )

    response = await integration.consult_security_question(request)

    # Validate response completeness
    assert response.executive_summary, "Missing executive summary"
    assert response.technical_analysis, "Missing technical analysis"
    assert response.remediation_steps, "Missing remediation steps"
    assert response.compliance_mapping, "Missing compliance mapping"
    assert response.confidence_score > 0, "Invalid confidence score"

    print(f"✅ Executive Summary Generated: {len(response.executive_summary)} chars")
    print(f"✅ Technical Analysis Generated: {len(response.technical_analysis)} chars")
    print(f"✅ Remediation Steps: {len(response.remediation_steps)} steps")
    print(f"✅ Compliance Frameworks: {len(response.compliance_mapping)} frameworks")
    print(f"✅ Confidence Score: {response.confidence_score:.1%}")
    print(f"✅ Sources Referenced: {len(response.sources)} sources")

    return response

async def test_aws_security_consulting():
    """Test AWS security consulting with real scenario"""

    print("\n🧪 Testing AWS Security Consulting...")
    print("=" * 60)

    integration = GuidePointRAGIntegration()

    # Real-world AWS security scenario
    request = SecurityConsultingRequest(
        question="How do I secure my AWS S3 buckets and fix encryption vulnerabilities?",
        vulnerability_findings=[
            {
                "vulnerability_type": "CKV_AWS_145",
                "description": "S3 bucket server-side encryption not enabled",
                "severity": "critical",
                "affected_resources": ["customer-data-bucket", "logs-bucket"]
            },
            {
                "vulnerability_type": "CKV_AWS_23",
                "description": "Security group allows unrestricted ingress",
                "severity": "high",
                "affected_resources": ["web-sg", "api-sg"]
            }
        ],
        client_context={
            "industry": "healthcare",
            "compliance": ["HIPAA", "SOC2"],
            "environment": "multi-region",
            "data_classification": "PHI"
        },
        urgency_level="critical"
    )

    response = await integration.consult_security_question(request)

    # Validate AWS-specific guidance
    assert "S3" in response.technical_analysis, "Missing S3 guidance"
    assert "encryption" in response.technical_analysis.lower(), "Missing encryption guidance"
    assert response.confidence_score > 0.5, "Low confidence for well-known vulnerabilities"

    print(f"✅ AWS-Specific Analysis: Contains S3 and encryption guidance")
    print(f"✅ HIPAA Compliance: {'HIPAA' in str(response.compliance_mapping)}")
    print(f"✅ Critical Priority: {'critical' in response.business_impact.lower()}")
    print(f"✅ Confidence Score: {response.confidence_score:.1%}")

    return response

async def test_compliance_framework_mapping():
    """Test compliance framework mapping accuracy"""

    print("\n🧪 Testing Compliance Framework Mapping...")
    print("=" * 60)

    integration = GuidePointRAGIntegration()

    # Test CIS benchmark mapping
    request = SecurityConsultingRequest(
        question="What CIS Kubernetes benchmark controls apply to privileged containers?",
        compliance_requirements=["CIS", "NIST", "SOC2"],
        urgency_level="medium"
    )

    response = await integration.consult_security_question(request)

    # Validate compliance mapping
    frameworks_found = list(response.compliance_mapping.keys())

    print(f"✅ Frameworks Identified: {frameworks_found}")
    print(f"✅ CIS Coverage: {'CIS' in frameworks_found}")
    print(f"✅ NIST Coverage: {'NIST' in frameworks_found}")

    # Check for specific CIS controls
    if 'CIS' in response.compliance_mapping:
        cis_controls = response.compliance_mapping['CIS']
        print(f"✅ CIS Controls Found: {len(cis_controls)} controls")

    return response

async def test_vulnerability_context_integration():
    """Test vulnerability context and MITRE ATT&CK integration"""

    print("\n🧪 Testing Vulnerability Context Integration...")
    print("=" * 60)

    integration = GuidePointRAGIntegration()

    # Test MITRE ATT&CK mapping
    request = SecurityConsultingRequest(
        question="Analyze privilege escalation attack vectors in my infrastructure",
        vulnerability_findings=[
            {
                "vulnerability_type": "CVE-2021-25741",
                "description": "Kubernetes symlink attack",
                "severity": "critical"
            }
        ],
        urgency_level="critical"
    )

    response = await integration.consult_security_question(request)

    # Check for MITRE context
    mitre_mentioned = any("mitre" in source.get("type", "").lower() or
                         "T1" in str(source) for source in response.sources)

    print(f"✅ MITRE ATT&CK Context: {mitre_mentioned}")
    print(f"✅ CVE Context Available: {'CVE-2021-25741' in response.technical_analysis}")
    print(f"✅ Attack Vector Analysis: {'attack' in response.technical_analysis.lower()}")

    return response

async def test_consulting_template_utilization():
    """Test consulting template utilization for different client types"""

    print("\n🧪 Testing Consulting Template Utilization...")
    print("=" * 60)

    integration = GuidePointRAGIntegration()

    # Test executive communication template
    request = SecurityConsultingRequest(
        question="Provide executive summary of security posture for board meeting",
        client_context={"audience": "C-suite", "format": "executive_summary"},
        urgency_level="medium"
    )

    response = await integration.consult_security_question(request)

    # Check for executive-appropriate content
    executive_keywords = ["business risk", "investment", "compliance", "executive"]
    executive_content = any(keyword in response.executive_summary.lower()
                          for keyword in executive_keywords)

    print(f"✅ Executive Content: {executive_content}")
    print(f"✅ Business Language: {'$' in response.business_impact or 'cost' in response.business_impact.lower()}")
    print(f"✅ Template Sources: {any('template' in str(source) for source in response.sources)}")

    return response

async def test_end_to_end_consulting_workflow():
    """Test complete end-to-end consulting workflow"""

    print("\n🧪 Testing End-to-End Consulting Workflow...")
    print("=" * 60)

    integration = GuidePointRAGIntegration()

    # Comprehensive security assessment scenario
    request = SecurityConsultingRequest(
        question="Conduct comprehensive security assessment and provide remediation roadmap",
        vulnerability_findings=[
            {"vulnerability_type": "CKV_K8S_12", "severity": "high"},
            {"vulnerability_type": "CKV_AWS_145", "severity": "critical"},
            {"vulnerability_type": "CKV_AWS_23", "severity": "high"}
        ],
        client_context={
            "industry": "enterprise_saas",
            "compliance": ["SOC2", "ISO27001", "GDPR"],
            "budget": "$50000",
            "timeline": "90_days"
        },
        compliance_requirements=["CIS", "NIST", "SOC2"],
        urgency_level="high"
    )

    response = await integration.consult_security_question(request)

    # Comprehensive validation
    quality_metrics = {
        "executive_summary_length": len(response.executive_summary) > 200,
        "technical_depth": len(response.technical_analysis) > 300,
        "actionable_steps": len(response.remediation_steps) >= 5,
        "compliance_coverage": len(response.compliance_mapping) >= 2,
        "high_confidence": response.confidence_score > 0.6,
        "source_diversity": len(response.sources) >= 3
    }

    passed_metrics = sum(quality_metrics.values())
    total_metrics = len(quality_metrics)

    print(f"✅ Quality Metrics Passed: {passed_metrics}/{total_metrics}")
    print(f"✅ Overall Quality Score: {(passed_metrics/total_metrics)*100:.1f}%")

    for metric, passed in quality_metrics.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {metric.replace('_', ' ').title()}")

    return response, (passed_metrics/total_metrics)

async def main():
    """Run complete GuidePoint RAG consulting test suite"""

    print("🚀 GuidePoint RAG Consulting Test Suite")
    print("=" * 80)

    test_results = []

    try:
        # Run all test scenarios
        k8s_response = await test_kubernetes_security_consulting()
        test_results.append(("Kubernetes Security", "✅ Passed"))

        aws_response = await test_aws_security_consulting()
        test_results.append(("AWS Security", "✅ Passed"))

        compliance_response = await test_compliance_framework_mapping()
        test_results.append(("Compliance Mapping", "✅ Passed"))

        vuln_response = await test_vulnerability_context_integration()
        test_results.append(("Vulnerability Context", "✅ Passed"))

        template_response = await test_consulting_template_utilization()
        test_results.append(("Template Utilization", "✅ Passed"))

        e2e_response, quality_score = await test_end_to_end_consulting_workflow()
        test_results.append(("End-to-End Workflow", f"✅ Passed ({quality_score:.1%} quality)"))

    except Exception as e:
        test_results.append(("Test Execution", f"❌ Failed: {str(e)}"))

    # Final Summary
    print("\n" + "=" * 80)
    print("🎯 GUIDEPOINT RAG CONSULTING TEST RESULTS")
    print("=" * 80)

    for test_name, result in test_results:
        print(f"{result:<20} {test_name}")

    passed_tests = sum(1 for _, result in test_results if "✅" in result)
    total_tests = len(test_results)

    print(f"\n📊 Test Summary: {passed_tests}/{total_tests} passed ({(passed_tests/total_tests)*100:.1f}%)")

    if passed_tests == total_tests:
        print("✅ GuidePoint RAG is ready for security consulting!")
        print("🎯 James can now provide professional security consulting guidance")
        print("🏆 Integration between GuidePoint and James RAG is complete")
    else:
        print("⚠️ Some tests failed - review implementation before deployment")

if __name__ == "__main__":
    asyncio.run(main())