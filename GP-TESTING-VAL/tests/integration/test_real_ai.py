#!/usr/bin/env python3
"""
Test Real AI Integration
========================

Tests that James AI is actually using OpenAI GPT-4 instead of mock responses.
"""

import asyncio
import sys
import os
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.james_ai_engine import JamesAIEngine, SecurityFinding


async def test_real_ai_analysis():
    """Test that James AI uses real OpenAI GPT-4"""

    print("\n" + "="*60)
    print("    Testing Real AI Integration")
    print("="*60 + "\n")

    ai_engine = JamesAIEngine()

    # Create a real security scan result
    scan_results = {
        "trivy_results": {
            "vulnerabilities": [
                {
                    "vulnerability_id": "CVE-2019-10744",
                    "pkg_name": "lodash",
                    "installed_version": "4.17.4",
                    "fixed_version": "4.17.12",
                    "severity": "HIGH",
                    "title": "Prototype Pollution in lodash",
                    "description": "lodash prior to 4.17.12 is vulnerable to Prototype Pollution",
                }
            ]
        },
        "checkov_results": {
            "findings": [
                {
                    "check_id": "CKV_AWS_20",
                    "check_name": "S3 bucket encrypted",
                    "file_path": "main.tf",
                    "severity": "HIGH",
                    "description": "S3 bucket is not encrypted at rest"
                }
            ]
        }
    }

    print("🧠 Testing AI analysis with real vulnerability data...")

    # Generate analysis using real AI
    analysis = await ai_engine.analyze_scan_results(scan_results, "test_project_real_ai")

    print(f"📊 Analysis Results:")
    print(f"  - Analysis ID: {analysis.analysis_id}")
    print(f"  - Findings analyzed: {analysis.findings_analyzed}")
    print(f"  - Risk score: {analysis.risk_score}/100")
    print(f"  - Priority: {analysis.priority_level}")
    print(f"  - Summary: {analysis.summary[:100]}...")
    print(f"  - Recommendations: {len(analysis.recommendations)}")
    print(f"  - Auto-fixable: {len(analysis.auto_fixable)}")

    # Check if responses are generic placeholders or real AI
    is_real_ai = False

    # Real AI would provide specific analysis, not generic placeholders
    real_ai_indicators = [
        "CVE-2019-10744" in analysis.detailed_analysis,
        "lodash" in analysis.summary.lower(),
        len(analysis.summary) > 50,  # Real AI gives detailed summaries
        "prototype pollution" in analysis.detailed_analysis.lower(),
        analysis.risk_score > 0.0,  # Real analysis calculates actual risk
        len(analysis.recommendations) > 0
    ]

    ai_quality_score = sum(real_ai_indicators) / len(real_ai_indicators) * 100

    print(f"\n🔍 AI Quality Assessment:")
    for i, (indicator, passed) in enumerate(zip([
        "Mentions specific CVE",
        "Identifies package name",
        "Detailed summary (>50 chars)",
        "Understands vulnerability type",
        "Calculates risk score",
        "Provides recommendations"
    ], real_ai_indicators), 1):
        status = "✅" if passed else "❌"
        print(f"  {status} {indicator}")

    print(f"\n📈 Overall AI Quality: {ai_quality_score:.1f}%")

    if ai_quality_score >= 70:
        print("✅ HIGH QUALITY: Real AI analysis detected")
        is_real_ai = True
    elif ai_quality_score >= 50:
        print("⚠️  MEDIUM QUALITY: Partial AI analysis")
    else:
        print("❌ LOW QUALITY: Likely using mock/fallback responses")

    # Show the actual analysis content
    print(f"\n📋 Analysis Summary:")
    print("-" * 50)
    print(f"Summary: {analysis.summary}")
    print(f"\nDetailed Analysis: {analysis.detailed_analysis[:200]}...")
    print(f"\nRecommendations:")
    for rec in analysis.recommendations[:3]:
        print(f"  • {rec}")

    return is_real_ai, ai_quality_score


async def test_ai_communication():
    """Test direct AI API communication"""

    print(f"\n{'='*60}")
    print("    Testing Direct AI API Communication")
    print('='*60 + "\n")

    ai_engine = JamesAIEngine()

    # Test the internal AI call method
    findings = [
        SecurityFinding(
            id="test-001",
            severity="high",
            title="Prototype Pollution in lodash@4.17.4",
            description="CVE-2019-10744: lodash library vulnerable to prototype pollution attack",
            tool="npm-audit",
            cve_id="CVE-2019-10744"
        )
    ]

    print("🌐 Testing direct ms-brain API call...")

    try:
        # Call the AI analysis method directly
        ai_response = await ai_engine._call_ms_brain_api(findings, "test_project")

        print("✅ AI API call successful!")
        print(f"Response keys: {list(ai_response.keys())}")
        print(f"Summary: {ai_response.get('summary', 'N/A')[:100]}...")

        return True, ai_response

    except Exception as e:
        print(f"❌ AI API call failed: {e}")
        return False, {}


async def main():
    """Run AI integration tests"""

    print("\n" + "="*60)
    print("     James-OS Real AI Integration Test")
    print("     Testing: GPT-4 + RAG + Analysis Pipeline")
    print("="*60)

    # Test 1: Real AI analysis
    ai_working, quality_score = await test_real_ai_analysis()

    # Test 2: Direct API communication
    api_working, api_response = await test_ai_communication()

    # Summary
    print("\n" + "="*60)
    print("                    TEST SUMMARY")
    print("="*60)
    print(f"AI Analysis Quality: {quality_score:.1f}% ({'✅ PASS' if quality_score >= 70 else '❌ FAIL'})")
    print(f"API Communication: {'✅ PASS' if api_working else '❌ FAIL'}")

    overall_success = quality_score >= 70 and api_working
    print(f"\nOverall AI Integration: {'✅ SUCCESS' if overall_success else '❌ NEEDS IMPROVEMENT'}")

    if overall_success:
        print("\n🎉 James-OS is now using REAL AI for security analysis!")
    else:
        print("\n⚠️  AI integration partially working - may still use fallbacks")

    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)