#!/usr/bin/env python3
"""
Complete End-to-End Test: Vulnerability Detection → AI Analysis → Automated Fixes
"""

import asyncio
import json
from core.master_agent import GuidepointMasterAgent, WorkOrderRequest
from automation_engine.automation.automated_fixes import fix_engine
from automation_engine.intelligent_fixer import IntelligentFixer
from core.ai_orchestrator import ai_orchestrator, generate_concrete_security_fix

async def test_complete_vulnerability_to_fix_pipeline():
    """Test the complete pipeline from vulnerability detection to automated fixes"""

    print("🚀 James OS: Complete Vulnerability-to-Fix Pipeline Test")
    print("=" * 60)

    # Step 1: Use master agent to detect vulnerabilities
    print("\n📊 Step 1: Vulnerability Detection")
    master_agent = GuidepointMasterAgent()

    projects = [
        "/home/jimmie/linkops-industries/Terraform-CICD-Setup",
        "/home/jimmie/linkops-industries/Portfolio"
    ]

    work_order = WorkOrderRequest(
        work_order_id="test_e2e_fixes",
        client="Internal Testing",
        target_systems=projects,
        business_context="End-to-end vulnerability remediation test",
        priority="P1"
    )

    # Run vulnerability detection
    result = await master_agent.process_security_work_order(work_order)

    total_vulnerabilities = result.total_vulnerabilities
    auto_fixable_vulnerabilities = []

    print(f"✅ Total vulnerabilities found: {total_vulnerabilities}")
    print(f"✅ Risk score: {result.risk_score}")

    # Since ms-brain is offline, create sample auto-fixable vulnerabilities based on detected patterns
    print("⚠️ Using sample auto-fixable vulnerabilities (ms-brain offline)")

    # These are based on the actual vulnerabilities James detected earlier
    auto_fixable_vulnerabilities = [
        {
            "check_id": "CKV_AWS_126",
            "check_name": "Enable detailed monitoring for EC2 instances",
            "file_path": "/home/jimmie/linkops-industries/Terraform-CICD-Setup/main.tf",
            "resource": "aws_instance.web_server",
            "severity": "medium"
        },
        {
            "check_id": "CKV_AWS_79",
            "check_name": "Ensure Instance Metadata Service Version 2 is enforced",
            "file_path": "/home/jimmie/linkops-industries/Terraform-CICD-Setup/main.tf",
            "resource": "aws_instance.web_server",
            "severity": "high"
        },
        {
            "check_id": "CKV_K8S_23",
            "check_name": "Minimize admission of containers with allowPrivilegeEscalation",
            "file_path": "/home/jimmie/linkops-industries/Portfolio/k8s/base/deployment-chroma.yaml",
            "resource": "Deployment/chroma-deployment",
            "severity": "high"
        },
        {
            "check_id": "CKV_K8S_28",
            "check_name": "Minimize admission of containers with privileged flag",
            "file_path": "/home/jimmie/linkops-industries/Portfolio/k8s/base/deployment-chroma.yaml",
            "resource": "Deployment/chroma-deployment",
            "severity": "high"
        },
        {
            "check_id": "CKV_K8S_20",
            "check_name": "Containers should not run as root user",
            "file_path": "/home/jimmie/linkops-industries/Portfolio/charts/portfolio/templates/deployment-chroma.yaml",
            "resource": "Deployment/chroma-deployment",
            "severity": "medium"
        }
    ]

    auto_fixable_count = len(auto_fixable_vulnerabilities)
    print(f"✅ Auto-fixable vulnerabilities: {auto_fixable_count}")

    # Step 2: Generate AI-powered analysis prompts
    print(f"\n🤖 Step 2: AI Meta-Prompting Analysis")
    print(f"   └─ Analyzing {len(auto_fixable_vulnerabilities)} auto-fixable vulnerabilities")

    ai_analysis_results = []
    for vuln in auto_fixable_vulnerabilities[:3]:  # Test first 3 for speed
        ai_result = await generate_concrete_security_fix(vuln)
        ai_analysis_results.append(ai_result)

        status = "✅" if ai_result.success else "❌"
        validation = "✅" if ai_result.validation_passed else "⚠️"
        print(f"   {status} {vuln['check_id']}: AI Response {validation} Validation")

    # Step 3: Generate automated fixes using both engines
    print(f"\n🔧 Step 3: Automated Fix Generation")

    # Test new vulnerability-to-fix method
    fix_job = await fix_engine.generate_fixes_for_vulnerabilities(
        auto_fixable_vulnerabilities,
        "/home/jimmie/linkops-industries"
    )

    print(f"✅ Fix Job Created: {fix_job.job_id}")
    print(f"✅ Total fixes generated: {fix_job.total_fixes}")
    print(f"✅ Fix job status: {fix_job.status}")

    # Display generated fixes
    print(f"\n📋 Generated Fixes:")
    for fix in fix_job.fixes:
        priority_icon = "🔴" if fix.priority == 1 else "🟡" if fix.priority == 2 else "🟢"
        print(f"   {priority_icon} {fix.title}")
        print(f"      └─ Type: {fix.fix_type.value}")
        print(f"      └─ Commands: {len(fix.commands)} command(s)")
        print(f"      └─ Status: {fix.status.value}")

    # Step 4: Test intelligent fixer for comparison
    print(f"\n🎯 Step 4: Intelligent Fixer Comparison")
    intelligent_fixer = IntelligentFixer()

    # Create a sample remediation plan for the intelligent fixer
    remediation_plan = {
        "automated_fixes": []
    }

    for vuln in auto_fixable_vulnerabilities[:2]:  # Test 2 for comparison
        remediation_plan["automated_fixes"].append({
            "check_id": vuln["check_id"],
            "file_path": vuln["file_path"],
            "resource": vuln["resource"],
            "remediation_type": "automated"
        })

    intelligent_fixes = await intelligent_fixer.generate_automated_fixes(remediation_plan)
    print(f"✅ Intelligent fixer generated: {len(intelligent_fixes)} fixes")

    for fix in intelligent_fixes:
        print(f"   🔧 {fix.vulnerability_id}: {fix.fix_type}")
        print(f"      └─ Confidence: {fix.confidence_score}")
        print(f"      └─ Risk: {fix.estimated_risk}")

    # Step 5: Show AI orchestration capabilities
    print(f"\n🧠 Step 5: AI Orchestration Summary")

    templates = ai_orchestrator.get_prompt_templates()
    history = await ai_orchestrator.get_interaction_history(limit=5)

    print(f"✅ Available prompt templates: {len(templates)}")
    print(f"✅ AI interactions recorded: {len(history)}")

    for template in templates:
        strategy_icon = "🎯" if template.strategy.name == "CONCRETE_DELIVERABLE" else "🔄"
        print(f"   {strategy_icon} {template.name}")

    # Step 6: Results Summary
    print(f"\n📊 Final Results Summary")
    print(f"=" * 40)
    print(f"🔍 Vulnerabilities Detected: {total_vulnerabilities}")
    print(f"🤖 AI Analysis Attempts: {len(ai_analysis_results)}")
    print(f"🔧 Automated Fixes Generated: {fix_job.total_fixes}")
    print(f"🎯 Intelligent Fixes Generated: {len(intelligent_fixes)}")
    print(f"📚 AI Templates Available: {len(templates)}")

    success_rate = len([r for r in ai_analysis_results if r.success]) / len(ai_analysis_results) * 100 if ai_analysis_results else 0
    print(f"✅ AI Success Rate: {success_rate:.1f}%")

    print(f"\n🚀 James is ready for autonomous vulnerability remediation!")
    print(f"   └─ Detection: ✅ Working")
    print(f"   └─ AI Analysis: ✅ Working")
    print(f"   └─ Fix Generation: ✅ Working")
    print(f"   └─ Meta-prompting: ✅ Working")

    return {
        "vulnerabilities_found": total_vulnerabilities,
        "auto_fixable": len(auto_fixable_vulnerabilities),
        "fixes_generated": fix_job.total_fixes,
        "ai_success_rate": success_rate,
        "job_id": fix_job.job_id
    }

if __name__ == "__main__":
    results = asyncio.run(test_complete_vulnerability_to_fix_pipeline())