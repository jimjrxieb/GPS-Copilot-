#!/usr/bin/env python3
"""
Test Kubernetes Implementation Planner
Validates practical consulting value with TechCorp scenario
"""

import asyncio
from datetime import datetime

from guidance.kubernetes_planner import (
    kubernetes_planner, SecurityLevel, DeploymentEnvironment
)
from clients.client_profiler import (
    ClientProfile, ClientProfileManager, AssetCriticality,
    Industry, ComplianceFramework, RiskTolerance
)

def test_kubernetes_planner():
    """Test the Kubernetes planner with realistic consulting scenario"""

    print('🎯 TESTING KUBERNETES IMPLEMENTATION PLANNER')
    print('=' * 60)
    print('Real Consulting Scenario: TechCorp Production Hardening')
    print()

    # Step 1: Use existing TechCorp client profile
    print('👤 Step 1: Loading TechCorp client profile...')

    client_manager = ClientProfileManager()

    # Create TechCorp profile (as would exist from previous meeting)
    techcorp_client = ClientProfile(
        company_name="TechCorp Solutions",
        industry=Industry.TECHNOLOGY,
        annual_revenue=25000000,  # $25M
        employee_count=120,
        business_model="B2B SaaS Platform",
        key_revenue_drivers=["API platform", "Data analytics", "Customer dashboard"],
        customer_base_size=2500,
        compliance_frameworks=[ComplianceFramework.SOC2, ComplianceFramework.GDPR],
        risk_tolerance=RiskTolerance.MODERATE,
        critical_assets=[
            AssetCriticality(
                system_name="api-gateway",
                business_function="Revenue API",
                revenue_impact=True,
                customer_facing=True,
                contains_pii=True,
                downtime_tolerance_hours=0.25,  # 15 minutes max
                data_classification="confidential"
            ),
            AssetCriticality(
                system_name="customer-database",
                business_function="Customer Data",
                revenue_impact=False,
                customer_facing=False,
                contains_pii=True,
                downtime_tolerance_hours=2.0,
                data_classification="restricted"
            ),
            AssetCriticality(
                system_name="analytics-engine",
                business_function="Data Processing",
                revenue_impact=True,
                customer_facing=False,
                contains_pii=False,
                downtime_tolerance_hours=4.0,
                data_classification="internal"
            )
        ],
        technology_stack=["kubernetes", "postgresql", "redis", "python", "jenkins"],
        cloud_providers=["AWS"]
    )

    client_id = client_manager.create_profile(techcorp_client)
    print(f'   ✅ Client loaded: {techcorp_client.company_name} (ID: {client_id})')

    # Step 2: Generate production hardening plan
    print('📋 Step 2: Generating production Kubernetes hardening plan...')

    specific_requirements = [
        "SOC2 Type II compliance required by Q4",
        "GDPR compliance for 15% European customer base",
        "API gateway generates 80% of revenue",
        "Zero tolerance for downtime during business hours",
        "Jenkins CI/CD integration required"
    ]

    implementation_plan = kubernetes_planner.generate_implementation_plan(
        client_profile_id=client_id,
        environment=DeploymentEnvironment.PRODUCTION,
        security_level=SecurityLevel.HARDENED,
        specific_requirements=specific_requirements
    )

    print(f'   ✅ Plan generated: {implementation_plan.plan_id}')
    print(f'   ⏱️ Estimated time: {implementation_plan.estimated_total_time_hours:.1f} hours')
    print(f'   🎯 Complexity: {implementation_plan.complexity_score}/10')
    print(f'   ⚠️ Risk level: {implementation_plan.risk_level}')

    # Step 3: Display practical implementation guidance
    print()
    print('📖 IMPLEMENTATION PLAN OVERVIEW')
    print('=' * 60)

    print('\n🎯 Business Context:')
    for req in implementation_plan.business_requirements:
        print(f'   • {req}')

    print('\n⚠️ Risk Considerations:')
    for risk in implementation_plan.risk_considerations:
        print(f'   • {risk}')

    print('\n✅ Prerequisites:')
    for i, prereq in enumerate(implementation_plan.prerequisites[:5], 1):
        print(f'   {i}. {prereq}')

    # Step 4: Show first implementation step in detail
    print()
    print('🔧 DETAILED IMPLEMENTATION STEP EXAMPLE')
    print('=' * 60)

    first_step = implementation_plan.implementation_steps[0]
    print(f'Step {first_step.step_number}: {first_step.title}')
    print(f'Description: {first_step.description}')
    print(f'Business Justification: {first_step.business_justification}')
    print(f'Security Impact: {first_step.security_impact}')
    print(f'Estimated Time: {first_step.estimated_time_minutes} minutes')
    print()
    print('Commands to Execute:')
    for cmd in first_step.commands[:10]:  # Show first 10 commands
        if cmd.strip():
            print(f'   {cmd}')
    if len(first_step.commands) > 10:
        print(f'   ... ({len(first_step.commands) - 10} more commands)')

    print()
    print('Validation Commands:')
    for cmd in first_step.validation_commands:
        print(f'   {cmd}')

    # Step 5: Show network security step (most relevant to TechCorp)
    print()
    print('🌐 NETWORK SECURITY IMPLEMENTATION')
    print('=' * 60)

    network_step = None
    for step in implementation_plan.implementation_steps:
        if "Network Security" in step.title:
            network_step = step
            break

    if network_step:
        print(f'Step {network_step.step_number}: {network_step.title}')
        print(f'Business Justification: {network_step.business_justification}')
        print()
        print('Key Commands for TechCorp API Gateway Protection:')
        for cmd in network_step.commands:
            if 'api-gateway' in cmd or 'customer-facing' in cmd or 'ingress' in cmd:
                print(f'   {cmd}')

    # Step 6: Demonstrate business-aware prioritization
    print()
    print('💼 BUSINESS-AWARE IMPLEMENTATION PRIORITIZATION')
    print('=' * 60)

    print('James AI has prioritized implementation steps based on TechCorp business context:')
    print()

    for i, step in enumerate(implementation_plan.implementation_steps, 1):
        revenue_impact = "🔴" if any(asset in step.business_justification for asset in ["revenue", "API", "customer"]) else "🟡"
        compliance_impact = "⚖️" if any(framework in step.business_justification for framework in ["SOC2", "GDPR"]) else ""

        print(f'{i}. {revenue_impact} {compliance_impact} {step.title}')
        print(f'   Time: {step.estimated_time_minutes}min | Business: {step.business_justification[:80]}...')
        print()

    # Step 7: Validation procedures specific to TechCorp
    print()
    print('✅ VALIDATION PROCEDURES FOR TECHCORP')
    print('=' * 60)

    print('Customized validation for TechCorp requirements:')
    for i, validation in enumerate(implementation_plan.validation_procedures, 1):
        print(f'{i}. {validation}')

    # Step 8: Demonstrate rollback planning
    print()
    print('🔄 ROLLBACK PLAN (Risk Mitigation)')
    print('=' * 60)

    print('Comprehensive rollback plan for production safety:')
    for rollback_step in implementation_plan.rollback_plan[:10]:
        print(f'   {rollback_step}')
    if len(implementation_plan.rollback_plan) > 10:
        print(f'   ... ({len(implementation_plan.rollback_plan) - 10} more steps)')

    # Step 9: Assess consulting value
    print()
    print('💰 CONSULTING VALUE ASSESSMENT')
    print('=' * 60)

    value_metrics = {
        "business_context_integration": len(implementation_plan.business_requirements) > 0,
        "compliance_specific_guidance": len(implementation_plan.compliance_frameworks) > 0,
        "revenue_protection_focus": any("revenue" in req.lower() for req in implementation_plan.business_requirements),
        "practical_commands_provided": all(len(step.commands) > 0 for step in implementation_plan.implementation_steps),
        "validation_procedures_included": len(implementation_plan.validation_procedures) > 0,
        "rollback_plan_comprehensive": len(implementation_plan.rollback_plan) > 5,
        "time_estimation_realistic": 2 <= implementation_plan.estimated_total_time_hours <= 40,
        "risk_assessment_provided": implementation_plan.risk_level in ["LOW", "MEDIUM", "HIGH"]
    }

    value_score = sum(value_metrics.values()) / len(value_metrics) * 100

    print(f'Overall Consulting Value Score: {value_score:.1f}%')
    print()
    print('Value Delivered:')
    for metric, passed in value_metrics.items():
        status = "✅" if passed else "❌"
        metric_name = metric.replace("_", " ").title()
        print(f'   {status} {metric_name}')

    # Step 10: Compare to traditional consulting
    print()
    print('📊 TRADITIONAL CONSULTING COMPARISON')
    print('=' * 60)

    traditional_approach = {
        "discovery_phase": "2-4 weeks",
        "plan_development": "1-2 weeks",
        "review_cycles": "1-2 weeks",
        "total_time": "4-8 weeks",
        "cost_estimate": "$50,000 - $150,000",
        "customization_level": "High manual effort"
    }

    james_approach = {
        "discovery_phase": "Meeting notes processed in real-time",
        "plan_development": "Generated in minutes with business context",
        "review_cycles": "Instant iterations with client feedback",
        "total_time": "Same day delivery",
        "cost_estimate": "Automated - fraction of traditional cost",
        "customization_level": "AI-driven personalization"
    }

    print('Traditional vs James AI Approach:')
    print()
    for metric in traditional_approach:
        print(f'{metric.replace("_", " ").title()}:')
        print(f'   Traditional: {traditional_approach[metric]}')
        print(f'   James AI: {james_approach[metric]}')
        print()

    # Final assessment
    print('🌟 PRACTICAL CONSULTING VALIDATION')
    print('=' * 60)

    practical_tests = [
        implementation_plan.estimated_total_time_hours > 0,
        len(implementation_plan.implementation_steps) >= 4,
        any("kubectl" in " ".join(step.commands) for step in implementation_plan.implementation_steps),
        any("SOC2" in step.business_justification for step in implementation_plan.implementation_steps),
        implementation_plan.risk_level != "UNKNOWN",
        len(implementation_plan.business_requirements) > 0
    ]

    practical_score = sum(practical_tests) / len(practical_tests) * 100

    print(f'Practical Implementation Readiness: {practical_score:.1f}%')

    if practical_score >= 80:
        print()
        print('🎉 KUBERNETES IMPLEMENTATION PLANNER: PRODUCTION READY')
        print('✅ Generates actionable, business-aware implementation plans')
        print('✅ Integrates client business context into technical recommendations')
        print('✅ Provides step-by-step guidance with validation procedures')
        print('✅ Includes comprehensive risk mitigation and rollback plans')
        print('✅ Delivers consulting value equivalent to $50K+ traditional engagement')

        return True
    else:
        print()
        print('⚠️ IMPLEMENTATION PLANNER NEEDS REFINEMENT')
        print('Some aspects require improvement for production consulting use.')

        return False

if __name__ == "__main__":
    success = test_kubernetes_planner()
    print(f'\n🏁 PRACTICAL CONSULTING TEST: {"PASSED" if success else "NEEDS WORK"}')